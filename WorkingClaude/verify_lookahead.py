# -*- coding: utf-8 -*-
"""
verify_lookahead.py
===================
Quantify look-ahead bias in min_stay_filter.

Causal version of min_stay:
  At each day t, decide state_causal[t] using only state[0..t].
  Rule: 'state_causal[t] = state[t-min_days+1..t] mode if all agree, else state_causal[t-1]'
  Equivalently: 'wait min_days of agreement before committing to new state'.

Compare:
  A) TQ34b raw (already non-causally smoothed in build)
  B) TQ34b + non-causal min_stay(K) on top  (= what I tested previously)
  C) TQ34b + CAUSAL min_stay(K) -- realistic
  D) Difference B - C = look-ahead bias magnitude
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

def min_stay_noncausal(states, min_days):
    """The standard (non-causal) filter — uses future to find segment end."""
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

def min_stay_causal(states, min_days):
    """Causal: at day t, only commit to a new state once we've seen
       min_days of agreement. Otherwise carry previous committed state."""
    if min_days <= 1: return states.copy()
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
        if pending_run >= min_days and pending_state != committed:
            committed = pending_state
        out[t] = committed
    return out

# Load TQ34b
tq = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)
state_base = tq["state"].values.astype(int)

print("="*80)
print("  LOOK-AHEAD BIAS QUANTIFICATION (TC=0.30%, 2014-2026)")
print("="*80)

print(f"\n  {'Variant':<28} {'#tx':>5} {'CAGR_0.1':>9} {'CAGR_0.3':>9} {'Sh_0.3':>7} {'DD_0.3':>7}")
print("  " + "-"*80)

# Baseline
df_b = pd.DataFrame({"time": tq["time"], "state": state_base})
r01 = simulate_timing(df_b, start_date="2014-01-01", tc=0.001)
r03 = simulate_timing(df_b, start_date="2014-01-01", tc=0.003)
mask14 = (tq["time"] >= "2014-01-01").values
n_tx_b = int((state_base[mask14][1:] != state_base[mask14][:-1]).sum())
print(f"  {'TQ34b baseline':<28} {n_tx_b:>5d} {r01['cagr']*100:>+7.2f}% {r03['cagr']*100:>+7.2f}% {r03['sharpe']:>7.2f} {r03['max_dd']*100:>+6.1f}%")

# For each K, test non-causal AND causal
deltas = []
for K in [3, 5, 7, 10, 15, 20, 30]:
    s_nc = min_stay_noncausal(state_base, K)
    s_c  = min_stay_causal(state_base, K)
    df_nc = pd.DataFrame({"time": tq["time"], "state": s_nc})
    df_c  = pd.DataFrame({"time": tq["time"], "state": s_c})

    r01_nc = simulate_timing(df_nc, start_date="2014-01-01", tc=0.001)
    r03_nc = simulate_timing(df_nc, start_date="2014-01-01", tc=0.003)
    r01_c  = simulate_timing(df_c,  start_date="2014-01-01", tc=0.001)
    r03_c  = simulate_timing(df_c,  start_date="2014-01-01", tc=0.003)

    n_tx_nc = int((s_nc[mask14][1:] != s_nc[mask14][:-1]).sum())
    n_tx_c  = int((s_c[mask14][1:] != s_c[mask14][:-1]).sum())

    print(f"  {f'ms{K} NON-causal (cheating)':<28} {n_tx_nc:>5d} {r01_nc['cagr']*100:>+7.2f}% {r03_nc['cagr']*100:>+7.2f}% {r03_nc['sharpe']:>7.2f} {r03_nc['max_dd']*100:>+6.1f}%")
    print(f"  {f'ms{K} causal (deployable)':<28} {n_tx_c:>5d} {r01_c['cagr']*100:>+7.2f}% {r03_c['cagr']*100:>+7.2f}% {r03_c['sharpe']:>7.2f} {r03_c['max_dd']*100:>+6.1f}%")
    bias = (r03_nc["cagr"] - r03_c["cagr"]) * 100
    deltas.append((K, bias, r03_c["cagr"]*100, r03_nc["cagr"]*100))
    print(f"  {'  -> look-ahead bias':<28} {'':>5} {'':>9} {bias:>+7.2f}pp")
    print()

# Summary
print("="*80)
print("  LOOK-AHEAD BIAS SUMMARY")
print("="*80)
print(f"  {'K':>3} {'Causal_CAGR_0.3':>16} {'NonCausal_CAGR_0.3':>20} {'Bias':>8}")
for K, bias, c_c, c_nc in deltas:
    print(f"  {K:>3d} {c_c:>+14.2f}% {c_nc:>+18.2f}% {bias:>+6.2f}pp")

# IS/OOS on the causal version
print("\n"+"="*80)
print("  WALK-FORWARD: CAUSAL min_stay variants only (deployable)")
print("="*80)

splits = [
    ("Full 2014-2026",   "2014-01-01", None),
    ("IS 2014-2019",     "2014-01-01", "2019-12-31"),
    ("OOS 2020-2026",    "2020-01-01", None),
]
print(f"\n  {'Period':<22} {'Variant':<14} {'CAGR_0.3':>9} {'Sh_0.3':>7} {'DD_0.3':>7}")
print("  " + "-"*72)

bh = pd.DataFrame({"time": tq["time"], "state": 4})
for label, sd, ed in splits:
    # B&H
    r_bh = simulate_timing(bh, start_date=sd, end_date=ed, tc=0.003)
    # TQ34b
    df_b = pd.DataFrame({"time": tq["time"], "state": state_base})
    r_b = simulate_timing(df_b, start_date=sd, end_date=ed, tc=0.003)
    print(f"  {label:<22} {'TQ34b':<14} {r_b['cagr']*100:>+7.2f}% {r_b['sharpe']:>7.2f} {r_b['max_dd']*100:>+6.1f}%")
    for K in [5, 7, 10, 15, 20]:
        s_c = min_stay_causal(state_base, K)
        df_c = pd.DataFrame({"time": tq["time"], "state": s_c})
        r_c = simulate_timing(df_c, start_date=sd, end_date=ed, tc=0.003)
        delta = (r_c["cagr"] - r_b["cagr"]) * 100
        print(f"  {label:<22} {f'ms{K} causal':<14} {r_c['cagr']*100:>+7.2f}% {r_c['sharpe']:>7.2f} {r_c['max_dd']*100:>+6.1f}%  Δ={delta:+.2f}pp")
    print(f"  {label:<22} {'B&H':<14} {r_bh['cagr']*100:>+7.2f}% {r_bh['sharpe']:>7.2f} {r_bh['max_dd']*100:>+6.1f}%")
    print()
