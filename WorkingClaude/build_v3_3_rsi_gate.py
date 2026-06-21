# -*- coding: utf-8 -*-
"""
build_v3_3_rsi_gate.py
======================
v3.3 = v3.1 + "RSI uptrend protection" rule (from F6 diagnostic).

Rule:
  When v3.1 fires a 1-step downgrade AND VN-Index RSI(14) ≥ 55 at trigger:
    → Block the downgrade (hold previous state).
    → Continue blocking until one of:
       (a) RSI drops below 55 (momentum broken)
       (b) v3.1 state recovers to ≥ blocked level (system itself reverses)
       (c) v3.1 state drops 2+ steps below blocked level (real bear signal)

Intent: 30/138 downgrades fire on RSI ≥ 55 (i.e. during momentum tops
without actual breakdown). These 30 had T+20 mean +2.97%, T+60 +6.23%
— pure noise — while the remaining 108 retain ~base-rate quality.

Output: vnindex_5state_tam_quan_v3_3_full_history.csv
        Schema: time, state, state_raw  (same as v3.1)
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
RSI_THRESHOLD = 55

# Load v3.1 + close (for RSI)
v31 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_full_history.csv"))
v31["time"] = pd.to_datetime(v31["time"]); v31 = v31.sort_values("time").reset_index(drop=True)
dual = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_full.csv"))
dual["time"] = pd.to_datetime(dual["time"])

df = v31.merge(dual[["time","Close"]], on="time", how="left").reset_index(drop=True)
n = len(df)
close = df["Close"].values
v31_state = df["state"].values.astype(int)
print(f"Loaded {n} rows | {df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()}")

# ── RSI(14) ────────────────────────────────────────────────────────────
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

# ── Apply RSI gate ─────────────────────────────────────────────────────
result = v31_state.copy()
blocked = False
blocked_at = None  # the higher state we're holding
blocks = []  # log

for t in range(1, n):
    cur_v31  = v31_state[t]
    prev_v31 = v31_state[t-1]
    cur_rsi  = rsi[t]

    if blocked:
        # exit conditions
        if (cur_rsi is None) or np.isnan(cur_rsi) or (cur_rsi < RSI_THRESHOLD):
            blocked = False
            result[t] = cur_v31
        elif cur_v31 >= blocked_at:
            # v3.1 state recovered to/above blocked level — release
            blocked = False
            result[t] = cur_v31
        elif (blocked_at - cur_v31) >= 2:
            # v3.1 says state dropped 2+ steps — real bear, honor it
            blocked = False
            result[t] = cur_v31
        else:
            # hold blocked state
            result[t] = blocked_at
    else:
        # detect 1-step downgrade in v3.1 with RSI ≥ threshold
        if (prev_v31 - cur_v31 == 1) and (cur_rsi is not None) and (not np.isnan(cur_rsi)) and (cur_rsi >= RSI_THRESHOLD):
            blocked = True
            blocked_at = prev_v31
            result[t] = blocked_at
            blocks.append((df["time"].iloc[t], prev_v31, cur_v31, cur_rsi))
        # else leave result[t] = v31_state[t] (already from copy)

# Track how long each block lasted
release_dates = []
i = 0
while i < n:
    if i < len(blocks):
        pass  # logged separately
    i += 1

# ── Diagnostics ────────────────────────────────────────────────────────
n_trans_v31 = int((np.diff(v31_state)!=0).sum())
n_trans_v33 = int((np.diff(result)!=0).sum())
print(f"\nv3.1 transitions: {n_trans_v31}")
print(f"v3.3 transitions: {n_trans_v33}  (Δ {n_trans_v33-n_trans_v31:+d})")

print(f"\nRSI gate fired {len(blocks)} times:")
print(f"{'Date':<12}{'from→to (v3.1)':<24}{'RSI':>6}")
for dt, prv, cur, r in blocks:
    print(f"{dt.date().isoformat():<12}{STATE_NAMES[prv]+'→'+STATE_NAMES[cur]:<24}{r:>5.0f}")

# Days spent in elevated state (blocking active)
diff_days = (result > v31_state).sum()
print(f"\nDays held in elevated state (vs v3.1): {diff_days}")

# Distribution shift
print(f"\n{'State':<10} {'v3.1':>8} {'v3.3':>8} {'Δ':>8}")
for s in [1,2,3,4,5]:
    p1 = (v31_state==s).mean()*100; p3 = (result==s).mean()*100
    print(f"  {STATE_NAMES[s]:<8} {p1:>7.1f}% {p3:>7.1f}% {p3-p1:>+7.1f}pp")

# ── Save ──────────────────────────────────────────────────────────────
out = pd.DataFrame({
    "time":      df["time"].dt.strftime("%Y-%m-%d"),
    "state":     result.astype(int),
    "state_raw": df["state_raw"].astype(int),
})
out_path = os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_3_full_history.csv")
out.to_csv(out_path, index=False)
print(f"\n✓ Saved: {out_path}")
