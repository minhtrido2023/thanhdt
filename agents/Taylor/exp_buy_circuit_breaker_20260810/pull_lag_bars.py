#!/usr/bin/env python3
"""Bars for every ticker traded by the LAG book in the pinned R3 audit (PIT event set)."""
import os, sys, csv
import pandas as pd
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "secrets/sa-key.json")
from google.cloud import bigquery

WC = "/home/trido/thanhdt/WorkingClaude"
AUD = os.path.join(WC, "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
                       "etfliqcustompitg_wtnamecap_liquncap_advprice_exp_cap50b_ideal_univpit.csv")
d = pd.read_csv(AUD, low_memory=False)
tx = d[(d.record_type == "TX")]
tk = sorted(tx.ticker.dropna().unique())
print(f"{len(tk)} tickers, {len(tx)} TX rows", file=sys.stderr)

c = bigquery.Client(project="lithe-record-440915-m9")
q = """SELECT t.ticker,t.time,t.Open,t.High,t.Low,t.Close,t.Volume
       FROM tav2_bq.ticker AS t
       WHERE t.ticker IN UNNEST(@tk) AND t.time >= '2013-06-01'
       ORDER BY t.ticker,t.time"""
job = c.query(q, job_config=bigquery.QueryJobConfig(
    query_parameters=[bigquery.ArrayQueryParameter("tk", "STRING", tk)]))
n = 0
with open("bars_lag_audit.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["ticker", "time", "open", "high", "low", "close", "volume"])
    for r in job.result():
        w.writerow([r.ticker, r.time, r.Open, r.High, r.Low, r.Close, r.Volume]); n += 1
print(f"wrote {n} rows", file=sys.stderr)
