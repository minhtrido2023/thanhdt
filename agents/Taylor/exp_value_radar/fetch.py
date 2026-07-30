"""Value Radar - keo panel. Giu NGUYEN dinh nghia Phu luc B:
mcap=Price*OShares, book=BVPS*OShares, earn=mcap/PE (== NP_ttm, dong nhat thuc).
Ro chuan = top-N von hoa moi phien trong so ma co OShares>0, Price>0.
Floor 2008-01-01 (quy uoc data_registry/price-volume/vnindex_pe_mirror_col.md).
"""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd
from google.cloud import bigquery
EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_value_radar/'
c = bigquery.Client(project='lithe-record-440915-m9')

# A) panel top-300 von hoa moi phien (du de cat top-100/250 + tach nganh)
SQL_A = """
WITH base AS (
  SELECT t.time, t.ticker, t.ICB_Code,
         t.Price*t.OShares AS mcap,
         t.BVPS*t.OShares  AS book,
         SAFE_DIVIDE(t.Price*t.OShares, t.PE) AS earn,
         t.PB, t.PE, t.NP_P0, t.NP_P1, t.NP_P2, t.NP_P3, t.NP_P4
  FROM `lithe-record-440915-m9.tav2_bq.ticker` t
  WHERE t.time >= '2008-01-01' AND t.ticker != 'VNINDEX'
    AND t.OShares > 0 AND t.Price > 0
)
SELECT * FROM base
QUALIFY ROW_NUMBER() OVER (PARTITION BY time ORDER BY mcap DESC) <= 300
"""

# B) tong hop TOAN universe moi phien (breadth PB<1 + aggregate + tach ngan hang)
SQL_B = """
WITH base AS (
  SELECT t.time, t.ticker,
         IF(t.ICB_Code = 8355, 1, 0) AS is_bank,
         t.Price*t.OShares AS mcap,
         t.BVPS*t.OShares  AS book,
         SAFE_DIVIDE(t.Price*t.OShares, t.PE) AS earn,
         t.PB, t.PE
  FROM `lithe-record-440915-m9.tav2_bq.ticker` t
  WHERE t.time >= '2008-01-01' AND t.ticker != 'VNINDEX'
    AND t.OShares > 0 AND t.Price > 0
)
SELECT time,
  COUNT(*)                                   AS n_rows,
  COUNTIF(PB > 0)                            AS n_pb_pos,
  COUNTIF(PB > 0 AND PB < 1)                 AS n_pb_lt1,
  COUNTIF(PE IS NOT NULL)                    AS n_pe,
  COUNTIF(PE > 0)                            AS n_pe_pos,
  SUM(IF(PB > 0, mcap, 0))                   AS mcap_pb,
  SUM(IF(PB > 0, book, 0))                   AS book_pb,
  SUM(IF(PE IS NOT NULL, mcap, 0))           AS mcap_pe,
  SUM(earn)                                  AS earn_all,
  -- tach ngan hang / phi ngan hang (chi ro PB>0 / PE non-null)
  COUNTIF(PB > 0 AND is_bank = 1)            AS n_pb_bank,
  SUM(IF(PB > 0 AND is_bank = 1, mcap, 0))   AS mcap_pb_bank,
  SUM(IF(PB > 0 AND is_bank = 1, book, 0))   AS book_pb_bank,
  SUM(IF(PE IS NOT NULL AND is_bank = 1, mcap, 0)) AS mcap_pe_bank,
  SUM(IF(is_bank = 1, earn, 0))              AS earn_bank
FROM base GROUP BY time ORDER BY time
"""

for name, sql, fmt in [('panel300', SQL_A, 'parquet'), ('agg_universe', SQL_B, 'csv')]:
    j = c.query(sql); df = j.result().to_dataframe()
    df['time'] = pd.to_datetime(df['time'])
    if fmt == 'parquet':
        df.to_parquet(EXP + name + '.parquet', index=False)
    else:
        df.to_csv(EXP + name + '.csv', index=False)
    print(name, df.shape, '%.2f GB billed' % (j.total_bytes_billed / 1e9))
