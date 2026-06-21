"""Test kết nối BigQuery - chạy script này để kiểm tra"""
from google.cloud import bigquery

client = bigquery.Client(project="lithe-record-440915-m9")

query = """
SELECT
    COUNT(*) as total_rows,
    MIN(time) as date_min,
    MAX(time) as date_max,
    COUNT(DISTINCT ticker) as total_tickers
FROM tav2_bq.ticker AS t
"""

print("Đang kết nối BigQuery...")
result = client.query(query).result()
for row in result:
    print(f"Tổng rows: {row.total_rows:,}")
    print(f"Ngày đầu: {row.date_min}")
    print(f"Ngày cuối: {row.date_max}")
    print(f"Số tickers: {row.total_tickers}")

print("\nKết nối BigQuery OK!")
input("\nNhấn Enter để đóng...")
