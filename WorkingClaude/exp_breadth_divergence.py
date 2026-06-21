# -*- coding: utf-8 -*-
"""Leading-IC + event study of BREADTH-DIVERGENCE as a reversal signal (research-only).
Breadth = % of ticker_prune with Close>MA200 (causal). Bearish divergence = index rising
while breadth deteriorating (e.g. 2025 VIC-led). Measure: (1) leading IC of breadth level
& momentum vs forward VNINDEX return; (2) conditional fwd returns under bearish divergence;
(3) complementarity with BearDvg fires (does it catch DIFFERENT reversals?).
Data 2014+ (ticker_prune coverage). All features causal (T-1 lag). NO deploy."""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq

print("[1] breadth from ticker_prune + VNINDEX...")
bd = bq("""SELECT t.time, AVG(IF(t.Close>t.MA200,1.0,0.0)) AS breadth, COUNT(*) AS univ
FROM tav2_bq.ticker_prune AS t WHERE t.MA200 IS NOT NULL AND t.time>=DATE '2014-01-01'
GROUP BY t.time ORDER BY t.time""")
bd["time"]=pd.to_datetime(bd["time"])
px = bq("""SELECT p.time, p.Close FROM tav2_bq.ticker AS p WHERE p.ticker='VNINDEX' AND p.time>=DATE '2014-01-01' ORDER BY p.time""")
px["time"]=pd.to_datetime(px["time"])
d = px.merge(bd, on="time", how="inner").sort_values("time").reset_index(drop=True)
d = d[d["univ"]>=100].reset_index(drop=True)
c=d["Close"].values; b=d["breadth"].values; n=len(d)
print(f"  {n} sessions {d['time'].iloc[0].date()}->{d['time'].iloc[-1].date()}  breadth {np.nanmin(b):.2f}-{np.nanmax(b):.2f}")

def chg(a,k): o=np.full(len(a),np.nan); o[k:]=a[k:]-a[:-k]; return o
def ret(a,k): o=np.full(len(a),np.nan); o[k:]=a[k:]/a[:-k]-1; return o
d["br_lvl"]=b
d["br_chg20"]=chg(b,20); d["br_chg60"]=chg(b,60)
d["px_chg20"]=ret(c,20); d["px_chg60"]=ret(c,60)
# bearish divergence magnitude: price up but breadth down (price_ret - breadth-implied)
d["diverg"]=d["px_chg20"] - (d["br_chg20"])   # high when price rises & breadth falls
# forward returns
def fwd(k): o=np.full(n,np.nan); o[:n-k]=c[k:]/c[:n-k]-1; return o
for h in (20,60,120): d[f"f{h}"]=fwd(h)
# causal lag features by 1 session
for col in ["br_lvl","br_chg20","br_chg60","px_chg20","diverg"]: d[col+"_L"]=d[col].shift(1)

def ic(x,y):
    s=pd.concat([x,y],axis=1).dropna(); return s.corr("spearman").iloc[0,1] if len(s)>50 else np.nan
print("\n[2] Leading IC (Spearman, causal features vs forward VNINDEX return)")
print(f"  {'feature':16s}{'f20':>9s}{'f60':>9s}{'f120':>9s}")
for col,desc in [("br_lvl_L","breadth level"),("br_chg20_L","breadth chg20"),("br_chg60_L","breadth chg60"),
                 ("diverg_L","px-breadth diverg")]:
    print(f"  {desc:16s}"+"".join(f"{ic(d[col],d[f'f{h}']):>9.3f}" for h in (20,60,120)))

print("\n[3] Forward return conditioned on BEARISH DIVERGENCE")
print("    (price_chg20>0 = index up, while breadth_chg20<thr = participation shrinking)")
dd=d.dropna(subset=["px_chg20_L","br_chg20","f60","f120"]).copy()
for thr in (0.0,-0.05,-0.10):
    g=dd[(dd["px_chg20_L"]>0)&(dd["br_chg20"].shift(1)<thr)]
    if len(g)<20: print(f"    breadth_chg20<{thr:+.2f}: n={len(g)} (too few)"); continue
    print(f"    diverg (px↑ & br_chg20<{thr:+.2f}): n={len(g):4d}  fwd60 {g['f60'].mean()*100:+5.1f}%  fwd120 {g['f120'].mean()*100:+5.1f}%  P(f60<0) {(g['f60']<0).mean()*100:.0f}%")
allf60=dd["f60"].mean()*100; allf120=dd["f120"].mean()*100
print(f"    [baseline all]:                n={len(dd):4d}  fwd60 {allf60:+5.1f}%  fwd120 {allf120:+5.1f}%  P(f60<0) {(dd['f60']<0).mean()*100:.0f}%")

print("\n[4] Low-breadth-level regime (participation already weak)")
for lo,hi,lbl in [(0.0,0.30,"breadth<30%"),(0.30,0.50,"30-50%"),(0.50,0.70,"50-70%"),(0.70,1.01,">70%")]:
    g=dd[(dd["br_lvl_L"]>=lo)&(dd["br_lvl_L"]<hi)]
    if len(g)<20: continue
    print(f"    {lbl:12s} n={len(g):4d}  fwd60 {g['f60'].mean()*100:+5.1f}%  fwd120 {g['f120'].mean()*100:+5.1f}%")
print("\nDONE.")
