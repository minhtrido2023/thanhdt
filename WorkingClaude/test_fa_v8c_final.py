#!/usr/bin/env python3
"""
test_fa_v8c_final.py
====================
v8c_final = selective sub-sector schemas (only adopt where v8c wins).

Drops:
  - REIT_KCN (broken — fell to v8b REIT bucket)
  - MAT (lost vs v6b — fell to DEFAULT)
  - DEFAULT sub-sectors (Industrials/Materials/Tech/etc.) all use v6b

Adopts:
  - BANK (8355)            → v8b BANK schema (Q+V)
  - SECURITIES (8775/8777) → v8b SEC growth-focused
  - INSURANCE (8536)       → v8b INS simple Q+V
  - REIT_RES (manual list) → NEW value-quality (winner WR 75%)
  - REIT (8633/8637, non-RES, includes KCN) → v8b REIT_OTHER (FCF augmented)
  - BLACKLIST_AUTO (3353)  → force-exclude
  - DEFAULT (everything else) → v6b universal

Compare: v6b vs v8b vs v8c_final at profit_3M, O6M, O1Y, O2Y.
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

# Manual classification: residential developers (REIT_RES)
RESIDENTIAL_TICKERS = {"VHM","NVL","DXG","KDH","NLG","AGG","KHG","HDG","CRE","FLC","IJC","HDC",
                       "TIG","QCG","DIG","DXS","HQC","API","AAV","BII","C21","ITC","SCR","VPI",
                       "CEO","TCH","NTL"}

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

SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE_Trailing,
    f.NP_R, f.Revenue_YoY_P0,
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

print("Fetching ..."); df = bq_query(SQL); print(f"  {len(df):,} rows")
df["ICB_Code"] = df["ICB_Code"].fillna(0).astype(int)

# Build indicators
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

# v8c_final sub-sector classification
def subsector_v8c_final(row):
    icb = row["ICB_Code"]; tk = row["ticker"]
    if icb == 8355:                            return "BANK"
    if icb in (8775, 8777):                    return "SECURITIES"
    if icb == 8536:                            return "INSURANCE"
    if icb in (8633, 8637):
        if tk in RESIDENTIAL_TICKERS:          return "REIT_RES"
        return "REIT"  # KCN, REIT_OTHER merge here
    if icb == 3353:                            return "BLACKLIST_AUTO"
    return "DEFAULT"

df["sub"] = df.apply(subsector_v8c_final, axis=1)
print("\nSub-sector distribution:")
print(df["sub"].value_counts().to_string())

# Compute within-sub-sector ranks (for v8c_final scoring)
ALL_INDS = ["ROIC5Y","ROE_Min5Y","ROE_Trailing","NP_R","NP_TTM_growth","NP_peak_ratio","Rev_peak_ratio",
            "GPM_change","NP_CV","Rev_CV","LT_CAGR","CF_OA_5Y","CFOA_NP","FCF_yield","FCF_OA_ratio",
            "Cash_MktCap","DY_adj","Dividend_Min3Y","DY_sust","smoothed_EY","EY","BY","CFY",
            "NetDebt_EBITDA_inv","IntCov_inv"]
print("Computing within-sub-sector ranks ...")
for c in ALL_INDS:
    df[f"r_{c}"] = df.groupby(["quarter","sub"])[c].rank(pct=True, na_option="keep")
df["r_magic_pb"] = (df["r_ROE_Min5Y"] + df["r_BY"]) / 2.0
df["r_magic_pe"] = (df["r_ROIC5Y"] + df["r_EY"]) / 2.0

# Schemas (only winners adopted)
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
SCHEMA_REIT = {  # for all REIT non-residential (KCN + OTHER): v8b REIT schema
    "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.20),
    "cash":        (["r_CF_OA_5Y","r_FCF_yield"], 0.20),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y","r_DY_sust"], 0.20),
    "valuation":   (["r_smoothed_EY","r_BY","r_magic_pb"], 0.40),
}
SCHEMA_DEFAULT = {  # v6b universal (within-sub ranking)
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

# Apply v8c_final scoring
print("Scoring v8c_final ...")
df["v8c_score"] = np.nan
for sub, sch in SCHEMAS.items():
    mask = df["sub"] == sub
    if mask.sum() == 0: continue
    df.loc[mask, "v8c_score"] = score_with_schema(df[mask], sch)
df.loc[df["sub"]=="BLACKLIST_AUTO", "v8c_score"] = 0.0  # force bottom

# Also compute v6b global score (baseline comparison)
ALL_INDS_G = list(set(ALL_INDS))
for c in ALL_INDS_G:
    df[f"g_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
df["g_magic_pe"] = (df["g_ROIC5Y"] + df["g_EY"]) / 2.0
v6b_axes_global = {
    "quality":     (["g_ROIC5Y","g_ROE_Min5Y"], 0.18),
    "stability":   (["g_NP_CV","g_Rev_CV","g_LT_CAGR"], 0.18),
    "cash":        (["g_CF_OA_5Y","g_CFOA_NP"], 0.18),
    "shareholder": (["g_DY_adj","g_Dividend_Min3Y","g_FCF_OA_ratio","g_DY_sust"], 0.15),
    "growth":      (["g_GPM_change","g_NP_peak_ratio","g_Rev_peak_ratio"], 0.13),
    "health":      (["g_Cash_MktCap","g_NetDebt_EBITDA_inv","g_IntCov_inv"], 0.08),
    "valuation":   (["g_smoothed_EY","g_FCF_yield","g_magic_pe"], 0.10),
}
df["v6b_score"] = score_with_schema(df, v6b_axes_global)

# Tier assignment
def tier_of(p):
    for n,lo,hi in TIERS:
        if lo<=p<=hi: return n
    return "E"

df_v6b = df.dropna(subset=["v6b_score"]).copy()
df_v6b["pct"] = df_v6b.groupby("quarter")["v6b_score"].rank(pct=True)
df_v6b["tier"] = df_v6b["pct"].apply(tier_of)

df_v8c = df.dropna(subset=["v8c_score"]).copy()
df_v8c["pct"] = df_v8c.groupby(["quarter","sub"])["v8c_score"].rank(pct=True)
df_v8c["tier"] = df_v8c["pct"].apply(tier_of)
df_v8c.loc[df_v8c["sub"]=="BLACKLIST_AUTO", "tier"] = "E"

# Reports
def tier_summary(d, target):
    v = d.dropna(subset=[target])
    rows = []
    for tier in ["A","B","C","D","E"]:
        g = v[v["tier"]==tier][target]
        if len(g):
            rows.append({"tier":tier,"N":len(g),"median":g.median(),
                         "mean":g.mean(),"WR":(g>0).mean()*100})
    return pd.DataFrame(rows)

print("\n" + "="*80); print("v8c_final OVERALL TIER ORDERING (profit_3M)"); print("="*80)
for label, d in [("v6b global", df_v6b), ("v8c_final", df_v8c)]:
    t = tier_summary(d, "profit_3M")
    meds = t["median"].values
    spread = meds[0]-meds[-1] if len(meds)==5 else np.nan
    inv = sum(1 for i in range(len(meds)-1) if meds[i]<meds[i+1])
    print(f"\n{label}:")
    print(t.to_string(index=False, float_format="%.2f"))
    print(f"  spread = {spread:+.2f}  inv={inv}")

# Multi-horizon
print("\n" + "="*80); print("MULTI-HORIZON A TIER + COMPOSITE IC"); print("="*80)
print(f"\n{'Horizon':<12}{'Variant':<14}{'A N':>5}{'A med':>9}{'A WR':>8}{'spread':>9}{'IC':>9}")
for target in ["profit_3M","O6M","O1Y","O2Y"]:
    for label, d in [("v6b global", df_v6b), ("v8c_final", df_v8c)]:
        t = tier_summary(d, target)
        if len(t) < 5: continue
        a = t[t.tier=="A"].iloc[0]
        spread = t["median"].iloc[0] - t["median"].iloc[-1]
        ic, _ = spearman_ic(d.dropna(subset=[target])["v6b_score" if "v6b" in label else "v8c_score"],
                            d.dropna(subset=[target])[target])
        print(f"{target:<12}{label:<14}{int(a.N):>5}{a['median']:>+8.3f}{a['WR']:>+7.1f}%{spread:>+9.3f}{ic:>+9.3f}")
    print()

# Per-sub-sector A tier breakdown
print("\n" + "="*80); print("v8c_final per-sub-sector A tier"); print("="*80)
print(f"\n  {'Sub-sector':<14}{'N':>5}{'A_n':>5}{'A_med':>9}{'A_WR':>8}{'all_med':>10}{'all_WR':>9}")
print("  " + "-"*65)
for sub in sorted(df_v8c["sub"].unique()):
    if sub == "BLACKLIST_AUTO": continue
    s = df_v8c[df_v8c["sub"]==sub]
    A = s[s["tier"]=="A"].dropna(subset=["profit_3M"])
    all_v = s.dropna(subset=["profit_3M"])
    if len(A) < 3: continue
    print(f"  {sub:<14}{len(s):>5}{len(A):>5}{A['profit_3M'].median():>+8.2f}%{(A['profit_3M']>0).mean()*100:>+7.1f}%"
          f"{all_v['profit_3M'].median():>+9.2f}%{(all_v['profit_3M']>0).mean()*100:>+8.1f}%")

# Within sub-sector tier ordering
print("\n" + "="*80); print("WITHIN sub-sector tier ordering (profit_3M, v8c_final)"); print("="*80)
for sub in sorted(df_v8c["sub"].unique()):
    if sub == "BLACKLIST_AUTO": continue
    s = df_v8c[df_v8c["sub"]==sub]
    if len(s) < 30: continue
    print(f"\n  --- {sub} (N={len(s)}) ---")
    for tier in ["A","B","C","D","E"]:
        g = s[s["tier"]==tier].dropna(subset=["profit_3M"])["profit_3M"]
        if len(g):
            print(f"    {tier}  N={len(g):4d}  med={g.median():+6.2f}%  WR={(g>0).mean()*100:.1f}%")

print("\n" + "="*80); print("DONE"); print("="*80)
