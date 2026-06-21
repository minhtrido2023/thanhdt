#!/usr/bin/env python3
"""
test_fa_ic_2007_2013_crisis.py
===============================
Stress test FA signals on 2007-2013 era using quarterly Close prices.

Data available: ticker_financial has Close at each quarterly release date
from 2006. Can compute QUARTERLY forward returns by joining successive
snapshots per ticker.

Forward return = Close(Q+1) / Close(Q) - 1  (≈ 1-quarter forward return)
            or = Close(Q+4) / Close(Q) - 1  (≈ 1-year forward)

Test windows:
  CRISIS_2008: 2007Q4 - 2009Q2 (GFC period)
  RECOVERY_2009_10: 2009Q3 - 2010Q4
  INFLATION_2011: 2010Q4 - 2012Q2 (rate hike + crash)
  SIDEWAYS_2012_13: 2012Q3 - 2013Q4
  ALL_2007_2013: aggregate

Indicators tested (using only data available pre-2014):
  - smoothed_EY (need NP_P0..P3 + OShares + Close)
  - ROE_Min5Y (need 5Y history → 2012+)
  - NP_R, NP_peak_ratio
  - Cash_MktCap (need Cash_P0 + MktCap)
  - AdvCust_MktCap_yld (have AdvCust from 2007)
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(f"{r.stdout[:300]}|{r.stderr[:300]}")
    return pd.read_csv(StringIO(r.stdout.strip()))

def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 20: return float("nan"), 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

# Pull all quarterly snapshots 2006-2014 from ticker_financial
SQL = """
SELECT
  ticker, quarter, time,
  Close, OShares, PE, PB,
  NP_P0, NP_P1, NP_P2, NP_P3, NP_P4, NP_P5, NP_P6, NP_P7,
  Revenue_P0, Revenue_P4,
  AdvCust_P0, AdvCust_P4,
  UnearnRev_P0,
  Cash_P0, EBITDA_P0, StDebt_P0, LtDebt_P0,
  ROIC5Y, ROE_Min5Y, ROE_Trailing,
  CF_OA_5Y, CF_OA_P0,
  NP_R, Revenue_YoY_P0,
  DY, Dividend_Min3Y, FSCORE,
  Debt_Eq_P0, IntCov_P0
FROM tav2_bq.ticker_financial
WHERE time >= "2006-01-01" AND time < "2015-01-01"
  AND Close IS NOT NULL AND Close > 0
ORDER BY ticker, time
"""

print("Fetching ticker_financial 2006-2014 ..."); df = bq_query(SQL)
print(f"  {len(df):,} rows, {df['ticker'].nunique()} tickers")
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values(["ticker", "time"]).reset_index(drop=True)

# Compute forward returns: next quarter's Close / current Close - 1
df["next_close"] = df.groupby("ticker")["Close"].shift(-1)
df["next_close_4q"] = df.groupby("ticker")["Close"].shift(-4)
df["fwd_1q"] = (df["next_close"] / df["Close"] - 1) * 100  # %
df["fwd_4q"] = (df["next_close_4q"] / df["Close"] - 1) * 100

# Time-to-next-snapshot (sanity check)
df["next_time"] = df.groupby("ticker")["time"].shift(-1)
df["days_to_next"] = (df["next_time"] - df["time"]).dt.days

print(f"\nForward return distribution (fwd_1q):")
print(f"  Median: {df['fwd_1q'].median():.2f}%, Mean: {df['fwd_1q'].mean():.2f}%")
print(f"  Q1: {df['fwd_1q'].quantile(0.25):.2f}%, Q3: {df['fwd_1q'].quantile(0.75):.2f}%")
print(f"  Sample size with fwd_1q: {df['fwd_1q'].notna().sum():,}")

# ─── Build indicators ──────────────────────────────────────────────────
df["MktCap"] = df["Close"] * df["OShares"]
df["NP_4Q_mean"] = df[[f"NP_P{i}" for i in range(4)]].mean(axis=1, skipna=True)
df["smoothed_EY"] = (df["NP_4Q_mean"] / df["OShares"].replace(0, np.nan) / df["Close"].replace(0, np.nan)).clip(-1, 1)
df["EY"] = np.where(df["PE"] > 0, 1.0 / df["PE"], np.nan)
df["BY"] = np.where(df["PB"] > 0, 1.0 / df["PB"], np.nan)
df["Cash_MktCap"] = np.where(df["MktCap"] > 0, df["Cash_P0"] / df["MktCap"], np.nan).clip(-1, 5)

def sd(num, den):
    return np.where(np.abs(den) > 1e-3, num / den.replace(0, np.nan), np.nan)
df["AdvCust_MktCap_yld"] = sd(df["AdvCust_P0"], df["MktCap"]).clip(-1, 20)
df["AdvCust_YoY"] = sd(df["AdvCust_P0"] - df["AdvCust_P4"], df["AdvCust_P4"].abs()).clip(-5, 20)

# NP_peak_ratio
np_cols = [f"NP_P{i}" for i in range(8)]
np_max = df[np_cols].max(axis=1)
df["NP_peak_ratio"] = np.where(np_max > 0, df["NP_P0"] / np_max, np.nan)

# Stability (NP_CV)
np_arr = df[np_cols].values.astype(float)
np_n = np.sum(~np.isnan(np_arr), axis=1)
with np.errstate(divide="ignore", invalid="ignore"):
    np_m = np.nanmean(np_arr, axis=1); np_s = np.nanstd(np_arr, axis=1, ddof=1)
    df["NP_CV_inv"] = -np.where(np_n >= 6, np_s / np.maximum(np.abs(np_m), 1e6), np.nan).clip(max=10)

# Define periods
df["year"] = df["time"].dt.year
df["yr_q"] = df["year"].astype(str) + df["quarter"].str.extract(r"(Q\d)").fillna("?")[0]

def period(row):
    y = row["year"]
    if y in [2007, 2008]:
        if (y == 2007 and row["time"].month >= 10) or y == 2008: return "CRISIS_2008"
        return "BOOM_2007"
    if y == 2009 and row["time"].month <= 6: return "CRISIS_2008"
    if y == 2009: return "RECOVERY_2009"
    if y == 2010: return "RECOVERY_2010"
    if y == 2011 or (y == 2012 and row["time"].month <= 6): return "INFLATION_2011"
    if (y == 2012 and row["time"].month >= 7) or y == 2013: return "SIDEWAYS_2012_13"
    if y == 2014: return "EARLY_2014"
    return f"y{y}"

df["regime"] = df.apply(period, axis=1)
print("\nRegime distribution:")
print(df.groupby("regime").size().to_string())

# ─── IC per period ──────────────────────────────────────────────────────
INDICATORS = [
    ("ROIC5Y",          "ROIC5Y"),
    ("ROE_Min5Y",       "ROE_Min5Y"),
    ("ROE_Trailing",    "ROE_Trailing"),
    ("FSCORE",          "FSCORE"),
    ("NP_R",            "NP_R"),
    ("NP_peak_ratio",   "NP_peak_ratio"),
    ("NP_CV (inv)",     "NP_CV_inv"),
    ("CF_OA_5Y",        "CF_OA_5Y"),
    ("DY",              "DY"),
    ("smoothed_EY",     "smoothed_EY"),
    ("EY (1/PE)",       "EY"),
    ("BY (1/PB)",       "BY"),
    ("Cash_MktCap",     "Cash_MktCap"),
    ("AdvCust_MktCap",  "AdvCust_MktCap_yld"),
    ("AdvCust_YoY",     "AdvCust_YoY"),
]
# Rank per quarter (cross-sectional)
for name, col in INDICATORS:
    df[f"r_{col}"] = df.groupby("quarter")[col].rank(pct=True, na_option="keep")

PERIODS = ["CRISIS_2008","RECOVERY_2009","RECOVERY_2010","INFLATION_2011","SIDEWAYS_2012_13","EARLY_2014"]
TARGETS = ["fwd_1q", "fwd_4q"]

print("\n" + "="*110)
print("IC of FA indicators in stress periods (2007-2014)")
print("Target: fwd_1q (quarterly forward return) and fwd_4q (1Y forward)")
print("="*110)

for target in TARGETS:
    print(f"\n--- TARGET: {target} ---")
    print(f"{'Indicator':<22}", end="")
    for p in PERIODS: print(f"{p[:11]:>11}", end="")
    print(f"{'2007-13':>10}")
    print("-" * (22 + 11*len(PERIODS) + 10))
    for name, col in INDICATORS:
        rcol = f"r_{col}"
        row = f"{name:<22}"
        for p in PERIODS:
            sub = df[df["regime"]==p]
            rho, n = spearman_ic(sub[rcol], sub[target])
            if np.isnan(rho):
                row += f"{'n/a':>11}"
            else:
                row += f"{rho:>+10.3f} "
        # Full pre-2014
        full = df[~df["regime"].isin(["EARLY_2014"])]
        rho_f, _ = spearman_ic(full[rcol], full[target])
        row += f"{rho_f:>+10.3f}"
        print(row)
    # N per period
    ns_row = f"{'(N)':<22}"
    for p in PERIODS:
        n = df[df["regime"]==p][target].notna().sum()
        ns_row += f"{n:>11}"
    full = df[~df["regime"].isin(["EARLY_2014"])]
    ns_row += f"{full[target].notna().sum():>10}"
    print(ns_row)

# ─── Compare 2007-2013 IC vs 2014-2026 IC (use the previous results) ───
print("\n" + "="*100)
print("COMPARISON: 2007-2013 vs 2014-2026 IC (using quarterly fwd_1q)")
print("="*100)
# 2014-2026 was using profit_3M (daily 3M forward). Different metric but similar in spirit.
# Read previous IC results if available
prev = None
try:
    prev = pd.read_csv("fa_ic_regime_results.csv")
    print("\nLoaded fa_ic_regime_results.csv (2014-2026 IC)")
except FileNotFoundError:
    print("  fa_ic_regime_results.csv not available")

if prev is not None:
    print(f"\n{'Indicator':<22}{'2007-13 IC':>12}{'2014-26 P2':>12}{'2014-26 FULL':>14}  Verdict")
    print("-"*75)
    # Map previous indicator names to current
    name_map = {"ROIC5Y":"ROIC5Y","ROE_Min5Y":"ROE_Min5Y","ROE_Trailing":"ROE_Trailing",
                "FSCORE":"FSCORE","NP_R":"NP_R","NP_peak_ratio":"NP_peak_ratio",
                "smoothed_EY":"smoothed_EY","EY (1/PE)":"EY (1/PE)","BY (1/PB)":"BY (1/PB)",
                "Cash_MktCap":"Cash_MktCap","AdvCust_MktCap":"AdvCust_MktCap_yld",
                "AdvCust_YoY":"AdvCust_YoY","NP_CV (inv)":"NP_CV (inv)","CF_OA_5Y":"CF_OA_5Y",
                "DY":"DY_adj"}
    full = df[~df["regime"].isin(["EARLY_2014"])]
    for name, col in INDICATORS:
        prev_name = name_map.get(name, name)
        prev_row = prev[prev["indicator"]==prev_name]
        rho_2007, _ = spearman_ic(full[f"r_{col}"], full["fwd_1q"])
        if len(prev_row) > 0:
            prev_p2 = prev_row.iloc[0]["P2"]
            prev_full = prev_row.iloc[0]["FULL"]
            if not np.isnan(rho_2007) and not np.isnan(prev_full):
                same_sign = (rho_2007 * prev_full > 0)
                verdict = "✓ same sign timeless" if same_sign else "⚠ FLIP across eras"
            else:
                verdict = "—"
            print(f"{name:<22}{rho_2007:>+12.3f}{prev_p2:>+12.3f}{prev_full:>+14.3f}  {verdict}")
        else:
            print(f"{name:<22}{rho_2007:>+12.3f}{'n/a':>12}{'n/a':>14}")

# ─── 2008 GFC specific stress test ─────────────────────────────────────
print("\n" + "="*100); print("2008 GFC SPECIFIC: which FA indicators held up?"); print("="*100)
gfc = df[df["regime"]=="CRISIS_2008"]
print(f"\nGFC universe: N={len(gfc)} rows, {gfc['ticker'].nunique()} tickers")
print(f"GFC fwd_1q distribution: mean={gfc['fwd_1q'].mean():+.2f}%, median={gfc['fwd_1q'].median():+.2f}%, WR={(gfc['fwd_1q']>0).mean()*100:.1f}%")
print(f"\n  Tier ordering test in GFC (using smoothed_EY ranks):")
gfc_v = gfc.dropna(subset=["fwd_1q","smoothed_EY"]).copy()
gfc_v["sEY_q"] = pd.qcut(gfc_v["smoothed_EY"].rank(pct=True), 5, labels=["Q1_cheap","Q2","Q3","Q4","Q5_expensive"])
for q in ["Q1_cheap","Q2","Q3","Q4","Q5_expensive"]:
    g = gfc_v[gfc_v["sEY_q"]==q]
    if len(g) == 0: continue
    # smoothed_EY ranks: HIGH rank = HIGH earnings yield = CHEAP (good)
    # But qcut: Q1 = lowest = expensive; Q5 = highest = cheapest. Flip labels...
    # Actually: rank(pct=True) returns 0-1, qcut splits into 5 equal bins. Q1 = lowest 20% (lowest EY = most expensive).
    print(f"    {q:<14}  N={len(g):4d}  median fwd_1q={g['fwd_1q'].median():+.2f}%  mean={g['fwd_1q'].mean():+.2f}%  WR={(g['fwd_1q']>0).mean()*100:.1f}%")

print("\n  Same in BOOM 2007 era for comparison:")
boom = df[df["regime"]=="BOOM_2007"]
print(f"  BOOM_2007 N={len(boom)}, fwd_1q mean={boom['fwd_1q'].mean():+.2f}%, median={boom['fwd_1q'].median():+.2f}%")

print("\n" + "="*100); print("DONE"); print("="*100)
