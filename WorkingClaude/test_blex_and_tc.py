# -*- coding: utf-8 -*-
"""
test_blex_and_tc.py
===================
(B) BULL <-> EX-BULL specific smoothing on top of ms15_causal.
(C) Multi-TC robustness check.

Variants built on ms15_causal state series:
  BL1  base ms15_causal (control)
  BL2  BLEX_demote     -- EX-BULL -> BULL (cap leverage at 100%)
  BL3  BLEX_merge_alloc -- keep states distinct but cap alloc[EX-BULL]=1.0
  BL4  BLEX_asym_confirm  -- transitions INTO EX-BULL require 30d (vs 15d default)
  BL5  BLEX_asym_strict   -- transitions INTO EX-BULL require 45d
  BL6  BLEX_alloc_115     -- EX-BULL alloc=1.15 (less leverage, halfway)
  BL7  BLEX_alloc_120     -- EX-BULL alloc=1.20

Also test:
  BL_full = ms15_causal + asymmetric BLEX (30d for EX-BULL)

TC sweep at: 0.1%, 0.3%, 0.5%, 0.7%, 1.0%
Periods: Full / IS 2014-2019 / OOS 2020-2026
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# ---------- Causal smoothing helpers ----------------------------------------
def min_stay_causal(states, min_days):
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

def min_stay_causal_asym(states, default_min, target_state_min):
    """Asymmetric: most transitions need default_min consecutive days,
       but transitions INTO target_state need their own (longer) min."""
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
        # Choose required confirmation count
        if pending_state in target_state_min:
            need = target_state_min[pending_state]
        else:
            need = default_min
        if pending_run >= need and pending_state != committed:
            committed = pending_state
        out[t] = committed
    return out

# ---------- Load data --------------------------------------------------------
tq = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)
state_base = tq["state"].values.astype(int)

# Pre-build ms15_causal
state_ms15 = min_stay_causal(state_base, 15)

# B&H ref
bh = pd.DataFrame({"time": tq["time"], "state": 4})

# ---------- Build BLEX variants ---------------------------------------------
print("="*82)
print("  (B) BULL <-> EX-BULL VARIANTS on top of ms15_causal")
print("="*82)
print(f"\n  Baseline ms15_causal #BULL<->EXBULL trans:")
ms14 = state_ms15[(tq["time"] >= "2014-01-01").values]
trans = sum(1 for i in range(1, len(ms14)) if {ms14[i-1], ms14[i]} == {4, 5})
print(f"    {trans} flips (vs 24 in TQ34b)")

# BL2: demote EX-BULL -> BULL
state_bl2 = state_ms15.copy()
state_bl2[state_bl2 == 5] = 4

# BL3: same as BL2 but reflected as alloc change (we'll do via alloc dict)
alloc_bl3 = {1:0.0, 2:0.2, 3:0.7, 4:1.0, 5:1.0}  # cap EX-BULL alloc at 1.0

# BL4: asymmetric — entering EX-BULL needs 30 days agreement
state_bl4 = min_stay_causal_asym(state_base, 15, {5: 30})

# BL5: strict — entering EX-BULL needs 45 days
state_bl5 = min_stay_causal_asym(state_base, 15, {5: 45})

# BL6 / BL7: alternative alloc curves
alloc_bl6 = {1:0.0, 2:0.2, 3:0.7, 4:1.0, 5:1.15}
alloc_bl7 = {1:0.0, 2:0.2, 3:0.7, 4:1.0, 5:1.20}

# BL_safer: BL4 (30d for EX-BULL) + 25d for CRISIS entry (avoid quick CRISIS calls in bull)
state_bl_safer = min_stay_causal_asym(state_base, 15, {5: 30, 1: 25})

variants_b = {
    "ms15_causal (control)": (state_ms15, None),
    "BL2 demote EX-BULL->BULL": (state_bl2, None),
    "BL3 cap alloc(EX-BULL)=1.0": (state_ms15, alloc_bl3),
    "BL4 asym 30d->EX-BULL": (state_bl4, None),
    "BL5 asym 45d->EX-BULL": (state_bl5, None),
    "BL6 alloc(EX-BULL)=1.15": (state_ms15, alloc_bl6),
    "BL7 alloc(EX-BULL)=1.20": (state_ms15, alloc_bl7),
    "BL_safer 30d EXBULL+25d CRISIS": (state_bl_safer, None),
}

def count_tx(s, mask):
    s = s[mask]
    return int((s[1:] != s[:-1]).sum())

mask14 = (tq["time"] >= "2014-01-01").values

print(f"\n  {'Variant':<32} {'#tx':>5} {'CAGR_0.1':>9} {'CAGR_0.3':>9} {'CAGR_0.5':>9} {'Sh_0.3':>7} {'DD_0.3':>7}")
print("  " + "-"*86)

# Baseline: TQ34b
df_tq = pd.DataFrame({"time": tq["time"], "state": state_base})
r01 = simulate_timing(df_tq, start_date="2014-01-01", tc=0.001)
r03 = simulate_timing(df_tq, start_date="2014-01-01", tc=0.003)
r05 = simulate_timing(df_tq, start_date="2014-01-01", tc=0.005)
n_tx = count_tx(state_base, mask14)
print(f"  {'TQ34b (baseline)':<32} {n_tx:>5d} {r01['cagr']*100:>+7.2f}% {r03['cagr']*100:>+7.2f}% {r05['cagr']*100:>+7.2f}% {r03['sharpe']:>7.2f} {r03['max_dd']*100:>+6.1f}%")

for name, (sarr, alloc) in variants_b.items():
    df_v = pd.DataFrame({"time": tq["time"], "state": sarr})
    r01 = simulate_timing(df_v, start_date="2014-01-01", tc=0.001, alloc=alloc)
    r03 = simulate_timing(df_v, start_date="2014-01-01", tc=0.003, alloc=alloc)
    r05 = simulate_timing(df_v, start_date="2014-01-01", tc=0.005, alloc=alloc)
    n_tx = count_tx(sarr, mask14)
    print(f"  {name:<32} {n_tx:>5d} {r01['cagr']*100:>+7.2f}% {r03['cagr']*100:>+7.2f}% {r05['cagr']*100:>+7.2f}% {r03['sharpe']:>7.2f} {r03['max_dd']*100:>+6.1f}%")

# ---------- (C) Multi-TC sweep on key variants -----------------------------
print("\n"+"="*82)
print("  (C) MULTI-TC ROBUSTNESS SWEEP (Full 2014-2026)")
print("="*82)

# Choose 4 candidates: TQ34b, ms15_causal, BL2, BL_safer (assuming BL4 also)
key_variants = {
    "TQ34b": (state_base, None),
    "ms15_causal": (state_ms15, None),
    "BL2 demote EX-BULL": (state_bl2, None),
    "BL3 cap alloc=1.0": (state_ms15, alloc_bl3),
    "BL4 30d EX-BULL": (state_bl4, None),
    "BL_safer 30/25": (state_bl_safer, None),
}

print(f"\n  {'Variant':<22} {'TC':>5} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'vs B&H':>8}")
print("  " + "-"*82)

# B&H reference at each TC
bh_by_tc = {}
for tc in [0.001, 0.003, 0.005, 0.007, 0.010]:
    r_bh = simulate_timing(bh, start_date="2014-01-01", tc=tc)
    bh_by_tc[tc] = r_bh

for name, (sarr, alloc) in key_variants.items():
    df_v = pd.DataFrame({"time": tq["time"], "state": sarr})
    for tc in [0.001, 0.003, 0.005, 0.007, 0.010]:
        r = simulate_timing(df_v, start_date="2014-01-01", tc=tc, alloc=alloc)
        bh_delta = (r["cagr"] - bh_by_tc[tc]["cagr"]) * 100
        print(f"  {name:<22} {tc*100:>4.1f}% {r['cagr']*100:>+6.2f}% {r['sharpe']:>7.2f} {r['max_dd']*100:>+6.1f}% {r['calmar']:>7.2f} {bh_delta:>+6.2f}pp")
    print()

# B&H summary
print(f"  {'B&H (any TC)':<22} {'-':>5} {bh_by_tc[0.003]['cagr']*100:>+6.2f}% {bh_by_tc[0.003]['sharpe']:>7.2f} {bh_by_tc[0.003]['max_dd']*100:>+6.1f}% {bh_by_tc[0.003]['calmar']:>7.2f}")

# ---------- Walk-forward on top candidates ----------------------------------
print("\n"+"="*82)
print("  WALK-FORWARD on candidates (TC=0.30%)")
print("="*82)

splits = [
    ("Full 2014-2026",   "2014-01-01", None),
    ("IS 2014-2019",     "2014-01-01", "2019-12-31"),
    ("OOS 2020-2026",    "2020-01-01", None),
]

for label, sd, ed in splits:
    print(f"\n  [{label}]")
    print(f"  {'Variant':<22} {'CAGR_0.3':>9} {'Sh_0.3':>7} {'DD_0.3':>7} {'vs TQ34b':>9}")
    df_tq = pd.DataFrame({"time": tq["time"], "state": state_base})
    r_b = simulate_timing(df_tq, start_date=sd, end_date=ed, tc=0.003)
    print(f"  {'TQ34b':<22} {r_b['cagr']*100:>+7.2f}% {r_b['sharpe']:>7.2f} {r_b['max_dd']*100:>+6.1f}% {'baseline':>9}")
    for name, (sarr, alloc) in key_variants.items():
        if name == "TQ34b": continue
        df_v = pd.DataFrame({"time": tq["time"], "state": sarr})
        r = simulate_timing(df_v, start_date=sd, end_date=ed, tc=0.003, alloc=alloc)
        d = (r["cagr"] - r_b["cagr"]) * 100
        print(f"  {name:<22} {r['cagr']*100:>+7.2f}% {r['sharpe']:>7.2f} {r['max_dd']*100:>+6.1f}% {d:>+7.2f}pp")
    r_bh = simulate_timing(bh, start_date=sd, end_date=ed, tc=0.003)
    print(f"  {'B&H':<22} {r_bh['cagr']*100:>+7.2f}% {r_bh['sharpe']:>7.2f} {r_bh['max_dd']*100:>+6.1f}%")
