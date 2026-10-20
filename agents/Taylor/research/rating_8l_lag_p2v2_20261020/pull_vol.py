"""Kéo Price×Volume cho ADV (read-only BQ) -> raw/vol.parquet. Chạy: $DNA_PYEXE pull_vol.py"""
from google.cloud import bigquery
c = bigquery.Client(project="lithe-record-440915-m9")
q = """SELECT t.ticker, t.time, t.Price, t.Volume FROM tav2_bq.ticker AS t WHERE t.time >= '2013-09-01'
       AND t.ticker IN (SELECT DISTINCT u.ticker FROM tav2_mike.universe_pit AS u WHERE u.in_universe AND u.time >= '2013-09-01')"""
df = c.query(q).to_dataframe()
df.to_parquet("raw/vol.parquet", index=False)
print("vol", len(df), df.time.min(), df.time.max())
