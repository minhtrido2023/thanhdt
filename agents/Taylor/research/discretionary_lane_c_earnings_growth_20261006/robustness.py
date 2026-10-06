"""Robustness for lane C (reads panel.csv/monthly.csv from lane_c_backtest.py). Job Taylor_20261005_180155."""
import os, sys, glob, math
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, WC)
from dsr_pbo_annex import moments, expected_max_sr, dsr, cscv_pbo
OUT = os.path.dirname(os.path.abspath(__file__))
P = pd.read_csv(f"{OUT}/panel.csv", parse_dates=["d", "entry", "exit", "known"])
M = pd.read_csv(f"{OUT}/monthly.csv", parse_dates=["d"]).set_index("d")
P = P.dropna(subset=["ret"])
IS_END, OOS_START = pd.Timestamp("2019-12-31"), pd.Timestamp("2020-01-01")
def tt(x):
    x = pd.Series(x).dropna(); return x.mean(), x.mean() / x.std() * np.sqrt(len(x)), len(x)
def line(name, x):
    x = pd.Series(x).dropna()
    f = tt(x); i = tt(x[x.index <= IS_END]); o = tt(x[x.index >= OOS_START])
    print(f"{name:42s} FULL {f[0]*100:+.2f}%/m t={f[1]:.2f} | IS {i[0]*100:+.2f} t={i[1]:.2f} | OOS {o[0]*100:+.2f} t={o[1]:.2f} (n={f[2]})")
    return dict(name=name, full=f[0], full_t=f[1], is_=i[0], is_t=i[1], oos=o[0], oos_t=o[1])
rm = P.groupby(["d", "route"]).ret.transform("mean"); P["xr"] = P.ret - rm
base = P.groupby("d").ret.mean()
C1 = (P.g_yoy >= 0.30) & (P.g_qoq > 0) & (P.PE > 0) & (P.PE <= 12)
rows = []
print("== 1. outliers ==")
lo, hi = P.groupby("d").ret.transform(lambda s: s.quantile(0.01)), P.groupby("d").ret.transform(lambda s: s.quantile(0.99))
P["rw"] = P.ret.clip(lo, hi)
rows.append(line("C1 gross excess vs BASE (raw)", P[C1].groupby("d").ret.mean() - base))
rows.append(line("C1 excess, stock ret winsor 1/99", P[C1].groupby("d").rw.mean() - P.groupby("d").rw.mean()))
rows.append(line("C1 MEDIAN pick xroute", P[C1].groupby("d").xr.median()))
print(f"   per-pick hit (ret > same-route mean): FULL {(P[C1].xr>0).mean():.3f}  BASE-all {(P.xr>0).mean():.3f}  picks={C1.sum()}")
rows.append(line("C1 median xroute MINUS BASE median xroute", P[C1].groupby("d").xr.median() - P.groupby("d").xr.median()))
for a, b in (("2014", "2019"), ("2020", "2026")):
    w = (P.d >= a) & (P.d <= b + "-12-31")
    print(f"   hit {a}-{b}: C1 {(P[C1 & w].xr>0).mean():.3f} vs BASE {(P[w].xr>0).mean():.3f}; C1 pick xroute quantiles p10/p50/p90 = {P[C1&w].xr.quantile([.1,.5,.9]).round(3).tolist()}")

print("== 2. liquidity (60-session median Trading_Value, bn VND nominal) ==")
tv = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Trading_Value"]) for f in sorted(glob.glob(f"{WC}/data/bq_cache/ticker/*.parquet")) if int(os.path.basename(f)[:4]) >= 2013])
tv["time"] = pd.to_datetime(tv["time"]); tv = tv.drop_duplicates(["time", "ticker"]).pivot(index="time", columns="ticker", values="Trading_Value").sort_index()
liq = tv.rolling(60, min_periods=20).median()
P["liq_bn"] = [liq.at[d, t] / 1e9 if t in liq.columns else np.nan for d, t in zip(P.d, P.ticker)]
print(f"   median liq: C1 picks {P[C1].liq_bn.median():.2f}bn | BASE {P.liq_bn.median():.2f}bn ; share C1 picks <3bn: {(P[C1].liq_bn<3).mean():.2f}")
L3 = P.liq_bn >= 3
rows.append(line("C1 & liq>=3bn excess vs BASE(liq>=3bn)", P[C1 & L3].groupby("d").ret.mean() - P[L3].groupby("d").ret.mean()))
L10 = P.liq_bn >= 10
rows.append(line("C1 & liq>=10bn excess vs BASE(liq>=10bn)", P[C1 & L10].groupby("d").ret.mean() - P[L10].groupby("d").ret.mean()))

print("== 3. dose-response grid (SENSITIVITY, counted as extra trials for DSR) ==")
grid = []
for g in (0.15, 0.30, 0.50):
    for pmax in (8, 12, 15):
        for q in (True, False):
            m = (P.g_yoy >= g) & (P.PE > 0) & (P.PE <= pmax) & ((P.g_qoq > 0) if q else True)
            x = P[m].groupby("d").ret.mean().reindex(base.index).fillna(0) - base
            f, i, o = tt(x), tt(x[x.index <= IS_END]), tt(x[x.index >= OOS_START])
            grid.append(dict(g_yoy=g, pe_max=pmax, qoq=q, avg_n=P[m].groupby("d").size().mean(), full=f[0], full_t=f[1], is_=i[0], is_t=i[1], oos=o[0], oos_t=o[1]))
G = pd.DataFrame(grid); G.to_csv(f"{OUT}/dose_grid.csv", index=False); print(G.round(4).to_string())
# growth-only (no PE cap) and value-only (no growth) decomposition
rows.append(line("growth only: g_yoy>=30% & qoq>0 (no PE cap)", P[(P.g_yoy >= .3) & (P.g_qoq > 0)].groupby("d").ret.mean() - base))
rows.append(line("value only: 0<PE<=12 (no growth)", P[(P.PE > 0) & (P.PE <= 12)].groupby("d").ret.mean() - base))
rows.append(line("PE<=12 & g_yoy<0 (cheap, shrinking)", P[(P.PE > 0) & (P.PE <= 12) & (P.g_yoy < 0)].groupby("d").ret.mean() - base))

print("== 4. DSR / PBO on monthly excess vs BASE ==")
T4 = ["C1_GARP", "C2_PEG", "C3_RUNRATE3", "C4_PEG3"]
X = M[T4].sub(M["BASE"], axis=0)
srs = [moments(X[c].values)[0] for c in T4]
sr, g3, g4 = moments(X["C1_GARP"].values)
grid_srs = list(G.full_t / np.sqrt(len(X)))  # per-month SR = t/sqrt(n)
for N, var in ((4, np.var(srs, ddof=1)), (4 + len(G), np.var(srs + grid_srs, ddof=1))):
    sr0 = expected_max_sr(var, N); p, z = dsr(sr, sr0, g3, g4, len(X))
    print(f"   C1 excess per-month SR={sr:.3f} (ann {sr*np.sqrt(12):.2f}) N_trials={N} SR0={sr0:.3f} DSR={p:.4f}")
pbo, lg, nc, ncfg, T2 = cscv_pbo(X.values, S=8)
print(f"   PBO (CSCV S=8, 4 trials) = {pbo:.3f}  over {nc} splits")

print("== 5. DT5G state at rebalance ==")
st = pd.read_parquet(f"{WC}/data/bq_cache/vnindex_5state_dt5g_live.parquet")
st["time"] = pd.to_datetime(st["time"]); st = st.sort_values("time").set_index("time")["state"]
sx = st.reindex(X.index, method="ffill")
print(pd.DataFrame({"state": sx, "ex": X["C1_GARP"]}).groupby("state").ex.agg(["mean", "count", lambda s: s.mean() / s.std() * np.sqrt(len(s))]).round(4).to_string())

print("== 6. LAG overlap / orthogonality ==")
print(f"   C1 picks: same-quarter LAG event {P[C1].lag_same_q.mean():.3f}, held by LAG at entry {P[C1].lag_held.mean():.3f}, either {(P[C1].lag_same_q|P[C1].lag_held).mean():.3f}")
lag = pd.read_csv(f"{OUT}/lag_events_prodgate.csv", parse_dates=["Release_Date", "entry", "exit"])
px = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Close"]) for f in sorted(glob.glob(f"{WC}/data/bq_cache/ticker/*.parquet")) if int(os.path.basename(f)[:4]) >= 2013])
px["time"] = pd.to_datetime(px["time"]); cl = px.drop_duplicates(["time", "ticker"]).pivot(index="time", columns="ticker", values="Close")
lag = lag.dropna(subset=["entry", "exit"]); lag = lag[lag.ticker.isin(cl.columns)]
lag["r"] = [cl.at[b, t] / cl.at[a, t] - 1 if cl.at[a, t] > 0 else np.nan for t, a, b in zip(lag.ticker, lag.entry, lag.exit)]
lag["m"] = lag.entry.dt.to_period("M")
lagm = lag.groupby("m").r.mean()
hm = lambda idx: (pd.DatetimeIndex(idx) + pd.offsets.MonthBegin(1)).to_period("M")  # rebalance month d -> holding month d+1
bm = base.copy(); bm.index = hm(bm.index)
cx = X["C1_GARP"].copy(); cx.index = hm(cx.index)
J = pd.DataFrame({"c1x": cx, "lagx": lagm - bm.reindex(lagm.index), "lag": lagm, "base": bm}).dropna()
print(f"   LAG proxy (EW event T+5->T+30, by entry month) months={len(J)}; corr(C1 excess, LAG excess)={J.c1x.corr(J.lagx):.3f}; corr(C1 excess, LAG raw)={J.c1x.corr(J.lag):.3f}")
wq = J.lagx <= J.lagx.quantile(0.25)
print(f"   C1 excess in LAG-worst-quartile months: {J.c1x[wq].mean()*100:+.2f}%/m (n={wq.sum()}) vs other {J.c1x[~wq].mean()*100:+.2f}%/m")
noL = C1 & ~P.lag_same_q & ~P.lag_held
rows.append(line("C1 minus any LAG overlap, excess vs BASE", P[noL].groupby("d").ret.mean() - base))
rows.append(line("C1 picks THAT ARE LAG-overlap, excess", P[C1 & ~noL].groupby("d").ret.mean() - base))
print("== 7. turnover / new names ==")
h = P[C1].groupby("d").ticker.apply(set); new = [len(b - a) for a, b in zip(h.iloc[:-1], h.iloc[1:])]
print(f"   C1 names/month median {h.apply(len).median():.0f}, NEW names/month median {np.median(new):.0f} mean {np.mean(new):.1f}")
pd.DataFrame(rows).to_csv(f"{OUT}/robustness_lines.csv", index=False)
