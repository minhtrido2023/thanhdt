# -*- coding: utf-8 -*-
"""
cfy_stability_test.py — is the 1/PCF (cfy) lens too noisy for v3? User worry: CFO flips sign
quarter to quarter (neg this Q, pos next, two neg then pos). Tests:
  1. Is PCF single-quarter or TTM based? (correlate PCF-present with single-Q vs TTM CFO sign)
  2. How OFTEN does cfy actually flip present<->absent quarter-to-quarter? (frequency of the problem)
  3. Does the COVERAGE-AWARE composite absorb it? (value_score persistence with vs without cfy)
  4. Would cfo_normy (TTM-3Y normalized, smoother) be a steadier lens than raw 1/PCF? (persistence + IC)
"""
import os, numpy as np, pandas as pd
from scipy.stats import spearmanr
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
df = pd.read_csv(f"{WORKDIR}/data/value_panel_2014.csv", parse_dates=["time"])
df["q"] = df.time.dt.to_period("Q")
# quarter-level (last month per ticker-quarter)
q = df.sort_values("time").groupby(["ticker","q"]).last().reset_index()
q = q[(q.Close*q.Volume >= 5e9)].copy()
q["cfo_q"]  = q["CF_OA_P0"]                                   # single-quarter CFO/assets
q["cfo_ttm"]= q[[f"CF_OA_P{i}" for i in range(4)]].sum(axis=1, min_count=1)   # trailing-4Q
q["pcf_pos"]= (q.PCF > 0)
q["cfy"]    = np.where(q.PCF>0, 100/q.PCF, np.nan)
q = q.sort_values(["ticker","q"])

print("### 1) Is PCF single-Q or TTM based? (agreement of PCF>0 with each CFO sign) ###")
v = q.dropna(subset=["PCF","cfo_q","cfo_ttm"])
agree_q   = (v.pcf_pos == (v.cfo_q>0)).mean()
agree_ttm = (v.pcf_pos == (v.cfo_ttm>0)).mean()
print(f"  PCF>0 matches single-Q CFO>0 : {agree_q:.0%}")
print(f"  PCF>0 matches TTM(4Q)  CFO>0 : {agree_ttm:.0%}   <- higher => PCF is TTM-smoothed")

print("\n### 2) How often does each actually flip sign quarter-to-quarter? (per-ticker mean) ###")
def flip_rate(col_sign):
    r=[]
    for t,g in q.groupby("ticker"):
        s = g[col_sign].dropna().astype(int)
        if len(s)>=8: r.append((s.diff().abs()>0).mean())
    return np.mean(r)
print(f"  single-Q CFO>0 flip rate : {flip_rate('cfo_q' ) if False else np.mean([ (g['cfo_q'].dropna().gt(0).astype(int).diff().abs()>0).mean() for _,g in q.groupby('ticker') if g['cfo_q'].notna().sum()>=8]):.1%}  (the user's worry)")
print(f"  PCF-present flip rate     : {np.mean([ (g['pcf_pos'].astype(int).diff().abs()>0).mean() for _,g in q.groupby('ticker') if g['pcf_pos'].notna().sum()>=8]):.1%}  (does the LENS flip?)")
print(f"  TTM CFO>0 flip rate       : {np.mean([ (g['cfo_ttm'].dropna().gt(0).astype(int).diff().abs()>0).mean() for _,g in q.groupby('ticker') if g['cfo_ttm'].notna().sum()>=8]):.1%}")
print(f"  PCF overall coverage      : {q.PCF.gt(0).mean():.0%}")

print("\n### 3) Does coverage-aware composite ABSORB cfy dropping out? (q-to-q rank persistence) ###")
# build the v3-style lenses (route-neutral pct) at quarter level
q["F_ey"]=np.where(q.PE>0,100/q.PE,np.nan); q["F_cfy"]=q.cfy; q["F_ps"]=np.where(q.PS>0,100/q.PS,np.nan)
for c in ["F_ey","F_cfy","F_ps"]: q["p_"+c[2:]]=q.groupby(["q","route"])[c].rank(pct=True)
def cov_aware(d,w):
    P=np.vstack([d.p_ey.values,d.p_cfy.values,d.p_ps.values]); W=np.array(w)[:,None]
    pr=~np.isnan(P); return pd.Series(np.where(np.nansum(np.where(pr,W,0),0)>0,
        np.nansum(np.where(pr,P*W,0),0)/np.nansum(np.where(pr,W,0),0),np.nan), index=d.index)
q["vs_full"]=cov_aware(q,[.45,.30,.25]); q["vs_eyonly"]=cov_aware(q,[1,0,0])
def persistence(col):    # mean q-to-q rank autocorr per ticker
    ac=[]
    for t,g in q.groupby("ticker"):
        s=g[col].dropna()
        if len(s)>=8: ac.append(s.autocorr(1))
    return np.nanmean(ac)
print(f"  persistence (q-to-q autocorr): cfy-rank {persistence('p_cfy'):.2f} | ey-rank {persistence('p_ey'):.2f} | ps-rank {persistence('p_ps'):.2f}")
print(f"  composite value_score persistence: full(ey+cfy+ps) {persistence('vs_full'):.2f} | ey-only {persistence('vs_eyonly'):.2f}")
print("  -> if full ~ ey-only, the coverage-aware blend is NOT destabilized by cfy flipping")

print("\n### 4) raw 1/PCF vs cfo_normy (TTM-3Y smoothed) — persistence + IC ###")
_ttm = q[[f"CF_OA_P{i}" for i in range(4)]].sum(axis=1,min_count=1); _n3=q["CF_OA_3Y"]/3.0
q["cfo_normy"]=np.where((q.PCF>0)&(_ttm>0)&(_n3>0),(100/q.PCF)*np.clip(_n3/_ttm,0.3,3.0),np.nan)
q["p_normy"]=q.groupby(["q","route"])["cfo_normy"].rank(pct=True)
def xic(col,fwd="profit_2M"):
    a=[]
    for _,g in q.groupby("q"):
        s=g[[col,fwd]].dropna()
        if len(s)>=8 and s[col].nunique()>3: a.append(spearmanr(s[col],s[fwd]).correlation)
    a=np.array([x for x in a if pd.notna(x)]); return a.mean(), a.mean()/(a.std(ddof=1)/np.sqrt(len(a)))
ic_raw=xic("cfy"); ic_norm=xic("cfo_normy")
print(f"  raw 1/PCF   : persistence {persistence('p_cfy'):.2f}  IC {ic_raw[0]:+.3f} (t{ic_raw[1]:.1f})  cov {q.cfy.notna().mean():.0%}")
print(f"  cfo_normy   : persistence {persistence('p_normy'):.2f}  IC {ic_norm[0]:+.3f} (t{ic_norm[1]:.1f})  cov {q.cfo_normy.notna().mean():.0%}")
print("[done]")
