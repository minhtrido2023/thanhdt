# -*- coding: utf-8 -*-
"""capit_ew_maturity.py — test the user's refinement (2026-06-12): the cap-weighted VNINDEX is
masked by a few megacaps (VIC-led 2025), so INDEX dd52w mis-measures how mature a decline is.
The right lens is EQUAL-WEIGHT / breadth: how far has the MEDIAN stock fallen from its own 52w
high, and what share of stocks are below MA200.

Prediction: 2025-10-20 (index shallow, won) should show a DEEP equal-weight correction (mature),
while 2022-04-19 (index shallow, lost) should show a SHALLOW one (whole market still near 2021 top).
If EW-maturity separates them where index dd52w could not, it is the better gate input.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq

A = pd.read_csv("data/v23c_golive_audit_2014_now.csv", low_memory=False)
ev = A[A["record_type"] == "EVENT_CAPIT"].copy()
ev["ymd"] = pd.to_datetime(ev["ymd"]); ev = ev.reset_index(drop=True)

# index dd52w + fwd60 (recompute from VNINDEX for context)
vni = bq("SELECT t.time, t.Close FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX' "
         "AND t.time BETWEEN DATE '2013-01-01' AND DATE '2026-06-11' ORDER BY t.time")
vni["time"] = pd.to_datetime(vni["time"]); vd = list(vni["time"]); vc = vni["Close"].values
import bisect
def idx_dd52(d0):
    i = bisect.bisect_right(vd, pd.Timestamp(d0)) - 1
    lo = max(0, i - 252)
    return (vc[i] / np.nanmax(vc[lo:i+1]) - 1) * 100
def fwd60(d0):
    i = bisect.bisect_left(vd, pd.Timestamp(d0))
    return (vc[i+60]/vc[i]-1)*100 if i+60 < len(vc) else np.nan

def ew_maturity(d0):
    """Equal-weight broad-market maturity at d0 from ticker_prune (causal 1y window).
    Returns (median dd-from-own-52w-high %, p25 dd %, % below MA200)."""
    q = f"""
    WITH win AS (
      SELECT ticker, time, Close, MA200,
        MAX(Close) OVER (PARTITION BY ticker ORDER BY time
                         ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS hi52,
        ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS rn
      FROM tav2_bq.ticker_prune
      WHERE time BETWEEN DATE_SUB(DATE '{d0.date()}', INTERVAL 365 DAY) AND DATE '{d0.date()}'
    )
    SELECT
      APPROX_QUANTILES(SAFE_DIVIDE(Close,hi52)-1, 100)[OFFSET(50)] AS med_dd,
      APPROX_QUANTILES(SAFE_DIVIDE(Close,hi52)-1, 100)[OFFSET(25)] AS p25_dd,
      AVG(CASE WHEN MA200>0 AND Close<MA200 THEN 1.0 ELSE 0 END) AS pct_below,
      COUNT(*) AS n
    FROM win WHERE rn=1 AND Close>0 AND hi52>0"""
    r = bq(q)
    if r.empty: return (np.nan, np.nan, np.nan, 0)
    return (float(r["med_dd"][0])*100, float(r["p25_dd"][0])*100,
            float(r["pct_below"][0])*100, int(r["n"][0]))

print("CAPIT events — INDEX dd52w vs EQUAL-WEIGHT broad-market maturity")
print("(user: index masked by megacaps; EW = how far the MEDIAN stock has fallen)\n")
print(f"{'date':>11} {'st':>2} | {'idx_dd52w':>9} | {'EW_med_dd':>9} {'EW_p25_dd':>9} {'%<MA200':>8} (n) | {'fwd60':>7}")
print("-" * 86)
rows = []
for r in ev.itertuples():
    d0 = r.ymd
    idd = idx_dd52(d0); med, p25, below, n = ew_maturity(d0); f = fwd60(d0)
    rows.append({"date": d0.date(), "state": int(r.state), "idx_dd52w": idd,
                 "ew_med_dd": med, "ew_p25_dd": p25, "pct_below_ma200": below, "fwd60": f})
    print(f"{str(d0.date()):>11} {int(r.state):>2} | {idd:>+8.1f}% | {med:>+8.1f}% {p25:>+8.1f}% "
          f"{below:>7.0f}% ({n:>3}) | {f:>+6.1f}%")
d = pd.DataFrame(rows)

print("\n" + "=" * 70)
print("KEY CONTRAST — the two index-shallow events that disagreed on outcome:")
for dt in ["2022-04-19", "2025-10-20"]:
    rr = d[d["date"].astype(str) == dt]
    if len(rr):
        rr = rr.iloc[0]
        print(f"  {dt}: index_dd52w {rr['idx_dd52w']:+.1f}% (both shallow) | "
              f"EW_med_dd {rr['ew_med_dd']:+.1f}%  %<MA200 {rr['pct_below_ma200']:.0f}%  -> fwd60 {rr['fwd60']:+.1f}%")
print("  If user is right: 2025-10 EW deeply corrected (mature) vs 2022-04 EW shallow (fresh).")

# does EW_med_dd rank-separate winners/losers better than index dd52w?
print("\nCorrelation with fwd60 (more-negative dd = deeper correction = should help):")
for col in ["idx_dd52w", "ew_med_dd", "ew_p25_dd", "pct_below_ma200"]:
    sub = d[["fwd60", col]].dropna()
    if len(sub) > 3:
        print(f"  corr(fwd60, {col:<16}) = {sub['fwd60'].corr(sub[col]):+.2f}")
d.to_csv("data/capit_ew_maturity_table.csv", index=False)
print("\nSaved data/capit_ew_maturity_table.csv")
