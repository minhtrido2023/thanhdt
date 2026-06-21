#!/usr/bin/env python3
"""vgc_energy.py — does gas/energy input drive VGC margin? And does the IP segment dilute it?
(A) GPM vs Brent (interp quarterly, lagged: high energy -> margin compress with lag -> expect NEG corr).
(B) VGC GPM co-movement with energy-intensive cohort (cement HT1/BCC + ceramic CVT) vs pure-ceramic VHL."""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"
def corr(a,b):
    z=pd.concat([a,b],axis=1).dropna(); return (z.iloc[:,0].corr(z.iloc[:,1]),len(z)) if len(z)>=8 else (np.nan,len(z))
# --- energy proxy: Brent interpolated to quarter-end ---
br=pd.read_csv(os.path.join(W,"data","brent_monthly.csv")); br["d"]=pd.to_datetime(br["m"])
br=br.set_index("d")["p"].sort_index()
brq=br.resample("QE").mean().interpolate("linear"); brq.index=brq.index.to_period("Q")
# --- GPM panel ---
d=pd.read_csv(os.path.join(W,"data","vgc_energy_panel.csv")); d["time"]=pd.to_datetime(d["time"]); d["q"]=d["time"].dt.to_period("Q")
g=d.sort_values("time").groupby(["ticker","q"]).last().reset_index().pivot(index="q",columns="ticker",values="gpm").sort_index()

print("=== (A) GPM vs Brent energy proxy (NEG = high energy compresses margin) ===")
print(f"{'ticker':<7}{'corr lvl':>10}{'corr Δ':>9}{'lag+1Q lvl':>12}{'lag+2Q lvl':>12}   (n)")
for t in ["VGC","VHL","CVT","HT1","BCC","DTC"]:
    if t not in g: continue
    s=g[t].dropna(); e=brq.reindex(s.index)
    cl,n=corr(s,e); cd,_=corr(s.diff(),e.diff())
    # Brent LEADS margin: shift brent forward so this-q energy aligns to next-q margin
    cl1,_=corr(s, brq.shift(1).reindex(s.index)); cl2,_=corr(s, brq.shift(2).reindex(s.index))
    print(f"{t:<7}{cl:>+10.2f}{cd:>+9.2f}{cl1:>+12.2f}{cl2:>+12.2f}   ({n})")
print("  [VGC blended (VLXD+IP) vs VHL pure-ceramic: if |VGC corr| < |VHL corr| → IP segment DILUTES energy sensitivity]")
print()
print("=== (B) VGC GPM co-movement with energy-intensive cohort (Δ-change corr) ===")
coh=["VHL","CVT","HT1","BCC"]
for t in coh:
    if t in g: cl,_=corr(g["VGC"].diff(),g[t].diff()); cll,_=corr(g["VGC"],g[t]); print(f"  VGC vs {t:<4}: Δcorr {cl:+.2f}  levelcorr {cll:+.2f}")
# VGC correlation to cohort average
cohort=g[[c for c in coh if c in g]].mean(axis=1)
clc,_=corr(g["VGC"].diff(),cohort.diff()); print(f"  VGC vs COHORT-avg: Δcorr {clc:+.2f}")
print()
print("=== margin volatility (energy passthrough leaves a footprint: high vol = exposed) ===")
for t in ["VGC","VHL","CVT","HT1","BCC"]:
    if t in g: s=g[t].dropna()*100; print(f"  {t:<5} GPM mean {s.mean():.1f}%  stdev {s.std():.1f}pp  range [{s.min():.0f},{s.max():.0f}]")
