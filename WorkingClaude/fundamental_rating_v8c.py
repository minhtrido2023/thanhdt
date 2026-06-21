#!/usr/bin/env python3
"""
fundamental_rating_v8c.py
==========================
Production v8c_final ratings generator.

Sub-sector schemas:
  BANK (ICB 8355)            → Q + Sh + V (40/20/40)
  SECURITIES (8775/8777)     → Q + S + Sh + G + V (20/10/10/35/25) growth-focused
  INSURANCE (8536)           → Q + Sh + V (40/20/40)
  REIT_RES (manual ticker)   → Q + V + S + Sh + G (25/40/15/10/10) value-quality
  REIT (8633/8637 non-RES)   → Q + Ca + Sh + V (20/20/20/40) FCF augmented
  BLACKLIST_AUTO (3353)      → force E tier
  DEFAULT (else)             → v6b 7-axis universal

Tier: within (quarter, sub-sector), top 10%/30%/60%/85%.

Output: fundamental_rating_v8c.csv + uploads to tav2_bq.fa_ratings_v8c
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"
OUT_CSV = "data/fundamental_rating_v8c.csv"
TIERS = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]

# Manual classification: residential developers (split out of REIT)
RESIDENTIAL_TICKERS = {
    "VHM","NVL","DXG","KDH","NLG","AGG","KHG","HDG","CRE","FLC","IJC","HDC",
    "TIG","QCG","DIG","DXS","HQC","API","AAV","BII","C21","ITC","SCR","VPI",
    "CEO","TCH","NTL",
}

def bq_query(sql, label=""):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = (f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
               f'--project_id={PROJECT} --format=csv --max_rows=10000000')
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0:
        raise RuntimeError(f"[BQ ERROR] {label}: {(r.stdout or r.stderr)[:600]}")
    return pd.read_csv(StringIO(r.stdout.strip()))

# Pull all raw data (since 2014, matches BA-system baseline)
SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE_Trailing, f.FSCORE,
    f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y, f.Dividend_3Y,
    SAFE_DIVIDE(f.CF_OA_5Y + f.CF_Invest_5Y, ABS(f.CF_OA_5Y)) AS FCF_OA_ratio,
    f.Debt_Eq_P0, f.IntCov_P0, f.CashR_P0,
    f.PE, f.PB, f.PCF, f.OShares,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
    f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3,
    f.StDebt_P0, f.LtDebt_P0, f.Cash_P0, f.EBITDA_P0,
    f.AdvCust_P0, f.AdvCust_P4, f.UnearnRev_P0,
    CASE WHEN GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0, GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    CASE WHEN GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                       f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7) > 0
         THEN SAFE_DIVIDE(f.Revenue_P0, GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                                                  f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7))
         ELSE NULL END AS Rev_peak_ratio,
    t.Close, t.ICB_Code, t.profit_3M,
    t.Volume_3M_P50 * t.Close AS trading_value_1M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2014-01-01"
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching raw data ..."); df = bq_query(SQL, "raw")
print(f"  {len(df):,} rows (all quarters since 2014)")
df["ICB_Code"] = df["ICB_Code"].fillna(0).astype(int)

# ─── Sub-sector classification ──────────────────────────────────────────
def subsector(row):
    icb = row["ICB_Code"]; tk = row["ticker"]
    if icb == 8355:                            return "BANK"
    if icb in (8775, 8777):                    return "SECURITIES"
    if icb == 8536:                            return "INSURANCE"
    if icb in (8633, 8637):
        if tk in RESIDENTIAL_TICKERS:          return "REIT_RES"
        return "REIT"
    if icb == 3353:                            return "BLACKLIST_AUTO"
    return "DEFAULT"

df["sub_sector"] = df.apply(subsector, axis=1)
print("\nSub-sector distribution:")
print(df["sub_sector"].value_counts().to_string())

# ─── Build all indicators ───────────────────────────────────────────────
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"]*_mult; df["DY_sust"] = _mult

# Stability (NP/Rev CV — inverted: lower CV = higher rank = good)
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

# Valuation v6 (Opt B)
df["NP_4Q_mean"]=df[[f"NP_P{i}" for i in range(4)]].mean(axis=1,skipna=True)
df["MktCap"]=df["Close"]*df["OShares"]
df["smoothed_EY"]=(df["NP_4Q_mean"]/df["OShares"].replace(0,np.nan)/df["Close"].replace(0,np.nan)).clip(-1,1)
df["EY"]=np.where(df["PE"]>0,1.0/df["PE"],np.nan)
df["BY"]=np.where(df["PB"]>0,1.0/df["PB"],np.nan)
df["CFY"]=np.where(df["PCF"]>0,1.0/df["PCF"],np.nan)
df["FCF_4Q"]=(df["CF_OA_P0"]+df["CF_OA_P1"]+df["CF_OA_P2"]+df["CF_OA_P3"]
            +df["CF_Invest_P0"]+df["CF_Invest_P1"]+df["CF_Invest_P2"]+df["CF_Invest_P3"])
df["FCF_yield"]=(df["FCF_4Q"]/df["MktCap"]).clip(-1,1)

# Health v6 (rescued)
df["TotalDebt"]=df["StDebt_P0"].fillna(0)+df["LtDebt_P0"].fillna(0)
df["NetDebt"]=df["TotalDebt"]-df["Cash_P0"].fillna(0)
df["NetDebt_EBITDA_inv"]=-np.where(df["EBITDA_P0"]>0,df["NetDebt"]/df["EBITDA_P0"],np.nan).clip(-20,50)
df["Cash_MktCap"]=np.where(df["MktCap"]>0,df["Cash_P0"]/df["MktCap"],np.nan).clip(-1,5)
df["IntCov_inv"]=-df["IntCov_P0"]

# NP_TTM_growth (for Securities schema)
ttm_now = df[[f"NP_P{i}" for i in range(4)]].sum(axis=1, skipna=False)
ttm_prv = df[[f"NP_P{i}" for i in range(4,8)]].sum(axis=1, skipna=False)
df["NP_TTM_growth"] = np.where(ttm_prv.abs()>0,(ttm_now-ttm_prv)/ttm_prv.abs(),np.nan).clip(-5,5)

# ─── Within-sub-sector ranks ──────────────────────────────────────────────
RANK_INDS = ["ROIC5Y","ROE_Min5Y","ROE_Trailing","NP_R","NP_TTM_growth","NP_peak_ratio","Rev_peak_ratio",
             "GPM_change","NP_CV","Rev_CV","LT_CAGR","CF_OA_5Y","CFOA_NP","FCF_yield","FCF_OA_ratio",
             "Cash_MktCap","DY_adj","Dividend_Min3Y","DY_sust","smoothed_EY","EY","BY","CFY",
             "NetDebt_EBITDA_inv","IntCov_inv"]
print("\nComputing within-sub-sector ranks ...")
for c in RANK_INDS:
    df[f"r_{c}"] = df.groupby(["quarter","sub_sector"])[c].rank(pct=True, na_option="keep")
df["r_magic_pb"] = (df["r_ROE_Min5Y"] + df["r_BY"]) / 2.0
df["r_magic_pe"] = (df["r_ROIC5Y"] + df["r_EY"]) / 2.0

# ─── Schemas ──────────────────────────────────────────────────────────────
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
SCHEMA_REIT_RES = {
    "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.25),
    "valuation":   (["r_smoothed_EY","r_EY","r_CFY"], 0.40),
    "stability":   (["r_NP_CV"], 0.15),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.10),
    "growth":      (["r_NP_peak_ratio"], 0.10),
}
SCHEMA_REIT = {
    "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.20),
    "cash":        (["r_CF_OA_5Y","r_FCF_yield"], 0.20),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y","r_DY_sust"], 0.20),
    "valuation":   (["r_smoothed_EY","r_BY","r_magic_pb"], 0.40),
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
SCHEMAS = {"BANK":SCHEMA_BANK, "SECURITIES":SCHEMA_SECURITIES, "INSURANCE":SCHEMA_INSURANCE,
           "REIT_RES":SCHEMA_REIT_RES, "REIT":SCHEMA_REIT, "DEFAULT":SCHEMA_DEFAULT}
for name, s in SCHEMAS.items():
    assert abs(sum(w for _,w in s.values()) - 1.0) < 1e-9, f"{name} weights bad"

def score_with_schema(df_local, schema):
    weights_sum = sum(w for _, w in schema.values())
    total = np.zeros(len(df_local))
    nan_mask = np.zeros(len(df_local), dtype=bool)
    axis_scores = {}
    for axis, (rank_cols, w) in schema.items():
        s = df_local[rank_cols].mean(axis=1, skipna=True).values
        axis_scores[axis] = s
        nan_mask |= np.isnan(s)
        total += np.nan_to_num(s, nan=0.0) * w
    return np.where(nan_mask, np.nan, total / weights_sum), axis_scores

# ─── Apply per-sub-sector scoring ────────────────────────────────────────
print("Computing v8c scores per sub-sector ...")
df["total_score"] = np.nan
# Track which axes contribute for each row (for diagnostic output)
all_axes = ["quality","stability","cash","shareholder","growth","health","valuation"]
for ax in all_axes:
    df[f"score_{ax}"] = np.nan

for sub, sch in SCHEMAS.items():
    mask = df["sub_sector"] == sub
    if mask.sum() == 0: continue
    scores, axis_scores = score_with_schema(df[mask], sch)
    df.loc[mask, "total_score"] = scores
    for axis in sch:
        df.loc[mask, f"score_{axis}"] = axis_scores[axis]

# BLACKLIST_AUTO: force score to 0 (will become tier E)
df.loc[df["sub_sector"]=="BLACKLIST_AUTO", "total_score"] = 0.0

# ─── Tier assignment (within sub-sector × quarter) ────────────────────────
print("Assigning tiers within (quarter, sub-sector) ...")
def tier_of(p):
    for n,lo,hi in TIERS:
        if lo<=p<=hi: return n
    return "E"

valid = df.dropna(subset=["total_score"]).copy()
valid["score_pct"] = valid.groupby(["quarter","sub_sector"])["total_score"].rank(pct=True)
valid["tier"] = valid["score_pct"].apply(tier_of)
valid.loc[valid["sub_sector"]=="BLACKLIST_AUTO", "tier"] = "E"

print(f"  {len(valid):,} rows scored")

# ─── Validation: forward profit_3M by tier ─────────────────────────────────
q4 = valid[valid["quarter"].str.endswith("Q4")].copy()
print(f"\n=== Q4 tier ordering (forward profit_3M, N={len(q4):,}) ===")
v = q4.dropna(subset=["profit_3M"])
for tier in ["A","B","C","D","E"]:
    g = v[v["tier"]==tier]["profit_3M"]
    if len(g):
        print(f"  {tier}  N={len(g):4d}  median={g.median():+6.2f}%  mean={g.mean():+6.2f}%  WR={(g>0).mean()*100:.1f}%")

# Per-sub-sector tier composition
print(f"\n=== A tier composition by sub-sector (Q4) ===")
for sub in sorted(q4["sub_sector"].unique()):
    A = q4[(q4["sub_sector"]==sub) & (q4["tier"]=="A")]
    A_v = A.dropna(subset=["profit_3M"])
    if len(A) < 3: continue
    med = A_v["profit_3M"].median() if len(A_v) else np.nan
    wr  = (A_v["profit_3M"]>0).mean()*100 if len(A_v) else np.nan
    print(f"  {sub:<16}  total {len(q4[q4['sub_sector']==sub]):4d}  A={len(A):3d}  med={med:+5.2f}%  WR={wr:5.1f}%")

# ─── Save output ────────────────────────────────────────────────────────
keep = ["ticker", "quarter", "time", "trading_value_1M", "ICB_Code", "sub_sector",
        "score_quality", "score_stability", "score_cash", "score_shareholder",
        "score_growth", "score_health", "score_valuation",
        "total_score", "score_pct", "tier"]
out = valid[keep].sort_values(["time","sub_sector","tier","ticker"], ascending=[False,True,True,True])
out.to_csv(OUT_CSV, index=False)
print(f"\nSaved {OUT_CSV}  ({len(out):,} rows)")

# Summary
print(f"\nDistribution:")
print(out["tier"].value_counts().sort_index().to_string())

print("\n=== Tickers ready for upload ===")
print(f"  CSV: {OUT_CSV}")
print(f"  Total rows: {len(out):,}")
print(f"  Latest: {out['time'].max()}")
print(f"\nNext: bq load --replace --source_format=CSV --skip_leading_rows=1 --autodetect \\")
print(f"      lithe-record-440915-m9:tav2_bq.fa_ratings_v8c {OUT_CSV}")
