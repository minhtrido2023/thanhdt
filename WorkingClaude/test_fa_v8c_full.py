#!/usr/bin/env python3
"""
test_fa_v8c_full.py
===================
v8c = full sub-sector FA system, building on v8b.

Sub-sector schemas:
  BANK (8355)              → v8b: Q+Sh+V (40/20/40)
  SECURITIES (8775/8777)   → v8b: growth-focused
  INSURANCE (8536)         → v8b: simple Q+V
  REIT_KCN (manual list)   → NEW: growth-cash (NP_R + Cash + GPM)
  REIT_RES (manual list)   → NEW: value-quality (smoothed_EY + ROE)
  REIT_OTHER (8633/8637)   → v8b REIT custom (FCF augmented)
  MAT (sector 1xxx)        → NEW: cash-heavy (CF_OA + FCF_yield + ROIC)
  CG_AUTO (3353)           → BLACKLIST (all FA anti-signal — exclude)
  DEFAULT                  → v6b universal (everything else)

Validation: tier-level at profit_3M, O6M, O1Y, O2Y vs v6b and v8b.
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

KCN_TICKERS = {"SIP","KBC","IDC","NTC","TIP","BCM","SZB","SZC","LHG","SZL","D2D","IDV","BAX",
               "ITA","SNZ","VRG","VGC","HPI","MH3","SZG","TID","TIX","LHC","DXP"}
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
    if r.returncode != 0: raise RuntimeError(r.stderr[:600])
    return pd.read_csv(StringIO(r.stdout.strip()))

def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 30: return float("nan"), 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE5Y, f.ROE_Trailing, f.FSCORE,
    f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y, f.Dividend_3Y,
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

# Build all indicators
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"]*_mult; df["DY_sust"] = _mult
np_arr = df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
rev_arr = df[[f"Revenue_P{i}" for i in range(8)]].values.astype(float)
np_n = np.sum(~np.isnan(np_arr),axis=1); rev_n = np.sum(~np.isnan(rev_arr),axis=1)
with np.errstate(divide="ignore",invalid="ignore"):
    np_m=np.nanmean(np_arr,axis=1); np_s=np.nanstd(np_arr,axis=1,ddof=1)
    rev_m=np.nanmean(rev_arr,axis=1); rev_s=np.nanstd(rev_arr,axis=1,ddof=1)
    df["NP_CV_raw"]=np.where(np_n>=6,np_s/np.maximum(np.abs(np_m),1e6),np.nan).clip(max=10)
    df["Rev_CV_raw"]=np.where(rev_n>=6,rev_s/np.maximum(np.abs(rev_m),1e6),np.nan).clip(max=10)
df["NP_CV"] = -df["NP_CV_raw"]; df["Rev_CV"] = -df["Rev_CV_raw"]
rev_p0=df["Revenue_P0"].values; rev_p7=df["Revenue_P7"].values
df["LT_CAGR"]=np.where((rev_p0>0)&(rev_p7>0),(rev_p0/rev_p7)**(4/7)-1,np.nan).clip(-0.95,5.0)

# v6b indicators
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

# Sub-sector assignment
def subsector(row):
    icb = row["ICB_Code"]; tk = row["ticker"]
    if icb == 8355:                            return "BANK"
    if icb in (8775, 8777):                    return "SECURITIES"
    if icb == 8536:                            return "INSURANCE"
    if icb in (8633, 8637):
        if tk in KCN_TICKERS:                  return "REIT_KCN"
        if tk in RESIDENTIAL_TICKERS:          return "REIT_RES"
        return "REIT_OTHER"
    if 1000 <= icb < 2000:                     return "MAT"
    if icb == 3353:                            return "BLACKLIST_AUTO"
    return "DEFAULT"

df["subsector"] = df.apply(subsector, axis=1)
print("\nSub-sector distribution:")
print(df["subsector"].value_counts().to_string())

# ─── Within-sub-sector ranks for each sub-sector schema ────────────────────
# Need to rank within (quarter, subsector) for each indicator used
ALL_RANK_COLS = [
    # universal indicators
    "ROIC5Y","ROE_Min5Y","ROE_Trailing","FSCORE",
    "NP_R","Revenue_YoY_P0","GPM_change","NP_peak_ratio","Rev_peak_ratio","NP_TTM_growth",
    "NP_CV","Rev_CV","LT_CAGR",
    "CF_OA_5Y","CFOA_NP","FCF_yield","FCF_OA_ratio","Cash_MktCap",
    "DY_adj","Dividend_Min3Y","DY_sust","Dividend_3Y",
    "smoothed_EY","EY","BY","CFY",
    "NetDebt_EBITDA_inv","IntCov_inv",
    "Debt_Eq_P0",  # raw (high debt = better for VN, surprising)
]
print("Computing within-sub-sector ranks ...")
for c in ALL_RANK_COLS:
    df[f"r_{c}"] = df.groupby(["quarter","subsector"])[c].rank(pct=True, na_option="keep")
# Magic formula variants (using within-subsector ranks)
df["r_magic_pb"] = (df["r_ROE_Min5Y"] + df["r_BY"]) / 2.0
df["r_magic_pe"] = (df["r_ROIC5Y"] + df["r_EY"]) / 2.0

# ═══════════════════════════════════════════════════════════════════════════
# Sub-sector schemas — each: {axis: (rank_cols, weight)}, sum of weights = 1
# ═══════════════════════════════════════════════════════════════════════════
SCHEMA_BANK = {
    "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.40),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.20),
    "valuation":   (["r_smoothed_EY","r_BY"], 0.40),
}
SCHEMA_SECURITIES = {  # v8b var5 growth-focused
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
# REIT_KCN: growth-cash (industrial parks are growth-driven)
SCHEMA_REIT_KCN = {
    "growth":      (["r_NP_R","r_NP_TTM_growth","r_NP_peak_ratio"], 0.30),
    "cash":        (["r_Cash_MktCap","r_FCF_yield","r_CF_OA_5Y"], 0.25),
    "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
    "valuation":   (["r_smoothed_EY","r_BY"], 0.15),
    "shareholder": (["r_DY_adj"], 0.10),
}
# REIT_RES: value-quality (residential needs classical FA)
SCHEMA_REIT_RES = {
    "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.25),
    "valuation":   (["r_smoothed_EY","r_EY","r_CFY"], 0.40),
    "stability":   (["r_NP_CV"], 0.15),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.10),
    "growth":      (["r_NP_peak_ratio"], 0.10),
}
# REIT_OTHER: v8b REIT custom (default fallback)
SCHEMA_REIT_OTHER = {
    "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.20),
    "cash":        (["r_CF_OA_5Y","r_FCF_yield"], 0.20),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y","r_DY_sust"], 0.20),
    "valuation":   (["r_smoothed_EY","r_BY","r_magic_pb"], 0.40),
}
# MAT: cash-heavy (commodity sectors share this pattern)
SCHEMA_MAT = {
    "cash":        (["r_CF_OA_5Y","r_FCF_yield","r_FCF_OA_ratio"], 0.40),
    "quality":     (["r_ROIC5Y","r_ROE_Min5Y"], 0.25),
    "valuation":   (["r_smoothed_EY"], 0.15),
    "health":      (["r_NetDebt_EBITDA_inv","r_Cash_MktCap"], 0.15),
    "growth":      (["r_NP_peak_ratio"], 0.05),
}
# DEFAULT: v6b universal — but using within-subsector ranks
SCHEMA_DEFAULT = {
    "quality":     (["r_ROIC5Y","r_ROE_Min5Y"], 0.18),
    "stability":   (["r_NP_CV","r_Rev_CV","r_LT_CAGR"], 0.18),
    "cash":        (["r_CF_OA_5Y","r_CFOA_NP"], 0.18),
    "shareholder": (["r_DY_adj","r_Dividend_Min3Y","r_FCF_OA_ratio","r_DY_sust"], 0.15),
    "growth":      (["r_GPM_change","r_NP_peak_ratio","r_Rev_peak_ratio"], 0.13),
    "health":      (["r_Cash_MktCap","r_NetDebt_EBITDA_inv","r_IntCov_inv"], 0.08),
    "valuation":   (["r_smoothed_EY","r_FCF_yield","r_magic_pe"], 0.10),
}
SCHEMAS = {
    "BANK":SCHEMA_BANK, "SECURITIES":SCHEMA_SECURITIES, "INSURANCE":SCHEMA_INSURANCE,
    "REIT_KCN":SCHEMA_REIT_KCN, "REIT_RES":SCHEMA_REIT_RES, "REIT_OTHER":SCHEMA_REIT_OTHER,
    "MAT":SCHEMA_MAT, "DEFAULT":SCHEMA_DEFAULT,
}
# Sanity check
for name, s in SCHEMAS.items():
    total_w = sum(w for _, w in s.values())
    assert abs(total_w - 1.0) < 1e-9, f"{name} weights sum to {total_w}"

def score_with_schema(df_local, schema):
    weights_sum = sum(w for _, w in schema.values())
    total = np.zeros(len(df_local))
    nan_mask = np.zeros(len(df_local), dtype=bool)
    for axis, (rank_cols, w) in schema.items():
        axis_score = df_local[rank_cols].mean(axis=1, skipna=True).values
        nan_mask |= np.isnan(axis_score)
        total += np.nan_to_num(axis_score, nan=0.0) * w
    return np.where(nan_mask, np.nan, total / weights_sum)

# Apply per-sub-sector schema scoring
print("Scoring per sub-sector ...")
df["v8c_score"] = np.nan
for sub, sch in SCHEMAS.items():
    mask = df["subsector"] == sub
    if mask.sum() == 0: continue
    df.loc[mask, "v8c_score"] = score_with_schema(df[mask], sch)
# BLACKLIST_AUTO: assign very low score so they fall to E
df.loc[df["subsector"]=="BLACKLIST_AUTO", "v8c_score"] = 0.0  # forced bottom

# Also compute v6b global universal score (apples-to-apples baseline)
# Need GLOBAL ranks (not within-subsector) for v6b
ALL_INDS_GLOBAL = ["ROIC5Y","ROE_Min5Y","NP_CV","Rev_CV","LT_CAGR","CF_OA_5Y","CFOA_NP",
                   "DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust",
                   "GPM_change","NP_peak_ratio","Rev_peak_ratio",
                   "Cash_MktCap","NetDebt_EBITDA_inv","IntCov_inv",
                   "smoothed_EY","FCF_yield","ROIC5Y","EY"]
for c in set(ALL_INDS_GLOBAL):
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
    for n, lo, hi in TIERS:
        if lo <= p <= hi: return n
    return "E"

# v6b: tier globally
df_v6b = df.dropna(subset=["v6b_score"]).copy()
df_v6b["pct"] = df_v6b.groupby("quarter")["v6b_score"].rank(pct=True)
df_v6b["tier"] = df_v6b["pct"].apply(tier_of)

# v8c: tier within sub-sector
df_v8c = df.dropna(subset=["v8c_score"]).copy()
df_v8c["pct"] = df_v8c.groupby(["quarter","subsector"])["v8c_score"].rank(pct=True)
df_v8c["tier"] = df_v8c["pct"].apply(tier_of)
# Force BLACKLIST_AUTO to E
df_v8c.loc[df_v8c["subsector"]=="BLACKLIST_AUTO", "tier"] = "E"

# ═══════════════════════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════════════════════
def tier_summary(df_, target):
    v = df_.dropna(subset=[target])
    rows = []
    for tier in ["A","B","C","D","E"]:
        g = v[v["tier"]==tier][target]
        if len(g):
            rows.append({"tier":tier,"N":len(g),"median":g.median(),
                         "mean":g.mean(),"WR":(g>0).mean()*100})
    return pd.DataFrame(rows)

print("\n" + "="*80); print("OVERALL TIER ORDERING — profit_3M"); print("="*80)
for label, d in [("v6b global", df_v6b), ("v8c sub-sector", df_v8c)]:
    t = tier_summary(d, "profit_3M")
    meds = t["median"].values
    spread = meds[0]-meds[-1] if len(meds)==5 else np.nan
    inv = sum(1 for i in range(len(meds)-1) if meds[i]<meds[i+1])
    print(f"\n{label}:")
    print(t.to_string(index=False, float_format="%.2f"))
    print(f"  spread A-E = {spread:+.2f}pp  inv={inv}")

# Multi-horizon
print("\n" + "="*80); print("MULTI-HORIZON A TIER SUMMARY"); print("="*80)
print(f"\n{'Horizon':<12}{'Variant':<18}{'A N':>5}{'A median':>10}{'A WR':>9}{'spread':>9}")
for target in ["profit_3M","O6M","O1Y","O2Y"]:
    for label, d in [("v6b global", df_v6b), ("v8c sub-sector", df_v8c)]:
        t = tier_summary(d, target)
        if len(t) < 5: continue
        a = t[t.tier=="A"].iloc[0]
        spread = t["median"].iloc[0] - t["median"].iloc[-1]
        print(f"{target:<12}{label:<18}{int(a.N):>5}{a['median']:>+9.3f}{a['WR']:>+8.1f}%{spread:>+9.3f}")
    print()

# Per-sub-sector A tier comparison (v6b A picks within sub vs v8c A picks)
print("\n" + "="*80); print("A TIER PER SUB-SECTOR — v6b vs v8c"); print("="*80)
print(f"\n{'Sub-sector':<18}{'v6b A':>22}{'v8c A':>22}{'Δmed':>9}{'ΔWR':>8}")
print("-"*85)
all_subs = sorted(df["subsector"].unique())
for sub in all_subs:
    sub_v6 = df_v6b[(df_v6b["subsector"]==sub) & (df_v6b["tier"]=="A")].dropna(subset=["profit_3M"])
    sub_v8 = df_v8c[(df_v8c["subsector"]==sub) & (df_v8c["tier"]=="A")].dropna(subset=["profit_3M"])
    if len(sub_v6) < 3 and len(sub_v8) < 3:
        continue
    def stats(s):
        if len(s) == 0: return (0, np.nan, np.nan)
        return (len(s), s["profit_3M"].median(), (s["profit_3M"]>0).mean()*100)
    n6,m6,w6 = stats(sub_v6); n8,m8,w8 = stats(sub_v8)
    print(f"  {sub:<16}  N={n6:3d} med={m6 if not np.isnan(m6) else 0:+5.2f}% WR={w6 if not np.isnan(w6) else 0:5.1f}%  "
          f"N={n8:3d} med={m8 if not np.isnan(m8) else 0:+5.2f}% WR={w8 if not np.isnan(w8) else 0:5.1f}%"
          f"  {(m8-m6) if not (np.isnan(m8) or np.isnan(m6)) else 0:+6.2f}"
          f" {(w8-w6) if not (np.isnan(w8) or np.isnan(w6)) else 0:+6.1f}")

# v8c per-sub-sector tier ordering
print("\n" + "="*80); print("v8c WITHIN-SUB-SECTOR tier ordering (profit_3M)"); print("="*80)
for sub in all_subs:
    s = df_v8c[df_v8c["subsector"]==sub]
    if len(s) < 30: continue
    print(f"\n  --- {sub} (N={len(s)}) ---")
    for tier in ["A","B","C","D","E"]:
        g = s[s["tier"]==tier].dropna(subset=["profit_3M"])["profit_3M"]
        if len(g):
            print(f"    {tier}  N={len(g):4d}  med={g.median():+6.2f}%  WR={(g>0).mean()*100:.1f}%")

# Composite IC at each horizon
print("\n" + "="*80); print("COMPOSITE IC at each horizon"); print("="*80)
print(f"\n{'Horizon':<12}{'v6b global':>14}{'v8c sub':>14}{'Δ':>10}")
for h in ["profit_3M","O6M","O1Y","O2Y"]:
    s6 = df_v6b.dropna(subset=[h])
    s8 = df_v8c.dropna(subset=[h])
    ic6, _ = spearman_ic(s6["v6b_score"], s6[h])
    ic8, _ = spearman_ic(s8["v8c_score"], s8[h])
    print(f"{h:<12}{ic6:>+14.4f}{ic8:>+14.4f}{ic8-ic6:>+10.4f}")

print("\n" + "="*80); print("DONE"); print("="*80)
