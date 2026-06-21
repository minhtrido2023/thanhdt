#!/usr/bin/env python3
"""
final_overlay_overlap_corrected.py — OVERLAP-CORRECTED capitulation overlay
===============================================================================
Removes the last inflation in the cash-only overlay: the static model held the
washout-date idle fraction c0 CONSTANT for the full 60d, but the engine RE-RISKS
its own cash inside the window (verified: 2014-05-08 CRISIS entry 1.00 -> 60d
mean 0.47; 2022-06-20 entry 1.00 -> mean 0.68). Holding c0 flat double-claims the
cash the engine already redeployed.

FIX: the overlay sweeps ONLY the engine's *actual* idle cash each day. It reads
the daily logged fraction cash_pct[t] (run_5systems_prodspec, dt5g+rscap) over the
60d hold and uses it as the day-t overlay weight. When the engine re-risks,
cash_pct[t] falls and the overlay position falls with it -> never competes for the
same dong.

Models:
  STATIC   : old cash-only (c0 flat 60d)                 -> upper bound, overlaps
  CAPPED   : f_t = min(c0, cash_pct[t])  (deploy the washout cash, give it back as
             the engine reclaims it; never exceed the original deploy) -> PRIMARY
  RAW      : f_t = cash_pct[t]            (sweep whatever is idle each day, may
             exceed c0 if the engine raises cash later) -> alt
Cost: charged on the daily traded delta |Δf_t| (entry ramp, intra-window rebal as
the engine reclaims/frees cash, and the exit ramp), COST per side.
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

def overlay(navcol,cpref,scope,model):
    ret=core[navcol].pct_change().fillna(0).values.copy()
    cashser=cf[f"{cpref}_cash_pct"].reindex(idx).ffill().fillna(0).clip(lower=0).values
    rows=[]
    for e in events:
        if scope=="crisis" and e["state"]!=1: continue
        scale=0.5 if (scope=="grindhalf" and e["grind"]) else 1.0
        bk=B[B["event"]==str(e["date"].date())].set_index("time")["nav"]
        if len(bk)<5: continue
        i0=idx.searchsorted(e["date"]); bret=bk.pct_change().fillna(0).values
        n=min(H,len(bret)-1,len(idx)-1-i0)
        if n<=0: continue
        b=bret[1:1+n]
        fday=cashser[i0+1:i0+1+n]*scale
        c0=fday[0] if len(fday) else 0.0
        if model=="static": fday=np.full(n,c0)
        elif model=="capped": fday=np.minimum(fday,c0)
        # raw: leave as engine's daily cash
        if fday.max()<=0: continue
        ret[i0+1:i0+1+n]+=fday*b
        trades=np.abs(np.diff(np.concatenate([[0.0],fday,[0.0]])))  # len n+1
        for k in range(n): ret[i0+1+k]-=COST*trades[k]
        ret[i0+n]-=COST*trades[n]
        rows.append((str(e["date"].date()),e["state"],round(c0,2),round(float(fday.mean()),2)))
    return pd.Series(np.cumprod(1+ret),index=idx),rows

def metrics(nav):
    nav=nav.dropna(); r=nav.pct_change().dropna(); yrs=(nav.index[-1]-nav.index[0]).days/365.25
    return (nav.iloc[-1]**(1/yrs)-1)*100,(nav/nav.cummax()-1).min()*100,r.mean()/r.std()*np.sqrt(252)

# show how much the engine re-risks inside each window (V5, GRINDHALF scope)
print("Engine re-risk inside 60d hold (V5, entry c0 vs realized daily mean):")
_,rows=overlay("V5_V4_KellyQ2","V5","grindhalf","capped")
print(f"  {'date':<12}{'state':>6}{'c0_entry':>10}{'mean_60d':>10}")
for d,st,c0,mn in rows: print(f"  {d:<12}{st:>6}{c0:>10.2f}{mn:>10.2f}")

print("\n"+"="*94)
print("OVERLAP-CORRECTED overlay  (CAGR / MaxDD / Sharpe ; Δ vs baseline)")
print("="*94)
for sysname,navcol,cpref in [("V4","V4_V121_ENS_TQ34b","V4"),("V5","V5_V4_KellyQ2","V5")]:
    cb,db,sb=metrics(core[navcol])
    print(f"{sysname} baseline                                  : {cb:6.2f}% / {db:6.1f}% / {sb:.2f}")
    for tag,scope,model in [("CRISIS-only  STATIC (old, overlaps)","crisis","static"),
                            ("CRISIS-only  CAPPED (overlap-fixed)","crisis","capped"),
                            ("CRISIS-only  RAW    (overlap-fixed)","crisis","raw"),
                            ("GRINDHALF    STATIC (old, overlaps)","grindhalf","static"),
                            ("GRINDHALF    CAPPED (overlap-fixed)","grindhalf","capped"),
                            ("GRINDHALF    RAW    (overlap-fixed)","grindhalf","raw")]:
        nav,_=overlay(navcol,cpref,scope,model); cn,dn,sn=metrics(nav)
        mark="   <-- recommend" if (model=="capped") else ("   <-- old" if model=="static" else "")
        print(f"{sysname} +ovl {tag:<37}: {cn:6.2f}% / {dn:6.1f}% / {sn:.2f}   ({cn-cb:+.2f}pp){mark}")
    print()
