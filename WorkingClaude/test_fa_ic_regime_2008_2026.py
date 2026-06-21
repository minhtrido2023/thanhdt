#!/usr/bin/env python3
"""
test_fa_ic_regime_2008_2026.py
==============================
Phase 1: IC stability diagnostic across regimes 2008-2026.

Question: which FA indicators are timeless (work in any regime) vs
regime-dependent (work only post-2014)?

Sub-periods:
  P1: 2008-2013 (pre-modern, GFC + recovery + sideways)
  P2: 2014-2018 (maturation phase)
  P3: 2019-2023 (modern + COVID + crash)
  P4: 2024-2026 (recent OOS)

For each top v8c_final indicator: compute IC per sub-period.
Identify:
  - TIMELESS: positive IC across all 4 sub-periods (deploy with confidence)
  - REGIME-DEPENDENT: works only in some periods (caveat)
  - ANTI-SIGNAL EARLY: positive recent, negative pre-2014 (speculation era diff)
  - BROKEN: not stable in any direction
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
    if len(s) < 30: return float("nan"), 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

# Pull 2008-2026 Q4 data
SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE_Trailing, f.FSCORE,
    f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y,
    SAFE_DIVIDE(f.CF_OA_5Y + f.CF_Invest_5Y, ABS(f.CF_OA_5Y)) AS FCF_OA_ratio,
    f.Debt_Eq_P0, f.IntCov_P0, f.CashR_P0,
    f.PE, f.PB, f.PCF, f.OShares,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
    f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7,
    f.AdvCust_P0, f.AdvCust_P4,
    f.UnearnRev_P0,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3,
    f.StDebt_P0, f.LtDebt_P0, f.Cash_P0, f.EBITDA_P0,
    CASE WHEN GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0, GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    t.Close, t.ICB_Code, t.profit_3M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2008-01-01" AND f.quarter LIKE "%Q4"
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching 2008-2026 Q4 data ..."); df = bq_query(SQL); print(f"  {len(df):,} rows")
df["year"] = pd.to_datetime(df["time"]).dt.year
df["ICB_Code"] = df["ICB_Code"].fillna(0).astype(int)

# Build indicators
df["MktCap"] = df["Close"] * df["OShares"]
df["NP_4Q_mean"] = df[[f"NP_P{i}" for i in range(4)]].mean(axis=1, skipna=True)
df["smoothed_EY"] = (df["NP_4Q_mean"] / df["OShares"].replace(0,np.nan) / df["Close"].replace(0,np.nan)).clip(-1,1)
df["EY"] = np.where(df["PE"]>0, 1.0/df["PE"], np.nan)
df["BY"] = np.where(df["PB"]>0, 1.0/df["PB"], np.nan)
df["CFY"] = np.where(df["PCF"]>0, 1.0/df["PCF"], np.nan)
df["FCF_4Q"] = df["CF_OA_P0"] + df["CF_OA_P1"] + df["CF_OA_P2"] + df["CF_OA_P3"] \
              + df["CF_Invest_P0"] + df["CF_Invest_P1"] + df["CF_Invest_P2"] + df["CF_Invest_P3"]
df["FCF_yield"] = (df["FCF_4Q"] / df["MktCap"]).clip(-1, 1)

# Stability
np_arr = df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
rev_arr = df[[f"Revenue_P{i}" for i in range(8)]].values.astype(float)
np_n = np.sum(~np.isnan(np_arr),axis=1); rev_n = np.sum(~np.isnan(rev_arr),axis=1)
with np.errstate(divide="ignore",invalid="ignore"):
    np_m = np.nanmean(np_arr,axis=1); np_s = np.nanstd(np_arr,axis=1,ddof=1)
    rev_m = np.nanmean(rev_arr,axis=1); rev_s = np.nanstd(rev_arr,axis=1,ddof=1)
    df["NP_CV_inv"] = -np.where(np_n>=6, np_s/np.maximum(np.abs(np_m),1e6), np.nan).clip(max=10)
    df["Rev_CV_inv"] = -np.where(rev_n>=6, rev_s/np.maximum(np.abs(rev_m),1e6), np.nan).clip(max=10)

# Health
df["NetDebt"] = df["StDebt_P0"].fillna(0)+df["LtDebt_P0"].fillna(0)-df["Cash_P0"].fillna(0)
df["NetDebt_EBITDA_inv"] = -np.where(df["EBITDA_P0"]>0, df["NetDebt"]/df["EBITDA_P0"], np.nan).clip(-20,50)
df["Cash_MktCap"] = np.where(df["MktCap"]>0, df["Cash_P0"]/df["MktCap"], np.nan).clip(-1,5)
df["IntCov_inv"] = -df["IntCov_P0"]
df["Debt_Eq_inv"] = -df["Debt_Eq_P0"]

# Magic Formula
df["r_ROIC5Y_q"] = df.groupby("quarter")["ROIC5Y"].rank(pct=True, na_option="keep")
df["r_EY_q"] = df.groupby("quarter")["EY"].rank(pct=True, na_option="keep")
df["magic_formula"] = (df["r_ROIC5Y_q"] + df["r_EY_q"]) / 2.0

# Pre-sales
def sd(num, den):
    return np.where(np.abs(den)>1e-3, num/den.replace(0,np.nan), np.nan)
df["AdvCust_MktCap_yld"] = sd(df["AdvCust_P0"], df["MktCap"]).clip(-1, 20)
df["AdvCust_YoY"] = sd(df["AdvCust_P0"]-df["AdvCust_P4"], df["AdvCust_P4"].abs()).clip(-5, 20)

# DY adj
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"]*_mult

# Define sub-periods
def period(y):
    if y <= 2013: return "P1_2008-13"
    if y <= 2018: return "P2_2014-18"
    if y <= 2023: return "P3_2019-23"
    return "P4_2024-26"
df["period"] = df["year"].apply(period)

# Sample sizes per period
print("\nSample sizes per period (with profit_3M):")
for p in ["P1_2008-13","P2_2014-18","P3_2019-23","P4_2024-26"]:
    sub = df[(df["period"]==p)].dropna(subset=["profit_3M"])
    print(f"  {p}: N={len(sub):,}")

# ─── IC per indicator per period ─────────────────────────────────────────
INDICATORS = [
    # Quality
    ("ROIC5Y",          "ROIC5Y"),
    ("ROE_Min5Y",       "ROE_Min5Y"),
    ("ROE_Trailing",    "ROE_Trailing"),
    ("FSCORE",          "FSCORE"),
    # Stability
    ("NP_CV (inv)",     "NP_CV_inv"),
    ("Rev_CV (inv)",    "Rev_CV_inv"),
    # Cash
    ("CF_OA_5Y",        "CF_OA_5Y"),
    ("CFOA_NP",         "CFOA_NP"),
    ("FCF_OA_ratio",    "FCF_OA_ratio"),
    ("FCF_yield",       "FCF_yield"),
    # Shareholder
    ("DY_adj",          "DY_adj"),
    ("Dividend_Min3Y",  "Dividend_Min3Y"),
    # Growth
    ("NP_R",            "NP_R"),
    ("Revenue_YoY",     "Revenue_YoY_P0"),
    ("GPM_change",      "GPM_change"),
    ("NP_peak_ratio",   "NP_peak_ratio"),
    # Health (rescued)
    ("Cash_MktCap",     "Cash_MktCap"),
    ("NetDebt_EBITDA_inv","NetDebt_EBITDA_inv"),
    ("IntCov_inv",      "IntCov_inv"),
    ("Debt_Eq_inv (v4)","Debt_Eq_inv"),
    # Valuation
    ("smoothed_EY",     "smoothed_EY"),
    ("EY (1/PE)",       "EY"),
    ("BY (1/PB)",       "BY"),
    ("CFY (1/PCF)",     "CFY"),
    ("magic_formula",   "magic_formula"),
    # Pre-sales (new)
    ("AdvCust_MktCap_yld","AdvCust_MktCap_yld"),
    ("AdvCust_YoY",     "AdvCust_YoY"),
]

# Compute ranks per quarter (so IC is cross-sectional)
print("\nComputing per-quarter ranks ...")
for name, col in INDICATORS:
    df[f"r_{col}"] = df.groupby("quarter")[col].rank(pct=True, na_option="keep")

PERIODS = ["P1_2008-13","P2_2014-18","P3_2019-23","P4_2024-26"]
print("\n" + "="*100)
print("IC by sub-period — indicators that are TIMELESS vs REGIME-DEPENDENT")
print("="*100)
print(f"\n{'Indicator':<24}", end="")
for p in PERIODS: print(f"{p[3:]:>11}", end="")
print(f"{'FULL':>10}{'Verdict':>22}")
print("-"*(24 + 11*4 + 10 + 22))

results = []
for name, col in INDICATORS:
    rcol = f"r_{col}"
    ics = []
    ns = []
    for p in PERIODS:
        sub = df[df["period"]==p]
        rho, n = spearman_ic(sub[rcol], sub["profit_3M"])
        ics.append(rho); ns.append(n)
    # Full
    rho_full, n_full = spearman_ic(df[rcol], df["profit_3M"])

    # Classify
    pos_periods = sum(1 for ic in ics if not np.isnan(ic) and ic > 0.03)
    neg_periods = sum(1 for ic in ics if not np.isnan(ic) and ic < -0.03)
    valid_periods = sum(1 for ic in ics if not np.isnan(ic))
    if pos_periods == valid_periods and valid_periods >= 3:
        verdict = "🟢 TIMELESS"
    elif pos_periods >= 3 and neg_periods == 0:
        verdict = "🔵 mostly positive"
    elif neg_periods == valid_periods and valid_periods >= 3:
        verdict = "❌ always anti"
    elif pos_periods > 0 and neg_periods > 0:
        verdict = "⚠ regime-flip"
    elif pos_periods >= 2 and neg_periods == 0:
        verdict = "  partial+"
    else:
        verdict = "  noise"

    row = f"{name:<24}"
    for ic in ics:
        row += f"{ic:>+10.3f} " if not np.isnan(ic) else f"{'n/a':>11}"
    row += f"{rho_full:>+10.3f}  {verdict:<20}"
    print(row)
    results.append({"indicator":name, "P1":ics[0], "P2":ics[1], "P3":ics[2], "P4":ics[3],
                    "FULL":rho_full, "verdict":verdict})

# Sample sizes per period
ns_row = f"{'(N per period)':<24}"
for p in PERIODS:
    sub = df[(df["period"]==p)].dropna(subset=["profit_3M"])
    ns_row += f"{len(sub):>11}"
print(ns_row)

# ─── Axis-level IC per period ────────────────────────────────────────────
print("\n" + "="*80); print("AXIS-LEVEL IC per period (v8c_final composites)"); print("="*80)

# Build axes (using within-quarter ranks; simple equal-weight within axis)
AXES = {
    "quality_v6b":     ["ROIC5Y","ROE_Min5Y"],          # drop FSCORE
    "stability_v4":    ["NP_CV_inv","Rev_CV_inv"],
    "cash_v4":         ["CF_OA_5Y","CFOA_NP"],
    "shareholder_v4":  ["DY_adj","Dividend_Min3Y","FCF_OA_ratio"],
    "growth_v6b":      ["GPM_change","NP_peak_ratio"],   # drop NP_R/Rev_YoY
    "health_v4 (old)": ["Debt_Eq_inv","IntCov_P0","CashR_P0"],
    "health_v6 (new)": ["Cash_MktCap","NetDebt_EBITDA_inv","IntCov_inv"],
    "valuation_v4":    ["PE","PB"],                       # raw
    "valuation_v6":    ["smoothed_EY","FCF_yield","magic_formula"],
    "presales (new)":  ["AdvCust_MktCap_yld"],
}
# For raw PE/PB in v4 axis use negative rank (cheap = high rank)
# Make sure ranks exist
need_rank = set()
for cols in AXES.values(): need_rank.update(cols)
for c in need_rank:
    if f"r_{c}" not in df.columns:
        # Invert for valuation: lower PE/PB = better → negate
        if c in ("PE","PB","IntCov_P0","CashR_P0"):
            df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
            # For PE/PB: lower = better; we want high rank = good, so invert
            if c in ("PE","PB"):
                df[f"r_{c}"] = 1 - df[f"r_{c}"]
        else:
            df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

for axis, cols in AXES.items():
    rank_cols = [f"r_{c}" for c in cols]
    df[f"ax_{axis}"] = df[rank_cols].mean(axis=1, skipna=True)

print(f"\n{'Axis':<26}", end="")
for p in PERIODS: print(f"{p[3:]:>11}", end="")
print(f"{'FULL':>10}")
print("-"*(26 + 11*4 + 10))
for axis in AXES:
    row = f"{axis:<26}"
    for p in PERIODS:
        sub = df[df["period"]==p]
        rho, _ = spearman_ic(sub[f"ax_{axis}"], sub["profit_3M"])
        row += f"{rho:>+10.3f} " if not np.isnan(rho) else f"{'n/a':>11}"
    rho_full, _ = spearman_ic(df[f"ax_{axis}"], df["profit_3M"])
    row += f"{rho_full:>+10.3f}"
    print(row)

# ─── Save & summary ────────────────────────────────────────────────────────
pd.DataFrame(results).to_csv("data/fa_ic_regime_results.csv", index=False)
print("\nSaved fa_ic_regime_results.csv")

# Categorize
print("\n" + "="*80); print("SUMMARY: indicators by regime stability"); print("="*80)
print("\n🟢 TIMELESS (positive in all 4 periods, IC>0.03):")
for r in results:
    if r["verdict"] == "🟢 TIMELESS":
        print(f"  {r['indicator']:<24} P1={r['P1']:+.2f} P2={r['P2']:+.2f} P3={r['P3']:+.2f} P4={r['P4']:+.2f}  FULL={r['FULL']:+.3f}")

print("\n🔵 Mostly positive (3 of 4 periods):")
for r in results:
    if r["verdict"] == "🔵 mostly positive":
        print(f"  {r['indicator']:<24} P1={r['P1']:+.2f} P2={r['P2']:+.2f} P3={r['P3']:+.2f} P4={r['P4']:+.2f}  FULL={r['FULL']:+.3f}")

print("\n⚠ REGIME-FLIP (positive in some, negative in others):")
for r in results:
    if r["verdict"] == "⚠ regime-flip":
        print(f"  {r['indicator']:<24} P1={r['P1']:+.2f} P2={r['P2']:+.2f} P3={r['P3']:+.2f} P4={r['P4']:+.2f}  FULL={r['FULL']:+.3f}")

print("\n❌ Always anti (4 periods negative):")
for r in results:
    if r["verdict"] == "❌ always anti":
        print(f"  {r['indicator']:<24} P1={r['P1']:+.2f} P2={r['P2']:+.2f} P3={r['P3']:+.2f} P4={r['P4']:+.2f}  FULL={r['FULL']:+.3f}")

print("\n" + "="*80); print("DONE"); print("="*80)
