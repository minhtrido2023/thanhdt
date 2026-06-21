# -*- coding: utf-8 -*-
"""
build_v36_smart_floor.py
========================
v3.6 = TQ34b + Smart BEAR Floor (VN Macro + VNI Momentum Guard)

Logic:
  Khi BearDvg gate dang mo (state==1/CRISIS), neu DONG THOI:
  1. VN macro quiet:  SBV refi <= 6.5% AND refi_chg_90d <= 0.5pp
  2. US macro quiet:  VIX < 25 AND SPX_DD_1Y > -0.10
  3. Momentum guard:  VNI 12m return TAI DIEM TRIGGER cua CRISIS run < R12M_THR
     -> Neu bull run truoc BearDvg manh (>30%), CRISIS co the sau va dai -> giu nguyen
     -> Neu bull run vua phai (<30%), BearDvg chi la correction ngan -> nang len BEAR

Ket qua theo thu tu R12m:
  2016 (+3%)  -> LIFT (correction nhe sau stagnant)
  2019 (-13%) -> LIFT (VNI dang giam, BearDvg technical, khong phai bull tail)
  2021 (+49%) -> KEEP CRISIS (bull run khong lo +100% tu COVID, correction sau)
  2018 (+44%) -> KEEP CRISIS (bull run lớn, correction manh)
  2024 (+18%) -> LIFT (bull run vua phai, correction ngan)

Macro quiet giu:
  2020 COVID: VIX=82 -> keep ✓
  2022 SBV: refi +3pp in 90d -> keep ✓
  2025 tariff: VIX>25 -> keep ✓

Output: vnindex_5state_v36_smart_floor.csv (one per threshold)
"""
import sys, io, os, bisect, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# Thresholds to scan
R12M_THRESHOLDS = [0.20, 0.25, 0.30, 0.35]
VN_REFI_MAX   = 6.5
VN_REFI_CHG   = 0.5
US_VIX_MAX    = 25.0
US_SPX_DD_MIN = -0.10

print("="*70)
print("v3.6 = TQ34b + Smart BEAR Floor (macro + VNI momentum guard)")
print("="*70)

# ---- 1. Load TQ34b ----------------------------------------------------------
print("\n[1] Load TQ34b state...")
tq = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)
print(f"  TQ34b: {len(tq)} rows | {tq['time'].iloc[0].date()} -> {tq['time'].iloc[-1].date()}")

# ---- 2. SBV refi series -----------------------------------------------------
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

# ---- 3. US macro data -------------------------------------------------------
print("\n[3] Align US market data...")
us = pd.read_csv(os.path.join(WORKDIR, "us_market_history.csv"))
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

# ---- 4. VNINDEX 12m return --------------------------------------------------
print("\n[4] Load VNINDEX data for VNI_12m momentum...")
vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"))
vni["time"] = pd.to_datetime(vni["time"])
tq = tq.merge(vni[["time","Close","VNINDEX_PE_PERCENTILE"]].rename(columns={"Close":"vni_close"}),
              on="time", how="left")
tq["vni_ret_12m"] = tq["vni_close"].pct_change(252)

# ---- 5. Identify CRISIS runs and tag trigger-date R12m ----------------------
print("\n[5] Tag each CRISIS run with trigger-date VNI_12m...")
state_base = tq["state"].values.astype(int)
both_quiet  = tq["both_quiet"].values
pe_pct_arr  = tq["VNINDEX_PE_PERCENTILE"].values
r12m_arr    = tq["vni_ret_12m"].values

# Propagate trigger-date values to all days in each CRISIS run
trigger_r12m = np.full(len(state_base), np.nan)
trigger_pe   = np.full(len(state_base), np.nan)
i = 0
while i < len(state_base):
    if state_base[i] == 1:
        j = i + 1
        while j < len(state_base) and state_base[j] == 1: j += 1
        # CRISIS run [i, j)
        trigger_r12m[i:j] = r12m_arr[i]   # R12m at trigger date
        trigger_pe[i:j]   = pe_pct_arr[i] # PE_pct at trigger date
        i = j
    else:
        i += 1

# ---- 6. Diagnostic: show CRISIS runs (post-2014) with trigger values --------
print("\n[6] CRISIS runs post-2014 — trigger diagnostics:")
print(f"  {'Start':<12} {'End':<12} {'Days':>5}  {'GateF%':>7}  {'PE_trig':>8}  {'R12m_trig':>10}  {'MacroQ%':>8}")
print("  " + "-"*72)
i = 0
while i < len(tq):
    if state_base[i] == 1 and tq["time"].iloc[i] >= pd.Timestamp("2014-01-01"):
        j = i+1
        while j < len(tq) and state_base[j] == 1: j += 1
        sub = tq.iloc[i:j]
        gate_forced_pct = (sub["state_raw"] != 1).mean() * 100
        macro_quiet_pct = tq["both_quiet"].iloc[i:j].mean() * 100
        pe_t  = trigger_pe[i]
        r12_t = trigger_r12m[i]
        start = tq["time"].iloc[i].date(); end = tq["time"].iloc[j-1].date()
        print(f"  {str(start):<12} {str(end):<12} {j-i:>5}  {gate_forced_pct:>6.0f}%  {pe_t:>7.0%}  {r12_t:>+9.0%}  {macro_quiet_pct:>7.0f}%")
        i = j
    else:
        i += 1

# ---- 7. Threshold scan ------------------------------------------------------
print(f"\n[7] Threshold scan — Days lifted by different R12M_THR (post-2014):")
mask14 = tq["time"] >= "2014-01-01"

print(f"  {'R12M_THR':<10} {'Total_lift':>11} {'2016':>8} {'2018':>8} {'2019':>8} {'2021':>8} {'2024':>8}")
print("  " + "-"*60)
for thr in [0.15, 0.20, 0.25, 0.30, 0.35, 0.40]:
    floor_cond = (
        (state_base == 1) &
        both_quiet &
        (trigger_r12m < thr) &
        ~np.isnan(trigger_r12m)
    )
    total = floor_cond[mask14.values].sum()
    # By episode
    def ep_lift(s_str, e_str):
        m = (tq["time"] >= s_str) & (tq["time"] <= e_str)
        return floor_cond[m.values].sum()
    l16 = ep_lift("2016-07-27","2016-12-20")
    l18 = ep_lift("2018-02-06","2018-06-07")
    l19 = ep_lift("2019-03-20","2019-05-21")
    l21 = ep_lift("2021-11-23","2022-05-31")
    l24 = ep_lift("2024-04-04","2024-08-16")
    print(f"  R12m<{thr:.0%}  {total:>10} {l16:>8} {l18:>8} {l19:>8} {l21:>8} {l24:>8}")

# ---- 8. Build v3.6 states for each threshold --------------------------------
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

print(f"\n[8] Building v3.6 states for each threshold...")
results = {}
s14_tq = state_base[mask14.values]
r14_tq = stay_stats(s14_tq)

for thr in R12M_THRESHOLDS:
    floor_cond = (
        (state_base == 1) &
        both_quiet &
        (trigger_r12m < thr) &
        ~np.isnan(trigger_r12m)
    )
    state_floored = np.where(floor_cond, 2, state_base).astype(int)
    state_v36 = rolling_mode(state_floored, 3)
    state_v36 = min_stay_filter(state_v36, 2)

    s14_v36 = state_v36[mask14.values]
    r14_v36 = stay_stats(s14_v36)
    n_lifted = int(floor_cond.sum())
    n_lifted_14 = int(floor_cond[mask14.values].sum())

    results[thr] = state_v36

    print(f"\n  -- R12M_THR={thr:.0%} --")
    print(f"  Days lifted (all): {n_lifted} | post-2014: {n_lifted_14}")
    print(f"  Post-2014 transitions: TQ34b={len(r14_tq)} | v3.6={len(r14_v36)}")
    print(f"  Post-2014 stays<=5d:   TQ34b={(r14_tq<=5).sum()} | v3.6={(r14_v36<=5).sum()}")
    print(f"  State distribution (post-2014):")
    print(f"  {'State':<12} {'TQ34b':>8} {'v3.6':>8} {'Delta':>8}")
    for s in [1,2,3,4,5]:
        p_tq  = (s14_tq  == s).mean() * 100
        p_v36 = (s14_v36 == s).mean() * 100
        print(f"  {STATE_NAMES[s]:<12} {p_tq:>7.1f}% {p_v36:>7.1f}% {p_v36-p_tq:>+7.1f}pp")

# ---- 9. Save CHOSEN threshold (default: R12M=0.30) --------------------------
CHOSEN_THR = 0.30
state_chosen = results[CHOSEN_THR]
out = pd.DataFrame({
    "time":      tq["time"].dt.strftime("%Y-%m-%d"),
    "state":     state_chosen.astype(int),
    "state_raw": tq["state_raw"].astype(int) if "state_raw" in tq.columns else state_chosen.astype(int),
})
out_path = os.path.join(WORKDIR, "vnindex_5state_v36_smart_floor.csv")
out.to_csv(out_path, index=False)

# ---- 10. Final summary for chosen threshold ---------------------------------
print(f"\n{'='*70}")
print(f"  CHOSEN: R12M_THR={CHOSEN_THR:.0%}")
print(f"{'='*70}")
floor_cond_chosen = (
    (state_base == 1) & both_quiet &
    (trigger_r12m < CHOSEN_THR) & ~np.isnan(trigger_r12m)
)
n_lifted = int(floor_cond_chosen[mask14.values].sum())
crisis_total = int((state_base[mask14.values] == 1).sum())
print(f"  Post-2014 CRISIS days lifted: {n_lifted}/{crisis_total} ({n_lifted/crisis_total*100:.0f}%)")
print(f"\n  Key episodes:")
for label, s_str, e_str in [
    ("2016 Jul (104d)", "2016-07-27","2016-12-20"),
    ("2018 Feb (80d)",  "2018-02-06","2018-06-07"),
    ("2019 Mar (41d)",  "2019-03-20","2019-05-21"),
    ("2020 COVID",      "2020-03-02","2020-04-29"),
    ("2021 Nov (127d)", "2021-11-23","2022-05-31"),
    ("2022 SBV (47d)",  "2022-09-28","2022-12-01"),
    ("2023 Sep (40d)",  "2023-09-19","2023-11-13"),
    ("2024 Apr (93d)",  "2024-04-04","2024-08-16"),
    ("2025 Apr (10d)",  "2025-04-09","2025-04-22"),
]:
    m = (tq["time"] >= s_str) & (tq["time"] <= e_str)
    tq_crisis = (state_base[m.values] == 1).sum()
    lifted = floor_cond_chosen[m.values].sum()
    kept = tq_crisis - lifted
    r12m_t = trigger_r12m[m.values & (state_base==1)][0] if (m.values & (state_base==1)).any() else np.nan
    print(f"  {label:<20} TQ crisis={tq_crisis:>3}  lifted={lifted:>3}  kept={kept:>3}  R12m_trig={r12m_t:>+6.0%}")

# Current state
last = tq.iloc[-1]
print(f"\n  Current ({last['time'].date()}):")
print(f"  TQ34b:  {STATE_NAMES.get(int(last['state']))}")
print(f"  v3.6:   {STATE_NAMES.get(int(state_chosen[-1]))}")
print(f"\n-> {out_path} ({len(out)} rows)")
