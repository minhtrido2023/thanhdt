"""Pull full-universe Close/Volume/PB panel 2006-04-01..2023-05-09 (covers all 7 dd52<=-20%
episodes + lookback for pre-crisis peak calc). CLAUDE.md trap #2: table name == column name
`ticker` -> MUST alias table + qualify columns, else `ticker` resolves to the whole-row STRUCT."""
import time
from google.cloud import bigquery

t0 = time.time()
client = bigquery.Client(project="lithe-record-440915-m9")

q = """
SELECT t.ticker AS ticker, t.time AS time, t.Close AS Close, t.Volume AS Volume, t.PB AS PB
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN "2006-04-01" AND "2023-05-09"
  AND t.Volume > 0
"""
job = client.query(q)
result = job.result()
print(f"query done in {time.time()-t0:.1f}s, rows={result.total_rows}", flush=True)

t1 = time.time()
df = job.to_dataframe(create_bqstorage_client=True)
print(f"fetch done in {time.time()-t1:.1f}s, shape={df.shape}, cols={list(df.columns)}", flush=True)
import pandas as pd
df["time"] = pd.to_datetime(df["time"].astype(str))
df.to_parquet("full_panel.parquet", index=False)
print(f"total {time.time()-t0:.1f}s", flush=True)
