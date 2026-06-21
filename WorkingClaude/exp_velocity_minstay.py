# -*- coding: utf-8 -*-
"""
exp_velocity_minstay.py
=======================
EXPERIMENT (user idea 2026-06-03): make the equal-weight label smoother
VELOCITY-AWARE on the DE-RISK direction only.

Canonical pipeline tail:  state_dvg -> rolling_mode(15) -> min_stay_filter(7) = state
min_stay_filter merges any run < 7 sessions into the PREVIOUS state. That erases
short defensive dips regardless of how FAST the drop was.

Velocity-aware variant: keep a short DE-RISK run (state < preceding committed state)
even if < min_days, PROVIDED the EMA r_score slope over the last `vk` sessions at the
run's start is steeply negative (<= q-quantile of the slope distribution). A small
floor (FLOOR days) still guards against 1-2 session flicker. Up-moves & choppy moves
keep the full canonical dwell (no change) -> asymmetric by SPEED.

Eval = pure-index Kelly-style metric (simulate_state_timing), the same metric used to
adopt DT. Reports CAGR / MaxDD / Sharpe / Calmar / #transitions for full(2011) & 2014.
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_state_timing import simulate_timing

MODE_WIN, MIN_STAY = 15, 7

# ---- canonical smoothing primitives (copied verbatim from vnindex_5state_system) ----
def rolling_mode(states, window=MODE_WIN):
    out = states.copy()
    for t in range(window - 1, len(states)):
        wv = states[t-window+1:t+1]
        vals, counts = np.unique(wv, return_counts=True)
        cand = vals[counts == counts.max()]
        for v in reversed(wv):
            if v in cand:
                out[t] = v; break
    return out

def min_stay_filter(states, min_days=MIN_STAY):
    out = states.copy(); changed = True
    while changed:
        changed = False; i = 0
        while i < len(out):
            j = i + 1
            while j < len(out) and out[j] == out[i]:
                j += 1
            if (j - i) < min_days:
                fill = out[i-1] if i > 0 else (out[j] if j < len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

def min_stay_velocity(states, slope, min_days=MIN_STAY, vk=5, q=0.10, floor=3):
    """Velocity-aware min_stay. Keep a short run if it is a DE-RISK move (state lower
    than the previous committed state) AND slope at run start is <= the q-quantile of
    negative slopes (a steep drop), down to a small `floor`. Else canonical merge."""
    s = pd.Series(slope)
    neg = s[s < 0]
    thr = neg.quantile(q) if len(neg) > 20 else -np.inf   # steeper than this => fast
    out = states.copy(); changed = True
    passn = 0
    while changed and passn < 50:
        changed = False; passn += 1; i = 0
        while i < len(out):
            j = i + 1
            while j < len(out) and out[j] == out[i]:
                j += 1
            run_len = j - i
            prev = out[i-1] if i > 0 else None
            is_derisk = (prev is not None) and (out[i] < prev)
            sl = slope[i] if (i < len(slope) and not np.isnan(slope[i])) else 0.0
            fast = is_derisk and (sl <= thr) and (run_len >= floor)
            if run_len < min_days and not fast:
                fill = out[i-1] if i > 0 else (out[j] if j < len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

def count_transitions(st):
    return int(np.sum(np.asarray(st)[1:] != np.asarray(st)[:-1]))

def evaluate(state_arr, time_arr, label):
    df = pd.DataFrame({"time": time_arr, "state": state_arr})
    rows = {}
    for start in ("2011-01-01", "2014-01-01"):
        r = simulate_timing(df, start_date=start)
        sub = df[pd.to_datetime(df["time"]) >= pd.Timestamp(start)]
        rows[start] = dict(cagr=r["cagr"], dd=r["max_dd"], sharpe=r["sharpe"],
                           calmar=r["calmar"], trans=count_transitions(sub["state"].values))
    return label, rows

# ---- load intermediate ----
m = pd.read_csv(os.path.join(WORKDIR, "data", "vnindex_5state_intermediate.csv"))
m["time"] = pd.to_datetime(m["time"])
state_dvg = m["state_dvg"].values.astype(int)
rema = m["r_score_ema"].values.astype(float)
tarr = m["time"].values

results = []

# CANONICAL (reproduce baseline from state_dvg)
canon = min_stay_filter(rolling_mode(state_dvg, MODE_WIN), MIN_STAY)
# sanity: should equal the exported 'state'
mismatch = int(np.sum(canon != m["state"].values.astype(int)))
print(f"[sanity] reconstructed canon vs exported state mismatch = {mismatch} (expect 0)")
results.append(evaluate(canon, tarr, "CANON ms7"))

# VELOCITY VARIANTS — grid over (vk, q, floor)
mode_state = rolling_mode(state_dvg, MODE_WIN)
for vk in (3, 5):
    slope = np.full(len(rema), np.nan)
    slope[vk:] = rema[vk:] - rema[:-vk]
    for q in (0.05, 0.10, 0.20):
        for floor in (2, 3):
            vstate = min_stay_velocity(mode_state, slope, MIN_STAY, vk=vk, q=q, floor=floor)
            lbl = f"VELO vk{vk} q{int(q*100)} fl{floor}"
            results.append(evaluate(vstate, tarr, lbl))

# ---- report ----
print("\n" + "="*108)
print("VELOCITY-GATED DE-RISK min_stay vs CANONICAL — pure-index Kelly metric")
print("="*108)
for window in ("2011-01-01", "2014-01-01"):
    print(f"\n--- since {window} ---")
    print(f"  {'variant':22s}{'CAGR':>8s}{'MaxDD':>9s}{'Sharpe':>8s}{'Calmar':>8s}{'#trans':>8s}{'  vs CANON CAGR':>16s}")
    base = next(r[1][window]['cagr'] for r in results if r[0]=='CANON ms7')
    for lbl, rows in results:
        d = rows[window]
        delta = (d['cagr']-base)*100
        mark = "  ← base" if lbl=='CANON ms7' else f"  {delta:+.2f}pp"
        print(f"  {lbl:22s}{d['cagr']*100:7.2f}%{d['dd']*100:8.1f}%{d['sharpe']:8.2f}{d['calmar']:8.2f}{d['trans']:8d}{mark:>16s}")
print("\nDONE.")
