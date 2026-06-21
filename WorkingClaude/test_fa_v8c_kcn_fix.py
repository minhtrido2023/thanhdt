#!/usr/bin/env python3
"""
test_fa_v8c_kcn_fix.py
======================
Fix REIT_KCN "B beats A" syndrome.

Current KCN schema gives A tier -1.66% / WR 47% — A is WORST tier!
  C 25 +7.78% (best, middle tier)
  B 13 +6.30%
  D 21 +2.33%
  A 15 -1.66%
  E  5 -7.73%

Hypothesis: top-decile KCN = peak-cycle (high NP_R, high cash buildup) →
mean revert. Growth/cash signals are CONTRARIAN at extremes for KCN.

Test variants:
  orig          - v8c current (growth-cash heavy)
  v1 less_growth - reduce growth weight, boost valuation
  v2 ttm_only   - replace NP_R with TTM growth (less peak-prone)
  v3 pure_QV    - drop growth entirely, pure value+quality
  v4 anti_peak  - INVERT NP_peak_ratio (low peak = early cycle = buy)
  v5 BY_heavy   - emphasize PB (industrial parks have land value)
  v6 default    - fallback to v6b universal
  v7 stability  - boost stability, reduce growth
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

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(f"stdout={r.stdout[:500]} | stderr={r.stderr[:500]}")
    return pd.read_csv(StringIO(r.stdout.strip()))

def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 30: return float("nan"), 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

# Pull KCN tickers only
ticker_filter = ",".join([f'"{t}"' for t in sorted(KCN_TICKERS)])
SQL = f"""
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE_Trailing, f.FSCORE,
    f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y,
    f.Debt_Eq_P0, f.IntCov_P0,
    f.PE, f.PB, f.PCF, f.OShares,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0,f.Revenue_P1,f.Revenue_P4,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3,
    f.StDebt_P0, f.LtDebt_P0, f.Cash_P0, f.EBITDA_P0,
    CASE WHEN GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0, GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    t.Close, t.ICB_Code, t.profit_3M,
    t.Volume_3M_P50 * t.Close AS liquidity,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2014-01-01" AND f.quarter LIKE "%Q4"
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
    AND t.ticker IN ({ticker_filter})
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""
print("Fetching KCN-only data ..."); df = bq_query(SQL); print(f"  {len(df):,} KCN rows")
print(f"  Tickers: {sorted(df['ticker'].unique())}")

# Build indicators
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"]*_mult
np_arr = df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
np_n = np.sum(~np.isnan(np_arr),axis=1)
with np.errstate(divide="ignore",invalid="ignore"):
    np_m=np.nanmean(np_arr,axis=1); np_s=np.nanstd(np_arr,axis=1,ddof=1)
    df["NP_CV"]=-np.where(np_n>=6,np_s/np.maximum(np.abs(np_m),1e6),np.nan).clip(max=10)
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
df["NetDebt"]=df["StDebt_P0"].fillna(0)+df["LtDebt_P0"].fillna(0)-df["Cash_P0"].fillna(0)
df["NetDebt_EBITDA_inv"]=-np.where(df["EBITDA_P0"]>0,df["NetDebt"]/df["EBITDA_P0"],np.nan).clip(-20,50)
# Anti-peak: invert NP_peak_ratio (low = early cycle = buy)
df["NP_peak_inv"] = -df["NP_peak_ratio"]
df["MktCap_inv"] = -df["MktCap"]

# Within-KCN ranks
RANK_INDS = ["ROIC5Y","ROE_Min5Y","ROE_Trailing","FSCORE","NP_R","NP_TTM_growth","NP_peak_ratio","NP_peak_inv",
             "GPM_change","NP_CV","CF_OA_5Y","CFOA_NP","FCF_yield","Cash_MktCap","NetDebt_EBITDA_inv",
             "DY_adj","Dividend_Min3Y","Debt_Eq_P0","smoothed_EY","EY","BY","CFY","MktCap_inv"]
for c in RANK_INDS:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
df["r_magic_pb"] = (df["r_ROE_Min5Y"] + df["r_BY"]) / 2.0

# ─── Schema variants ──────────────────────────────────────────────────────
def s_orig():
    return {
        "growth":      (["r_NP_R","r_NP_TTM_growth","r_NP_peak_ratio"], 0.30),
        "cash":        (["r_Cash_MktCap","r_FCF_yield","r_CF_OA_5Y"], 0.25),
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
        "valuation":   (["r_smoothed_EY","r_BY"], 0.15),
        "shareholder": (["r_DY_adj"], 0.10),
    }
def s_v1_less_growth():
    return {
        "growth":      (["r_NP_TTM_growth","r_NP_peak_ratio"], 0.15),  # less + drop NP_R
        "cash":        (["r_Cash_MktCap","r_FCF_yield","r_CF_OA_5Y"], 0.25),
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
        "valuation":   (["r_smoothed_EY","r_BY","r_magic_pb"], 0.30),  # boost
        "shareholder": (["r_DY_adj"], 0.10),
    }
def s_v2_ttm_only():
    return {
        "growth":      (["r_NP_TTM_growth"], 0.15),
        "cash":        (["r_Cash_MktCap","r_CF_OA_5Y"], 0.30),
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
        "valuation":   (["r_smoothed_EY","r_BY"], 0.25),
        "shareholder": (["r_DY_adj"], 0.10),
    }
def s_v3_pure_QV():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.35),
        "valuation":   (["r_smoothed_EY","r_BY","r_magic_pb"], 0.40),
        "cash":        (["r_CF_OA_5Y"], 0.15),
        "shareholder": (["r_DY_adj"], 0.10),
    }
def s_v4_anti_peak():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.25),
        "cash":        (["r_Cash_MktCap","r_FCF_yield"], 0.20),
        "valuation":   (["r_smoothed_EY","r_BY"], 0.25),
        "growth":      (["r_NP_R","r_NP_peak_inv"], 0.20),  # REWARD low peak ratio (early cycle)
        "shareholder": (["r_DY_adj"], 0.10),
    }
def s_v5_BY_heavy():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
        "valuation":   (["r_BY","r_BY","r_smoothed_EY","r_magic_pb"], 0.40),  # double-weight BY
        "cash":        (["r_CF_OA_5Y","r_Cash_MktCap"], 0.20),
        "shareholder": (["r_DY_adj"], 0.10),
        "growth":      (["r_NP_peak_inv"], 0.10),
    }
def s_v6_default_like():
    # v6b-style 7-axis universal but within-KCN
    return {
        "quality":     (["r_ROIC5Y","r_ROE_Min5Y"], 0.18),
        "stability":   (["r_NP_CV"], 0.18),
        "cash":        (["r_CF_OA_5Y","r_CFOA_NP"], 0.18),
        "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.15),
        "growth":      (["r_GPM_change","r_NP_peak_ratio"], 0.13),
        "health":      (["r_Cash_MktCap","r_NetDebt_EBITDA_inv"], 0.08),
        "valuation":   (["r_smoothed_EY","r_FCF_yield"], 0.10),
    }
def s_v7_stability_heavy():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.25),
        "stability":   (["r_NP_CV"], 0.20),
        "cash":        (["r_CF_OA_5Y","r_Cash_MktCap"], 0.15),
        "valuation":   (["r_smoothed_EY","r_BY"], 0.25),
        "shareholder": (["r_DY_adj"], 0.10),
        "growth":      (["r_NP_peak_inv"], 0.05),  # tiny anti-peak
    }
def s_v8_smallcap_value():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
        "valuation":   (["r_smoothed_EY","r_BY","r_MktCap_inv"], 0.40),  # small cap bonus
        "cash":        (["r_CF_OA_5Y","r_Cash_MktCap"], 0.20),
        "shareholder": (["r_DY_adj"], 0.10),
        "growth":      (["r_NP_peak_inv"], 0.10),
    }

VARIANTS = {
    "orig (broken)":      s_orig(),
    "v1 less_growth":     s_v1_less_growth(),
    "v2 ttm_only":        s_v2_ttm_only(),
    "v3 pure QV":         s_v3_pure_QV(),
    "v4 anti_peak":       s_v4_anti_peak(),
    "v5 BY_heavy":        s_v5_BY_heavy(),
    "v6 default-like":    s_v6_default_like(),
    "v7 stability_heavy": s_v7_stability_heavy(),
    "v8 smallcap_value":  s_v8_smallcap_value(),
}

def score(df_local, schema):
    weights_sum = sum(w for _, w in schema.values())
    total = np.zeros(len(df_local))
    nan_mask = np.zeros(len(df_local), dtype=bool)
    for axis, (rank_cols, w) in schema.items():
        axis_score = df_local[rank_cols].mean(axis=1, skipna=True).values
        nan_mask |= np.isnan(axis_score)
        total += np.nan_to_num(axis_score, nan=0.0) * w
    return np.where(nan_mask, np.nan, total / weights_sum)

def tier_of(p):
    for n,lo,hi in TIERS:
        if lo<=p<=hi: return n
    return "E"

print("\n" + "="*90); print("KCN SCHEMA VARIANTS (within-KCN ranking, profit_3M)"); print("="*90)
print(f"\n{'Schema':<25}{'A_n':>4}{'A_med':>10}{'A_WR':>8}{'spread':>9}{'IC':>9}{'mono':>7}")
print("-"*72)

results = {}
for label, sch in VARIANTS.items():
    df["s"] = score(df, sch)
    s = df.dropna(subset=["s"]).copy()
    s["pct"] = s.groupby("quarter")["s"].rank(pct=True)
    s["tier"] = s["pct"].apply(tier_of)
    v = s.dropna(subset=["profit_3M"])
    rows = []
    for tier in ["A","B","C","D","E"]:
        g = v[v["tier"]==tier]["profit_3M"]
        if len(g):
            rows.append({"tier":tier,"N":len(g),"median":g.median(),
                         "WR":(g>0).mean()*100})
    out = pd.DataFrame(rows)
    meds = out["median"].values
    spread = meds[0]-meds[-1] if len(meds)==5 else np.nan
    inv = sum(1 for i in range(len(meds)-1) if meds[i]<meds[i+1])
    ic, _ = spearman_ic(s["s"], s["profit_3M"])
    a_med = out[out.tier=="A"]["median"].iloc[0] if (out.tier=="A").any() else np.nan
    a_wr  = out[out.tier=="A"]["WR"].iloc[0] if (out.tier=="A").any() else np.nan
    a_n   = int(out[out.tier=="A"]["N"].iloc[0]) if (out.tier=="A").any() else 0
    mono  = "✓" if inv == 0 else f"⚠{inv}"
    print(f"{label:<25}{a_n:>4}{a_med:>+9.2f}%{a_wr:>+7.1f}%{spread:>+8.2f}{ic:>+8.3f}{mono:>6}")
    results[label] = (out, ic, spread)

# Detailed tier breakdown for best 3 variants
print("\n" + "="*80); print("DETAILED TIER ORDERING — top 3 schemas"); print("="*80)
ranked = sorted(results.items(), key=lambda x: (x[1][0][x[1][0]["tier"]=="A"]["median"].iloc[0]
                                                  if (x[1][0]["tier"]=="A").any() else -99),
                reverse=True)
for label, (out, ic, spread) in ranked[:4]:
    print(f"\n  {label}  (IC={ic:+.3f}, spread={spread:+.2f}):")
    print(out.to_string(index=False, float_format="%.2f"))

print("\n" + "="*80); print("DONE"); print("="*80)
