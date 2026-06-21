# -*- coding: utf-8 -*-
"""
composite_v3_sweep.py  (Stage 2 of 8L valuation v3)
====================================================
Build the coverage-aware, sector-aware value composite and weight-sweep it for a ROBUST
PLATEAU (not a sharp peak). Lenses (route-neutral percentile, higher=cheaper):
  p_ey  = pct(100/PE)      p_cfy = pct(100/PCF)     p_ps = pct(100/PS)
Coverage-aware: value = Σ(wᵢ·pᵢ over PRESENT i) / Σ(wᵢ over present i)  (NO fillna(0.5) bias).
Golden bonus: + g·1[pb_z<=-1] (only non-linear pb_z signal). TRAP: ROE_Min3Y<0 excluded from IC.
Negative handling: PE<=0 / PCF<=0 / PS<=0 → that lens NaN (no reward). PB<0 → score=0.
Compares candidate weight sets vs the v2 baseline (0.35·pct(-pb_z)+0.65·pct(1/PE)).
"""
import os, numpy as np, pandas as pd
from scipy.stats import spearmanr
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
df = pd.read_csv(f"{WORKDIR}/data/value_panel_2014.csv", parse_dates=["time"])
df["F_ey"]  = np.where(df.PE  > 0, 100.0/df.PE,  np.nan)
df["F_cfy"] = np.where(df.PCF > 0, 100.0/df.PCF, np.nan)
df["F_ps"]  = np.where(df.PS  > 0, 100.0/df.PS,  np.nan)
df["mo"] = df.time.dt.to_period("M")
df = df[(df.Close*df.Volume) >= 5e9].copy()
# TRAP guard: drop loss-quality from IC eval (they're force-zoned 4_TRAP in prod anyway)
df = df[~(df.ROE_Min3Y < 0)].copy()

# route-neutral percentile of each lens within (month, route)
for c in ["F_ey","F_cfy","F_ps"]:
    df["p_"+c[2:]] = df.groupby(["mo","route"])[c].rank(pct=True)
df["golden"] = (df.pb_z <= -1).astype(float)   # non-linear pb_z flag

def composite(d, w_ey, w_cfy, w_ps, g=0.05):
    P = np.vstack([d.p_ey.values, d.p_cfy.values, d.p_ps.values])      # 3 x N
    W = np.array([w_ey, w_cfy, w_ps])[:, None]
    present = ~np.isnan(P)
    num = np.nansum(np.where(present, P*W, 0.0), axis=0)
    den = np.nansum(np.where(present, W, 0.0), axis=0)
    s = np.where(den > 0, num/den, np.nan)
    s = s + g*np.where(d.golden.fillna(0).values > 0, 1.0, 0.0)        # golden bonus
    s = np.where(d.PB.values < 0, 0.0, s)                              # PB<0 -> 0
    return pd.Series(np.clip(s, 0, 1.2), index=d.index)

def ic(score, d, fwd="profit_2M", minn=8):
    a=[]
    t=pd.DataFrame({"s":score,"y":d[fwd],"mo":d.mo}).dropna()
    for _,gm in t.groupby("mo"):
        if len(gm)>=minn and gm.s.nunique()>3:
            a.append(spearmanr(gm.s, gm.y).correlation)
    a=[x for x in a if pd.notna(x)]; a=np.array(a)
    return a.mean(), a.mean()/(a.std(ddof=1)/np.sqrt(len(a))), (a>0).mean(), len(a)

def decile(score, d, fwd="profit_2M"):
    t=pd.DataFrame({"s":score,"y":d[fwd],"mo":d.mo}).dropna()
    t["q"]=t.groupby("mo").s.transform(lambda x: pd.qcut(x.rank(method="first"),5,labels=False,duplicates="drop"))
    m=t.groupby("q").y.median()
    return m.get(4,np.nan)-m.get(0,np.nan), m.to_dict()

def byyear(score,d,fwd="profit_2M"):
    t=pd.DataFrame({"s":score,"y":d[fwd],"mo":d.mo,"yr":d.time.dt.year}).dropna()
    out={}
    for yr,gy in t.groupby("yr"):
        a=[spearmanr(gm.s,gm.y).correlation for _,gm in gy.groupby("mo") if len(gm)>=8 and gm.s.nunique()>3]
        a=[x for x in a if pd.notna(x)]
        if a: out[yr]=np.mean(a)
    return out

# --- v2 baseline: 0.35*pct(-pb_z) + 0.65*pct(1/PE) with .fillna(0.5) (the current prod shape) ---
df["p_pbz"]=df.groupby(["mo","route"])["pb_z"].rank(pct=True,ascending=False)
v2 = (0.35*df.p_pbz.fillna(0.5) + 0.65*df.p_ey.fillna(0.5))
print("### Baseline v2 (0.35 pct(-pb_z) + 0.65 pct(1/PE), fillna .5) — BROAD ###")
for fwd in ["profit_1M","profit_2M","profit_3M"]:
    i=ic(v2,df,fwd); print(f"  {fwd}: IC{i[0]:+.3f} t{i[1]:.1f} hit{100*i[2]:.0f}% mo{i[3]}")
ds=decile(v2,df); print(f"  decile D5-D1 (2M): {ds[0]:+.2f}  ladder={{{', '.join(f'{k}:{v:+.1f}' for k,v in ds[1].items())}}}")

# --- candidate weight grid (robust-plateau scan) on BROAD ---
print("\n### Composite v3 weight sweep — BROAD (profit_2M) ###")
print(f"  {'w_ey':>5}{'w_cfy':>6}{'w_ps':>5} | {'IC':>7}{'t':>6}{'hit%':>6}{'D5-D1':>8}")
GRID=[(.5,.3,.2),(.45,.3,.25),(.4,.3,.3),(.5,.25,.25),(.6,.2,.2),(.4,.35,.25),
      (.35,.35,.3),(.45,.35,.2),(.33,.33,.34),(.5,.35,.15),(.4,.25,.35),(.55,.25,.2)]
best=[]
for w in GRID:
    s=composite(df,*w); i=ic(s,df); d5=decile(s,df)[0]
    best.append((w,i[0],d5))
    print(f"  {w[0]:>5.2f}{w[1]:>6.2f}{w[2]:>5.2f} | {i[0]:>+7.3f}{i[1]:>6.1f}{100*i[2]:>6.0f}{d5:>+8.2f}")

# --- chosen sector weights -> per-route IC + by-year ---
SECTOR_W = {  # (w_ey, w_cfy, w_ps)
  "COMPOUNDER":(.45,.30,.25), "CYCLICAL":(.35,.50,.15),
  "RETAIL":(.35,.20,.45), "_default":(.45,.30,.25),
}
print("\n### Chosen sector weights: per-route composite IC (profit_2M) + by-year ###")
for rt in ["COMPOUNDER","CYCLICAL","SECURITIES","REALESTATE"]:
    d=df[df.route==rt]
    if len(d)<200: continue
    w=SECTOR_W.get(rt, SECTOR_W["_default"]); s=composite(d,*w)
    i=ic(s,d); d5=decile(s,d)[0]
    print(f"  {rt:<12} w={w} IC{i[0]:+.3f} t{i[1]:.1f} hit{100*i[2]:.0f}% D5-D1{d5:+.2f} (vs v2 ", end="")
    iv=ic((0.35*d.p_pbz.fillna(0.5)+0.65*d.p_ey.fillna(0.5)),d); print(f"IC{iv[0]:+.3f})")
# consumer proxy
cons=df[df.ICB_Code.apply(lambda c: pd.notna(c) and (3500<=c<3800 or 5300<=c<5400))]
s=composite(cons,*SECTOR_W["RETAIL"]); i=ic(s,cons); d5=decile(s,cons)[0]
iv=ic((0.35*cons.p_pbz.fillna(0.5)+0.65*cons.p_ey.fillna(0.5)),cons)
print(f"  {'CONSUMER':<12} w={SECTOR_W['RETAIL']} IC{i[0]:+.3f} t{i[1]:.1f} D5-D1{d5:+.2f} (vs v2 IC{iv[0]:+.3f})")

print("\n### Best plateau pick — COMPOUNDER (.45,.30,.25) by-year (profit_2M) ###")
by=byyear(composite(df[df.route=='COMPOUNDER'],.45,.30,.25),df[df.route=='COMPOUNDER'])
print("  "+"  ".join(f"{y}:{v:+.02f}" for y,v in by.items()))
print("[done]")
