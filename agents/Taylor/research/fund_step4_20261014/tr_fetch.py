#!/usr/bin/env python3
"""Việc 1 — kéo dữ liệu THÔ (chỉ đọc BQ) cho chỉ số VN-Index có cổ tức tự dựng.
Ghi parquet vào --out (mặc định /tmp/fund_step4_tr). Không ghi gì vào data/ hay BQ.

    /home/trido/thanhdt/wc_venv/bin/python tr_fetch.py [--out DIR]
"""
import argparse
import os

from google.cloud import bigquery

PROJECT = "lithe-record-440915-m9"
Q = {
    # Price = giá THÔ, Close = giá điều chỉnh hồi tố; OShares = số CP lưu hành (trễ theo quý).
    "panel": """
        SELECT t.time, t.ticker, t.Price, t.Close, t.OShares, t.Volume
        FROM tav2_bq.ticker AS t WHERE t.time >= '2013-12-01'""",
    # Mọi sự kiện có ex-date/hiệu lực từ 2013-12; lọc trạng thái ở bước dựng (để đếm được số bị loại).
    "ca": """
        SELECT c.id, c.ticker, c.event_code, c.exright_date, c.record_date, c.payout_date,
               c.effective_date, c.value_per_share, c.exercise_ratio, c.dividend_year,
               c.dividend_stage_vi, c.issue_method_name_vi, c.event_status, c.event_title_vi,
               c.public_date, c.ingested_at
        FROM tav2_bq.corporate_action AS c
        WHERE COALESCE(c.exright_date, c.effective_date) >= '2000-01-01'""",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/fund_step4_tr")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cl = bigquery.Client(project=PROJECT)
    for name, sql in Q.items():
        df = cl.query(sql).result().to_dataframe()
        p = os.path.join(a.out, f"{name}.parquet")
        df.to_parquet(p)
        print(name, len(df), "dòng ->", p)


if __name__ == "__main__":
    main()
