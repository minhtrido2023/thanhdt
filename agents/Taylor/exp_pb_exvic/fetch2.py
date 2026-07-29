"""Ban dung LAI dung cong thuc da cong bo: mcap=Price*OShares, book=BVPS*OShares, earn=EPS*OShares.
Loc: PB>0 (ro PB) / PE>0 (ro PE), OShares>0, Price>0.
"""
import pandas as pd
from google.cloud import bigquery
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pb_exvic/'
c=bigquery.Client(project='lithe-record-440915-m9')

SQL="""
WITH base AS (
  SELECT t.time, t.ticker,
         t.Price*t.OShares AS mcap,
         t.BVPS*t.OShares  AS book,
         SAFE_DIVIDE(t.Price*t.OShares, t.PE) AS earn,
         t.PB, t.PE
  FROM `lithe-record-440915-m9.tav2_bq.ticker` t
  WHERE t.time>='2008-01-01' AND t.ticker!='VNINDEX'
    AND t.PB>0 AND t.OShares>0 AND t.Price>0
)
SELECT * FROM base
QUALIFY ROW_NUMBER() OVER (PARTITION BY time ORDER BY mcap DESC) <= 100
"""
SQL_ALL="""
WITH pb AS (
  SELECT t.time,t.ticker,t.Price*t.OShares AS mcap,t.BVPS*t.OShares AS book
  FROM `lithe-record-440915-m9.tav2_bq.ticker` t
  WHERE t.time>='2008-01-01' AND t.ticker!='VNINDEX' AND t.PB>0 AND t.OShares>0 AND t.Price>0)
SELECT time, SUM(mcap) mcap_all, SUM(book) book_all, COUNT(*) n_pb,
       SUM(IF(ticker='VIC',0,mcap)) mcap_ex, SUM(IF(ticker='VIC',0,book)) book_ex
FROM pb GROUP BY time ORDER BY time
"""
for n,s in [('t100_panel2',SQL),('agg_all2',SQL_ALL)]:
    j=c.query(s); df=j.result().to_dataframe()
    df['time']=pd.to_datetime(df['time'])
    df.to_csv(EXP+n+'.csv',index=False)
    print(n,df.shape,'%.2f GB'%(j.total_bytes_billed/1e9))
