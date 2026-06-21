# -*- coding: utf-8 -*-
"""value_horizon_ic.py — establish the RIGHT YARDSTICK for a value-book leg.
User insight: value doesn't rise with trend like momentum/LAG -> measuring it with a short-horizon
(fwd_1m/3m) momentum-style metric understates it. Test: forward IC of value signals (pb_z, earn_yield
1/PE, cfo_yield 1/PCF) vs momentum (mom_200) at horizons 1m/3m/6m/12m, quality universe (ticker_prune,
gate-ish), month-end sampled, 2012+ (pb_z exists). If |IC_value| GROWS with horizon while momentum is
flat/decays -> value is a long-horizon edge -> the book needs long holds + a long-horizon measure.
"""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude"); os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq

q = """
WITH base AS (
  SELECT ticker, time, Close, PE, PCF,
    SAFE_DIVIDE(PB-PB_MA5Y, NULLIF(PB_SD5Y,0)) AS pbz,
    SAFE_DIVIDE(Close, NULLIF(MA200,0))-1 AS mom200,
    CAST(FLOOR(ICB_Code/1000) AS INT64) AS sec,
    LEAD(Close,21)  OVER w AS c1,  LEAD(Close,63)  OVER w AS c3,
    LEAD(Close,126) OVER w AS c6,  LEAD(Close,252) OVER w AS c12,
    ROW_NUMBER() OVER (PARTITION BY ticker, FORMAT_DATE('%Y-%m',time) ORDER BY time DESC) AS rn_me
  FROM tav2_bq.ticker_prune
  WHERE time >= '2012-01-01' AND PE>0 AND PB_SD5Y>0 AND Close>0
    AND ROE_Min5Y>=0.10 AND FSCORE>=5
  WINDOW w AS (PARTITION BY ticker ORDER BY time))
SELECT time, ticker, sec, pbz, mom200,
  SAFE_DIVIDE(1.0,PE) AS ey, SAFE_DIVIDE(1.0,PCF) AS cfy,
  SAFE_DIVIDE(c1,Close)-1 AS r1, SAFE_DIVIDE(c3,Close)-1 AS r3,
  SAFE_DIVIDE(c6,Close)-1 AS r6, SAFE_DIVIDE(c12,Close)-1 AS r12
FROM base WHERE rn_me=1"""
d = bq(q); d["time"] = pd.to_datetime(d["time"])
print(f"panel: {len(d):,} month-end obs, {d['ticker'].nunique()} tickers, "
      f"{d['time'].min().date()} -> {d['time'].max().date()}")

# sector-neutral earn-yield (demean 1/PE within sector each month)
d["ey_sn"] = d["ey"] - d.groupby(["time","sec"])["ey"].transform("mean")
d["vscore"] = 0.35*(-d["pbz"]) + 0.65*( (d["ey_sn"]-d.groupby("time")["ey_sn"].transform("mean"))
                                        / d.groupby("time")["ey_sn"].transform("std") )
# note: higher vscore = cheaper (pb_z low + high earn-yield). pb_z sign flipped so + = cheap.

def spearman(a, b):
    m = a.notna() & b.notna()
    if m.sum() < 20: return np.nan
    return a[m].rank().corr(b[m].rank())

sigs = {"pb_z(cheap=-pbz)": -d["pbz"], "earn_yield(1/PE)": d["ey"], "cfo_yield(1/PCF)": d["cfy"],
        "value_score(8L v2)": d["vscore"], "momentum(MA200)": d["mom200"]}
hor = {"1m":"r1","3m":"r3","6m":"r6","12m":"r12"}
d["_ym"] = d["time"].dt.to_period("M")
print(f"\n{'signal':22s} " + "  ".join(f"{h:>7s}" for h in hor))
rows = {}
for nm, s in sigs.items():
    dd = d.assign(_s=s)
    line = []
    for h, col in hor.items():
        ics = [spearman(g["_s"], g[col]) for _, g in dd.groupby("_ym") if g[col].notna().sum() >= 20]
        ics = [x for x in ics if x == x]
        line.append(np.mean(ics) if ics else np.nan)
    rows[nm] = line
    print(f"{nm:22s} " + "  ".join(f"{v:+7.3f}" for v in line))
print("\n(IC = mean monthly Spearman vs forward return; + = predictive. "
      "value should RISE toward 12m; momentum should fade/flip.)")
