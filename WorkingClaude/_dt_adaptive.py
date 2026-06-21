# -*- coding: utf-8 -*-
"""
Regime-adaptive 4-gate asymmetric commitment.
Confirmation thresholds SHRINK in turbulent regimes (high realized vol),
stay at base in calm regimes. Goal: catch 2008 crash + 2020 V-recovery fast
WITHOUT the modern-bull whipsaw cost of globally-fast thresholds.
"""
import os, sys, io
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
W = r"/home/trido/thanhdt/WorkingClaude"

# ---- load v3.4b base + align VNINDEX returns for vol regime ----
v34 = pd.read_csv(os.path.join(W, "_cmp_v34b.csv")); v34["time"] = pd.to_datetime(v34["time"])
vni = pd.read_csv(os.path.join(W, "VNINDEX.csv"), usecols=["time","Close"]); vni["time"] = pd.to_datetime(vni["time"])
df = v34.merge(vni, on="time", how="left").sort_values("time").reset_index(drop=True)
df["ret"] = df["Close"].pct_change().fillna(0.0)
base = df["state"].values.astype(int)
dates = df["time"].values
mask_m = dates >= np.datetime64("2014-01-01")

def regime_turbulent(ret, window=20, pctl=0.70):
    """Causal: turbulent if trailing realized vol > expanding pctl of vol (shifted)."""
    vol = pd.Series(ret).rolling(window).std()
    thr = vol.expanding(min_periods=60).quantile(pctl).shift(1)
    turb = (vol > thr).fillna(False).values
    return turb

def asym_dir_adaptive(states, turb, params, shrink, floor):
    default, enC, exC, enX, exX = params
    states = np.asarray(states, int); out = states.copy()
    committed = states[0]; ps, pr = states[0], 1
    for t in range(1, len(states)):
        s = states[t]
        if s == ps: pr += 1
        else: ps, pr = s, 1
        if ps == committed:
            out[t] = committed; continue
        if ps == 1:   need = enC
        elif ps == 5: need = enX
        elif committed == 1: need = exC
        elif committed == 5: need = exX
        else: need = default
        if turb[t]:
            need = max(floor, int(round(need * shrink)))
        if pr >= need:
            committed = ps
        out[t] = committed
    return out

def ntr(s, mask=None):
    s = np.asarray(s, int)
    if mask is not None: s = s[mask]
    return int((s[1:] != s[:-1]).sum())

def ev(s):
    out = pd.DataFrame({"time": df["time"], "state": s})
    rm = simulate_timing(out, start_date="2014-01-01")
    rf = simulate_timing(out, start_date=None)
    r07 = simulate_timing(out, start_date="2007-01-01", end_date="2010-12-31")
    n = rm["nav_series"]; a = n[n.index.year == 2020]; y20 = (a.iloc[-1]/a.iloc[0]-1)*100
    return (rm["final_nav"]/1e9, rm["cagr"]*100, rm["sharpe"], rm["max_dd"]*100,
            rm["calmar"], ntr(s, mask_m), y20, rf["cagr"]*100, rf["max_dd"]*100, r07["max_dd"]*100)

BASE = (10, 25, 10, 25, 10)  # validated 4-gate = DT canonical
hdr = f"  {'variant':<34}{'NAVm':>7}{'CAGRm':>7}{'Shm':>5}{'DDm':>7}{'Calm':>6}{'Trm':>4}{'2020':>7} |{'CAGRf':>7}{'DDf':>7}{'DD0708':>8}"
def prow(name, v):
    print(f"  {name:<34}{v[0]:>7.2f}{v[1]:>+7.2f}{v[2]:>5.2f}{v[3]:>7.1f}{v[4]:>6.2f}{v[5]:>4}{v[6]:>+7.1f} |{v[7]:>+7.2f}{v[8]:>7.1f}{v[9]:>8.1f}")

# canonical (no adaptive: shrink=1)
turb_dummy = np.zeros(len(base), bool)
print("="*120); print("  REFERENCE (no adaptive)"); print("="*120); print(hdr)
prow("DT canonical 4-gate", ev(asym_dir_adaptive(base, turb_dummy, BASE, 1.0, 99)))

print("\n" + "="*120)
print("  REGIME-ADAPTIVE: shrink thresholds when turbulent (vol > expanding pctl)")
print("="*120); print(hdr)
for pctl in (0.60, 0.70, 0.80):
    turb = regime_turbulent(df["ret"].values, window=20, pctl=pctl)
    frac = turb[mask_m].mean()*100
    for shrink in (0.3, 0.4, 0.5):
        for floor in (3, 5):
            s = asym_dir_adaptive(base, turb, BASE, shrink, floor)
            prow(f"p{int(pctl*100)} shrink{shrink} floor{floor} ({frac:.0f}%turb)", ev(s))
    print()
