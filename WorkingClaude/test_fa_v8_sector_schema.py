#!/usr/bin/env python3
"""
test_fa_v8_sector_schema.py
===========================
v8 = sector-specific INDICATOR schemas (different axes/indicators per sector)
     NOT just different weights.

Design rationale per sector:
  BANK (8355):
    - Drop CF_OA, Debt_Eq, IntCov, CashR (irrelevant — banks structurally leveraged)
    - ROE focus (not ROIC — banks have weird ROIC due to leverage)
    - PB-based valuation (PE less meaningful for banks)
    - Avoid NP_R as growth (IC -0.125 anti-signal for banks)

  SECURITIES (8775, 8777):
    - Similar to banks: drop CF/Debt indicators
    - More BV-driven; volatility matters less
    - FCF_yield surprisingly matters (+0.280 IC, our discovery)

  INSURANCE (8536):
    - Drop CF/Debt
    - Dividend critical (insurance heavy payers)
    - Smoothed earnings (cycle-aware)

  REIT (8633, 8637):
    - High debt is NORMAL (don't penalize)
    - Lumpy earnings → use LT_CAGR over CV
    - Cash flow matters (rental income)
    - PB-based valuation

  DEFAULT (everything else):
    - Use v6b full schema

Aggregation: rank within sector → tier within sector (top 10% per sector group).
This avoids cross-sector score-comparability issues.
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"
TIERS = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]

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

SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE5Y, f.ROE_Trailing,
    f.FSCORE, f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y, f.Dividend_1Y, f.Dividend_3Y,
    SAFE_DIVIDE(f.CF_OA_5Y + f.CF_Invest_5Y, ABS(f.CF_OA_5Y)) AS FCF_OA_ratio,
    f.Debt_Eq_P0, f.IntCov_P0, f.CashR_P0,
    f.PE, f.PB, f.PCF, f.EVEB, f.OShares,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
    f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3,
    f.StDebt_P0, f.LtDebt_P0, f.Cash_P0, f.EBITDA_P0,
    CASE WHEN GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0, GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    CASE WHEN GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                       f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7) > 0
         THEN SAFE_DIVIDE(f.Revenue_P0, GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                                                  f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7))
         ELSE NULL END AS Rev_peak_ratio,
    t.Close, t.ICB_Code, t.profit_3M,
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
df["ICB_Code"] = df["ICB_Code"].fillna(0)

# ─── Build all indicators ──────────────────────────────────────────────────
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"]*_mult; df["DY_sust"] = _mult

np_arr=df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
rev_arr=df[[f"Revenue_P{i}" for i in range(8)]].values.astype(float)
np_n=np.sum(~np.isnan(np_arr),axis=1); rev_n=np.sum(~np.isnan(rev_arr),axis=1)
with np.errstate(divide="ignore",invalid="ignore"):
    np_m=np.nanmean(np_arr,axis=1); np_s=np.nanstd(np_arr,axis=1,ddof=1)
    rev_m=np.nanmean(rev_arr,axis=1); rev_s=np.nanstd(rev_arr,axis=1,ddof=1)
    df["NP_CV"]=-np.where(np_n>=6,np_s/np.maximum(np.abs(np_m),1e6),np.nan).clip(max=10)
    df["Rev_CV"]=-np.where(rev_n>=6,rev_s/np.maximum(np.abs(rev_m),1e6),np.nan).clip(max=10)
rev_p0=df["Revenue_P0"].values; rev_p7=df["Revenue_P7"].values
df["LT_CAGR"]=np.where((rev_p0>0)&(rev_p7>0),(rev_p0/rev_p7)**(4/7)-1,np.nan).clip(-0.95,5.0)

# v6b indicators
df["NP_4Q_mean"]=df[[f"NP_P{i}" for i in range(4)]].mean(axis=1,skipna=True)
df["MktCap"]=df["Close"]*df["OShares"]
df["smoothed_EY"]=(df["NP_4Q_mean"]/df["OShares"].replace(0,np.nan)/df["Close"].replace(0,np.nan)).clip(-1,1)
df["EY"]=np.where(df["PE"]>0,1.0/df["PE"],np.nan)
df["BY"]=np.where(df["PB"]>0,1.0/df["PB"],np.nan)
df["FCF_4Q"]=(df["CF_OA_P0"]+df["CF_OA_P1"]+df["CF_OA_P2"]+df["CF_OA_P3"]
            +df["CF_Invest_P0"]+df["CF_Invest_P1"]+df["CF_Invest_P2"]+df["CF_Invest_P3"])
df["FCF_yield"]=(df["FCF_4Q"]/df["MktCap"]).clip(-1,1)
df["r_ROIC5Y_pre"]=df.groupby("quarter")["ROIC5Y"].rank(pct=True,na_option="keep")
df["r_ROE_Min5Y_pre"]=df.groupby("quarter")["ROE_Min5Y"].rank(pct=True,na_option="keep")
df["r_EY_pre"]=df.groupby("quarter")["EY"].rank(pct=True,na_option="keep")
df["r_BY_pre"]=df.groupby("quarter")["BY"].rank(pct=True,na_option="keep")
df["magic_formula_pe"]=(df["r_ROIC5Y_pre"]+df["r_EY_pre"])/2.0
df["magic_formula_roe"]=(df["r_ROE_Min5Y_pre"]+df["r_EY_pre"])/2.0  # Bank version: ROE+EY
df["magic_formula_pb"]=(df["r_ROE_Min5Y_pre"]+df["r_BY_pre"])/2.0   # Bank/REIT: ROE+1/PB
df["TotalDebt"]=df["StDebt_P0"].fillna(0)+df["LtDebt_P0"].fillna(0)
df["NetDebt"]=df["TotalDebt"]-df["Cash_P0"].fillna(0)
df["NetDebt_EBITDA_inv"]=-np.where(df["EBITDA_P0"]>0,df["NetDebt"]/df["EBITDA_P0"],np.nan).clip(-20,50)
df["Cash_MktCap"]=np.where(df["MktCap"]>0,df["Cash_P0"]/df["MktCap"],np.nan).clip(-1,5)
df["IntCov_inv"]=-df["IntCov_P0"]

# Bank-specific: invert NP_R (high growth banks underperform — IC -0.125)
df["NP_R_inv_bank"] = -df["NP_R"]

# ─── Sector bucket ─────────────────────────────────────────────────────────
def sector_bucket(icb):
    if pd.isna(icb): return "DEFAULT"
    try: code = int(float(icb))
    except: return "DEFAULT"
    if code == 8355:           return "BANK"
    if code in (8633, 8637):   return "REIT"
    if code == 8536:           return "INSURANCE"
    if code in (8775, 8777):   return "SECURITIES"
    return "DEFAULT"
df["sector"] = df["ICB_Code"].apply(sector_bucket)
print("\nSector distribution:")
print(df["sector"].value_counts().to_string())

# ─── Sector-specific axis schemas (DIFFERENT indicators) ───────────────────
# Each axis = list of indicators. Sum of axis weights = 1.0 per schema.
SCHEMA_DEFAULT = {
    "axes": {
        "quality":     ["ROIC5Y","ROE_Min5Y"],
        "stability":   ["NP_CV","Rev_CV","LT_CAGR"],
        "cash":        ["CF_OA_5Y","CFOA_NP"],
        "shareholder": ["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
        "growth":      ["GPM_change","NP_peak_ratio","Rev_peak_ratio"],
        "health":      ["Cash_MktCap","NetDebt_EBITDA_inv","IntCov_inv"],
        "valuation":   ["smoothed_EY","FCF_yield","magic_formula_pe"],
    },
    "weights": {"quality":0.18,"stability":0.18,"cash":0.18,"shareholder":0.15,
                "growth":0.13,"health":0.08,"valuation":0.10},
}
SCHEMA_BANK = {
    "axes": {
        # No cash, no health (irrelevant for banks structurally)
        "quality":     ["ROE_Min5Y","ROE5Y","ROE_Trailing"],
        "stability":   ["NP_CV","Rev_CV"],
        "shareholder": ["DY_adj","Dividend_Min3Y","DY_sust","Dividend_3Y"],
        "growth":      ["NP_R_inv_bank","GPM_change","NP_peak_ratio"],  # invert NP_R for banks
        "valuation":   ["smoothed_EY","magic_formula_pb"],  # PB-based for banks
    },
    "weights": {"quality":0.30,"stability":0.20,"shareholder":0.18,
                "growth":0.07,"valuation":0.25},  # ROE+valuation heavy
}
SCHEMA_SECURITIES = {
    "axes": {
        # Securities are leveraged, BV-driven; FCF surprisingly works (+0.280)
        "quality":     ["ROE_Min5Y","ROIC5Y"],
        "stability":   ["NP_CV"],  # only NP_CV (Rev_CV less stable)
        "shareholder": ["DY_adj","Dividend_Min3Y"],
        "growth":      ["NP_peak_ratio","GPM_change"],
        "valuation":   ["smoothed_EY","FCF_yield","magic_formula_pb"],
    },
    "weights": {"quality":0.22,"stability":0.20,"shareholder":0.15,
                "growth":0.10,"valuation":0.33},  # FCF + valuation heavy for SEC
}
SCHEMA_INSURANCE = {
    "axes": {
        "quality":     ["ROE_Min5Y","ROIC5Y","ROE_Trailing"],
        "stability":   ["NP_CV","Rev_CV"],
        "shareholder": ["DY_adj","Dividend_Min3Y","DY_sust","Dividend_3Y"],
        "growth":      ["NP_peak_ratio","Rev_peak_ratio"],
        "valuation":   ["smoothed_EY"],
    },
    "weights": {"quality":0.25,"stability":0.20,"shareholder":0.25,
                "growth":0.15,"valuation":0.15},
}
SCHEMA_REIT = {
    "axes": {
        # REIT: lumpy earnings — use LT_CAGR over CV; cash flow matters (rental)
        "quality":     ["ROE_Min5Y","ROIC5Y"],
        "stability":   ["LT_CAGR"],  # only long-term CAGR (8Q CV too volatile for REIT)
        "cash":        ["CF_OA_5Y"],
        "shareholder": ["DY_adj","Dividend_Min3Y","DY_sust"],
        "growth":      ["NP_peak_ratio"],
        "valuation":   ["smoothed_EY","magic_formula_pb"],  # PB-based for REIT
    },
    "weights": {"quality":0.18,"stability":0.10,"cash":0.12,"shareholder":0.20,
                "growth":0.10,"valuation":0.30},
}

SCHEMAS = {"DEFAULT":SCHEMA_DEFAULT, "BANK":SCHEMA_BANK, "SECURITIES":SCHEMA_SECURITIES,
           "INSURANCE":SCHEMA_INSURANCE, "REIT":SCHEMA_REIT}

# Sanity check weight sums
for name, s in SCHEMAS.items():
    total = sum(s["weights"].values())
    assert abs(total - 1.0) < 1e-9, f"{name} weights sum {total}"
    assert set(s["weights"].keys()) == set(s["axes"].keys()), f"{name} axis mismatch"

# Pre-rank all needed indicators
ALL_INDS = set()
for s in SCHEMAS.values():
    for cs in s["axes"].values(): ALL_INDS.update(cs)
print("\nComputing ranks ...")
for c in ALL_INDS:
    if c.startswith("magic_formula"): continue  # already pre-computed
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
# magic_formula_pb already computed above
for mf in ["magic_formula_pe","magic_formula_pb","magic_formula_roe"]:
    df[f"r_{mf}"] = df.groupby("quarter")[mf].rank(pct=True, na_option="keep")

# Score per row using its sector's schema
def score_row(row):
    schema = SCHEMAS[row["sector"]]
    total = 0.0
    valid = 0
    for axis, cs in schema["axes"].items():
        rcols = [f"r_{c}" for c in cs]
        vals = [row[rc] for rc in rcols if not pd.isna(row[rc])]
        if vals:
            axis_score = np.mean(vals)
            total += axis_score * schema["weights"][axis]
            valid += schema["weights"][axis]
    if valid < 0.5: return np.nan
    return total / valid   # normalize for missing axes

print("Computing v8 sector-specific scores ...")
df["v8_score"] = df.apply(score_row, axis=1)

# v6b global score (for comparison)
v6b_axes = SCHEMA_DEFAULT["axes"]; v6b_weights = SCHEMA_DEFAULT["weights"]
v6b_total = np.zeros(len(df))
v6b_nan = np.zeros(len(df), dtype=bool)
for axis, cs in v6b_axes.items():
    rcols = [f"r_{c}" for c in cs]
    axis_score = df[rcols].mean(axis=1, skipna=True)
    v6b_nan |= axis_score.isna()
    v6b_total += np.nan_to_num(axis_score.values, nan=0.0) * v6b_weights[axis]
df["v6b_score"] = np.where(v6b_nan, np.nan, v6b_total)

# Tier assignment:
# v6b: rank globally (universe-wide per quarter)
# v8: rank within sector (per quarter × sector)
def tier_of(p):
    for n,lo,hi in TIERS:
        if lo<=p<=hi: return n
    return "E"

df_v6b = df.dropna(subset=["v6b_score"]).copy()
df_v6b["v6b_pct"] = df_v6b.groupby("quarter")["v6b_score"].rank(pct=True)
df_v6b["v6b_tier"] = df_v6b["v6b_pct"].apply(tier_of)

df_v8 = df.dropna(subset=["v8_score"]).copy()
df_v8["v8_pct"] = df_v8.groupby(["quarter","sector"])["v8_score"].rank(pct=True)
df_v8["v8_tier"] = df_v8["v8_pct"].apply(tier_of)

# ═══════════════════════════════════════════════════════════════════════════
# Report
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("OVERALL TIER ORDERING (profit_3M)"); print("="*80)
print(f"\nv6b (universal scoring, global rank):")
for tier in ["A","B","C","D","E"]:
    g = df_v6b[df_v6b["v6b_tier"]==tier].dropna(subset=["profit_3M"])["profit_3M"]
    if len(g):
        print(f"  {tier}  N={len(g):4d}  median={g.median():+6.2f}%  mean={g.mean():+6.2f}%  WR={(g>0).mean()*100:.1f}%")

print(f"\nv8 (sector-specific schemas, within-sector rank):")
for tier in ["A","B","C","D","E"]:
    g = df_v8[df_v8["v8_tier"]==tier].dropna(subset=["profit_3M"])["profit_3M"]
    if len(g):
        print(f"  {tier}  N={len(g):4d}  median={g.median():+6.2f}%  mean={g.mean():+6.2f}%  WR={(g>0).mean()*100:.1f}%")

# Per-sector A tier comparison
print("\n" + "="*80); print("A-TIER PER SECTOR — v6b vs v8"); print("="*80)
print(f"\n{'Sector':<14}{'v6b A':>22}{'v8 A':>22}{'Δmed':>9}{'ΔWR':>8}")
print("-"*80)
for sec in ["BANK","SECURITIES","INSURANCE","REIT","DEFAULT"]:
    sub6 = df_v6b[(df_v6b["sector"]==sec) & (df_v6b["v6b_tier"]=="A")].dropna(subset=["profit_3M"])
    sub8 = df_v8[(df_v8["sector"]==sec) & (df_v8["v8_tier"]=="A")].dropna(subset=["profit_3M"])
    if len(sub6) < 3 or len(sub8) < 3:
        print(f"  {sec:<12}  insufficient")
        continue
    m6 = sub6["profit_3M"].median(); w6 = (sub6["profit_3M"]>0).mean()*100
    m8 = sub8["profit_3M"].median(); w8 = (sub8["profit_3M"]>0).mean()*100
    print(f"  {sec:<12}  N={len(sub6):3d} med={m6:+5.2f}% WR={w6:5.1f}%  N={len(sub8):3d} med={m8:+5.2f}% WR={w8:5.1f}%"
          f"  {m8-m6:>+6.2f} {w8-w6:>+6.1f}")

# Tier ordering by sector for v8
print("\n" + "="*80); print("v8 WITHIN-SECTOR tier ordering (profit_3M)"); print("="*80)
for sec in ["BANK","SECURITIES","INSURANCE","REIT","DEFAULT"]:
    sub = df_v8[df_v8["sector"]==sec]
    if len(sub) < 100: continue
    print(f"\n  --- {sec} (N={len(sub)}) ---")
    for tier in ["A","B","C","D","E"]:
        g = sub[sub["v8_tier"]==tier].dropna(subset=["profit_3M"])["profit_3M"]
        if len(g):
            print(f"  {tier}  N={len(g):4d}  median={g.median():+6.2f}%  mean={g.mean():+6.2f}%  WR={(g>0).mean()*100:.1f}%")

# Composite IC
print("\n" + "="*80); print("COMPOSITE IC vs profit_3M"); print("="*80)
ic6, n6 = spearman_ic(df_v6b["v6b_score"], df_v6b["profit_3M"])
print(f"  v6b global score:    IC={ic6:+.4f}  N={n6}")
ic8, n8 = spearman_ic(df_v8["v8_score"], df_v8["profit_3M"])
print(f"  v8 sector-specific:  IC={ic8:+.4f}  N={n8}")
print(f"  Δ = {ic8-ic6:+.4f}")

# Within-sector IC for v8
print(f"\n  v8 IC per sector:")
for sec in ["BANK","SECURITIES","INSURANCE","REIT","DEFAULT"]:
    sub = df_v8[df_v8["sector"]==sec]
    if len(sub) < 100: continue
    ic, n = spearman_ic(sub["v8_score"], sub["profit_3M"])
    ic_v6b_sec, _ = spearman_ic(df_v6b[df_v6b["sector"]==sec]["v6b_score"],
                                  df_v6b[df_v6b["sector"]==sec]["profit_3M"])
    print(f"    {sec:<12}  v8 IC={ic:+.4f}  v6b IC={ic_v6b_sec:+.4f}  Δ={ic-ic_v6b_sec:+.4f}  N={n}")

print("\n" + "="*80); print("DONE"); print("="*80)
