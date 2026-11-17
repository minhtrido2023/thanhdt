#!/usr/bin/env python3
"""B — kéo dữ liệu thô từ BQ (một lần), ghi parquet vào B/data/.  PAT bị loại ở mọi truy vấn.

Chạy: /home/trido/thanhdt/wc_venv/bin/python code/fetch_exp.py
"""
import os
from google.cloud import bigquery

PROJ = "lithe-record-440915-m9"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(OUT, exist_ok=True)
cli = bigquery.Client(project=PROJ)

Q_EVENTS = """
SELECT DISTINCT c.ticker, c.event_code, c.exright_date, c.value_per_share, c.exercise_ratio,
       c.issue_method_name_vi, c.event_status, c.event_title_vi
FROM tav2_bq.corporate_action AS c
WHERE c.ticker != 'PAT' AND c.exright_date IS NOT NULL
  AND ((c.event_code = 'DIV' AND c.event_status = 'executed' AND c.value_per_share > 0)
    OR (c.event_code = 'ISS' AND IFNULL(c.event_status,'') != 'not_executed'
        AND c.issue_method_name_vi IN ('Trả Cổ tức bằng Cổ phiếu', 'Cổ phiếu thưởng')
        AND c.exercise_ratio > 0))
"""

Q_PANEL = """
WITH dates AS (
  SELECT MAX(t.time) AS D FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN '2011-01-01' AND '2025-12-31'
  GROUP BY EXTRACT(YEAR FROM t.time), EXTRACT(QUARTER FROM t.time)
),
u AS (
  SELECT p.time AS D, p.ticker FROM tav2_mike.universe_pit AS p JOIN dates AS d ON p.time = d.D
  WHERE p.in_universe AND p.ruleset_version = 1 AND p.ticker != 'PAT'
),
base AS (
  SELECT u.D, u.ticker, t.Price, t.Close, t.ICB_Code, t.PE, t.DY, t.Dividend_Min3Y
  FROM u JOIN tav2_bq.ticker AS t ON t.ticker = u.ticker AND t.time = u.D
),
fwd AS (
  SELECT b.D, b.ticker,
    ARRAY_AGG(STRUCT(t.time AS dt, t.Close AS c, t.Price AS p) ORDER BY t.time DESC LIMIT 1)[OFFSET(0)] AS lst,
    ARRAY_AGG(STRUCT(t.time AS dt, t.Close AS c) ORDER BY t.Close ASC, t.time ASC LIMIT 1)[OFFSET(0)] AS mn,
    COUNT(*) AS n_fwd
  FROM base AS b JOIN tav2_bq.ticker AS t
    ON t.ticker = b.ticker AND t.time > b.D AND t.time <= DATE_ADD(b.D, INTERVAL 365 DAY)
  WHERE t.Close > 0
  GROUP BY 1, 2
)
SELECT b.*, f.lst.dt AS last_dt, f.lst.c AS last_close, f.lst.p AS last_price,
       f.mn.dt AS min_dt, f.mn.c AS min_close, f.n_fwd
FROM base AS b LEFT JOIN fwd AS f USING (D, ticker)
"""

for name, q in [("events", Q_EVENTS), ("panel", Q_PANEL)]:
    df = cli.query(q).to_dataframe()
    assert not (df["ticker"] == "PAT").any()
    df.to_parquet(os.path.join(OUT, f"{name}_exp.parquet"), index=False)
    print(name, len(df))
