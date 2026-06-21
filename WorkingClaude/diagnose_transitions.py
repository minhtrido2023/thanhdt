# -*- coding: utf-8 -*-
"""
diagnose_transitions.py
=======================
Phase 1 + 2: baseline transition analysis on TQ34b post-2014.

Q: where are the "noisy" transitions that we want to suppress without
   losing directional accuracy?
Q: how much does CAGR change when TC scales 0.1% -> 0.3% -> 0.5% -> 1.0%?

Output:
  - Transitions per year
  - State stay-duration histogram
  - Transition matrix (counts of state-pair flips, post-2014)
  - "Quick reversal" pattern: state X -> Y -> X within N days
  - TC sensitivity table
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

tq = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)
mask14 = tq["time"] >= "2014-01-01"
tq14 = tq[mask14].reset_index(drop=True)
state = tq14["state"].values.astype(int)
times = tq14["time"]

print("="*72)
print("  TQ34b TRANSITION DIAGNOSIS (post-2014)")
print("="*72)
print(f"Rows post-2014: {len(tq14)} | {times.iloc[0].date()} -> {times.iloc[-1].date()}")

# ---- (1) Transitions per year ----------------------------------------------
print("\n[1] Transitions per year")
print("-"*72)
trans_idx = np.where(state[1:] != state[:-1])[0] + 1
n_trans_total = len(trans_idx)
print(f"  Total transitions (post-2014): {n_trans_total}")
yrs = times.dt.year.values
trans_yr = pd.Series(yrs[trans_idx]).value_counts().sort_index()
for y, c in trans_yr.items():
    print(f"    {y}: {c}")

# ---- (2) Stay duration distribution ----------------------------------------
print("\n[2] Stay duration histogram (each segment = run of same state)")
print("-"*72)
runs = []
i = 0
while i < len(state):
    j = i+1
    while j < len(state) and state[j] == state[i]: j += 1
    runs.append((state[i], j-i, times.iloc[i], times.iloc[j-1]))
    i = j
durs = np.array([r[1] for r in runs])
print(f"  N segments: {len(runs)}")
print(f"  Mean: {durs.mean():.1f} | Median: {int(np.median(durs))} | Min: {durs.min()} | Max: {durs.max()}")
print(f"  Stay-duration percentiles: p10={np.percentile(durs,10):.0f}  p25={np.percentile(durs,25):.0f}  p50={np.percentile(durs,50):.0f}  p75={np.percentile(durs,75):.0f}  p90={np.percentile(durs,90):.0f}")

# By state
print(f"\n  Mean stay by state:")
print(f"  {'State':<10} {'count':>6} {'mean':>6} {'med':>5} {'min':>5} {'max':>5}")
df_runs = pd.DataFrame(runs, columns=["state","dur","start","end"])
for s in [1,2,3,4,5]:
    sub = df_runs[df_runs["state"]==s]
    if len(sub)==0: continue
    print(f"  {STATE_NAMES[s]:<10} {len(sub):>6d} {sub['dur'].mean():>6.1f} {int(sub['dur'].median()):>5d} {int(sub['dur'].min()):>5d} {int(sub['dur'].max()):>5d}")

# Short-stay flag
short = df_runs[df_runs["dur"] <= 10]
print(f"\n  Short stays (<=10 days): {len(short)} / {len(df_runs)} ({100*len(short)/len(df_runs):.0f}%)")
if len(short) > 0:
    print(f"  First 15 short-stays:")
    print(f"  {'state':<8} {'dur':>4} {'start':<12} {'end':<12}")
    for _, r in short.head(15).iterrows():
        print(f"  {STATE_NAMES[int(r['state'])]:<8} {int(r['dur']):>4d} {r['start'].date()}   {r['end'].date()}")

# ---- (3) Transition matrix --------------------------------------------------
print("\n[3] Transition matrix (counts of pair X->Y)")
print("-"*72)
trans_pairs = {}
for k in trans_idx:
    a, b = int(state[k-1]), int(state[k])
    trans_pairs[(a,b)] = trans_pairs.get((a,b), 0) + 1
print(f"  {'From':<10} {'To':<10} {'count':>5}")
for (a,b), c in sorted(trans_pairs.items(), key=lambda x:-x[1]):
    print(f"  {STATE_NAMES[a]:<10} {STATE_NAMES[b]:<10} {c:>5d}")

# ---- (4) Quick reversal patterns -------------------------------------------
# Pattern: A -> B -> A in <= K days
print("\n[4] Quick-reversal patterns (A -> B -> A within K days)")
print("-"*72)
for K in [10, 20, 30]:
    n_rev = 0
    examples = []
    for i, (s, d, st_, en_) in enumerate(runs):
        if i == 0 or i == len(runs)-1: continue
        prev_state, _, _, _ = runs[i-1]
        next_state, _, _, _ = runs[i+1]
        if prev_state == next_state and d <= K:
            n_rev += 1
            if len(examples) < 5:
                examples.append((prev_state, s, next_state, d, st_, en_))
    print(f"  K={K}d: {n_rev} reversal middle-segments")
    if n_rev > 0 and K == 20:
        print(f"  Sample reversals:")
        for ex in examples:
            print(f"    {STATE_NAMES[ex[0]]:<8} -> {STATE_NAMES[ex[1]]:<8} -> {STATE_NAMES[ex[2]]:<8}  ({ex[3]}d, {ex[4].date()} - {ex[5].date()})")

# ---- (5) TC sensitivity ----------------------------------------------------
print("\n[5] TC sensitivity (TQ34b standalone, 2014-2026)")
print("-"*72)
print(f"  {'TC %':>7} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'FinalNAV':>11}")
for tc in [0.0001, 0.001, 0.003, 0.005, 0.010]:
    res = simulate_timing(tq, start_date="2014-01-01", tc=tc)
    print(f"  {tc*100:>6.2f}% {res['cagr']*100:>+6.2f}% {res['sharpe']:>7.2f} {res['max_dd']*100:>+6.1f}% {res['calmar']:>7.2f} {res['final_nav']/1e9:>10.3f}B")

# Compare to Buy & Hold
print("\n  (For reference, Buy&Hold 100% VNI at any TC since w doesn't change):")
bh = pd.DataFrame({"time": tq["time"], "state": 4})
res_bh = simulate_timing(bh, start_date="2014-01-01", tc=0.001)
print(f"  B&H               CAGR={res_bh['cagr']*100:+.2f}%  Sh={res_bh['sharpe']:.2f}  DD={res_bh['max_dd']*100:.1f}%")

# ---- (6) TC drag per transition --------------------------------------------
# Approx: each transition causes |delta_w| * TC drag once
# Get total |delta_w| over all transitions
weights = np.array([{1:0.0,2:0.2,3:0.7,4:1.0,5:1.3}[s] for s in state])
total_dw = np.sum(np.abs(np.diff(weights)))
print(f"\n[6] Total |delta_w| across {n_trans_total} transitions = {total_dw:.2f}")
years_span = (times.iloc[-1] - times.iloc[0]).days / 365.25
print(f"  Annualized |delta_w| = {total_dw/years_span:.3f} /yr")
print(f"  TC drag @ 0.1% TC = {total_dw/years_span * 0.001 * 100:.2f}%/yr")
print(f"  TC drag @ 0.3% TC = {total_dw/years_span * 0.003 * 100:.2f}%/yr")
print(f"  TC drag @ 0.5% TC = {total_dw/years_span * 0.005 * 100:.2f}%/yr")
print(f"  TC drag @ 1.0% TC = {total_dw/years_span * 0.010 * 100:.2f}%/yr")
