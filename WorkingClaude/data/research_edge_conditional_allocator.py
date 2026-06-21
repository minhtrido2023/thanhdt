# -*- coding: utf-8 -*-
"""research_edge_conditional_allocator.py — should the LAG/BAL allocator tilt to LAG 65% ONLY when
LAG's own edge-health is positive? (user 2026-06-13, combining [[edge_health_monitor]]).

The allocator is a RETURN-STREAM overlay on the two standalone book NAVs -> we can re-test tilt rules
WITHOUT re-running the sim, using nav_bal_ref / nav_lag_ref from the postbull audit file + the causal
LAG edge-health series (mean12 = trailing-12M mean LAG trade post-return) from lag_edge_health.csv.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
W = r"/home/trido/thanhdt/WorkingClaude"; os.chdir(W)

# book NAVs (postbull-gated standalone 25B books) + state
A = pd.read_csv("data/v23c_golive_audit_2014_now_matpostbull_shrink0.csv", low_memory=False)
d = A[A["record_type"] == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d["ymd"]); d = d.set_index("ymd")
navb = d["nav_bal_ref"].astype(float); navl = d["nav_lag_ref"].astype(float)
state = d["state"].astype(float).astype(int)
common = d.index
rb = navb.pct_change().fillna(0).values; rl = navl.pct_change().fillna(0).values
st = state.values

# causal LAG edge-health: mean12 (trailing-12M mean trade return %), forward-filled daily
eh = pd.read_csv("data/lag_edge_health.csv", parse_dates=["entry"]).drop_duplicates("entry").set_index("entry").sort_index()
mean12 = eh["mean12"].reindex(common, method="ffill")
print(f"LAG edge-health mean12: latest {mean12.iloc[-1]:.2f}% | "
      f"range [{mean12.min():.1f}, {mean12.max():.1f}] | %time<4%: {(mean12<4).mean()*100:.0f}%")

TOTAL = 50e9; BAND = 0.10; TC = 0.001
def run_alloc(wfunc):
    """band-only allocator recurrence; wfunc(i)->target w_LAG. Returns combined NAV series."""
    w0 = wfunc(0); cb = (1-w0)*TOTAL; cl = w0*TOTAL; out = np.empty(len(common)); nreb = 0
    for i in range(len(common)):
        if i > 0: cb *= (1+rb[i]); cl *= (1+rl[i])
        P = cb+cl; wt = wfunc(i)
        if P > 0 and abs(cl/P - wt) > BAND:
            P -= TC*abs(wt*P - cl); cl = wt*P; cb = (1-wt)*P; nreb += 1
        out[i] = cb+cl
    return pd.Series(out, index=common), nreb

def met(s, a="2014-01-01", b="2027-01-01"):
    s = s[(s.index>=a)&(s.index<=b)].dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    r=s.pct_change().dropna(); c=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; dd=(s/s.cummax()-1).min()
    return c*100, r.mean()/r.std()*np.sqrt(252), dd*100, c/abs(dd)
def dd_win(s,a,b): s=s[(s.index>=a)&(s.index<=b)]; return (s/s.cummax()-1).min()*100

# tilt rules
STATE_W = {1:0.50, 2:0.00, 3:0.65, 4:0.65, 5:0.65}
def w_static(i): return 0.50
def w_state(i):  return STATE_W.get(st[i], 0.5)
def make_edge(thr, weak_w):
    def f(i):
        base = STATE_W.get(st[i], 0.5)
        if st[i] in (3,4,5):   # only gate the good-state LAG tilt by edge-health
            return 0.65 if mean12.iloc[i] >= thr else weak_w
        return base            # BEAR=0, CRISIS=0.50 unchanged
    return f

rules = {
 "A0 static 50/50 (V2.3C)":      w_static,
 "A1 state-tilt (V2.3A)":        w_state,
 "A2 edge-cond thr4 weak->.50":  make_edge(4.0, 0.50),
 "A3 edge-cond thr4 weak->.40":  make_edge(4.0, 0.40),
 "A4 edge-cond thr2 weak->.50":  make_edge(2.0, 0.50),
}
print(f"\n{'rule':<30}{'FULL CAGR':>10}{'Sh':>6}{'DD':>7}{'Cal':>6}{'DD21-23':>9}{'2025+CAGR':>10}{'reb':>5}")
print("-"*86)
for name, wf in rules.items():
    s, nreb = run_alloc(wf); m = met(s); dd2223 = dd_win(s,"2021-06-01","2023-06-30")
    m25 = met(s,"2025-01-01")
    print(f"{name:<30}{m[0]:>9.2f}%{m[1]:>6.2f}{m[2]:>6.1f}%{m[3]:>6.2f}{dd2223:>8.1f}%{m25[0]:>9.2f}%{nreb:>5}")
print("\nNote: A0/A1 reproduce V2.3C/V2.3A+postbull. A2-A4 only tilt LAG to .65 when mean12>=thr (edge healthy),")
print("else hold .50/.40 in good states. Goal: cut the 2021-23 DD (allocator over-weighted weak-edge LAG in 2023).")
