#!/usr/bin/env python3
"""
committed_sleeve_overlay.py — "carve-out 60d, no cash switching" model (user spec 2026-06-07)
===============================================================================
Philosophy (user): at a washout we DELIBERATELY pick the golden basket, so commit
c0 of NAV to it and HOLD a fixed 60 trading days — do NOT switch cash back and forth
with the engine. During the hold the engine manages the REST of the book to keep its
target ratio (if DT5G drops NEUTRAL->BEAR->CRISIS, the engine cuts the OTHER holdings,
the capitulation sleeve is respected). After 60d the sleeve sells -> engine resumes.

Accounting = SUBSTITUTION, not addition (so NOT the inflated static double-count):
   combined_ret[t] = (1 - w_t)*core_ret[t] + w_t*basket_ret[t]
where w_t = NAV fraction currently locked in active sleeves (each sleeve = c0 at its
washout, held 60d). Identity: combined = core + w*(basket - core) = static - w*core_ret,
i.e. it REMOVES the engine's return on the carved cash that the old static model
double-counted, and replaces it with the basket. Cost = COST*c0 at entry and exit only
(no intra-window rebalancing — that's the point).

Sizing matches the overlap script for apples-to-apples: scope grindhalf -> f=cash_pct
at entry, x0.5 on grind (repeat) washouts; crisis-only -> crisis events only.
Compared head-to-head with: baseline, STATIC (inflated), OVERLAP (engine-priority, +5pp).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"; H=60; COST=0.003
core=pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g_rscap.csv"),parse_dates=["time"]).set_index("time")
cf=pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g_rscap_cashfrac.csv"),parse_dates=["time"]).set_index("time")
B=pd.read_csv(os.path.join(W,"data","_washout_baskets.csv"),parse_dates=["time"])
D=pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"),parse_dates=["time"]).sort_values("time").reset_index(drop=True)
state_by=D.set_index("time")["state"]
ws=D[D["pct_oversold"]>=0.40].copy().sort_values("time"); ws["g"]=ws["time"].diff().dt.days.fillna(999); ws["c"]=(ws["g"]>=30).cumsum()
ev=sorted([(g.iloc[0]["time"],int(state_by.get(g.iloc[0]["time"],3))) for _,g in ws.groupby("c")])
def tdpos(t): return D.index[D["time"]==t][0]
events=[dict(date=d,state=st,grind=(i>0 and tdpos(d)-tdpos(ev[i-1][0])<=90)) for i,(d,st) in enumerate(ev)]
idx=core.index; N=len(idx)

def c0_of(cpref,d,scope,grind):
    pos=cf.index.searchsorted(pd.Timestamp(d)); lo=max(0,pos-2)
    seg=cf[f"{cpref}_cash_pct"].iloc[lo:pos+1]; c=float(seg.mean()) if len(seg) else 0.0
    c=max(0.0,c)
    if scope=="grindhalf" and grind: c*=0.5
    return c

# ---- model A: committed sleeve (user) ----
def committed(navcol,cpref,scope):
    cr=core[navcol].pct_change().fillna(0).values
    w=np.zeros(N); contrib=np.zeros(N); cost=np.zeros(N)
    for e in events:
        if scope=="crisis" and e["state"]!=1: continue
        c=c0_of(cpref,e["date"],scope,e["grind"])
        if c<=0: continue
        bk=B[B["event"]==str(e["date"].date())].set_index("time")["nav"]
        if len(bk)<5: continue
        i0=idx.searchsorted(e["date"]); bret=bk.pct_change().fillna(0).values
        n=min(H,len(bret)-1,N-1-i0)
        if n<=0: continue
        for k in range(n):
            w[i0+1+k]+=c; contrib[i0+1+k]+=c*bret[1+k]
        cost[i0+1]+=COST*c; cost[i0+n]+=COST*c
    wc=np.minimum(w,1.0)
    # if sleeves stack >1, scale basket contribution down proportionally
    scale=np.where(w>1.0,1.0/np.where(w>0,w,1),1.0)
    comb=(1-wc)*cr + contrib*scale - cost
    return pd.Series(np.cumprod(1+comb),index=idx), w.max()

# ---- model B: static (inflated, for reference) ----
def static(navcol,cpref,scope):
    ret=core[navcol].pct_change().fillna(0).values.copy()
    for e in events:
        if scope=="crisis" and e["state"]!=1: continue
        c=c0_of(cpref,e["date"],scope,e["grind"])
        if c<=0: continue
        bk=B[B["event"]==str(e["date"].date())].set_index("time")["nav"]
        if len(bk)<5: continue
        i0=idx.searchsorted(e["date"]); bret=bk.pct_change().fillna(0).values
        n=min(H,len(bret)-1,N-1-i0)
        if n<=0: continue
        ret[i0+1:i0+1+n]+=c*bret[1:1+n]; ret[i0+1]-=COST*c; ret[i0+n]-=COST*c
    return pd.Series(np.cumprod(1+ret),index=idx)

# ---- model C: overlap engine-priority (yesterday's +5pp) ----
def overlap(navcol,cpref,scope):
    ret=core[navcol].pct_change().fillna(0).values.copy()
    cashser=cf[f"{cpref}_cash_pct"].reindex(idx).ffill().fillna(0).clip(lower=0).values
    for e in events:
        if scope=="crisis" and e["state"]!=1: continue
        scale=0.5 if (scope=="grindhalf" and e["grind"]) else 1.0
        bk=B[B["event"]==str(e["date"].date())].set_index("time")["nav"]
        if len(bk)<5: continue
        i0=idx.searchsorted(e["date"]); bret=bk.pct_change().fillna(0).values
        n=min(H,len(bret)-1,N-1-i0)
        if n<=0: continue
        fday=np.minimum(cashser[i0+1:i0+1+n]*scale, cashser[i0+1]*scale)
        if fday.max()<=0: continue
        ret[i0+1:i0+1+n]+=fday*bret[1:1+n]
        trades=np.abs(np.diff(np.concatenate([[0.0],fday,[0.0]])))
        for k in range(n): ret[i0+1+k]-=COST*trades[k]
        ret[i0+n]-=COST*trades[n]
    return pd.Series(np.cumprod(1+ret),index=idx)

def metrics(nav):
    nav=nav.dropna(); r=nav.pct_change().dropna(); yrs=(nav.index[-1]-nav.index[0]).days/365.25
    return (nav.iloc[-1]**(1/yrs)-1)*100,(nav/nav.cummax()-1).min()*100,r.mean()/r.std()*np.sqrt(252)

print("="*96)
print("COMMITTED-SLEEVE (carve 60d, no switching) vs STATIC(inflated) vs OVERLAP(engine-priority)")
print("="*96)
for sysname,navcol,cpref in [("V4","V4_V121_ENS_TQ34b","V4"),("V5","V5_V4_KellyQ2","V5")]:
    cb,db,sb=metrics(core[navcol])
    print(f"\n{sysname} baseline                              : {cb:6.2f}% / {db:6.1f}% / {sb:.2f}")
    for scope in ["crisis","grindhalf"]:
        lab="CRISIS-only" if scope=="crisis" else "GRINDHALF  "
        ns=static(navcol,cpref,scope);            cs,ds,ss=metrics(ns)
        no=overlap(navcol,cpref,scope);           co,do_,so=metrics(no)
        nc,wmax=committed(navcol,cpref,scope);    cc,dc,sc=metrics(nc)
        print(f"  {lab}  STATIC   (đếm trùng, ảo)      : {cs:6.2f}% / {ds:6.1f}% / {ss:.2f}   ({cs-cb:+.2f}pp)")
        print(f"  {lab}  OVERLAP  (engine ưu tiên)     : {co:6.2f}% / {do_:6.1f}% / {so:.2f}   ({co-cb:+.2f}pp)")
        print(f"  {lab}  COMMITTED(carve 60d=user) ✅  : {cc:6.2f}% / {dc:6.1f}% / {sc:.2f}   ({cc-cb:+.2f}pp)   [max sleeve {wmax*100:.0f}% NAV]")
