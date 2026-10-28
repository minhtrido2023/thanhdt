"""Kéo giá từ PIN tav2_pin.ticker_pin_202610 (snapshot 2026-10-01T15:00:12Z) — read-only -> raw/px_pin.parquet.
Cùng tập mã/khoảng ngày với px.parquet vòng 1, chỉ đổi bảng nguồn. Chạy: $DNA_PYEXE pull_pin.py"""
import os
from google.cloud import bigquery
os.chdir(os.path.dirname(os.path.abspath(__file__)))
c = bigquery.Client(project="lithe-record-440915-m9")
q = """SELECT t.ticker, t.time, t.Close, t.Price, t.Volume FROM tav2_pin.ticker_pin_202610 AS t WHERE t.time >= '2013-09-01'
       AND t.ticker IN (SELECT DISTINCT u.ticker FROM tav2_mike.universe_pit AS u WHERE u.in_universe AND u.time >= '2013-09-01')"""
df = c.query(q).to_dataframe()
df.to_parquet("raw/px_pin.parquet", index=False)
print("px_pin", len(df), df.time.min(), df.time.max(), df.ticker.nunique())
