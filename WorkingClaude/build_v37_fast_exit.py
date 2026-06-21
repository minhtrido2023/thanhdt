# -*- coding: utf-8 -*-
"""
build_v37_fast_exit.py
======================
v3.7 = TQ34b + Smart BearDvg Gate EARLY EXIT

Key insight from v3.5/v3.6 analysis:
  - v3.5/v3.6 lifted CRISIS → BEAR (2, 20% alloc) = small improvement
  - v3.7 triggers EARLY EXIT from BearDvg gate → return to state_raw
    state_raw = underlying v3 staging score (NEUTRAL=3 / BULL=4 in most episodes)
    NEUTRAL = 70% allocation vs CRISIS = 0% → much larger impact

Early exit logic (post-hoc on TQ34b output):
  For each gate-forced CRISIS run [i, j):
    1. Compute R12m at trigger date (day i)
    2. If R12m_trig < R12M_THR (not coming from big bull run):
       Find first day t >= (i + MIN_DUR) where both_quiet is True
       From day t to j: use state_raw[t] instead of forcing state=1
  → This is equivalent to "gate exits early when macro is quiet AND VNI correction
    was not preceded by major bull run"

Key episodes (R12M_THR=0.30, MIN_DUR=20):
  2016 (+3%):  LIFT after day 20 → state_raw=NEUTRAL → +70% alloc for ~84 days ✓
  2019 (-13%): LIFT after day 20 → state_raw=NEUTRAL → +70% alloc for ~21 days ✓
  2024 (+18%): LIFT after day 20 → state_raw=NEUTRAL → +70% alloc for ~73 days ✓
  2021 (+49%): R12m > 30% → keep full CRISIS ✓
  2018 (+44%): R12m > 30% → keep full CRISIS ✓
  2020 COVID:  VIX=82 → not macro quiet → keep CRISIS ✓
  2025 tariff: VIX>25 → not macro quiet → keep CRISIS ✓

Output: vnindex_5state_v37_fast_exit_{thr}_{dur}.csv (per threshold combination)
        Best = vnindex_5state_v37_fast_exit.csv
"""
import sys, io, os, bisect, json
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing, print_result
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# Scan parameters
R12M_THRESHOLDS = [0.25, 0.30, 0.35]
MIN_DURS        = [20, 30]
MIN_LENS        = [0, 50, 70, 90]   # minimum run length to qualify for early exit (0 = no filter)

VN_REFI_MAX   = 6.5
VN_REFI_CHG   = 0.5
US_VIX_MAX    = 25.0
US_SPX_DD_MIN = -0.10

print("="*70)
print("v3.7 = TQ34b + Smart BearDvg Gate Early Exit")
print("="*70)

# ---- 1. Load TQ34b -----------------------------------------------------------
print("\n[1] Load TQ34b state + state_raw...")
tq = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)
print(f"  TQ34b: {len(tq)} rows | {tq['time'].iloc[0].date()} -> {tq['time'].iloc[-1].date()}")

# ---- 2. SBV refi series ------------------------------------------------------
print("\n[2] Build SBV refi daily series...")
with open(os.path.join(WORKDIR, "sbv_refi_events.json")) as fp:
    data = json.load(fp)
sbv_events = pd.DataFrame(data["events"], columns=["time","refi"])
sbv_events["time"] = pd.to_datetime(sbv_events["time"])
all_dates = pd.date_range(tq["time"].min(), tq["time"].max())
refi_series = pd.Series(index=all_dates, dtype=float)
for _, row in sbv_events.iterrows():
    refi_series[row["time"]:] = row["refi"]
refi_series = refi_series.ffill()
tq["refi"] = tq["time"].map(lambda t: refi_series.get(t))
tq["refi_chg_90d"] = tq["time"].apply(
    lambda t: (refi_series.get(t, np.nan) or np.nan) -
              (refi_series.get(t - pd.Timedelta(days=90), np.nan) or np.nan)
)
tq["vn_quiet"] = (tq["refi"] <= VN_REFI_MAX) & (tq["refi_chg_90d"] <= VN_REFI_CHG)

# ---- 3. US macro data --------------------------------------------------------
print("\n[3] Align US market data...")
us = pd.read_csv(os.path.join(WORKDIR, "data/us_market_history.csv"))
us["time"] = pd.to_datetime(us["time"])
us_dates = sorted(us["time"].tolist())
def nearest_us(t):
    target = t - pd.Timedelta(days=1)
    idx = bisect.bisect_right(us_dates, target)
    return us_dates[idx-1] if idx > 0 else None
tq["us_date"] = tq["time"].apply(nearest_us)
tq = tq.merge(us[["time","vix","spx_dd_1y"]],
              left_on="us_date", right_on="time", how="left", suffixes=("","_us"))
tq = tq.drop(columns=["time_us","us_date"])
tq["us_quiet"] = (tq["vix"] < US_VIX_MAX) & (tq["spx_dd_1y"] > US_SPX_DD_MIN)
tq["both_quiet"] = tq["vn_quiet"] & tq["us_quiet"]

# ---- 4. VNINDEX 12m return ---------------------------------------------------
print("\n[4] Load VNINDEX 12m return...")
vni = pd.read_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"), usecols=["time","Close"])
vni["time"] = pd.to_datetime(vni["time"])
tq = tq.merge(vni.rename(columns={"Close":"vni_close"}), on="time", how="left")
tq["vni_r12m"] = tq["vni_close"].pct_change(252)

# ---- 5. Propagate trigger-date R12m over each CRISIS run --------------------
print("\n[5] Propagate trigger-date VNI_12m to each CRISIS run...")
state_base = tq["state"].values.astype(int)
state_raw  = tq["state_raw"].values.astype(int)
both_quiet = tq["both_quiet"].values
r12m_arr   = tq["vni_r12m"].values

trigger_r12m = np.full(len(state_base), np.nan)
i = 0
while i < len(state_base):
    if state_base[i] == 1:
        j = i+1
        while j < len(state_base) and state_base[j] == 1: j += 1
        trigger_r12m[i:j] = r12m_arr[i]
        i = j
    else:
        i += 1

# ---- 6. CRISIS run diagnostics (post-2014) -----------------------------------
print("\n[6] CRISIS runs post-2014 — trigger diagnostics:")
print(f"  {'Start':<12} {'End':<12} {'Days':>5}  {'R12m_trig':>10}  {'quiet%':>7}  {'sr_modes'}")
print("  " + "-"*72)
mask14 = tq["time"] >= "2014-01-01"
i = 0
while i < len(tq):
    if state_base[i] == 1 and tq["time"].iloc[i] >= pd.Timestamp("2014-01-01"):
        j = i+1
        while j < len(tq) and state_base[j] == 1: j += 1
        sub = tq.iloc[i:j]
        r12m_t = trigger_r12m[i]
        quiet_pct = sub["both_quiet"].mean() * 100
        sr_counts = pd.Series(state_raw[i:j]).value_counts().sort_index()
        sr_str = " ".join([f"s{k}:{v}d" for k,v in sr_counts.items()])
        start_d = tq["time"].iloc[i].date(); end_d = tq["time"].iloc[j-1].date()
        marker = "  <LIFT?" if (not np.isnan(r12m_t) and r12m_t < 0.30) else "  keep"
        print(f"  {str(start_d):<12} {str(end_d):<12} {j-i:>5}  {r12m_t:>+9.0%}  {quiet_pct:>6.0f}%  {sr_str}{marker}")
        i = j
    else:
        i += 1

# ---- 7. Smoothing helpers ----------------------------------------------------
def rolling_mode(states, window):
    if window <= 1: return states.copy()
    out = states.copy()
    for t in range(window-1, len(states)):
        win = states[t-window+1:t+1]
        vals, counts = np.unique(win, return_counts=True)
        mc = counts.max(); cand = vals[counts==mc]
        for v in reversed(win):
            if v in cand: out[t]=v; break
    return out

def min_stay_filter(states, min_days):
    if min_days <= 1: return states.copy()
    out = states.copy(); changed = True
    while changed:
        changed = False; i = 0
        while i < len(out):
            j = i+1
            while j<len(out) and out[j]==out[i]: j += 1
            if (j-i) < min_days:
                fill = out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

def stay_stats(states):
    runs = []; i = 0
    while i < len(states):
        j = i+1
        while j < len(states) and states[j] == states[i]: j += 1
        runs.append(j-i); i = j
    return np.array(runs)

# ---- 8. Threshold scan -------------------------------------------------------
print(f"\n[7] Standalone simulation scan (2014→now)...")
print(f"\n  {'Variant':<35} {'NAV(B)':>7} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'ΔCAGR':>7}")
print("  " + "-"*80)

# Baseline: TQ34b
tq_path = os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
res_tq = simulate_timing(tq_path, start_date="2014-01-01")
print(f"  {'TQ34b (baseline)':<35} {res_tq['final_nav']/1e9:>7.3f} {res_tq['cagr']*100:>+7.2f}% "
      f"{res_tq['sharpe']:>7.2f} {res_tq['max_dd']*100:>+7.1f}% {res_tq['calmar']:>7.2f}  {'baseline':>8}")

# v3.5 and v3.6 for reference
for label, path in [
    ("v3.5 macro floor", "data/vnindex_5state_v35_macro_floor.csv"),
    ("v3.6 smart floor R12m<30%", "data/vnindex_5state_v36_smart_floor.csv"),
]:
    full_path = os.path.join(WORKDIR, path)
    if os.path.exists(full_path):
        res = simulate_timing(full_path, start_date="2014-01-01")
        delta = (res["cagr"] - res_tq["cagr"]) * 100
        print(f"  {label:<35} {res['final_nav']/1e9:>7.3f} {res['cagr']*100:>+7.2f}% "
              f"{res['sharpe']:>7.2f} {res['max_dd']*100:>+7.1f}% {res['calmar']:>7.2f} {delta:>+7.2f}pp")

print()

best_cagr = res_tq["cagr"]
best_params = None
best_state = None
all_results = {}

# Also precompute VNI close for recovery check
vni_close_arr = tq["vni_close"].values

for min_len in MIN_LENS:
    for min_dur in MIN_DURS:
        for r12m_thr in R12M_THRESHOLDS:
            # Build v3.7 state array
            state_v37 = state_base.copy()
            n_lifted_runs = 0
            n_lifted_days = 0

            i = 0
            while i < len(state_base):
                if state_base[i] == 1:
                    j = i+1
                    while j < len(state_base) and state_base[j] == 1: j += 1
                    run_len = j - i

                    # Check if this run qualifies for early exit
                    r12m_t = trigger_r12m[i]
                    qualifies = (
                        not np.isnan(r12m_t) and r12m_t < r12m_thr
                        and run_len > min_len  # run length filter
                    )
                    if qualifies:
                        # Find first macro-quiet day >= i + min_dur
                        exit_day = None
                        for t in range(i + min_dur, j):
                            if both_quiet[t]:
                                exit_day = t
                                break
                        if exit_day is not None:
                            # Early exit: use state_raw from exit_day onward
                            state_v37[exit_day:j] = state_raw[exit_day:j]
                            n_lifted_runs += 1
                            n_lifted_days += (j - exit_day)
                    i = j
                else:
                    i += 1

            # Re-smooth
            state_v37 = rolling_mode(state_v37, 3)
            state_v37 = min_stay_filter(state_v37, 2)

            # Build simulation DataFrame
            sim_df = pd.DataFrame({
                "time":  tq["time"].dt.strftime("%Y-%m-%d"),
                "state": state_v37.astype(int)
            })
            res = simulate_timing(sim_df, start_date="2014-01-01")

            delta = (res["cagr"] - res_tq["cagr"]) * 100
            len_tag = f"len>{min_len}" if min_len > 0 else "noLenF"
            label = f"v3.7 R12m<{r12m_thr:.0%} dur≥{min_dur}d {len_tag}"
            print(f"  {label:<42} {res['final_nav']/1e9:>7.3f} {res['cagr']*100:>+7.2f}% "
                  f"{res['sharpe']:>7.2f} {res['max_dd']*100:>+7.1f}% {res['calmar']:>7.2f} {delta:>+7.2f}pp")

            all_results[(r12m_thr, min_dur, min_len)] = (res, state_v37.copy(), n_lifted_runs, n_lifted_days)
            if res["cagr"] > best_cagr:
                best_cagr = res["cagr"]
                best_params = (r12m_thr, min_dur, min_len)
                best_state  = state_v37.copy()

    print()  # blank line between min_len groups

# ---- 9. Detailed analysis of chosen threshold --------------------------------
if best_params is None:
    print("\n  No variant beats TQ34b. Using R12m<30%, dur>=20, len>0 as reference.")
    best_params = (0.30, 20, 0)

r12m_chosen, dur_chosen, len_chosen = best_params
res_best, best_state, n_runs, n_days = all_results[best_params]

print(f"\n{'='*70}")
print(f"  BEST: R12M_THR={r12m_chosen:.0%}  MIN_DUR={dur_chosen}d  MIN_LEN>{len_chosen}d")
print(f"  Early exits: {n_runs} runs, {n_days} days lifted")
print(f"{'='*70}")

# Annual breakdown: TQ34b vs v3.7
print(f"\n[8] Annual breakdown: TQ34b vs v3.7 vs B&H")
bh_df = pd.DataFrame({"time": tq["time"].dt.strftime("%Y-%m-%d"), "state": 4})
res_bh = simulate_timing(bh_df, start_date="2014-01-01")

nav_tq   = res_tq["nav_series"]
nav_v37  = res_best["nav_series"]
nav_bh   = res_bh["nav_series"]
print(f"  {'Year':<6} {'TQ34b':>8} {'v3.7':>8} {'Δ':>6} {'B&H':>8}")
for yr in sorted(nav_tq.index.year.unique()):
    m_tq  = nav_tq.index.year  == yr
    m_v37 = nav_v37.index.year == yr
    m_bh  = nav_bh.index.year  == yr
    if m_tq.sum() < 5: continue
    r_tq  = nav_tq[m_tq].iloc[-1]  / nav_tq[m_tq].iloc[0]  - 1
    r_v37 = nav_v37[m_v37].iloc[-1] / nav_v37[m_v37].iloc[0] - 1
    r_bh  = nav_bh[m_bh].iloc[-1]  / nav_bh[m_bh].iloc[0]  - 1
    delta = r_v37 - r_tq
    marker = " ✓" if delta > 0 else "  "
    print(f"  {yr:<6} {r_tq*100:>+7.1f}%  {r_v37*100:>+7.1f}% {delta*100:>+5.1f}pp  {r_bh*100:>+7.1f}%{marker}")

# Episode analysis
print(f"\n[9] Key CRISIS episode detail for best variant:")
print(f"  {'Episode':<22} {'TQ_days':>8} {'ExitDay':>8} {'LiftDays':>9} {'state_raw_modes'}")
print("  " + "-"*70)

i = 0
while i < len(tq):
    if state_base[i] == 1 and tq["time"].iloc[i] >= pd.Timestamp("2014-01-01"):
        j = i+1
        while j < len(tq) and state_base[j] == 1: j += 1
        r12m_t = trigger_r12m[i]
        start_d = tq["time"].iloc[i].date()

        # Find exit day in best variant
        run_len = j - i
        if not np.isnan(r12m_t) and r12m_t < r12m_chosen and run_len > len_chosen:
            exit_day = None
            for t in range(i + dur_chosen, j):
                if both_quiet[t]:
                    exit_day = t
                    break
            lifted = j - exit_day if exit_day is not None else 0
            exit_d = tq["time"].iloc[exit_day].date() if exit_day is not None else "N/A"
        else:
            lifted = 0
            exit_d = "KEEP"

        sr_in_lifted = pd.Series(state_raw[i if lifted==0 else (j-lifted):j]).value_counts().sort_index()
        sr_str = " ".join([f"s{k}:{v}d" for k,v in sr_in_lifted.items()]) if lifted > 0 else "---"

        print(f"  {str(start_d):<22} {j-i:>8} {str(exit_d):>8} {lifted:>9}  {sr_str}")
        i = j
    else:
        i += 1

# ---- 10. Save best variant ---------------------------------------------------
out_path = os.path.join(WORKDIR, "data/vnindex_5state_v37_fast_exit.csv")
out = pd.DataFrame({
    "time":      tq["time"].dt.strftime("%Y-%m-%d"),
    "state":     best_state.astype(int),
    "state_raw": tq["state_raw"].astype(int),
})
out.to_csv(out_path, index=False)

# Summary comparison
print(f"\n{'='*70}")
print(f"  FINAL SUMMARY (2014→now, standalone VNINDEX simulation)")
print(f"{'='*70}")
print(f"  {'Variant':<30} {'NAV(B)':>7} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7}")
print(f"  {'-'*65}")
for label, res in [
    ("Buy&Hold", res_bh),
    ("TQ34b", res_tq),
    ("v3.7 best", res_best),
]:
    print(f"  {label:<30} {res['final_nav']/1e9:>7.3f} {res['cagr']*100:>+7.2f}% "
          f"{res['sharpe']:>7.2f} {res['max_dd']*100:>+7.1f}% {res['calmar']:>7.2f}")

# Current state
last = tq.iloc[-1]
print(f"\n  Current ({last['time'].date()}):")
print(f"  TQ34b:  {STATE_NAMES.get(int(last['state']))}")
print(f"  v3.7:   {STATE_NAMES.get(int(best_state[-1]))}")
print(f"\n-> {out_path} ({len(out)} rows)")
print(f"   Best params: R12M_THR={r12m_chosen:.0%}, MIN_DUR={dur_chosen}d, MIN_LEN>{len_chosen}d")
