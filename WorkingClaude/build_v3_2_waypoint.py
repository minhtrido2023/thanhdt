# -*- coding: utf-8 -*-
"""
build_v3_2_waypoint.py
======================
v3.2 = v3.1 + "CRISIS exit waypoint" rule.

Rule:
  When the state transitions directly from CRISIS (1) → NEUTRAL (3)
  (a 2-step upgrade) and r_dual at the trigger day is < 0.60:
    → snap state to BEAR (2) instead.
    → hold BEAR until r_dual ≥ 0.60 (advance to NEUTRAL),
      or v3.1 says CRISIS reasserts (1), or v3.1 says BULL+ (≥4).

Intent: stop the system from prematurely declaring "crisis over" on
weak/marginal r_dual signals. Diagnostic identified 9 such trades
out of 15 2-step upgrades with negative forward edge.

Output: vnindex_5state_tam_quan_v3_2_full_history.csv
        (same schema as v3.1: time, state, state_raw)
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
THRESHOLD = 0.60   # r_dual cutoff for CRISIS→NEUTRAL direct upgrade

# Load v3.1 + dual scores
v31 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_full_history.csv"))
v31["time"] = pd.to_datetime(v31["time"]); v31 = v31.sort_values("time").reset_index(drop=True)

dual = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_full.csv"))
dual["time"] = pd.to_datetime(dual["time"])
dual["r_dual"] = dual["alpha"]*dual["r_score_raw"] + (1-dual["alpha"])*dual["r_score_ew"]

df = v31.merge(dual[["time","r_dual"]], on="time", how="left").reset_index(drop=True)
n = len(df)
v31_state = df["state"].values.astype(int)
r_dual    = df["r_dual"].values
print(f"Loaded {n} rows | {df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()}")
print(f"v3.1 transitions: {int((np.diff(v31_state)!=0).sum())}")

# ── Apply waypoint rule ────────────────────────────────────────────────
result = v31_state.copy()
waypoint_active = False
patches = []  # for logging

for t in range(1, n):
    prev = result[t-1]      # already-patched previous day
    cur_v31 = v31_state[t]  # what v3.1 says today

    if waypoint_active:
        # Exit conditions
        if cur_v31 == 1:
            result[t] = 1
            waypoint_active = False
        elif cur_v31 >= 4:
            result[t] = cur_v31
            waypoint_active = False
        elif (r_dual[t] is not None) and (not np.isnan(r_dual[t])) and (r_dual[t] >= THRESHOLD):
            result[t] = 3   # promote BEAR → NEUTRAL on convincing score
            waypoint_active = False
        else:
            result[t] = 2   # hold BEAR
    else:
        # Detect direct CRISIS → NEUTRAL with weak score
        is_2step_up = (prev == 1) and (cur_v31 == 3)
        weak = (r_dual[t] is None) or np.isnan(r_dual[t]) or (r_dual[t] < THRESHOLD)
        if is_2step_up and weak:
            result[t] = 2
            waypoint_active = True
            patches.append((df["time"].iloc[t], r_dual[t]))
        # else: leave result[t] = v31_state[t] (already set from copy)

# ── Diagnostics ────────────────────────────────────────────────────────
n_trans_new = int((np.diff(result)!=0).sum())
print(f"v3.2 transitions: {n_trans_new}  (delta vs v3.1: {n_trans_new - int((np.diff(v31_state)!=0).sum()):+d})")
print(f"\nWaypoint fired {len(patches)} times (CRISIS→BEAR snap):")
for dt, rd in patches:
    print(f"  {dt.date()}  r_dual={rd:.2f}")

# Count days spent in BEAR waypoint
bear_diff = (result == 2).sum() - (v31_state == 2).sum()
print(f"\nExtra BEAR days vs v3.1: {bear_diff:+d}")
print(f"Net NEUTRAL day delta:    {(result==3).sum() - (v31_state==3).sum():+d}")

# State distribution
print(f"\n{'State':<10} {'v3.1':>8} {'v3.2':>8} {'Δ':>8}")
for s in [1,2,3,4,5]:
    p1 = (v31_state==s).mean()*100; p2 = (result==s).mean()*100
    print(f"  {STATE_NAMES[s]:<8} {p1:>7.1f}% {p2:>7.1f}% {p2-p1:>+7.1f}pp")

# ── Save ──────────────────────────────────────────────────────────────
out = pd.DataFrame({
    "time":      df["time"].dt.strftime("%Y-%m-%d"),
    "state":     result.astype(int),
    "state_raw": df["state_raw"].astype(int),
})
out_path = os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_2_full_history.csv")
out.to_csv(out_path, index=False)
print(f"\n✓ Saved: {out_path}")
