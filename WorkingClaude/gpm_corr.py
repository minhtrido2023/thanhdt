#!/usr/bin/env python3
"""gpm_corr.py — does COARSE input-grouping (oil/petrochem) capture margin co-movement?
Tests gross-margin correlation within/across plastic-resin consumers vs rubber vs non-oil controls,
on GPM levels AND QoQ changes (isolates input-cost cycle), + lead-lag. Answers: coarse vs fine, VCS membership."""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"
d=pd.read_csv(os.path.join(W,"data","gpm_corr_panel.csv")); d["time"]=pd.to_datetime(d["time"])
d["q"]=d["time"].dt.to_period("Q")
w=d.sort_values("time").groupby(["ticker","q"]).last().reset_index().pivot(index="q",columns="ticker",values="gpm")
w=w.sort_index()
GROUPS={"BMP":"plastic","NTP":"plastic","AAA":"plastic","TLG":"plastic","VCS":"plastic(quartz+resin)",
        "DRC":"rubber","CSM":"rubber","VNM":"control-milk","PNJ":"control-gold"}
def corr(a,b,diff=False):
    x=w[a].copy(); y=w[b].copy()
    if diff: x=x.diff(); y=y.diff()
    z=pd.concat([x,y],axis=1).dropna()
    return (z.iloc[:,0].corr(z.iloc[:,1]), len(z)) if len(z)>=8 else (np.nan,len(z))
print(f"GPM panel: {w.shape[1]} tickers, {w.shape[0]} quarters {w.index.min()}–{w.index.max()}\n")
print("=== Pairwise GPM correlation (level / ΔQoQ-change) ===")
pairs=[("BMP","NTP","within-PVC (both pipe, PVC input)"),
       ("BMP","AAA","cross-plastic (PVC vs other resin)"),
       ("BMP","TLG","cross-plastic (PVC vs plastic/petro)"),
       ("BMP","VCS","plastic vs VCS(quartz+resin binder)"),
       ("NTP","VCS","plastic vs VCS"),
       ("AAA","TLG","cross-plastic"),
       ("DRC","CSM","within-rubber (control group)"),
       ("BMP","DRC","plastic vs rubber (diff input)"),
       ("BMP","VNM","plastic vs milk (non-oil control)"),
       ("BMP","PNJ","plastic vs gold (non-oil control)")]
for a,b,lab in pairs:
    if a in w and b in w:
        cl,n=corr(a,b); cd,_=corr(a,b,diff=True)
        print(f"  {a}-{b:4s} level {cl:+.2f}  Δchange {cd:+.2f}  (n={n})  {lab}")
print()
# lead-lag on ΔGPM: does BMP lead NTP / VCS by ~1 quarter?
print("=== Lead-lag (ΔGPM cross-corr; +k = first name LEADS by k quarters) ===")
for a,b in [("BMP","NTP"),("BMP","VCS")]:
    xa=w[a].diff(); xb=w[b].diff()
    line=f"  {a} vs {b}: "
    for k in [-1,0,1]:
        z=pd.concat([xa.shift(k),xb],axis=1).dropna()
        r=z.iloc[:,0].corr(z.iloc[:,1]) if len(z)>=8 else np.nan
        line+=f"lag{k:+d} {r:+.2f}  "
    print(line)
print()
# coarse-group cohesion: mean cross-corr WITHIN coarse plastic bucket vs to controls
plastic=["BMP","NTP","AAA","TLG","VCS"]
import itertools
within=[corr(a,b,diff=True)[0] for a,b in itertools.combinations([p for p in plastic if p in w],2)]
within=[x for x in within if pd.notna(x)]
toctrl=[corr(p,c,diff=True)[0] for p in plastic for c in ["VNM","PNJ"] if p in w and c in w]
toctrl=[x for x in toctrl if pd.notna(x)]
print(f"COARSE plastic/oil bucket — mean within-group ΔGPM corr: {np.mean(within):+.2f} (n_pairs {len(within)})")
print(f"                          — mean plastic-to-control corr: {np.mean(toctrl):+.2f} (n_pairs {len(toctrl)})")
