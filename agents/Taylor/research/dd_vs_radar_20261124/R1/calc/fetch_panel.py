"""Fetch monthly-end panel (all tickers) 2007+ from tav2_bq.ticker + universe_pit. Writes panel_monthly.parquet."""
import sys
from google.cloud import bigquery
sql = open("panel.sql").read()
c = bigquery.Client(project="lithe-record-440915-m9")
dr = c.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
print("dry_run GB", dr.total_bytes_processed / 1e9, flush=True)
if "--dry" in sys.argv: sys.exit(0)
df = c.query(sql).result(timeout=900).to_dataframe()
import pandas as pd
df["time"] = pd.to_datetime(df["time"].astype(str))  # dbdate -> datetime64 (bước đã làm tay 24/11, nay đưa vào script)
df.to_parquet("panel_monthly.parquet", index=False)
print(len(df), df.time.min(), df.time.max(), df.ticker.nunique())
