# -*- coding: utf-8 -*-
"""Refresh local CSVs for 5-state classifier from BigQuery.

Produces:
  VNINDEX.csv        — full VNINDEX OHLCV + indicators (D_RSI, MACD, CMF, divergences)
  breadth_data.csv   — daily % stocks above MA50 across ticker_prune universe

Run BEFORE vnindex_5state_system.py daily.

Usage:
  python refresh_data.py
  python refresh_data.py --since 2024-01-01   # full rebuild from date X
  python refresh_data.py --since 2000-01-01   # full rebuild from scratch

By default pulls from 2000-01-01 to today (full history, ~6500 rows).
"""
import argparse
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time
from io import StringIO

import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = os.environ.get("BAVN_WORKDIR",
                          os.path.dirname(os.path.abspath(__file__)))
PROJECT = "lithe-record-440915-m9"

# Find bq CLI: env var first, then PATH, then common install dirs.
def _find_bq():
    import shutil as _sh
    for cand in [os.environ.get("BQ_BIN"),
                 _sh.which("bq"), _sh.which("bq.cmd"),
                 "/usr/local/google-cloud-sdk/bin/bq",
                 os.path.expanduser("~/google-cloud-sdk/bin/bq"),
                 r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd",
                 r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd",
                 os.path.expanduser(r"~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd")]:
        if cand and os.path.exists(cand):
            return cand
    raise RuntimeError("bq CLI not found. Install Google Cloud SDK or set BQ_BIN env var.")

BQ = _find_bq()


def bq_query(sql: str, max_rows: int = 2_000_000) -> pd.DataFrame:
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql)
        path = f.name
    try:
        cmd = (f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} '
               f'--format=csv --max_rows={max_rows} < "{path}"')
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    finally:
        os.unlink(path)
    return pd.read_csv(StringIO(out.stdout))


VNINDEX_SQL = """
-- Pull VNINDEX OHLCV + indicators + PE from ticker (canonical) + ticker_1m (latest).
-- IMPORTANT: ticker_1m contains BOTH 'VNI' và 'VNINDEX' rows. 'VNI' chứa data
-- SAI (placeholder/mock 6300, 7000, 8188 — không phải VNINDEX thật). Chỉ
-- dùng ticker='VNINDEX' từ ticker_1m để tránh ô nhiễm dữ liệu.
WITH combined AS (
  SELECT t.time, t.Open, t.High, t.Low, t.Close, t.Volume,
    t.VNINDEX_PE,
    t.D_RSI, t.D_RSI_T1W, t.D_RSI_Max1W, t.D_RSI_Max3M,
    t.D_RSI_Min1W, t.D_RSI_Min3M,
    t.D_RSI_Max1W_Close, t.D_RSI_Max3M_Close,
    t.D_RSI_Max1W_MACD,
    t.D_RSI_MinT3,
    t.D_MACDdiff, t.D_CMF, t.C_L1M, t.C_L1W
  FROM tav2_bq.ticker AS t
  WHERE t.ticker = "VNINDEX"
    AND t.time >= DATE "{since}"
  UNION ALL
  SELECT t.time, t.Open, t.High, t.Low, t.Close, t.Volume,
    t.VNINDEX_PE,
    t.D_RSI, t.D_RSI_T1W, t.D_RSI_Max1W, t.D_RSI_Max3M,
    t.D_RSI_Min1W, t.D_RSI_Min3M,
    t.D_RSI_Max1W_Close, t.D_RSI_Max3M_Close,
    t.D_RSI_Max1W_MACD,
    t.D_RSI_MinT3,
    t.D_MACDdiff, t.D_CMF, t.C_L1M, t.C_L1W
  FROM tav2_bq.ticker_1m AS t
  WHERE t.ticker = "VNINDEX"     -- NOT 'VNI'! VNI row is junk placeholder.
    AND t.time >= DATE "{since}"
    AND t.time > (SELECT MAX(t2.time) FROM tav2_bq.ticker AS t2 WHERE t2.ticker = "VNINDEX")
)
SELECT * FROM combined ORDER BY time
"""

BREADTH_SQL = """
WITH base AS (
  SELECT t.time,
    CASE WHEN t.Close > t.MA50 THEN 1 ELSE 0 END AS above
  FROM tav2_bq.ticker AS t
  WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.time >= DATE "{since}"
    AND t.MA50 IS NOT NULL AND t.Close IS NOT NULL
)
SELECT time,
  ROUND(SUM(above) / COUNT(*), 4) AS breadth
FROM base
GROUP BY time
ORDER BY time
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", default="2000-01-01",
                        help="Start date (default: 2000-01-01)")
    args = parser.parse_args()

    print(f"=== Refresh 5-state inputs from BQ (since {args.since}) ===")
    print(f"   WORKDIR: {WORKDIR}")
    print(f"   BQ:      {BQ}")

    t0 = time.time()

    # 1) VNINDEX with all indicators including VNINDEX_PE
    print("\n[1/2] Fetching VNINDEX OHLCV + indicators + VNINDEX_PE ...")
    vni = bq_query(VNINDEX_SQL.format(since=args.since))
    vni["time"] = pd.to_datetime(vni["time"])
    n_pe = int(vni["VNINDEX_PE"].notna().sum())
    pe_latest = vni.loc[vni["VNINDEX_PE"].notna(), "time"].max()
    print(f"   {len(vni):,} rows, "
          f"{vni['time'].min().date()} → {vni['time'].max().date()}")
    print(f"   VNINDEX_PE: {n_pe:,} non-NaN rows, latest "
          f"{pe_latest.date() if pd.notna(pe_latest) else 'NONE'}")
    if n_pe < len(vni) * 0.5:
        print(f"   ⚠ Cảnh báo: VNINDEX_PE thưa (<50%). Risk override PE>P90 sẽ "
              f"có ít tác dụng. Yêu cầu upstream pipeline backfill PE.")
    vni["ticker"] = "VNINDEX"

    out_vni = os.path.join(WORKDIR, "VNINDEX.csv")
    if os.path.exists(out_vni):
        shutil.copy(out_vni, out_vni + ".bak")
    vni.to_csv(out_vni, index=False)
    print(f"   Saved {out_vni}")

    # 2) Breadth
    print("\n[2/2] Fetching daily breadth (% ticker_prune above MA50) ...")
    breadth = bq_query(BREADTH_SQL.format(since=args.since))
    breadth["time"] = pd.to_datetime(breadth["time"])
    out_br = os.path.join(WORKDIR, "breadth_data.csv")
    if os.path.exists(out_br):
        shutil.copy(out_br, out_br + ".bak")
    breadth.to_csv(out_br, index=False)
    print(f"   {len(breadth):,} rows, range "
          f"[{breadth['breadth'].min():.3f}, {breadth['breadth'].max():.3f}]")
    print(f"   Saved {out_br}")

    print(f"\n=== Done in {time.time()-t0:.1f}s ===")
    print("Next step: python vnindex_5state_system.py")


if __name__ == "__main__":
    main()
