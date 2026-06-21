# -*- coding: utf-8 -*-
"""
singlebook_gating_sweep.py — (A) optimize the DT5G state-gating for the custom30 single-book.
Question: should BEAR/CRISIS exit (0%)? when re-enter? Sweep state-weight vectors + a re-entry
confirmation lag. Faithful costs (transition-TC + borrow + rebal-TC). IS 2014-19 / OOS 2020-now.
Re-entry = DT5G state upgrade (implicit); RE_LAG tests waiting N sessions after an upgrade before adding.
"""
import os, sys, numpy as np, pandas as pd
WORKDIR=os.environ.get("WORKDIR_8L","/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb
TC=0.003; REBAL_TURN=0.35; BORROW=0.10/252.0
st=bq("SELECT s.time,s.state FROM tav2_bq.vnindex_5state_dt5g_live s"); st["time"]=pd.to_datetime(st["time"])
SD=dict(zip(st["time"],st["state"]))

def basket_ret(sel):
    os.environ["BASKET_SELECT"]=sel
    lvl,_,memdf,_=cb.build_pit(bq,"2014-01-01","2026-06-19",quality="none",rebal="q2m5",gate_rating=3,weight_scheme="namecap")
    s=pd.Series(lvl).sort_index(); s.index=pd.to_datetime(s.index)
    return s.pct_change().dropna(), set(pd.to_datetime(memdf["rebal_date"].unique()))

def metrics(r):
    s=(1+r).cumprod(); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; spd=len(r)/yrs
    sh=r.mean()/r.std()*np.sqrt(spd) if r.std()>0 else 0; dd=(s/s.cummax()-1).min()
    return cagr*100, sh, dd*100, (cagr*100)/abs(dd*100) if dd<0 else 0

def run(rb, rebd, W, re_lag=0):
    idx=rb.index
    raw_state=pd.Series([SD.get(d,np.nan) for d in idx],index=idx).ffill().bfill()
    w=pd.Series([W.get(int(s),0.7) for s in raw_state],index=idx)
    if re_lag>0:   # delay INCREASES in exposure by re_lag sessions (slow re-entry); cuts immediately
        wv=w.values.copy()
        for i in range(1,len(wv)):
            if wv[i]>wv[i-1]:  # upgrade -> hold prior until re_lag sessions of sustained upgrade
                lo=max(0,i-re_lag);
                if not all(w.values[j]>=wv[i] for j in range(lo,i+1)): wv[i]=wv[i-1]
        w=pd.Series(wv,index=idx)
    wl=w.shift(1).fillna(0.7)
    r=wl*rb - np.maximum(0.0,wl-1.0)*BORROW - wl.diff().abs().fillna(0.0)*TC
    r=r - pd.Series([REBAL_TURN*TC*wl[d] if d in rebd else 0.0 for d in idx],index=idx)
    return r

def wins(r):
    out={}
    for tag,a,b in [("FULL",None,None),("IS",None,pd.Timestamp("2019-12-31")),("OOS",pd.Timestamp("2020-01-01"),None)]:
        rr=r.copy()
        if a is not None: rr=rr[rr.index>=a]
        if b is not None: rr=rr[rr.index<=b]
        out[tag]=metrics(rr)
    return out

GATINGS={
 "base C0/B.2/N.7/Bull1/Ex1.3": {1:0.0,2:0.2,3:0.7,4:1.0,5:1.3},
 "BEAR exit  C0/B0":            {1:0.0,2:0.0,3:0.7,4:1.0,5:1.3},
 "BEAR .4    C0/B.4":           {1:0.0,2:0.4,3:0.7,4:1.0,5:1.3},
 "no EXBULL lev (Ex1.0)":       {1:0.0,2:0.2,3:0.7,4:1.0,5:1.0},
 "heavier NEU (N.85)":          {1:0.0,2:0.2,3:0.85,4:1.0,5:1.3},
 "lighter NEU (N.55)":          {1:0.0,2:0.2,3:0.55,4:1.0,5:1.3},
 "CRISIS .2 (not full exit)":   {1:0.2,2:0.2,3:0.7,4:1.0,5:1.3},
}
for sel in ["yieldcombo"]:
    rb,rebd=basket_ret(sel)
    print(f"\n################ SELECTOR={sel} — gating sweep ################")
    print(f"  {'gating':<30}{'win':<5}{'CAGR':>7}{'Sh':>6}{'DD':>7}{'Cal':>6}")
    for name,W in GATINGS.items():
        o=wins(run(rb,rebd,W))
        for t in ["FULL","IS","OOS"]:
            c,sh,dd,cal=o[t]; print(f"  {name if t=='FULL' else '':<30}{t:<5}{c:>7.2f}{sh:>6.2f}{dd:>7.1f}{cal:>6.2f}")
    print("\n  --- re-entry lag (base gating, wait N sessions before re-risking) ---")
    for lag in [0,3,5,10]:
        o=wins(run(rb,rebd,GATINGS["base C0/B.2/N.7/Bull1/Ex1.3"],re_lag=lag))
        c,sh,dd,cal=o["OOS"]; cF,_,ddF,calF=o["FULL"]
        print(f"  re_lag={lag:<3} FULL CAGR{cF:6.2f}/DD{ddF:6.1f}/Cal{calF:.2f}  | OOS CAGR{c:6.2f}/DD{dd:6.1f}/Cal{cal:.2f}")
print("[done]")
