# -*- coding: utf-8 -*-
"""
Synthesis v2: DT (v3.4b base + asym commit) keeps money+stability;
overlay Tinh Te's FAST defensive detection as a protective floor to cut DD.
state = DT, but when Tinh Te is in CRISIS/BEAR, pull DT down to derisk faster.
"""
import os, sys, io
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

def asym_commit(states, default_min, target_state_min):
    states = np.asarray(states, dtype=int); out = states.copy()
    committed = states[0]; pending_state, pending_run = states[0], 1
    for t in range(1, len(states)):
        s = states[t]
        if s == pending_state: pending_run += 1
        else: pending_state, pending_run = s, 1
        need = target_state_min.get(pending_state, default_min)
        if pending_run >= need and pending_state != committed: committed = pending_state
        out[t] = committed
    return out

tt  = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state.csv"))
v34 = pd.read_csv(os.path.join(WORKDIR, "_cmp_v34b.csv"))
for d in (tt, v34): d["time"] = pd.to_datetime(d["time"])
m = v34.rename(columns={"state":"v34"}).merge(
    tt.rename(columns={"state":"tt","state_raw":"tt_raw"}), on="time", how="inner"
).sort_values("time").reset_index(drop=True)

def ntrans(s, mask=None):
    s = np.asarray(s, int)
    if mask is not None: s = s[mask]
    return int((s[1:] != s[:-1]).sum())

def evalstate(name, s, df):
    out = pd.DataFrame({"time": df["time"], "state": np.asarray(s, int)})
    rm = simulate_timing(out, start_date="2014-01-01"); rf = simulate_timing(out)
    mask = df["time"].values >= np.datetime64("2014-01-01")
    return dict(name=name, nav_m=rm["final_nav"]/1e9, cagr_m=rm["cagr"]*100, sh_m=rm["sharpe"],
                dd_m=rm["max_dd"]*100, cal_m=rm["cal" if "cal" in rm else "calmar"]*1 if False else rm["calmar"],
                tr_m=ntrans(s,mask), nav_f=rf["final_nav"]/1e9, cagr_f=rf["cagr"]*100,
                dd_f=rf["max_dd"]*100, tr_f=ntrans(s))
def hdr(): print(f"  {'variant':<40}{'NAVm':>7}{'CAGRm':>7}{'Shm':>5}{'DDm':>7}{'Calm':>6}{'Trm':>5}  | {'NAVf':>7}{'CAGRf':>7}{'DDf':>7}{'Trf':>5}")
def row(r): print(f"  {r['name']:<40}{r['nav_m']:>7.2f}{r['cagr_m']:>+7.2f}{r['sh_m']:>5.2f}{r['dd_m']:>7.1f}{r['cal_m']:>6.2f}{r['tr_m']:>5}  | {r['nav_f']:>7.2f}{r['cagr_f']:>+7.2f}{r['dd_f']:>7.1f}{r['tr_f']:>5}")

# DT canonical = v34 base + asym(10,25,25)
dt = asym_commit(m["v34"].values, 10, {1:25,5:25})

print("="*120); print("  REFERENCE"); print("="*120); hdr()
row(evalstate("Tinh_Te (DD champ)", m["tt"].values, m))
row(evalstate("DT_10_25_25 (money champ)", dt, m))

print("\n"+"="*120)
print("  FLOOR SYNTHESIS: state = min(DT, TinhTe-defensive-floor)")
print("  i.e. if Tinh Te derisks to CRISIS/BEAR fast, pull DT down too")
print("="*120); hdr()
# Floor variants: when TT in {1} or {1,2}, cap DT at TT level
tt_s = m["tt"].values; tt_raw = m["tt_raw"].values
# A: floor only on CRISIS (TT==1 -> force <=1)
f_crisis     = np.minimum(dt, np.where(tt_s==1, 1, 5))
# B: floor on CRISIS+BEAR (TT<=2 -> cap DT at TT)
f_crisisbear = np.where(tt_s<=2, np.minimum(dt, tt_s), dt)
# C: floor using TT raw (faster) on CRISIS
f_crisis_raw = np.minimum(dt, np.where(tt_raw==1, 1, 5))
# D: floor CRISIS+BEAR using raw
f_cb_raw     = np.where(tt_raw<=2, np.minimum(dt, tt_raw), dt)
row(evalstate("DT + TT-CRISIS floor",        f_crisis,     m))
row(evalstate("DT + TT-CRISIS/BEAR floor",   f_crisisbear, m))
row(evalstate("DT + TT_raw-CRISIS floor",    f_crisis_raw, m))
row(evalstate("DT + TT_raw-CRISIS/BEAR floor",f_cb_raw,    m))

# Re-smooth the floored series with light asym to remove floor-induced flicker
print("\n"+"="*120)
print("  FLOOR + light re-commit (asym 5,15,15) to clean floor flicker")
print("="*120); hdr()
for nm, base in [("CRISIS", f_crisis), ("CRISIS/BEAR", f_crisisbear),
                 ("CRISIS_raw", f_crisis_raw), ("CRISIS/BEAR_raw", f_cb_raw)]:
    s2 = asym_commit(base, 5, {1:5, 5:15})  # crisis re-entry fast (5), exbull slow
    row(evalstate(f"DT+{nm}floor + recommit", s2, m))
