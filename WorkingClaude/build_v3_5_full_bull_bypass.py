# -*- coding: utf-8 -*-
"""
build_v3_5_full_bull_bypass.py
==============================
v3.5 = v3.4b + bull-conditional conc filter bypass.

When BTC_R6M = True (confirmed bull):
  • Bypass US override (use v3 staging, same as v3.4b)
  • ALSO bypass conc filter (RSI gate fires regardless of concentration)
    → in confirmed bull, narrow leadership is normal; conc filter would
       block legitimate gate fires that protect portfolio in bull pullbacks

When BTC_R6M = False:
  • Keep US override + conc filter (same as v3.3b out-of-bull behavior)

3 sub-variants tested:
  v3.5a: same conc threshold (0.55) but only outside bull
  v3.5b: NO conc filter at all (regardless of BTC) — test for completeness
  v3.5c: tighter conc threshold (0.65) outside bull — stricter

Output: vnindex_5state_tam_quan_v3_5{x}_full_history.csv
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
RSI_THR = 55

# Load
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
v31_state = df["state"].values.astype(int)
v3_state  = df["state_v3"].values.astype(int)
conc = df["concentration_smooth"].values

# RSI(14)
def rsi14(c):
    delta = np.diff(c, prepend=c[0])
    up   = np.where(delta>0, delta, 0.0); down = np.where(delta<0, -delta, 0.0)
    out = np.full(len(c), np.nan)
    for i in range(14, len(c)):
        gain = up[i-13:i+1].mean(); loss = down[i-13:i+1].mean()
        rs = gain/loss if loss>0 else 100; out[i] = 100 - 100/(1+rs)
    return out
rsi = rsi14(close)

# BTC_R6M
ma200 = pd.Series(close).rolling(200).mean().values
ma200_dev = close/ma200 - 1
ret_120d = pd.Series(close).pct_change(120).values
BTC_R6M = ((ret_120d > 0.15) & (ma200_dev > 0)) & ~np.isnan(ret_120d)

# Smoothing
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


def build(label, conc_thr_in_bull, conc_thr_out_bull):
    """
    conc_thr_in_bull = None means no conc filter when bull
    conc_thr_out_bull = threshold when not bull
    Both gates always fire when threshold is None.
    """
    # Step 1: bypass US in bull
    base = np.where(BTC_R6M, v3_state, v31_state)
    # Step 2: re-smooth
    base = rolling_mode(base, 3)
    base = min_stay_filter(base, 2)
    # Step 3: RSI gate + conditional conc filter
    result = base.copy()
    blocked = False; blocked_at = None; n_fires = 0; n_blocked_by_conc = 0
    for t in range(1, n):
        cur = base[t]; prev = base[t-1]; cr = rsi[t]; cc = conc[t]
        in_bull = bool(BTC_R6M[t])
        if blocked:
            if (cr is None) or np.isnan(cr) or (cr < RSI_THR):
                blocked=False; result[t]=cur
            elif cur >= blocked_at:
                blocked=False; result[t]=cur
            elif (blocked_at - cur) >= 2:
                blocked=False; result[t]=cur
            else:
                result[t] = blocked_at
        else:
            is_1step = (prev - cur == 1)
            rsi_ok = (cr is not None) and (not np.isnan(cr)) and (cr >= RSI_THR)
            # Conditional conc filter
            thr = conc_thr_in_bull if in_bull else conc_thr_out_bull
            if thr is None:
                conc_ok = True   # no filter — always allow gate
            else:
                conc_ok = (cc is None) or np.isnan(cc) or (cc <= thr)
            if is_1step and rsi_ok:
                if conc_ok:
                    blocked = True; blocked_at = prev; result[t] = blocked_at; n_fires += 1
                else:
                    n_blocked_by_conc += 1
    n_trans = int((np.diff(result)!=0).sum())
    print(f"  {label}: {n_fires} gate fires, {n_blocked_by_conc} blocked by conc, {n_trans} transitions")
    return result


variants = [
    ("v3.5a (bull:no-conc, !bull:0.55)", None, 0.55),
    ("v3.5b (no conc anywhere)",          None, None),
    ("v3.5c (bull:no-conc, !bull:0.65)", None, 0.65),
]
for label, t_in, t_out in variants:
    result = build(label, t_in, t_out)
    suffix = label.split()[0].replace("v3.5","").lower()
    out = pd.DataFrame({"time": df["time"].dt.strftime("%Y-%m-%d"),
                        "state": result.astype(int),
                        "state_raw": df["state_raw"].astype(int)})
    fn = f"vnindex_5state_tam_quan_v3_5{suffix}_full_history.csv"
    out.to_csv(os.path.join(WORKDIR, fn), index=False)
    print(f"    ✓ Saved {fn}\n")

# State distribution comparison
print("\nState distribution comparison:")
print(f"{'State':<10}{'v3.1':>8}{'v3.3b':>8}{'v3.4b':>8}{'v3.5a':>8}{'v3.5b':>8}{'v3.5c':>8}")
v33b = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_3b_full_history.csv"))["state"].values
v34b = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_4b_full_history.csv"))["state"].values
v35a = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_5a_full_history.csv"))["state"].values
v35b = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_5b_full_history.csv"))["state"].values
v35c = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_5c_full_history.csv"))["state"].values
for s in [1,2,3,4,5]:
    p1   = (v31_state==s).mean()*100
    p3b  = (v33b==s).mean()*100
    p4b  = (v34b==s).mean()*100
    p5a  = (v35a==s).mean()*100
    p5b  = (v35b==s).mean()*100
    p5c  = (v35c==s).mean()*100
    print(f"  {STATE_NAMES[s]:<8}{p1:>7.1f}%{p3b:>7.1f}%{p4b:>7.1f}%{p5a:>7.1f}%{p5b:>7.1f}%{p5c:>7.1f}%")
