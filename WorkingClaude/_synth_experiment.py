# -*- coding: utf-8 -*-
"""
Synthesis experiment: DT-style asymmetric causal commitment applied to
Tinh Te's composite (better regime detector) vs v3.4b base, + bull-aware lock.
Measured on the pure-VNINDEX money sim.
"""
import os, sys, io
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ---------- DT asymmetric causal commitment (from build_dt_variants_csv.py) ----------
def asym_commit(states, default_min, target_state_min):
    states = np.asarray(states, dtype=int)
    out = states.copy()
    committed = states[0]
    pending_state, pending_run = states[0], 1
    out[0] = committed
    for t in range(1, len(states)):
        s = states[t]
        if s == pending_state: pending_run += 1
        else: pending_state, pending_run = s, 1
        need = target_state_min.get(pending_state, default_min)
        if pending_run >= need and pending_state != committed:
            committed = pending_state
        out[t] = committed
    return out

# ---------- v3.4b bull-aware lock: block 1-step downgrade in confirmed bull ----------
def bull_lock(committed, raw, bull_mask):
    """Causal: in bull regime, hold prev state if proposed is a 1-level downgrade.
    Release if bull ends OR raw drops >=2 levels below held state."""
    committed = np.asarray(committed, dtype=int); raw = np.asarray(raw, dtype=int)
    out = committed.copy()
    for t in range(1, len(out)):
        prev = out[t-1]
        prop = committed[t]
        if bull_mask[t] and prop == prev - 1 and raw[t] >= prev - 1:
            out[t] = prev
        else:
            out[t] = prop
    return out

# ---------- Load bases ----------
tt  = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state.csv"))          # Tinh Te (state, state_raw)
v34 = pd.read_csv(os.path.join(WORKDIR, "data/_cmp_v34b.csv"))               # v3.4b (state)
v34r= pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))
for d in (tt, v34, v34r): d["time"] = pd.to_datetime(d["time"])

# bull mask from VNINDEX: 6M (126-session) return > 15% AND Close > MA200
vni = pd.read_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"), usecols=["time","Close"])
vni["time"] = pd.to_datetime(vni["time"]); vni = vni.sort_values("time").reset_index(drop=True)
vni["ma200"] = vni["Close"].rolling(200).mean()
vni["r6m"]   = vni["Close"] / vni["Close"].shift(126) - 1
vni["bull"]  = (vni["r6m"] > 0.15) & (vni["Close"] > vni["ma200"])

def attach_bull(df):
    m = df.merge(vni[["time","bull"]], on="time", how="left")
    m["bull"] = m["bull"].fillna(False).values
    return m

tt  = attach_bull(tt).sort_values("time").reset_index(drop=True)
v34 = attach_bull(v34).sort_values("time").reset_index(drop=True)

def ntrans(s, mask=None):
    s = np.asarray(s, int)
    if mask is not None: s = s[mask]
    return int((s[1:] != s[:-1]).sum())

def run(name, df, base_col, params, use_bull=False, raw_col=None):
    base = df[base_col].values.astype(int)
    sm = asym_commit(base, params[0], {1: params[1], 5: params[2]})
    if use_bull:
        raw = df[raw_col].values.astype(int) if raw_col else base
        sm = bull_lock(sm, raw, df["bull"].values)
    out = pd.DataFrame({"time": df["time"], "state": sm})
    res_m = simulate_timing(out, start_date="2014-01-01")
    res_f = simulate_timing(out, start_date=None)
    mask_m = df["time"].values >= np.datetime64("2014-01-01")
    return {
        "name": name,
        "nav_m": res_m["final_nav"]/1e9, "cagr_m": res_m["cagr"]*100,
        "sh_m": res_m["sharpe"], "dd_m": res_m["max_dd"]*100, "cal_m": res_m["calmar"],
        "tr_m": ntrans(sm, mask_m),
        "nav_f": res_f["final_nav"]/1e9, "cagr_f": res_f["cagr"]*100,
        "dd_f": res_f["max_dd"]*100, "tr_f": ntrans(sm),
    }

def hdr():
    print(f"  {'variant':<34}{'NAVm':>7}{'CAGRm':>7}{'Shm':>5}{'DDm':>7}{'Calm':>6}{'Trm':>5}  | {'NAVf':>7}{'CAGRf':>7}{'DDf':>7}{'Trf':>5}")
def row(r):
    print(f"  {r['name']:<34}{r['nav_m']:>7.2f}{r['cagr_m']:>+7.2f}{r['sh_m']:>5.2f}{r['dd_m']:>7.1f}{r['cal_m']:>6.2f}{r['tr_m']:>5}  | {r['nav_f']:>7.2f}{r['cagr_f']:>+7.2f}{r['dd_f']:>7.1f}{r['tr_f']:>5}")

print("="*120)
print("  BASELINES (no synthesis)")
print("="*120); hdr()
# raw baselines (no asym commit): use very low min to pass through
row(run("Tinh_Te (mode3, as-is)",   tt,  "state", (1,1,1)))
row(run("v3.4b (as-is)",            v34, "state", (1,1,1)))
row(run("DT_10_25_25 (=v34 base)",  v34, "state", (10,25,25)))

print("\n" + "="*120)
print("  SYNTHESIS A: asym-commit on Tinh Te composite (state_raw), param sweep")
print("="*120); hdr()
for p in [(10,25,25),(7,20,20),(10,30,30),(15,25,25),(10,20,30),(15,30,25)]:
    row(run(f"TT_raw + asym{p}", tt, "state_raw", p))

print("\n" + "="*120)
print("  SYNTHESIS A2: asym-commit on Tinh Te smoothed (state), param sweep")
print("="*120); hdr()
for p in [(10,25,25),(7,20,20),(10,30,30),(15,25,25)]:
    row(run(f"TT_state + asym{p}", tt, "state", p))

print("\n" + "="*120)
print("  SYNTHESIS B: best TT base + asym-commit + bull-aware lock")
print("="*120); hdr()
for p in [(10,25,25),(10,30,30),(15,25,25)]:
    row(run(f"TT_raw + asym{p} + bull", tt, "state_raw", p, use_bull=True, raw_col="state_raw"))
    row(run(f"TT_state + asym{p} + bull", tt, "state", p, use_bull=True, raw_col="state_raw"))
