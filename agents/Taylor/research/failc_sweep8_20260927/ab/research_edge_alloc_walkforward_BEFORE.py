# -*- coding: utf-8 -*-
"""Walk-forward of the edge-conditional LAG allocator. IS=2014-2019 (pick threshold), OOS=2020+ (test).
Overlay re-test on postbull-gated book NAVs (allocator is a return-stream overlay)."""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
W = r"/home/trido/thanhdt/WorkingClaude"; os.chdir(W)
A = pd.read_csv("data/v23c_golive_audit_2014_now_matpostbull_shrink0.csv", low_memory=False)
d = A[A["record_type"] == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d["ymd"]); d = d.set_index("ymd")
navb = d["nav_bal_ref"].astype(float); navl = d["nav_lag_ref"].astype(float); st = d["state"].astype(float).astype(int).values
common = d.index; rb = navb.pct_change().fillna(0).values; rl = navl.pct_change().fillna(0).values
eh = pd.read_csv("data/lag_edge_health.csv", parse_dates=["entry"]).drop_duplicates("entry").set_index("entry").sort_index()
mean12 = eh["mean12"].reindex(common, method="ffill")

# is LAG edge weak in IS or only OOS?
print("LAG edge-health mean12 (causal trailing-12M LAG trade return):")
for lbl, a, b in [("IS 2014-2019","2014-01-01","2019-12-31"),("OOS 2020+","2020-01-01","2027-01-01")]:
    m = mean12[(mean12.index>=a)&(mean12.index<=b)]
    print(f"  {lbl}: mean {m.mean():.1f}%  median {m.median():.1f}%  %time<4% {(m<4).mean()*100:.0f}%  min {m.min():.1f}%")

TOTAL=50e9; BAND=0.10; TC=0.001; STATE_W={1:0.50,2:0.00,3:0.65,4:0.65,5:0.65}
def run(wf):
    w0=wf(0); cb=(1-w0)*TOTAL; cl=w0*TOTAL; out=np.empty(len(common))
    for i in range(len(common)):
        if i>0: cb*=(1+rb[i]); cl*=(1+rl[i])
        P=cb+cl; wt=wf(i)
        if P>0 and abs(cl/P-wt)>BAND: P-=TC*abs(wt*P-cl); cl=wt*P; cb=(1-wt)*P
        out[i]=cb+cl
    return pd.Series(out,index=common)
def met(s,a,b):
    s=s[(s.index>=a)&(s.index<=b)].dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    r=s.pct_change().dropna(); c=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; dd=(s/s.cummax()-1).min()
    return c*100,r.mean()/r.std()*np.sqrt(252),dd*100,c/abs(dd)
def w_state(i): return STATE_W.get(st[i],0.5)
def edge(thr,weak=0.50):
    def f(i):
        if st[i] in (3,4,5): return 0.65 if mean12.iloc[i]>=thr else weak
        return STATE_W.get(st[i],0.5)
    return f

IS=("2014-01-01","2019-12-31"); OOS=("2020-01-01","2027-01-01")
print("\n--- threshold grid: pick on IS, read OOS (Calmar) ---")
print(f"{'thr':>5}{'IS_CAGR':>9}{'IS_Cal':>8}{'OOS_CAGR':>10}{'OOS_Cal':>9}{'OOS_DD':>8}")
for thr in [0,2,3,4,5,6,8]:
    wf = w_state if thr==0 else edge(thr)
    s=run(wf); mi=met(s,*IS); mo=met(s,*OOS)
    tag=" <- state-tilt(V2.3A)" if thr==0 else ""
    print(f"{thr:>5}{mi[0]:>8.2f}%{mi[3]:>8.2f}{mo[0]:>9.2f}%{mo[3]:>8.2f}{mo[2]:>7.1f}%{tag}")

print("\n--- head-to-head IS vs OOS (state-tilt vs edge-cond thr4) ---")
print(f"{'rule':<24}{'window':>14}{'CAGR':>8}{'Sh':>6}{'DD':>7}{'Cal':>6}")
for name,wf in [("state-tilt (V2.3A)",w_state),("edge-cond thr4",edge(4.0))]:
    s=run(wf)
    for wl,a,b in [("IS 2014-2019",*[IS[0],IS[1]]),("OOS 2020+",*[OOS[0],OOS[1]])]:
        m=met(s,a,b); print(f"{name:<24}{wl:>14}{m[0]:>7.2f}%{m[1]:>6.2f}{m[2]:>6.1f}%{m[3]:>6.2f}")
