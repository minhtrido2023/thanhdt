#!/usr/bin/env python3
"""
test_fa_growth_sector_horizon.py
=================================
3 explorations to strengthen FA v6b further:

PART 1: Growth axis redesign — find better growth indicators
  - QoQ momentum (NP_P0/NP_P1 - 1)
  - Earnings acceleration (QoQ_now vs QoQ_prior)
  - Earnings consistency (count of growing transitions)
  - Margin trajectory: NPM_delta, EBITM_delta, GPM slope (8Q regression)
  - Operating efficiency: AssetTurn delta, InvTurn delta, CashCycle delta

PART 2: Sector-conditional IC
  - For each ICB top-digit sector, compute IC of top v6 indicators
  - Identify sector-specific patterns

PART 3: Forward horizon sensitivity (using ticker_prune O6M, O1Y, O2Y)
  - Does FA signal strengthen further at 6M / 1Y / 2Y?
  - Sweet spot for FA = ?
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
    if r.returncode != 0: raise RuntimeError(r.stderr[:600])
    return pd.read_csv(StringIO(r.stdout.strip()))

def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 30: return float("nan"), 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

# Pull margin/efficiency cols + use ticker_prune to get O6M/O1Y/O2Y where available
SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0, f.Revenue_P1, f.Revenue_P4,
    f.GPM_P0, f.GPM_P1, f.GPM_P2, f.GPM_P3, f.GPM_P4, f.GPM_P5, f.GPM_P6, f.GPM_P7,
    f.NPM_P0, f.NPM_P4, f.EBITM_P0, f.EBITM_P4,
    f.AssetTurn_P0, f.AssetTurn_P4, f.InvTurn_P0, f.InvTurn_P4,
    f.CashCycle_P0, f.CashCycle_P4, f.DSO_P0, f.DSO_P4,
    f.DY, f.Dividend_Min3Y, f.OShares,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3,
    t.Close, t.ICB_Code, t.profit_3M,
    -- O-stats from ticker_prune (NULL if ticker not in prune universe)
    tp.O6M, tp.O1Y, tp.O2Y,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  LEFT JOIN `lithe-record-440915-m9.tav2_bq.ticker_prune` AS tp
    ON tp.ticker = t.ticker AND tp.time = t.time
  WHERE f.time >= "2014-01-01" AND f.quarter LIKE "%Q4"
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching Q4 data ..."); df = bq_query(SQL); print(f"  {len(df):,} rows")
df["year"] = pd.to_datetime(df["time"]).dt.year
df["ICB_Code"] = df["ICB_Code"].fillna(0)
df["sector_top"] = (df["ICB_Code"] / 1000).astype(int)  # leading digit

# ═══════════════════════════════════════════════════════════════════════════
# PART 1: Growth indicator candidates
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("PART 1: Growth axis redesign candidates"); print("="*80)

# 1.1 QoQ NP growth (most recent quarter sequential)
df["NP_QoQ"] = np.where(df["NP_P1"].abs() > 0,
                        (df["NP_P0"] - df["NP_P1"]) / df["NP_P1"].abs(), np.nan).clip(-5, 5)
# 1.2 Acceleration: QoQ_now - QoQ_prior (i.e., (P0/P1) - (P1/P2))
df["NP_QoQ_prev"] = np.where(df["NP_P2"].abs() > 0,
                             (df["NP_P1"] - df["NP_P2"]) / df["NP_P2"].abs(), np.nan).clip(-5, 5)
df["NP_acceleration"] = (df["NP_QoQ"] - df["NP_QoQ_prev"]).clip(-5, 5)

# 1.3 Consistency: count NP_Pi > NP_Pi+1 in 4 consecutive transitions (P0>P1, P1>P2, P2>P3, P3>P4)
df["NP_growing_streak"] = (
    (df["NP_P0"] > df["NP_P1"]).astype(int)
  + (df["NP_P1"] > df["NP_P2"]).astype(int)
  + (df["NP_P2"] > df["NP_P3"]).astype(int)
  + (df["NP_P3"] > df["NP_P4"]).astype(int)
)
# 1.4 Positive-earnings consistency: count NP_Pi > 0 in last 4 quarters
df["NP_positive_4Q"] = (
    (df["NP_P0"] > 0).astype(int) + (df["NP_P1"] > 0).astype(int)
  + (df["NP_P2"] > 0).astype(int) + (df["NP_P3"] > 0).astype(int)
)
# 1.5 TTM NP growth: (sum P0..P3) vs (sum P4..P7)
ttm_now = df[["NP_P0","NP_P1","NP_P2","NP_P3"]].sum(axis=1, skipna=False)
ttm_prv = df[["NP_P4","NP_P5","NP_P6","NP_P7"]].sum(axis=1, skipna=False)
df["NP_TTM_growth"] = np.where(ttm_prv.abs() > 0,
                               (ttm_now - ttm_prv) / ttm_prv.abs(), np.nan).clip(-5, 5)
# 1.6 Margin deltas
df["NPM_delta"]  = df["NPM_P0"]  - df["NPM_P4"]
df["EBITM_delta"]= df["EBITM_P0"]- df["EBITM_P4"]
# 1.7 GPM slope (8Q linear regression)
GPM_COLS_ORDERED = [f"GPM_P{i}" for i in [7,6,5,4,3,2,1,0]]
gpm_mat = df[GPM_COLS_ORDERED].values.astype(float)
x = np.arange(8)
def slope_row(y):
    m = ~np.isnan(y)
    if m.sum() < 4: return np.nan
    xx = x[m]; yy = y[m]
    n = len(xx); sx = xx.sum(); sy = yy.sum()
    sxx = (xx*xx).sum(); sxy = (xx*yy).sum()
    denom = n*sxx - sx*sx
    return np.nan if denom == 0 else (n*sxy - sx*sy) / denom
df["GPM_slope"] = np.array([slope_row(r) for r in gpm_mat])

# 1.8 Operating efficiency deltas (improvement = positive)
df["AssetTurn_delta"] = df["AssetTurn_P0"] - df["AssetTurn_P4"]
df["InvTurn_delta"]   = df["InvTurn_P0"]   - df["InvTurn_P4"]
df["CashCycle_imp"]   = df["CashCycle_P4"] - df["CashCycle_P0"]  # shorter cycle = better
df["DSO_imp"]         = df["DSO_P4"]       - df["DSO_P0"]        # lower DSO = better

# v6 baseline growth indicators (for comparison)
df["GPM_change"] = np.where(df["GPM_P4"].abs() > 0,
                            (df["GPM_P0"] - df["GPM_P4"]) / df["GPM_P4"].abs(), np.nan)
df["NP_peak_ratio"] = np.where(df[NP_cols if False else ["NP_P0","NP_P1","NP_P2","NP_P3","NP_P4","NP_P5","NP_P6","NP_P7"]].max(axis=1) > 0,
                               df["NP_P0"] / df[["NP_P0","NP_P1","NP_P2","NP_P3","NP_P4","NP_P5","NP_P6","NP_P7"]].max(axis=1),
                               np.nan)
df["Rev_peak_ratio"] = np.where(df[["Revenue_P0","Revenue_P1","Revenue_P4"]].max(axis=1) > 0,
                                df["Revenue_P0"] / df[["Revenue_P0","Revenue_P1","Revenue_P4"]].max(axis=1),
                                np.nan)  # simplified

# Per-quarter ranks
candidates = ["NP_QoQ","NP_acceleration","NP_growing_streak","NP_positive_4Q","NP_TTM_growth",
              "NPM_delta","EBITM_delta","GPM_slope","AssetTurn_delta","InvTurn_delta","CashCycle_imp","DSO_imp",
              "GPM_change","NP_peak_ratio"]
print("\nComputing ranks for candidates ...")
for c in candidates:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

# Single-indicator IC
print(f"\n{'Indicator':<24}{'IC':>10}{'P1 IC':>10}{'P2 IC':>10}{'Stable?':>11}  Notes")
print("-"*80)
def ic_with_period(col, target="profit_3M"):
    rho_full, n = spearman_ic(df[col], df[target])
    p1 = df[df["year"]<=2019]; p2 = df[df["year"]>=2020]
    rho1, _ = spearman_ic(p1[col], p1[target])
    rho2, _ = spearman_ic(p2[col], p2[target])
    flag = "✓ stable" if rho1*rho2 > 0 and abs(rho1) > 0.02 and abs(rho2) > 0.02 else ("FLIP" if rho1*rho2<0 else "noise")
    return rho_full, rho1, rho2, flag, n

for c in candidates:
    rho, p1, p2, flag, n = ic_with_period(f"r_{c}")
    marker = " 🟢" if abs(rho) > 0.08 and flag == "✓ stable" else (" 🔵" if abs(rho) > 0.05 and flag == "✓ stable" else "")
    note = ""
    if c == "GPM_change": note = "(v6 baseline)"
    if c == "NP_peak_ratio": note = "(v6 baseline)"
    print(f"{c:<24}{rho:>+10.4f}{p1:>+10.4f}{p2:>+10.4f}{flag:>11}{marker}  {note}")

# Test composite candidates
print(f"\n--- Composite growth schemas ---")
# C1: v6 baseline (GPM_change + NP_peak + Rev_peak)
df["r_Rev_peak_ratio"] = df.groupby("quarter")["Rev_peak_ratio"].rank(pct=True, na_option="keep")
df["growth_v6"]      = df[["r_GPM_change","r_NP_peak_ratio","r_Rev_peak_ratio"]].mean(axis=1, skipna=True)
# C2: New candidate: NP_TTM_growth + NPM_delta + GPM_slope
df["growth_C2"] = df[["r_NP_TTM_growth","r_NPM_delta","r_GPM_slope"]].mean(axis=1, skipna=True)
# C3: Momentum + peak: NP_QoQ + NP_acceleration + NP_peak_ratio
df["growth_C3"] = df[["r_NP_QoQ","r_NP_acceleration","r_NP_peak_ratio"]].mean(axis=1, skipna=True)
# C4: Consistency + TTM: NP_positive_4Q + NP_TTM_growth + NP_peak_ratio
df["growth_C4"] = df[["r_NP_positive_4Q","r_NP_TTM_growth","r_NP_peak_ratio"]].mean(axis=1, skipna=True)
# C5: All-strong: NP_TTM_growth + NP_peak_ratio + NPM_delta
df["growth_C5"] = df[["r_NP_TTM_growth","r_NP_peak_ratio","r_NPM_delta"]].mean(axis=1, skipna=True)
# C6: NPM_delta + EBITM_delta + GPM_slope (pure margin trajectory)
df["growth_C6_margin"] = df[["r_NPM_delta","r_EBITM_delta","r_GPM_slope"]].mean(axis=1, skipna=True)

comps = [
    ("v6 baseline (GPM_change+NP_peak+Rev_peak)", "growth_v6"),
    ("C2: NP_TTM + NPM_delta + GPM_slope",        "growth_C2"),
    ("C3: NP_QoQ + acceleration + NP_peak",       "growth_C3"),
    ("C4: NP_positive_4Q + NP_TTM + NP_peak",     "growth_C4"),
    ("C5: NP_TTM + NP_peak + NPM_delta",          "growth_C5"),
    ("C6: NPM_delta + EBITM_delta + GPM_slope",   "growth_C6_margin"),
]
print(f"{'Composite':<45}{'IC':>10}{'P1':>10}{'P2':>10}{'Stable?':>11}")
print("-"*85)
for name, col in comps:
    rho, p1, p2, flag, _ = ic_with_period(col)
    marker = " 🟢" if abs(rho) > 0.08 else (" 🔵" if abs(rho) > 0.06 else "")
    print(f"{name:<45}{rho:>+10.4f}{p1:>+10.4f}{p2:>+10.4f}{flag:>11}{marker}")

# ═══════════════════════════════════════════════════════════════════════════
# PART 2: Sector-conditional IC
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("PART 2: Sector-conditional IC for top v6 indicators"); print("="*80)
# Top digit groups (per ICB)
# 0/1 = Materials, 2 = Industrials, 3 = Consumer Goods, 5 = Consumer Services, 7 = Utilities, 8 = Financials, 9 = Tech
sector_labels = {0:"Energy/Mat", 1:"Materials", 2:"Industrials", 3:"ConsGoods",
                 5:"ConsServ", 7:"Utilities", 8:"Financials", 9:"Tech"}
print("\nSector distribution:")
sec_dist = df["sector_top"].value_counts().sort_index()
for s, n in sec_dist.items():
    label = sector_labels.get(s, f"sec{s}")
    print(f"  {s} ({label}): {n}")

# Top indicators (smoothed_EY, ROE_Min5Y, NP_CV, Cash_MktCap, etc.) — need to recompute
# Compute the v6 winning indicators
df["NP_4Q_mean"] = df[["NP_P0","NP_P1","NP_P2","NP_P3"]].mean(axis=1, skipna=True)
df["MktCap"] = df["Close"] * df["OShares"]
df["smoothed_EY"] = (df["NP_4Q_mean"] / df["OShares"].replace(0,np.nan) / df["Close"].replace(0,np.nan)).clip(-1,1)
df["FCF_4Q"] = (df["CF_OA_P0"] + df["CF_OA_P1"] + df["CF_OA_P2"] + df["CF_OA_P3"]
              + df["CF_Invest_P0"] + df["CF_Invest_P1"] + df["CF_Invest_P2"] + df["CF_Invest_P3"])
df["FCF_yield"] = (df["FCF_4Q"] / df["MktCap"]).clip(-1,1)
# NP_CV
np_arr = df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
np_n = np.sum(~np.isnan(np_arr), axis=1)
with np.errstate(divide="ignore", invalid="ignore"):
    np_m = np.nanmean(np_arr, axis=1); np_s = np.nanstd(np_arr, axis=1, ddof=1)
    df["NP_CV"] = np.where(np_n>=6, np_s/np.maximum(np.abs(np_m), 1e6), np.nan).clip(max=10)

for c in ["smoothed_EY","FCF_yield","ROE_Min5Y","ROIC5Y","NP_CV","NP_peak_ratio"]:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
# Invert NP_CV (lower CV = better)
df["r_NP_CV_inv"] = 1 - df["r_NP_CV"]

print(f"\nIC by sector (full period, profit_3M):")
print(f"{'Indicator':<22}{'Energy':>9}{'Materials':>10}{'Industri':>10}{'ConsGds':>10}{'ConsSrv':>10}{'Utility':>10}{'Financ':>10}{'Tech':>10}")
print("-"*100)
indicators_to_test = [
    ("smoothed_EY",  "r_smoothed_EY"),
    ("ROE_Min5Y",    "r_ROE_Min5Y"),
    ("ROIC5Y",       "r_ROIC5Y"),
    ("Rev_CV (inv)", None),  # compute special
    ("NP_CV (inv)",  "r_NP_CV_inv"),
    ("NP_peak_ratio","r_NP_peak_ratio"),
    ("NP_TTM_growth","r_NP_TTM_growth"),
    ("FCF_yield",    "r_FCF_yield"),
]
# Compute Rev_CV separately
rev_arr = df[[f"Revenue_P{i}" for i in range(8)]].values.astype(float) if all(f"Revenue_P{i}" in df.columns for i in range(8)) else None
if rev_arr is not None:
    rev_n = np.sum(~np.isnan(rev_arr), axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        rev_m = np.nanmean(rev_arr, axis=1); rev_s = np.nanstd(rev_arr, axis=1, ddof=1)
        df["Rev_CV"] = np.where(rev_n>=6, rev_s/np.maximum(np.abs(rev_m), 1e6), np.nan).clip(max=10)
    df["r_Rev_CV_inv"] = 1 - df.groupby("quarter")["Rev_CV"].rank(pct=True, na_option="keep")
    indicators_to_test[3] = ("Rev_CV (inv)", "r_Rev_CV_inv")

sectors_to_show = [0,1,2,3,5,7,8,9]
for name, col in indicators_to_test:
    if col is None: continue
    row = f"{name:<22}"
    for s in sectors_to_show:
        sub = df[df["sector_top"]==s]
        if len(sub) < 50:
            row += f"{'n<50':>10}"
            continue
        rho, _ = spearman_ic(sub[col], sub["profit_3M"])
        row += f"{rho:>+10.3f}"
    print(row)

# ═══════════════════════════════════════════════════════════════════════════
# PART 3: Forward horizon (O6M, O1Y, O2Y from ticker_prune)
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("PART 3: Forward horizon (longer windows via ticker_prune)"); print("="*80)
# Universe with prune coverage
n_prune = df["O6M"].notna().sum()
print(f"Q4 rows with prune coverage (has O6M): {n_prune} / {len(df)}")
# Ensure all needed columns are ranked
for c in ["smoothed_EY","FCF_yield","ROE_Min5Y","ROIC5Y","NP_CV","NP_peak_ratio","NP_TTM_growth"]:
    if f"r_{c}" not in df.columns:
        df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
if "r_Rev_CV_inv" not in df.columns and "Rev_CV" in df.columns:
    df["r_Rev_CV_inv"] = 1 - df.groupby("quarter")["Rev_CV"].rank(pct=True, na_option="keep")
if "r_NP_CV_inv" not in df.columns and "NP_CV" in df.columns:
    df["r_NP_CV_inv"] = 1 - df.groupby("quarter")["NP_CV"].rank(pct=True, na_option="keep")
prune_df = df[df["O6M"].notna()].copy()
horizons = ["profit_3M","O6M","O1Y","O2Y"]
print(f"\nIC of top v6 indicators at different horizons (universe = prune coverage only):")
print(f"{'Indicator':<22}{'profit_3M':>11}{'O6M':>11}{'O1Y':>11}{'O2Y':>11}")
print("-"*68)
for name, col in [
    ("smoothed_EY",   "r_smoothed_EY"),
    ("ROE_Min5Y",     "r_ROE_Min5Y"),
    ("ROIC5Y",        "r_ROIC5Y"),
    ("NP_CV (inv)",   "r_NP_CV_inv"),
    ("Rev_CV (inv)",  "r_Rev_CV_inv"),
    ("NP_TTM_growth", "r_NP_TTM_growth"),
    ("NP_peak_ratio", "r_NP_peak_ratio"),
    ("FCF_yield",     "r_FCF_yield"),
]:
    row = f"{name:<22}"
    for h in horizons:
        if col not in prune_df.columns:
            row += f"{'N/A':>11}"
            continue
        rho, _ = spearman_ic(prune_df[col], prune_df[h])
        row += f"{rho:>+10.3f} " if not np.isnan(rho) else f"{'N/A':>11}"
    print(row)

# Also report sample sizes per horizon
print(f"\nSample size at each horizon:")
for h in horizons:
    n = prune_df[h].notna().sum()
    print(f"  {h}: N={n}")

# Also: do BAD indicators (e.g. raw PE) get worse with longer horizons?
print(f"\nNoise-check: v4 PE z-score at different horizons (should stay ~0 if true noise):")
if "PE" in df.columns:
    df["PE_z_v4"] = -df.groupby("quarter")["PE"].transform(lambda x: (x - x.median())/x.std())
    df["r_PE_z_v4"] = df.groupby("quarter")["PE_z_v4"].rank(pct=True, na_option="keep")
    prune_df["r_PE_z_v4"] = df.loc[prune_df.index, "r_PE_z_v4"]
    row = f"{'v4 PE_z_inv':<22}"
    for h in horizons:
        rho, _ = spearman_ic(prune_df["r_PE_z_v4"], prune_df[h])
        row += f"{rho:>+10.3f} "
    print(row)

print("\n" + "="*80); print("DONE"); print("="*80)
