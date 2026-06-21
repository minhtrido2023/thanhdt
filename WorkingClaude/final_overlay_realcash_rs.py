#!/usr/bin/env python3
"""
final_overlay_realcash.py — capitulation overlay using the ENGINE'S REAL daily cash
===============================================================================
No proxy. f = the V4/V5 sleeve's actual idle-cash fraction at the washout date,
logged by run_5systems_prodspec.py (STATE_OVERRIDE=dt5g) into
data/5sys_prodspec_201401_202605_dt5g_rs_cashfrac.csv:
   cash_pct    = raw cash (deposit, earns ~0) = genuinely FREE to redeploy
   reserve_pct = cash + cash_etf (ETF parking is index-exposed; redeploying it
                 SWAPS index for the basket, not free)
Overlay (addition model): new_ret = core_ret + f*basket_ret over a 60d hold.
Variants: CRISIS-only and EXTENDED-GRIND-HALF, each with f=cash_pct and f=reserve_pct.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"; H=60; COST=0.003
core=pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g_rs.csv"),parse_dates=["time"]).set_index("time")
cf=pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g_rs_cashfrac.csv"),parse_dates=["time"]).set_index("time")
B=pd.read_csv(os.path.join(W,"data","_washout_baskets.csv"),parse_dates=["time"])
D=pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"),parse_dates=["time"]).sort_values("time").reset_index(drop=True)
state_by=D.set_index("time")["state"]
ws=D[D["pct_oversold"]>=0.40].copy().sort_values("time"); ws["g"]=ws["time"].diff().dt.days.fillna(999); ws["c"]=(ws["g"]>=30).cumsum()
ev=sorted([(g.iloc[0]["time"],int(state_by.get(g.iloc[0]["time"],3))) for _,g in ws.groupby("c")])
def tdpos(t): return D.index[D["time"]==t][0]
events=[dict(date=d,state=st,grind=(i>0 and tdpos(d)-tdpos(ev[i-1][0])<=90)) for i,(d,st) in enumerate(ev)]
idx=core.index
def fval(col_pref,d,which):
    """real cash fraction for V4/V5 at the washout date (avg of signal day +- 2d for stability)."""
    pos=cf.index.searchsorted(pd.Timestamp(d)); lo=max(0,pos-2)
    seg=cf[f"{col_pref}_{which}"].iloc[lo:pos+1]
    return float(seg.mean()) if len(seg) else 0.0
def overlay(navcol,cpref,which,scope):
    ret=core[navcol].pct_change().fillna(0).values.copy()
    used=[]
    for e in events:
        if scope=="crisis" and e["state"]!=1: continue
        f=fval(cpref,e["date"],which)
        if scope=="grindhalf" and e["grind"]: f*=0.5
        if f<=0: continue
        bk=B[B["event"]==str(e["date"].date())].set_index("time")["nav"]
        if len(bk)<5: continue
        i0=idx.searchsorted(e["date"]); bret=bk.pct_change().fillna(0).values
        n=min(H,len(bret)-1,len(idx)-1-i0)
        ret[i0+1:i0+1+n]+=f*bret[1:1+n]; ret[i0+1]-=COST*f; ret[i0+n]-=COST*f
        used.append((str(e["date"].date()),round(f,2)))
    return pd.Series(np.cumprod(1+ret),index=idx),used
def metrics(nav):
    nav=nav.dropna(); r=nav.pct_change().dropna(); yrs=(nav.index[-1]-nav.index[0]).days/365.25
    return (nav.iloc[-1]**(1/yrs)-1)*100,(nav/nav.cummax()-1).min()*100,r.mean()/r.std()*np.sqrt(252)

print("REAL per-event idle-cash fraction at each washout (V4):")
print(f"  {'date':<12}{'state':>6}{'grind':>7}{'cash_pct':>10}{'reserve_pct':>13}")
for e in events:
    print(f"  {str(e['date'].date()):<12}{e['state']:>6}{str(e['grind']):>7}"
          f"{fval('V4',e['date'],'cash_pct'):>10.2f}{fval('V4',e['date'],'reserve_pct'):>13.2f}")
print("\n"+"="*86)
print("FINAL overlay using ENGINE REAL cash (no proxy)")
print("="*86)
for sysname,navcol,cpref in [("V4","V4_V121_ENS_TQ34b","V4"),("V5","V5_V4_KellyQ2","V5")]:
    cb,db,sb=metrics(core[navcol])
    print(f"{sysname} baseline                         : CAGR {cb:5.2f}%  MaxDD {db:6.1f}%  Sharpe {sb:.2f}")
    for tag,which,scope in [("CRISIS-only  f=cash","cash_pct","crisis"),
                            ("CRISIS-only  f=reserve","reserve_pct","crisis"),
                            ("EXTENDED-GRINDHALF f=cash","cash_pct","grindhalf"),
                            ("EXTENDED-GRINDHALF f=reserve","reserve_pct","grindhalf")]:
        nav,_=overlay(navcol,cpref,which,scope); cn,dn,sn=metrics(nav)
        print(f"{sysname} +ovl {tag:<31}: CAGR {cn:5.2f}%  MaxDD {dn:6.1f}%  Sharpe {sn:.2f}   ({cn-cb:+.2f}pp)")
    print()
