# -*- coding: utf-8 -*-
"""
analyze_smoothing_ripple.py
============================
Deep dive: WHY does re-applying rolling_mode(3) + min_stay_filter(2) to
v3.5/v3.6/v3.7 (after lifting some CRISIS days) create CAGR improvements
at days far from the lifted episodes?

Hypothesis to test:
  H1) Smoothing applied to TQ34b alone (no mods) is idempotent
      -> if YES, ripples must originate from the lift points
  H2) Ripple changes cluster near transition boundaries
  H3) Ripple changes are random in sign (not systematically beneficial)
      -> if YES, the +0.76pp v3.6 improvement is luck, not signal
  H4) Most ripple-affected days fall in BULL/NEUTRAL regions where
      a downgrade (e.g. 4 -> 3) hurts and an upgrade (3 -> 4) helps

Method:
  1) Baseline smoothing test: apply rolling_mode+min_stay to TQ34b state
  2) v3.6 lift map: identify which days were lifted (direct effect)
  3) v3.6 ripple map: which days changed but were NOT lifted
  4) Sign analysis: ripple-day state delta and its NAV impact
  5) Run a counterfactual where we KEEP the lifts but DON'T re-smooth
     -> already done in summary, but recompute here precisely
  6) Permutation test: randomly pick same # CRISIS days from TQ34b,
     lift them, re-smooth, measure CAGR. Repeat 200 times.
     -> If v3.6's +0.76pp is within the noise distribution, it's luck.
     -> If it's a clear outlier, smoothing-ripple IS systematic.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing, STATE_ALLOC

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
np.random.seed(42)

# ---------- Smoothing helpers (same as build_v35/v36) ------------------------
def rolling_mode(states, window):
    if window <= 1: return states.copy()
    out = states.copy()
    for t in range(window-1, len(states)):
        win = states[t-window+1:t+1]
        vals, counts = np.unique(win, return_counts=True)
        mc = counts.max(); cand = vals[counts==mc]
        for v in reversed(win):
            if v in cand: out[t] = v; break
    return out

def min_stay_filter(states, min_days):
    if min_days <= 1: return states.copy()
    out = states.copy(); changed = True
    while changed:
        changed = False; i = 0
        while i < len(out):
            j = i+1
            while j < len(out) and out[j] == out[i]: j += 1
            if (j-i) < min_days:
                fill = out[i-1] if i > 0 else (out[j] if j < len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

def smooth_pipeline(states):
    s = rolling_mode(np.asarray(states, dtype=int), 3)
    s = min_stay_filter(s, 2)
    return s

# ---------- Load data --------------------------------------------------------
tq = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)

state_tq = tq["state"].values.astype(int)
state_raw = tq["state_raw"].values.astype(int) if "state_raw" in tq.columns else state_tq.copy()
dates = tq["time"].values

print("="*72)
print("  SMOOTHING RIPPLE DEEP DIVE")
print("="*72)
print(f"Rows: {len(tq)} | {tq['time'].iloc[0].date()} -> {tq['time'].iloc[-1].date()}")

# ---------- H1: is the smoothing pipeline idempotent on TQ34b? ---------------
print("\n[H1] Smoothing idempotency test")
print("-"*72)
state_tq_resmooth = smooth_pipeline(state_tq)
diff_h1 = (state_tq != state_tq_resmooth).sum()
print(f"  Re-smoothing TQ34b state: {diff_h1} days differ from original")
if diff_h1 > 0:
    print(f"  -> NOT idempotent: pipeline still finds short-stays to absorb")
    idx_diff = np.where(state_tq != state_tq_resmooth)[0]
    print(f"  First 10 diff dates:")
    for i in idx_diff[:10]:
        print(f"    {pd.Timestamp(dates[i]).date()}  TQ={state_tq[i]} -> resmooth={state_tq_resmooth[i]}")

    # Run simulation on the re-smoothed TQ34b alone
    df_resmooth = pd.DataFrame({"time": tq["time"], "state": state_tq_resmooth})
    res_resmooth = simulate_timing(df_resmooth, start_date="2014-01-01")
    df_orig = pd.DataFrame({"time": tq["time"], "state": state_tq})
    res_orig = simulate_timing(df_orig, start_date="2014-01-01")
    print(f"\n  TQ34b original           CAGR = {res_orig['cagr']*100:+.2f}%")
    print(f"  TQ34b re-smoothed (no lift) CAGR = {res_resmooth['cagr']*100:+.2f}%  delta {(res_resmooth['cagr']-res_orig['cagr'])*100:+.2f}pp")
    print(f"  ** If this delta is positive, re-smoothing TQ34b alone already gives free CAGR **")
else:
    print("  -> IDEMPOTENT: pipeline stable on TQ34b")

# ---------- Build v3.6 lift set ----------------------------------------------
print("\n[H2/H3] v3.6 lift vs ripple decomposition")
print("-"*72)

# Recompute v3.6 lift logic (lightweight, no re-build)
# v3.6 lifts CRISIS -> BEAR when:
#   - both VN macro and US macro quiet
#   - VNI R12m at trigger < 30%
# We use the existing v3.6 CSV
v36_path = os.path.join(WORKDIR, "vnindex_5state_v36_smart_floor.csv")
v36 = pd.read_csv(v36_path)
v36["time"] = pd.to_datetime(v36["time"])
v36 = v36.sort_values("time").reset_index(drop=True)
state_v36 = v36["state"].values.astype(int)

# Sanity align
assert len(state_v36) == len(state_tq), f"length mismatch {len(state_v36)} vs {len(state_tq)}"

# v3.6 pre-smooth (the "lift only" state - reverse-engineer it)
# Since we don't have the intermediate from the v3.6 build, simulate it:
# v3.6 lift = TQ34b but with CRISIS -> BEAR where macro both quiet AND r12m<30
# We need the lift mask. The simplest: state_v36_pre = TQ34b with lifts applied
# Then state_v36 = smooth_pipeline(state_v36_pre).
# Identify ACTUAL lift days from v36 itself: where state_v36 != state_tq.
# But that's lift + ripple combined. Need an alternate approach:
# Re-run the build logic in-line.

import json, bisect
with open(os.path.join(WORKDIR, "sbv_refi_events.json")) as fp:
    data = json.load(fp)
sbv = pd.DataFrame(data["events"], columns=["time","refi"])
sbv["time"] = pd.to_datetime(sbv["time"])
all_dates = pd.date_range(tq["time"].min(), tq["time"].max())
refi_s = pd.Series(index=all_dates, dtype=float)
for _, r in sbv.iterrows(): refi_s[r["time"]:] = r["refi"]
refi_s = refi_s.ffill()
tq["refi"] = tq["time"].map(refi_s.get)
def refi_chg(t):
    a = refi_s.get(t, np.nan); b = refi_s.get(t-pd.Timedelta(days=90), np.nan)
    return (a or np.nan) - (b or np.nan)
tq["refi_chg_90d"] = tq["time"].apply(refi_chg)
tq["vn_quiet"] = (tq["refi"] <= 6.5) & (tq["refi_chg_90d"] <= 0.5)

us = pd.read_csv(os.path.join(WORKDIR, "us_market_history.csv"))
us["time"] = pd.to_datetime(us["time"])
us_dates = sorted(us["time"].tolist())
def nearest_us(t):
    tgt = t - pd.Timedelta(days=1)
    idx = bisect.bisect_right(us_dates, tgt)
    return us_dates[idx-1] if idx > 0 else None
tq["us_date"] = tq["time"].apply(nearest_us)
tq = tq.merge(us[["time","vix","spx_dd_1y"]], left_on="us_date", right_on="time",
              how="left", suffixes=("","_us"))
tq = tq.drop(columns=["time_us","us_date"])
tq["us_quiet"] = (tq["vix"] < 25.0) & (tq["spx_dd_1y"] > -0.10)
tq["both_quiet"] = tq["vn_quiet"] & tq["us_quiet"]

# VNI R12m at trigger (gate open = first day of each CRISIS run)
vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"), usecols=["time","Close"])
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
vni["r12m"] = vni["Close"].pct_change(252)
tq = tq.merge(vni[["time","r12m"]], on="time", how="left")

# Trigger R12m for each CRISIS run
trig_r12m = np.full(len(tq), np.nan)
i = 0; r12 = tq["r12m"].values
while i < len(tq):
    if state_tq[i] == 1:
        j = i+1
        while j < len(tq) and state_tq[j] == 1: j += 1
        # trigger = day i, but use r12m at day i (or i-1 if NaN)
        rt = r12[i]
        trig_r12m[i:j] = rt
        i = j
    else:
        i += 1

# Build the v3.6 pre-smooth lift state
both_quiet = tq["both_quiet"].values
state_v36_pre = state_tq.copy()
lift_mask = (state_tq == 1) & both_quiet & (trig_r12m < 0.30) & ~np.isnan(trig_r12m)
state_v36_pre[lift_mask] = 2

n_lifted = int(lift_mask.sum())
print(f"  v3.6 direct lift days (CRISIS->BEAR): {n_lifted}")

# Verify reproducibility
state_v36_built = smooth_pipeline(state_v36_pre)
match_built = (state_v36_built == state_v36).mean() * 100
print(f"  Match between our reproduced v3.6 and CSV v3.6: {match_built:.1f}%")

# Compute ripple = days where state_v36 differs from state_tq BUT not in lift_mask
diff_mask = (state_v36 != state_tq)
ripple_mask = diff_mask & ~lift_mask
print(f"  Total diff days (v3.6 vs TQ34b): {int(diff_mask.sum())}")
print(f"  Direct lift (CRISIS->BEAR before smoothing): {n_lifted}")
print(f"  Ripple days (changed by smoothing, not direct lift): {int(ripple_mask.sum())}")

# ---------- Ripple breakdown -------------------------------------------------
print("\n[H4] Ripple change directions")
print("-"*72)
print(f"  {'TQ->v36':>10} {'count':>6} {'mean Δalloc':>12}")
print("  " + "-"*32)
transitions = {}
for i in np.where(ripple_mask)[0]:
    key = (int(state_tq[i]), int(state_v36[i]))
    transitions[key] = transitions.get(key,0)+1
for (a,b), c in sorted(transitions.items(), key=lambda x:-x[1]):
    dw = STATE_ALLOC[b] - STATE_ALLOC[a]
    print(f"  {a}->{b:<7d} {c:>6d}     {dw*100:+5.0f}%")

# Ripple by year
print("\n  Ripple days by year:")
ripple_years = pd.Series(pd.to_datetime(dates[ripple_mask])).dt.year.value_counts().sort_index()
for yr, c in ripple_years.items():
    print(f"    {yr}: {c}")

# ---------- Quantify ripple's PnL contribution -------------------------------
print("\n[H5] PnL decomposition: direct lift vs ripple")
print("-"*72)

# Variant A: TQ34b only
resA = simulate_timing(pd.DataFrame({"time": tq["time"], "state": state_tq}), start_date="2014-01-01")

# Variant B: lift CRISIS->BEAR, NO smoothing  (pure direct effect)
resB = simulate_timing(pd.DataFrame({"time": tq["time"], "state": state_v36_pre}), start_date="2014-01-01")

# Variant C: lift + smoothing (full v3.6) - already in CSV
resC = simulate_timing(pd.DataFrame({"time": tq["time"], "state": state_v36}), start_date="2014-01-01")

# Variant D: TQ34b + smoothing (no lift)
resD = simulate_timing(pd.DataFrame({"time": tq["time"], "state": state_tq_resmooth}), start_date="2014-01-01")

print(f"  A) TQ34b raw                       CAGR={resA['cagr']*100:+.2f}%  baseline")
print(f"  B) TQ34b + lift, NO smooth         CAGR={resB['cagr']*100:+.2f}%  delta={(resB['cagr']-resA['cagr'])*100:+.2f}pp  (direct lift only)")
print(f"  C) TQ34b + lift + smooth (v3.6)    CAGR={resC['cagr']*100:+.2f}%  delta={(resC['cagr']-resA['cagr'])*100:+.2f}pp  (full)")
print(f"  D) TQ34b + smooth, NO lift         CAGR={resD['cagr']*100:+.2f}%  delta={(resD['cagr']-resA['cagr'])*100:+.2f}pp  (smoothing only)")
print()
print(f"  Direct lift contribution      (B-A): {(resB['cagr']-resA['cagr'])*100:+.2f}pp")
print(f"  Smoothing-on-TQ contribution  (D-A): {(resD['cagr']-resA['cagr'])*100:+.2f}pp")
print(f"  Pure interaction              (C-B-D+A): {((resC['cagr']-resB['cagr'])-(resD['cagr']-resA['cagr']))*100:+.2f}pp")

# ---------- H6: Permutation test -- is +0.76pp distinguishable from noise? ---
print("\n[H6] Permutation test: random lifts produce what distribution?")
print("-"*72)

# Pick n_lifted random non-BEAR/non-NEUTRAL/non-BULL CRISIS days, lift them to BEAR, smooth, simulate
crisis_idx = np.where(state_tq == 1)[0]
n_perm = 100
deltas = []
for k in range(n_perm):
    sel = np.random.choice(crisis_idx, size=n_lifted, replace=False)
    s_perm = state_tq.copy()
    s_perm[sel] = 2
    s_perm = smooth_pipeline(s_perm)
    rp = simulate_timing(pd.DataFrame({"time": tq["time"], "state": s_perm}), start_date="2014-01-01")
    deltas.append((rp["cagr"] - resA["cagr"]) * 100)

deltas = np.array(deltas)
v36_delta = (resC["cagr"] - resA["cagr"]) * 100
print(f"  Random lift distribution (n={n_perm}):")
print(f"    mean   = {deltas.mean():+.3f}pp")
print(f"    std    = {deltas.std():.3f}pp")
print(f"    median = {np.median(deltas):+.3f}pp")
print(f"    min    = {deltas.min():+.3f}pp")
print(f"    max    = {deltas.max():+.3f}pp")
print(f"  v3.6 actual delta = {v36_delta:+.3f}pp")
pct_below = (deltas < v36_delta).mean() * 100
print(f"  v3.6 percentile in random distribution: {pct_below:.0f}%")
if pct_below > 90:
    print("  -> v3.6 is significantly better than random lifts: macro+r12m logic ADDS signal")
elif pct_below > 60:
    print("  -> v3.6 is somewhat above random: weak signal")
else:
    print("  -> v3.6 indistinguishable from random lifts: 'improvement' is noise/luck")
