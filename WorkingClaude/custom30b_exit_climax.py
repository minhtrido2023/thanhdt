# -*- coding: utf-8 -*-
"""custom30b_exit_climax.py — EXIT signal for custom30B: at TOPS there are blow-off sessions with
HUGE volume vs history. Test if a volume-climax predicts NEGATIVE/low forward returns (distribution top).
Two levels:
  (1) STOCK-level: for extended names (mom200>0) in bull/exbull, forward r5/r20 bucketed by
      climax = Volume / Volume_Max1Y_High  (>=1 => today is ~biggest volume day in a year).
  (2) MARKET-level: VNINDEX daily volume vs its trailing-1Y max -> forward VNINDEX r5/r20/r20.
If top climax bucket shows much LOWER (or negative) forward return vs baseline -> a sell/trim trigger."""
import os, numpy as np, pandas as pd
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq

st=bq("SELECT time, state FROM tav2_bq.vnindex_5state WHERE time>='2010-01-01'")
st["time"]=pd.to_datetime(st["time"]); state=st.set_index("time")["state"]
state=state[~state.index.duplicated(keep="last")].sort_index()

# (1) STOCK-level climax
q="""WITH base AS (
  SELECT ticker, time, Close, MA200, Volume, Volume_Max1Y_High, Volume_3M_P90,
    LEAD(Close,5)  OVER w AS c5, LEAD(Close,20) OVER w AS c20
  FROM tav2_bq.ticker_prune WHERE time>='2010-01-01' AND Close>0 AND Volume_Max1Y_High>0
  WINDOW w AS (PARTITION BY ticker ORDER BY time))
SELECT time, ticker, SAFE_DIVIDE(Close,NULLIF(MA200,0))-1 AS mom200,
  SAFE_DIVIDE(Volume, Volume_Max1Y_High) AS climax1y,
  SAFE_DIVIDE(Volume, NULLIF(Volume_3M_P90,0)) AS climax_p90,
  SAFE_DIVIDE(c5,Close)-1 AS r5, SAFE_DIVIDE(c20,Close)-1 AS r20
FROM base WHERE c20 IS NOT NULL"""
d=bq(q); d["time"]=pd.to_datetime(d["time"]); d["st"]=d["time"].map(state)
d=d.dropna(subset=["st","climax1y","r20"])
d=d[d.st.isin([4,5]) & (d.mom200>0)]   # bull/exbull, extended (uptrend names we'd hold)
print(f"(1) STOCK-level: {len(d):,} extended bull/exbull obs\n")
d["bin"]=pd.cut(d["climax1y"],[0,0.5,1.0,1.5,2.0,100],labels=["<0.5","0.5-1","1-1.5","1.5-2",">2x_1Ymax"])
print(f"  climax = Volume / Volume_Max1Y_High (>=1 = new ~1Y volume high)")
print(f"  {'bucket':12s} {'n':>8s} {'fwd_r5':>9s} {'fwd_r20':>9s} {'r20_median':>11s} {'%neg_r20':>9s}")
for b in ["<0.5","0.5-1","1-1.5","1.5-2",">2x_1Ymax"]:
    g=d[d.bin==b]
    if len(g)<30: continue
    print(f"  {b:12s} {len(g):8d} {g.r5.mean()*100:+8.1f}% {g.r20.mean()*100:+8.1f}% {g.r20.median()*100:+10.1f}% {(g.r20<0).mean()*100:8.1f}%")

# (2) MARKET-level: VNINDEX volume vs trailing-1Y max
v=bq("""SELECT t.time, t.Close, t.Volume FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX'
  AND t.time>='2010-01-01' ORDER BY t.time""")
v["time"]=pd.to_datetime(v["time"]); v=v.set_index("time").sort_index()
v["vmax1y"]=v["Volume"].rolling(252,min_periods=120).max()
v["climax"]=v["Volume"]/v["vmax1y"]
v["r5"]=v["Close"].shift(-5)/v["Close"]-1; v["r20"]=v["Close"].shift(-20)/v["Close"]-1
v["st"]=v.index.map(state); vb=v[v.st.isin([4,5])].dropna(subset=["climax","r20"])
print(f"\n(2) MARKET-level VNINDEX (bull/exbull, {len(vb)} days): volume / trailing-1Y-max")
vb=vb.copy(); vb["bin"]=pd.cut(vb["climax"],[0,0.6,0.85,1.0,100],labels=["<0.6","0.6-0.85","0.85-1.0",">=1.0(new high)"])
print(f"  {'bucket':16s} {'n':>6s} {'fwd_r5':>9s} {'fwd_r20':>9s} {'%neg_r20':>9s}")
for b in ["<0.6","0.6-0.85","0.85-1.0",">=1.0(new high)"]:
    g=vb[vb.bin==b]
    if len(g)<10: continue
    print(f"  {b:16s} {len(g):6d} {g.r5.mean()*100:+8.1f}% {g.r20.mean()*100:+8.1f}% {(g.r20<0).mean()*100:8.1f}%")
print("\nREAD: if top climax bucket fwd_r20 << baseline (or negative, high %neg) = volume blow-off = TRIM/EXIT signal.")
