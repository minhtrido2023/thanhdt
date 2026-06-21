# -*- coding: utf-8 -*-
"""
build_tam_quan_v3_1.py
======================
Tam Quan v3.1 = v3 + US shock override (4th view from external markets).

Override logic — 3-tier asymmetric cap (only restricts to defensive):
  Tier 3 CRISIS cap (state ≤ 1): SPX_DD_1Y < -25% OR VIX > 35
  Tier 2 BEAR cap   (state ≤ 2): SPX_DD_1Y < -15% OR VIX > 30
  Tier 1 NEUTRAL cap(state ≤ 3): SPX_DD_1Y < -10% OR VIX > 25

Applied AFTER s3 smoothing — pure post-hoc cap.
final_state = min(tam_quan_state, max_allowed_by_us_shock)

Output: vnindex_5state_tam_quan_v3_1_full_history.csv
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
import numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

print("="*70); print("Tam Quan v3.1 — v3 + US shock override"); print("="*70)

# Load existing v3 full-history state
print("\n[1] Load v3 full-history + US market")
v3 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_full_history.csv"))
v3["time"] = pd.to_datetime(v3["time"])
v3 = v3.sort_values("time").reset_index(drop=True)
v3_diag = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_full_history_diag.csv"))
v3_diag["time"] = pd.to_datetime(v3_diag["time"])

us = pd.read_csv(os.path.join(WORKDIR, "data/us_market_history.csv"))
us["time"] = pd.to_datetime(us["time"])

# Align US data to VN dates (most recent US day ≤ VN_day - 1)
import bisect
us_dates = sorted(us["time"].tolist())
def nearest_us(t):
    target = t - pd.Timedelta(days=1)
    idx = bisect.bisect_right(us_dates, target)
    return us_dates[idx-1] if idx > 0 else None
v3["us_date"] = v3["time"].apply(nearest_us)
v3 = v3.merge(us[["time","spx_close","vix","spx_dd_1y","spx_ret_20d","spx_ret_60d"]],
              left_on="us_date", right_on="time", how="left", suffixes=("","_us"))
v3 = v3.drop(columns=["time_us","us_date"]).rename(columns={"time":"time"})
print(f"  Merged: {len(v3)} rows | US data coverage: {v3['vix'].notna().sum()}/{len(v3)}")

# ─────────────────────────────────────────────────────────────────────
# [2] Compute US shock override
# ─────────────────────────────────────────────────────────────────────
print("\n[2] Compute US shock override")

def us_shock_cap(spx_dd_1y, vix):
    """Returns MAX ALLOWED STATE given US shock. 5 = no cap (= no override)."""
    if pd.isna(spx_dd_1y) or pd.isna(vix): return 5  # no US data → no override
    if spx_dd_1y < -0.25 or vix > 35: return 1
    if spx_dd_1y < -0.15 or vix > 30: return 2
    if spx_dd_1y < -0.10 or vix > 25: return 3
    return 5  # no override

v3["us_cap"] = v3.apply(lambda r: us_shock_cap(r["spx_dd_1y"], r["vix"]), axis=1)

# Apply: final_state = min(tam_quan_state, us_cap)
v3["state_v3_1"] = np.minimum(v3["state"], v3["us_cap"]).astype(int)
v3["override_fired"] = v3["state_v3_1"] < v3["state"]

# ─────────────────────────────────────────────────────────────────────
# [3] Smoothing pass on overridden state (s3 = mode3 + min_stay2)
# ─────────────────────────────────────────────────────────────────────
# Note: original v3 already smoothed; we re-smooth lightly to avoid 1-2 day
# override flickers. Use same s3 params.
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

# Light re-smoothing (mode3 + ms2) to avoid override-induced flicker
state_v3_1_arr = v3["state_v3_1"].values
state_v3_1_smoothed = rolling_mode(state_v3_1_arr, 3)
state_v3_1_smoothed = min_stay_filter(state_v3_1_smoothed, 2)
v3["state_v3_1_smooth"] = state_v3_1_smoothed.astype(int)

# ─────────────────────────────────────────────────────────────────────
# [4] Save outputs
# ─────────────────────────────────────────────────────────────────────
out_staging = pd.DataFrame({
    "time": v3["time"].dt.strftime("%Y-%m-%d"),
    "state": v3["state_v3_1_smooth"].astype(int),
    "state_raw": v3["state_raw"].astype(int),
})
out_staging.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_full_history.csv"), index=False)

diag = v3[["time","spx_close","vix","spx_dd_1y","spx_ret_60d",
           "us_cap","state_raw","state","state_v3_1","state_v3_1_smooth","override_fired"]].copy()
diag.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_diag.csv"), index=False)

# ─────────────────────────────────────────────────────────────────────
# [5] Summary
# ─────────────────────────────────────────────────────────────────────
print("\n[5] Override fire statistics")
total_fired = v3["override_fired"].sum()
print(f"  Total override-fired days: {total_fired} / {len(v3)} = {total_fired/len(v3)*100:.1f}%")

print("\nOverride fires per year:")
v3["year"] = v3["time"].dt.year
yr_stats = v3.groupby("year").agg(
    total=("time","count"),
    fired=("override_fired","sum"),
).reset_index()
yr_stats["pct"] = yr_stats["fired"] / yr_stats["total"] * 100
for _, r in yr_stats.iterrows():
    bar = "█" * int(r["pct"]/2)
    print(f"  {int(r['year']):<6} {int(r['fired']):>4}/{int(r['total'])} ({r['pct']:>4.1f}%) {bar}")

# State distribution post-2014 comparison
print("\nState distribution post-2014:")
post = v3[v3["time"] >= "2014-01-01"]
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
print(f"  {'State':<10} {'v3 only':>12} {'v3.1 override':>15}")
for s in [1,2,3,4,5]:
    p_v3 = (post["state"] == s).mean() * 100
    p_v3_1 = (post["state_v3_1_smooth"] == s).mean() * 100
    print(f"  {STATE_NAMES[s]:<10} {p_v3:>11.1f}% {p_v3_1:>14.1f}%")

# Verify Aug 18-19 fix
print("\n[6] Verification: Aug 18-19, 2008 (Tam Quan v3 failure days)")
fail_days = v3[v3["time"].isin([pd.Timestamp("2008-08-18"), pd.Timestamp("2008-08-19")])]
for _, r in fail_days.iterrows():
    print(f"  {r['time'].date()}: SPX_DD_1Y={r['spx_dd_1y']*100:+.1f}%  VIX={r['vix']:.1f}  "
          f"v3_state={STATE_NAMES.get(int(r['state']),'?')}  "
          f"us_cap={STATE_NAMES.get(int(r['us_cap']),'NO_OVERRIDE')}  "
          f"v3.1_state={STATE_NAMES.get(int(r['state_v3_1_smooth']),'?')}")

# Show recent days
print("\n[7] Last 10 sessions")
for _, r in v3.tail(10).iterrows():
    dd_s = f"{r['spx_dd_1y']*100:+.1f}%" if not pd.isna(r['spx_dd_1y']) else "n/a"
    vix_s = f"{r['vix']:.1f}" if not pd.isna(r['vix']) else "n/a"
    print(f"  {r['time'].strftime('%Y-%m-%d')}  DD_1Y={dd_s}  VIX={vix_s}  "
          f"v3={STATE_NAMES.get(int(r['state']),'?'):<8}  "
          f"v3.1={STATE_NAMES.get(int(r['state_v3_1_smooth']),'?')}")

print("\n→ vnindex_5state_tam_quan_v3_1_full_history.csv")
