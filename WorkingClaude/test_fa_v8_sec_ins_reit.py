#!/usr/bin/env python3
"""
test_fa_v8_sec_ins_reit.py
==========================
Apply bank-finetune lessons to SECURITIES, INSURANCE, REIT sectors.

Lessons from BANK finetune (var3 winner):
  - Simple Q + V structure (Quality 40% + Shareholder 20% + Valuation 40%)
  - Pure value (var4) good for IC, but with inversions
  - Don't blindly invert IC sign — confounder issue (CTG-effect)
  - Growth + Value combo (var5) gives best WR at top 5%

Test for each sector:
  orig (v8)               - current v8 schema
  v3 simple Q+V           - bank-winner pattern
  v4 pure value           - highest IC pattern
  v5 growth-focused       - highest top-5% WR pattern
  v6 balanced             - Q+V+G mix
  custom per-sector       - tuned to sector specifics

Sectors:
  SECURITIES (ICB 8775, 8777) — 253 obs
  INSURANCE  (ICB 8536)       — 28 obs (limited)
  REIT       (ICB 8633, 8637) — 588 obs (largest)
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

SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE5Y, f.ROE_Trailing,
    f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y, f.Dividend_3Y, f.Dividend_1Y,
    f.PE, f.PB, f.PCF, f.EVEB, f.OShares,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
    f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3,
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
    AND t.ICB_Code IN (8775, 8777, 8536, 8633, 8637)  -- SEC, INS, REIT only
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching SEC+INS+REIT data ..."); df = bq_query(SQL); print(f"  {len(df):,} rows")

def sector_bucket(icb):
    code = int(float(icb))
    if code in (8775, 8777): return "SECURITIES"
    if code == 8536: return "INSURANCE"
    if code in (8633, 8637): return "REIT"
    return "?"
df["sector"] = df["ICB_Code"].apply(sector_bucket)
print(df["sector"].value_counts().to_string())

# Build indicators (same as bank script)
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
df["FCF_4Q"]=(df["CF_OA_P0"]+df["CF_OA_P1"]+df["CF_OA_P2"]+df["CF_OA_P3"]
            +df["CF_Invest_P0"]+df["CF_Invest_P1"]+df["CF_Invest_P2"]+df["CF_Invest_P3"])
df["FCF_yield"]=(df["FCF_4Q"]/df["MktCap"]).clip(-1,1)
ttm_now = df[[f"NP_P{i}" for i in range(4)]].sum(axis=1, skipna=False)
ttm_prv = df[[f"NP_P{i}" for i in range(4,8)]].sum(axis=1, skipna=False)
df["NP_TTM_growth"] = np.where(ttm_prv.abs()>0,(ttm_now-ttm_prv)/ttm_prv.abs(),np.nan).clip(-5,5)

# Within-sector ranks (each sector ranked separately)
ALL_INDS = ["ROIC5Y","ROE_Min5Y","ROE5Y","ROE_Trailing","NP_R","GPM_change","CF_OA_5Y","CFOA_NP",
            "NP_CV","Rev_CV","LT_CAGR","DY_adj","Dividend_Min3Y","Dividend_3Y","DY_sust",
            "smoothed_EY","EY","BY","FCF_yield","NP_TTM_growth","NP_peak_ratio","Rev_peak_ratio"]
for c in ALL_INDS:
    df[f"r_{c}"] = df.groupby(["quarter","sector"])[c].rank(pct=True, na_option="keep")
# Magic formula (sector-internal)
df["r_magic_pb"] = (df["r_ROE_Min5Y"] + df["r_BY"]) / 2.0
df["r_magic_pe"] = (df["r_ROIC5Y"] + df["r_EY"]) / 2.0

TIERS_STD = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]
def tier_of(p, tiers=TIERS_STD):
    for n,lo,hi in tiers:
        if lo<=p<=hi: return n
    return "E"

# Schema variations (axis_name → (rank_col_list, weight))
def s_orig_sec():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.22),
        "stability":   (["r_NP_CV"], 0.20),
        "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.15),
        "growth":      (["r_NP_peak_ratio","r_GPM_change"], 0.10),
        "valuation":   (["r_smoothed_EY","r_FCF_yield","r_magic_pb"], 0.33),
    }
def s_orig_ins():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y","r_ROE_Trailing"], 0.25),
        "stability":   (["r_NP_CV","r_Rev_CV"], 0.20),
        "shareholder": (["r_DY_adj","r_Dividend_Min3Y","r_DY_sust","r_Dividend_3Y"], 0.25),
        "growth":      (["r_NP_peak_ratio","r_Rev_peak_ratio"], 0.15),
        "valuation":   (["r_smoothed_EY"], 0.15),
    }
def s_orig_reit():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.18),
        "stability":   (["r_LT_CAGR"], 0.10),
        "cash":        (["r_CF_OA_5Y"], 0.12),
        "shareholder": (["r_DY_adj","r_Dividend_Min3Y","r_DY_sust"], 0.20),
        "growth":      (["r_NP_peak_ratio"], 0.10),
        "valuation":   (["r_smoothed_EY","r_magic_pb"], 0.30),
    }

# Generic variation templates (from bank lessons)
def make_var3_simple_QV():  # 40/20/40
    return {
        "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.40),
        "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.20),
        "valuation":   (["r_smoothed_EY","r_BY"], 0.40),
    }
def make_var4_pure_value():
    return {
        "valuation":   (["r_smoothed_EY","r_BY","r_magic_pb"], 0.55),
        "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.25),
        "growth":      (["r_NP_peak_ratio"], 0.20),
    }
def make_var5_growth_focused():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.20),
        "stability":   (["r_NP_CV"], 0.10),
        "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.10),
        "growth":      (["r_NP_R","r_NP_TTM_growth","r_NP_peak_ratio"], 0.35),
        "valuation":   (["r_smoothed_EY","r_BY"], 0.25),
    }
def make_var6_balanced():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.25),
        "stability":   (["r_NP_CV"], 0.10),
        "shareholder": (["r_DY_adj","r_Dividend_Min3Y"], 0.15),
        "growth":      (["r_NP_R","r_GPM_change","r_NP_peak_ratio"], 0.20),
        "valuation":   (["r_smoothed_EY","r_BY","r_magic_pb"], 0.30),
    }
# Reit-specific custom: FCF + LT_CAGR matter for REIT (rental cash flow)
def make_reit_custom():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.20),
        "cash":        (["r_CF_OA_5Y","r_FCF_yield"], 0.20),
        "shareholder": (["r_DY_adj","r_Dividend_Min3Y","r_DY_sust"], 0.20),
        "valuation":   (["r_smoothed_EY","r_BY","r_magic_pb"], 0.40),
    }
# Sec-specific: FCF very strong for SEC (from earlier IC)
def make_sec_fcf_heavy():
    return {
        "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.20),
        "stability":   (["r_NP_CV"], 0.10),
        "valuation":   (["r_smoothed_EY","r_BY","r_FCF_yield"], 0.45),  # FCF heavy
        "shareholder": (["r_DY_adj"], 0.10),
        "growth":      (["r_NP_peak_ratio"], 0.15),
    }

SECTOR_VARIANTS = {
    "SECURITIES": [
        ("orig (v8)",       s_orig_sec()),
        ("var3 simple Q+V", make_var3_simple_QV()),
        ("var4 pure value", make_var4_pure_value()),
        ("var5 growth",     make_var5_growth_focused()),
        ("var6 balanced",   make_var6_balanced()),
        ("sec_custom FCF",  make_sec_fcf_heavy()),
    ],
    "INSURANCE": [
        ("orig (v8)",       s_orig_ins()),
        ("var3 simple Q+V", make_var3_simple_QV()),
        ("var4 pure value", make_var4_pure_value()),
        ("var5 growth",     make_var5_growth_focused()),
        ("var6 balanced",   make_var6_balanced()),
    ],
    "REIT": [
        ("orig (v8)",       s_orig_reit()),
        ("var3 simple Q+V", make_var3_simple_QV()),
        ("var4 pure value", make_var4_pure_value()),
        ("var5 growth",     make_var5_growth_focused()),
        ("var6 balanced",   make_var6_balanced()),
        ("reit_custom",     make_reit_custom()),
    ],
}

def score_with_schema(df_local, schema):
    weights_sum = sum(w for _, w in schema.values())
    total = np.zeros(len(df_local))
    nan_mask = np.zeros(len(df_local), dtype=bool)
    for axis, (rank_cols, w) in schema.items():
        axis_score = df_local[rank_cols].mean(axis=1, skipna=True).values
        nan_mask |= np.isnan(axis_score)
        total += np.nan_to_num(axis_score, nan=0.0) * w
    return np.where(nan_mask, np.nan, total / weights_sum)

def report_for_sector(sector_name, variants):
    sub = df[df["sector"]==sector_name].copy()
    print(f"\n{'='*80}")
    print(f"SECTOR: {sector_name}  (N={len(sub)})")
    print('='*80)
    if len(sub) < 50:
        print(f"  WARNING: too few obs to optimize ({len(sub)} rows)")
    print(f"\n{'Schema':<28}{'A_n':>4}{'A_med':>10}{'A_WR':>8}{'spread':>9}{'IC':>9}{'mono':>7}")
    for label, schema in variants:
        sub["s"] = score_with_schema(sub, schema)
        ss = sub.dropna(subset=["s"]).copy()
        ss["pct"] = ss.groupby("quarter")["s"].rank(pct=True)
        ss["tier"] = ss["pct"].apply(tier_of)
        v = ss.dropna(subset=["profit_3M"])
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
        ic, _ = spearman_ic(ss["s"], ss["profit_3M"])
        a_med = out[out.tier=="A"]["median"].iloc[0] if (out.tier=="A").any() else np.nan
        a_wr = out[out.tier=="A"]["WR"].iloc[0] if (out.tier=="A").any() else np.nan
        a_n = int(out[out.tier=="A"]["N"].iloc[0]) if (out.tier=="A").any() else 0
        mono = "✓" if inv == 0 else f"⚠{inv}"
        print(f"{label:<28}{a_n:>4}{a_med:>+9.2f}%{a_wr:>+7.1f}%{spread:>+8.2f}{ic:>+8.3f}{mono:>6}")
    # Diagnose top tier composition for orig schema
    orig_schema = variants[0][1]
    sub["s_orig"] = score_with_schema(sub, orig_schema)
    so = sub.dropna(subset=["s_orig"]).copy()
    so["pct"] = so.groupby("quarter")["s_orig"].rank(pct=True)
    so["tier"] = so["pct"].apply(tier_of)
    A = so[so["tier"]=="A"].sort_values("s_orig", ascending=False).head(8)
    B = so[so["tier"]=="B"].sort_values("s_orig", ascending=False).head(8)
    print(f"\n  Top A tier picks (orig):")
    print(A[["ticker","quarter","profit_3M","s_orig","ROE_Min5Y","DY","PE","PB"]].to_string(index=False))
    print(f"\n  Top B tier picks (orig):")
    print(B[["ticker","quarter","profit_3M","s_orig","ROE_Min5Y","DY","PE","PB"]].to_string(index=False))

for sec_name, variants in SECTOR_VARIANTS.items():
    report_for_sector(sec_name, variants)

print("\n" + "="*80); print("DONE"); print("="*80)
