# -*- coding: utf-8 -*-
"""e_bt2.py — mục tiêu 4 (PRELOCK V2 §6) + sửa lỗi skeptic 8, 9. Sổ 50 tỷ, tái cân bằng cuối tháng, khớp Close phiên kế (T+1),
phí 0,1%/chiều theo turnover, tiền nhàn rỗi 0% (pin0% = đầu sàn). Mã ngừng giao dịch: thoát ở giá cuối × (1 − 50%).
Trần vị thế mỗi mã ≤ 20% × GTGD trung vị 1 tháng × 5 phiên; phần không mua được nằm tiền.
Out: bt2_summary.csv, bt2_monthly_<tên>.csv, bt2_holdings_<tên>.csv, bt2_dsr.json."""
import os, sys, json, math
import numpy as np, pandas as pd
from scipy.stats import norm, skew, kurtosis
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "..", "out")
NAV0 = 50e9; FEE = 0.001; HAIR = 0.5; N_TRIALS = 57
cols = ["ticker", "ym", "mi", "in_universe", "src", "rating", "tv", "t1_close", "Close", "last_ym", "last_close", "ep", "dt5g",
        "lv_ENS1w", "lv_ENS2", "lv_ENS1", "lv_D0", "lv_D0B", "lv_MULT", "lv_A_pit", "lv_L2_ENS1w", "lv_L2_ENS2", "lv_N0", "lv_REL", "lv_EPN", "lv_WBOTH", "lv_WONLY", "lv_EONLY", "lv_EPN_E2", "lv_WBOTH_E2", "lv_WONLY_E2", "lv_EONLY_E2"]
vp = pd.read_parquet(os.path.join(OUT, "vp2.parquet"), columns=cols)
YMS = sorted(y for y in vp.ym.unique() if "2014-06" <= y <= "2026-10")
by = {ym: g.set_index("ticker") for ym, g in vp[vp.ym.isin(YMS)].groupby("ym")}
def nxt(ym):
    p = pd.Period(ym, freq="M") + 1; return str(p)
# [V3 NB-2] giá T+1 từ DỮ LIỆU GIÁ ĐẦY ĐỦ (px_t1.parquet = Close phiên đầu mỗi tháng của MỌI mã, từ allpx), KHÔNG từ panel có BCTC:
# vòng V2 lấy b = t1[(mã, tháng kế)] từ panel; mã còn giao dịch nhưng thiếu dòng panel (BCTC cũ > 200 ngày) bị coi như ngừng giao dịch và
# dính "giá cuối TOÀN CỤC × 0,5" (giá cuối có thể là giá 2026 ⇒ rò tương lai). Nay: thiếu giá đúng tháng ⇒ lấy giá phiên đầu của tháng KẾ TIẾP
# còn có giao dịch; chỉ khi mã KHÔNG còn giao dịch từ tháng đó trở đi (đã ngừng) mới áp mức mất HAIR trên giá cuối của CHÍNH mã đó.
_t1 = pd.read_parquet(os.path.join(OUT, "px_t1.parquet")); _lg = pd.read_parquet(os.path.join(OUT, "px_last.parquet")).set_index("ticker")
_t1["mi"] = pd.PeriodIndex(_t1.ym, freq="M").year * 12 + pd.PeriodIndex(_t1.ym, freq="M").month - 1
PXM = {t: (g.mi.values, g.c1.values) for t, g in _t1.sort_values(["ticker", "mi"]).groupby("ticker")}
LASTMI = {t: pd.Period(r.last_ym, freq="M").year * 12 + pd.Period(r.last_ym, freq="M").month - 1 for t, r in _lg.iterrows()}
LASTCL = _lg.last_close.to_dict()
def _px_at(tk, m):
    """giá phiên đầu của tháng m; thiếu ⇒ giá phiên đầu tháng gần nhất SAU m; không còn ⇒ nan."""
    a = PXM.get(tk)
    if a is None:
        return np.nan
    k = np.searchsorted(a[0], m, side="left")
    return a[1][k] if k < len(a[0]) else np.nan
def period_ret(ym, tks):
    """lợi suất từ T+1 của tháng ym (= giá phiên đầu tháng ym+1) tới T+1 của tháng kế; mã ngừng giao dịch ⇒ giá cuối × (1 − HAIR)."""
    p = pd.Period(ym, freq="M") + 1; m1 = p.year * 12 + p.month - 1; m2 = m1 + 1; out = []
    for t in tks:
        a = _px_at(t, m1); a = a if (np.isfinite(a) and LASTMI.get(t, -1) >= m1) else by[ym].Close.get(t, np.nan)
        if LASTMI.get(t, -1) < m2:                       # không còn phiên nào từ tháng m2 trở đi ⇒ đã ngừng giao dịch
            out.append(LASTCL[t] * (1 - HAIR) / a - 1)
        else:
            out.append(_px_at(t, m2) / a - 1)
    return np.array(out)

def run(weights_fn, name, cap=True):
    nav = NAV0; w_prev = pd.Series(dtype=float); rows = []; hold = []
    for ym in YMS[:-1]:
        g = by[ym]; w = weights_fn(ym, g, w_prev)                      # trọng số mục tiêu (tổng ≤ 1)
        if cap and len(w):
            lim = (0.2 * g.tv.reindex(w.index).fillna(0) * 5 / nav); w = np.minimum(w, lim)
        w = w[w > 1e-9]
        to = float((w.reindex(w.index.union(w_prev.index)).fillna(0) - w_prev.reindex(w.index.union(w_prev.index)).fillna(0)).abs().sum())
        r = period_ret(ym, list(w.index)) if len(w) else np.array([])
        gross = float((w.values * r).sum()); net = gross - FEE * to
        nav *= (1 + net)
        rows.append({"ym": ym, "ret": net, "gross": gross, "turnover": to, "n": int(len(w)), "invested": float(w.sum()), "nav": nav})
        for t, x, rr in zip(w.index, w.values, r):
            hold.append((ym, t, x, rr))
        w_prev = pd.Series(w.values * (1 + r), index=w.index) / (1 + gross) if len(w) else pd.Series(dtype=float)   # trôi theo giá
    m = pd.DataFrame(rows); m.to_csv(os.path.join(OUT, f"bt2_monthly_{name}.csv"), index=False)
    pd.DataFrame(hold, columns=["ym", "ticker", "w", "ret"]).to_csv(os.path.join(OUT, f"bt2_holdings_{name}.csv"), index=False)
    return m

def elig(g, floor, gate):
    e = g.in_universe & (g.tv.fillna(0) >= floor)
    if gate == "deadin":                       # ĐỘ NHẠY sống sót (sau prelock, skeptic #3): mã vắng BQ không có rating 8L ⇒ coi như LỌT cổng
        return e & ((g.rating <= 3) | (g.src == "VND"))
    return e & (g.rating <= 3) if gate else e
def s1(col, floor=1e9, gate=True, agree=None):
    state = {"held": set()}
    def fn(ym, g, w_prev):
        e = elig(g, floor, gate); lv = g[col]
        stay = [t for t in state["held"] if t in g.index and e.get(t, False) and lv.get(t, np.nan) >= 0]
        new = list(g.index[e & (lv >= np.log(1.25))])
        h = sorted(set(stay) | set(new)); state["held"] = set(h)
        if not h:
            return pd.Series(dtype=float)
        if agree is None:
            return pd.Series(1.0 / len(h), index=h)
        u = np.where(g[agree].reindex(h).values >= 0, 1.0, 0.5); return pd.Series(u / u.sum(), index=h)
    return fn
def ew(floor=1e9, exclude_col=None):
    def fn(ym, g, w_prev):
        e = elig(g, floor, False)
        if exclude_col:
            e = e & ~g[exclude_col].fillna(False).astype(bool)
        h = list(g.index[e]); return pd.Series(1.0 / len(h), index=h) if h else pd.Series(dtype=float)
    return fn
def s3f(n_by_ym, floor=1e9, gate=True):
    state = {"held": set()}
    def fn(ym, g, w_prev):
        n = int(n_by_ym.get(ym, 0)); e = elig(g, floor, gate) & g.ep.notna()
        if n == 0 or e.sum() == 0:
            state["held"] = set(); return pd.Series(dtype=float)
        rk = g.ep[e].sort_values(ascending=False); top2 = set(rk.index[:2 * n])
        keep = [t for t in rk.index if t in state["held"] and t in top2][:n]      # thứ tự theo hạng E/P ⇒ tất định (không phụ thuộc thứ tự set)
        for t in rk.index:
            if len(keep) >= n:
                break
            if t not in keep:
                keep.append(t)
        state["held"] = set(keep); return pd.Series(1.0 / len(keep), index=keep)
    return fn
# cờ cảnh báo đắt đang hiệu lực (V/P ≤ 0,67 đủ 6 tháng liên tiếp) cho S7
vp = vp.sort_values(["ticker", "mi"])
for c in ("ENS1w", "D0", "ENS2", "EPN", "WBOTH", "WONLY", "EONLY", "EPN_E2", "WBOTH_E2", "WONLY_E2", "EONLY_E2"):
    x = (vp[f"lv_{c}"] <= np.log(0.67)).astype(int)
    vp[f"warn_{c}"] = x.groupby(vp.ticker).transform(lambda s: s.rolling(6, min_periods=6).sum()) >= 6
by = {ym: g.set_index("ticker") for ym, g in vp[vp.ym.isin(YMS)].groupby("ym")}

def stats(m, a=None, b=None):
    x = m if a is None else m[(m.ym >= a) & (m.ym <= b)]
    if len(x) == 0:
        return {}
    yrs = len(x) / 12.0; tot = np.prod(1 + x.ret); nav = np.cumprod(1 + x.ret.values); dd = (nav / np.maximum.accumulate(np.concatenate([[1.0], nav]))[1:] - 1).min()
    return {"cagr": tot ** (1 / yrs) - 1, "sharpe": x.ret.mean() / x.ret.std() * math.sqrt(12), "maxdd": float(dd), "n": x.n.mean(), "turnover": x.turnover.mean(), "invested": x.invested.mean()}
RUNS = {}
def add(name, fn, cap=True):
    RUNS[name] = run(fn, name, cap); print(name, {k: round(v, 3) for k, v in stats(RUNS[name]).items()}, flush=True)
L1 = "lv_ENS1w"
for fl, tag in ((0, "f0"), (1e9, "f1"), (5e9, "f5")):
    add(f"EW_{tag}", ew(fl)); add(f"S1_ENS1w_{tag}", s1(L1, fl))
add("S1_ENS1w_f1_nocap", s1(L1, 1e9), cap=False); add("EW_f1_nocap", ew(1e9), cap=False)
add("S2_ENS1w_f1", s1(L1, 1e9, gate=False))
for c in ("D0", "ENS2", "ENS1", "MULT", "A_pit", "L2_ENS1w", "REL", "N0"):
    add(f"S1_{c}_f1", s1(f"lv_{c}", 1e9))
for tag, fl in (("f1", 1e9), ("f5", 5e9), ("f0", 0)):
    add(f"S3f_{tag}", s3f(RUNS[f"S1_ENS1w_{tag}"].set_index("ym").n.to_dict(), fl))
add("S3f_D0_f1", s3f(RUNS["S1_D0_f1"].set_index("ym").n.to_dict(), 1e9))
add("S5_ENS1w_f1", s1(L1, 1e9, agree="lv_L2_ENS1w"))
add("S1_ENS1w_f1_deadin", s1(L1, 1e9, gate="deadin")); add("S1_D0_f1_deadin", s1("lv_D0", 1e9, gate="deadin"))
add("S3f_f1_deadin", s3f(RUNS["S1_ENS1w_f1_deadin"].set_index("ym").n.to_dict(), 1e9, gate="deadin"))
add("EW_f1_bqonly", lambda ym, g, w_prev: (lambda h: pd.Series(1.0 / len(h), index=h))(list(g.index[elig(g, 1e9, False) & (g.src == "BQ")])))
add("S7_ENS1w_f1", ew(1e9, "warn_ENS1w")); add("S7_D0_f1", ew(1e9, "warn_D0"))
for c in ("EPN", "WBOTH", "WONLY", "EONLY", "ENS2", "EPN_E2", "WBOTH_E2", "WONLY_E2", "EONLY_E2"):   # [V3 B-1] S7 với null E/P cùng tỉ lệ cờ + tổ hợp (chỉ báo cáo)
    add(f"S7_{c}_f1", ew(1e9, f"warn_{c}"))
add("S3f_ENS2_f1", s3f(RUNS["S1_ENS2_f1"].set_index("ym").n.to_dict(), 1e9))      # [V3] đối chứng E/P công bằng cho bản được luật §5 chọn sau embargo
rows = []
for k, m in RUNS.items():
    for era, (a, b) in {"ALL": (None, None), "IS": ("2014-06", "2019-12"), "OOS": ("2020-01", "2026-10")}.items():
        rows.append({"strategy": k, "era": era, **stats(m, a, b)})
pd.DataFrame(rows).to_csv(os.path.join(OUT, "bt2_summary.csv"), index=False)
def dsr(ret, sh_trials, N):
    sr = ret.mean() / ret.std(); T = len(ret)
    v = np.nanvar(np.array(sh_trials) / math.sqrt(12)); emc = 0.5772156649
    sr0 = math.sqrt(v) * ((1 - emc) * norm.ppf(1 - 1.0 / N) + emc * norm.ppf(1 - 1.0 / (N * math.e)))
    g3 = skew(ret); g4 = kurtosis(ret, fisher=False)
    return float(norm.cdf((sr - sr0) * math.sqrt(T - 1) / math.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr * sr))), float(sr0 * math.sqrt(12))
res = {"N_trials_used": N_TRIALS}
s1names = [k for k in RUNS if k.startswith("S1_") and k.endswith("_f1")]
dead_w = {k: float(pd.read_csv(os.path.join(OUT, f"bt2_holdings_{k}.csv")).merge(vp[["ticker", "src"]].drop_duplicates("ticker"), on="ticker").query("src == 'VND'").w.sum()
              / max(pd.read_csv(os.path.join(OUT, f"bt2_holdings_{k}.csv")).w.sum(), 1e-9)) for k in ("S1_ENS1w_f1_deadin", "S1_D0_f1_deadin", "S3f_f1_deadin", "S2_ENS1w_f1", "EW_f1")}
sh_abs = [stats(RUNS[k])["sharpe"] for k in s1names]; b = RUNS["EW_f1"]
sh_act = [(RUNS[k].ret - b.ret).mean() / (RUNS[k].ret - b.ret).std() * math.sqrt(12) for k in s1names]
for k in ("S1_ENS1w_f1", "S1_D0_f1", "S1_ENS2_f1"):
    m = RUNS[k]; act = (m.ret - b.ret).values
    res[k] = {"dsr_abs": dsr(m.ret.values, sh_abs, N_TRIALS)[0], "dsr_active_vs_EW": dsr(act, sh_act, N_TRIALS)[0], "sr0_active": dsr(act, sh_act, N_TRIALS)[1], "dsr_abs_N80": dsr(m.ret.values, sh_abs, 80)[0], "dsr_active_N80": dsr(act, sh_act, 80)[0],
              "active_sharpe": float(act.mean() / act.std() * math.sqrt(12))}
    m2 = m.assign(b=b.ret.values, year=m.ym.str[:4]); py = m2.groupby("year").apply(lambda x: pd.Series({"s1": np.prod(1 + x.ret) - 1, "ew": np.prod(1 + x.b) - 1, "n": x.n.mean()}))
    py["excess"] = py.s1 - py.ew; py.to_csv(os.path.join(OUT, f"bt2_peryear_{k}.csv")); res[k]["years_beat_EW"] = f"{int((py.excess > 0).sum())}/{len(py)}"
    e3 = RUNS[{"S1_ENS1w_f1": "S3f_f1", "S1_D0_f1": "S3f_D0_f1", "S1_ENS2_f1": "S3f_ENS2_f1"}[k]]; a3 = (m.ret - e3.ret).values
    res[k]["active_sharpe_vs_S3f"] = float(a3.mean() / a3.std() * math.sqrt(12))
    dt = {ym: by[ym].dt5g.iloc[0] for ym in YMS[:-1]}; m2["dt5g"] = m2.ym.map(dt)
    res[k]["dt5g_excess_m"] = {str(kk): [float(x.ret.mean() - x.b.mean()), int(len(x))] for kk, x in m2.groupby("dt5g")}
res["sharpes_S1_f1"] = dict(zip(s1names, sh_abs)); res["weight_share_in_dead_names"] = dead_w
json.dump(res, open(os.path.join(OUT, "bt2_dsr.json"), "w"), indent=1, default=float)
s = pd.DataFrame(rows).pivot(index="strategy", columns="era", values="cagr").round(4)[["ALL", "IS", "OOS"]]
x = pd.DataFrame(rows); x = x[x.era == "ALL"].set_index("strategy")[["sharpe", "maxdd", "n", "turnover", "invested"]].round(3)
print(s.join(x).to_string()); print(json.dumps({k: res[k] for k in ("S1_ENS1w_f1", "S1_D0_f1", "S1_ENS2_f1")}, default=float))
