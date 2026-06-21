# -*- coding: utf-8 -*-
"""
build_v3_3_conc_variants.py
===========================
Build 2 v3.3 variants with additional concentration filter:

  v3.3b: RSI gate fires only when conc ≤ 0.55  (blocks narrow-market fires)
  v3.3c: RSI gate fires only when conc ≤ 0.45  (stricter; only very broad)

Same v3.3 logic, plus: if concentration_smooth > threshold at the moment
of detection, do NOT activate the gate — let the downgrade through.
For days with conc=N/A (pre-2014), gate fires as usual (no filter).

Saves 2 CSV files:
  vnindex_5state_tam_quan_v3_3b_full_history.csv
  vnindex_5state_tam_quan_v3_3c_full_history.csv
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
RSI_THR = 55

v31 = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_1_full_history.csv"))
v31["time"] = pd.to_datetime(v31["time"]); v31 = v31.sort_values("time").reset_index(drop=True)
dual = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v3_full.csv"))
dual["time"] = pd.to_datetime(dual["time"])

df = v31.merge(dual[["time","Close","concentration_smooth"]],
               on="time", how="left").reset_index(drop=True)
n = len(df)
close = df["Close"].values
v31_state = df["state"].values.astype(int)
conc = df["concentration_smooth"].values

def rsi14(c):
    delta = np.diff(c, prepend=c[0])
    up   = np.where(delta>0, delta, 0.0)
    down = np.where(delta<0, -delta, 0.0)
    out = np.full(len(c), np.nan)
    for i in range(14, len(c)):
        gain = up[i-13:i+1].mean(); loss = down[i-13:i+1].mean()
        rs = gain/loss if loss>0 else 100
        out[i] = 100 - 100/(1+rs)
    return out
rsi = rsi14(close)


def build_variant(conc_thr, label):
    """Apply v3.3 RSI gate, but only fire if conc ≤ conc_thr (or conc is NaN)."""
    result = v31_state.copy()
    blocked = False; blocked_at = None
    fires = []

    for t in range(1, n):
        cur_v31  = v31_state[t]; prev_v31 = v31_state[t-1]
        cur_rsi  = rsi[t]; cur_conc = conc[t]

        if blocked:
            if (cur_rsi is None) or np.isnan(cur_rsi) or (cur_rsi < RSI_THR):
                blocked = False; result[t] = cur_v31
            elif cur_v31 >= blocked_at:
                blocked = False; result[t] = cur_v31
            elif (blocked_at - cur_v31) >= 2:
                blocked = False; result[t] = cur_v31
            else:
                result[t] = blocked_at
        else:
            is_1step_dn = (prev_v31 - cur_v31 == 1)
            rsi_ok = (cur_rsi is not None) and (not np.isnan(cur_rsi)) and (cur_rsi >= RSI_THR)
            # Concentration filter: pass if NaN (pre-conc era) or conc ≤ threshold
            conc_ok = (cur_conc is None) or np.isnan(cur_conc) or (cur_conc <= conc_thr)
            if is_1step_dn and rsi_ok and conc_ok:
                blocked = True; blocked_at = prev_v31
                result[t] = blocked_at
                fires.append((df["time"].iloc[t], prev_v31, cur_v31, cur_rsi, cur_conc))

    n_trans = int((np.diff(result)!=0).sum())
    elev_days = int((result > v31_state).sum())
    print(f"\n=== {label}  (conc ≤ {conc_thr}) ===")
    print(f"  fires: {len(fires)} | transitions: {n_trans} | elev days: {elev_days}")
    return result, fires


for thr, suffix, label in [(0.55, "b", "v3.3b"), (0.45, "c", "v3.3c")]:
    result, fires = build_variant(thr, label)
    # Save
    out = pd.DataFrame({
        "time":      df["time"].dt.strftime("%Y-%m-%d"),
        "state":     result.astype(int),
        "state_raw": df["state_raw"].astype(int),
    })
    out_path = os.path.join(WORKDIR, f"vnindex_5state_tam_quan_v3_3{suffix}_full_history.csv")
    out.to_csv(out_path, index=False)
    print(f"  ✓ Saved: {os.path.basename(out_path)}")

# Also rebuild v3.3 (no conc filter) for reference (no-op, already exists)
print("\nReminder: v3.3 (no conc filter) = vnindex_5state_tam_quan_v3_3_full_history.csv (31 fires)")
