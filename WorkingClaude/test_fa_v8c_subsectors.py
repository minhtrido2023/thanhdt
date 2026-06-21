#!/usr/bin/env python3
"""
test_fa_v8c_subsectors.py
=========================
Deep dive into sub-sectors within Industrials, Materials, Real Estate.

Focus areas:
  1. REIT split: Industrial Park (KCN) vs Residential developers
     - KCN: SIP, KBC, IDC, NTC, TIP, BCM, SZB, SZC, LHG, ...
     - Residential: VHM, NVL, DXG, KDH, NLG, AGG, KHG, ...
     - Manual classification — VN REIT ICB doesn't split

  2. Industrials (sector 2): split by ICB 4-digit
     - 2353/2357: Construction materials & general construction
     - 2723: Electrical equipment
     - 2773/2777/2779: Transport (shipping/airports/ports)
     - 2791: Industrial support services

  3. Materials (sector 1): split
     - 1353/1357: Chemicals (fertilizer/specialty)
     - 1733/1737: Mining (coal/gold)
     - 1757/1777: Industrial metals (steel)
     - 1771/1775: Other mining/paper

For each: compute IC of v6b/v8b top indicators, identify distinct patterns.
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

# KCN tickers (curated VN industrial park developers)
KCN_TICKERS = {"SIP","KBC","IDC","NTC","TIP","BCM","SZB","SZC","LHG","SZL","D2D","IDV","BAX",
               "ITA","SNZ","VRG","VGC","HPI","MH3","NTL","SZG","TID","TIX","LHC","DXP"}
# Residential developers
RESIDENTIAL_TICKERS = {"VHM","NVL","DXG","KDH","NLG","AGG","KHG","HDG","CRE","FLC","IJC","HDC",
                       "TIG","QCG","DIG","DXS","HQC","API","AAV","BII","C21","ITC","SCR","VPI",
                       "CEO","TCH","NLG"}

SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE5Y, f.ROE_Trailing, f.FSCORE,
    f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y,
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
    df["NP_CV_inv"]=-np.where(np_n>=6,np_s/np.maximum(np.abs(np_m),1e6),np.nan).clip(max=10)
    df["Rev_CV_inv"]=-np.where(rev_n>=6,rev_s/np.maximum(np.abs(rev_m),1e6),np.nan).clip(max=10)
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

# ─── Sub-sector assignment ────────────────────────────────────────────────
def subgroup(row):
    icb = row["ICB_Code"]; tk = row["ticker"]
    # REIT split (8633/8637)
    if icb in (8633, 8637):
        if tk in KCN_TICKERS:           return "REIT_KCN"
        if tk in RESIDENTIAL_TICKERS:   return "REIT_RES"
        return "REIT_OTHER"
    # Industrials (sector 2)
    if 2000 <= icb < 3000:
        if icb in (2353, 2357):         return "IND_CONSTR"      # construction
        if icb == 2723:                 return "IND_ELECT"        # electrical
        if icb in (2773, 2777, 2779):   return "IND_TRANSPORT"    # transport
        if icb == 2791:                 return "IND_SUPPORT"
        return f"IND_{icb}"
    # Materials (sector 1)
    if 1000 <= icb < 2000:
        if icb in (1353, 1357):         return "MAT_CHEM"
        if icb in (1733, 1737, 1771):   return "MAT_MINING"
        if icb in (1757, 1777):         return "MAT_METALS"
        if icb == 1775:                 return "MAT_PAPER"
        return f"MAT_{icb}"
    # Consumer Goods (sector 3)
    if 3000 <= icb < 4000:
        if icb in (3353,):              return "CG_AUTO"
        if icb in (3533, 3537):         return "CG_TOBACCO"
        if icb in (3573, 3577):         return "CG_FOOD"
        if icb == 3763:                 return "CG_PERSONAL"
        return f"CG_{icb}"
    return f"OTHER_{icb}"

df["subgroup"] = df.apply(subgroup, axis=1)
print("\nSub-group distribution (only groups with N>=30):")
sg = df["subgroup"].value_counts()
print(sg[sg >= 30].to_string())

# Top FA indicators to test
TEST_INDICATORS = [
    ("ROIC5Y",       "ROIC5Y"),
    ("ROE_Min5Y",    "ROE_Min5Y"),
    ("FSCORE",       "FSCORE"),
    ("NP_R",         "NP_R"),
    ("NP_TTM_growth","NP_TTM_growth"),
    ("NP_peak_ratio","NP_peak_ratio"),
    ("Rev_peak_ratio","Rev_peak_ratio"),
    ("GPM_change",   "GPM_change"),
    ("NP_CV (inv)",  "NP_CV_inv"),
    ("LT_CAGR",      "LT_CAGR"),
    ("CF_OA_5Y",     "CF_OA_5Y"),
    ("CFOA_NP",      "CFOA_NP"),
    ("DY_adj",       "DY_adj"),
    ("FCF_OA_ratio", "FCF_OA_ratio"),
    ("Debt_Eq (inv)","Debt_Eq_P0"),     # raw direction (high debt = high score for VN)
    ("Cash_MktCap",  "Cash_MktCap"),
    ("NetDebt_inv",  "NetDebt_EBITDA_inv"),
    ("smoothed_EY",  "smoothed_EY"),
    ("EY (1/PE)",    "EY"),
    ("BY (1/PB)",    "BY"),
    ("CFY (1/PCF)",  "CFY"),
    ("FCF_yield",    "FCF_yield"),
]
# Compute ranks within sub-group
for _, col in TEST_INDICATORS:
    df[f"r_{col}"] = df.groupby(["quarter","subgroup"])[col].rank(pct=True, na_option="keep")

# ─── Report IC per sub-group for each indicator ───────────────────────────
groups_to_report = sg[sg >= 30].index.tolist()
print(f"\n{'='*100}")
print("IC by sub-group (within-group rank vs profit_3M)")
print('='*100)
print(f"\n{'Indicator':<22}", end="")
for g in groups_to_report:
    label = g[:11]
    print(f"{label:>10}", end="")
print()
print("-"*(22 + 10*len(groups_to_report)))
for name, col in TEST_INDICATORS:
    row = f"{name:<22}"
    for g in groups_to_report:
        sub = df[df["subgroup"]==g]
        rho, n = spearman_ic(sub[f"r_{col}"], sub["profit_3M"])
        if np.isnan(rho):
            row += f"{'  N/A':>10}"
        else:
            row += f"{rho:>+10.3f}"
    print(row)

# Sample sizes
ns_row = f"{'(N)':<22}"
for g in groups_to_report:
    sub = df[df["subgroup"]==g].dropna(subset=["profit_3M"])
    ns_row += f"{len(sub):>10}"
print(ns_row)

# ─── Identify strongest indicator per group ───────────────────────────────
print(f"\n{'='*100}")
print("TOP 3 INDICATORS PER SUB-GROUP (by |IC|)")
print('='*100)
for g in groups_to_report:
    sub = df[df["subgroup"]==g]
    n_obs = sub.dropna(subset=["profit_3M"]).shape[0]
    results = []
    for name, col in TEST_INDICATORS:
        rho, _ = spearman_ic(sub[f"r_{col}"], sub["profit_3M"])
        if not np.isnan(rho):
            results.append((name, rho))
    results.sort(key=lambda x: abs(x[1]), reverse=True)
    print(f"\n  {g} (N={n_obs}):")
    for name, rho in results[:5]:
        sign = "+" if rho > 0 else "-"
        marker = " 🟢" if abs(rho) > 0.15 else (" 🔵" if abs(rho) > 0.10 else "")
        print(f"    {sign} {name:<22} IC={rho:+.3f}{marker}")

# ─── Forward return distribution per sub-group ────────────────────────────
print(f"\n{'='*100}")
print("FORWARD RETURN SUMMARY per sub-group (profit_3M)")
print('='*100)
print(f"{'Sub-group':<18}{'N':>5}{'Mean':>9}{'Median':>9}{'StdDev':>9}{'WR':>7}")
print("-"*60)
for g in groups_to_report:
    sub = df[df["subgroup"]==g].dropna(subset=["profit_3M"])
    if len(sub) == 0: continue
    p = sub["profit_3M"]
    print(f"{g:<18}{len(p):>5}{p.mean():>+8.2f}%{p.median():>+8.2f}%{p.std():>+8.2f}%{(p>0).mean()*100:>6.1f}%")

print(f"\n{'='*100}\nDONE\n{'='*100}")
