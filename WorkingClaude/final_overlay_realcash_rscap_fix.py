#!/usr/bin/env python3
"""
final_overlay_realcash_rscap_fix.py — DOUBLE-COUNT-CORRECTED capitulation overlay
===============================================================================
Fixes the inflation in final_overlay_realcash_rscap.py.

Engine logs two idle fractions at each washout (run_5systems_prodspec, dt5g+rscap):
   cash_pct    = raw cash (deposit, earns ~0)        -> GENUINELY FREE to redeploy
   reserve_pct = cash + cash_etf (ETF parking is INDEX-EXPOSED in the core NAV)

The OLD overlay did  new_ret = core_ret + reserve_pct * basket_ret  -> WRONG:
the cash_etf slice already earns the index inside core_ret, so the old model paid
BOTH index (in core) AND basket (in overlay) on the same money = double count.

CORRECT redeploy accounting per event (deploy the WHOLE reserve into the basket):
   free cash slice  c   : was earning ~0  -> +c*basket_ret
   ETF slice       (r-c): was earning idx -> SWAP -> +(r-c)*(basket_ret - idx_ret)
   => delta = r*basket_ret - (r-c)*idx_ret           (idx_ret = VNINDEX daily ret)
Cost: the whole reserve r is traded (in + out) -> COST*r each side.

Variants reported:
  CASH-ONLY    : deploy only the free cash c (leave ETF parked) = most conservative,
                 no swap assumption, identical to old f=cash.
  FULL-SWAP    : deploy whole reserve r with the index-swap correction = the honest
                 version of the old "f=reserve" (which was inflated).
  [OLD-RESERVE]: the inflated f=reserve number, shown only to size the fix.

Caveat still open (EXTENDED scope only): on NEUTRAL/BEAR washouts the engine may
re-risk its own free cash inside the 60d hold -> the addition model can still
slightly overlap. CRISIS-only is clean (cash truly parked through the panic).
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
idx=core.index
vni_ret=core["VNI"].pct_change().fillna(0).values   # index leg for the ETF swap

def fval(cpref,d,which):
    pos=cf.index.searchsorted(pd.Timestamp(d)); lo=max(0,pos-2)
    seg=cf[f"{cpref}_{which}"].iloc[lo:pos+1]
    return float(seg.mean()) if len(seg) else 0.0

def overlay(navcol,cpref,scope,model):
    """model: 'cashonly' | 'fullswap' | 'oldreserve'(inflated)."""
    ret=core[navcol].pct_change().fillna(0).values.copy()
    for e in events:
        if scope=="crisis" and e["state"]!=1: continue
        c=fval(cpref,e["date"],"cash_pct"); r=fval(cpref,e["date"],"reserve_pct")
        if scope=="grindhalf" and e["grind"]: c*=0.5; r*=0.5
        bk=B[B["event"]==str(e["date"].date())].set_index("time")["nav"]
        if len(bk)<5: continue
        i0=idx.searchsorted(e["date"]); bret=bk.pct_change().fillna(0).values
        n=min(H,len(bret)-1,len(idx)-1-i0)
        if n<=0: continue
        b=bret[1:1+n]; v=vni_ret[i0+1:i0+1+n]
        if model=="cashonly":
            if c<=0: continue
            ret[i0+1:i0+1+n]+=c*b;                 tc=c
        elif model=="fullswap":
            if r<=0: continue
            ret[i0+1:i0+1+n]+=r*b-(r-c)*v;        tc=r   # swap-correct: ETF slice nets out its index
        elif model=="oldreserve":
            if r<=0: continue
            ret[i0+1:i0+1+n]+=r*b;                tc=r   # WRONG (kept to size the fix)
        ret[i0+1]-=COST*tc; ret[i0+n]-=COST*tc
    return pd.Series(np.cumprod(1+ret),index=idx)

def metrics(nav):
    nav=nav.dropna(); r=nav.pct_change().dropna(); yrs=(nav.index[-1]-nav.index[0]).days/365.25
    return (nav.iloc[-1]**(1/yrs)-1)*100,(nav/nav.cummax()-1).min()*100,r.mean()/r.std()*np.sqrt(252)

print("Washout events (V4 real idle fractions):")
print(f"  {'date':<12}{'state':>6}{'grind':>7}{'cash':>7}{'reserve':>9}")
for e in events:
    print(f"  {str(e['date'].date()):<12}{e['state']:>6}{str(e['grind']):>7}"
          f"{fval('V4',e['date'],'cash_pct'):>7.2f}{fval('V4',e['date'],'reserve_pct'):>9.2f}")

print("\n"+"="*92)
print("DOUBLE-COUNT-CORRECTED overlay  (CAGR / MaxDD / Sharpe ; Δ vs baseline)")
print("="*92)
for sysname,navcol,cpref in [("V4","V4_V121_ENS_TQ34b","V4"),("V5","V5_V4_KellyQ2","V5")]:
    cb,db,sb=metrics(core[navcol])
    print(f"{sysname} baseline                              : {cb:6.2f}% / {db:6.1f}% / {sb:.2f}")
    rows=[("CRISIS-only  CASH-ONLY (clean)","crisis","cashonly"),
          ("CRISIS-only  FULL-SWAP (corrected)","crisis","fullswap"),
          ("CRISIS-only  [OLD f=reserve, inflated]","crisis","oldreserve"),
          ("GRINDHALF    CASH-ONLY (clean)","grindhalf","cashonly"),
          ("GRINDHALF    FULL-SWAP (corrected)","grindhalf","fullswap"),
          ("GRINDHALF    [OLD f=reserve, inflated]","grindhalf","oldreserve")]
    for tag,scope,model in rows:
        cn,dn,sn=metrics(overlay(navcol,cpref,scope,model))
        mark="   <-- inflated" if model=="oldreserve" else ""
        print(f"{sysname} +ovl {tag:<40}: {cn:6.2f}% / {dn:6.1f}% / {sn:.2f}   ({cn-cb:+.2f}pp){mark}")
    print()
