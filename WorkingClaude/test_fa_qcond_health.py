#!/usr/bin/env python3
"""
test_fa_qcond_health.py
=======================
Two explorations in parallel:

PART 1 — Quality-conditional valuation (Option C from session)
  Hypothesis: value premium splits by quality:
    Low-quality: use raw EY + BY (mean reversion plays)
    High-quality: use FCF Yield + EBITY (cash-based; PE traps avoided)
  Compare vs Option B (uniform composite of Smoothed_EY + FCF + Magic Formula)

PART 2 — Health axis rescue
  Current health IC = -0.045 (anti-signal).
  Test:
    a) Absolute thresholds (sweet spot, U-shape)
    b) Net debt / EBITDA instead of D/E
    c) Delta-debt (debt change YoY)
    d) Quality-conditional health
    e) Bin-based forward returns (where do D/E, IntCov bins peak?)
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

# Pull additional debt-detail columns for health redesign
SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y,
    f.NP_R,
    f.PE, f.PB, f.PCF, f.EVEB,
    f.EPS, f.BVPS, f.OShares,
    f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3,
    f.Debt_Eq_P0, f.Debt_Eq_P4,
    f.IntCov_P0, f.IntCov_P4,
    f.CashR_P0, f.CashR_P4,
    f.StDebt_P0, f.LtDebt_P0, f.Cash_P0, f.EBITDA_P0,
    f.STLTDebt_Eq_P0, f.STLTDebt_Eq_P4,
    f.FinLev_P0, f.FinLev_P4,
    f.totalAsset_P0,
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

# Build core derived columns
df["NP_4Q_mean"] = df[["NP_P0","NP_P1","NP_P2","NP_P3"]].mean(axis=1, skipna=True)
df["MktCap"] = df["Close"] * df["OShares"]
df["smoothed_EPS"] = df["NP_4Q_mean"] / df["OShares"].replace(0, np.nan)
df["smoothed_EY"]  = (df["smoothed_EPS"] / df["Close"].replace(0, np.nan)).clip(-1, 1)
df["EY"]  = np.where(df["PE"] > 0,  1.0 / df["PE"],  np.nan)
df["BY"]  = np.where(df["PB"] > 0,  1.0 / df["PB"],  np.nan)
df["CFY"] = np.where(df["PCF"] > 0, 1.0 / df["PCF"], np.nan)
df["EBITY"] = np.where(df["EVEB"] > 0, 1.0 / df["EVEB"], np.nan)
df["FCF_4Q"] = (df["CF_OA_P0"] + df["CF_OA_P1"] + df["CF_OA_P2"] + df["CF_OA_P3"]
              + df["CF_Invest_P0"] + df["CF_Invest_P1"] + df["CF_Invest_P2"] + df["CF_Invest_P3"])
df["FCF_yield"] = np.where(df["MktCap"] > 0, df["FCF_4Q"] / df["MktCap"], np.nan).clip(-1, 1)

# Ranks
for c in ["EY","BY","CFY","EBITY","smoothed_EY","FCF_yield","ROIC5Y","ROE_Min5Y"]:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

# ═══════════════════════════════════════════════════════════════════════════
# PART 1 — Quality-conditional valuation
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("PART 1: Quality-conditional valuation"); print("="*80)

# Quality bucket from ROIC5Y rank within quarter
df["quality_tile"] = df.groupby("quarter")["ROIC5Y"].transform(
    lambda x: pd.qcut(x.rank(pct=True), 4, labels=False, duplicates="drop"))
# 0 = Q4 low, 3 = Q1 high

# Option B (uniform composite): equal-weight smoothed_EY + FCF_yield + Magic Formula
df["magic_formula"] = (df["r_ROIC5Y"] + df["r_EY"]) / 2.0
df["r_magic_formula"] = df.groupby("quarter")["magic_formula"].rank(pct=True, na_option="keep")
df["optB_val"] = (df["r_smoothed_EY"] + df["r_FCF_yield"] + df["r_magic_formula"]) / 3.0

# Option C: conditional
# Low quality (tile 0,1): use raw EY + BY rank
# High quality (tile 2,3): use FCF_yield + EBITY (cash-based)
df["r_EY_BY"]      = ((df["r_EY"] + df["r_BY"]) / 2.0)
df["r_FCFY_EBITY"] = ((df["r_FCF_yield"] + df["r_EBITY"]) / 2.0)
df["optC_val"] = np.where(df["quality_tile"] <= 1,
                          df["r_EY_BY"].values,
                          df["r_FCFY_EBITY"].values)

# Option C2: more granular (4-way)
def optC2(row):
    t = row["quality_tile"]
    if pd.isna(t): return np.nan
    if t == 0:   return (row["r_EY"] + row["r_BY"]) / 2          # Q4 low: pure value play
    elif t == 1: return (row["r_EY"] + row["r_BY"] + row["r_FCF_yield"]) / 3  # Q3
    elif t == 2: return (row["r_smoothed_EY"] + row["r_FCF_yield"]) / 2       # Q2
    else:        return (row["r_FCF_yield"] + row["r_EBITY"]) / 2             # Q1 high
df["optC2_val"] = df.apply(optC2, axis=1)

# Option C3: smoothed weight by quality (continuous)
# weight_value_part = (1 - quality_rank) * pure_value + quality_rank * cash_value
qr = df.groupby("quarter")["ROIC5Y"].rank(pct=True).fillna(0.5).values
val_pure  = ((df["r_EY"] + df["r_BY"]) / 2.0).values
val_cash  = ((df["r_FCF_yield"] + df["r_EBITY"]) / 2.0).values
df["optC3_val"] = (1 - qr) * val_pure + qr * val_cash

# Compare ICs
print(f"\n{'Variant':<48}{'IC':>10}{'P1':>10}{'P2':>10}{'Stable?':>11}")
print("-"*88)
for name, col in [
    ("v4 valuation composite (baseline)", "optB_val"),  # placeholder, will override
    ("OPT-B: uniform composite (sm_EY+FCFY+MF)",   "optB_val"),
    ("OPT-C: 2-way conditional (low=PE/PB; high=FCFY/EBITY)", "optC_val"),
    ("OPT-C2: 4-way granular conditional", "optC2_val"),
    ("OPT-C3: continuous quality weight", "optC3_val"),
    ("Smoothed EY alone (reference)",     "r_smoothed_EY"),
    ("FCF yield alone (reference)",       "r_FCF_yield"),
]:
    if name.startswith("v4"): continue  # skip placeholder
    rho_full, n = spearman_ic(df[col], df["profit_3M"])
    p1 = df[df["year"]<=2019]; p2 = df[df["year"]>=2020]
    rho1, _ = spearman_ic(p1[col], p1["profit_3M"])
    rho2, _ = spearman_ic(p2[col], p2["profit_3M"])
    flag = "✓ stable" if rho1*rho2 > 0 and abs(rho1) > 0.02 and abs(rho2) > 0.02 else ("FLIP" if rho1*rho2<0 else "noise")
    mark = " 🟢" if abs(rho_full) > 0.10 and flag == "✓ stable" else ""
    print(f"{name:<48}{rho_full:>+10.4f}{rho1:>+10.4f}{rho2:>+10.4f}{flag:>11}{mark}")

# Conditional drilldown — IC of optC within each quality tile (should be similar across tiles)
print(f"\nOPT-C2 IC within each quality tile (should be balanced):")
for tl in [0,1,2,3]:
    sub = df[df["quality_tile"]==tl]
    rho, n = spearman_ic(sub["optC2_val"], sub["profit_3M"])
    label = {0:"Q4 low",1:"Q3",2:"Q2",3:"Q1 high"}[tl]
    print(f"  Tile {tl} ({label})  N={n:4d}  IC={rho:+.4f}")

# ═══════════════════════════════════════════════════════════════════════════
# PART 2 — Health axis rescue
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("PART 2: Health axis rescue (currently IC = -0.045)"); print("="*80)

# Build new health indicators
# H1. Net Debt / EBITDA
df["TotalDebt"] = df["StDebt_P0"].fillna(0) + df["LtDebt_P0"].fillna(0)
df["NetDebt"]   = df["TotalDebt"] - df["Cash_P0"].fillna(0)
df["NetDebt_EBITDA"] = np.where(df["EBITDA_P0"] > 0,
                                df["NetDebt"] / df["EBITDA_P0"], np.nan).clip(-20, 50)
# H2. Debt change YoY (delta)
df["DEbt_delta"] = df["Debt_Eq_P0"] - df["Debt_Eq_P4"]  # +ve = added debt
# H3. STLT Debt/Eq (alt to D/E)
df["STLT_DE_delta"] = df["STLTDebt_Eq_P0"] - df["STLTDebt_Eq_P4"]
# H4. Cash / MktCap (cash-cushion yield)
df["Cash_MktCap"] = np.where(df["MktCap"] > 0, df["Cash_P0"] / df["MktCap"], np.nan).clip(-1, 5)
# H5. Total debt / Total Asset (leverage ratio)
df["DA_ratio"] = np.where(df["totalAsset_P0"] > 0, df["TotalDebt"] / df["totalAsset_P0"], np.nan).clip(0, 2)

# Compute IC for each raw indicator (un-inverted, original sign)
print(f"\nRaw health indicator IC (BEFORE any inversion):")
print(f"{'Indicator':<28}{'IC':>10}{'P1':>10}{'P2':>10}{'Direction good?':>20}")
print("-"*78)
candidates = [
    ("Debt_Eq_P0",      "Debt_Eq_P0"),
    ("IntCov_P0",       "IntCov_P0"),
    ("CashR_P0",        "CashR_P0"),
    ("NetDebt/EBITDA",  "NetDebt_EBITDA"),
    ("Debt change (Δ D/E YoY)", "DEbt_delta"),
    ("STLT D/E",        "STLTDebt_Eq_P0"),
    ("STLT D/E change", "STLT_DE_delta"),
    ("Cash/MktCap",     "Cash_MktCap"),
    ("Debt/Asset",      "DA_ratio"),
    ("FinLev_P0",       "FinLev_P0"),
]
for name, col in candidates:
    df[f"r_{col}"] = df.groupby("quarter")[col].rank(pct=True, na_option="keep")
    rho_full, n = spearman_ic(df[f"r_{col}"], df["profit_3M"])
    p1 = df[df["year"]<=2019]; p2 = df[df["year"]>=2020]
    rho1, _ = spearman_ic(p1[f"r_{col}"], p1["profit_3M"])
    rho2, _ = spearman_ic(p2[f"r_{col}"], p2["profit_3M"])
    # Original direction: + IC means HIGHER value → BETTER returns
    # For debt-related: positive IC unexpected (more debt = better?)
    if rho_full > 0.04: interp = "+ HIGH = good (unusual)"
    elif rho_full < -0.04: interp = "- LOW = good (expected)"
    else: interp = "  ~noise"
    print(f"{name:<28}{rho_full:>+10.4f}{rho1:>+10.4f}{rho2:>+10.4f}  {interp}")

# Forward return by bin — find sweet spot
print(f"\nForward return by Debt_Eq bin (absolute thresholds):")
bins = [-1, 0.1, 0.3, 0.6, 1.0, 1.5, 100]
labels = ["DE<0.1","DE 0.1-0.3","DE 0.3-0.6","DE 0.6-1","DE 1-1.5","DE>1.5"]
df["de_bin"] = pd.cut(df["Debt_Eq_P0"], bins=bins, labels=labels)
print(f"{'Bin':<14}{'N':>6}{'Median':>10}{'Mean':>10}{'WR':>8}")
for lab in labels:
    g = df[df["de_bin"]==lab].dropna(subset=["profit_3M"])
    if len(g)==0: continue
    med = g["profit_3M"].median(); mean = g["profit_3M"].mean(); wr = (g["profit_3M"]>0).mean()*100
    print(f"{lab:<14}{len(g):>6}{med:>+9.2f}%{mean:>+9.2f}%{wr:>7.1f}%")

print(f"\nForward return by IntCov bin (absolute thresholds, log-scaled):")
bins = [-100, 0, 2, 5, 10, 50, 1000]
labels = ["IC<0","IC 0-2","IC 2-5","IC 5-10","IC 10-50","IC>50"]
df["ic_bin"] = pd.cut(df["IntCov_P0"], bins=bins, labels=labels)
print(f"{'Bin':<14}{'N':>6}{'Median':>10}{'Mean':>10}{'WR':>8}")
for lab in labels:
    g = df[df["ic_bin"]==lab].dropna(subset=["profit_3M"])
    if len(g)==0: continue
    med = g["profit_3M"].median(); mean = g["profit_3M"].mean(); wr = (g["profit_3M"]>0).mean()*100
    print(f"{lab:<14}{len(g):>6}{med:>+9.2f}%{mean:>+9.2f}%{wr:>7.1f}%")

print(f"\nForward return by NetDebt/EBITDA bin:")
bins = [-30, -2, 0, 2, 4, 8, 100]
labels = ["NetCash>2","Cash mod","ND/E 0-2","ND/E 2-4","ND/E 4-8","ND/E >8"]
df["nd_bin"] = pd.cut(df["NetDebt_EBITDA"], bins=bins, labels=labels)
print(f"{'Bin':<14}{'N':>6}{'Median':>10}{'Mean':>10}{'WR':>8}")
for lab in labels:
    g = df[df["nd_bin"]==lab].dropna(subset=["profit_3M"])
    if len(g)==0: continue
    med = g["profit_3M"].median(); mean = g["profit_3M"].mean(); wr = (g["profit_3M"]>0).mean()*100
    print(f"{lab:<14}{len(g):>6}{med:>+9.2f}%{mean:>+9.2f}%{wr:>7.1f}%")

print(f"\nForward return by Debt change (Δ D/E YoY) bin:")
bins = [-10, -0.2, -0.05, 0.05, 0.2, 10]
labels = ["Big↓debt","Sm↓debt","Stable","Sm↑debt","Big↑debt"]
df["dedelta_bin"] = pd.cut(df["DEbt_delta"], bins=bins, labels=labels)
print(f"{'Bin':<14}{'N':>6}{'Median':>10}{'Mean':>10}{'WR':>8}")
for lab in labels:
    g = df[df["dedelta_bin"]==lab].dropna(subset=["profit_3M"])
    if len(g)==0: continue
    med = g["profit_3M"].median(); mean = g["profit_3M"].mean(); wr = (g["profit_3M"]>0).mean()*100
    print(f"{lab:<14}{len(g):>6}{med:>+9.2f}%{mean:>+9.2f}%{wr:>7.1f}%")

# U-shape detection? Maybe extreme values both hurt
print(f"\nU-shape check on Debt_Eq (decile):")
df["de_decile"] = pd.qcut(df["Debt_Eq_P0"].rank(pct=True), 10, labels=False, duplicates="drop")
print(f"{'Decile':<8}{'N':>6}{'Median':>10}{'Mean':>10}{'WR':>8}")
for d in range(10):
    g = df[df["de_decile"]==d].dropna(subset=["profit_3M"])
    if len(g)==0: continue
    med = g["profit_3M"].median(); mean = g["profit_3M"].mean(); wr = (g["profit_3M"]>0).mean()*100
    extra = " (lowest debt)" if d==0 else " (highest debt)" if d==9 else ""
    print(f"D{d}{extra:<8}{len(g):>6}{med:>+9.2f}%{mean:>+9.2f}%{wr:>7.1f}%")

# Quality-conditional health
print(f"\nHealth IC within quality tile (does H1 IntCov work for any subgroup?):")
print(f"{'Indicator':<22}{'Q4 low':>10}{'Q3':>10}{'Q2':>10}{'Q1 high':>10}")
for ind, col in [("Debt_Eq_P0","r_Debt_Eq_P0"), ("IntCov_P0","r_IntCov_P0"),
                 ("NetDebt/EBITDA","r_NetDebt_EBITDA"), ("Cash/MktCap","r_Cash_MktCap"),
                 ("ΔD/E YoY","r_DEbt_delta")]:
    row = f"{ind:<22}"
    for tl in [0,1,2,3]:
        sub = df[df["quality_tile"]==tl]
        rho, _ = spearman_ic(sub[col], sub["profit_3M"])
        row += f"{rho:>+10.4f}"
    print(row)

print("\n" + "="*80); print("DONE"); print("="*80)
