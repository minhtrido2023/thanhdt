"""Pull VNINDEX daily + universe panel monthly autocorr sufficient-stats from BigQuery.
Vintage: run date 2026-09-10. Sources (data_registry checked):
  tav2_bq.ticker            CANONICAL (price-volume/ticker_ohlcv_tables.md)
  tav2_mike.universe_pit    CANONICAL (price-volume/universe_pit.md)
Uses Close (dividend/split-adjusted) — correct basis for RETURN calcs per
coding_guidelines §quant-research #9 (adjusted price for returns, raw Price for selection).
"""
import os, sys
from google.cloud import bigquery

D = os.path.dirname(os.path.abspath(__file__))
client = bigquery.Client(project="lithe-record-440915-m9")

for name, out in [("q1_vnindex", "vnindex_daily.csv"), ("q2_panel", "panel_ac_stats.csv")]:
    sql = open(os.path.join(D, name + ".sql")).read()
    job = client.query(sql, location="asia-southeast1")
    df = job.result().to_dataframe()
    df.to_csv(os.path.join(D, out), index=False)
    print(f"{name} -> {out}: {len(df):,} rows, {df.shape[1]} cols, bytes_billed={job.total_bytes_billed:,}")
