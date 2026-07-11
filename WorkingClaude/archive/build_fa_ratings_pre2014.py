#!/usr/bin/env python3
"""
build_fa_ratings_pre2014.py
===========================
Run fundamental_rating.py 7-axis FA scoring on pre-2014 ticker_financial data.
Output: fundamental_rating_pre2014.csv + fundamental_rating_pre2014_all.csv

Differences from original fundamental_rating.py:
  - Date filter: f.time BETWEEN 2006-01-01 AND 2013-12-31 (instead of >= 2014)
  - Liquidity threshold relaxed: 100M VND (instead of 1B) — pre-2014 markets thin
  - Universe wider: drops `ticker_prune` filter (table empty pre-2014)
  - PE valuation axis effectively neutral (PE/PE_MA5Y mostly NULL pre-2014)
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"
OUT_CSV    = "fundamental_rating_pre2014.csv"
OUT_ALL    = "data/fundamental_rating_pre2014_all.csv"

WEIGHTS = {
    "quality":     0.18,
    "stability":   0.18,
    "cash":        0.18,
    "shareholder": 0.15,
    "growth":      0.13,
    "health":      0.08,
    "valuation":   0.10,
}

TIERS = [
    ("A", 0.90, 1.00),
    ("B", 0.70, 0.90),
    ("C", 0.40, 0.70),
    ("D", 0.15, 0.40),
    ("E", 0.00, 0.15),
]

def bq_query(sql, label=""):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = (f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
               f'--project_id={PROJECT} --format=csv --max_rows=10000000')
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0:
        raise RuntimeError(f"[BQ ERROR] {label}: {(r.stdout or r.stderr)[:600]}")
    txt = r.stdout.strip()
    return pd.read_csv(StringIO(txt)) if txt else pd.DataFrame()

SQL = """
WITH joined AS (
  SELECT
    f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.FSCORE,
    f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y,
    SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y,
    SAFE_DIVIDE(f.CF_OA_5Y + f.CF_Invest_5Y, ABS(f.CF_OA_5Y)) AS FCF_OA_ratio,
    f.Debt_Eq_P0, f.IntCov_P0, f.CashR_P0,
    SAFE_DIVIDE(f.PE - f.PE_MA5Y, f.PE_SD5Y) AS PE_self_z,
    SAFE_DIVIDE(f.PB - f.PB_MA5Y, f.PB_SD5Y) AS PB_self_z,
    CASE WHEN f.PE > 0 THEN SAFE_DIVIDE(f.NP_R, f.PE) ELSE NULL END AS growth_yield,
    f.PE, f.PB, f.PCF,
    f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
    f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
    f.Revenue_P4, f.Revenue_P5, f.Revenue_P6, f.Revenue_P7,
    CASE WHEN GREATEST(f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3,
                       f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0, GREATEST(f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3,
                                             f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    CASE WHEN GREATEST(f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
                       f.Revenue_P4, f.Revenue_P5, f.Revenue_P6, f.Revenue_P7) > 0
         THEN SAFE_DIVIDE(f.Revenue_P0,
                          GREATEST(f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
                                   f.Revenue_P4, f.Revenue_P5, f.Revenue_P6, f.Revenue_P7))
         ELSE NULL END AS Rev_peak_ratio,
    t.time AS t_time, t.ICB_Code,
    t.Volume_3M_P50 * t.Close AS trading_value_1M,
    t.profit_3M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker
    AND t.time <= f.time
    AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time BETWEEN DATE "2006-01-01" AND DATE "2013-12-31"
    AND t.Volume_3M_P50 IS NOT NULL
    AND t.Volume_3M_P50 * t.Close >= 1e8  -- 100M VND (relaxed from 1B for thin pre-2014 market)
)
SELECT * EXCEPT(rn, t_time) FROM joined WHERE rn = 1
"""

print("Fetching pre-2014 raw indicators ...")
df = bq_query(SQL, "raw")
print(f"  {len(df):,} (ticker, quarter) rows after liquidity filter")

if len(df) == 0:
    print("No data — aborting"); sys.exit(1)

df["growth_yield"] = df["growth_yield"].clip(lower=-0.15, upper=0.15)

_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"]  = df["DY"] * _mult
df["DY_sust"] = _mult

NP_COLS  = [f"NP_P{i}"      for i in range(8)]
REV_COLS = [f"Revenue_P{i}" for i in range(8)]

np_arr  = df[NP_COLS].values.astype(float)
rev_arr = df[REV_COLS].values.astype(float)

np_n  = np.sum(~np.isnan(np_arr),  axis=1)
rev_n = np.sum(~np.isnan(rev_arr), axis=1)

with np.errstate(divide="ignore", invalid="ignore"):
    np_mean  = np.nanmean(np_arr,  axis=1)
    np_std   = np.nanstd(np_arr,   axis=1, ddof=1)
    rev_mean = np.nanmean(rev_arr, axis=1)
    rev_std  = np.nanstd(rev_arr,  axis=1, ddof=1)
    df["NP_CV"]  = np.where(np_n  >= 6, np_std  / np.maximum(np.abs(np_mean),  1e6), np.nan)
    df["Rev_CV"] = np.where(rev_n >= 6, rev_std / np.maximum(np.abs(rev_mean), 1e6), np.nan)
    df["NP_CV"]  = df["NP_CV"].clip(upper=10)
    df["Rev_CV"] = df["Rev_CV"].clip(upper=10)

rev_p0 = df["Revenue_P0"].values; rev_p7 = df["Revenue_P7"].values
mask = (rev_p0 > 0) & (rev_p7 > 0)
df["LT_CAGR"] = np.where(mask, (rev_p0 / rev_p7) ** (4/7) - 1, np.nan)
df["LT_CAGR"] = df["LT_CAGR"].clip(lower=-0.95, upper=5.0)

print("Computing industry-relative valuations ...")
df["ICB_Code"] = df["ICB_Code"].fillna("UNK")
for col in ["PE", "PB", "PCF"]:
    grp = df.groupby(["quarter", "ICB_Code"])[col]
    med = grp.transform("median")
    sd  = grp.transform("std")
    z_ind = (df[col] - med) / sd.replace(0, np.nan)
    z_global = df.groupby("quarter")[col].transform(
        lambda x: (x - x.median()) / x.std()
    )
    df[f"{col}_ind_z"] = z_ind.fillna(z_global)

INV_COLS = ["Debt_Eq_P0",
            "PE_self_z", "PB_self_z",
            "PE_ind_z", "PB_ind_z", "PCF_ind_z",
            "NP_CV", "Rev_CV"]
for c in INV_COLS:
    df[c] = -df[c]

AXIS_COLS = {
    "quality":     ["ROIC5Y", "ROE_Min5Y", "FSCORE"],
    "stability":   ["NP_CV", "Rev_CV", "LT_CAGR"],
    "cash":        ["CF_OA_5Y", "CFOA_NP"],
    "shareholder": ["DY_adj", "Dividend_Min3Y", "FCF_OA_ratio", "DY_sust"],
    "growth":      ["NP_R", "Revenue_YoY_P0", "GPM_change", "NP_peak_ratio", "Rev_peak_ratio"],
    "health":      ["Debt_Eq_P0", "IntCov_P0", "CashR_P0"],
    "valuation":   ["PE_self_z", "PB_self_z", "PE_ind_z", "PB_ind_z", "PCF_ind_z", "growth_yield"],
}

print("Computing per-quarter percentile ranks ...")
for cols in AXIS_COLS.values():
    for c in cols:
        df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

for axis, cols in AXIS_COLS.items():
    rank_cols = [f"r_{c}" for c in cols]
    df[f"score_{axis}"] = df[rank_cols].mean(axis=1, skipna=True)

# Pre-2014: shareholder + valuation axes have ~85% missing data.
# Use weighted mean over AVAILABLE axes (re-normalize weights when any axis is NaN).
score_cols = [f"score_{a}" for a in WEIGHTS]
weights_arr = np.array([WEIGHTS[a] for a in WEIGHTS])
score_mat = df[score_cols].values  # (n, 7)
# Mask of available (non-NaN) axes per row
mask = ~np.isnan(score_mat)
# Weighted sum (treating NaN as 0)
weighted_sum = np.where(mask, score_mat * weights_arr, 0.0).sum(axis=1)
# Available weight sum (normalize)
avail_weights = (mask * weights_arr).sum(axis=1)
df["total_score"] = np.where(avail_weights > 0, weighted_sum / avail_weights, np.nan)
df["n_axes_available"] = mask.sum(axis=1)

# Require at least 4/7 axes available (out of 7). Pre-2014 typically gets 5 (no DY/no PE).
df = df[df["n_axes_available"] >= 4].copy()
print(f"  {len(df):,} rows with >=4/7 axes available")

df["score_pct"] = df.groupby("quarter")["total_score"].rank(pct=True)

def tier_of(p):
    for name, lo, hi in TIERS:
        if lo <= p <= hi:
            return name
    return "E"
df["tier"] = df["score_pct"].apply(tier_of)

keep = ["ticker", "quarter", "time", "trading_value_1M", "ICB_Code",
        "score_quality", "score_stability", "score_cash", "score_shareholder",
        "score_growth", "score_health", "score_valuation",
        "total_score", "score_pct", "tier", "profit_3M",
        "NP_CV", "Rev_CV", "LT_CAGR", "DY", "DY_adj", "DY_sust", "Dividend_Min3Y", "FCF_OA_ratio",
        "NP_R", "Revenue_YoY_P0", "NP_peak_ratio", "Rev_peak_ratio"]
out_all = df[keep].sort_values(["time", "tier", "ticker"], ascending=[False, True, True])
out_all.to_csv(OUT_ALL, index=False)
print(f"  Saved {OUT_ALL}  ({len(out_all):,} rows, all quarters)")

print("\n=== Pre-2014 FA tier distribution ===")
print(out_all["tier"].value_counts())

print("\n=== Validation: forward profit_3M by tier (pre-2014) ===")
print(f"{'Tier':<6}{'N':>8}{'Median':>10}{'Mean':>10}{'WinRate':>10}")
v = df.dropna(subset=["profit_3M"])
for tier in ["A","B","C","D","E"]:
    g = v[v["tier"] == tier]["profit_3M"]
    if len(g):
        print(f"{tier:<6}{len(g):>8,}{g.median():>9.2f}%{g.mean():>9.2f}%{(g>0).mean()*100:>9.1f}%")

print("\n=== Coverage by year ===")
df["year"] = pd.to_datetime(df["time"]).dt.year
print(df.groupby("year")["tier"].value_counts().unstack(fill_value=0))
