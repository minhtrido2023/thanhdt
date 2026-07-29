"""Fetch du lieu cho khung dinh gia co ban (CAPE / ERP / EV-EBITDA) + breadth CAPIT.
Cong thuc giu DUNG cach da cong bo o Phu luc B: mcap=Price*OShares, book=BVPS*OShares,
earn=mcap/PE. Them EVEB (EV/EBITDA) va PS.
"""
import pandas as pd
from google.cloud import bigquery
EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
c = bigquery.Client(project='lithe-record-440915-m9')

SQL_PANEL = """
WITH base AS (
  SELECT t.time, t.ticker,
         t.Price*t.OShares AS mcap,
         t.BVPS*t.OShares  AS book,
         SAFE_DIVIDE(t.Price*t.OShares, t.PE) AS earn,
         t.PB, t.PE, t.EVEB, t.PCF, t.EBITDA_P0
  FROM `lithe-record-440915-m9.tav2_bq.ticker` t
  WHERE t.time>='2007-01-01' AND t.ticker!='VNINDEX'
    AND t.OShares>0 AND t.Price>0
)
SELECT * FROM base
QUALIFY ROW_NUMBER() OVER (PARTITION BY time ORDER BY mcap DESC) <= 150
"""

SQL_BREADTH = """
SELECT p.time,
       AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) AS oversold,
       COUNT(*) AS n
FROM `lithe-record-440915-m9.tav2_bq.ticker_prune` p
WHERE p.time >= DATE '2008-01-01' AND p.Close_T1 > 0
GROUP BY p.time ORDER BY p.time
"""

SQL_VNI = """
SELECT t.time, t.Close, t.VNINDEX_PE
FROM `lithe-record-440915-m9.tav2_bq.ticker` t
WHERE t.ticker='VNINDEX' AND t.time>='2000-01-01' ORDER BY t.time
"""

for n, s in [('panel150', SQL_PANEL), ('breadth_prune', SQL_BREADTH), ('vni', SQL_VNI)]:
    j = c.query(s); df = j.result().to_dataframe()
    df['time'] = pd.to_datetime(df['time'])
    df.to_parquet(EXP + n + '.parquet', index=False)
    print(n, df.shape, '%.2f GB billed' % (j.total_bytes_billed/1e9))
