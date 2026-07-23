#!/usr/bin/env python3
"""
stage6_cont_univariate.py — Q2 univariate (job Taylor_20260723_135623)
LAG post_ret as a CONTINUOUS function of each market feature.
 - Spearman IC(feature, post_ret) full + IS/OOS
 - quintile-binned mean post_ret (level) per feature -> which feature best
   explains the LEVEL decline (edge compression)
 - separate the two things: does the feature predict LEVEL (avg drift) or
   RANKING (surprise IC within bucket)?
Run with $DNA_PYEXE.
"""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
from scipy import stats

E = pd.read_pickle("research/lag_regime_gate/lag_events_cont.pkl")
E["pr"] = E["post_ret"]
FEATS = ["dd3m","dd6m","dd12m","roc5","roc10","roc20","liq_ratio","breadth",
         "vni_vs_ma200","vni_rsi"]
IS = E["year"]<=2019; OOS = E["year"]>=2020

print("="*84)
print("Q2a — Spearman IC( feature , LAG post_ret )  [does feature predict drift LEVEL?]")
print("      full / IS(<=2019) / OOS(>=2020); sign: which direction of feature = higher drift")
print("="*84)
rows=[]
for f in FEATS:
    d=E[[f,"pr"]].dropna()
    ic,p = stats.spearmanr(d[f], d["pr"])
    di=E[IS][[f,"pr"]].dropna(); ici,_=stats.spearmanr(di[f],di["pr"])
    do=E[OOS][[f,"pr"]].dropna(); ico,_=stats.spearmanr(do[f],do["pr"])
    rows.append(dict(feature=f, IC_full=ic, p=p, IC_IS=ici, IC_OOS=ico, N=len(d)))
df=pd.DataFrame(rows)
print(df.to_string(index=False, float_format=lambda x:f"{x:.3f}"))

print("\n"+"="*84)
print("Q2b — QUINTILE mean post_ret per feature (the LEVEL curve)")
print("      Q1=lowest feature value ... Q5=highest. Shows monotone edge vs feature.")
print("="*84)
for f in FEATS:
    d=E[[f,"pr"]].dropna().copy()
    d["q"]=pd.qcut(d[f],5,labels=[1,2,3,4,5],duplicates="drop")
    g=d.groupby("q")["pr"].agg(["mean","count"])
    line=" | ".join(f"Q{int(q)} {g.loc[q,'mean']:+5.2f}({int(g.loc[q,'count'])})" for q in g.index)
    print(f"{f:13s}: {line}")

print("\n"+"="*84)
print("Q2c — MULTIVARIATE: OLS post_ret ~ features (which survive jointly, std-beta)")
print("="*84)
d=E[FEATS+["pr"]].dropna().copy()
X=(d[FEATS]-d[FEATS].mean())/d[FEATS].std()
X=np.column_stack([np.ones(len(X)), X.values])
y=d["pr"].values
beta,_,_,_=np.linalg.lstsq(X,y,rcond=None)
resid=y-X@beta; se=np.sqrt(np.sum(resid**2)/(len(y)-X.shape[1]) * np.diag(np.linalg.inv(X.T@X)))
tvals=beta/se
names=["const"]+FEATS
for nm,b,t in zip(names,beta,tvals):
    print(f"  {nm:13s} std-beta {b:+6.3f}  t {t:+5.2f}")

print("\n"+"="*84)
print("Q2d — does feature predict RANKING (surprise-IC within bucket) or only LEVEL?")
print("      Spearman(surprise, post_ret) in low-third vs high-third of each feature")
print("="*84)
for f in ["dd6m","roc20","liq_ratio","breadth","vni_rsi"]:
    d=E[[f,"surprise","pr"]].dropna()
    lo=d[d[f]<=d[f].quantile(0.33)]; hi=d[d[f]>=d[f].quantile(0.67)]
    icl,pl=stats.spearmanr(lo["surprise"],lo["pr"])
    ich,ph=stats.spearmanr(hi["surprise"],hi["pr"])
    print(f"{f:12s}: low-third surpriseIC {icl:+.3f}(p{pl:.3f},N{len(lo)}) | "
          f"high-third {ich:+.3f}(p{ph:.3f},N{len(hi)})")
