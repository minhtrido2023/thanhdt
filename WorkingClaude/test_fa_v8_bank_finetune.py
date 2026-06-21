#!/usr/bin/env python3
"""
test_fa_v8_bank_finetune.py
============================
Fix non-monotonic A tier in v8 BANK schema (B beats A).

Diagnosis:
  v8 BANK A: median +3.58%, WR 64%
  v8 BANK B: median +9.91%, WR 67%  ← anomaly: B outperforms A

Hypotheses:
  H1. Big-bank effect: state-owned banks (CTG/BID/VCB) score highest but
      move slowly → A tier dominated by "stable boring" banks
  H2. Schema overweights stability/quality → biases mature banks
  H3. Top-10% threshold too narrow for 206-obs sample → noise

Tests:
  Var-A: Investigate WHICH banks in A vs B (sanity)
  Var-B: Multiple bank schema variations
  Var-C: Different tier thresholds (top 5%, 15%, 20%)
  Var-D: Size adjustment (penalize big banks; OR concentrate on smaller)
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

# Just banks for diagnostic (faster query)
SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE5Y, f.ROE_Trailing,
    f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.DY, f.Dividend_Min3Y, f.Dividend_3Y,
    f.PE, f.PB, f.PCF, f.OShares,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
    f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7,
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
    AND t.ICB_Code = 8355  -- Banks only
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching banks-only data ..."); df = bq_query(SQL); print(f"  {len(df):,} bank rows")

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

df["NP_4Q_mean"]=df[[f"NP_P{i}" for i in range(4)]].mean(axis=1,skipna=True)
df["MktCap"]=df["Close"]*df["OShares"]
df["smoothed_EY"]=(df["NP_4Q_mean"]/df["OShares"].replace(0,np.nan)/df["Close"].replace(0,np.nan)).clip(-1,1)
df["EY"]=np.where(df["PE"]>0,1.0/df["PE"],np.nan)
df["BY"]=np.where(df["PB"]>0,1.0/df["PB"],np.nan)
df["NP_R_inv_bank"] = -df["NP_R"]
df["MktCap_inv"]    = -df["MktCap"]    # smaller cap = higher rank

# TTM NP growth
ttm_now = df[[f"NP_P{i}" for i in range(4)]].sum(axis=1, skipna=False)
ttm_prv = df[[f"NP_P{i}" for i in range(4,8)]].sum(axis=1, skipna=False)
df["NP_TTM_growth"] = np.where(ttm_prv.abs()>0,(ttm_now-ttm_prv)/ttm_prv.abs(),np.nan).clip(-5,5)
df["NP_TTM_growth_inv"] = -df["NP_TTM_growth"]

ALL_INDS = ["ROIC5Y","ROE_Min5Y","ROE5Y","ROE_Trailing","NP_R","NP_R_inv_bank",
            "GPM_change","NP_CV","Rev_CV","DY_adj","Dividend_Min3Y","Dividend_3Y","DY_sust",
            "smoothed_EY","EY","BY","NP_TTM_growth","NP_TTM_growth_inv","NP_peak_ratio","MktCap_inv"]
for c in ALL_INDS:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
df["r_magic_pb"] = df.groupby("quarter").apply(
    lambda g: (g[["r_ROE_Min5Y","r_BY"]].mean(axis=1, skipna=True))
).reset_index(level=0, drop=True)

# ─── BANK schema variations ───────────────────────────────────────────────
# Each is dict: {axis_name: ([list of indicator cols], weight)}
def s_v8_orig():  # Current v8 bank schema
    return {
        "quality":     (["ROE_Min5Y","ROE5Y","ROE_Trailing"], 0.30),
        "stability":   (["NP_CV","Rev_CV"], 0.20),
        "shareholder": (["DY_adj","Dividend_Min3Y","DY_sust","Dividend_3Y"], 0.18),
        "growth":      (["NP_R_inv_bank","GPM_change","NP_peak_ratio"], 0.07),
        "valuation":   (["smoothed_EY","r_magic_pb"], 0.25),
    }
def s_var1_lessQ_moreG():  # Reduce quality (stable), boost growth
    return {
        "quality":     (["ROE_Min5Y","ROE_Trailing"], 0.22),
        "stability":   (["NP_CV"], 0.13),                       # only NP_CV
        "shareholder": (["DY_adj","Dividend_Min3Y"], 0.15),
        "growth":      (["NP_R","NP_peak_ratio"], 0.20),        # POSITIVE NP_R (not inverted)
        "valuation":   (["smoothed_EY","r_magic_pb"], 0.30),
    }
def s_var2_size_penalty():  # Penalize big banks
    return {
        "quality":     (["ROE_Min5Y","ROE_Trailing"], 0.25),
        "stability":   (["NP_CV","Rev_CV"], 0.15),
        "shareholder": (["DY_adj","Dividend_Min3Y","DY_sust"], 0.15),
        "growth":      (["NP_R","NP_peak_ratio"], 0.10),
        "valuation":   (["smoothed_EY","r_magic_pb","MktCap_inv"], 0.35),  # small cap bonus
    }
def s_var3_simple():  # Simpler: just ROE + value
    return {
        "quality":     (["ROE_Min5Y","ROE_Trailing"], 0.40),
        "shareholder": (["DY_adj","Dividend_Min3Y"], 0.20),
        "valuation":   (["smoothed_EY","BY"], 0.40),
    }
def s_var4_pure_value():  # Pure value (no quality)
    return {
        "valuation":   (["smoothed_EY","BY","r_magic_pb"], 0.55),
        "shareholder": (["DY_adj","Dividend_Min3Y"], 0.25),
        "growth":      (["NP_peak_ratio"], 0.20),
    }
def s_var5_growth_focused():  # Try positive growth
    return {
        "quality":     (["ROE_Min5Y","ROE_Trailing"], 0.20),
        "stability":   (["NP_CV"], 0.10),
        "shareholder": (["DY_adj","Dividend_Min3Y"], 0.10),
        "growth":      (["NP_R","NP_TTM_growth","NP_peak_ratio"], 0.35),  # heavy positive growth
        "valuation":   (["smoothed_EY","BY"], 0.25),
    }
def s_var6_balanced():  # Balanced 5-axis with right NP_R direction
    return {
        "quality":     (["ROE_Min5Y","ROE_Trailing"], 0.25),
        "stability":   (["NP_CV"], 0.10),
        "shareholder": (["DY_adj","Dividend_Min3Y"], 0.15),
        "growth":      (["NP_R","GPM_change","NP_peak_ratio"], 0.20),  # POSITIVE NP_R
        "valuation":   (["smoothed_EY","BY","r_magic_pb"], 0.30),
    }

SCHEMAS = {
    "orig (v8)":            s_v8_orig(),
    "var1 lessQ+G":         s_var1_lessQ_moreG(),
    "var2 size-penalty":    s_var2_size_penalty(),
    "var3 simple Q+V":      s_var3_simple(),
    "var4 pure value":      s_var4_pure_value(),
    "var5 growth-focused":  s_var5_growth_focused(),
    "var6 balanced (+NP_R)":s_var6_balanced(),
}

def score_with_schema(schema):
    weights_sum = sum(w for _, w in schema.values())
    total = np.zeros(len(df))
    nan_mask = np.zeros(len(df), dtype=bool)
    for axis, (cols, w) in schema.items():
        # Each col may already have r_ prefix (r_magic_pb)
        rank_cols = []
        for c in cols:
            if c.startswith("r_") or c == "r_magic_pb":
                rank_cols.append(c)
            else:
                rank_cols.append(f"r_{c}")
        axis_score = df[rank_cols].mean(axis=1, skipna=True).values
        nan_mask |= np.isnan(axis_score)
        total += np.nan_to_num(axis_score, nan=0.0) * w
    score = np.where(nan_mask, np.nan, total / weights_sum)
    return score

# Tier within quarter (banks-only universe)
def assign_tier_at(df_local, score_col, qcut_thresholds):
    """qcut_thresholds: list of (tier_name, lower, upper) tuples."""
    df_local = df_local.dropna(subset=[score_col]).copy()
    df_local["pct"] = df_local.groupby("quarter")[score_col].rank(pct=True)
    def t_of(p):
        for n, lo, hi in qcut_thresholds:
            if lo <= p <= hi: return n
        return "E"
    df_local["tier"] = df_local["pct"].apply(t_of)
    return df_local

T_STD  = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]
T_TIGHT = [("A",0.95,1.00),("B",0.80,0.95),("C",0.50,0.80),("D",0.20,0.50),("E",0.00,0.20)]
T_LOOSE = [("A",0.80,1.00),("B",0.60,0.80),("C",0.40,0.60),("D",0.20,0.40),("E",0.00,0.20)]

def report_schema(label, schema, thresholds=T_STD):
    df["s"] = score_with_schema(schema)
    t = assign_tier_at(df, "s", thresholds)
    v = t.dropna(subset=["profit_3M"])
    rows = []
    for tier in ["A","B","C","D","E"]:
        g = v[v["tier"]==tier]["profit_3M"]
        if len(g):
            rows.append({"tier":tier,"N":len(g),"median":g.median(),
                         "mean":g.mean(),"WR":(g>0).mean()*100})
    out = pd.DataFrame(rows)
    meds = out["median"].values
    spread = meds[0]-meds[-1] if len(meds)==5 else np.nan
    inv = sum(1 for i in range(len(meds)-1) if meds[i]<meds[i+1])
    ic, _ = spearman_ic(t["s"], t["profit_3M"])
    a_med = out[out.tier=="A"]["median"].iloc[0] if (out.tier=="A").any() else np.nan
    a_wr = out[out.tier=="A"]["WR"].iloc[0] if (out.tier=="A").any() else np.nan
    a_n = int(out[out.tier=="A"]["N"].iloc[0]) if (out.tier=="A").any() else 0
    monoflag = "✓" if inv == 0 else f"⚠inv={inv}"
    print(f"  {label:<28}  A={a_n:2d}|{a_med:+5.2f}%/WR{a_wr:.0f}%   spread={spread:+5.2f}  IC={ic:+.3f}  {monoflag}")
    return out, ic, spread

# ─── 1. Diagnose: list banks in v8 A vs B ─────────────────────────────────
print("\n" + "="*80); print("DIAGNOSIS: which banks land in A vs B with orig schema?"); print("="*80)
df["s_orig"] = score_with_schema(s_v8_orig())
t_orig = assign_tier_at(df, "s_orig", T_STD)
print("\nA tier banks (sorted by score, top 10):")
A = t_orig[t_orig["tier"]=="A"].sort_values("s_orig", ascending=False)
print(A[["ticker","quarter","profit_3M","s_orig","ROE_Min5Y","NP_R","PE","PB","DY"]].head(10).to_string(index=False))
print(f"\nB tier banks (top 10):")
B = t_orig[t_orig["tier"]=="B"].sort_values("s_orig", ascending=False)
print(B[["ticker","quarter","profit_3M","s_orig","ROE_Min5Y","NP_R","PE","PB","DY"]].head(10).to_string(index=False))

# A vs B comparison: tickers
A_tickers = set(A["ticker"])
B_tickers = set(B["ticker"])
print(f"\nA tier tickers ({len(A_tickers)} unique): {sorted(A_tickers)}")
print(f"B tier tickers ({len(B_tickers)} unique): {sorted(B_tickers)}")
common = A_tickers & B_tickers
print(f"Tickers in BOTH A and B (different quarters): {sorted(common)}")
only_A = A_tickers - B_tickers
only_B = B_tickers - A_tickers
print(f"Only-A: {sorted(only_A)}")
print(f"Only-B: {sorted(only_B)}")

# MktCap comparison
print(f"\nMktCap distribution (median):")
print(f"  A: {A['MktCap'].median()/1e9:.0f}B VND  (mean liq: {A['liquidity'].median()/1e9:.1f}B)")
print(f"  B: {B['MktCap'].median()/1e9:.0f}B VND  (mean liq: {B['liquidity'].median()/1e9:.1f}B)")

# ─── 2. Test all schema variations ─────────────────────────────────────────
print("\n" + "="*80); print("SCHEMA VARIATIONS (standard tier thresholds 10/30/60/85)"); print("="*80)
results = {}
for label, schema in SCHEMAS.items():
    out, ic, spread = report_schema(label, schema, T_STD)
    results[label] = (out, ic, spread)

# ─── 3. Best 2-3 schemas with different thresholds ─────────────────────────
print("\n" + "="*80); print("SAME SCHEMAS with LOOSER thresholds (top 20% A)"); print("="*80)
for label, schema in SCHEMAS.items():
    out, ic, spread = report_schema(label, schema, T_LOOSE)

print("\n" + "="*80); print("SAME SCHEMAS with TIGHTER thresholds (top 5% A)"); print("="*80)
for label, schema in SCHEMAS.items():
    out, ic, spread = report_schema(label, schema, T_TIGHT)

# ─── 4. Best combination summary ───────────────────────────────────────────
print("\n" + "="*80); print("SUMMARY — best schema for banks"); print("="*80)
print("Looking for: monotonic ordering + high A median + high IC")
print(f"\n  Original v8 BANK: A med +3.58%, B med +9.91% (NON-MONO)")
print(f"  Goal: A median > B, mono ordering, IC >= +0.10")

print("\n" + "="*80); print("DONE"); print("="*80)
