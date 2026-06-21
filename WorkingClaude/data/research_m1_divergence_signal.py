# -*- coding: utf-8 -*-
"""research_m1_divergence_signal.py — validate the megacap-divergence radar (M1) full-history BEFORE
wiring an ETF overlay. M1(t) = VNINDEX trailing-6M return - median(prune-stock trailing-6M return).
Checks: (1) does M1>thr fire in known megacap phases (2021/2025) and NOT whipsaw in broad 2014-19?
(2) when M1>thr, does E1VFVN30 (megacap) keep beating the broad market forward (so parking pays)?
"""
import os, sys, io, bisect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq

# daily M1 divergence (VNINDEX 6m - median prune 6m) + median-stock 6m fwd, 2013-now
q = """
WITH base AS (
  SELECT t.time, t.ticker, SAFE_DIVIDE(t.Close, LAG(t.Close,126) OVER(PARTITION BY t.ticker ORDER BY t.time))-1 r6
  FROM tav2_bq.ticker t WHERE t.time>=DATE '2013-01-01'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)),
vni AS (SELECT t.time, SAFE_DIVIDE(t.Close, LAG(t.Close,126) OVER(ORDER BY t.time))-1 vr6
  FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX' AND t.time>=DATE '2013-01-01')
SELECT b.time, AVG(vni.vr6) vni6, APPROX_QUANTILES(b.r6,100)[OFFSET(50)] med6
FROM base b JOIN vni USING(time) GROUP BY b.time ORDER BY b.time"""
m = bq(q); m["time"] = pd.to_datetime(m["time"]); m = m.set_index("time")
m["M1"] = (m["vni6"] - m["med6"]) * 100
# E1VFVN30 (megacap ETF) + VNINDEX close for forward returns
px = bq("""SELECT t.time, t.ticker, t.Close FROM tav2_bq.ticker t
WHERE t.ticker IN ('E1VFVN30','VNINDEX') AND t.time>=DATE '2014-01-01' ORDER BY t.time""")
px["time"] = pd.to_datetime(px["time"])
etf = px[px["ticker"]=="E1VFVN30"].set_index("time")["Close"]
vnix = px[px["ticker"]=="VNINDEX"].set_index("time")["Close"]

idx = m.index
M1 = m["M1"]
THR = 8.0
fire = (M1 > THR)
print(f"M1 divergence (VNINDEX 6m - median-stock 6m), THR={THR}pp")
print(f"  range [{M1.min():.0f}, {M1.max():.0f}] | %time fire {fire.mean()*100:.0f}%")

# episodes (gap>=20 trading rows)
print("\nFIRE EPISODES (M1>thr clusters) — check timing vs known megacap phases:")
fi = list(np.where(fire.values)[0]); prev=-999
def fwd(s, t0, h):
    i=s.index.searchsorted(t0); j=i+h
    return (s.iloc[j]/s.iloc[i]-1)*100 if i<len(s) and j<len(s) else np.nan
ep_starts=[]
for k in fi:
    if k-prev>20:
        t0=idx[k]; ep_starts.append(t0)
        # forward 120d: E1VFVN30 vs VNINDEX (both megacap-ish) and vs median-stock proxy
        e120=fwd(etf,t0,120); v120=fwd(vnix,t0,120)
        print(f"  {t0.date()}  M1={M1.iloc[k]:+5.0f}pp -> fwd120 E1VFVN30 {e120:+6.1f}%  VNINDEX {v120:+6.1f}%")
    prev=k

# whipsaw check by year + predictive value
print("\nBy YEAR: %days fire | mean M1 | (megacap regime if high)")
m["yr"]=m.index.year
for yr,g in m.groupby("yr"):
    f=(g["M1"]>THR); print(f"  {yr}: fire {f.mean()*100:>3.0f}%  meanM1 {g['M1'].mean():+5.1f}pp")

# predictive: when M1>thr, is fwd120 E1VFVN30 > fwd120 median-stock? (does parking megacap pay)
print("\nPREDICTIVE (does megacap keep winning when M1>thr): fwd120 E1VFVN30 vs broad-median proxy")
samp=[idx[k] for k in range(len(idx)) if fire.iloc[k]][::20]
e=[fwd(etf,t,120) for t in samp]; v=[fwd(vnix,t,120) for t in samp]
e=np.array([x for x in e if not np.isnan(x)]);
print(f"  fire days (n~{len(e)}): E1VFVN30 fwd120 mean {np.nanmean(e):+.1f}% | win {(e>0).mean()*100:.0f}%")
nf=[idx[k] for k in range(len(idx)) if not fire.iloc[k]][::20]
en=np.array([x for x in (fwd(etf,t,120) for t in nf) if not np.isnan(x)])
print(f"  non-fire days (n~{len(en)}): E1VFVN30 fwd120 mean {np.nanmean(en):+.1f}% | win {(en>0).mean()*100:.0f}%")
m[["M1"]].to_csv("data/m1_divergence_daily.csv")
print("\nsaved data/m1_divergence_daily.csv")
