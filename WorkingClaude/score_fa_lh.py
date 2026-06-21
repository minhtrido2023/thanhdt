#!/usr/bin/env python3
"""
score_fa_lh.py
==============
FA scoring for LONG-HOLD portfolio. Extends v8c_final:
  - ALL quarters since 2014 (not just Q4)
  - Adds pre-sales (AdvCust + UnearnRev) to REIT_RES and REIT schemas
  - Per-quarter, per-sub-sector ranking
  - Output: fa_ratings_lh.csv with (ticker, quarter, time, Release_Date, sub, score, tier, ICB_Code, MktCap)
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"
OUT_CSV = "data/fa_ratings_lh.csv"
TIERS = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]

RESIDENTIAL_TICKERS = {"VHM","NVL","DXG","KDH","NLG","AGG","KHG","HDG","CRE","FLC","IJC","HDC",
                       "TIG","QCG","DIG","DXS","HQC","API","AAV","BII","C21","ITC","SCR","VPI",
                       "CEO","TCH","NTL"}

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(f"{r.stdout[:500]}|{r.stderr[:500]}")
    return pd.read_csv(StringIO(r.stdout.strip()))

# Pull all quarters; one row per (ticker, quarter) at the nearest trading day on/before f.time
SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time, f.Release_Date,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE_Trailing,
    f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y,
    SAFE_DIVIDE(f.CF_OA_5Y + f.CF_Invest_5Y, ABS(f.CF_OA_5Y)) AS FCF_OA_ratio,
    f.IntCov_P0, f.PE, f.PB, f.PCF, f.OShares,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
    f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3,
    f.StDebt_P0, f.LtDebt_P0, f.Cash_P0, f.EBITDA_P0,
    f.AdvCust_P0, f.UnearnRev_P0,
    CASE WHEN GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0, GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    CASE WHEN GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                       f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7) > 0
         THEN SAFE_DIVIDE(f.Revenue_P0, GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                                                  f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7))
         ELSE NULL END AS Rev_peak_ratio,
    t.Close, t.ICB_Code, t.Volume_3M_P50,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2014-01-01"
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching all-quarter universe ..."); df = bq_query(SQL); print(f"  {len(df):,} rows, {df['ticker'].nunique()} tickers, {df['quarter'].nunique()} quarters")
df["ICB_Code"] = df["ICB_Code"].fillna(0).astype(int)

# Indicator construction (same as v8c_final + pre-sales yields)
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"]*_mult; df["DY_sust"] = _mult

np_arr = df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
rev_arr = df[[f"Revenue_P{i}" for i in range(8)]].values.astype(float)
np_n = np.sum(~np.isnan(np_arr),axis=1); rev_n = np.sum(~np.isnan(rev_arr),axis=1)
with np.errstate(divide="ignore",invalid="ignore"):
    np_m=np.nanmean(np_arr,axis=1); np_s=np.nanstd(np_arr,axis=1,ddof=1)
    rev_m=np.nanmean(rev_arr,axis=1); rev_s=np.nanstd(rev_arr,axis=1,ddof=1)
    df["NP_CV"]=-np.where(np_n>=6,np_s/np.maximum(np.abs(np_m),1e6),np.nan).clip(max=10)
    df["Rev_CV"]=-np.where(rev_n>=6,rev_s/np.maximum(np.abs(rev_m),1e6),np.nan).clip(max=10)

rev_p0=df["Revenue_P0"].values; rev_p7=df["Revenue_P7"].values
df["LT_CAGR"]=np.where((rev_p0>0)&(rev_p7>0),(rev_p0/rev_p7)**(4/7)-1,np.nan).clip(-0.95,5.0)
df["NP_4Q_mean"]=df[[f"NP_P{i}" for i in range(4)]].mean(axis=1,skipna=True)
df["MktCap"]=df["Close"]*df["OShares"]
df["smoothed_EY"]=(df["NP_4Q_mean"]/df["OShares"].replace(0,np.nan)/df["Close"].replace(0,np.nan)).clip(-1,1)
df["EY"]=np.where(df["PE"]>0,1.0/df["PE"],np.nan)
df["BY"]=np.where(df["PB"]>0,1.0/df["PB"],np.nan)
df["CFY"]=np.where(df["PCF"]>0,1.0/df["PCF"],np.nan)
df["FCF_4Q"]=(df["CF_OA_P0"]+df["CF_OA_P1"]+df["CF_OA_P2"]+df["CF_OA_P3"]
            +df["CF_Invest_P0"]+df["CF_Invest_P1"]+df["CF_Invest_P2"]+df["CF_Invest_P3"])
df["FCF_yield"]=(df["FCF_4Q"]/df["MktCap"]).clip(-1,1)
df["Cash_MktCap"] = np.where(df["MktCap"]>0, df["Cash_P0"]/df["MktCap"], np.nan).clip(-1, 5)
ttm_now = df[[f"NP_P{i}" for i in range(4)]].sum(axis=1, skipna=False)
ttm_prv = df[[f"NP_P{i}" for i in range(4,8)]].sum(axis=1, skipna=False)
df["NP_TTM_growth"] = np.where(ttm_prv.abs()>0,(ttm_now-ttm_prv)/ttm_prv.abs(),np.nan).clip(-5,5)
df["TotalDebt"]=df["StDebt_P0"].fillna(0)+df["LtDebt_P0"].fillna(0)
df["NetDebt"]=df["TotalDebt"]-df["Cash_P0"].fillna(0)
df["NetDebt_EBITDA_inv"]=-np.where(df["EBITDA_P0"]>0,df["NetDebt"]/df["EBITDA_P0"],np.nan).clip(-20,50)
df["IntCov_inv"]=-df["IntCov_P0"]

# Pre-sales yields (key for long-hold REIT/REIT_RES)
df["AdvCust_yld"] = np.where(df["MktCap"]>0, df["AdvCust_P0"]/df["MktCap"], np.nan).clip(-1, 10)
df["Backlog_yld"] = np.where(df["MktCap"]>0,
                              (df["AdvCust_P0"].fillna(0) + df["UnearnRev_P0"].fillna(0))/df["MktCap"],
                              np.nan).clip(-1, 10)

# Sub-sector classification
def subsector_v8c_final(row):
    icb = row["ICB_Code"]; tk = row["ticker"]
    if icb == 8355:                            return "BANK"
    if icb in (8775, 8777):                    return "SECURITIES"
    if icb == 8536:                            return "INSURANCE"
    if icb in (8633, 8637):
        if tk in RESIDENTIAL_TICKERS:          return "REIT_RES"
        return "REIT"
    if icb == 3353:                            return "BLACKLIST_AUTO"
    return "DEFAULT"

df["sub"] = df.apply(subsector_v8c_final, axis=1)
print("\nSub-sector distribution:\n" + df["sub"].value_counts().to_string())

# Within-sub-sector per-quarter rank
ALL_INDS = ["ROIC5Y","ROE_Min5Y","ROE_Trailing","NP_R","NP_TTM_growth","NP_peak_ratio","Rev_peak_ratio",
            "GPM_change","NP_CV","Rev_CV","LT_CAGR","CF_OA_5Y","CFOA_NP","FCF_yield","FCF_OA_ratio",
            "Cash_MktCap","DY_adj","Dividend_Min3Y","DY_sust","smoothed_EY","EY","BY","CFY",
            "NetDebt_EBITDA_inv","IntCov_inv","AdvCust_yld","Backlog_yld"]
print("Computing ranks ...")
for c in ALL_INDS:
    df[f"r_{c}"] = df.groupby(["quarter","sub"])[c].rank(pct=True, na_option="keep")
df["r_magic_pb"] = (df["r_ROE_Min5Y"] + df["r_BY"]) / 2.0
df["r_magic_pe"] = (df["r_ROIC5Y"] + df["r_EY"]) / 2.0

# Schemas - same as v8c_final but with pre-sales injection for REIT_RES + REIT
SCHEMA_BANK = {
    "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.40),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.20),
    "valuation":   (["r_smoothed_EY","r_BY"], 0.40),
}
SCHEMA_SECURITIES = {
    "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.20),
    "stability":   (["r_NP_CV"], 0.10),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.10),
    "growth":      (["r_NP_R","r_NP_TTM_growth","r_NP_peak_ratio"], 0.35),
    "valuation":   (["r_smoothed_EY","r_BY"], 0.25),
}
SCHEMA_INSURANCE = {
    "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.40),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.20),
    "valuation":   (["r_smoothed_EY","r_BY"], 0.40),
}
# REIT_RES: inject pre-sales axis 0.20 (was: stability+shareholder+growth 0.35) -> rebalanced
SCHEMA_REIT_RES = {
    "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
    "valuation":   (["r_smoothed_EY","r_EY","r_CFY"], 0.30),
    "presale":     (["r_AdvCust_yld","r_Backlog_yld"], 0.20),
    "stability":   (["r_NP_CV"], 0.10),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.10),
    "growth":      (["r_NP_peak_ratio"], 0.10),
}
# REIT (KCN + other dev): inject pre-sales axis 0.20, reduce valuation, drop cash
SCHEMA_REIT = {
    "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.15),
    "cash":        (["r_CF_OA_5Y","r_FCF_yield"], 0.15),
    "presale":     (["r_AdvCust_yld","r_Backlog_yld"], 0.20),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y","r_DY_sust"], 0.15),
    "valuation":   (["r_smoothed_EY","r_BY","r_magic_pb"], 0.35),
}
SCHEMA_DEFAULT = {
    "quality":     (["r_ROIC5Y","r_ROE_Min5Y"], 0.18),
    "stability":   (["r_NP_CV","r_Rev_CV","r_LT_CAGR"], 0.18),
    "cash":        (["r_CF_OA_5Y","r_CFOA_NP"], 0.18),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y","r_FCF_OA_ratio","r_DY_sust"], 0.15),
    "growth":      (["r_GPM_change","r_NP_peak_ratio","r_Rev_peak_ratio"], 0.13),
    "health":      (["r_Cash_MktCap","r_NetDebt_EBITDA_inv","r_IntCov_inv"], 0.08),
    "valuation":   (["r_smoothed_EY","r_FCF_yield","r_magic_pe"], 0.10),
}
SCHEMAS = {"BANK":SCHEMA_BANK,"SECURITIES":SCHEMA_SECURITIES,"INSURANCE":SCHEMA_INSURANCE,
           "REIT_RES":SCHEMA_REIT_RES,"REIT":SCHEMA_REIT,"DEFAULT":SCHEMA_DEFAULT}
for name, s in SCHEMAS.items():
    total = sum(w for _, w in s.values())
    assert abs(total-1.0) < 1e-9, f"{name} sums {total}"

def score_with_schema(df_local, schema):
    weights_sum = sum(w for _, w in schema.values())
    total = np.zeros(len(df_local))
    nan_mask = np.zeros(len(df_local), dtype=bool)
    for axis, (rank_cols, w) in schema.items():
        s = df_local[rank_cols].mean(axis=1, skipna=True).values
        nan_mask |= np.isnan(s)
        total += np.nan_to_num(s, nan=0.0) * w
    return np.where(nan_mask, np.nan, total / weights_sum)

print("Scoring ...")
df["score"] = np.nan
for sub, sch in SCHEMAS.items():
    mask = df["sub"] == sub
    if mask.sum() == 0: continue
    df.loc[mask, "score"] = score_with_schema(df[mask], sch)
df.loc[df["sub"]=="BLACKLIST_AUTO", "score"] = 0.0

# Tier within (quarter, sub-sector)
def tier_of(p):
    for n,lo,hi in TIERS:
        if lo<=p<=hi: return n
    return "E"

mask_valid = df["score"].notna()
df["pct"] = np.nan
df.loc[mask_valid, "pct"] = df.loc[mask_valid].groupby(["quarter","sub"])["score"].rank(pct=True)
df["tier"] = df["pct"].apply(lambda p: tier_of(p) if pd.notna(p) else "E")
df.loc[df["sub"]=="BLACKLIST_AUTO", "tier"] = "E"

# Output: minimal columns for backtest
out = df[["ticker","quarter","time","Release_Date","sub","ICB_Code","MktCap","Volume_3M_P50","Close",
          "score","pct","tier"]].copy()
out = out.sort_values(["quarter","ticker"]).reset_index(drop=True)

# Tier distribution check
print("\nTier distribution by quarter (last 8Q):")
qq = sorted(out["quarter"].unique())[-8:]
print(out[out["quarter"].isin(qq)].pivot_table(index="quarter", columns="tier", values="ticker", aggfunc="count", fill_value=0).to_string())

print("\nA tier per sub (full history):")
print(out[out["tier"]=="A"]["sub"].value_counts().to_string())

out.to_csv(OUT_CSV, index=False)
print(f"\nWrote {OUT_CSV} ({len(out):,} rows)")
print("DONE")
