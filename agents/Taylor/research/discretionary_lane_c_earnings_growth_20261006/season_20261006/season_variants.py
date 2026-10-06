"""Làn C — biến thể MÙA VỤ (job Taylor_20261006_052500). Research only; đọc data/bq_cache, ghi thư mục này.
Interpreter: /home/trido/thanhdt/wc_venv/bin/python. Khung y hệt ../lane_c_backtest.py (universe PIT, T+1,
TC 0,1%/chiều, EW tái cân bằng tháng, so BASE = EW toàn vũ trụ E(d)).

Biến thể (định nghĩa trước khi chạy, không tune):
  C1_KNOWN : C1 gốc — quý = dòng có ngày biết MUỘN NHẤT (< d). CONTROL: phải tái lập đúng ../monthly.csv C1_GARP.
  C1       : C1, quý = kỳ MỚI NHẤT (< d) theo luật funnel mới (quý mới nhất thiếu NP ⇒ loại, không lùi).
  C1S      : C1 + mùa vụ (SHIP): mã mùa vụ (seasonal_stats của funnel) thay QoQ>0 bằng QoQ đ/c mùa > 0.
  C1A      : QoQ đ/c mùa cho MỌI mã đủ lịch sử (>=3 năm/cặp), không cần η² — mã thiếu lịch sử giữ QoQ>0.
  C1Y      : bỏ QoQ, thay bằng YoY quý trước > 0 (NP_P1/NP_P5 − 1, 2 vế > 0) cho MỌI mã.
Hàm mùa vụ nạp TỪ funnel (FUNNEL_BIN, mặc định worktree) ⇒ cùng một định nghĩa với production.
"""
import os, sys, glob, json, importlib.util
import numpy as np, pandas as pd

os.environ.setdefault("OMP_NUM_THREADS", "1")
WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
FUNNEL_BIN = os.environ.get("FUNNEL_BIN", f"{WC}/mike/agents/Taylor/wt-season-1006/bin")
spec = importlib.util.spec_from_file_location("funnel", os.path.join(FUNNEL_BIN, "discretionary_candidate_funnel.py"))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
C = f"{WC}/data/bq_cache"
START, END = pd.Timestamp("2014-01-01"), pd.Timestamp("2026-10-05")
TC = 0.001
LEGS = ["BASE", "C1_KNOWN", "C1", "C1S", "C1A", "C1Y"]

px = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Close", "PE"])
                for f in sorted(glob.glob(f"{C}/ticker/*.parquet")) if int(os.path.basename(f)[:4]) >= 2013])
px["time"] = pd.to_datetime(px["time"])
px = px[(px.time >= "2013-10-01") & (px.time <= END)].drop_duplicates(["time", "ticker"])
close = px.pivot(index="time", columns="ticker", values="Close").sort_index()
pe = px.pivot(index="time", columns="ticker", values="PE").sort_index()
cal = close.index[close.index >= START]
allcal = close.index
up = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "in_universe", "banned", "pass_golden_floor", "rating_8l"])
                for f in sorted(glob.glob(f"{C}/universe_pit_q/*.parquet"))])
up["time"] = pd.to_datetime(up["time"])
fin = pd.read_parquet(f"{C}/ticker_financial.parquet",
                      columns=["ticker", "time", "quarter", "Release_Date"] + [f"NP_P{i}" for i in range(6)])
fin["known"] = pd.to_datetime(fin["Release_Date"]).fillna(pd.to_datetime(fin["time"]))
fin["p"] = F.quarter_index(fin["quarter"])
fin = fin.dropna(subset=["p"]).astype({"p": int})
fin_known = fin.dropna(subset=["NP_P0"]).sort_values(["known", "ticker"])   # đúng như lane_c_backtest.py

me = pd.Series(cal).groupby(cal.to_period("M")).max().values
reb = [pd.Timestamp(d) for d in me if pd.Timestamp(d) < cal[-2]]
def nxt(d):
    p = allcal.get_loc(d) + 1
    return allcal[p] if p < len(allcal) else pd.NaT

def g(a, b):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where((a > 0) & (b > 0), a / b - 1, np.nan)

rows = []
for d in reb:
    u = up[up.time == d]
    if u.empty:
        dd = up.time[up.time <= d].max(); u = up[up.time == dd]
    e = u[(u.in_universe == True) & (u.banned != True) & (u.pass_golden_floor == True) & (u.rating_8l <= 3)]
    if e.empty: continue
    fk = fin_known[fin_known.known < d].groupby("ticker").tail(1).set_index("ticker")       # C1_KNOWN
    f = fin[fin.known < d].sort_values(["ticker", "p", "known"]).drop_duplicates(["ticker", "p"], keep="last")
    lp = f.groupby("ticker").tail(1).set_index("ticker").join(F.seasonal_stats(f))       # kỳ mới nhất
    x = e[["ticker"]].set_index("ticker")
    x["PE"] = pe.loc[d].reindex(x.index)
    k = fk.reindex(x.index)
    x["k_yoy"], x["k_qoq"] = g(k.NP_P0.values, k.NP_P4.values), g(k.NP_P0.values, k.NP_P1.values)
    l = lp.reindex(x.index)
    n0, n1, n4, n5 = (l[c].values.astype(float) for c in ("NP_P0", "NP_P1", "NP_P4", "NP_P5"))
    x["yoy"], x["qoq"], x["yoy_prev"] = g(n0, n4), g(n0, n1), g(n1, n5)
    norm = l.season_norm.values.astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        x["qoq_adj"] = np.where((n0 > 0) & (n1 > 0), n0 / n1 / np.exp(norm) - 1, np.nan)
    x["seasonal"] = l.seasonal.eq(True).values
    x["hist_ok"] = (l.season_nmin.fillna(0) >= F.SEASON_MIN_PER_PAIR).values & np.isfinite(norm)
    x["quarter"] = l.quarter.values
    x["d"], x["entry"] = d, nxt(d)
    rows.append(x.reset_index())
P = pd.concat(rows, ignore_index=True)
pe_ok = (P.PE > 0) & (P.PE <= 12)
qoq_s = np.where(P.seasonal, P.qoq_adj > 0, P.qoq > 0)
qoq_a = np.where(P.hist_ok, P.qoq_adj > 0, P.qoq > 0)
sel = {
    "BASE": P,
    "C1_KNOWN": P[(P.k_yoy >= 0.30) & (P.k_qoq > 0) & pe_ok],
    "C1": P[(P.yoy >= 0.30) & (P.qoq > 0) & pe_ok],
    "C1S": P[(P.yoy >= 0.30) & qoq_s & pe_ok],
    "C1A": P[(P.yoy >= 0.30) & qoq_a & pe_ok],
    "C1Y": P[(P.yoy >= 0.30) & (P.yoy_prev > 0) & pe_ok],
}
ent = [nxt(d) for d in reb]
per = pd.DataFrame({"d": reb, "entry": ent, "exit": ent[1:] + [close.index[-1]]})
per = per[per.entry < per.exit]
def fwd(t, a, b):
    try: pa, pb = close.at[a, t], close.at[b, t]
    except KeyError: return np.nan
    if not (pa > 0): return np.nan
    if not (pb > 0):
        s = close.loc[a:b, t].dropna(); pb = s.iloc[-1] if len(s) else np.nan
    return pb / pa - 1
P = P.merge(per, on=["d", "entry"], how="inner")
P["ret"] = [fwd(t, a, b) for t, a, b in zip(P.ticker, P.entry, P.exit)]
_key = P.set_index(["d", "ticker"]).index
for k in sel: sel[k] = P[_key.isin(sel[k].set_index(["d", "ticker"]).index)]
def series(df):
    df = df.dropna(subset=["ret"]); gr = df.groupby("d"); s = gr.ret.mean()
    hold = gr.ticker.apply(set); to, prev = [], set()
    for d, h in hold.items():
        to.append(1.0 if not prev else len(h - prev) / max(len(h), 1)); prev = h
    return s - 2 * TC * pd.Series(to, index=hold.index), gr.size()
M = pd.DataFrame(index=pd.Index(per.d, name="d"))
for k in LEGS:
    r, n = series(sel[k]); M[k] = r.reindex(M.index).fillna(0.0); M[k + "_n"] = n.reindex(M.index).fillna(0)
# CONTROL: C1_KNOWN phải trùng chuỗi C1_GARP đã pin ở ../monthly.csv
ref = pd.read_csv(f"{PARENT}/monthly.csv", parse_dates=["d"]).set_index("d")
diff = (M["C1_KNOWN"] - ref["C1_GARP"].reindex(M.index)).abs().max()
print(f"[control] C1_KNOWN vs ../monthly.csv C1_GARP max|diff|={diff:.2e}")
assert diff < 1e-12, "control không tái lập được C1 đã pin — dừng"
M.to_csv(f"{HERE}/monthly_season.csv")
P[["d", "ticker", "quarter", "PE", "yoy", "qoq", "qoq_adj", "yoy_prev", "seasonal", "hist_ok", "ret"]].to_csv(
    f"{HERE}/panel_season.csv", index=False)
W = {"FULL": (START, END), "IS": (START, pd.Timestamp("2019-12-31")), "OOS": (pd.Timestamp("2020-01-01"), END),
     "OOS_ex2021": (pd.Timestamp("2022-01-01"), END)}
out = []
for w, (a, b) in W.items():
    m = M[(M.index >= a) & (M.index <= b)]
    for k in LEGS[1:]:
        x = (m[k] - m["BASE"]); n = len(x)
        y = (m[k] - m["C1_KNOWN"])
        out.append(dict(window=w, leg=k, months=n, avg_n=m[k + "_n"].mean(), ex_mean_m=x.mean(),
                        ex_t=x.mean() / x.std() * np.sqrt(n), ex_hit=(x > 0).mean(),
                        vsC1_mean_m=y.mean(), vsC1_t=(y.mean() / y.std() * np.sqrt(n)) if y.std() > 0 else np.nan))
S = pd.DataFrame(out); S.to_csv(f"{HERE}/summary_season.csv", index=False)
pd.set_option("display.width", 200); print(S.round(4).to_string())
sp = P[pe_ok & (P.yoy >= 0.30)]
print(f"seasonal share among yoy>=30%&PE<=12 rows: {sp.seasonal.mean():.3f}; hist_ok share {sp.hist_ok.mean():.3f}")
json.dump({"legs": LEGS, "months": int(len(M)), "control_maxdiff": float(diff), "funnel_bin": FUNNEL_BIN,
           "season": {"window_q": F.SEASON_WINDOW_Q, "min_per_pair": F.SEASON_MIN_PER_PAIR, "eta2_min": F.SEASON_ETA2_MIN}},
          open(f"{HERE}/meta_season.json", "w"), indent=1)
