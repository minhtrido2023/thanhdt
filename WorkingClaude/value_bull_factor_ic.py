# -*- coding: utf-8 -*-
"""value_bull_factor_ic.py — WHAT study: factor IC + forward-return theo GIAI ĐOẠN bull (custom30B research).
User hypothesis: trong broad bull quality GIẢM nhưng profit cao; "khi tất cả tăng nhất là cổ nhỏ/junk tăng mạnh
= thời điểm nên SỢ HÃI" (euphoria top). Test: IC từng factor + mean forward-r3 trong các bucket:
  NEUTRAL(3) | BULL4_broad (state4 & breadth>=0.60) | BULL4_narrow (state4 & breadth<0.50) | EXBULL5(state5, late)
Factors: value(1/PE), quality(FSCORE,ROE_Min5Y), junk/penny(1/Close), momentum(MA200), pb_z, bounce(C_L1M).
Đọc: (a) quality IC tụt/âm trong broad bull? (b) junk/penny IC dương broad bull rồi ĐẢO/forward-sụp ở EXBULL?
(c) mean forward-r3 ở EXBULL THẤP dù mọi thứ đang tăng = 'be fearful' xác nhận. Base-state để đủ mẫu bull."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude"); os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq

# 1. breadth per date (% above MA200, ticker_prune)
br = bq("""SELECT time, AVG(CASE WHEN MA200>0 AND Close<MA200 THEN 0.0 ELSE 1.0 END) AS breadth
FROM tav2_bq.ticker_prune WHERE time>='2010-01-01' AND MA200>0 GROUP BY time""")
br["time"]=pd.to_datetime(br["time"]); breadth=br.set_index("time")["breadth"].sort_index()

# 2. state per date (base v3.4b, 2000+ for sample size)
st=bq("SELECT time, state FROM tav2_bq.vnindex_5state WHERE time>='2010-01-01'")
st["time"]=pd.to_datetime(st["time"]); state=st.set_index("time")["state"]
state=state[~state.index.duplicated(keep="last")].sort_index()

# 3. factor panel month-end (ticker_prune, NO quality pre-filter — phải gồm junk để test)
q="""WITH base AS (
  SELECT ticker, time, Close, PE, FSCORE, ROE_Min5Y, C_L1M,
    SAFE_DIVIDE(PB-PB_MA5Y, NULLIF(PB_SD5Y,0)) AS pbz,
    SAFE_DIVIDE(Close, NULLIF(MA200,0))-1 AS mom200,
    LEAD(Close,21)  OVER w AS c1, LEAD(Close,63) OVER w AS c3,
    ROW_NUMBER() OVER (PARTITION BY ticker, FORMAT_DATE('%Y-%m',time) ORDER BY time DESC) AS rn
  FROM tav2_bq.ticker_prune WHERE time>='2010-01-01' AND Close>0
  WINDOW w AS (PARTITION BY ticker ORDER BY time))
SELECT time, ticker, SAFE_DIVIDE(1.0,PE) AS ey, FSCORE, ROE_Min5Y, C_L1M, pbz, mom200,
  SAFE_DIVIDE(1.0,Close) AS inv_price, SAFE_DIVIDE(c1,Close)-1 AS r1, SAFE_DIVIDE(c3,Close)-1 AS r3
FROM base WHERE rn=1 AND c3 IS NOT NULL"""
d=bq(q); d["time"]=pd.to_datetime(d["time"])
d["st"]=d["time"].map(state); d["bd"]=d["time"].map(breadth.reindex(d["time"].unique(),method="ffill").to_dict()) \
    if False else d["time"].map(breadth.to_dict())
d["bd"]=d["time"].map(breadth.to_dict())
d=d.dropna(subset=["st","bd"])
print(f"panel {len(d):,} obs, {d['ticker'].nunique()} tickers, {d['time'].min().date()}->{d['time'].max().date()}")

def bucket(r):
    s,b=r["st"],r["bd"]
    if s==3: return "NEUTRAL"
    if s==4 and b>=0.60: return "BULL4_broad"
    if s==4 and b<0.50:  return "BULL4_narrow"
    if s==5: return "EXBULL5"
    return None
d["bkt"]=d.apply(bucket,axis=1); d=d[d["bkt"].notna()]
d["_ym"]=d["time"].dt.to_period("M")

def spear(a,b):
    m=a.notna()&b.notna()
    return a[m].rank().corr(b[m].rank()) if m.sum()>=15 else np.nan
facs={"value(1/PE)":"ey","quality(FSCORE)":"FSCORE","quality(ROE_Min5Y)":"ROE_Min5Y",
      "junk/penny(1/Close)":"inv_price","momentum(MA200)":"mom200","pb_z(cheap)":"pbz","bounce(C_L1M)":"C_L1M"}
bkts=["NEUTRAL","BULL4_broad","EXBULL5","BULL4_narrow"]
# sign: pb_z lower=cheaper -> test -pbz so + = cheap predictive
d["pbz"]=-d["pbz"]; d["inv_price_s"]=d["inv_price"]
print(f"\nbucket months/obs:")
for bk in bkts:
    sub=d[d["bkt"]==bk]; print(f"  {bk:14s} {sub['_ym'].nunique():3d} months  {len(sub):6d} obs  "
          f"mean_fwd_r3 {sub['r3'].mean()*100:+5.1f}%")
print(f"\n{'factor (IC fwd-3m)':22s} " + "".join(f"{bk:>14s}" for bk in bkts))
for nm,c in facs.items():
    line=[]
    for bk in bkts:
        sub=d[d["bkt"]==bk]
        ics=[spear(g[c],g["r3"]) for _,g in sub.groupby("_ym")]; ics=[x for x in ics if x==x]
        line.append(np.mean(ics) if ics else np.nan)
    print(f"{nm:22s} " + "".join(f"{v:+14.3f}" for v in line))
print("\nĐỌC: quality IC tụt ở BULL4_broad/EXBULL? junk/penny IC dương broad rồi forward-r3 SỤP ở EXBULL = 'be fearful'.")
