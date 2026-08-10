#!/usr/bin/env python3
"""Pull daily bars for the LAG/BAL/PARK buy-candidate universe (from the last ~2 months of
golive recommendation CSVs) to calibrate an intraday buy circuit-breaker threshold.

READ-ONLY. Writes one non-canonical CSV into this experiment dir (guidelines §8).
"""
import csv, glob, os, sys
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "secrets/sa-key.json")
from google.cloud import bigquery

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "bars_universe.csv")

books = {}
for p in sorted(glob.glob('deploy_golive_dt5g_v4/out/golive_v23_recommendations_*.csv')):
    for r in csv.DictReader(open(p)):
        t = (r.get('ticker') or '').strip()
        b = (r.get('book') or '').strip()
        if t:
            books.setdefault(t, set()).add(b)
tickers = sorted(books)
print(f"universe: {len(tickers)} tickers", file=sys.stderr)

c = bigquery.Client(project='lithe-record-440915-m9')
q = """
SELECT t.ticker, t.time, t.Open, t.High, t.Low, t.Close, t.Price, t.Volume
FROM tav2_bq.ticker AS t
WHERE t.ticker IN UNNEST(@tk) AND t.time >= '2023-01-01' AND t.time <= '2026-08-07'
ORDER BY t.ticker, t.time
"""
job = c.query(q, job_config=bigquery.QueryJobConfig(
    query_parameters=[bigquery.ArrayQueryParameter("tk", "STRING", tickers)]))
n = 0
with open(OUT, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(["ticker", "time", "open", "high", "low", "close", "price", "volume", "books"])
    for r in job.result():
        w.writerow([r.ticker, r.time, r.Open, r.High, r.Low, r.Close, r.Price, r.Volume,
                    "|".join(sorted(books.get(r.ticker, ())))])
        n += 1
print(f"wrote {n} rows -> {OUT}", file=sys.stderr)
