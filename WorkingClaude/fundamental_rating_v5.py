#!/usr/bin/env python3
"""
fundamental_rating_v5.py
========================
v5 = v4 + H3+H4 combo (validated via test_fa_t6_combo.py)

Changes vs v4:
  H3: Indicator-level NaN fill 0 (within axis, BEFORE mean)
  H4: Beneish-lite indicators (DSO_delta, FinLev_delta, GPM_delta_abs,
      AT_delta) added to health axis ONLY for DEFAULT sector
  + Hybrid mode: universe-rank DEFAULT, sector-rank for BANK/REIT/INS/SEC
  + Sector buckets by numeric ICB_Code (8355=BANK, 8633/37=REIT,
    8536=INS, 8775/77=SEC, else DEFAULT)

Expected Q4 improvement vs v4:
  A median: 6.67% → 7.39% (+0.72)
  A mean:   7.31% → 8.58% (+1.27)
  Tier mono robust across all-quarter universe (v4 had A<B inversion)

Output schema MATCHES v4 (same columns) so BA-system can swap in.
Output: fundamental_rating_v5.csv  (drop-in for fundamental_rating_all.csv)
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"
OUT_CSV = "fundamental_rating_v5.csv"

WEIGHTS = {"quality":0.18,"stability":0.18,"cash":0.18,"shareholder":0.15,
           "growth":0.13,"health":0.08,"valuation":0.10}
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

SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.FSCORE, f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y,
    SAFE_DIVIDE(f.CF_OA_5Y + f.CF_Invest_5Y, ABS(f.CF_OA_5Y)) AS FCF_OA_ratio,
    f.Debt_Eq_P0, f.IntCov_P0, f.CashR_P0,
    SAFE_DIVIDE(f.PE - f.PE_MA5Y, f.PE_SD5Y) AS PE_self_z,
    SAFE_DIVIDE(f.PB - f.PB_MA5Y, f.PB_SD5Y) AS PB_self_z,
    CASE WHEN f.PE > 0 THEN SAFE_DIVIDE(f.NP_R, f.PE) ELSE NULL END AS growth_yield,
    f.PE, f.PB, f.PCF,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
    f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7,
    f.GPM_P0, f.GPM_P4, f.DSO_P0, f.DSO_P4, f.FinLev_P0, f.FinLev_P4,
    f.AssetTurn_P0, f.AssetTurn_P4,
    CASE WHEN GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0, GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    CASE WHEN GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                       f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7) > 0
         THEN SAFE_DIVIDE(f.Revenue_P0, GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                                                  f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7))
         ELSE NULL END AS Rev_peak_ratio,
    t.ICB_Code,
    t.Volume_3M_P50 * t.Close AS trading_value_1M,
    t.profit_3M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2014-01-01"
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching raw indicators ..."); df = bq_query(SQL)
print(f"  {len(df):,} rows after liquidity filter")

# Sector bucket
def sector_bucket(icb):
    if pd.isna(icb): return "DEFAULT"
    try: code = int(float(icb))
    except: return "DEFAULT"
    if code == 8355: return "BANK"
    if code in (8633, 8637): return "REIT"
    if code == 8536: return "INSURANCE"
    if code in (8775, 8777): return "SECURITIES"
    return "DEFAULT"
df["sector"] = df["ICB_Code"].apply(sector_bucket)

# Standard transforms
df["growth_yield"] = df["growth_yield"].clip(-0.15, 0.15)
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"]*_mult; df["DY_sust"]=_mult
NP_COLS=[f"NP_P{i}" for i in range(8)]; REV_COLS=[f"Revenue_P{i}" for i in range(8)]
np_arr=df[NP_COLS].values.astype(float); rev_arr=df[REV_COLS].values.astype(float)
np_n=np.sum(~np.isnan(np_arr),axis=1); rev_n=np.sum(~np.isnan(rev_arr),axis=1)
with np.errstate(divide="ignore",invalid="ignore"):
    np_mean=np.nanmean(np_arr,axis=1); np_std=np.nanstd(np_arr,axis=1,ddof=1)
    rev_mean=np.nanmean(rev_arr,axis=1); rev_std=np.nanstd(rev_arr,axis=1,ddof=1)
    df["NP_CV"]=np.where(np_n>=6,  np_std/np.maximum(np.abs(np_mean), 1e6), np.nan)
    df["Rev_CV"]=np.where(rev_n>=6, rev_std/np.maximum(np.abs(rev_mean),1e6), np.nan)
    df["NP_CV"]=df["NP_CV"].clip(upper=10); df["Rev_CV"]=df["Rev_CV"].clip(upper=10)
rev_p0=df["Revenue_P0"].values; rev_p7=df["Revenue_P7"].values
mask=(rev_p0>0)&(rev_p7>0)
df["LT_CAGR"] = np.where(mask, (rev_p0/rev_p7)**(4/7)-1, np.nan).clip(min=-0.95, max=5.0)
df["ICB_Code_raw"] = df["ICB_Code"].fillna("UNK")
for col in ["PE","PB","PCF"]:
    grp = df.groupby(["quarter","ICB_Code_raw"])[col]
    med=grp.transform("median"); sd=grp.transform("std")
    z_ind = (df[col]-med)/sd.replace(0,np.nan)
    z_global = df.groupby("quarter")[col].transform(lambda x: (x-x.median())/x.std())
    df[f"{col}_ind_z"] = z_ind.fillna(z_global)

# Beneish-lite indicators (used only for DEFAULT health axis)
df["DSO_delta"]    = df["DSO_P0"] - df["DSO_P4"]
df["FinLev_delta"] = df["FinLev_P0"] - df["FinLev_P4"]
df["GPM_delta_abs"]= df["GPM_P4"] - df["GPM_P0"]
df["AT_delta"]     = df["AssetTurn_P4"] - df["AssetTurn_P0"]

INV=["Debt_Eq_P0","PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","NP_CV","Rev_CV",
     "DSO_delta","FinLev_delta","GPM_delta_abs","AT_delta"]
for c in INV: df[c] = -df[c]

AXIS_BASE = {
    "quality":     ["ROIC5Y","ROE_Min5Y","FSCORE"],
    "stability":   ["NP_CV","Rev_CV","LT_CAGR"],
    "cash":        ["CF_OA_5Y","CFOA_NP"],
    "shareholder": ["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
    "growth":      ["NP_R","Revenue_YoY_P0","GPM_change","NP_peak_ratio","Rev_peak_ratio"],
    "health":      ["Debt_Eq_P0","IntCov_P0","CashR_P0"],
    "valuation":   ["PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","growth_yield"],
}
AXIS_DEFAULT = dict(AXIS_BASE)
AXIS_DEFAULT["health"] = AXIS_BASE["health"] + ["DSO_delta","FinLev_delta","GPM_delta_abs","AT_delta"]
AXIS_FIN = AXIS_BASE  # financials keep base health (Beneish not meaningful)

# Compute percentile ranks (universe + sector) for ALL indicators we'll need
all_cols = set()
for cs in AXIS_DEFAULT.values(): all_cols.update(cs)
print("Computing ranks (universe + sector) ...")
for c in all_cols:
    df[f"_u_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
    df[f"_s_{c}"] = df.groupby(["quarter","sector"])[c].rank(pct=True, na_option="keep")

# H3: indicator-level NaN fill = 0 (within axis, BEFORE mean)
# Hybrid mode: DEFAULT rows use universe rank + AXIS_DEFAULT; financials use sector rank + AXIS_FIN
is_default = (df["sector"] == "DEFAULT").values

def axis_mean(df, axis_schema, rank_prefix, fill_indicator=0.0):
    out = {}
    for a, cs in axis_schema.items():
        rcols = [f"{rank_prefix}_{c}" for c in cs]
        sub = df[rcols].fillna(fill_indicator)
        out[a] = sub.mean(axis=1, skipna=True)
    return out

print("Computing axis scores (H3 indicator-NaN-fill=0) ...")
ax_u_default = axis_mean(df, AXIS_DEFAULT, "_u", 0.0)   # for DEFAULT rows
ax_s_fin     = axis_mean(df, AXIS_FIN,     "_s", 0.0)   # for fin rows

# Compose: pick per-row axis score by sector
scores = {}
for a in WEIGHTS:
    scores[a] = pd.Series(np.where(is_default, ax_u_default[a].values, ax_s_fin[a].values),
                          index=df.index)
for a in WEIGHTS:
    df[f"score_{a}"] = scores[a].values

# Total weighted score
total = np.zeros(len(df))
for a in WEIGHTS:
    total += np.nan_to_num(scores[a].values, nan=0.0) * WEIGHTS[a]
df["total_score"] = total

# Hybrid tiering: DEFAULT rows ranked by quarter; fin rows ranked by (quarter, sector)
df["score_pct"] = np.nan
df.loc[is_default, "score_pct"] = df[is_default].groupby("quarter")["total_score"].rank(pct=True)
df.loc[~is_default, "score_pct"] = df[~is_default].groupby(["quarter","sector"])["total_score"].rank(pct=True)

def tier_of(p):
    for n, lo, hi in TIERS:
        if lo <= p <= hi: return n
    return "E"
df["tier"] = df["score_pct"].apply(tier_of)

# Save (full schema matching v4 fundamental_rating_all.csv)
keep = ["ticker", "quarter", "time", "trading_value_1M", "ICB_Code",
        "score_quality", "score_stability", "score_cash", "score_shareholder",
        "score_growth", "score_health", "score_valuation",
        "total_score", "score_pct", "tier", "profit_3M",
        "NP_CV", "Rev_CV", "LT_CAGR", "DY", "DY_adj", "DY_sust",
        "Dividend_Min3Y", "FCF_OA_ratio",
        "NP_R", "Revenue_YoY_P0", "NP_peak_ratio", "Rev_peak_ratio"]
out = df[keep].sort_values(["time", "tier", "ticker"], ascending=[False, True, True])
out.to_csv(OUT_CSV, index=False)
print(f"\nSaved {OUT_CSV} ({len(out):,} rows, all quarters)")

# Q4-only validation
print("\n=== Validation: forward profit_3M by tier (Q4-only) ===")
v_q4 = df[df["quarter"].str.endswith("Q4")].dropna(subset=["profit_3M"])
for tier in ["A","B","C","D","E"]:
    g = v_q4[v_q4["tier"]==tier]["profit_3M"]
    if len(g):
        print(f"  {tier}  N={len(g):4d}  median={g.median():6.2f}%  mean={g.mean():6.2f}%  WR={(g>0).mean()*100:.1f}%")

# Q4 sector breakdown
print("\n=== Sector composition of tier A (Q4-only) ===")
q4_A = df[(df["quarter"].str.endswith("Q4")) & (df["tier"]=="A")]
print(q4_A["sector"].value_counts().to_string())
