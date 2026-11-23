"""D1/G3 — kéo panel cuối tháng PIT từ BQ (universe_pit ∩ ticker). Chỉ đọc.
Cột: Price thô, Close (adj, cho lợi suất kỳ sau), PB, PE (đều tính trên Price thô = PIT theo
kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md), ROE5Y, ICB_Code, giá trị GD 20 phiên.
KHÔNG dùng profit_*; KHÔNG ticker_prune. Ghi calc/panel.parquet.
"""
import os, subprocess, json, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SQL = r"""
WITH d AS (
  SELECT DISTINCT time FROM tav2_mike.universe_pit WHERE time >= '2011-01-01' AND ruleset_version = 1
), me AS (
  SELECT MAX(time) AS time FROM d GROUP BY FORMAT_DATE('%Y-%m', time)
), u AS (
  SELECT p.time AS time, p.ticker AS ticker FROM tav2_mike.universe_pit p JOIN me USING(time)
  WHERE p.in_universe AND p.ruleset_version = 1
), tv AS (
  SELECT k.ticker AS ticker, k.time AS time,
    AVG(k.Price*k.Volume) OVER (PARTITION BY k.ticker ORDER BY k.time ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS adv20
  FROM tav2_bq.ticker AS k WHERE k.time >= '2010-11-01'
)
SELECT t.time, t.ticker, t.Price, t.Close, t.PB, t.PE, t.ROE5Y, t.ICB_Code, tv.adv20
FROM tav2_bq.ticker t
JOIN u ON u.time = t.time AND u.ticker = t.ticker
JOIN tv ON tv.time = t.time AND tv.ticker = t.ticker
"""

def main():
    out = os.path.join(HERE, "panel.parquet")
    cmd = ["bq", "query", "--use_legacy_sql=false", "--project_id=lithe-record-440915-m9",
           "--format=csv", "--max_rows=2000000", SQL]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("bq lỗi: " + r.stderr[-2000:])
    from io import StringIO
    df = pd.read_csv(StringIO(r.stdout))
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(["time", "ticker"]).reset_index(drop=True)
    df.to_parquet(out, index=False)
    print(len(df), df.time.min(), df.time.max(), df.time.nunique(), df.ticker.nunique())


SQL_ALL = r"""
WITH d AS (
  SELECT DISTINCT time FROM tav2_mike.universe_pit WHERE time >= '2011-01-01' AND ruleset_version = 1
), me AS (SELECT MAX(time) AS time FROM d GROUP BY FORMAT_DATE('%Y-%m', time))
SELECT k.time AS time, k.ticker AS ticker, k.Price AS Price, k.Close AS Close, k.PB AS PB, k.PE AS PE,
       k.ROE5Y AS ROE5Y, k.ICB_Code AS ICB_Code
FROM tav2_bq.ticker AS k JOIN me ON me.time = k.time
"""

def main_all():
    """Mọi mã tại cuối tháng (không lọc universe) — để lợi suất kỳ sau không mất mã rời universe
    (giảm survivorship) và để có dữ liệu cho mã DD ngoài universe."""
    from io import StringIO
    r = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--project_id=lithe-record-440915-m9",
                        "--format=csv", "--max_rows=3000000", SQL_ALL], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("bq lỗi: " + (r.stderr + r.stdout)[-2000:])
    df = pd.read_csv(StringIO(r.stdout)); df["time"] = pd.to_datetime(df["time"])
    df.sort_values(["time", "ticker"]).reset_index(drop=True).to_parquet(os.path.join(HERE, "panel_all.parquet"), index=False)
    print("all", len(df), df.ticker.nunique())

if __name__ == "__main__":
    (main_all if "--all" in sys.argv else main)()
