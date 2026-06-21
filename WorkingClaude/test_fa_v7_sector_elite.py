#!/usr/bin/env python3
"""
test_fa_v7_sector_elite.py
==========================
v7 takeaway: weight tuning per sector FAILS. v6b uniform stays best.

But sector-IC differences are REAL. Approach: post-process A tier with
sector-specific elite filters (like MEGA-A but per-sector).

Logic from sector-IC findings:
  Banks (8):    A + ROE_Min5Y top half (skip high-growth banks via NP_TTM filter)
  Tech (9):     A + FCF_yield top half
  Cyclical (0): A + NP_peak_ratio top half (catch peak earnings)
  Materials(1): A + ROIC5Y top half (value zero, ROIC matters)
  Industri (2): A + smoothed_EY top half (value strong)
  ConsServ (5): A + (smoothed_EY top half OR NP_TTM top half)
  ConsGoods(3): A + standard (no extra filter, v4-like)
  Utility (7):  A + ROIC5Y top half (FCF doesn't matter)

Per-sector ELITE = A AND sector_specific_condition
Overall ELITE = union of all sector-elite picks

Compare ELITE_SECTOR vs A-tier-baseline on profit_3M / O6M / O1Y / O2Y.
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
W_V6B = {"quality":0.18,"stability":0.18,"cash":0.18,"shareholder":0.15,
         "growth":0.13,"health":0.08,"valuation":0.10}

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

SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y,
    SAFE_DIVIDE(f.CF_OA_5Y + f.CF_Invest_5Y, ABS(f.CF_OA_5Y)) AS FCF_OA_ratio,
    f.IntCov_P0,
    f.PE, f.PB, f.PCF, f.OShares,
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
df["sector_top"] = (df["ICB_Code"] / 1000).astype(int)

# Build v6b indicators (truncated, same as v7 test)
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"]*_mult; df["DY_sust"] = _mult
np_arr = df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
rev_arr = df[[f"Revenue_P{i}" for i in range(8)]].values.astype(float)
np_n = np.sum(~np.isnan(np_arr),axis=1); rev_n = np.sum(~np.isnan(rev_arr),axis=1)
with np.errstate(divide="ignore", invalid="ignore"):
    np_m=np.nanmean(np_arr,axis=1); np_s=np.nanstd(np_arr,axis=1,ddof=1)
    rev_m=np.nanmean(rev_arr,axis=1); rev_s=np.nanstd(rev_arr,axis=1,ddof=1)
    df["NP_CV_raw"]=np.where(np_n>=6, np_s/np.maximum(np.abs(np_m),1e6), np.nan).clip(max=10)
    df["Rev_CV_raw"]=np.where(rev_n>=6, rev_s/np.maximum(np.abs(rev_m),1e6),np.nan).clip(max=10)
df["NP_CV"]  = -df["NP_CV_raw"]
df["Rev_CV"] = -df["Rev_CV_raw"]
rev_p0=df["Revenue_P0"].values; rev_p7=df["Revenue_P7"].values
df["LT_CAGR"]=np.where((rev_p0>0)&(rev_p7>0),(rev_p0/rev_p7)**(4/7)-1,np.nan).clip(-0.95,5.0)
df["NP_4Q_mean"]=df[[f"NP_P{i}" for i in range(4)]].mean(axis=1,skipna=True)
df["MktCap"]=df["Close"]*df["OShares"]
df["smoothed_EY"]=(df["NP_4Q_mean"]/df["OShares"].replace(0,np.nan)/df["Close"].replace(0,np.nan)).clip(-1,1)
df["EY"]=np.where(df["PE"]>0,1.0/df["PE"],np.nan)
df["FCF_4Q"]=(df["CF_OA_P0"]+df["CF_OA_P1"]+df["CF_OA_P2"]+df["CF_OA_P3"]
            +df["CF_Invest_P0"]+df["CF_Invest_P1"]+df["CF_Invest_P2"]+df["CF_Invest_P3"])
df["FCF_yield"]=(df["FCF_4Q"]/df["MktCap"]).clip(-1,1)
df["r_ROIC5Y_pre"]=df.groupby("quarter")["ROIC5Y"].rank(pct=True,na_option="keep")
df["r_EY_pre"]=df.groupby("quarter")["EY"].rank(pct=True,na_option="keep")
df["magic_formula"]=(df["r_ROIC5Y_pre"]+df["r_EY_pre"])/2.0
df["TotalDebt"]=df["StDebt_P0"].fillna(0)+df["LtDebt_P0"].fillna(0)
df["NetDebt"]=df["TotalDebt"]-df["Cash_P0"].fillna(0)
df["NetDebt_EBITDA_inv"]=-np.where(df["EBITDA_P0"]>0,df["NetDebt"]/df["EBITDA_P0"],np.nan).clip(-20,50)
df["Cash_MktCap"]=np.where(df["MktCap"]>0,df["Cash_P0"]/df["MktCap"],np.nan).clip(-1,5)
df["IntCov_inv"]=-df["IntCov_P0"]

# NP TTM growth (helper for filtering)
ttm_now = df[[f"NP_P{i}" for i in range(4)]].sum(axis=1, skipna=False)
ttm_prv = df[[f"NP_P{i}" for i in range(4,8)]].sum(axis=1, skipna=False)
df["NP_TTM_growth"] = np.where(ttm_prv.abs()>0,(ttm_now-ttm_prv)/ttm_prv.abs(),np.nan).clip(-5,5)

AXIS = {
    "quality":["ROIC5Y","ROE_Min5Y"], "stability":["NP_CV","Rev_CV","LT_CAGR"],
    "cash":["CF_OA_5Y","CFOA_NP"], "shareholder":["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
    "growth":["GPM_change","NP_peak_ratio","Rev_peak_ratio"],
    "health":["Cash_MktCap","NetDebt_EBITDA_inv","IntCov_inv"],
    "valuation":["smoothed_EY","FCF_yield","magic_formula"],
}
ALL_INDS=set()
for cs in AXIS.values(): ALL_INDS.update(cs)
for c in ALL_INDS:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
for axis,cs in AXIS.items():
    df[f"_score_{axis}"] = df[[f"r_{c}" for c in cs]].mean(axis=1, skipna=True)

# v6b total score + tier
score_cols=[f"_score_{a}" for a in W_V6B]
w_arr = np.array([W_V6B[a] for a in W_V6B])
total = (df[score_cols].values * w_arr).sum(axis=1)
nan_any = df[score_cols].isna().any(axis=1)
df["total_score"] = np.where(nan_any, np.nan, total)
df_clean = df.dropna(subset=["total_score"]).copy()
df_clean["score_pct"] = df_clean.groupby("quarter")["total_score"].rank(pct=True)
def tier_of(p):
    for n,lo,hi in TIERS:
        if lo<=p<=hi: return n
    return "E"
df_clean["tier"] = df_clean["score_pct"].apply(tier_of)

# Rank smoothed_EY/FCF_yield within sector for filter conditions
for c in ["smoothed_EY","FCF_yield","ROE_Min5Y","ROIC5Y","NP_peak_ratio","NP_TTM_growth"]:
    df_clean[f"rsec_{c}"] = df_clean.groupby(["quarter","sector_top"])[c].rank(pct=True, na_option="keep")

A = df_clean[df_clean["tier"]=="A"].copy()
A_v = A.dropna(subset=["profit_3M"])
n_A = len(A_v); med_A = A_v["profit_3M"].median(); wr_A = (A_v["profit_3M"]>0).mean()*100
print(f"\nA tier baseline (v6b): N={n_A}  median={med_A:.2f}%  WR={wr_A:.1f}%")

# ─── Define sector-specific ELITE conditions (within A tier) ──────────────
# Sector elite = within-sector rank of key indicator >= some threshold
def sector_elite_v1(row):
    s = row["sector_top"]
    if s == 8:   return row["rsec_ROE_Min5Y"] >= 0.5     # Banks: top half ROE
    if s == 9:   return row["rsec_FCF_yield"] >= 0.5     # Tech: top half FCF
    if s == 0:   return row["rsec_NP_peak_ratio"] >= 0.5 # Cyclical: peak detect
    if s == 1:   return row["rsec_ROIC5Y"] >= 0.5        # Materials: ROIC
    if s == 2:   return row["rsec_smoothed_EY"] >= 0.5   # Industrials: value
    if s == 5:   return (row["rsec_smoothed_EY"] >= 0.5) | (row["rsec_NP_TTM_growth"] >= 0.5)  # ConsServ
    if s == 7:   return row["rsec_ROIC5Y"] >= 0.5        # Utility: ROIC
    return True  # Default: all pass (sectors 3,4,6)

# Apply elite filter
A_v["sector_elite_v1"] = A_v.apply(sector_elite_v1, axis=1)
elite = A_v[A_v["sector_elite_v1"]]
print(f"\n  SECTOR-ELITE v1 (within-sector rank >=50% on key indicator):")
print(f"    N={len(elite)}  median={elite['profit_3M'].median():+.2f}%  mean={elite['profit_3M'].mean():+.2f}%  WR={(elite['profit_3M']>0).mean()*100:.1f}%")

# Stricter: top 25% within sector
def sector_elite_v2(row):
    s = row["sector_top"]
    if s == 8:   return row["rsec_ROE_Min5Y"] >= 0.75
    if s == 9:   return row["rsec_FCF_yield"] >= 0.75
    if s == 0:   return row["rsec_NP_peak_ratio"] >= 0.75
    if s == 1:   return row["rsec_ROIC5Y"] >= 0.75
    if s == 2:   return row["rsec_smoothed_EY"] >= 0.75
    if s == 5:   return (row["rsec_smoothed_EY"] >= 0.75) | (row["rsec_NP_TTM_growth"] >= 0.75)
    if s == 7:   return row["rsec_ROIC5Y"] >= 0.75
    return True
A_v["sector_elite_v2"] = A_v.apply(sector_elite_v2, axis=1)
elite2 = A_v[A_v["sector_elite_v2"]]
print(f"\n  SECTOR-ELITE v2 (within-sector rank >=75% on key indicator):")
print(f"    N={len(elite2)}  median={elite2['profit_3M'].median():+.2f}%  mean={elite2['profit_3M'].mean():+.2f}%  WR={(elite2['profit_3M']>0).mean()*100:.1f}%")

# Even stricter: top 25% on key indicator AND another check
# For Banks: also require NP_TTM_growth < median (avoid hot growth banks)
def sector_elite_v3(row):
    s = row["sector_top"]
    if s == 8:   return (row["rsec_ROE_Min5Y"] >= 0.75) & (row["rsec_NP_TTM_growth"] <= 0.75)
    if s == 9:   return (row["rsec_FCF_yield"] >= 0.75)
    if s == 0:   return (row["rsec_NP_peak_ratio"] >= 0.75)
    if s == 1:   return (row["rsec_ROIC5Y"] >= 0.75)
    if s == 2:   return (row["rsec_smoothed_EY"] >= 0.75)
    if s == 5:   return (row["rsec_smoothed_EY"] >= 0.75) | (row["rsec_NP_TTM_growth"] >= 0.75)
    if s == 7:   return (row["rsec_ROIC5Y"] >= 0.75)
    return True
A_v["sector_elite_v3"] = A_v.apply(sector_elite_v3, axis=1)
elite3 = A_v[A_v["sector_elite_v3"]]
print(f"\n  SECTOR-ELITE v3 (v2 + Banks avoid high NP_TTM):")
print(f"    N={len(elite3)}  median={elite3['profit_3M'].median():+.2f}%  mean={elite3['profit_3M'].mean():+.2f}%  WR={(elite3['profit_3M']>0).mean()*100:.1f}%")

# Per-sector elite breakdown for v2
print(f"\n  v2 ELITE breakdown by sector:")
print(f"  {'Sec':<6}{'A_n':>5}{'Elite_n':>9}{'A_med':>10}{'Elite_med':>12}{'A_WR':>8}{'Elite_WR':>10}")
print("  " + "-"*65)
for s in sorted(A_v["sector_top"].unique()):
    sub = A_v[A_v["sector_top"]==s]
    el = sub[sub["sector_elite_v2"]]
    if len(sub) < 5: continue
    print(f"  {s:<6}{len(sub):>5}{len(el):>9}{sub['profit_3M'].median():>+8.2f}% "
          f"{el['profit_3M'].median():>+9.2f}% {(sub['profit_3M']>0).mean()*100:>6.1f}%"
          f" {(el['profit_3M']>0).mean()*100:>8.1f}%")

print("\n" + "="*80); print("DONE"); print("="*80)
