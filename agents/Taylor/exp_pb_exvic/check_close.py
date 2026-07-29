import pandas as pd
from google.cloud import bigquery
c=bigquery.Client(project='lithe-record-440915-m9')
sql="""
WITH pb AS (
  SELECT t.time, t.ticker, t.Close*t.OShares AS mcap, SAFE_DIVIDE(t.Close*t.OShares,t.PB) AS book
  FROM `lithe-record-440915-m9.tav2_bq.ticker` t
  WHERE t.time>='2008-01-01' AND t.ticker!='VNINDEX' AND t.PB>0 AND t.OShares>0 AND t.Close>0)
SELECT time, SUM(mcap)/SUM(book) AS pb_all_close, COUNT(*) n FROM pb GROUP BY time ORDER BY time
"""
df=c.query(sql).result().to_dataframe(); df['time']=pd.to_datetime(df.time)
old=pd.read_csv('/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/agg_pepb.csv',parse_dates=['time'])
old['pb_all_old']=old.mcap_pb_all/old.book_all
m=df.merge(old[['time','pb_all_old','n_pb_all']],on='time')
print('close-based vs old: corr=%.8f max|diff|=%.3e  n match=%s'%(m.pb_all_close.corr(m.pb_all_old),
  (m.pb_all_close-m.pb_all_old).abs().max(), (m.n==m.n_pb_all).mean()))
print(m.head(3).to_string(index=False)); print(m.tail(2).to_string(index=False))
