#!/usr/bin/env python3
"""test_regime_off_in_capitulation.py — does TURNING OFF regime_size during capitulation windows help?

regime_size (defensive: halve weak names in BEAR/CRISIS) and the capitulation overlay (offensive: redeploy
idle cash into the washout basket) both fire in stress and partially CANCEL. This tests a hybrid policy:
  regime_size ON normally, but SUPPRESSED during each capitulation event's 60d hold window
  (so it stops fighting the overlay there), then apply the capitulation+grind overlay on top.

Mechanism (no re-backtest needed): splice daily returns from the two existing cores —
  r_base[t] = r_NORS[t]  if t in any active capitulation window  else  r_RS[t]
then add the overlay (f*basket_ret), f from the NO-regime_size cashfrac (regime_size is off at the event).

Compares 3 policies for V4/V5: RS-always / RS-off-in-capitulation(HYBRID) / RS-never.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"; H=60; COST=0.003
core_rs   = pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g_rs.csv"),parse_dates=["time"]).set_index("time")
core_nors = pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g.csv"),parse_dates=["time"]).set_index("time")
cf_nors   = pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g_cashfrac.csv"),parse_dates=["time"]).set_index("time")
B = pd.read_csv(os.path.join(W,"data","_washout_baskets.csv"),parse_dates=["time"])
D = pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"),parse_dates=["time"]).sort_values("time").reset_index(drop=True)
state_by = D.set_index("time")["state"]
ws = D[D["pct_oversold"]>=0.40].copy().sort_values("time"); ws["g"]=ws["time"].diff().dt.days.fillna(999); ws["c"]=(ws["g"]>=30).cumsum()
ev = sorted([(g.iloc[0]["time"],int(state_by.get(g.iloc[0]["time"],3))) for _,g in ws.groupby("c")])
def tdpos(t): return D.index[D["time"]==t][0]
events=[dict(date=d,state=st,grind=(i>0 and tdpos(d)-tdpos(ev[i-1][0])<=90)) for i,(d,st) in enumerate(ev)]
idx = core_rs.index

def fval(d):
    pos=cf_nors.index.searchsorted(pd.Timestamp(d)); lo=max(0,pos-2)
    seg=cf_nors["V_PLACEHOLDER"].iloc[lo:pos+1] if False else None
    return None  # replaced per-system below
def fval_sys(cpref,d,which):
    pos=cf_nors.index.searchsorted(pd.Timestamp(d)); lo=max(0,pos-2)
    seg=cf_nors[f"{cpref}_{which}"].iloc[lo:pos+1]
    return float(seg.mean()) if len(seg) else 0.0

def active_events(scope):
    return [e for e in events if (scope!="crisis" or e["state"]==1)]

def base_returns(navcol, scope, policy):
    """policy: 'rs_always' | 'hybrid' (rs off in capitulation windows) | 'rs_never'."""
    r_rs   = core_rs[navcol].pct_change().fillna(0).values.copy()
    r_nors = core_nors[navcol].pct_change().fillna(0).values.copy()
    if policy=="rs_always": return r_rs
    if policy=="rs_never":  return r_nors
    # hybrid: use no-rs returns inside each active capitulation window, rs returns elsewhere
    r = r_rs.copy()
    for e in active_events(scope):
        i0=idx.searchsorted(e["date"]); n=min(H,len(idx)-1-i0)
        r[i0:i0+n+1] = r_nors[i0:i0+n+1]
    return r

def overlay(navcol, cpref, which, scope, policy):
    ret = base_returns(navcol, scope, policy)
    for e in active_events(scope):
        f=fval_sys(cpref,e["date"],which)
        if scope=="grindhalf" and e["grind"]: f*=0.5
        if f<=0: continue
        bk=B[B["event"]==str(e["date"].date())].set_index("time")["nav"]
        if len(bk)<5: continue
        i0=idx.searchsorted(e["date"]); bret=bk.pct_change().fillna(0).values
        n=min(H,len(bret)-1,len(idx)-1-i0)
        ret[i0+1:i0+1+n]+=f*bret[1:1+n]; ret[i0+1]-=COST*f; ret[i0+n]-=COST*f
    return pd.Series(np.cumprod(1+ret),index=idx)

def metrics(nav):
    nav=nav.dropna(); r=nav.pct_change().dropna(); yrs=(nav.index[-1]-nav.index[0]).days/365.25
    return (nav.iloc[-1]**(1/yrs)-1)*100,(nav/nav.cummax()-1).min()*100,r.mean()/r.std()*np.sqrt(252)

print("="*98)
print("  regime_size policy x capitulation+grind overlay (f=cash, 2014->2026)")
print("  HYBRID = regime_size ON normally, OFF during each capitulation 60d window")
print("="*98)
for sysname,navcol,cpref in [("V4","V4_V121_ENS_TQ34b","V4"),("V5","V5_V4_KellyQ2","V5")]:
    print(f"\n{sysname}:")
    # baselines (no overlay) per policy — show the standalone effect first
    for policy,lab in [("rs_never","RS never (orig)"),("rs_always","RS always"),("hybrid","RS off-in-capit (HYBRID)")]:
        nav=pd.Series(np.cumprod(1+base_returns(navcol,"grindhalf",policy)),index=idx)
        c,d,s=metrics(nav); print(f"  baseline   {lab:<26}: CAGR {c:5.2f}%  MaxDD {d:6.1f}%  Sharpe {s:.2f}")
    print("  " + "-"*70)
    # + capitulation+grind overlay per policy
    base_c=None
    for policy,lab in [("rs_never","RS never (orig)"),("rs_always","RS always"),("hybrid","RS off-in-capit (HYBRID)")]:
        nav=overlay(navcol,cpref,"cash_pct","grindhalf",policy); c,d,s=metrics(nav)
        if base_c is None: base_c=c
        print(f"  +cap+grind {lab:<26}: CAGR {c:5.2f}%  MaxDD {d:6.1f}%  Sharpe {s:.2f}   (vs RSnever {c-base_c:+.2f}pp)")
print("\nDONE.")
