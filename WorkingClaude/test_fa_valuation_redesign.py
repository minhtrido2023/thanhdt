#!/usr/bin/env python3
"""
test_fa_valuation_redesign.py
=============================
Current v4 valuation axis has IC = -0.001 (noise). But academic literature
strongly supports value premium. Explore redesigns before dropping.

Hypotheses:
  V1. Raw absolute valuation (1/PE, 1/PB, 1/PCF) — no mean-reversion assumption
  V2. Combined value composite (geometric mean of 1/PE + 1/PB + 1/PCF)
  V3. Magic Formula (Greenblatt): combined rank of ROIC + Earnings Yield
  V4. Conditional valuation: does PE work WITHIN quality tier?
  V5. Shiller-PE proxy: use 5Y avg earnings (NP_P0..P4 mean) instead of P0
  V6. FCF yield: (CF_OA - |CF_Invest|) / Market Cap
  V7. PB-only (lowest of the bunch) — sometimes single-best beats composite

Tests:
  - IC full period + period split (2014-19 vs 2020-26)
  - Conditional IC within tier subsets
  - Pull forward returns
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
    rho = s["x"].rank().corr(s["y"].rank(), method="pearson")
    return rho, len(s)

# Pull raw PE/PB/PCF + EPS, BVPS, OShares for market cap; CF_OA_P0..P4, CF_Invest_P0..P4
SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y,
    f.NP_R,
    f.PE, f.PB, f.PCF, f.EVEB,
    f.EPS, f.BVPS, f.OShares,
    f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4,
    f.Revenue_P0,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3,
    f.CF_OA_5Y, f.CF_Invest_5Y,
    SAFE_DIVIDE(f.PE - f.PE_MA5Y, f.PE_SD5Y) AS PE_self_z,
    SAFE_DIVIDE(f.PB - f.PB_MA5Y, f.PB_SD5Y) AS PB_self_z,
    CASE WHEN f.PE > 0 THEN SAFE_DIVIDE(f.NP_R, f.PE) ELSE NULL END AS growth_yield,
    t.Close,
    t.ICB_Code, t.profit_3M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2014-01-01" AND f.quarter LIKE "%Q4"
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching ..."); df = bq_query(SQL); print(f"  {len(df):,} rows")
df["year"] = pd.to_datetime(df["time"]).dt.year
df["ICB_Code"] = df["ICB_Code"].fillna(0)

# ─── Build new valuation indicators ────────────────────────────────────────
print("Building valuation alternatives ...")

# V1. Earnings/Book/Cashflow yields (inverse of multiple)
df["EY"]  = np.where(df["PE"] > 0,  1.0 / df["PE"],  np.nan)   # earnings yield
df["BY"]  = np.where(df["PB"] > 0,  1.0 / df["PB"],  np.nan)   # book yield
df["CFY"] = np.where(df["PCF"] > 0, 1.0 / df["PCF"], np.nan)  # cash-flow yield
df["EBITY"] = np.where(df["EVEB"] > 0, 1.0 / df["EVEB"], np.nan) # EBITDA yield

# V2. Composite value (mean of ranks of EY/BY/CFY/EBITY)
for c in ["EY","BY","CFY","EBITY"]:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
df["value_composite"] = df[[f"r_EY", f"r_BY", f"r_CFY", f"r_EBITY"]].mean(axis=1, skipna=True)

# V3. Magic Formula (Greenblatt): combined rank of ROIC + EY
df["r_ROIC5Y"] = df.groupby("quarter")["ROIC5Y"].rank(pct=True, na_option="keep")
df["magic_formula"] = (df["r_ROIC5Y"] + df["r_EY"]) / 2.0

# V5. Shiller-PE proxy: use 4Q earnings (NP_P0..P3 mean as smoothed EPS proxy)
df["NP_4Q_mean"] = df[["NP_P0","NP_P1","NP_P2","NP_P3"]].mean(axis=1, skipna=True)
# Smoothed EY: NP_4Q_mean × shares = smoothed earnings. Price = Close. So EY = (NP_4Q_mean × OShares) / (Close × OShares) = NP_4Q_mean / (Close × OShares × ratio)
# Simpler: use ratio of smoothed earnings to current earnings × current EY
# CAPE_proxy = NP_4Q_mean / |NP_P0| (smoothing factor) × EY when NP_P0 > 0
# Cleanest: smoothed_EPS = NP_4Q_mean / OShares; smoothed_EY = smoothed_EPS / Close
df["smoothed_EPS"] = df["NP_4Q_mean"] / df["OShares"].replace(0, np.nan)
df["smoothed_EY"]  = df["smoothed_EPS"] / df["Close"].replace(0, np.nan)
df["smoothed_EY"]  = df["smoothed_EY"].clip(lower=-1, upper=1)  # winsorize

# V6. FCF yield: (CF_OA_P0 + CF_Invest_P0) / MktCap (CF_Invest is negative for capex)
# Use 4Q sum to smooth
df["FCF_4Q"] = (df["CF_OA_P0"] + df["CF_OA_P1"] + df["CF_OA_P2"] + df["CF_OA_P3"]
              + df["CF_Invest_P0"] + df["CF_Invest_P1"] + df["CF_Invest_P2"] + df["CF_Invest_P3"])
df["MktCap"] = df["Close"] * df["OShares"]
df["FCF_yield"] = np.where(df["MktCap"] > 0, df["FCF_4Q"] / df["MktCap"], np.nan)
df["FCF_yield"] = df["FCF_yield"].clip(lower=-1, upper=1)

# Compute ranks for new indicators
print("Computing ranks ...")
for c in ["EY","BY","CFY","EBITY","value_composite","magic_formula","smoothed_EY","FCF_yield"]:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

# Existing v4 valuation indicators (for comparison)
df["PE_self_z"] = -df["PE_self_z"]   # original inversion (lower = better)
df["PB_self_z"] = -df["PB_self_z"]
df["growth_yield"] = df["growth_yield"].clip(-0.15, 0.15)

# Industry-relative
for col in ["PE","PB","PCF"]:
    grp = df.groupby(["quarter","ICB_Code"])[col]
    med=grp.transform("median"); sd=grp.transform("std")
    df[f"{col}_ind_z"] = -((df[col]-med)/sd.replace(0,np.nan))  # inverted
    df[f"r_{col}_ind_z"] = df.groupby("quarter")[f"{col}_ind_z"].rank(pct=True, na_option="keep")

df["r_PE_self_z"] = df.groupby("quarter")["PE_self_z"].rank(pct=True, na_option="keep")
df["r_PB_self_z"] = df.groupby("quarter")["PB_self_z"].rank(pct=True, na_option="keep")
df["r_growth_yield"] = df.groupby("quarter")["growth_yield"].rank(pct=True, na_option="keep")

# v4 composite valuation rank (mean of 6 indicators)
v4_val_cols = ["PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","growth_yield"]
df["v4_valuation"] = df[[f"r_{c}" for c in v4_val_cols]].mean(axis=1, skipna=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: IC comparison — single indicators
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("SECTION 1: IC of single valuation indicators"); print("="*80)
cands = [
    ("EY (1/PE) raw",             "r_EY"),
    ("BY (1/PB) raw",             "r_BY"),
    ("CFY (1/PCF) raw",           "r_CFY"),
    ("EBITY (1/EVEB) raw",        "r_EBITY"),
    ("Smoothed EY (Shiller-like)", "r_smoothed_EY"),
    ("FCF yield (4Q smoothed)",   "r_FCF_yield"),
    ("PE_self_z (v4)",            "r_PE_self_z"),
    ("PB_self_z (v4)",            "r_PB_self_z"),
    ("PE_ind_z (v4)",             "r_PE_ind_z"),
    ("PB_ind_z (v4)",             "r_PB_ind_z"),
    ("PCF_ind_z (v4)",            "r_PCF_ind_z"),
    ("growth_yield (v4)",         "r_growth_yield"),
]
print(f"\n{'Indicator':<35}{'IC':>10}{'P1 IC':>10}{'P2 IC':>10}{'Stable?':>11}{'N (full)':>10}")
print("-"*86)
for name, col in cands:
    rho_full, n_full = spearman_ic(df[col], df["profit_3M"])
    p1 = df[df["year"]<=2019]; p2 = df[df["year"]>=2020]
    rho1, _ = spearman_ic(p1[col], p1["profit_3M"])
    rho2, _ = spearman_ic(p2[col], p2["profit_3M"])
    flag = "✓" if rho1 * rho2 > 0 and abs(rho1) > 0.02 and abs(rho2) > 0.02 else ("FLIP" if rho1*rho2<0 else " noise")
    marker = " 🟢" if abs(rho_full) > 0.08 and flag == "✓" else (" 🔵" if abs(rho_full) > 0.05 and flag == "✓" else "")
    print(f"{name:<35}{rho_full:>+10.4f}{rho1:>+10.4f}{rho2:>+10.4f}{flag:>11}{n_full:>10}{marker}")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: IC of composites
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("SECTION 2: Composite valuation IC"); print("="*80)
comps = [
    ("v4 valuation (6-indicator avg)",  "v4_valuation"),
    ("value_composite (4 yields avg)",  "r_value_composite"),
    ("magic_formula (ROIC + EY)",       "r_magic_formula"),
    ("EY only (raw earnings yield)",    "r_EY"),
    ("BY only (raw book yield)",        "r_BY"),
    ("(EY + BY)/2",                     None),  # special: compute inline
    ("(EY + BY + FCFY)/3",              None),  # special
]
df["EY_BY"]      = (df["r_EY"] + df["r_BY"]) / 2.0
df["EY_BY_FCFY"] = (df["r_EY"] + df["r_BY"] + df["r_FCF_yield"]) / 3.0
df["r_EY_BY"]      = df.groupby("quarter")["EY_BY"].rank(pct=True, na_option="keep")
df["r_EY_BY_FCFY"] = df.groupby("quarter")["EY_BY_FCFY"].rank(pct=True, na_option="keep")
comp_extra = [
    ("(EY + BY)/2",        "r_EY_BY"),
    ("(EY + BY + FCFY)/3", "r_EY_BY_FCFY"),
]
print(f"\n{'Composite':<40}{'IC (full)':>11}{'P1 IC':>10}{'P2 IC':>10}{'Stable?':>11}")
print("-"*82)
for name, col in [("v4 valuation (6-indicator avg)",  "v4_valuation"),
                  ("value_composite (4 yields avg)",  "r_value_composite"),
                  ("magic_formula (ROIC + EY)",       "r_magic_formula"),
                  *comp_extra]:
    rho_full, _ = spearman_ic(df[col], df["profit_3M"])
    p1 = df[df["year"]<=2019]; p2 = df[df["year"]>=2020]
    rho1, _ = spearman_ic(p1[col], p1["profit_3M"])
    rho2, _ = spearman_ic(p2[col], p2["profit_3M"])
    flag = "✓" if rho1 * rho2 > 0 and abs(rho1) > 0.02 and abs(rho2) > 0.02 else ("FLIP" if rho1*rho2<0 else " noise")
    marker = " 🟢" if abs(rho_full) > 0.08 and flag == "✓" else ""
    print(f"{name:<40}{rho_full:>+11.4f}{rho1:>+10.4f}{rho2:>+10.4f}{flag:>11}{marker}")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: Conditional valuation — does it work within quality tiers?
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("SECTION 3: Conditional valuation (within quality subgroup)"); print("="*80)
# Use ROIC5Y rank as quality proxy
df["quality_q"] = pd.qcut(df["ROIC5Y"].rank(pct=True), 4, labels=["Q4_low","Q3","Q2","Q1_high"], duplicates="drop")
print(f"\nIC of EY (raw earnings yield) within each quality quartile:")
print(f"{'Quality bucket':<20}{'N':>6}{'IC':>10}{'Median profit':>15}")
print("-"*55)
for ql in ["Q1_high","Q2","Q3","Q4_low"]:
    sub = df[df["quality_q"]==ql]
    rho, n = spearman_ic(sub["r_EY"], sub["profit_3M"])
    med = sub["profit_3M"].median()
    print(f"{ql:<20}{n:>6}{rho:>+10.4f}{med:>+14.2f}%")

print(f"\nIC of EY within each shareholder-yield bucket (DY adj):")
# Use DY_adj proxy. Approx: DY > 5% vs DY <= 5%
df["yields_div"] = pd.cut(df["EY"], bins=[-1,0.04,0.08,0.12,1], labels=["EY≤4%","EY 4-8%","EY 8-12%","EY>12%"], duplicates="drop")
print(f"\nForward return by EY bin (absolute thresholds):")
print(f"{'EY bin':<14}{'N':>6}{'Median':>10}{'Mean':>10}{'WR':>8}")
for label in ["EY≤4%","EY 4-8%","EY 8-12%","EY>12%"]:
    g = df[df["yields_div"]==label].dropna(subset=["profit_3M"])
    if len(g)==0: continue
    med = g["profit_3M"].median(); mean = g["profit_3M"].mean()
    wr = (g["profit_3M"]>0).mean()*100
    print(f"{label:<14}{len(g):>6}{med:>+9.2f}%{mean:>+9.2f}%{wr:>7.1f}%")

print(f"\nForward return by BY bin (1/PB):")
df["yields_book"] = pd.cut(df["BY"], bins=[-1,0.4,0.7,1.0,5], labels=["PB>2.5","PB 1.4-2.5","PB 1-1.4","PB<1"], duplicates="drop")
print(f"{'PB bin':<14}{'N':>6}{'Median':>10}{'Mean':>10}{'WR':>8}")
for label in ["PB>2.5","PB 1.4-2.5","PB 1-1.4","PB<1"]:
    g = df[df["yields_book"]==label].dropna(subset=["profit_3M"])
    if len(g)==0: continue
    med = g["profit_3M"].median(); mean = g["profit_3M"].mean()
    wr = (g["profit_3M"]>0).mean()*100
    print(f"{label:<14}{len(g):>6}{med:>+9.2f}%{mean:>+9.2f}%{wr:>7.1f}%")

print(f"\nMagic Formula deciles (combined rank of ROIC + EY, 0=worst, 9=best):")
df["mf_decile"] = pd.qcut(df["r_magic_formula"], 10, labels=False, duplicates="drop")
print(f"{'Decile':<8}{'N':>6}{'Median':>10}{'Mean':>10}{'WR':>8}")
for d in range(10):
    g = df[df["mf_decile"]==d].dropna(subset=["profit_3M"])
    if len(g)==0: continue
    med = g["profit_3M"].median(); mean = g["profit_3M"].mean()
    wr = (g["profit_3M"]>0).mean()*100
    label = f"D{d}" + (" (best)" if d == 9 else " (worst)" if d==0 else "")
    print(f"{label:<8}{len(g):>6}{med:>+9.2f}%{mean:>+9.2f}%{wr:>7.1f}%")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: Tier-conditional — does v4 valuation work for A tier only?
# ═══════════════════════════════════════════════════════════════════════════
# Build v4 tier (need other axes — skip and just check if PE-related signals work
# WITHIN top-quality stocks)
print("\n" + "="*80); print("SECTION 4: Valuation within top quality (ROIC + ROE filter)"); print("="*80)
# Top quality = top 25% ROIC5Y + top 25% ROE_Min5Y
quality_top = df[(df["ROIC5Y"] > df["ROIC5Y"].quantile(0.50)) &
                 (df["ROE_Min5Y"] > df["ROE_Min5Y"].quantile(0.50))]
print(f"Universe restricted to top 50% × top 50% quality (ROIC × ROE): N={len(quality_top)}")
for name, col in [("EY raw", "r_EY"), ("BY raw", "r_BY"),
                  ("CFY raw", "r_CFY"), ("FCF yield", "r_FCF_yield"),
                  ("value_composite", "r_value_composite"),
                  ("v4_valuation", "v4_valuation")]:
    rho, n = spearman_ic(quality_top[col], quality_top["profit_3M"])
    print(f"  {name:<22} IC={rho:+.4f}  N={n}")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: Year-by-year IC for the new best indicators
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("SECTION 5: Year-by-year IC for new best indicators"); print("="*80)
years = sorted(df["year"].unique())
print(f"\n{'Indicator':<28}" + "".join([f"{y:>7}" for y in years[:13]]))
print("-"*(28 + 7*min(13,len(years))))
for name, col in [("EY (1/PE)", "r_EY"),
                  ("BY (1/PB)", "r_BY"),
                  ("Magic Formula", "r_magic_formula"),
                  ("FCF yield", "r_FCF_yield"),
                  ("v4_valuation", "v4_valuation")]:
    row = f"{name:<28}"
    for y in years[:13]:
        sub = df[df["year"]==y]
        rho, _ = spearman_ic(sub[col], sub["profit_3M"])
        row += f"{rho:+6.2f} " if not np.isnan(rho) else "   N/A "
    print(row)

print("\n" + "="*80); print("DONE"); print("="*80)
