#!/usr/bin/env python3
"""
test_fa_kcn_with_advcust.py
============================
Fix REIT_KCN schema using new AdvCust_MktCap_yld indicator (IC +0.152).

Previous KCN issue (v8c):
  A 15  -1.66% / WR 47% ← A is WORST
  B 13  +6.30%
  C 25  +7.78% (best, middle)
  D 21  +2.33%
  E  5  -7.73%

New schema candidates with pre-sales:
  V1 Adv_value_heavy: AdvCust_MktCap_yld as primary value
  V2 Backlog_separate: Treat as own axis
  V3 TotalBacklog: Use combined AdvCust + UnearnRev
  V4 Anti-momentum: V1 + penalize AdvCust_accel
  V5 Stability_heavy + Adv: v8c_kcn_fix v7 best + AdvCust
  V6 Pure value composite: focus value indicators

Test on KCN universe (N~82-91), within-KCN ranking.
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
    if r.returncode != 0: raise RuntimeError(f"{r.stdout[:300]}|{r.stderr[:300]}")
    return pd.read_csv(StringIO(r.stdout.strip()))

def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 30: return float("nan"), 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

# Pull KCN-only
ticker_filter = ",".join([f'"{t}"' for t in sorted(KCN_TICKERS)])
SQL = f"""
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE_Trailing,
    f.NP_R, f.Revenue_P0, f.Revenue_P1,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, f.DY, f.Dividend_Min3Y,
    f.PE, f.PB, f.OShares,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.AdvCust_P0, f.AdvCust_P1, f.AdvCust_P2, f.AdvCust_P3,
    f.AdvCust_P4, f.AdvCust_P5, f.AdvCust_P6, f.AdvCust_P7,
    f.UnearnRev_P0, f.UnearnRev_P1, f.UnearnRev_P2, f.UnearnRev_P3,
    f.UnearnRev_P4, f.UnearnRev_P5, f.UnearnRev_P6, f.UnearnRev_P7,
    f.Inventory_P0, f.Inventory_P4,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.Cash_P0, f.StDebt_P0, f.LtDebt_P0,
    CASE WHEN GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0, GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    t.Close, t.ICB_Code, t.profit_3M,
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
df["MktCap"] = df["Close"] * df["OShares"]
df["NP_4Q_mean"] = df[[f"NP_P{i}" for i in range(4)]].mean(axis=1, skipna=True)
df["smoothed_EY"] = (df["NP_4Q_mean"] / df["OShares"].replace(0,np.nan) / df["Close"].replace(0,np.nan)).clip(-1,1)
df["EY"] = np.where(df["PE"]>0, 1.0/df["PE"], np.nan)
df["BY"] = np.where(df["PB"]>0, 1.0/df["PB"], np.nan)
df["FCF_4Q"] = df["CF_OA_P0"] + df["CF_OA_P1"] + df["CF_OA_P2"] + df["CF_OA_P3"]
df["FCF_yield"] = (df["FCF_4Q"] / df["MktCap"]).clip(-1, 1)
df["Cash_MktCap"] = np.where(df["MktCap"]>0, df["Cash_P0"]/df["MktCap"], np.nan).clip(-1,5)
ttm_now = df[[f"NP_P{i}" for i in range(4)]].sum(axis=1, skipna=False)
ttm_prv = df[[f"NP_P{i}" for i in range(4,8)]].sum(axis=1, skipna=False)
df["NP_TTM_growth"] = np.where(ttm_prv.abs()>0,(ttm_now-ttm_prv)/ttm_prv.abs(),np.nan).clip(-5,5)

# Pre-sales indicators
def safe_div(num, den):
    return np.where(np.abs(den) > 1e-3, num / den.replace(0, np.nan), np.nan)

df["AdvCust_MktCap_yld"] = safe_div(df["AdvCust_P0"], df["MktCap"]).clip(-1, 20)
df["TotalBacklog_P0"] = df["AdvCust_P0"].fillna(0) + df["UnearnRev_P0"].fillna(0)
df["TotalBacklog_MktCap_yld"] = safe_div(df["TotalBacklog_P0"], df["MktCap"]).clip(-1, 20)
df["AdvCust_YoY"] = safe_div(df["AdvCust_P0"] - df["AdvCust_P4"], df["AdvCust_P4"].abs()).clip(-5, 20)
df["AdvCust_QoQ"] = safe_div(df["AdvCust_P0"] - df["AdvCust_P1"], df["AdvCust_P1"].abs()).clip(-5, 20)
df["AdvCust_QoQ_prev"] = safe_div(df["AdvCust_P1"] - df["AdvCust_P2"], df["AdvCust_P2"].abs()).clip(-5, 20)
df["AdvCust_accel"] = df["AdvCust_QoQ"] - df["AdvCust_QoQ_prev"]
df["AdvCust_accel_inv"] = -df["AdvCust_accel"]
df["AdvCust_Rev_cover"] = safe_div(df["AdvCust_P0"], df["Revenue_P0"].abs()).clip(-1, 50)

# NP_peak inv (anti-peak)
df["NP_peak_inv"] = -df["NP_peak_ratio"]

# Stability
np_arr = df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
np_n = np.sum(~np.isnan(np_arr),axis=1)
with np.errstate(divide="ignore",invalid="ignore"):
    np_m = np.nanmean(np_arr,axis=1); np_s = np.nanstd(np_arr,axis=1,ddof=1)
    df["NP_CV"] = -np.where(np_n>=6, np_s/np.maximum(np.abs(np_m),1e6), np.nan).clip(max=10)

# Net debt
df["NetDebt"] = df["StDebt_P0"].fillna(0)+df["LtDebt_P0"].fillna(0)-df["Cash_P0"].fillna(0)

RANK_COLS = ["ROIC5Y","ROE_Min5Y","ROE_Trailing","NP_R","NP_TTM_growth","NP_peak_ratio","NP_peak_inv",
             "GPM_change","NP_CV","CF_OA_5Y","Cash_MktCap","DY","Dividend_Min3Y",
             "smoothed_EY","EY","BY","FCF_yield",
             "AdvCust_MktCap_yld","TotalBacklog_MktCap_yld","AdvCust_YoY","AdvCust_QoQ",
             "AdvCust_accel","AdvCust_accel_inv","AdvCust_Rev_cover"]
for c in RANK_COLS:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
df["r_magic_pb"] = (df["r_ROE_Min5Y"] + df["r_BY"]) / 2.0

# ─── Schema variants ──────────────────────────────────────────────────────
def s_v8c_orig():  # v8c_final REIT schema (KCN merged into REIT bucket)
    return {
        "quality":     (["r_ROE_Min5Y","r_ROE_Trailing"], 0.20),
        "cash":        (["r_CF_OA_5Y","r_FCF_yield"], 0.20),
        "shareholder": (["r_DY","r_Dividend_Min3Y"], 0.20),
        "valuation":   (["r_smoothed_EY","r_BY","r_magic_pb"], 0.40),
    }
def s_V1_Adv_value():  # AdvCust_MktCap_yld in valuation axis (heavy)
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
        "stability":   (["r_NP_CV"], 0.15),
        "shareholder": (["r_DY","r_Dividend_Min3Y"], 0.10),
        "valuation":   (["r_AdvCust_MktCap_yld","r_smoothed_EY","r_BY"], 0.45),
        "cash":        (["r_FCF_yield","r_Cash_MktCap"], 0.10),
    }
def s_V2_Backlog_separate():  # Backlog as separate axis
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
        "stability":   (["r_NP_CV"], 0.15),
        "shareholder": (["r_DY"], 0.10),
        "valuation":   (["r_smoothed_EY","r_BY"], 0.20),
        "backlog":     (["r_AdvCust_MktCap_yld"], 0.30),  # primary
        "cash":        (["r_FCF_yield"], 0.05),
    }
def s_V3_TotalBacklog():  # TotalBacklog (combined) primary
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
        "stability":   (["r_NP_CV"], 0.15),
        "shareholder": (["r_DY"], 0.10),
        "valuation":   (["r_smoothed_EY","r_BY"], 0.20),
        "backlog":     (["r_TotalBacklog_MktCap_yld"], 0.30),
        "cash":        (["r_FCF_yield"], 0.05),
    }
def s_V4_AntiMomentum():  # V1 + anti-acceleration
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
        "stability":   (["r_NP_CV"], 0.10),
        "shareholder": (["r_DY","r_Dividend_Min3Y"], 0.10),
        "valuation":   (["r_AdvCust_MktCap_yld","r_smoothed_EY","r_BY"], 0.40),
        "anti_mom":    (["r_AdvCust_accel_inv","r_NP_peak_inv"], 0.15),
        "cash":        (["r_FCF_yield"], 0.05),
    }
def s_V5_Stab_plus_Adv():  # v7 stability_heavy + AdvCust
    return {
        "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.22),
        "stability":   (["r_NP_CV"], 0.18),
        "valuation":   (["r_AdvCust_MktCap_yld","r_smoothed_EY","r_BY"], 0.35),
        "cash":        (["r_CF_OA_5Y","r_Cash_MktCap"], 0.10),
        "shareholder": (["r_DY"], 0.10),
        "growth":      (["r_NP_peak_inv"], 0.05),
    }
def s_V6_Pure_yield():  # Pure value composite (all yield-based)
    return {
        "valuation":   (["r_AdvCust_MktCap_yld","r_TotalBacklog_MktCap_yld","r_smoothed_EY","r_BY","r_FCF_yield"], 0.55),
        "quality":     (["r_ROE_Min5Y"], 0.20),
        "stability":   (["r_NP_CV"], 0.15),
        "shareholder": (["r_DY"], 0.10),
    }

SCHEMAS = {
    "v8c_orig (broken)":       s_v8c_orig(),
    "V1 Adv_value_heavy":      s_V1_Adv_value(),
    "V2 Backlog_separate":     s_V2_Backlog_separate(),
    "V3 TotalBacklog":         s_V3_TotalBacklog(),
    "V4 V1+AntiMomentum":      s_V4_AntiMomentum(),
    "V5 Stability+Adv":        s_V5_Stab_plus_Adv(),
    "V6 Pure_yield":           s_V6_Pure_yield(),
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

print("\n" + "="*90); print("KCN SCHEMA VARIANTS WITH PRE-SALES (within-KCN ranking, profit_3M)"); print("="*90)
print(f"\n{'Schema':<28}{'A_n':>4}{'A_med':>10}{'A_WR':>8}{'spread':>9}{'IC':>9}{'mono':>7}")
print("-"*78)

results = {}
for label, sch in SCHEMAS.items():
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
    a_wr = out[out.tier=="A"]["WR"].iloc[0] if (out.tier=="A").any() else np.nan
    a_n = int(out[out.tier=="A"]["N"].iloc[0]) if (out.tier=="A").any() else 0
    mono = "✓" if inv == 0 else f"⚠{inv}"
    print(f"{label:<28}{a_n:>4}{a_med:>+9.2f}%{a_wr:>+7.1f}%{spread:>+8.2f}{ic:>+8.3f}{mono:>6}")
    results[label] = (out, ic, spread, a_med, a_wr)

# Detailed tier breakdown for top 3
print("\n" + "="*80); print("DETAILED TIER ORDERING — top 3 schemas (by A median)"); print("="*80)
ranked = sorted(results.items(), key=lambda x: x[1][3] if not np.isnan(x[1][3]) else -99, reverse=True)
for label, (out, ic, spread, a_med, a_wr) in ranked[:4]:
    print(f"\n  {label}  (IC={ic:+.3f}, spread={spread:+.2f}):")
    print(out.to_string(index=False, float_format="%.2f"))

# Show top A picks for the winner
winner = ranked[0]
print(f"\n  Top A tier picks for WINNER ({winner[0]}):")
df["s_w"] = score(df, SCHEMAS[winner[0]])
s = df.dropna(subset=["s_w"]).copy()
s["pct"] = s.groupby("quarter")["s_w"].rank(pct=True)
s["tier"] = s["pct"].apply(tier_of)
A = s[s["tier"]=="A"].sort_values("s_w", ascending=False)
print(A[["ticker","quarter","profit_3M","s_w","AdvCust_MktCap_yld","ROE_Min5Y","PB"]].head(15).to_string(index=False))

print("\n" + "="*80); print("DONE"); print("="*80)
