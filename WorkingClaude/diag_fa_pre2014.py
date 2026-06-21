#!/usr/bin/env python3
"""Diagnose pre-2014 FA axis NaN distribution."""
import sys;
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"

SQL = """
SELECT f.ticker, f.quarter, f.time,
  f.ROIC5Y, f.ROE_Min5Y, f.FSCORE,
  f.NP_R, f.Revenue_YoY_P0,
  f.GPM_P0, f.GPM_P4, f.CF_OA_5Y,
  SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
  f.DY, f.Dividend_Min3Y, f.CF_Invest_5Y,
  f.Debt_Eq_P0, f.IntCov_P0, f.CashR_P0,
  f.PE, f.PB, f.PCF, f.PE_MA5Y, f.PB_MA5Y,
  f.NP_P0, f.NP_P4, f.NP_P7,
  f.Revenue_P0, f.Revenue_P7
FROM tav2_bq.ticker_financial AS f
WHERE f.time BETWEEN DATE "2006-01-01" AND DATE "2013-12-31"
"""
with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
    f.write(SQL); tmp = f.name
cmd = (f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
       f'--project_id={PROJECT} --format=csv --max_rows=10000000')
r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, shell=True)
os.unlink(tmp)
df = pd.read_csv(StringIO(r.stdout))
print(f"Total pre-2014 rows: {len(df):,}")
print(f"\nPer-column NaN%:")
for c in df.columns:
    nan_pct = df[c].isna().mean() * 100
    if nan_pct > 0:
        print(f"  {c:<20} {nan_pct:5.1f}% NaN")

# Coverage by year
df["year"] = pd.to_datetime(df["time"]).dt.year
print(f"\nRow count by year:")
print(df["year"].value_counts().sort_index())

# Key per-axis indicators
axes = {
    "quality":     ["ROIC5Y","ROE_Min5Y","FSCORE"],
    "stability":   ["NP_P0","NP_P7","Revenue_P0","Revenue_P7"],
    "cash":        ["CF_OA_5Y","CFOA_NP"],
    "shareholder": ["DY","Dividend_Min3Y"],
    "growth":      ["NP_R","Revenue_YoY_P0","GPM_P0","GPM_P4"],
    "health":      ["Debt_Eq_P0","IntCov_P0","CashR_P0"],
    "valuation":   ["PE","PB","PCF"],
}
print(f"\nAxis coverage (rows with >=1 non-NaN indicator):")
for axis, cols in axes.items():
    any_nonna = df[cols].notna().any(axis=1).mean() * 100
    all_nonna = df[cols].notna().all(axis=1).mean() * 100
    print(f"  {axis:<12} any: {any_nonna:5.1f}%  all: {all_nonna:5.1f}%")
