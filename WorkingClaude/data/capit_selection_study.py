# -*- coding: utf-8 -*-
"""capit_selection_study.py — which NAMES within a CAPIT washout basket recover best?
Per-name realized P&L (from the audit ledger) vs entry-time characteristics, scored by
WITHIN-EVENT rank IC (demean by event => isolates name-selection from event-timing).

Axes (incl. user's ideas): valuation PB_z, stock own 52w drawdown depth, quality (FSCORE/
ROIC5Y/ROE_Min5Y/8L), sector ICB, momentum/technicals (D_RSI/D_MACDdiff/D_CMF/D_CMB/C_L1W/C_L1M),
and the stock's OWN historical rebound strength after past >=25% drops (causal).
"""
import os, sys, io, pickle, bisect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
def _corr(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0: return np.nan
    return float(np.corrcoef(a, b)[0, 1])
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq

pos = pd.read_csv("data/capit_positions.csv", parse_dates=["entry"])
print(f"positions {len(pos)} | tickers {pos['ticker'].nunique()} | events {pos['evidx'].nunique()}")

# ---------- 1. entry-time fundamentals/technicals from BQ ----------
tks = sorted(pos["ticker"].unique()); dates = sorted(pos["entry"].dt.strftime("%Y-%m-%d").unique())
in_tk = ",".join(f"'{t}'" for t in tks); in_dt = ",".join(f"DATE '{d}'" for d in dates)
f = bq(f"""SELECT t.ticker, t.time, t.Close, t.PB, t.PB_MA5Y, t.PB_SD5Y, t.PE,
  t.FSCORE, t.ROIC5Y, t.ROE_Min5Y, t.D_RSI, t.D_MACDdiff, t.D_CMF, t.D_CMB,
  t.C_L1W, t.C_L1M, t.ICB_Code
FROM tav2_bq.ticker t WHERE t.ticker IN ({in_tk}) AND t.time IN ({in_dt})""")
f["time"] = pd.to_datetime(f["time"])
f["PB_z"] = (f["PB"] - f["PB_MA5Y"]) / f["PB_SD5Y"]
f["sector"] = (f["ICB_Code"] // 1000).astype("Int64")
d = pos.merge(f, left_on=["ticker", "entry"], right_on=["ticker", "time"], how="left")
print(f"  fundamentals matched: {d['PB'].notna().sum()}/{len(d)}")

# 8L rating (point-in-time)
r8 = bq(f"SELECT f.ticker, f.time, f.rating AS r8l FROM tav2_bq.fa_ratings_8l f WHERE f.ticker IN ({in_tk})")
r8["time"] = pd.to_datetime(r8["time"]); r8 = r8.sort_values("time")
d = d.sort_values("entry")
d = pd.merge_asof(d, r8, left_on="entry", right_on="time", by="ticker", direction="backward", suffixes=("", "_r8"))

# ---------- 2. stock own 52w drawdown + historical rebound strength (causal, from earnings_px) ----------
px = pickle.load(open("data/earnings_px.pkl", "rb")); px["time"] = pd.to_datetime(px["time"])
pxp = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index()
def own_dd52(tk, e):
    if tk not in pxp.columns: return np.nan
    s = pxp[tk].loc[:e].dropna()
    if len(s) < 60: return np.nan
    return s.iloc[-1] / s.tail(252).max() - 1
def rebound_strength(tk, e, drop=0.25, h=60, min_ep=3):
    """Mean forward-h return after past days where the stock was >=drop below its trailing 252d high.
    Fully causal: only episodes whose h-day forward window completed strictly before entry e."""
    if tk not in pxp.columns: return np.nan
    s = pxp[tk].loc[:e].dropna()
    if len(s) < 300: return np.nan
    v = s.values; hi = pd.Series(v).rolling(252, min_periods=60).max().values
    dd = v / hi - 1
    outs = []
    for i in range(len(v) - h):
        if dd[i] <= -drop and (i == 0 or dd[i-1] > -drop):   # entry into the drop zone (episode start)
            if v[i] > 0: outs.append(v[i + h] / v[i] - 1)
    return float(np.mean(outs)) if len(outs) >= min_ep else np.nan
d["own_dd52"] = [own_dd52(t, e) for t, e in zip(d["ticker"], d["entry"])]
d["rebound"]  = [rebound_strength(t, e) for t, e in zip(d["ticker"], d["entry"])]
print(f"  own_dd52 ok: {d['own_dd52'].notna().sum()} | rebound ok: {d['rebound'].notna().sum()}")

# ---------- 3. WITHIN-EVENT rank IC (demean by event) ----------
FEATS = {"PB_z": "-", "PB": "-", "PE": "-", "own_dd52": "-", "FSCORE": "+", "ROIC5Y": "+",
         "ROE_Min5Y": "+", "r8l": "-", "D_RSI": "-", "D_MACDdiff": "+", "D_CMF": "+",
         "D_CMB": "?", "C_L1W": "-", "C_L1M": "-", "rebound": "+"}
def within_event_ic(df, feat):
    sub = df[["evidx", "ret", feat]].dropna()
    sub = sub[sub.groupby("evidx")[feat].transform("count") >= 3]   # events with >=3 names
    if sub["evidx"].nunique() < 2 or len(sub) < 12: return (np.nan, 0, 0)
    rr = sub.groupby("evidx")["ret"].rank() - sub.groupby("evidx")["ret"].transform(lambda x: (len(x)+1)/2)
    fr = sub.groupby("evidx")[feat].rank() - sub.groupby("evidx")[feat].transform(lambda x: (len(x)+1)/2)
    return (_corr(fr, rr), len(sub), sub["evidx"].nunique())
def pooled_ic(df, feat):
    sub = df[["ret", feat]].dropna()
    return _corr(sub[feat].rank(), sub["ret"].rank()) if len(sub) > 12 else np.nan

print("\n" + "=" * 78)
print("SELECTION IC — realized CAPIT return vs entry feature")
print("(within-event = name-selection skill; expected-sign in [ ])")
print(f"{'feature':<12}{'exp':>4}{'within_IC':>11}{'pooled_IC':>11}{'n':>5}{'events':>7}")
print("-" * 78)
res = []
for ft, sign in FEATS.items():
    if ft not in d.columns: continue
    wic, n, nev = within_event_ic(d, ft); pic = pooled_ic(d, ft)
    res.append((ft, sign, wic, pic, n, nev))
for ft, sign, wic, pic, n, nev in sorted(res, key=lambda x: -(abs(x[2]) if not np.isnan(x[2]) else -1)):
    print(f"{ft:<12}{sign:>4}{wic:>+11.3f}{pic:>+11.3f}{n:>5}{nev:>7}")

# ---------- 4. quintile spread of the top within-event feature ----------
top = max([r for r in res if not np.isnan(r[2])], key=lambda x: abs(x[2]))
ftop = top[0]
print(f"\nTop within-event discriminator: {ftop} (within_IC {top[2]:+.3f})")
sub = d[["evidx", "ret", ftop]].dropna().copy()
sub["q"] = sub.groupby("evidx")[ftop].transform(lambda x: pd.qcut(x.rank(method="first"), min(3, x.nunique()), labels=False, duplicates="drop"))
print(f"  tercile of {ftop} within each event -> mean realized CAPIT return:")
print(sub.groupby("q")["ret"].agg(["mean", "median", "count"]).to_string())

# sector tilt (descriptive)
print("\nBy sector (ICB top-level) — mean realized return (n>=5):")
sec = d.dropna(subset=["sector"]).groupby("sector")["ret"].agg(["mean", "median", "count"])
print(sec[sec["count"] >= 5].sort_values("mean", ascending=False).to_string())

d.to_csv("data/capit_selection_features.csv", index=False)
print("\nsaved data/capit_selection_features.csv")
