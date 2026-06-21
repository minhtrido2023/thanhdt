# -*- coding: utf-8 -*-
"""
build_v21_plus.py
=================
v2.1+ = v2.1 + "offense layer" from TQ34b

Architecture:
  Base:       BQ LIVE state (tav2_bq.vnindex_5state = v2g_pe3c_s3)
  Defense:    US shock override (same as v2.1) — applied when BTC=False
  Offense-1:  BTC bypass (same as TQ34b v3.4b) — skip US override when BTC=True
              BTC_R6M = ret_120d > 15% AND ma200_dev > 0
  Offense-2:  RSI gate (same as TQ34b) — block 1-step downgrades when RSI>=55
              RSI_THR=55, CONC_THR=0.55
  Smoothing:  mode(3) + min_stay(2)  [same as TQ34b final step]

vs TQ34b (v3.4b):
  Base:       v3 staging (v2g_pe3c_s3 rebuilt from scratch)
  Defense:    US shock override
  Offense-1:  BTC bypass (same thresholds)
  Offense-2:  RSI gate (same thresholds)

Since BQ LIVE vs v3_staging agree 82.3% (2014-2026), v2.1+ may have slight
differences — particularly in the 149 days where BQ LIVE > v3_staging
(upstream diversity kept, not neutralized by rebuild).

Output: vnindex_5state_v21_plus.csv
"""
import sys, io, os, bisect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq

RSI_THR  = 55
CONC_THR = 0.55
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

print("="*70)
print("v2.1+ = BQ LIVE + US override (BTC bypass) + RSI gate")
print("="*70)

# ---- 1. BQ LIVE state (pre-override base) -----------------------------------
print("\n[1] Download BQ LIVE state...")
df_live = bq("SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s ORDER BY s.time")
df_live["time"] = pd.to_datetime(df_live["time"])
df_live = df_live.sort_values("time").reset_index(drop=True)
print(f"  BQ LIVE: {len(df_live)} rows | {df_live['time'].iloc[0].date()} -> {df_live['time'].iloc[-1].date()}")
print(f"  Last state: {STATE_NAMES.get(int(df_live['state'].iloc[-1]))} on {df_live['time'].iloc[-1].date()}")

# ---- 2. VNI data for BTC computation ----------------------------------------
print("\n[2] Load VNI data for BTC_R6M...")
vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"))
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
# Must cover all BQ LIVE dates
# Merge BQ LIVE with VNI
df = df_live.merge(vni[["time","Close","MA200","D_RSI"]], on="time", how="left")
print(f"  VNI merged: {df['Close'].notna().sum()}/{len(df)} dates with close price")

close    = df["Close"].values.astype(float)
ma200    = df["MA200"].values.astype(float)
n        = len(df)

# BTC_R6M = trailing 120-day return > 15% AND close > MA200
ret_120d   = pd.Series(close).pct_change(120).values
ma200_dev  = np.where((ma200 > 0) & ~np.isnan(ma200), close / ma200 - 1, np.nan)
BTC_arr    = ((ret_120d > 0.15) & (ma200_dev > 0) &
              ~np.isnan(ret_120d) & ~np.isnan(ma200_dev))
print(f"  BTC_R6M active: {BTC_arr.sum()} days = {BTC_arr.mean()*100:.1f}%")

# ---- 3. US shock override ---------------------------------------------------
print("\n[3] Align US market data...")
us = pd.read_csv(os.path.join(WORKDIR, "us_market_history.csv"))
us["time"] = pd.to_datetime(us["time"])
us_dates = sorted(us["time"].tolist())

def nearest_us(t):
    target = t - pd.Timedelta(days=1)
    idx = bisect.bisect_right(us_dates, target)
    return us_dates[idx-1] if idx > 0 else None

df["us_date"] = df["time"].apply(nearest_us)
df = df.merge(us[["time","vix","spx_dd_1y"]],
              left_on="us_date", right_on="time", how="left",
              suffixes=("","_us"))
df = df.drop(columns=["time_us","us_date"])

def us_shock_cap(spx_dd_1y, vix):
    if pd.isna(spx_dd_1y) or pd.isna(vix): return 5
    if spx_dd_1y < -0.25 or vix > 35: return 1
    if spx_dd_1y < -0.15 or vix > 30: return 2
    if spx_dd_1y < -0.10 or vix > 25: return 3
    return 5

df["us_cap"] = df.apply(lambda r: us_shock_cap(r["spx_dd_1y"], r["vix"]), axis=1)
us_fires = ((df["us_cap"] < 5)).sum()
print(f"  US override fires (any cap): {us_fires} days ({us_fires/len(df)*100:.1f}%)")

# ---- 4. BTC bypass + US override blend -------------------------------------
print("\n[4] Build base state with BTC bypass...")
bqlive_state = df["state"].values.astype(int)
us_cap_arr   = df["us_cap"].values.astype(int)

base_state = np.where(
    BTC_arr,
    bqlive_state,                              # BTC=True: use BQ LIVE (no override)
    np.minimum(bqlive_state, us_cap_arr)       # BTC=False: apply US cap
).astype(int)

n_bypassed = int(((base_state > np.minimum(bqlive_state, us_cap_arr)) & BTC_arr).sum())
n_overridden = int((np.minimum(bqlive_state, us_cap_arr) < bqlive_state).sum())
n_btc_prevented = int(n_overridden - ((np.minimum(bqlive_state, us_cap_arr) < bqlive_state) & ~BTC_arr).sum())
print(f"  US override would fire: {n_overridden} days")
print(f"  BTC bypass prevented:   {n_btc_prevented} days (kept at BQ LIVE)")
print(f"  US override applied:    {n_overridden - n_btc_prevented} days (BTC=False)")

# ---- 5. RSI gate (same as TQ34b v3.4b) -------------------------------------
print("\n[5] RSI gate...")

# Simple RSI14 on VNI close (same as build_v3_4_bull_aware.py)
def rsi14(c):
    delta = np.diff(c, prepend=c[0])
    up   = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)
    out  = np.full(len(c), np.nan)
    for i in range(14, len(c)):
        gain = up[i-13:i+1].mean()
        loss = down[i-13:i+1].mean()
        rs   = gain / loss if loss > 0 else 100
        out[i] = 100 - 100 / (1 + rs)
    return out

rsi_arr  = rsi14(close)

# Concentration smooth from v3 dual full (same series as TQ34b)
dr = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])
df = df.merge(dr[["time","concentration_smooth"]], on="time", how="left")
conc_arr = df["concentration_smooth"].values

# Apply RSI gate
result = base_state.copy()
blocked = False; blocked_at = None; n_blocked = 0
for t in range(1, n):
    cur = base_state[t]; prev = base_state[t-1]
    cr  = rsi_arr[t]; cc = conc_arr[t]
    if blocked:
        if np.isnan(cr) or cr < RSI_THR:
            blocked = False; result[t] = cur
        elif cur >= blocked_at:
            blocked = False; result[t] = cur
        elif (blocked_at - cur) >= 2:
            blocked = False; result[t] = cur
        else:
            result[t] = blocked_at; n_blocked += 1
    else:
        is_1step = (prev - cur == 1)
        rsi_ok   = (not np.isnan(cr)) and (cr >= RSI_THR)
        conc_ok  = np.isnan(cc) or (cc <= CONC_THR)
        if is_1step and rsi_ok and conc_ok:
            blocked = True; blocked_at = prev; result[t] = blocked_at; n_blocked += 1

print(f"  RSI gate blocked {n_blocked} downgrade-days")

# ---- 6. Smoothing: mode(3) + min_stay(2) ------------------------------------
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

result = rolling_mode(result, 3)
result = min_stay_filter(result, 2)
print(f"\n[6] Smoothing: mode(3) + min_stay(2)")

# ---- 7. Save ----------------------------------------------------------------
out = pd.DataFrame({
    "time":  df["time"].dt.strftime("%Y-%m-%d"),
    "state": result.astype(int)
})
out.to_csv(os.path.join(WORKDIR, "vnindex_5state_v21_plus.csv"), index=False)

# ---- 8. Stats ---------------------------------------------------------------
print("\n" + "="*70)
print("  v2.1+ STATISTICS")
print("="*70)

def stay_stats(states):
    runs = []; i = 0
    while i < len(states):
        j = i+1
        while j < len(states) and states[j] == states[i]: j += 1
        runs.append(j-i); i = j
    return np.array(runs)

# Load TQ34b for comparison
tq = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])

# Mask post-2014 for comparison
mask14 = df["time"] >= "2014-01-01"
mask14_tq = tq["time"] >= "2014-01-01"
res14 = result[mask14.values]
tq14  = tq.loc[mask14_tq, "state"].values

runs_v21p = stay_stats(result)
runs_tq   = stay_stats(tq["state"].values)
runs14_v21p = stay_stats(res14)
runs14_tq   = stay_stats(tq14)

print(f"\nFull history:")
print(f"  v2.1+:  {len(runs_v21p)} transitions | min={runs_v21p.min()}d | median={int(np.median(runs_v21p))}d | stays<=5d: {(runs_v21p<=5).sum()}")
print(f"  TQ34b:  {len(runs_tq)} transitions  | min={runs_tq.min()}d  | median={int(np.median(runs_tq))}d | stays<=5d: {(runs_tq<=5).sum()}")

print(f"\nPost-2014:")
print(f"  v2.1+:  {len(runs14_v21p)} transitions | min={runs14_v21p.min()}d | median={int(np.median(runs14_v21p))}d | stays<=5d: {(runs14_v21p<=5).sum()}")
print(f"  TQ34b:  {len(runs14_tq)} transitions  | min={runs14_tq.min()}d  | median={int(np.median(runs14_tq))}d | stays<=5d: {(runs14_tq<=5).sum()}")

print(f"\nState distribution (post-2014):")
print(f"  {'State':<12} {'v2.1+':>8} {'TQ34b':>8} {'Delta':>8}")
for s in [1,2,3,4,5]:
    p_v21p = (res14 == s).mean() * 100
    p_tq   = (tq14 == s).mean()  * 100
    print(f"  {STATE_NAMES[s]:<12} {p_v21p:>7.1f}% {p_tq:>7.1f}% {p_v21p-p_tq:>+7.1f}pp")

# Agreement with TQ34b post-2014
common_dates = df[mask14]["time"]
tq_aligned = tq.set_index("time")["state"].reindex(common_dates).values
v21p_aligned = res14
agree_rate = (tq_aligned == v21p_aligned).mean()
print(f"\nv2.1+ vs TQ34b agreement (2014-2026): {agree_rate*100:.1f}%")
diff_days = (tq_aligned != v21p_aligned).sum()
more_bull = (v21p_aligned > tq_aligned).sum()
more_bear  = (v21p_aligned < tq_aligned).sum()
print(f"  Diff days: {diff_days} | v2.1+ more bullish: {more_bull}d | TQ34b more bullish: {more_bear}d")

# Current state
last = df.iloc[-1]
print(f"\nCurrent ({last['time'].date()}):")
print(f"  BQ LIVE:  {STATE_NAMES.get(int(last['state']))}")
print(f"  BTC_R6M:  {bool(BTC_arr[-1])}")
print(f"  US cap:   {STATE_NAMES.get(int(last['us_cap']))}")
print(f"  v2.1+:    {STATE_NAMES.get(int(result[-1]))}")

print(f"\n-> vnindex_5state_v21_plus.csv saved ({len(out)} rows)")
