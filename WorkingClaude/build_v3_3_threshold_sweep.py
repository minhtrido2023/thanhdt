# -*- coding: utf-8 -*-
"""
build_v3_3_threshold_sweep.py
=============================
Build v3.3 variants across full conc threshold sweep for walk-forward test.

Thresholds: 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70
(0.45 = v3.3c, 0.55 = v3.3b already exist; v3.3 itself = no conc filter)

Output: vnindex_5state_tam_quan_v3_3_t{XX}_full_history.csv where XX = threshold*100
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
RSI_THR = 55
THRESHOLDS = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]

v31 = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_1_full_history.csv"))
v31["time"] = pd.to_datetime(v31["time"]); v31 = v31.sort_values("time").reset_index(drop=True)
dual = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v3_full.csv"))
dual["time"] = pd.to_datetime(dual["time"])
df = v31.merge(dual[["time","Close","concentration_smooth"]], on="time", how="left").reset_index(drop=True)
n = len(df); close = df["Close"].values
v31_state = df["state"].values.astype(int); conc = df["concentration_smooth"].values

def rsi14(c):
    delta = np.diff(c, prepend=c[0])
    up   = np.where(delta>0, delta, 0.0); down = np.where(delta<0, -delta, 0.0)
    out = np.full(len(c), np.nan)
    for i in range(14, len(c)):
        gain = up[i-13:i+1].mean(); loss = down[i-13:i+1].mean()
        rs = gain/loss if loss>0 else 100; out[i] = 100 - 100/(1+rs)
    return out
rsi = rsi14(close)

def build(conc_thr):
    result = v31_state.copy()
    blocked = False; blocked_at = None; n_fires = 0
    for t in range(1, n):
        cv = v31_state[t]; pv = v31_state[t-1]; cr = rsi[t]; cc = conc[t]
        if blocked:
            if (cr is None) or np.isnan(cr) or (cr < RSI_THR): blocked=False; result[t]=cv
            elif cv >= blocked_at: blocked=False; result[t]=cv
            elif (blocked_at - cv) >= 2: blocked=False; result[t]=cv
            else: result[t] = blocked_at
        else:
            is_1step = (pv - cv == 1)
            rsi_ok = (cr is not None) and (not np.isnan(cr)) and (cr >= RSI_THR)
            conc_ok = (cc is None) or np.isnan(cc) or (cc <= conc_thr)
            if is_1step and rsi_ok and conc_ok:
                blocked = True; blocked_at = pv; result[t] = blocked_at; n_fires += 1
    return result, n_fires

for thr in THRESHOLDS:
    result, n_fires = build(thr)
    suffix = f"t{int(thr*100):02d}"
    out = pd.DataFrame({"time": df["time"].dt.strftime("%Y-%m-%d"),
                        "state": result.astype(int), "state_raw": df["state_raw"].astype(int)})
    fn = f"vnindex_5state_tam_quan_v3_3_{suffix}_full_history.csv"
    out.to_csv(os.path.join(WORKDIR, fn), index=False)
    print(f"  conc≤{thr:.2f} → {n_fires:>2} fires → {fn}")
