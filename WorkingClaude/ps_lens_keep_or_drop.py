# -*- coding: utf-8 -*-
"""
ps_lens_keep_or_drop.py — should the 1/PS lens stay in the 8L v3 SCREENER composite, or is it
noise? (Distinct from the concentrated-basket finding.) Tests on the BROAD universe panel:
  1. PS by-year IC per route (robust vs lumpy?)
  2. PS marginal IC orthogonal to (ey, cfy) — does it add NEW info in the screener?
  3. Composite ablation: ey+cfy-only  vs  +ps(all routes)  vs  +ps(consumer-only)
Decide: keep as-is / gate PS to consumer-only / drop PS.
"""
import os, numpy as np, pandas as pd
from scipy.stats import spearmanr
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
df = pd.read_csv(f"{WORKDIR}/data/value_panel_2014.csv", parse_dates=["time"])
df["F_ey"]=np.where(df.PE>0,100/df.PE,np.nan); df["F_cfy"]=np.where(df.PCF>0,100/df.PCF,np.nan)
df["F_ps"]=np.where(df.PS>0,100/df.PS,np.nan); df["mo"]=df.time.dt.to_period("M")
df=df[(df.Close*df.Volume>=5e9) & (df.ROE_Min3Y>=0)].copy()     # liquid + book-OK (the screener set)
FWD="profit_2M"

def xic(d,col):
    a=[]
    for _,g in d.groupby("mo"):
        s=g[[col,FWD]].dropna()
        if len(s)>=8 and s[col].nunique()>3: a.append(spearmanr(s[col],s[FWD]).correlation)
    a=np.array([x for x in a if pd.notna(x)])
    return (a.mean(), a.mean()/(a.std(ddof=1)/np.sqrt(len(a))), (a>0).mean(), len(a)) if len(a)>=6 else (np.nan,)*4

print("### 1) PS by-year IC (robust or lumpy?) ###")
for lbl,d in [("BROAD",df),("CONSUMER",df[df.ICB_Code.apply(lambda c: pd.notna(c) and ((3500<=c<3800)or(5300<=c<5400)))]),
              ("COMPOUNDER",df[df.route=="COMPOUNDER"]),("CYCLICAL",df[df.route=="CYCLICAL"])]:
    yr=[]
    for y,g in d.groupby(d.time.dt.year):
        r=xic(g,"F_ps"); yr.append((y,r[0]))
    pos=sum(1 for _,v in yr if pd.notna(v) and v>0); tot=sum(1 for _,v in yr if pd.notna(v))
    full=xic(d,"F_ps")
    print(f"  {lbl:<11} IC{full[0]:+.3f} t{full[1]:.1f} pos {pos}/{tot}yr | " + " ".join(f"{y}:{v:+.02f}" for y,v in yr if pd.notna(v)))

print("\n### 2) PS marginal IC orthogonal to (ey,cfy) — adds NEW info? ###")
def marg(d, fac, bases):
    res=[]
    for _,g in d.groupby("mo"):
        s=g[[fac,FWD]+bases].dropna()
        if len(s)<12: continue
        X=np.column_stack([s[b].rank() for b in bases]+[np.ones(len(s))])
        rf=s[fac].rank().values
        beta,_,_,_=np.linalg.lstsq(X,rf,rcond=None); resid=rf-X@beta
        if np.std(resid)>0: res.append(spearmanr(resid,s[FWD]).correlation)
    a=np.array([x for x in res if pd.notna(x)])
    return (a.mean(), a.mean()/(a.std(ddof=1)/np.sqrt(len(a)))) if len(a)>=6 else (np.nan,np.nan)
for lbl,d in [("BROAD",df),("CONSUMER",df[df.ICB_Code.apply(lambda c: pd.notna(c) and ((3500<=c<3800)or(5300<=c<5400)))]),
              ("COMPOUNDER",df[df.route=="COMPOUNDER"]),("CYCLICAL",df[df.route=="CYCLICAL"])]:
    m=marg(d,"F_ps",["F_ey","F_cfy"]); print(f"  {lbl:<11} PS ⟂(ey,cfy): resid-IC {m[0]:+.3f} (t{m[1]:.1f})")

print("\n### 3) Composite ablation (BROAD, coverage-aware) ###")
for c in ["F_ey","F_cfy","F_ps"]: df["p_"+c[2:]]=df.groupby(["mo","route"])[c].rank(pct=True)
def comp(d, w_ey,w_cfy,w_ps, ps_consumer_only=False):
    isc = d.ICB_Code.apply(lambda c: pd.notna(c) and ((3500<=c<3800)or(5300<=c<5400))).values
    P=np.vstack([d.p_ey.values,d.p_cfy.values,d.p_ps.values])
    W=np.tile(np.array([w_ey,w_cfy,w_ps])[:,None],(1,len(d))).astype(float)
    if ps_consumer_only: W[2,:]=np.where(isc, w_ps, 0.0)
    pr=~np.isnan(P); num=np.nansum(np.where(pr,P*W,0),0); den=np.nansum(np.where(pr,W,0),0)
    return pd.Series(np.where(den>0,num/den,np.nan), index=d.index)
for lbl,s in [("ey+cfy only      ", comp(df,.6,.4,0)),
              ("+ps ALL routes   ", comp(df,.45,.30,.25)),
              ("+ps CONSUMER-only", comp(df,.45,.30,.25,ps_consumer_only=True))]:
    r=xic(df.assign(_s=s).rename(columns={"_s":"S"}),"S")
    print(f"  {lbl}: IC{r[0]:+.3f} t{r[1]:.1f} hit{100*r[2]:.0f}%")
# consumer-subset: does +ps help the consumer names specifically?
cons=df[df.ICB_Code.apply(lambda c: pd.notna(c) and ((3500<=c<3800)or(5300<=c<5400)))]
for lbl,w in [("ey+cfy only",(.6,.4,0)),("+ps",(.45,.30,.25))]:
    s=comp(cons,*w); r=xic(cons.assign(S=s),"S")
    print(f"  [CONSUMER subset] {lbl:<12}: IC{r[0]:+.3f} t{r[1]:.1f}")
print("[done]")
