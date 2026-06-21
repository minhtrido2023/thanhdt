#!/usr/bin/env python3
"""cfo_yield_ic.py — does CFO/MarketCap (TTM) add forward-return signal? IC test before wiring in.
Cross-sectional Spearman IC by date (proper IC, removes time trend), excl banks (CFO meaningless).
Tests: cfo_yield, fcf_yield, earnings_yield(ey), pb_z, cfo_np vs fwd O3M/O6M/O1Y. Incremental vs PE/PB."""
import warnings; warnings.filterwarnings("ignore")
import sys, os
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
def spearmanr(a,b):
    a=pd.Series(np.asarray(a,dtype=float)); b=pd.Series(np.asarray(b,dtype=float))
    ra,rb=a.rank(),b.rank()
    if ra.std()==0 or rb.std()==0: return (np.nan,np.nan)
    return (ra.corr(rb),0.0)
W=r"/home/trido/thanhdt/WorkingClaude"
d=pd.read_csv(os.path.join(W,"data","cfo_yield_panel.csv"))
banks=set(pd.read_csv(os.path.join(W,"data","bank_lens_v3.csv"))["ticker"])
d=d[~d["ticker"].isin(banks)].copy()
d["time"]=pd.to_datetime(d["time"]); d["yr"]=d["time"].dt.year
# fwd return columns: O* are price-relatives (~1.0), profit_3M is %; Spearman is scale/offset-invariant
FWD=["O3M","O6M","O1Y"]
METRICS=["cfo_yield","fcf_yield","ey","cfo_np","pb_z"]
# direction note: higher yield = cheaper = expect +IC; pb_z lower = cheaper = expect -IC

def xs_ic(df, m, f):
    """cross-sectional Spearman by date, averaged; returns mean IC, t-stat, n_dates"""
    ics=[]
    for _,g in df.groupby("time"):
        g2=g[[m,f]].dropna()
        if len(g2)>=8:
            r,_=spearmanr(g2[m],g2[f])
            if not np.isnan(r): ics.append(r)
    ics=np.array(ics)
    if len(ics)<6: return (np.nan,np.nan,len(ics))
    return (ics.mean(), ics.mean()/ics.std()*np.sqrt(len(ics)), len(ics))

print(f"panel: {len(d)} obs, {d['ticker'].nunique()} non-bank tickers, {d['time'].nunique()} month-dates, {d['yr'].min()}-{d['yr'].max()}")
print()
print("=== Cross-sectional IC (mean Spearman by date, t-stat) ===")
print(f"{'metric':<11}"+"".join(f"{f:>22}" for f in FWD))
for m in METRICS:
    row=f"{m:<11}"
    for f in FWD:
        ic,t,n=xs_ic(d,m,f); row+=f"{ic:+.3f} (t={t:+.1f},n{n})".rjust(22)
    print(row)
print("  [higher yield=cheaper→expect +IC; pb_z lower=cheaper→expect −IC]")
print()
# ---- redundancy: how correlated is cfo_yield with ey and pb (rank space)? ----
print("=== Redundancy (pooled Spearman between predictors) ===")
for a,b in [("cfo_yield","ey"),("cfo_yield","pb_z"),("cfo_yield","fcf_yield"),("fcf_yield","ey"),("cfo_np","ey")]:
    g=d[[a,b]].dropna(); r,_=spearmanr(g[a],g[b]); print(f"  {a:<11} vs {b:<11}: {r:+.2f}")
print()
# ---- INCREMENTAL: residualize cfo_yield on (ey, pb_z) per date, test residual IC ----
print("=== Incremental IC: cfo_yield AFTER removing earnings-yield & PB (rank-residual) ===")
def resid_ic(df,f):
    ics=[]
    for _,g in df.groupby("time"):
        g2=g[["cfo_yield","ey","pb_z",f]].dropna()
        if len(g2)<10: continue
        R=g2.rank()
        # residual of cfo_yield rank vs [ey rank, pb_z rank]
        X=np.column_stack([np.ones(len(R)),R["ey"],R["pb_z"]]); y=R["cfo_yield"].values
        try: beta,_,_,_=np.linalg.lstsq(X,y,rcond=None); res=y-X@beta
        except Exception: continue
        r,_=spearmanr(res,g2[f]);
        if not np.isnan(r): ics.append(r)
    ics=np.array(ics); return (ics.mean(), ics.mean()/ics.std()*np.sqrt(len(ics)), len(ics)) if len(ics)>=6 else (np.nan,np.nan,len(ics))
for f in FWD:
    ic,t,n=resid_ic(d,f); print(f"  resid cfo_yield vs {f:<5}: IC {ic:+.3f} (t={t:+.1f}, n={n})")
print()
# ---- by-year stability (O6M) ----
print("=== cfo_yield IC vs O6M by year (cyclicality check) ===")
for yr in sorted(d["yr"].unique()):
    sub=d[d["yr"]==yr]; ic,t,n=xs_ic(sub,"cfo_yield","O6M")
    if not np.isnan(ic): print(f"  {yr}: IC {ic:+.3f} (n_dates {n})")
