# -*- coding: utf-8 -*-
"""
build_v3_1_clean.py
===================
v3.1-clean = v3 STAGING + US shock override (pure overlay, no EW rebuild).

Logic:
  base = vnindex_5state_dual_v3_staging.csv  (the existing deployed candidate)
  override = min(base.state, us_shock_cap(date))
  re-smooth lightly (mode3+ms2)

Override (same as v3.1):
  Tier 3 CRISIS cap (state ≤ 1): SPX_DD_1Y < -25% OR VIX > 35
  Tier 2 BEAR cap   (state ≤ 2): SPX_DD_1Y < -15% OR VIX > 30
  Tier 1 NEUTRAL cap(state ≤ 3): SPX_DD_1Y < -10% OR VIX > 25

Output: vnindex_5state_tam_quan_v3_1_clean.csv
"""
import sys, io, os, bisect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
import numpy as np

WORKDIR = os.environ.get("STATE_WORKDIR", os.path.dirname(os.path.abspath(__file__)))
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

print("="*70); print("v3.1-clean = v3 STAGING + US override overlay"); print("="*70)

# Load v3 staging
v3 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_staging.csv"))
v3["time"] = pd.to_datetime(v3["time"])
v3 = v3.sort_values("time").reset_index(drop=True)
print(f"  v3 staging: {len(v3)} rows | {v3['time'].iloc[0].date()} → {v3['time'].iloc[-1].date()}")

us = pd.read_csv(os.path.join(WORKDIR, "data/us_market_history.csv"))
us["time"] = pd.to_datetime(us["time"])

# Align US (most recent US ≤ VN-1)
us_dates = sorted(us["time"].tolist())
def nearest_us(t):
    target = t - pd.Timedelta(days=1)
    idx = bisect.bisect_right(us_dates, target)
    return us_dates[idx-1] if idx > 0 else None
v3["us_date"] = v3["time"].apply(nearest_us)
v3 = v3.merge(us[["time","vix","spx_dd_1y"]], left_on="us_date", right_on="time",
              how="left", suffixes=("","_us"))
v3 = v3.drop(columns=["time_us","us_date"]).rename(columns={"time":"time"})

def us_shock_cap(spx_dd_1y, vix):
    if pd.isna(spx_dd_1y) or pd.isna(vix): return 5
    if spx_dd_1y < -0.25 or vix > 35: return 1
    if spx_dd_1y < -0.15 or vix > 30: return 2
    if spx_dd_1y < -0.10 or vix > 25: return 3
    return 5

v3["us_cap"] = v3.apply(lambda r: us_shock_cap(r["spx_dd_1y"], r["vix"]), axis=1)
v3["state_overridden"] = np.minimum(v3["state"], v3["us_cap"]).astype(int)
v3["fired"] = v3["state_overridden"] < v3["state"]

# Light re-smooth (mode3+ms2)
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

s_arr = v3["state_overridden"].values
s_sm = rolling_mode(s_arr, 3)
s_sm = min_stay_filter(s_sm, 2)
v3["state_v3_1_clean"] = s_sm.astype(int)

# Save
out = pd.DataFrame({
    "time": v3["time"].dt.strftime("%Y-%m-%d"),
    "state": v3["state_v3_1_clean"].astype(int),
    "state_raw": v3["state_raw"].astype(int),
})
out.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_clean.csv"), index=False)

# Compare distributions
print(f"\nState distribution comparison:")
print(f"  {'State':<10} {'v3 staging':>12} {'v3.1-clean':>12} {'Δ':>8}")
for s in [1,2,3,4,5]:
    p_v3 = (v3["state"] == s).mean() * 100
    p_v31 = (v3["state_v3_1_clean"] == s).mean() * 100
    print(f"  {STATE_NAMES[s]:<10} {p_v3:>11.1f}% {p_v31:>11.1f}% {p_v31-p_v3:>+7.1f}pp")

# Year-by-year fires
v3["year"] = v3["time"].dt.year
print(f"\nOverride fire frequency per year:")
print(f"  {'Year':<6} {'Total':>8} {'Fired':>8} {'%':>6}")
for y in sorted(v3["year"].unique()):
    sub = v3[v3["year"] == y]
    n = len(sub); f = sub["fired"].sum()
    print(f"  {y:<6} {n:>8d} {f:>8d} {f/n*100 if n else 0:>5.1f}%")

# Aug 18-19 2008 verify
print(f"\nAug 18-19, 2008 verification:")
for d in ["2008-08-18", "2008-08-19"]:
    r = v3[v3["time"]==pd.Timestamp(d)]
    if len(r)==0: continue
    r = r.iloc[0]
    dd = f"{r['spx_dd_1y']*100:+.1f}%" if not pd.isna(r['spx_dd_1y']) else "n/a"
    print(f"  {d}: v3={STATE_NAMES.get(int(r['state']))} us_cap={STATE_NAMES.get(int(r['us_cap']))} v3.1={STATE_NAMES.get(int(r['state_v3_1_clean']))} (US DD={dd}, VIX={r['vix']:.1f})")

# Today
last = v3.iloc[-1]
print(f"\nToday ({last['time'].date()}):")
print(f"  v3 staging:  {STATE_NAMES.get(int(last['state']))}")
print(f"  v3.1-clean:  {STATE_NAMES.get(int(last['state_v3_1_clean']))}")
print(f"  US: DD_1Y={last['spx_dd_1y']*100:+.1f}%, VIX={last['vix']:.1f}, us_cap={STATE_NAMES.get(int(last['us_cap']))}")

print("\n→ vnindex_5state_tam_quan_v3_1_clean.csv")
