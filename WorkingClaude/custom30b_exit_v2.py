# -*- coding: utf-8 -*-
"""custom30b_exit_v2.py — EXIT signal redo with SELF-COMPUTED rolling volume stats (the BQ
Volume_Max1Y_High column was unreliable). For extended names in bull/exbull, test whether a
volume BLOW-OFF predicts weak/negative forward returns (distribution top).
Volume features per ticker (causal, rolling):
  vol_z      = (Volume - mean60) / std60           (spike vs own 2-month norm)
  climax_1y  = Volume / max252                      (today vs own true 1Y max daily volume)
Forward r5/r10/r20 bucketed by each, restricted to uptrend (Close>MA50). Split BULL4 vs EXBULL5
(IC study: momentum/RSI IC inverts in EXBULL = be-fearful). Also VNINDEX market-level vol_z."""
import os, numpy as np, pandas as pd
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq

st=bq("SELECT time, state FROM tav2_bq.vnindex_5state WHERE time>='2010-01-01'")
st["time"]=pd.to_datetime(st["time"]); state=st.set_index("time")["state"]
state=state[~state.index.duplicated(keep="last")].sort_index()

raw=bq("""SELECT ticker, time, Close, Volume, MA50, D_RSI
FROM tav2_bq.ticker_prune WHERE time>='2010-01-01' AND Close>0 AND Volume>0 ORDER BY ticker, time""")
raw["time"]=pd.to_datetime(raw["time"])
g=raw.groupby("ticker",group_keys=False)
raw["vm60"]=g["Volume"].transform(lambda s:s.rolling(60,min_periods=30).mean())
raw["vs60"]=g["Volume"].transform(lambda s:s.rolling(60,min_periods=30).std())
raw["vmax252"]=g["Volume"].transform(lambda s:s.rolling(252,min_periods=120).max())
raw["vol_z"]=(raw["Volume"]-raw["vm60"])/raw["vs60"]
raw["climax_1y"]=raw["Volume"]/raw["vmax252"]
raw["r5"]=g["Close"].transform(lambda s:s.shift(-5)/s-1)
raw["r10"]=g["Close"].transform(lambda s:s.shift(-10)/s-1)
raw["r20"]=g["Close"].transform(lambda s:s.shift(-20)/s-1)
raw["st"]=raw["time"].map(state)
d=raw[(raw.Close>raw.MA50)&raw.st.isin([4,5])].dropna(subset=["vol_z","climax_1y","r20"])
print(f"extended (Close>MA50) bull/exbull obs: {len(d):,}\n")

def show(sub,col,bins,labels,title):
    sub=sub.copy(); sub["bin"]=pd.cut(sub[col],bins,labels=labels)
    base=sub["r20"].mean()*100
    print(f"  {title} (baseline fwd_r20={base:+.1f}%)")
    print(f"  {'bucket':14s} {'n':>7s} {'r5':>8s} {'r10':>8s} {'r20':>8s} {'r20_med':>9s} {'%neg20':>8s}")
    for b in labels:
        x=sub[sub.bin==b]
        if len(x)<30: continue
        print(f"  {b:14s} {len(x):7d} {x.r5.mean()*100:+7.1f}% {x.r10.mean()*100:+7.1f}% {x.r20.mean()*100:+7.1f}% "
              f"{x.r20.median()*100:+8.1f}% {(x.r20<0).mean()*100:7.1f}%")

print("(1) STOCK-level vol_z (spike vs 2-month norm):")
show(d,"vol_z",[-9,1,2,3,5,99],["<1","1-2","2-3","3-5",">5(blowoff)"],"all bull/exbull")
print("\n(2) STOCK-level climax_1y = Volume / true 1Y-max-daily:")
show(d,"climax_1y",[0,0.5,0.8,1.0,99],["<0.5","0.5-0.8","0.8-1.0",">=1.0(1Y high)"],"all bull/exbull")
print("\n(3) EXBULL5 only (be-fearful regime) — blow-off + overbought:")
de=d[d.st==5]
show(de,"vol_z",[-9,2,3,5,99],["<2","2-3","3-5",">5(blowoff)"],"EXBULL5")
print("\n(4) STOCK blow-off AT high RSI (overbought distribution), bull/exbull:")
dd=d[d.D_RSI>=0.70]
show(dd,"vol_z",[-9,2,3,99],["<2","2-3",">3(blowoff+OB)"],"RSI>=0.70")

# market-level VNINDEX vol_z
v=bq("""SELECT t.time,t.Close,t.Volume FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX' AND t.time>='2010-01-01' ORDER BY t.time""")
v["time"]=pd.to_datetime(v["time"]); v=v.set_index("time").sort_index()
v["vz"]=(v.Volume-v.Volume.rolling(60,min_periods=30).mean())/v.Volume.rolling(60,min_periods=30).std()
v["r5"]=v.Close.shift(-5)/v.Close-1; v["r10"]=v.Close.shift(-10)/v.Close-1; v["r20"]=v.Close.shift(-20)/v.Close-1
v["st"]=v.index.map(state); vb=v[v.st.isin([4,5])].dropna(subset=["vz","r20"]).copy()
vb["bin"]=pd.cut(vb["vz"],[-9,1,2,3,99],labels=["<1","1-2","2-3",">3(mkt blowoff)"])
print(f"\n(5) MARKET VNINDEX vol_z (bull/exbull, baseline fwd_r20={vb.r20.mean()*100:+.1f}%):")
for b in ["<1","1-2","2-3",">3(mkt blowoff)"]:
    x=vb[vb.bin==b]
    if len(x)<8: continue
    print(f"  {b:16s} {len(x):5d} r5 {x.r5.mean()*100:+6.1f}% r10 {x.r10.mean()*100:+6.1f}% r20 {x.r20.mean()*100:+6.1f}% %neg20 {(x.r20<0).mean()*100:.0f}%")
print("\nREAD: top vol-blowoff bucket fwd_r20 << baseline / negative / high %neg = volume-climax TOP = trim/exit signal.")
