"""Compute get_macro_state() for the FULL 2008-01-01 -> AUDIT_END window (single continuous call,
so IS and OOS share one state series, per dispatch job Taylor_20260825_055651 Step 2 instruction)
and write it to a non-canonical temp BQ table so engine_p1.py's SQL (which JOINs against a
STATE_TABLE name) can consume it unchanged. NOT touching vnindex_5state_dt5g_live (production).
"""
import sys, os
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.chdir("/home/trido/thanhdt/WorkingClaude")
import pandas as pd
from google.cloud import bigquery
from macro_state_live import get_macro_state

AUDIT_START = "2008-01-01"
AUDIT_END = "2026-08-24"
PROJECT = "lithe-record-440915-m9"
TABLE = f"{PROJECT}.tav2_bq.taylor_exp_dt5g_recompute_2008_2026_20260825"

df = get_macro_state(start=AUDIT_START, end=AUDIT_END)
df["time"] = pd.to_datetime(df["time"]).dt.date
out = df[["time", "state"]].copy()
out["state"] = out["state"].astype("int64")
print(f"Rows: {len(out)}  range {out['time'].min()} -> {out['time'].max()}")
print(out["state"].value_counts())

client = bigquery.Client(project=PROJECT)
job_config = bigquery.LoadJobConfig(
    schema=[
        bigquery.SchemaField("time", "DATE"),
        bigquery.SchemaField("state", "INT64"),
    ],
    write_disposition="WRITE_TRUNCATE",
)
job = client.load_table_from_dataframe(out, TABLE, job_config=job_config)
job.result()
print(f"Loaded {job.output_rows} rows into {TABLE}")

# verify
chk = client.query(f"SELECT COUNT(*) n, MIN(time) mn, MAX(time) mx FROM `{TABLE}`").to_dataframe()
print(chk)
