"""Rebuild VNINDEX.csv with OHLCV from BQ + Pe from current CSV.

The user's new VNINDEX.csv has Pe/trading_session/volume_session but no OHLCV.
The 5-state system needs OHLCV. We merge BQ OHLCV with the existing Pe data.
Output: VNINDEX.csv backup + enhanced version with all needed columns.
"""
import os, subprocess, tempfile, pandas as pd
from io import StringIO

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ = r"bq"


def bq(sql):
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql)
        path = f.name
    try:
        cmd = (f'"{BQ}" query --use_legacy_sql=false --project_id=lithe-record-440915-m9 '
               f'--format=csv --max_rows=50000 < "{path}"')
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    finally:
        os.unlink(path)
    return pd.read_csv(StringIO(out.stdout))


print("Pulling VNINDEX OHLCV from BQ (ticker + ticker_1m latest)...")
ohlcv = bq("""
WITH combined AS (
  SELECT t.time, t.Open, t.High, t.Low, t.Close, t.Volume FROM tav2_bq.ticker AS t
  WHERE t.ticker = "VNINDEX"
  UNION ALL
  SELECT t.time, t.Open, t.High, t.Low, t.Close, t.Volume FROM tav2_bq.ticker_1m AS t
  WHERE t.ticker = "VNINDEX"
    AND t.time > (SELECT MAX(t2.time) FROM tav2_bq.ticker AS t2 WHERE t2.ticker = "VNINDEX")
)
SELECT * FROM combined ORDER BY time
""")
ohlcv["time"] = pd.to_datetime(ohlcv["time"])
print(f"  OHLCV: {len(ohlcv):,} rows, {ohlcv['time'].min().date()} → {ohlcv['time'].max().date()}")

# Read current VNINDEX.csv (Pe data)
print("Reading current VNINDEX.csv (Pe + trading_session)...")
cur = pd.read_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"))
cur["time"] = pd.to_datetime(cur["time"], format="mixed")
print(f"  Pe data: {len(cur):,} rows, {cur['time'].min().date()} → {cur['time'].max().date()}")

# Backup current CSV
import shutil
backup = os.path.join(WORKDIR, "data/VNINDEX_pe_only.csv")
shutil.copy(os.path.join(WORKDIR, "data/VNINDEX.csv"), backup)
print(f"  Backed up Pe-only file: {backup}")

# For dates after BQ's max, use user's CSV Index as Close + approximate OHL
bq_max = ohlcv["time"].max()
extra = cur[cur["time"] > bq_max].copy()
if len(extra):
    extra["Open"] = extra["Index"]
    extra["High"] = extra["Index"]
    extra["Low"] = extra["Index"]
    extra["Close"] = extra["Index"]
    extra["Volume"] = extra["volume_session"].fillna(0)
    extra = extra[["time", "Open", "High", "Low", "Close", "Volume"]]
    print(f"  Adding {len(extra)} rows from CSV (May 2026 dates) — OHL approximated as Close")
    ohlcv = pd.concat([ohlcv, extra], ignore_index=True).sort_values("time")

# Merge OHLCV with Pe data
merged = ohlcv.merge(cur[["time", "Pe", "trading_session", "volume_session"]],
                     on="time", how="left")
merged["ticker"] = "VNINDEX"
print(f"\n  Merged: {len(merged):,} rows")
print(f"  Last 3 rows:")
print(merged.tail(3).to_string(index=False))

# Save back as VNINDEX.csv (script-compatible format)
merged.to_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"), index=False)
print(f"\n  Saved enhanced VNINDEX.csv with OHLCV + Pe ({merged['time'].max().date()})")
