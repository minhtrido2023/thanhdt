# -*- coding: utf-8 -*-
"""
custom30v_select_audit.py — does the FULL 8L valuation-v3 axis beat the simple yieldcombo
(1/PE+1/PCF) as the custom30V PARKING-basket selector? Head-to-head, SAME gate/weight/rebal —
only the RANKER differs. Ablation: yieldcombo -> +1/PS (ps3) -> full v3 (route-neutral sector-
weighted coverage-aware + golden floor). Faithful: reuses custom_basket.build_pit PIT machinery
(gate_rating=3, namecap10, q2m5) so every variant shares the identical universe & weighting.
Basket index = the chained namecap-weighted return (the parking sleeve's own NAV).
"""
import os, sys, numpy as np, pandas as pd
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb
START, END = "2014-01-01", "2026-06-15"

def metrics(lvl):
    s = pd.Series(lvl).sort_index(); s.index = pd.to_datetime(s.index)
    r = s.pct_change().dropna()
    yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1
    spd = len(r)/yrs                                    # sessions/yr (calendar-faithful)
    sharpe = r.mean()/r.std()*np.sqrt(spd) if r.std()>0 else 0
    dd = (s/s.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=sharpe, MaxDD=dd*100, Calmar=(cagr*100)/abs(dd*100) if dd<0 else 0)

def by_year(lvl):
    s = pd.Series(lvl).sort_index(); s.index = pd.to_datetime(s.index)
    out = {}
    for y, g in s.groupby(s.index.year):
        if len(g) > 1: out[y] = (g.iloc[-1]/g.iloc[0]-1)*100
    return out

RES = {}; MEM = {}
for mode in ["yieldcombo", "ps3", "v3comp"]:
    os.environ["BASKET_SELECT"] = mode
    print(f"\n===== build basket: BASKET_SELECT={mode} =====")
    lvl, adv, memdf, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                       gate_rating=3, weight_scheme="namecap")
    RES[mode] = lvl; MEM[mode] = memdf

print("\n############ RESULT — custom30V parking basket, selection ablation ############")
print(f"{'selector':<12}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}")
for m in ["yieldcombo","ps3","v3comp"]:
    x = metrics(RES[m]); print(f"{m:<12}{x['CAGR']:>8.2f}{x['Sharpe']:>8.2f}{x['MaxDD']:>9.1f}{x['Calmar']:>8.2f}")

print("\n--- delta vs yieldcombo (baseline = the current 06-30 go-live) ---")
base = metrics(RES["yieldcombo"])
for m in ["ps3","v3comp"]:
    x = metrics(RES[m])
    print(f"  {m:<10} ΔCAGR {x['CAGR']-base['CAGR']:+.2f}pp  ΔSharpe {x['Sharpe']-base['Sharpe']:+.2f}  ΔMaxDD {x['MaxDD']-base['MaxDD']:+.1f}pp")

print("\n--- by-year basket return (%) — overfit/robustness check ---")
yb = {m: by_year(RES[m]) for m in RES}
yrs = sorted(set().union(*[set(v) for v in yb.values()]))
print(f"  {'year':<6}{'yield':>8}{'ps3':>8}{'v3':>8}{'v3-yc':>8}")
for y in yrs:
    a,b,c = yb['yieldcombo'].get(y,float('nan')), yb['ps3'].get(y,float('nan')), yb['v3comp'].get(y,float('nan'))
    print(f"  {y:<6}{a:>8.1f}{b:>8.1f}{c:>8.1f}{(c-a):>+8.1f}")

print("\n--- membership overlap vs yieldcombo (avg names shared per rebal, of top-30) ---")
def overlap(ma, mb):
    A = ma.groupby("rebal_date").ticker.apply(set); B = mb.groupby("rebal_date").ticker.apply(set)
    ov = [len(A[d] & B[d]) for d in A.index if d in B.index]
    return np.mean(ov)
for m in ["ps3","v3comp"]:
    print(f"  {m}: {overlap(MEM['yieldcombo'], MEM[m]):.1f}/30 shared")
print("\n[done]")
