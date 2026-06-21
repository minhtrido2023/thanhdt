# -*- coding: utf-8 -*-
"""
validate_minstay_variants.py
=============================
Walk-forward + year-by-year validation of V2_minstay variants.

Top candidates from Phase 3:
  V2_minstay15: 37 tx, CAGR@0.3%=16.66%, Sh=0.83, DD=-18.4%
  V2_minstay30: 20 tx, CAGR@0.3%=17.12%, Sh=0.82, DD=-21.4%

Tests:
  (1) IS = 2014-2019 / OOS = 2020-2026 walk-forward
  (2) Year-by-year CAGR (system vs TQ34b vs B&H)
  (3) DD episodes: how does each handle 2018, 2020 COVID, 2022 bear?
  (4) Mechanism check: what gets absorbed?
       For each variant, identify segments TQ34b had that got absorbed.
       Check VNI return during those absorbed periods.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing, STATE_ALLOC, STATE_NAMES

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

def min_stay_filter(states, min_days):
    if min_days <= 1: return states.copy()
    out = states.copy(); changed = True
    while changed:
        changed = False; i = 0
        while i < len(out):
            j = i+1
            while j < len(out) and out[j] == out[i]: j += 1
            if (j-i) < min_days:
                fill = out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

# Load
tq = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)
state_base = tq["state"].values.astype(int)

# Build variants
state_ms15 = min_stay_filter(state_base, 15)
state_ms30 = min_stay_filter(state_base, 30)
state_ms20 = min_stay_filter(state_base, 20)

# Buy & hold ref
bh = pd.DataFrame({"time": tq["time"], "state": 4})

# ----- (1) IS/OOS Walk-forward -----------------------------------------------
print("="*80)
print("  WALK-FORWARD VALIDATION (IS 2014-2019 / OOS 2020-2026)")
print("="*80)

splits = [
    ("Full 2014-2026",   "2014-01-01", None),
    ("IS 2014-2019",     "2014-01-01", "2019-12-31"),
    ("OOS 2020-2026",    "2020-01-01", None),
    ("Pre-COVID 14-20",  "2014-01-01", "2020-02-28"),
    ("Post-COVID 20-26", "2020-03-01", None),
]

print(f"\n  {'Period':<22} {'Strategy':<14} {'CAGR_0.1':>9} {'CAGR_0.3':>9} {'Sh_0.3':>7} {'DD_0.3':>7}")
print("  " + "-"*80)

for label, sd, ed in splits:
    for sname, sarr in [("TQ34b", state_base), ("ms15", state_ms15), ("ms20", state_ms20), ("ms30", state_ms30)]:
        df_v = pd.DataFrame({"time": tq["time"], "state": sarr})
        try:
            r01 = simulate_timing(df_v, start_date=sd, end_date=ed, tc=0.001)
            r03 = simulate_timing(df_v, start_date=sd, end_date=ed, tc=0.003)
            print(f"  {label:<22} {sname:<14} {r01['cagr']*100:>+7.2f}% {r03['cagr']*100:>+7.2f}% {r03['sharpe']:>7.2f} {r03['max_dd']*100:>+6.1f}%")
        except Exception as e:
            print(f"  {label:<22} {sname:<14} ERROR {e}")
    # B&H ref
    r_bh = simulate_timing(bh, start_date=sd, end_date=ed, tc=0.003)
    print(f"  {label:<22} {'B&H':<14} {r_bh['cagr']*100:>+7.2f}% {r_bh['cagr']*100:>+7.2f}% {r_bh['sharpe']:>7.2f} {r_bh['max_dd']*100:>+6.1f}%")
    print()

# ----- (2) Year-by-year ------------------------------------------------------
print("\n"+"="*80)
print("  YEAR-BY-YEAR CAGR (TC=0.30%)")
print("="*80)

# Build NAV series for each variant
dfs = {
    "TQ34b": pd.DataFrame({"time": tq["time"], "state": state_base}),
    "ms15":  pd.DataFrame({"time": tq["time"], "state": state_ms15}),
    "ms20":  pd.DataFrame({"time": tq["time"], "state": state_ms20}),
    "ms30":  pd.DataFrame({"time": tq["time"], "state": state_ms30}),
    "B&H":   bh,
}
nav_series = {}
for name, dfv in dfs.items():
    res = simulate_timing(dfv, start_date="2014-01-01", tc=0.003)
    nav_series[name] = res["nav_series"]

print(f"\n  {'Year':<6} {'TQ34b':>8} {'ms15':>8} {'ms20':>8} {'ms30':>8} {'B&H':>8} {'Δms15-TQ':>10}")
years_list = sorted(nav_series["TQ34b"].index.year.unique())
totals = {n: 1.0 for n in nav_series}
for yr in years_list:
    rets = {}
    for name, nav in nav_series.items():
        msk = nav.index.year == yr
        if msk.sum() < 5: continue
        sub = nav[msk]
        rets[name] = sub.iloc[-1]/sub.iloc[0] - 1
    if not rets: continue
    delta = (rets.get("ms15",0) - rets.get("TQ34b",0)) * 100
    print(f"  {yr:<6} {rets.get('TQ34b',0)*100:>+7.1f}% {rets.get('ms15',0)*100:>+7.1f}% "
          f"{rets.get('ms20',0)*100:>+7.1f}% {rets.get('ms30',0)*100:>+7.1f}% "
          f"{rets.get('B&H',0)*100:>+7.1f}% {delta:>+8.1f}pp")

# ----- (3) Absorption analysis: what got eaten? ------------------------------
print("\n"+"="*80)
print("  WHAT min_stay(15) ABSORBED (post-2014)")
print("="*80)

mask14 = (tq["time"] >= "2014-01-01").values
t14 = tq["time"][mask14].reset_index(drop=True)
sb14 = state_base[mask14]
ms14 = state_ms15[mask14]

# Find segments where ms15 differs from base
# For each base segment that got absorbed, find: original state, dur, absorbed-to-state,
# and VNI return during that period
vni = pd.read_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"), usecols=["time","Close"])
vni["time"] = pd.to_datetime(vni["time"])
vni_map = vni.set_index("time")["Close"]

abs_segs = []
i = 0
while i < len(sb14):
    j = i+1
    while j < len(sb14) and sb14[j] == sb14[i]: j += 1
    dur = j - i
    if dur < 15:  # was an absorption target
        orig = int(sb14[i])
        absorbed_to = int(ms14[i])
        if orig != absorbed_to:
            t_s = t14.iloc[i]; t_e = t14.iloc[j-1]
            c_s = vni_map.get(t_s); c_e = vni_map.get(t_e)
            ret_period = (c_e/c_s - 1)*100 if c_s and c_e else np.nan
            abs_segs.append((t_s.date(), t_e.date(), STATE_NAMES[orig], STATE_NAMES[absorbed_to], dur, ret_period))
    i = j

print(f"  Segments absorbed by ms15 (post-2014): {len(abs_segs)}")
print(f"  {'Start':<12} {'End':<12} {'Was':<10} {'->':>3} {'Now':<10} {'dur':>4} {'VNI_ret':>8}")
for s, e, w, n, d, r in abs_segs[:30]:
    print(f"  {str(s):<12} {str(e):<12} {w:<10} {'->':>3} {n:<10} {d:>4d} {r:>+7.2f}%")
if len(abs_segs) > 30:
    print(f"  ... {len(abs_segs)-30} more")

# Aggregate: how many absorbed CRISIS days, etc.
print(f"\n  Aggregate absorption (orig state -> count of segments):")
abs_df = pd.DataFrame(abs_segs, columns=["start","end","was","now","dur","ret"])
agg_was = abs_df.groupby("was").size().sort_values(ascending=False)
for w, c in agg_was.items():
    total_days = abs_df[abs_df["was"]==w]["dur"].sum()
    mean_ret = abs_df[abs_df["was"]==w]["ret"].mean()
    print(f"    {w:<10} segments={c:<3d}  total_days={total_days:<4d}  mean_VNI_ret_during={mean_ret:+.2f}%")

# Key question: when ms15 absorbs a CRISIS sandwich into BEAR/NEUTRAL,
# what's VNI return during those days? If positive, ms15 wins.
print(f"\n  CRISIS absorptions specifically (where ms15 stays NON-crisis):")
crisis_absorbed = abs_df[abs_df["was"]=="CRISIS"]
if len(crisis_absorbed) > 0:
    print(f"    {len(crisis_absorbed)} CRISIS segments absorbed, total {crisis_absorbed['dur'].sum()} days")
    print(f"    Mean VNI return during absorption: {crisis_absorbed['ret'].mean():+.2f}%")
    print(f"    Positive: {(crisis_absorbed['ret']>0).sum()}/{len(crisis_absorbed)}")
    print(f"    -- if mean > 0, ms15 correctly stayed in equity during false CRISIS alarms")
