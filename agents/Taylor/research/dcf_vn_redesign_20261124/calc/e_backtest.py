# -*- coding: utf-8 -*-
"""e_backtest.py — tiêu chí (4): danh mục lịch-thời-gian theo luật PRELOCK §5 (S1..S4), T+1, EW, phí 0,1%/chiều.
Out: ../out/bt_summary.csv, bt_monthly_<v>.csv, holdings_<v>_S1.csv, bt_dsr.json, resid_ic.csv"""
import os, sys, json, math
import numpy as np, pandas as pd, duckdb
from scipy.stats import norm, skew, kurtosis, spearmanr, rankdata
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out"); WC = "/home/trido/thanhdt/WorkingClaude"
vp = pd.read_parquet(os.path.join(OUT, "vp.parquet")).sort_values(["ticker", "ym"]).reset_index(drop=True)
vp["ymp"] = pd.PeriodIndex(vp.ym, freq="M")
t1 = vp.set_index(["ticker", "ymp"]).t1_close
nx = t1.reindex(pd.MultiIndex.from_arrays([vp.ticker, vp.ymp + 1])).values
vp["ret1"] = nx / vp.t1_close.values - 1            # lợi suất giữ từ T+1 tháng này tới T+1 tháng sau
vp["vanish"] = vp.t1_close.notna() & np.isnan(nx)
YMS = sorted(vp[(vp.ym >= "2014-06") & vp.ret1.notna()].ym.unique())
VARS = [c[3:] for c in vp.columns if c.startswith("lv_")]
HAIR = float(os.environ.get("HAIRCUT", "0"))        # độ nhạy mã rời sàn
by_ym = {ym: g.set_index("ticker") for ym, g in vp[vp.ym >= "2014-06"].groupby("ym")}

def run_nav(hold_by_ym, tag=None):
    nav = 1.0; w_prev = {}; rows = []
    for ym in YMS:
        g = by_ym[ym]; H = [t for t in hold_by_ym.get(ym, []) if t in g.index and g.t1_close.notna().get(t, False)]
        w = {t: 1.0 / len(H) for t in H}
        turn = sum(abs(w.get(t, 0) - w_prev.get(t, 0)) for t in set(w) | set(w_prev))
        cost = 0.001 * turn
        r = 0.0
        for t in H:
            x = g.ret1.get(t)
            r += w[t] * ((-HAIR) if (x != x) else x)
        gross = (1 - cost) * (1 + r)
        nav *= gross
        # trọng số trôi tới cuối kỳ
        tot = sum(w[t] * (1 + (0 if g.ret1.get(t) != g.ret1.get(t) else g.ret1.get(t))) for t in H) if H else 1
        w_prev = {t: w[t] * (1 + (0 if g.ret1.get(t) != g.ret1.get(t) else g.ret1.get(t))) / tot for t in H}
        rows.append((ym, gross - 1, len(H), turn))
    return pd.DataFrame(rows, columns=["ym", "ret", "n", "turn"])

def s1_holdings(col, gate=True, entry=np.log(1.25)):
    hold = {}; state = set()
    for ym in YMS:
        g = by_ym[ym]; lv = g[col]
        ok_r = (g.rating <= 3) if gate else pd.Series(True, index=g.index)
        keep = {t for t in state if t in g.index and lv.get(t) == lv.get(t) and lv[t] >= 0 and bool(ok_r[t])}
        new = set(g.index[(lv >= entry) & g.in_universe & ok_r & g.t1_close.notna()])
        state = keep | new; hold[ym] = sorted(state)
    return hold

def stats(m, a=None, b=None):
    x = m[(m.ym >= (a or "0")) & (m.ym <= (b or "9"))]
    if len(x) < 6: return {}
    yrs = len(x) / 12.0; tot = float(np.prod(1 + x.ret))
    nav = np.cumprod(1 + x.ret.values); dd = float((nav / np.maximum.accumulate(nav) - 1).min())
    return {"cagr": tot ** (1 / yrs) - 1, "sharpe": float(x.ret.mean() / x.ret.std() * math.sqrt(12)), "maxdd": dd, "avg_n": float(x.n.mean()), "turn_m": float(x.turn.mean())}

# benchmarks
uni_hold = {ym: sorted(by_ym[ym].index[by_ym[ym].in_universe & by_ym[ym].t1_close.notna()]) for ym in YMS}
bench = run_nav(uni_hold)
c = duckdb.connect()
vni = c.execute(f"SELECT CAST(time AS DATE) AS time, max(VNINDEX) v FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet') WHERE VNINDEX > 0 GROUP BY 1 ORDER BY 1").df()
vni["time"] = pd.to_datetime(vni.time); vni["ymp"] = vni.time.dt.to_period("M")
v1 = vni.groupby("ymp").v.first()                   # phiên đầu tháng = T+1 của tháng trước
vn = pd.DataFrame({"ym": YMS}); p = pd.PeriodIndex(vn.ym, freq="M")
vn["ret"] = v1.reindex(p + 2).values / v1.reindex(p + 1).values - 1; vn["n"] = 1; vn["turn"] = 0
summ = []; monthly = {"EW": bench, "VNINDEX": vn}; s1_sharpes = {}; s1_active = {}
def add(name, m):
    monthly[name] = m
    for era, (a, b) in {"ALL": (None, None), "IS": ("2014-06", "2019-12"), "OOS": ("2020-01", "2099")}.items():
        s = stats(m, a, b); s.update({"strategy": name, "era": era}); summ.append(s)
add("EW_universe", bench); add("VNINDEX_price", vn)
MAIN = os.environ.get("MAIN", "D0_fix,G1D0_fix,B_slow,A_fix,E_fix,F_adp,H_fix,D_fix,G05D0_fix").split(",")
for v in VARS:
    col = f"lv_{v}"; h = s1_holdings(col); m = run_nav(h)
    s1_sharpes[v] = float(m.ret.mean() / m.ret.std() * math.sqrt(12)) if m.ret.std() > 0 else np.nan
    act = m.ret.values - bench.ret.values; s1_active[v] = float(act.mean() / act.std() * math.sqrt(12)) if act.std() > 0 else np.nan
    add(f"S1_{v}", m)
    if v in MAIN:
        m.to_csv(os.path.join(OUT, f"bt_monthly_S1_{v}.csv"), index=False)
        pd.DataFrame([(ym, t) for ym, ts in h.items() for t in ts], columns=["ym", "ticker"]).to_csv(os.path.join(OUT, f"holdings_S1_{v}.csv"), index=False)
        add(f"S2_{v}", run_nav(s1_holdings(col, gate=False)))
        # S3: cùng số mã như S1, chọn theo E/P TTM cao nhất (rating<=3, in_universe)
        h3 = {}; h4 = {}
        for ym in YMS:
            g = by_ym[ym]; e = g[g.in_universe & (g.rating <= 3) & g.t1_close.notna()]
            ep = (e.roe * e.bp).sort_values(ascending=False); h3[ym] = list(ep.index[:len(h[ym])])
            u = g[g.in_universe & g[col].notna() & g.t1_close.notna()]
            h4[ym] = list(u[col].sort_values(ascending=False).index[:max(1, len(u) // 5)])
        add(f"S3_EPmatch_{v}", run_nav(h3)); add(f"S4_Q5_{v}", run_nav(h4))
S = pd.DataFrame(summ); S.to_csv(os.path.join(OUT, f"bt_summary{'_hair' if HAIR else ''}.csv"), index=False)
if HAIR: sys.exit(0)
# DSR (Bailey & López de Prado) cho S1 của biến thể đề xuất, N = số biến thể đã chạy
def dsr(ret, sh_trials):
    sr = ret.mean() / ret.std(); T = len(ret); N = len(sh_trials)
    v = np.nanvar(np.array(sh_trials) / math.sqrt(12)); emc = 0.5772156649
    sr0 = math.sqrt(v) * ((1 - emc) * norm.ppf(1 - 1.0 / N) + emc * norm.ppf(1 - 1.0 / (N * math.e)))
    g3 = skew(ret); g4 = kurtosis(ret, fisher=False)
    return float(norm.cdf((sr - sr0) * math.sqrt(T - 1) / math.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr * sr))), float(sr0 * math.sqrt(12))
res = {"N_trials": len(VARS), "s1_sharpe": s1_sharpes, "s1_active_sharpe": s1_active}
for v in MAIN:
    m = monthly[f"S1_{v}"]; act = m.ret.values - bench.ret.values
    d1, s0 = dsr(m.ret.values, list(s1_sharpes.values())); d2, s0a = dsr(act, list(s1_active.values()))
    res[f"dsr_abs_{v}"] = d1; res[f"dsr_active_{v}"] = d2; res["sr0_abs"] = s0; res["sr0_active"] = s0a
    # theo năm, LOO, DT5G
    m2 = m.assign(b=bench.ret.values, year=m.ym.str[:4])
    py = m2.groupby("year").apply(lambda x: pd.Series({"s1": np.prod(1 + x.ret) - 1, "ew": np.prod(1 + x.b) - 1, "n": x.n.mean()}))
    py["excess"] = py.s1 - py.ew; py.to_csv(os.path.join(OUT, f"bt_peryear_S1_{v}.csv"))
    res[f"years_beat_{v}"] = f"{int((py.excess > 0).sum())}/{len(py)}"
    loo = {y: float((np.prod(1 + m2[m2.year != y].ret) ** (12 / (len(m2) - (m2.year == y).sum())) - 1) - (np.prod(1 + m2[m2.year != y].b) ** (12 / (len(m2) - (m2.year == y).sum())) - 1)) for y in py.index}
    res[f"loo_excess_cagr_min_{v}"] = min(loo.values()); res[f"loo_excess_cagr_max_{v}"] = max(loo.values())
    dt = vp[vp.ym.isin(YMS)].groupby("ym").dt5g.first()
    m2["dt5g"] = m2.ym.map(dt)
    res[f"dt5g_excess_m_{v}"] = {str(k): [float(x.ret.mean() - x.b.mean()), int(len(x))] for k, x in m2.groupby("dt5g")}
json.dump(res, open(os.path.join(OUT, "bt_dsr.json"), "w"), indent=1, default=float)
# IC phần dư ⟂ {E/P, B/P}
rows = []
q = vp[vp.in_universe & vp.ymp.dt.month.isin([3, 6, 9, 12]) & vp.fwd36.notna() & (vp.ym >= "2014-01")].copy()
q["ep"] = q.roe * q.bp
for v in MAIN + ["Hd_fix"]:
    col = f"lv_{v}"
    for era, (a, b) in {"IS": ("2014-01", "2019-12"), "OOS": ("2020-01", "2099")}.items():
        ic = []; icr = []; icep = []; icbp = []
        for ym, g in q[(q.ym >= a) & (q.ym <= b) & q[col].notna()].groupby("ym"):
            if len(g) < 30: continue
            y = rankdata(g.fwd36); x = rankdata(g[col]); X = np.column_stack([np.ones(len(g)), rankdata(g.ep), rankdata(g.bp)])
            resid = x - X @ np.linalg.lstsq(X, x, rcond=None)[0]
            ic.append(np.corrcoef(x, y)[0, 1]); icr.append(np.corrcoef(resid, y)[0, 1]); icep.append(np.corrcoef(X[:, 1], y)[0, 1]); icbp.append(np.corrcoef(X[:, 2], y)[0, 1])
        if ic:
            rows.append({"variant": v, "era": era, "ic36": np.mean(ic), "ic36_resid": np.mean(icr), "t_resid": np.mean(icr) / (np.std(icr) / math.sqrt(len(icr))), "n_dates": len(ic), "ic36_EP": np.mean(icep), "ic36_BP": np.mean(icbp)})
pd.DataFrame(rows).to_csv(os.path.join(OUT, "resid_ic.csv"), index=False)
# SELF-CHECK: tính lại NAV S1 độc lập từ CSV danh mục (đường code khác: pandas pivot)
for v in MAIN[:3]:
    h = pd.read_csv(os.path.join(OUT, f"holdings_S1_{v}.csv")); m = monthly[f"S1_{v}"]
    R = vp[vp.ym >= "2014-06"].pivot(index="ym", columns="ticker", values="ret1"); P = vp[vp.ym >= "2014-06"].pivot(index="ym", columns="ticker", values="t1_close")
    nav = 1e9; wprev = pd.Series(dtype=float)
    for ym in YMS:
        ts = [t for t in h[h.ym == ym].ticker if pd.notna(P.loc[ym].get(t))]
        w = pd.Series(1.0 / len(ts), index=ts) if ts else pd.Series(dtype=float)
        turn = w.subtract(wprev, fill_value=0).abs().sum()
        r = R.loc[ym].reindex(ts).fillna(0.0)
        nav = nav * (1 - 0.001 * turn) * (1 + float((w * r).sum()))
        wd = w * (1 + r); wprev = wd / wd.sum() if len(wd) else wd
    nav_main = 1e9 * float(np.prod(1 + m.ret.values))
    print(f"SELFCHECK S1_{v}: NAV chính {nav_main:,.2f} VND | tính lại {nav:,.2f} VND | lệch {abs(nav - nav_main):.4f} VND")
pd.set_option("display.width", 220)
print(S[S.strategy.str.contains("EW_|VNINDEX|" + "|".join(MAIN[:7]))].round(3).to_string())
