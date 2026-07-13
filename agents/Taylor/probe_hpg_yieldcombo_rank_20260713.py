# -*- coding: utf-8 -*-
"""Reconstruct HPG's rank in the yieldcombo (custom30V) pool at rebal 2026-05-05.
Replicates custom_basket.build_pit SELECT_MODE=yieldcombo selection EXACTLY for one rebal date.
Read-only, no writes. Answers: is HPG gated out (rating/liq) or just ranked out on value-yield?"""
import os, sys, bisect
import numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq

REBAL = pd.Timestamp("2026-05-05")
SRC_Q = pd.Timestamp("2026-01-01")   # prior quarter to 2026-04-01 (Q2) => Q1 2026
END = "2026-05-05"
EFF_START = "2024-10-01"
GATE = 3; CFO_POOL = 60; TOP_N = 30
UNIVERSE_FILTER = "t.ICB_Code IS NOT NULL"

# (1) Q1-2026 liquidity (same query shape as build_pit)
qliq = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q,
  AVG(t.Volume_3M_P50*t.Close) AS liq, COUNT(*) AS nd
FROM tav2_bq.ticker t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
  AND {UNIVERSE_FILTER}
  AND t.time >= DATE '{EFF_START}' AND t.time <= DATE '{END}'
GROUP BY t.ticker, q HAVING nd >= 20""")
qliq["q"] = pd.to_datetime(qliq["q"])
liq_piv = qliq.pivot_table(index="q", columns="ticker", values="liq")
liq_row = liq_piv.loc[SRC_Q].dropna().sort_values(ascending=False)

# (2) ratings as-of REBAL
rat = bq(f"""SELECT r.ticker, r.time, r.rating FROM tav2_bq.fa_ratings_8l r
WHERE r.time <= DATE '{END}' ORDER BY r.ticker, r.time""")
rat["time"] = pd.to_datetime(rat["time"])
rat_by = {tk:(list(g["time"]),list(g["rating"])) for tk,g in rat.groupby("ticker")}
def rating_asof(tk,d):
    e=rat_by.get(tk)
    if not e: return np.nan
    i=bisect.bisect_right(e[0],d)-1
    return float(e[1][i]) if i>=0 else np.nan

# (3) yield pivots Q1-2026
def ypiv(col):
    y=bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q, AVG(SAFE_DIVIDE(1,t.{col})) AS y
FROM tav2_bq.ticker t WHERE t.{col}>0 AND t.time BETWEEN DATE '{EFF_START}' AND DATE '{END}'
GROUP BY t.ticker,q""")
    y["q"]=pd.to_datetime(y["q"]); return y.pivot_table(index="q",columns="ticker",values="y")
pe_piv=ypiv("PE"); pcf_piv=ypiv("PCF")
pe_s=pe_piv.loc[SRC_Q] if SRC_Q in pe_piv.index else None
pcf_s=pcf_piv.loc[SRC_Q] if SRC_Q in pcf_piv.index else None

# (4) gate in liquidity order
gated=[]
for tk in list(liq_row.index):
    rt=rating_asof(tk,REBAL)
    if not (pd.notna(rt) and rt<=GATE): continue
    gated.append((tk,rt))
pool=gated[:CFO_POOL]
pe_r =pd.Series({t:(pe_s.get(t,np.nan)  if pe_s  is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
pcf_r=pd.Series({t:(pcf_s.get(t,np.nan) if pcf_s is not None else np.nan) for t,_ in pool}).rank(pct=True).fillna(0.5)
score={t:pe_r[t]+pcf_r[t] for t,_ in pool}
ranked=sorted(pool,key=lambda tr:score[tr[0]],reverse=True)

pool_tickers=[t for t,_ in pool]
print(f"REBAL={REBAL.date()} SRC_Q={SRC_Q.date()} pool_size={len(pool)} (CFO_POOL={CFO_POOL})")
print(f"HPG in liquidity universe? {'HPG' in liq_row.index}  liq_rank(overall)={list(liq_row.index).index('HPG')+1 if 'HPG' in liq_row.index else 'NA'}")
print(f"HPG rating_asof(2026-05-05) = {rating_asof('HPG',REBAL)}  (gate<= {GATE})")
print(f"HPG in gated pool (rating<=3, top-{CFO_POOL} liq)? {'HPG' in pool_tickers}")
if 'HPG' in pool_tickers:
    hp_rank=[t for t,_ in ranked].index('HPG')+1
    print(f"HPG yieldcombo rank = {hp_rank} / {len(ranked)}  (cutoff top-{TOP_N})  --> {'IN' if hp_rank<=TOP_N else 'OUT'}")
    print(f"  HPG 1/PE avg Q1={pe_s.get('HPG'):.4f} (rank_pct={pe_r['HPG']:.3f}) | 1/PCF avg Q1={pcf_s.get('HPG'):.4f} (rank_pct={pcf_r['HPG']:.3f}) | score={score['HPG']:.3f}")
    # boundary: names at rank 28-33
    print("\n  --- boundary (rank 26..34) score=rank(1/PE)+rank(1/PCF) ---")
    for i,(t,_) in enumerate(ranked[25:34],start=26):
        mark=" <== HPG" if t=='HPG' else ""
        print(f"  {i:>2}. {t:5s} score={score[t]:.3f}  1/PE_pct={pe_r[t]:.3f} 1/PCF_pct={pcf_r[t]:.3f}{mark}")
print("\n  --- top-30 selected (yieldcombo) ---")
print("  " + ", ".join(t for t,_ in ranked[:TOP_N]))
