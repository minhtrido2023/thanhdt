#!/usr/bin/env python3
"""
test_fa_presales_ic.py
======================
IC analysis of pre-sales indicators (new BQ columns) vs forward returns.

New columns available:
  AdvCust_P0..P7      - Advance from customer (8 quarters)
  UnearnRev_P0..P7    - Unearned revenue (8 quarters)
  Inventory_P0..P7    - Inventory (8 quarters, expanded from just P0)
  RE_Inventory        - Real estate inventory (single)

Derived indicators tested:
  AdvCust_YoY         = (P0 - P4) / |P4|
  AdvCust_TTM_growth  = (P0+P1+P2+P3)/(P4+P5+P6+P7) - 1
  AdvCust_QoQ         = (P0 - P1) / |P1|
  AdvCust_accel       = QoQ_now - QoQ_prior
  AdvCust_Rev_cover   = AdvCust_P0 / Revenue_P0
  AdvCust_MktCap_yld  = AdvCust_P0 / MktCap
  AdvCust_CV          = std/mean of 8Q
  AdvCust_peak_ratio  = P0 / max(P0..P7)
  (same family for UnearnRev, Inventory)

Universes:
  REIT_KCN, REIT_RES, REIT_OTHER (real estate where pre-sales matters most)
  DEFAULT (sanity check — should be weak)
  All-universe (for completeness)
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"

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
    if r.returncode != 0: raise RuntimeError(f"{r.stdout[:300]}|{r.stderr[:300]}")
    return pd.read_csv(StringIO(r.stdout.strip()))

def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 30: return float("nan"), 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y,
    f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
    f.AdvCust_P0, f.AdvCust_P1, f.AdvCust_P2, f.AdvCust_P3,
    f.AdvCust_P4, f.AdvCust_P5, f.AdvCust_P6, f.AdvCust_P7,
    f.UnearnRev_P0, f.UnearnRev_P1, f.UnearnRev_P2, f.UnearnRev_P3,
    f.UnearnRev_P4, f.UnearnRev_P5, f.UnearnRev_P6, f.UnearnRev_P7,
    f.Inventory_P0, f.Inventory_P1, f.Inventory_P2, f.Inventory_P3,
    f.Inventory_P4, f.Inventory_P5, f.Inventory_P6, f.Inventory_P7,
    f.RE_Inventory,
    f.OShares, f.Close AS f_close,
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

# Sub-sector classification
def subsector(row):
    icb = row["ICB_Code"]; tk = row["ticker"]
    if icb in (8633, 8637):
        if tk in KCN_TICKERS:           return "REIT_KCN"
        if tk in RESIDENTIAL_TICKERS:   return "REIT_RES"
        return "REIT_OTHER"
    if icb == 8355:                     return "BANK"
    if icb in (8775, 8777):             return "SECURITIES"
    if icb == 8536:                     return "INSURANCE"
    if icb == 3353:                     return "CG_AUTO"
    return "DEFAULT"
df["sub"] = df.apply(subsector, axis=1)
print("\nSub-sector distribution (top 10):")
print(df["sub"].value_counts().head(10).to_string())

# ─── Build pre-sales indicators ────────────────────────────────────────────
df["MktCap"] = df["Close"] * df["OShares"]

# Helper to compute series stats safely
def safe_div(num, den):
    return np.where(np.abs(den) > 1e-3, num / den.replace(0, np.nan), np.nan)

# AdvCust family
df["AdvCust_YoY"] = safe_div(df["AdvCust_P0"] - df["AdvCust_P4"], df["AdvCust_P4"].abs())
df["AdvCust_YoY"] = df["AdvCust_YoY"].clip(-5, 20)
ttm_now_adv = df[["AdvCust_P0","AdvCust_P1","AdvCust_P2","AdvCust_P3"]].sum(axis=1, skipna=False)
ttm_prv_adv = df[["AdvCust_P4","AdvCust_P5","AdvCust_P6","AdvCust_P7"]].sum(axis=1, skipna=False)
df["AdvCust_TTM_growth"] = np.where(ttm_prv_adv.abs() > 1e-3,
                                     (ttm_now_adv - ttm_prv_adv) / ttm_prv_adv.abs(),
                                     np.nan).clip(-5, 20)
df["AdvCust_QoQ"] = safe_div(df["AdvCust_P0"] - df["AdvCust_P1"], df["AdvCust_P1"].abs())
df["AdvCust_QoQ"] = df["AdvCust_QoQ"].clip(-5, 20)
df["AdvCust_QoQ_prev"] = safe_div(df["AdvCust_P1"] - df["AdvCust_P2"], df["AdvCust_P2"].abs())
df["AdvCust_QoQ_prev"] = df["AdvCust_QoQ_prev"].clip(-5, 20)
df["AdvCust_accel"] = df["AdvCust_QoQ"] - df["AdvCust_QoQ_prev"]
df["AdvCust_Rev_cover"] = safe_div(df["AdvCust_P0"], df["Revenue_P0"].abs())
df["AdvCust_Rev_cover"] = df["AdvCust_Rev_cover"].clip(-1, 50)
df["AdvCust_MktCap_yld"] = safe_div(df["AdvCust_P0"], df["MktCap"])
df["AdvCust_MktCap_yld"] = df["AdvCust_MktCap_yld"].clip(-1, 20)

# 8Q stats
adv_8q = df[[f"AdvCust_P{i}" for i in range(8)]].values.astype(float)
adv_n = np.sum(~np.isnan(adv_8q), axis=1)
with np.errstate(divide="ignore", invalid="ignore"):
    adv_mean = np.nanmean(adv_8q, axis=1)
    adv_std = np.nanstd(adv_8q, axis=1, ddof=1)
    adv_max = np.nanmax(adv_8q, axis=1)
    df["AdvCust_CV"] = np.where(adv_n >= 6, adv_std / np.maximum(np.abs(adv_mean), 1e6), np.nan).clip(max=10)
    df["AdvCust_peak_ratio"] = np.where(adv_max > 0, df["AdvCust_P0"] / adv_max, np.nan)
df["AdvCust_CV_inv"] = -df["AdvCust_CV"]
df["AdvCust_peak_inv"] = -df["AdvCust_peak_ratio"]  # low peak = early cycle (anti-peak)

# UnearnRev family
df["UnearnRev_YoY"] = safe_div(df["UnearnRev_P0"] - df["UnearnRev_P4"], df["UnearnRev_P4"].abs()).clip(-5, 20)
ttm_now_un = df[["UnearnRev_P0","UnearnRev_P1","UnearnRev_P2","UnearnRev_P3"]].sum(axis=1, skipna=False)
ttm_prv_un = df[["UnearnRev_P4","UnearnRev_P5","UnearnRev_P6","UnearnRev_P7"]].sum(axis=1, skipna=False)
df["UnearnRev_TTM_growth"] = np.where(ttm_prv_un.abs() > 1e-3,
                                       (ttm_now_un - ttm_prv_un) / ttm_prv_un.abs(),
                                       np.nan).clip(-5, 20)
df["UnearnRev_QoQ"] = safe_div(df["UnearnRev_P0"] - df["UnearnRev_P1"], df["UnearnRev_P1"].abs()).clip(-5, 20)
df["UnearnRev_Rev_cover"] = safe_div(df["UnearnRev_P0"], df["Revenue_P0"].abs()).clip(-1, 50)
df["UnearnRev_MktCap_yld"] = safe_div(df["UnearnRev_P0"], df["MktCap"]).clip(-1, 20)

# Combined: AdvCust + UnearnRev (total forward revenue commitment)
df["TotalBacklog_P0"] = df["AdvCust_P0"].fillna(0) + df["UnearnRev_P0"].fillna(0)
df["TotalBacklog_P4"] = df["AdvCust_P4"].fillna(0) + df["UnearnRev_P4"].fillna(0)
df["TotalBacklog_YoY"] = safe_div(df["TotalBacklog_P0"] - df["TotalBacklog_P4"],
                                   df["TotalBacklog_P4"].abs()).clip(-5, 20)
df["TotalBacklog_MktCap_yld"] = safe_div(df["TotalBacklog_P0"], df["MktCap"]).clip(-1, 20)

# Inventory family (now 8Q!)
inv_8q = df[[f"Inventory_P{i}" for i in range(8)]].values.astype(float)
inv_n = np.sum(~np.isnan(inv_8q), axis=1)
with np.errstate(divide="ignore", invalid="ignore"):
    inv_mean = np.nanmean(inv_8q, axis=1)
    inv_std = np.nanstd(inv_8q, axis=1, ddof=1)
    df["Inventory_CV"] = np.where(inv_n >= 6, inv_std / np.maximum(np.abs(inv_mean), 1e6), np.nan).clip(max=10)
df["Inventory_YoY"] = safe_div(df["Inventory_P0"] - df["Inventory_P4"], df["Inventory_P4"].abs()).clip(-5, 20)
df["Inventory_Rev_cover"] = safe_div(df["Inventory_P0"], df["Revenue_P0"].abs()).clip(-1, 50)

# RE_Inventory (single point)
df["RE_Inventory_MktCap"] = safe_div(df["RE_Inventory"], df["MktCap"]).clip(-1, 20)

# ─── Compute IC per sub-sector ────────────────────────────────────────────
INDICATORS = [
    ("AdvCust_P0 (raw)",        "AdvCust_P0"),
    ("AdvCust_YoY",             "AdvCust_YoY"),
    ("AdvCust_TTM_growth",      "AdvCust_TTM_growth"),
    ("AdvCust_QoQ",             "AdvCust_QoQ"),
    ("AdvCust_accel",           "AdvCust_accel"),
    ("AdvCust_Rev_cover",       "AdvCust_Rev_cover"),
    ("AdvCust_MktCap_yld",      "AdvCust_MktCap_yld"),
    ("AdvCust_CV (inv)",        "AdvCust_CV_inv"),
    ("AdvCust_peak_ratio",      "AdvCust_peak_ratio"),
    ("AdvCust_peak (inv)",      "AdvCust_peak_inv"),
    ("UnearnRev_YoY",           "UnearnRev_YoY"),
    ("UnearnRev_TTM_growth",    "UnearnRev_TTM_growth"),
    ("UnearnRev_QoQ",           "UnearnRev_QoQ"),
    ("UnearnRev_Rev_cover",     "UnearnRev_Rev_cover"),
    ("UnearnRev_MktCap_yld",    "UnearnRev_MktCap_yld"),
    ("TotalBacklog_YoY",        "TotalBacklog_YoY"),
    ("TotalBacklog_MktCap_yld", "TotalBacklog_MktCap_yld"),
    ("Inventory_YoY",           "Inventory_YoY"),
    ("Inventory_Rev_cover",     "Inventory_Rev_cover"),
    ("Inventory_CV (inv)",      None),  # special
    ("RE_Inventory_MktCap",     "RE_Inventory_MktCap"),
]
df["Inventory_CV_inv"] = -df["Inventory_CV"]
INDICATORS[19] = ("Inventory_CV (inv)", "Inventory_CV_inv")

GROUPS = ["REIT_KCN", "REIT_RES", "REIT_OTHER", "DEFAULT", "ALL"]
# ALL = whole universe

def get_group(df_, g):
    if g == "ALL": return df_
    return df_[df_["sub"] == g]

print("\n" + "="*110)
print("IC vs profit_3M — pre-sales indicators by sub-sector")
print("="*110)
print(f"\n{'Indicator':<28}", end="")
for g in GROUPS:
    print(f"{g[:10]:>11}", end="")
print()
print("-"*(28 + 11*len(GROUPS)))
for name, col in INDICATORS:
    row = f"{name:<28}"
    for g in GROUPS:
        sub = get_group(df, g)
        rho, n = spearman_ic(sub[col], sub["profit_3M"])
        if np.isnan(rho):
            row += f"{'n/a':>11}"
        else:
            row += f"{rho:>+10.3f} "
    print(row)

# N per group (with profit_3M)
print(f"\n  Sample sizes (with profit_3M data):")
for g in GROUPS:
    sub = get_group(df, g).dropna(subset=["profit_3M"])
    print(f"    {g}: N={len(sub)}")

# ─── Multi-horizon IC for top indicators (in REIT_KCN + REIT_RES) ─────────
print("\n" + "="*100)
print("MULTI-HORIZON IC for pre-sales indicators (REIT_KCN + REIT_RES combined)")
print("="*100)
reit = df[df["sub"].isin(["REIT_KCN","REIT_RES"])]
print(f"  REIT_KCN + REIT_RES universe: N={len(reit)}")
horizons = ["profit_3M","O6M","O1Y","O2Y"]
print(f"\n{'Indicator':<28}", end="")
for h in horizons:
    print(f"{h:>11}", end="")
print()
print("-"*(28 + 11*len(horizons)))
for name, col in INDICATORS:
    row = f"{name:<28}"
    for h in horizons:
        rho, n = spearman_ic(reit[col], reit[h])
        if np.isnan(rho):
            row += f"{'n/a':>11}"
        else:
            row += f"{rho:>+10.3f} "
    print(row)

# ─── Find best indicator per sub-sector ───────────────────────────────────
print("\n" + "="*80)
print("TOP 5 INDICATORS PER SUB-SECTOR (by |IC| on profit_3M)")
print("="*80)
for g in ["REIT_KCN", "REIT_RES", "REIT_OTHER", "DEFAULT"]:
    sub = get_group(df, g)
    n_total = len(sub.dropna(subset=["profit_3M"]))
    results = []
    for name, col in INDICATORS:
        rho, _ = spearman_ic(sub[col], sub["profit_3M"])
        if not np.isnan(rho):
            results.append((name, rho))
    results.sort(key=lambda x: abs(x[1]), reverse=True)
    print(f"\n  {g} (N={n_total}):")
    for name, rho in results[:5]:
        marker = " 🟢" if abs(rho) > 0.15 else (" 🔵" if abs(rho) > 0.10 else "")
        sign = "+" if rho > 0 else "-"
        print(f"    {sign} {name:<28} IC={rho:+.3f}{marker}")

# Show sample values for REIT (sanity)
print("\n" + "="*80); print("SANITY: top REIT_KCN by AdvCust_YoY (recent)"); print("="*80)
recent = df[(df["sub"]=="REIT_KCN") & (df["quarter"].isin(["2024Q4","2023Q4"]))].copy()
recent = recent.sort_values("AdvCust_YoY", ascending=False).head(10)
print(recent[["ticker","quarter","AdvCust_P0","AdvCust_YoY","profit_3M"]].to_string(index=False))

print("\n" + "="*80); print("DONE"); print("="*80)
