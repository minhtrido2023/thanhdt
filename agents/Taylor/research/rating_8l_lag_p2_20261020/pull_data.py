"""Kéo dữ liệu thô cho Phần 2 (read-only BQ) -> raw/*.parquet. Chạy: $DNA_PYEXE pull_data.py"""
from google.cloud import bigquery
P = "lithe-record-440915-m9"
c = bigquery.Client(project=P)
Q = {
 "fa": "SELECT ticker, time, route, rating FROM tav2_bq.fa_ratings_8l",
 "tf": "SELECT ticker, quarter, time, Release_Date FROM tav2_bq.ticker_financial WHERE time >= '2013-01-01'",
 "univ": "SELECT ticker, time FROM tav2_mike.universe_pit WHERE in_universe AND time >= '2013-09-01'",
 "px": """SELECT t.ticker, t.time, t.Close, t.Price FROM tav2_bq.ticker AS t WHERE t.time >= '2013-09-01'
          AND t.ticker IN (SELECT DISTINCT u.ticker FROM tav2_mike.universe_pit AS u WHERE u.in_universe AND u.time >= '2013-09-01')""",
}
import os, sys
for k, q in Q.items():
    if os.path.exists(f'raw/{k}.parquet') and '--force' not in sys.argv: continue
    df = c.query(q).to_dataframe()
    df.to_parquet(f"raw/{k}.parquet", index=False)
    print(k, len(df), df.time.min(), df.time.max())
