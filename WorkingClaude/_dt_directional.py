# -*- coding: utf-8 -*-
"""
Directional asymmetric commitment: separate confirmation thresholds for
ENTERING vs EXITING the extreme states (CRISIS, EX-BULL).
Generalizes DT_10_25_25 (which only keyed on pending state).
"""
import os, sys, io
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
W = r"/home/trido/thanhdt/WorkingClaude"

def asym_dir(states, default, enter_crisis, exit_crisis, enter_exbull, exit_exbull):
    """need(committed, pending):
       - pending in {CRISIS,EXBULL}  -> entering extreme (slow)
       - committed in {CRISIS,EXBULL} -> exiting extreme (own param)
       - else default."""
    states = np.asarray(states, int); out = states.copy()
    committed = states[0]; ps, pr = states[0], 1
    for t in range(1, len(states)):
        s = states[t]
        if s == ps: pr += 1
        else: ps, pr = s, 1
        if ps == committed:
            out[t] = committed; continue
        if ps == 1:   need = enter_crisis
        elif ps == 5: need = enter_exbull
        elif committed == 1: need = exit_crisis
        elif committed == 5: need = exit_exbull
        else: need = default
        if pr >= need:
            committed = ps
        out[t] = committed
    return out

v34 = pd.read_csv(os.path.join(W, "_cmp_v34b.csv")); v34["time"] = pd.to_datetime(v34["time"])
base = v34["state"].values.astype(int)
mask_m = v34["time"].values >= np.datetime64("2014-01-01")

def ntr(s, mask=None):
    s = np.asarray(s, int)
    if mask is not None: s = s[mask]
    return int((s[1:] != s[:-1]).sum())

mask_f = np.ones(len(v34), bool)
def ev(s):
    out = pd.DataFrame({"time": v34["time"], "state": s})
    rm = simulate_timing(out, start_date="2014-01-01")
    rf = simulate_timing(out, start_date=None)            # TRUE full 2000-2026
    re0708 = simulate_timing(out, start_date="2007-01-01", end_date="2010-12-31")  # euphoria->crash
    n = rm["nav_series"]
    yr = {}
    for y in (2018, 2020, 2022):
        a = n[n.index.year == y]
        yr[y] = (a.iloc[-1]/a.iloc[0]-1)*100 if len(a) > 5 else float("nan")
    return dict(nav_m=rm["final_nav"]/1e9, cagr_m=rm["cagr"]*100, sh_m=rm["sharpe"],
                dd_m=rm["max_dd"]*100, cal_m=rm["calmar"], tr_m=ntr(s, mask_m),
                cagr_f=rf["cagr"]*100, dd_f=rf["max_dd"]*100, tr_f=ntr(s),
                cagr0708=re0708["cagr"]*100, dd0708=re0708["max_dd"]*100,
                y18=yr[2018], y20=yr[2020], y22=yr[2022])

rows = []
# canonical DT in new param space: default=10, enter_c=25, exit_c=10, enter_x=25, exit_x=10
def add(name, p):
    s = asym_dir(base, *p)
    r = ev(s); r["name"] = name; r["p"] = p; rows.append(r)

add("DT canonical (10/25/10/25/10)", (10, 25, 10, 25, 10))
# Grid: vary exit_crisis (recovery speed) and exit_exbull (derisk speed)
for ec in (5, 7, 10, 15, 20):
    for ex in (3, 5, 7, 10):
        add(f"exitC={ec:<2} exitX={ex:<2}", (10, 25, ec, 25, ex))

hdr = f"  {'variant':<32}{'NAVm':>7}{'CAGRm':>7}{'Shm':>5}{'DDm':>7}{'Calm':>6}{'Trm':>4} {'2020':>7}  |{'CAGRf':>7}{'DDf':>7}{'Trf':>4} |{'C0708':>7}{'DD0708':>8}"
def prow(r):
    print(f"  {r['name']:<32}{r['nav_m']:>7.2f}{r['cagr_m']:>+7.2f}{r['sh_m']:>5.2f}{r['dd_m']:>7.1f}{r['cal_m']:>6.2f}{r['tr_m']:>4}{r['y20']:>+7.1f}  |{r['cagr_f']:>+7.2f}{r['dd_f']:>7.1f}{r['tr_f']:>4} |{r['cagr0708']:>+7.1f}{r['dd0708']:>8.1f}")

print("="*132); print("  CANONICAL"); print("="*132); print(hdr)
prow(rows[0])
print("\n" + "="*132); print("  GRID (sorted by modern NAV)"); print("="*132); print(hdr)
for r in sorted(rows[1:], key=lambda x: -x["nav_m"]):
    prow(r)
print("\n  --- top 5 by Calmar (modern) ---"); print(hdr)
for r in sorted(rows[1:], key=lambda x: -x["cal_m"])[:5]:
    prow(r)
