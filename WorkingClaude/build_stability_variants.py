# -*- coding: utf-8 -*-
"""
build_stability_variants.py
===========================
Phase 3 + 4: build stability-focused TQ34b variants and evaluate with
TC=0.30% realistic objective.

Variants (all operate on TQ34b state series; no upstream changes):

  V1 = TQ34b baseline                       (155 trans)
  V2 = min_stay(K) -- absorb segments < K days
  V3 = N-day confirmation -- only flip if N consecutive days same direction
  V4 = reversal squash -- A->B->A within K days collapsed to A
  V5 = combo: V2 + V4 (best practical settings)
  V6 = "weight-clamp" variant -- limit |delta w| per day to MAX_DW
       (slow rotation: don't allow instant 0->100% jumps)

For each variant, score on:
  - CAGR @ TC=0.10%, 0.30%, 0.50%
  - Number of transitions (post-2014)
  - Mean stay duration
  - Sharpe @ TC=0.30%

Practical-objective winner = highest CAGR @ TC=0.30% AND
                              fewer transitions than TQ34b
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing, STATE_ALLOC

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# ------ Variant builders ----------------------------------------------------
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

def n_day_confirmation(states, n):
    """Only flip state if next n-1 days agree (causal)."""
    if n <= 1: return states.copy()
    out = states.copy()
    current = out[0]
    for t in range(1, len(out)):
        if states[t] != current:
            # Check next n-1 days starting at t agree
            end = min(t+n, len(states))
            window = states[t:end]
            if len(window) >= n and (window == window[0]).all():
                current = window[0]
            # else: keep current
            out[t] = current
        else:
            out[t] = current
    return out

def reversal_squash(states, K):
    """If A->B->A and middle segment B is shorter than K days, collapse middle to A."""
    out = states.copy()
    changed = True
    while changed:
        changed = False
        # Identify segments
        segs = []
        i = 0
        while i < len(out):
            j = i+1
            while j < len(out) and out[j] == out[i]: j += 1
            segs.append((i, j, int(out[i])))
            i = j
        # Look at middle segments
        for k in range(1, len(segs)-1):
            si, sj, ss = segs[k]
            prev_state = segs[k-1][2]; next_state = segs[k+1][2]
            if prev_state == next_state and (sj - si) < K:
                out[si:sj] = prev_state
                changed = True
                break  # restart segmentation
    return out

def weight_clamp(states, max_dw):
    """Convert states to weights, clamp |dw|<=max_dw per day, return clamped weights.
       Note: this returns weights, not states. Need custom sim or post-convert.
    """
    base_w = np.array([STATE_ALLOC[int(s)] for s in states])
    out_w = np.zeros(len(states))
    out_w[0] = base_w[0]
    for t in range(1, len(states)):
        target = base_w[t]
        prev = out_w[t-1]
        diff = target - prev
        if abs(diff) > max_dw:
            diff = np.sign(diff) * max_dw
        out_w[t] = prev + diff
    return out_w


# ------ Custom sim that takes weights directly ------------------------------
def simulate_weights(weights, vni_df, start_date, tc=0.001, deposit_apy=0.06, borrow_apy=0.10):
    """Simulate NAV given a weight series. weights aligned with vni_df."""
    df = vni_df.copy()
    df["w"] = weights
    df = df[df["time"] >= start_date].reset_index(drop=True)
    close = df["Close"].values
    ret = np.zeros(len(df)); ret[1:] = close[1:]/close[:-1]-1
    years = (df["time"].iloc[-1] - df["time"].iloc[0]).days / 365.25
    spy = len(df) / years
    nav = [1e9]
    daily = []
    eff_w = [0.0] + list(df["w"].values[:-1])  # T+1 lag
    INIT = 1e9
    for t in range(len(df)):
        w = eff_w[t]
        w_prev = eff_w[t-1] if t > 0 else 0.0
        r = float(ret[t])
        dw = abs(w - w_prev)
        c_frac = max(0.0, 1.0 - w)
        l_frac = max(0.0, w - 1.0)
        dret = w*r + c_frac*deposit_apy/spy - l_frac*borrow_apy/spy - dw*tc
        daily.append(dret)
        if t > 0: nav.append(nav[-1]*(1+dret))
        else: nav.append(INIT)
    nav = np.array(nav[1:])  # drop init
    final = nav[-1]
    cagr = (final/INIT)**(1/years)-1
    rf_d = deposit_apy/spy
    excess = np.array(daily) - rf_d
    sharpe = excess.mean()/excess.std()*np.sqrt(spy) if excess.std() > 0 else 0
    running_max = np.maximum.accumulate(nav)
    dd = (nav - running_max)/running_max
    max_dd = dd.min()
    return {"cagr":cagr, "sharpe":sharpe, "max_dd":max_dd, "final_nav":final,
            "calmar": cagr/(-max_dd) if max_dd<0 else np.inf, "years":years}


# ------ Load data -----------------------------------------------------------
tq = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)
vni = pd.read_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"), usecols=["time","Close"])
vni["time"] = pd.to_datetime(vni["time"])
df = vni.merge(tq[["time","state"]], on="time", how="inner").dropna(subset=["state"]).reset_index(drop=True)

state_base = df["state"].values.astype(int)

# ------ Build variants ------------------------------------------------------
print("="*78)
print("  STABILITY VARIANTS — practical objective: CAGR @ TC=0.30%")
print("="*78)

variants = {}
variants["V1_TQ34b"] = state_base.copy()
# V2 family: min_stay
for k in [10, 15, 20, 30]:
    variants[f"V2_minstay{k}"] = min_stay_filter(state_base, k)
# V3 family: N-day confirmation
for n in [3, 5, 7, 10]:
    variants[f"V3_confirm{n}"] = n_day_confirmation(state_base, n)
# V4 family: reversal squash
for K in [10, 20, 30]:
    variants[f"V4_squash{K}"] = reversal_squash(state_base, K)
# V5: combo — squash 20 + min_stay 15
v5 = reversal_squash(state_base, 20)
v5 = min_stay_filter(v5, 15)
variants["V5_combo"] = v5
# V5b: aggressive combo
v5b = reversal_squash(state_base, 30)
v5b = min_stay_filter(v5b, 20)
variants["V5b_combo_agg"] = v5b

# ------ Evaluate ------------------------------------------------------------
def n_transitions(s, mask14):
    s14 = s[mask14]
    return int((s14[1:] != s14[:-1]).sum())

def mean_stay(s, mask14):
    s14 = s[mask14]
    runs = []; i = 0
    while i < len(s14):
        j = i+1
        while j < len(s14) and s14[j] == s14[i]: j += 1
        runs.append(j-i); i = j
    return float(np.mean(runs)), int(np.median(runs))

mask14 = (df["time"] >= "2014-01-01").values

print(f"\n  {'Variant':<22} {'#tx':>5} {'meanS':>6} {'medS':>5} "
      f"{'CAGR_0.1':>9} {'CAGR_0.3':>9} {'CAGR_0.5':>9} "
      f"{'Sh_0.3':>7} {'DD_0.3':>7}")
print("  " + "-"*98)

# Also B&H ref
bh = pd.DataFrame({"time": tq["time"], "state": 4})
res_bh = simulate_timing(bh, start_date="2014-01-01", tc=0.003)
print(f"  {'BH_VNI':<22} {'-':>5} {'-':>6} {'-':>5} "
      f"{'?':>9} {res_bh['cagr']*100:>+7.2f}% {'?':>9} "
      f"{res_bh['sharpe']:>7.2f} {res_bh['max_dd']*100:>+6.1f}%")

results = {}
for name, s in variants.items():
    n_tx = n_transitions(s, mask14)
    ms, mds = mean_stay(s, mask14)
    dfv = pd.DataFrame({"time": df["time"], "state": s})
    r01 = simulate_timing(dfv, start_date="2014-01-01", tc=0.001)
    r03 = simulate_timing(dfv, start_date="2014-01-01", tc=0.003)
    r05 = simulate_timing(dfv, start_date="2014-01-01", tc=0.005)
    results[name] = {"n_tx":n_tx, "meanS":ms, "medS":mds,
                     "c01":r01["cagr"], "c03":r03["cagr"], "c05":r05["cagr"],
                     "sh03":r03["sharpe"], "dd03":r03["max_dd"]}
    print(f"  {name:<22} {n_tx:>5d} {ms:>6.1f} {mds:>5d} "
          f"{r01['cagr']*100:>+7.2f}% {r03['cagr']*100:>+7.2f}% {r05['cagr']*100:>+7.2f}% "
          f"{r03['sharpe']:>7.2f} {r03['max_dd']*100:>+6.1f}%")

# ------ V6: weight clamp (slow rotation) -----------------------------------
print("\n  V6 — weight-clamp (max |dw|/day): no state change, just rotation cap")
for max_dw in [0.05, 0.10, 0.20, 0.30]:
    wts = weight_clamp(state_base, max_dw)
    r01 = simulate_weights(wts, df, "2014-01-01", tc=0.001)
    r03 = simulate_weights(wts, df, "2014-01-01", tc=0.003)
    r05 = simulate_weights(wts, df, "2014-01-01", tc=0.005)
    # Count weight changes (approx)
    n_tx_w = int((np.abs(np.diff(wts[mask14])) > 0.001).sum())
    print(f"  {'V6_clamp_dw'+f'{int(max_dw*100):02d}'+'pct':<22} {n_tx_w:>5d} {'-':>6} {'-':>5} "
          f"{r01['cagr']*100:>+7.2f}% {r03['cagr']*100:>+7.2f}% {r05['cagr']*100:>+7.2f}% "
          f"{r03['sharpe']:>7.2f} {r03['max_dd']*100:>+6.1f}%")

# ------ Ranking -------------------------------------------------------------
print("\n"+"="*78)
print("  RANKING by practical CAGR (TC=0.30%) with fewer-tx constraint")
print("="*78)
ranked = sorted(results.items(), key=lambda kv: -kv[1]["c03"])
tq34b_tx = results["V1_TQ34b"]["n_tx"]
tq34b_c03 = results["V1_TQ34b"]["c03"]
print(f"  TQ34b baseline: #tx={tq34b_tx}, CAGR_0.3%={tq34b_c03*100:+.2f}%")
print(f"\n  Variants beating TQ34b on CAGR_0.3% AND #tx <= TQ34b:")
print(f"  {'Variant':<22} {'#tx':>5} {'CAGR_0.3':>9} {'delta':>8}")
for name, r in ranked:
    if r["c03"] >= tq34b_c03 and r["n_tx"] <= tq34b_tx:
        d = (r["c03"] - tq34b_c03) * 100
        print(f"  {name:<22} {r['n_tx']:>5d} {r['c03']*100:>+7.2f}% {d:>+6.2f}pp")
