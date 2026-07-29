"""Keo per-ticker top-100 mcap moi phien (2008+) de tinh lai PB thi truong
theo nhieu phuong phap (cap-weighted, ex-VIC, capped 10%, EW median, trimmed).
Universe PB = PB>0, OShares>0, Price>0 (khop cach dung o agg_pepb.csv).
"""
import pandas as pd
from google.cloud import bigquery

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pb_exvic/'
c = bigquery.Client(project='lithe-record-440915-m9')

SQL_T100 = """
WITH base AS (
  SELECT t.time, t.ticker,
         t.Price * t.OShares AS mcap,
         SAFE_DIVIDE(t.Price * t.OShares, t.PB) AS book,
         SAFE_DIVIDE(t.Price * t.OShares, t.PE) AS earn,
         t.PB, t.PE
  FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
  WHERE t.time >= '2008-01-01'
    AND t.ticker != 'VNINDEX'
    AND t.PB > 0 AND t.OShares > 0 AND t.Price > 0
)
SELECT * FROM base
QUALIFY ROW_NUMBER() OVER (PARTITION BY time ORDER BY mcap DESC) <= 100
"""

SQL_ALL = """
WITH pb AS (
  SELECT t.time, t.ticker, t.Price*t.OShares AS mcap,
         SAFE_DIVIDE(t.Price*t.OShares, t.PB) AS book
  FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
  WHERE t.time >= '2008-01-01' AND t.ticker != 'VNINDEX'
    AND t.PB > 0 AND t.OShares > 0 AND t.Price > 0
), pe AS (
  SELECT t.time, t.ticker, t.Price*t.OShares AS mcap,
         SAFE_DIVIDE(t.Price*t.OShares, t.PE) AS earn
  FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
  WHERE t.time >= '2008-01-01' AND t.ticker != 'VNINDEX'
    AND t.PE > 0 AND t.OShares > 0 AND t.Price > 0
)
SELECT COALESCE(a.time,b.time) AS time,
  a.mcap_all, a.book_all, a.n_pb, a.mcap_ex, a.book_ex,
  b.mcap_pe_all, b.earn_all, b.n_pe, b.mcap_pe_ex, b.earn_ex
FROM (
  SELECT time, SUM(mcap) mcap_all, SUM(book) book_all, COUNT(*) n_pb,
         SUM(IF(ticker='VIC',0,mcap)) mcap_ex, SUM(IF(ticker='VIC',0,book)) book_ex
  FROM pb GROUP BY time) a
FULL JOIN (
  SELECT time, SUM(mcap) mcap_pe_all, SUM(earn) earn_all, COUNT(*) n_pe,
         SUM(IF(ticker='VIC',0,mcap)) mcap_pe_ex, SUM(IF(ticker='VIC',0,earn)) earn_ex
  FROM pe GROUP BY time) b
USING (time)
ORDER BY time
"""

for name, sql in [('t100_panel', SQL_T100), ('agg_all', SQL_ALL)]:
    job = c.query(sql)
    df = job.result().to_dataframe()
    print(name, df.shape, 'bytes billed=%.2f GB' % (job.total_bytes_billed / 1e9))
    df.to_parquet(EXP + name + '.parquet', index=False)
