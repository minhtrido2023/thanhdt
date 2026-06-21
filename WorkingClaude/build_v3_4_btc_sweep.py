# -*- coding: utf-8 -*-
"""
build_v3_4_btc_sweep.py
=======================
Build v3.4 variants with different BTC definitions for walk-forward test.

BTC definition: return over H trading days > T% AND VNI > MA200

Variants:
  H=120 (6M):   T = 5, 10, 15, 20, 25, 30%  (6 variants)
  H=60  (3M):   T = 5, 8, 12, 15%           (4 variants)
  H=180 (9M):   T = 15, 20, 25, 30%         (4 variants)

= 14 variants total. Plus baseline v3.1 + current v3.4b = 16 backtests.

Robustness check: if FULL CAGR has plateau across reasonable thresholds
and IS-best matches OOS-best → not overfit.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
RSI_THR = 55
CONC_THR = 0.55

# Load all
v31 = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_1_full_history.csv"))
v31["time"] = pd.to_datetime(v31["time"]); v31 = v31.sort_values("time").reset_index(drop=True)
v3_stg = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v3_staging.csv"))
v3_stg["time"] = pd.to_datetime(v3_stg["time"])
v3_stg = v3_stg.rename(columns={"state": "state_v3"})
dr  = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])
df = v31.merge(v3_stg[["time","state_v3"]], on="time", how="left").merge(
    dr[["time","Close","concentration_smooth"]], on="time", how="left").reset_index(drop=True)
n = len(df); close = df["Close"].values
v31_state = df["state"].values.astype(int); v3_state = df["state_v3"].values.astype(int)
conc = df["concentration_smooth"].values

def rsi14(c):
    delta = np.diff(c, prepend=c[0])
    up   = np.where(delta>0, delta, 0.0); down = np.where(delta<0, -delta, 0.0)
    out = np.full(len(c), np.nan)
    for i in range(14, len(c)):
        gain = up[i-13:i+1].mean(); loss = down[i-13:i+1].mean()
        rs = gain/loss if loss>0 else 100; out[i] = 100 - 100/(1+rs)
    return out
rsi = rsi14(close)

ma200 = pd.Series(close).rolling(200).mean().values
ma200_dev = close/ma200 - 1

def make_btc(horizon_days, threshold_pct):
    ret = pd.Series(close).pct_change(horizon_days).values
    return ((ret > threshold_pct/100) & (ma200_dev > 0)) & ~np.isnan(ret)

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

def build_v34(btc_arr):
    base = np.where(btc_arr, v3_state, v31_state)
    base = rolling_mode(base, 3)
    base = min_stay_filter(base, 2)
    result = base.copy()
    blocked=False; blocked_at=None
    for t in range(1, n):
        cur=base[t]; prev=base[t-1]; cr=rsi[t]; cc=conc[t]
        if blocked:
            if (cr is None) or np.isnan(cr) or (cr<RSI_THR): blocked=False; result[t]=cur
            elif cur>=blocked_at: blocked=False; result[t]=cur
            elif (blocked_at-cur)>=2: blocked=False; result[t]=cur
            else: result[t]=blocked_at
        else:
            is_1step=(prev-cur==1)
            rsi_ok = (cr is not None) and (not np.isnan(cr)) and (cr>=RSI_THR)
            conc_ok = (cc is None) or np.isnan(cc) or (cc<=CONC_THR)
            if is_1step and rsi_ok and conc_ok:
                blocked=True; blocked_at=prev; result[t]=blocked_at
    return result

# Define sweep
SWEEP = []
# 6M (H=120) — main horizon
for t in [5, 10, 15, 20, 25, 30]:
    SWEEP.append((120, t, f"6M_T{t:02d}"))
# 3M (H=60)
for t in [5, 8, 12, 15]:
    SWEEP.append((60, t, f"3M_T{t:02d}"))
# 9M (H=180)
for t in [15, 20, 25, 30]:
    SWEEP.append((180, t, f"9M_T{t:02d}"))

print(f"Building {len(SWEEP)} v3.4 variants ...")
for h, thr, suffix in SWEEP:
    btc = make_btc(h, thr)
    n_bull_days = int(btc.sum())
    n_bypass = int(((v3_state != v31_state) & btc).sum())
    result = build_v34(btc)
    n_trans = int((np.diff(result)!=0).sum())
    print(f"  H={h:>3}d T>{thr:>2}%  bull_days={n_bull_days:>4}  override_bypass={n_bypass:>3}  trans={n_trans}")
    out = pd.DataFrame({"time": df["time"].dt.strftime("%Y-%m-%d"),
                        "state": result.astype(int),
                        "state_raw": df["state_raw"].astype(int)})
    fn = f"vnindex_5state_tam_quan_v3_4_btc{suffix}_full_history.csv"
    out.to_csv(os.path.join(WORKDIR, fn), index=False)

print(f"\n  ✓ {len(SWEEP)} variants saved as vnindex_5state_tam_quan_v3_4_btc{{H}}_T{{T}}_full_history.csv")
