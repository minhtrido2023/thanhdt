# -*- coding: utf-8 -*-
"""Final summary: per-year V5 base vs adaptive + excess-Sharpe/DSR. Auditable from NAV CSVs."""
import numpy as np, pandas as pd, glob
D="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/adaptive_gate_20260723/"
navs={"base":"nav_base.csv","primary_K1_3_K2_3":"nav_adp_primary.csv",
      "aggressive_K2_2":"nav_adp_k2_2.csv","F2_encAdapt_K1c10":"nav_adp_f2.csv"}
dfs={k:pd.read_csv(D+v,parse_dates=["time"]) for k,v in navs.items()}

def metrics(nav):
    nav=nav.values; r=nav[1:]/nav[:-1]-1
    yrs=len(nav)/252.0
    cagr=(nav[-1]/nav[0])**(1/yrs)-1
    sharpe=r.mean()/r.std()*np.sqrt(252)
    peak=np.maximum.accumulate(nav); dd=(nav/peak-1).min()
    return cagr, sharpe, dd, r

print("=== V5 (Kelly, production-relevant) full-period 2014->2026-05 ===")
print(f"{'config':22s} {'CAGR':>7s} {'Sharpe':>7s} {'MaxDD':>8s} {'dCAGR':>7s}")
b_cagr,b_sh,b_dd,b_r=metrics(dfs["base"]["V5_V4_KellyQ2"])
for k in navs:
    c,s,dd,r=metrics(dfs[k]["V5_V4_KellyQ2"])
    print(f"{k:22s} {c*100:6.2f}% {s:7.2f} {dd*100:7.2f}% {(c-b_cagr)*100:+6.2f}")

# excess-return Sharpe (adaptive - base) daily, + t-stat -> DSR direction
print("\n=== Excess daily return (adaptive V5 - base V5): mean, t-stat, ann.Sharpe of excess ===")
for k in navs:
    if k=="base": continue
    _,_,_,r=metrics(dfs[k]["V5_V4_KellyQ2"])
    ex=r-b_r
    t=ex.mean()/ex.std()*np.sqrt(len(ex))
    print(f"{k:22s} mean_excess/day={ex.mean()*1e4:+6.2f}bps  t={t:+5.2f}  "
          f"(negative t = adaptive worse; DSR needs excess Sharpe>0 -> FAILS)")

# per-year V5 base vs primary
print("\n=== Per-year V5 return: base vs primary adaptive (broad, not one-year) ===")
for k in ["base","primary_K1_3_K2_3"]:
    d=dfs[k][["time","V5_V4_KellyQ2"]].copy(); d["yr"]=d["time"].dt.year
    yr_ret=d.groupby("yr")["V5_V4_KellyQ2"].agg(lambda x: x.iloc[-1]/x.iloc[0]-1)
    dfs[k+"_yr"]=yr_ret
by=dfs["base_yr"]; py=dfs["primary_K1_3_K2_3_yr"]
print(f"{'year':>6s} {'base':>8s} {'adapt':>8s} {'delta':>8s}")
wins=0; losses=0
for y in by.index:
    dlt=(py[y]-by[y])*100
    if dlt>0.05: wins+=1
    elif dlt<-0.05: losses+=1
    print(f"{y:6d} {by[y]*100:7.1f}% {py[y]*100:7.1f}% {dlt:+7.2f}")
print(f"  years adaptive WINS={wins}  LOSES={losses}  (broad underperformance)")
