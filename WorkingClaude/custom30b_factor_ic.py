# -*- coding: utf-8 -*-
"""custom30b_factor_ic.py — improve custom30B selection: which MOMENTUM/VOLUME-SURGE factors add IC
on top of 1/PE IN BULL, and does a LOWER liquidity floor (2B vs 10B) open better opportunities?
Month-end panel from ticker_prune, fwd-3m return. Buckets: NEUTRAL(3) / BULL4_broad(state4 & breadth>=.60)
/ EXBULL5(5). Reports: (A) per-factor IC + combo ey+factor IC vs ey-alone baseline (+0.161 in broad bull);
(B) liquidity-tier split (<2B / 2-10B / >10B): fwd-r3 mean + 1/PE IC per tier -> does low-liq help or junk?"""
import os, numpy as np, pandas as pd
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq

br = bq("""SELECT time, AVG(CASE WHEN MA200>0 AND Close<MA200 THEN 0.0 ELSE 1.0 END) AS breadth
FROM tav2_bq.ticker_prune WHERE time>='2010-01-01' AND MA200>0 GROUP BY time""")
br["time"]=pd.to_datetime(br["time"]); breadth=br.set_index("time")["breadth"].sort_index()
st=bq("SELECT time, state FROM tav2_bq.vnindex_5state WHERE time>='2010-01-01'")
st["time"]=pd.to_datetime(st["time"]); state=st.set_index("time")["state"]
state=state[~state.index.duplicated(keep="last")].sort_index()

q="""WITH base AS (
  SELECT ticker, time, Close, PE, Volume, Volume_1M, Volume_3M_P50, Volume_3M_P90,
    Volume_Max1Y_High, MA50, MA200, D_RSI, D_MACDdiff, D_CMF, D_MFI, C_L1M,
    LEAD(Close,63) OVER w AS c3,
    ROW_NUMBER() OVER (PARTITION BY ticker, FORMAT_DATE('%Y-%m',time) ORDER BY time DESC) AS rn
  FROM tav2_bq.ticker_prune WHERE time>='2010-01-01' AND Close>0
  WINDOW w AS (PARTITION BY ticker ORDER BY time))
SELECT time, ticker,
  SAFE_DIVIDE(1.0,PE) AS ey,
  SAFE_DIVIDE(Volume_1M, NULLIF(Volume_3M_P50,0)) AS volsurge,        -- recent vs medium vol
  SAFE_DIVIDE(Volume, NULLIF(Volume_3M_P90,0))    AS vol_p90,         -- today vs 3M-P90 (spike)
  SAFE_DIVIDE(Volume_1M, NULLIF(Volume_Max1Y_High,0)) AS vol_max1y,   -- recent vs 1Y peak day
  SAFE_DIVIDE(Close, NULLIF(MA50,0))-1  AS mom50,
  SAFE_DIVIDE(Close, NULLIF(MA200,0))-1 AS mom200,
  D_RSI AS rsi, D_MACDdiff AS macd, D_CMF AS cmf, D_MFI AS mfi, C_L1M,
  Volume_3M_P50*Close AS liq,
  SAFE_DIVIDE(c3,Close)-1 AS r3
FROM base WHERE rn=1 AND c3 IS NOT NULL"""
d=bq(q); d["time"]=pd.to_datetime(d["time"])
d["st"]=d["time"].map(state); d["bd"]=d["time"].map(breadth.to_dict())
d=d.dropna(subset=["st","bd"])
def bucket(r):
    s,b=r["st"],r["bd"]
    if s==3: return "NEUTRAL"
    if s==4 and b>=0.60: return "BULL4_broad"
    if s==5: return "EXBULL5"
    return None
d["bkt"]=d.apply(bucket,axis=1); d=d[d["bkt"].notna()]; d["_ym"]=d["time"].dt.to_period("M")
print(f"panel {len(d):,} obs, {d['ticker'].nunique()} tickers")

def spear(a,b):
    m=a.notna()&b.notna()
    return a[m].rank().corr(b[m].rank()) if m.sum()>=15 else np.nan
def ic_by(sub,col):
    ics=[spear(g[col],g["r3"]) for _,g in sub.groupby("_ym")]; ics=[x for x in ics if x==x]
    return np.mean(ics) if ics else np.nan
def ic_combo(sub,c1,c2):  # equal rank-sum of two factors, per-month IC
    ics=[]
    for _,g in sub.groupby("_ym"):
        s=g[c1].rank(pct=True).fillna(.5)+g[c2].rank(pct=True).fillna(.5)
        ics.append(spear(s,g["r3"]))
    ics=[x for x in ics if x==x]; return np.mean(ics) if ics else np.nan

facs=["volsurge","vol_p90","vol_max1y","mom50","mom200","rsi","macd","cmf","mfi","C_L1M"]
bkts=["NEUTRAL","BULL4_broad","EXBULL5"]
print("\n(A) FACTOR IC (fwd-3m) and COMBO ey+factor IC  [baseline ey-alone in brackets]")
print(f"{'factor':12s} "+"".join(f"{b:>26s}" for b in bkts))
ey_ic={b:ic_by(d[d.bkt==b],"ey") for b in bkts}
print(f"{'ey(1/PE)':12s} "+"".join(f"{ey_ic[b]:+12.3f}{'':14s}" for b in bkts))
print(f"{'  -> combos: factorIC | comboIC(ey+factor) vs ey-alone='}{ {b:round(ey_ic[b],3) for b in bkts} }")
for f in facs:
    cells=[]
    for b in bkts:
        sub=d[d.bkt==b]; fi=ic_by(sub,f); ci=ic_combo(sub,"ey",f)
        cells.append(f"{fi:+7.3f}|{ci:+7.3f}({ci-ey_ic[b]:+.3f})")
    print(f"{f:12s} "+"".join(f"{c:>26s}" for c in cells))

print("\n(B) LIQUIDITY-TIER split (BULL4_broad + EXBULL5 combined): does lowering floor help or add junk?")
sub=d[d.bkt.isin(["BULL4_broad","EXBULL5"])].copy()
sub["tier"]=pd.cut(sub["liq"],[0,2e9,10e9,1e15],labels=["<2B","2-10B",">10B"])
for t in ["<2B","2-10B",">10B"]:
    g=sub[sub.tier==t]
    print(f"  liq {t:6s} n{len(g):6d}  fwd_r3 mean {g['r3'].mean()*100:+6.1f}%  median {g['r3'].median()*100:+6.1f}%  "
          f"ey_IC {ic_by(g,'ey'):+.3f}  volsurge_IC {ic_by(g,'volsurge'):+.3f}  std {g['r3'].std()*100:5.1f}%")
print("\nREAD (A): combo delta >0 = factor adds on top of 1/PE in bull. (B): low-liq higher mean BUT check std (junk=fat tail) + IC holds.")
