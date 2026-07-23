#!/usr/bin/env python3
"""
stage4_rating_by_regime.py — Q1 (job Taylor_20260723_135623)
Does RATING discrimination (good <=3 vs bad >=4) depend on regime?
Return GAP between LAG rating<=3 and rating>=4, split by DT5G regime + by
continuous drawdown bucket. Welch t-stat per regime. This is a DIFFERENT axis
than the prior job's IC(surprise, ret)-by-regime.
Event-level; no NAV. Run with $DNA_PYEXE.
"""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
from scipy import stats

E = pd.read_pickle("research/lag_regime_gate/lag_events_attributed.pkl")
E["pr"] = E["post_ret"]           # already in %
E["pass"] = E["rating"] <= 3
DT5G_NAME = {1:"BEAR",2:"low-NEUTRAL(2)",3:"NEUTRAL(3)",4:"BULL",5:"EX-BULL"}

def gap(sub):
    g = sub[sub["pass"]]["pr"].dropna()
    b = sub[~sub["pass"]]["pr"].dropna()
    if len(g)<8 or len(b)<8: return None
    t,p = stats.ttest_ind(g, b, equal_var=False)   # Welch
    return dict(N=len(sub), Ng=len(g), Nb=len(b),
                avg_pass=g.mean(), avg_fail=b.mean(),
                gap=g.mean()-b.mean(), t=t, p=p)

print("="*78)
print("Q1a — RATING GAP (rating<=3 minus rating>=4) BY DT5G REGIME")
print("      gap>0 means rating<=3 outperforms; t = Welch two-sample")
print("="*78)
rows=[]
for st in sorted(E["dt5g_state"].dropna().unique()):
    r = gap(E[E["dt5g_state"]==st])
    if r: r["regime"]=f"DT5G {int(st)} {DT5G_NAME.get(int(st),'')}"; rows.append(r)
# also combined BEAR+low-neutral (1,2) and BULL+ (4,5)
r=gap(E[E["dt5g_state"].isin([1,2])]);  r["regime"]="DT5G<=2 (bear/low-neut)"; rows.append(r)
r=gap(E[E["dt5g_state"].isin([4,5])]);  r["regime"]="DT5G>=4 (bull+)";        rows.append(r)
r=gap(E);                               r["regime"]="ALL";                    rows.append(r)
df=pd.DataFrame(rows)[["regime","N","Ng","Nb","avg_pass","avg_fail","gap","t","p"]]
print(df.to_string(index=False, float_format=lambda x:f"{x:.3f}"))

print("\n"+"="*78)
print("Q1b — RATING GAP BY CONTINUOUS DRAWDOWN BUCKET (vni_dd from 1y peak)")
print("="*78)
buckets = [("dd>=-5 (near-high)", E["vni_dd"]>=-5),
           ("dd -10..-5",  (E["vni_dd"]<-5)&(E["vni_dd"]>=-10)),
           ("dd -20..-10 (mild)", (E["vni_dd"]<-10)&(E["vni_dd"]>=-20)),
           ("dd<=-20 (deep)", E["vni_dd"]<=-20)]
rows=[]
for nm,mask in buckets:
    r=gap(E[mask])
    if r: r["regime"]=nm; rows.append(r)
df=pd.DataFrame(rows)[["regime","N","Ng","Nb","avg_pass","avg_fail","gap","t","p"]]
print(df.to_string(index=False, float_format=lambda x:f"{x:.3f}"))

print("\n"+"="*78)
print("Q1c — same split but rating as 5 buckets (monotonicity check), by DT5G group")
print("="*78)
for lbl,mask in [("DT5G<=2 bear",E["dt5g_state"].isin([1,2])),
                 ("DT5G==3 neut",E["dt5g_state"]==3),
                 ("DT5G>=4 bull",E["dt5g_state"].isin([4,5]))]:
    sub=E[mask]
    means=sub.groupby("rating")["pr"].agg(["mean","count"])
    print(f"\n{lbl} (N={len(sub)}):")
    print(means.to_string(float_format=lambda x:f"{x:.2f}"))
