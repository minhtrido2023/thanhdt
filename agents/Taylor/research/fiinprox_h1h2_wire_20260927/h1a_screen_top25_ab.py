#!/usr/bin/env python3
"""H1(a) — the ONLY continuous (non-binary) use of the 8L rating in the *_screen.py family:
     top25 = set(m.sort_values(["rating","tv"], ascending=False).head(25).ticker)
   present verbatim in 15 screens (aviation, bank_compounder, compounder, construction, energy,
   fertchem_rubber, fnb, livestock, logistics_port, re_compounder, retail_compounder, securities,
   steel_buildmat, tech, textile). It feeds ONLY the printed diagnostic `overlap_8l_top25` in each
   screen's verdict JSON -- it selects nothing and sizes nothing.
   Measured before/after the H1 wire with the screens' exact recipe."""
import glob, numpy as np, pandas as pd, os
os.chdir("/home/trido/thanhdt/WorkingClaude")
SBX = os.environ.get("H1_AB_DIR", os.path.dirname(os.path.abspath(__file__)))
A = pd.read_csv(f"{SBX}/ab_old.csv", parse_dates=["eff_date"])
B = pd.read_csv(f"{SBX}/ab_new.csv", parse_dates=["eff_date"])
pr = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Trading_Value_1M_P50"])
                for f in sorted(glob.glob("data/bq_cache/ticker_prune/*.parquet"))])
pr["time"] = pd.to_datetime(pr.time)
pr = pr[pr.Trading_Value_1M_P50 >= 1e9]                      # screens' LIQ floor
dates = pd.Series(sorted(d for d in pr.time.unique() if pd.Timestamp(d) >= pd.Timestamp("2014-07-01")))
grid = dates.groupby(dates.dt.to_period("M")).max().tolist()  # month-end rebalance grid

def top25(R, d):
    asof = R[R.eff_date <= d].sort_values("eff_date").groupby("ticker").tail(1)
    liq = pr[pr.time == d][["ticker", "Trading_Value_1M_P50"]].rename(
        columns={"Trading_Value_1M_P50": "tv"})
    m = asof.merge(liq, on="ticker", how="inner")
    return None if len(m) < 25 else set(m.sort_values(["rating", "tv"], ascending=False).head(25).ticker)

same = diff = 0; jac = []; swapped = []
for d in grid:
    a, b = top25(A, d), top25(B, d)
    if a is None or b is None: continue
    if a == b: same += 1
    else: diff += 1; jac.append(len(a & b) / len(a | b)); print(f"  DIFF {d.date()}: -{sorted(a-b)} +{sorted(b-a)}")
    swapped.append(len(a ^ b))
print(f"months evaluated     : {same+diff} ({grid[0].date()} .. {grid[-1].date()})")
print(f"top-25 IDENTICAL     : {same}")
print(f"top-25 DIFFERENT     : {diff}" + (f" (Jaccard median {np.median(jac):.3f})" if jac else ""))
print(f"names swapped/month  : mean {np.mean(swapped):.2f}, max {max(swapped)}")
print("\nNB: ascending=False on rating means these screens pick the WORST-rated 25 names. That is a")
print("pre-existing oddity of the screen family, NOT introduced or changed by this wire.")
