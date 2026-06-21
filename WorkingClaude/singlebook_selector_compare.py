# -*- coding: utf-8 -*-
"""
singlebook_selector_compare.py — (C) compare basket SELECTORS for the single-book under the OPTIMAL
gating from (A): {CRISIS0,BEAR.2,NEU.7,BULL1.0,EXBULL1.0} (no EXBULL leverage), immediate re-entry.
Selectors: yieldcombo (custom30V) | v3comp (old 8L v3) | v3latest (THIS-MORNING: cyclical ps->0 +
cfo_normy + golden CF_OA_3Y gate) | ps3 (1/PS-equal). Faithful costs. FULL / IS 2014-19 / OOS 2020-now.
"""
import os, sys, numpy as np, pandas as pd
WORKDIR=os.environ.get("WORKDIR_8L","/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb
TC=0.003; REBAL_TURN=0.35; BORROW=0.10/252.0
W={1:0.0,2:0.2,3:0.7,4:1.0,5:1.0}   # OPTIMAL gating from (A): no EXBULL leverage
st=bq("SELECT s.time,s.state FROM tav2_bq.vnindex_5state_dt5g_live s"); st["time"]=pd.to_datetime(st["time"])
SD=dict(zip(st["time"],st["state"]))
def metrics(r):
    s=(1+r).cumprod(); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; spd=len(r)/yrs
    sh=r.mean()/r.std()*np.sqrt(spd) if r.std()>0 else 0; dd=(s/s.cummax()-1).min()
    return cagr*100, sh, dd*100, (cagr*100)/abs(dd*100) if dd<0 else 0
def faithful(sel):
    os.environ["BASKET_SELECT"]=sel
    lvl,_,memdf,_=cb.build_pit(bq,"2014-01-01","2026-06-19",quality="none",rebal="q2m5",gate_rating=3,weight_scheme="namecap")
    s=pd.Series(lvl).sort_index(); s.index=pd.to_datetime(s.index); rb=s.pct_change().dropna()
    rebd=set(pd.to_datetime(memdf["rebal_date"].unique())); idx=rb.index
    raw=pd.Series([SD.get(d,np.nan) for d in idx],index=idx).ffill().bfill()
    w=pd.Series([W.get(int(x),0.7) for x in raw],index=idx); wl=w.shift(1).fillna(0.7)
    r=wl*rb - np.maximum(0.0,wl-1.0)*BORROW - wl.diff().abs().fillna(0.0)*TC
    r=r - pd.Series([REBAL_TURN*TC*wl[d] if d in rebd else 0.0 for d in idx],index=idx)
    return r
print(f"gating={W} (no EXBULL leverage), faithful costs\n")
print(f"  {'selector':<12}{'win':<5}{'CAGR':>7}{'Sh':>6}{'DD':>7}{'Cal':>6}")
agg={}
for sel in ["yieldcombo","v3comp","v3latest","ps3"]:
    r=faithful(sel); agg[sel]=r
    for tag,a,b in [("FULL",None,None),("IS",None,pd.Timestamp("2019-12-31")),("OOS",pd.Timestamp("2020-01-01"),None)]:
        rr=r.copy()
        if a is not None: rr=rr[rr.index>=a]
        if b is not None: rr=rr[rr.index<=b]
        c,sh,dd,cal=metrics(rr); print(f"  {sel if tag=='FULL' else '':<12}{tag:<5}{c:>7.2f}{sh:>6.2f}{dd:>7.1f}{cal:>6.2f}")
    print()
# by-year v3latest vs yieldcombo (sustainability of this-morning config)
print("by-year v3latest − yieldcombo (sustainability):")
ry=agg["yieldcombo"]; rl=agg["v3latest"]
for y in sorted(set(ry.index.year)):
    a=(1+ry[ry.index.year==y]).prod()-1; b=(1+rl[rl.index.year==y]).prod()-1
    print(f"  {y}: {(b-a)*100:+.1f}", end="")
print()
