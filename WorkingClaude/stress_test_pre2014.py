# -*- coding: utf-8 -*-
"""
stress_test_pre2014.py
======================
(B) Pre-2014 stress test: 2007 GFC + 2011 inflation + 2012-2013 stagnation.

Test the asymmetric causal confirmation variants (d=15, c=25-35, eb=25-30)
against TQ34b raw and B&H, on periods:
  - 2007-01-01 to 2013-12-31 (full pre-2014)
  - 2007 alone (peak then crash starts)
  - 2008 (GFC crash year)
  - 2009 (recovery)
  - 2010 (sideways)
  - 2011 (inflation crisis, -27% VNI)
  - 2012-2013 (stagnation)

Critical question: do longer confirmation delays HURT in fast bear markets?
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

def min_stay_causal_asym(states, default_min, target_state_min):
    out = states.copy()
    committed = states[0]
    pending_state = states[0]
    pending_run = 1
    out[0] = committed
    for t in range(1, len(states)):
        s = states[t]
        if s == pending_state:
            pending_run += 1
        else:
            pending_state = s
            pending_run = 1
        if pending_state in target_state_min:
            need = target_state_min[pending_state]
        else:
            need = default_min
        if pending_run >= need and pending_state != committed:
            committed = pending_state
        out[t] = committed
    return out

tq = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)
state_base = tq["state"].values.astype(int)

# Build 3 variants for stress test
variants = {
    "TQ34b":               (state_base.copy(),                          None),
    "DT_15_30_25":         (min_stay_causal_asym(state_base, 15, {1:30, 5:25}), None),
    "DT_15_25_30":         (min_stay_causal_asym(state_base, 15, {1:25, 5:30}), None),
    "DT_15_35_25 (robust)":(min_stay_causal_asym(state_base, 15, {1:35, 5:25}), None),
    "DT_10_25_25 (light)": (min_stay_causal_asym(state_base, 10, {1:25, 5:25}), None),
    "DT_20_30_30 (heavy)": (min_stay_causal_asym(state_base, 20, {1:30, 5:30}), None),
}
bh = pd.DataFrame({"time": tq["time"], "state": 4})

print("="*90)
print("  (B) PRE-2014 STRESS TEST")
print("="*90)

periods = [
    ("Full pre-2014 (07-13)", "2007-01-01", "2013-12-31"),
    ("2007 (peak/crash)",      "2007-01-01", "2007-12-31"),
    ("2008 GFC",               "2008-01-01", "2008-12-31"),
    ("2009 recovery",          "2009-01-01", "2009-12-31"),
    ("2010 sideways",          "2010-01-01", "2010-12-31"),
    ("2011 inflation crisis",  "2011-01-01", "2011-12-31"),
    ("2012-2013 stagnation",   "2012-01-01", "2013-12-31"),
    ("2008-2011 (worst)",      "2008-01-01", "2011-12-31"),
]

for label, sd, ed in periods:
    print(f"\n[{label}]")
    print(f"  {'Variant':<24} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'vs B&H':>8}")
    r_bh = simulate_timing(bh, start_date=sd, end_date=ed, tc=0.003)
    bh_cagr = r_bh["cagr"]
    for name, (sarr, alloc) in variants.items():
        try:
            df_v = pd.DataFrame({"time": tq["time"], "state": sarr})
            r = simulate_timing(df_v, start_date=sd, end_date=ed, tc=0.003, alloc=alloc)
            bh_d = (r["cagr"] - bh_cagr) * 100
            print(f"  {name:<24} {r['cagr']*100:>+6.2f}% {r['sharpe']:>7.2f} {r['max_dd']*100:>+6.1f}% {r['calmar']:>7.2f} {bh_d:>+6.2f}pp")
        except Exception as e:
            print(f"  {name:<24} ERROR: {e}")
    print(f"  {'B&H VNI':<24} {bh_cagr*100:>+6.2f}% {r_bh['sharpe']:>7.2f} {r_bh['max_dd']*100:>+6.1f}% {r_bh['calmar']:>7.2f}")

# Long-horizon: 2007 to today
print("\n"+"="*90)
print("  19-year horizon (2007-01-01 to 2026-05-26)")
print("="*90)
print(f"  {'Variant':<24} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'FinalNAV':>11}")
r_bh = simulate_timing(bh, start_date="2007-01-01", tc=0.003)
for name, (sarr, alloc) in variants.items():
    df_v = pd.DataFrame({"time": tq["time"], "state": sarr})
    r = simulate_timing(df_v, start_date="2007-01-01", tc=0.003, alloc=alloc)
    print(f"  {name:<24} {r['cagr']*100:>+6.2f}% {r['sharpe']:>7.2f} {r['max_dd']*100:>+6.1f}% {r['calmar']:>7.2f} {r['final_nav']/1e9:>10.3f}B")
print(f"  {'B&H VNI':<24} {r_bh['cagr']*100:>+6.2f}% {r_bh['sharpe']:>7.2f} {r_bh['max_dd']*100:>+6.1f}% {r_bh['calmar']:>7.2f} {r_bh['final_nav']/1e9:>10.3f}B")

# Drawdown comparison during GFC
print("\n"+"="*90)
print("  GFC DRAWDOWN ANALYSIS (peak-to-trough during 2007-2009)")
print("="*90)

for name, (sarr, alloc) in variants.items():
    df_v = pd.DataFrame({"time": tq["time"], "state": sarr})
    r = simulate_timing(df_v, start_date="2007-01-01", end_date="2009-12-31", tc=0.003, alloc=alloc)
    nav = r["nav_series"]
    rm = nav.expanding().max()
    dd = (nav - rm) / rm * 100
    worst_dd = dd.min()
    worst_idx = dd.idxmin()
    peak_idx = nav.loc[:worst_idx].idxmax()
    rec_mask = nav.loc[worst_idx:] >= rm.loc[worst_idx]
    rec_date = rec_mask[rec_mask].index[0] if rec_mask.any() else None
    days_to_rec = (rec_date - peak_idx).days if rec_date is not None else None
    print(f"  {name:<24} peak {peak_idx.date()}, trough {worst_idx.date()}, DD={worst_dd:+.1f}%, "
          f"rec_days={'inf' if days_to_rec is None else days_to_rec}")
