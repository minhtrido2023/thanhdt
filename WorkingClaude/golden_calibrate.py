# -*- coding: utf-8 -*-
"""
golden_calibrate.py — how much weight should the golden-cell (pb_z<=-1) dislocation carry in
Composite v3? Directly tests the DGC/VNM question: do BOOK-TRUSTWORTHY golden names with WEAK
cashflow-yield still earn forward return (=> add a FLOOR, don't demote), or underperform (=> the
cfy demotion is right)? Then calibrates the golden bonus / floor by composite IC + decile.
"""
import os, numpy as np, pandas as pd
from scipy.stats import spearmanr
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
df = pd.read_csv(f"{WORKDIR}/data/value_panel_2014.csv", parse_dates=["time"])
df["F_ey"]=np.where(df.PE>0,100/df.PE,np.nan); df["F_cfy"]=np.where(df.PCF>0,100/df.PCF,np.nan)
df["F_ps"]=np.where(df.PS>0,100/df.PS,np.nan); df["mo"]=df.time.dt.to_period("M")
df=df[(df.Close*df.Volume>=5e9)].copy()
book=df[df.ROE_Min3Y>=0].copy()                       # book-trustworthy only (the actionable set)
book["golden"]=book.pb_z<=-1
# cfy tercile within month (low/mid/high), among names with cfy present
book["cfy_t"]=book.groupby("mo").F_cfy.transform(lambda g: pd.qcut(g.rank(method="first"),3,labels=["lo","mid","hi"]) if g.notna().sum()>=9 else np.nan)

print("### Forward profit_2M (median %) — does golden survive WEAK cashflow? (book-trustworthy) ###")
print(f"  {'cell':<24}{'n':>7}{'med_2M':>9}{'med_3M':>9}{'win%>0':>8}")
def cell(d,lbl):
    if len(d)<30: print(f"  {lbl:<24}{len(d):>7}{'(thin)':>9}"); return
    print(f"  {lbl:<24}{len(d):>7}{d.profit_2M.median():>9.2f}{d.profit_3M.median():>9.2f}{100*(d.profit_2M>0).mean():>7.0f}%")
cell(book[book.golden], "GOLDEN (pb_z<=-1) all")
cell(book[book.golden & (book.cfy_t=='lo')], "  golden & cfy-LOW")
cell(book[book.golden & (book.cfy_t=='mid')], "  golden & cfy-mid")
cell(book[book.golden & (book.cfy_t=='hi')], "  golden & cfy-HIGH")
cell(book[~book.golden], "non-golden all")
cell(book[(~book.golden) & (book.cfy_t=='lo')], "  non-golden & cfy-LOW")

# is the golden edge robust by year? (book-trustworthy)
print("\n### golden vs non-golden fwd-2M edge by year (book-trustworthy) ###")
for y,g in book.groupby(book.time.dt.year):
    gg=g[g.golden].profit_2M.median(); ng=g[~g.golden].profit_2M.median()
    n=g.golden.sum()
    if pd.notna(gg) and n>=5: print(f"  {y}: golden {gg:+5.1f} (n{n:3d}) vs non {ng:+5.1f}  edge {gg-ng:+.1f}")

# --- calibrate golden bonus in the composite (BROAD COMPOUNDER weights) ---
for c in ["F_ey","F_cfy","F_ps"]:
    df["p_"+c[2:]]=df.groupby(["mo","route"])[c].rank(pct=True)
df["golden"]=(df.pb_z<=-1).astype(float)
dd=df[df.ROE_Min3Y>=0].copy()
def comp(d,g_bonus=0.0,floor=None):
    P=np.vstack([d.p_ey,d.p_cfy,d.p_ps]); W=np.array([.45,.30,.25])[:,None]
    pr=~np.isnan(P); s=np.nansum(np.where(pr,P*W,0),0)/np.nansum(np.where(pr,W,0),0)
    s=s+g_bonus*d.golden.fillna(0).values
    if floor is not None:                              # golden book-OK -> at least `floor` percentile-score
        s=np.where(d.golden.fillna(0).values>0, np.maximum(s,floor), s)
    return pd.Series(np.clip(s,0,1.2),index=d.index)
def ic(s,d,fwd="profit_2M"):
    a=[];t=pd.DataFrame({"s":s,"y":d[fwd],"mo":d.mo}).dropna()
    for _,gm in t.groupby("mo"):
        if len(gm)>=8 and gm.s.nunique()>3: a.append(spearmanr(gm.s,gm.y).correlation)
    a=np.array([x for x in a if pd.notna(x)]); return a.mean(),a.mean()/(a.std(ddof=1)/np.sqrt(len(a)))
print("\n### composite IC (profit_2M, book-OK) vs golden treatment ###")
for g in [0.0,0.05,0.10,0.15,0.20]:
    i=ic(comp(dd,g_bonus=g),dd); print(f"  bonus +{g:.2f}: IC{i[0]:+.3f} t{i[1]:.1f}")
for fl in [0.50,0.60,0.70]:
    i=ic(comp(dd,g_bonus=0.05,floor=fl),dd); print(f"  bonus .05 + golden floor {fl:.2f}: IC{i[0]:+.3f} t{i[1]:.1f}")
print("[done]")
