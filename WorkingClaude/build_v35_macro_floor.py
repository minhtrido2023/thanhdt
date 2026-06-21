# -*- coding: utf-8 -*-
"""
build_v35_macro_floor.py
========================
v3.5 = TQ34b (v3.4b) + VN Macro BEAR Floor

Khi v2g BearDvg gate dang mo (state==1/CRISIS), neu ca VN va US macro
deu binh thuong thi floor state len BEAR(2) thay vi CRISIS(1).
Gate van hoat dong binh thuong -- chi nang floor tu 1 -> 2.

VN macro quiet:  SBV refi <= 6.5% AND refi_chg_90d <= 0.5pp
US macro quiet:  VIX < 25 AND SPX_DD_1Y > -0.10

Combined quiet = VN quiet AND US quiet
  -> state = max(state, 2)   [CRISIS -> BEAR]
  -> re-smooth: mode(3) + min_stay(2)

Output: vnindex_5state_v35_macro_floor.csv
"""
import sys, io, os, bisect, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# VN macro thresholds
VN_REFI_MAX   = 6.5   # SBV refi <= this = not elevated
VN_REFI_CHG   = 0.5   # refi increase in 90d <= this = not tightening
# US macro thresholds
US_VIX_MAX    = 25.0
US_SPX_DD_MIN = -0.10

print("="*70)
print("v3.5 = TQ34b + VN Macro BEAR Floor")
print("="*70)

# ---- 1. Load TQ34b (base) ---------------------------------------------------
print("\n[1] Load TQ34b state...")
tq = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)
print(f"  TQ34b: {len(tq)} rows | {tq['time'].iloc[0].date()} -> {tq['time'].iloc[-1].date()}")

# ---- 2. SBV refi daily series -----------------------------------------------
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
print(f"  SBV events: {len(sbv_events)} | Last rate: {refi_series.iloc[-1]:.2f}% ({sbv_events['time'].iloc[-1].date()})")

tq["refi"] = tq["time"].map(lambda t: refi_series.get(t))
tq["refi_chg_90d"] = tq["time"].apply(
    lambda t: (refi_series.get(t, np.nan) or np.nan) -
              (refi_series.get(t - pd.Timedelta(days=90), np.nan) or np.nan)
)
tq["vn_quiet"] = (tq["refi"] <= VN_REFI_MAX) & (tq["refi_chg_90d"] <= VN_REFI_CHG)

# ---- 3. US macro data -------------------------------------------------------
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
              left_on="us_date", right_on="time", how="left",
              suffixes=("","_us"))
tq = tq.drop(columns=["time_us","us_date"])
tq["us_quiet"] = (tq["vix"] < US_VIX_MAX) & (tq["spx_dd_1y"] > US_SPX_DD_MIN)

# ---- 4. Combined quiet + floor lift ----------------------------------------
print("\n[4] Apply combined quiet floor lift...")
tq["both_quiet"] = tq["vn_quiet"] & tq["us_quiet"]

state_base = tq["state"].values.astype(int)
both_quiet  = tq["both_quiet"].values

# Floor lift: when state==CRISIS(1) AND both_quiet -> raise to BEAR(2)
state_floored = np.where(
    (state_base == 1) & both_quiet,
    2,
    state_base
).astype(int)

n_lifted = int(((state_base == 1) & both_quiet).sum())
print(f"  Days lifted CRISIS -> BEAR: {n_lifted} / {(state_base==1).sum()} CRISIS days ({n_lifted/(state_base==1).sum()*100:.0f}%)")

# ---- 5. Re-smooth: mode(3) + min_stay(2) ------------------------------------
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

state_v35 = rolling_mode(state_floored, 3)
state_v35 = min_stay_filter(state_v35, 2)

# ---- 6. Save ----------------------------------------------------------------
out = pd.DataFrame({
    "time":  tq["time"].dt.strftime("%Y-%m-%d"),
    "state": state_v35.astype(int),
    "state_raw": tq["state_raw"].astype(int) if "state_raw" in tq.columns else state_v35.astype(int),
})
out_path = os.path.join(WORKDIR, "data/vnindex_5state_v35_macro_floor.csv")
out.to_csv(out_path, index=False)

# ---- 7. Statistics ----------------------------------------------------------
def stay_stats(states):
    runs = []; i = 0
    while i < len(states):
        j = i+1
        while j < len(states) and states[j] == states[i]: j += 1
        runs.append(j-i); i = j
    return np.array(runs)

mask14 = tq["time"] >= "2014-01-01"
s14_tq  = state_base[mask14.values]
s14_v35 = state_v35[mask14.values]

r_tq  = stay_stats(state_base)
r_v35 = stay_stats(state_v35)
r14_tq  = stay_stats(s14_tq)
r14_v35 = stay_stats(s14_v35)

print(f"\n{'='*70}")
print(f"  v3.5 STATISTICS vs TQ34b")
print(f"{'='*70}")

print(f"\nFull history:")
print(f"  TQ34b: {len(r_tq)} trans | min={r_tq.min()}d | median={int(np.median(r_tq))}d | stays<=5d: {(r_tq<=5).sum()}")
print(f"  v3.5:  {len(r_v35)} trans | min={r_v35.min()}d | median={int(np.median(r_v35))}d | stays<=5d: {(r_v35<=5).sum()}")

print(f"\nPost-2014:")
print(f"  TQ34b: {len(r14_tq)} trans | min={r14_tq.min()}d | median={int(np.median(r14_tq))}d | stays<=5d: {(r14_tq<=5).sum()}")
print(f"  v3.5:  {len(r14_v35)} trans | min={r14_v35.min()}d | median={int(np.median(r14_v35))}d | stays<=5d: {(r14_v35<=5).sum()}")

print(f"\nState distribution (post-2014):")
print(f"  {'State':<12} {'TQ34b':>8} {'v3.5':>8} {'Delta':>8}")
for s in [1,2,3,4,5]:
    p_tq  = (s14_tq  == s).mean() * 100
    p_v35 = (s14_v35 == s).mean() * 100
    print(f"  {STATE_NAMES[s]:<12} {p_tq:>7.1f}% {p_v35:>7.1f}% {p_v35-p_tq:>+7.1f}pp")

# Agreement
agree = (s14_tq == s14_v35).mean()
diff  = (s14_tq != s14_v35).sum()
print(f"\nAgreement TQ34b vs v3.5 (2014-2026): {agree*100:.1f}% | Diff: {diff} days")
v35_higher = (s14_v35 > s14_tq).sum()
tq_higher  = (s14_tq  > s14_v35).sum()
print(f"  v3.5 more bullish: {v35_higher}d | TQ34b more bullish: {tq_higher}d")

# Current state
last = tq.iloc[-1]
print(f"\nCurrent ({last['time'].date()}):")
print(f"  TQ34b base: {STATE_NAMES.get(int(last['state']))}")
print(f"  VN quiet:   {bool(last['vn_quiet'])} (refi={last['refi']:.1f}%, chg={last['refi_chg_90d']:+.2f}pp)")
print(f"  US quiet:   {bool(last['us_quiet'])} (VIX={last['vix']:.1f}, DD={last['spx_dd_1y']*100:+.1f}%)")
print(f"  v3.5:       {STATE_NAMES.get(int(state_v35[-1]))}")

# Show CRISIS episodes comparison
print(f"\nCRISIS episodes TQ34b -> v3.5 change (post-2014):")
runs_tq = []; i = 0; df14 = tq[mask14].reset_index(drop=True)
s14_v35_ser = pd.Series(s14_v35, index=df14.index)
while i < len(df14):
    j = i+1
    while j < len(df14) and df14["state"].iloc[j] == df14["state"].iloc[i]: j += 1
    if df14["state"].iloc[i] == 1:
        sub_v35 = s14_v35_ser.iloc[i:j]
        bear_days = (sub_v35 == 2).sum()
        crisis_days = (sub_v35 == 1).sum()
        runs_tq.append({
            "start": df14["time"].iloc[i].date(),
            "days_tq": j-i,
            "crisis_remain": crisis_days,
            "bear_lifted": bear_days,
        })
    i = j

print(f"  {'Start':<12} {'TQ_days':>8} {'CRISIS_rem':>11} {'BEAR_lift':>10}")
print("  " + "-"*45)
total_lifted = 0
for r in runs_tq:
    print(f"  {str(r['start']):<12} {r['days_tq']:>8} {r['crisis_remain']:>11} {r['bear_lifted']:>10}")
    total_lifted += r["bear_lifted"]
print(f"\n  Total days lifted: {total_lifted}")
print(f"\n-> {out_path} ({len(out)} rows)")
