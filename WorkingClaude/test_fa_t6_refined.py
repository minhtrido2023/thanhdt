#!/usr/bin/env python3
"""
test_fa_t6_refined.py
=====================
Refined T6 Industry-modifier test, AFTER discovering that:
  1) ICB_Code in BQ is numeric (e.g. 8355 = Banks), NOT 2-letter codes
  2) Original T6 in test_fa_extensions.py used fillna(0) for missing axes,
     which alone explains the +1.52pp gain (NOT industry weighting)

This script re-tests with:
  - Proper ICB code mapping (BANK=8355, REIT=8633/37, INS=8536, SEC=8775/77)
  - Identical NaN treatment as baseline (mean(skipna=True), drop rows with full-NaN axis)
  - Multiple sector-weight schemes

Variants:
  baseline           - reference (re-run for clean comparison)
  T6a_nan0           - baseline + fillna(0) for axis score (isolate NaN-treatment effect)
  T6b_bank_only      - special weights for ICB=8355 (banks) only
  T6c_financials     - BANK + REIT + INS + SEC each with bespoke weights
  T6d_financials_v2  - same but more aggressive de-emphasis of cash/health for financials

Output: console + fa_t6_refined_results.csv
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"

WEIGHTS = {
    "quality":     0.18,
    "stability":   0.18,
    "cash":        0.18,
    "shareholder": 0.15,
    "growth":      0.13,
    "health":      0.08,
    "valuation":   0.10,
}
TIERS = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]

def bq_query(sql):
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
        raise RuntimeError(f"[BQ ERROR] {(r.stdout or r.stderr)[:800]}")
    return pd.read_csv(StringIO(r.stdout.strip()))

# ─── 1. Pull data (baseline columns only — we don't need T1-T5 cols now) ────
SQL = """
WITH joined AS (
  SELECT
    f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.FSCORE,
    f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y,
    SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y,
    SAFE_DIVIDE(f.CF_OA_5Y + f.CF_Invest_5Y, ABS(f.CF_OA_5Y)) AS FCF_OA_ratio,
    f.Debt_Eq_P0, f.IntCov_P0, f.CashR_P0,
    SAFE_DIVIDE(f.PE - f.PE_MA5Y, f.PE_SD5Y) AS PE_self_z,
    SAFE_DIVIDE(f.PB - f.PB_MA5Y, f.PB_SD5Y) AS PB_self_z,
    CASE WHEN f.PE > 0 THEN SAFE_DIVIDE(f.NP_R, f.PE) ELSE NULL END AS growth_yield,
    f.PE, f.PB, f.PCF,
    f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
    f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
    f.Revenue_P4, f.Revenue_P5, f.Revenue_P6, f.Revenue_P7,
    CASE WHEN GREATEST(f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3,
                       f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0, GREATEST(f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3,
                                             f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    CASE WHEN GREATEST(f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
                       f.Revenue_P4, f.Revenue_P5, f.Revenue_P6, f.Revenue_P7) > 0
         THEN SAFE_DIVIDE(f.Revenue_P0,
                          GREATEST(f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
                                   f.Revenue_P4, f.Revenue_P5, f.Revenue_P6, f.Revenue_P7))
         ELSE NULL END AS Rev_peak_ratio,
    t.ICB_Code,
    t.profit_3M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2014-01-01" AND f.quarter LIKE "%Q4"
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching ...")
df = bq_query(SQL)
print(f"  {len(df):,} Q4 rows")

# ─── 2. Map ICB to sector bucket ────────────────────────────────────────────
def sector_bucket(icb):
    if pd.isna(icb): return "DEFAULT"
    try: code = int(float(icb))
    except: return "DEFAULT"
    if code == 8355:                 return "BANK"
    if code in (8633, 8637):         return "REIT"
    if code == 8536:                 return "INSURANCE"
    if code in (8775, 8777):         return "SECURITIES"
    return "DEFAULT"

df["sector"] = df["ICB_Code"].apply(sector_bucket)
print("\nSector distribution:")
print(df["sector"].value_counts().to_string())

# ─── 3. Baseline indicators ─────────────────────────────────────────────────
df["growth_yield"] = df["growth_yield"].clip(-0.15, 0.15)
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"]  = df["DY"] * _mult
df["DY_sust"] = _mult

NP_COLS  = [f"NP_P{i}" for i in range(8)]
REV_COLS = [f"Revenue_P{i}" for i in range(8)]
np_arr  = df[NP_COLS].values.astype(float)
rev_arr = df[REV_COLS].values.astype(float)
np_n  = np.sum(~np.isnan(np_arr),  axis=1)
rev_n = np.sum(~np.isnan(rev_arr), axis=1)
with np.errstate(divide="ignore", invalid="ignore"):
    np_mean  = np.nanmean(np_arr,  axis=1); np_std  = np.nanstd(np_arr,  axis=1, ddof=1)
    rev_mean = np.nanmean(rev_arr, axis=1); rev_std = np.nanstd(rev_arr, axis=1, ddof=1)
    df["NP_CV"]  = np.where(np_n  >= 6, np_std  / np.maximum(np.abs(np_mean),  1e6), np.nan).clip(max=10)
    df["Rev_CV"] = np.where(rev_n >= 6, rev_std / np.maximum(np.abs(rev_mean), 1e6), np.nan).clip(max=10)
rev_p0 = df["Revenue_P0"].values; rev_p7 = df["Revenue_P7"].values
mask = (rev_p0 > 0) & (rev_p7 > 0)
df["LT_CAGR"] = np.where(mask, (rev_p0 / rev_p7) ** (4/7) - 1, np.nan)
df["LT_CAGR"] = df["LT_CAGR"].clip(-0.95, 5.0)
df["ICB_Code"] = df["ICB_Code"].fillna("UNK")
for col in ["PE", "PB", "PCF"]:
    grp = df.groupby(["quarter", "ICB_Code"])[col]
    med = grp.transform("median"); sd = grp.transform("std")
    z_ind = (df[col] - med) / sd.replace(0, np.nan)
    z_global = df.groupby("quarter")[col].transform(lambda x: (x - x.median()) / x.std())
    df[f"{col}_ind_z"] = z_ind.fillna(z_global)

# Invert lower-is-better cols
INV = ["Debt_Eq_P0","PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","NP_CV","Rev_CV"]
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

# Rank all columns once
all_cols = set()
for cs in AXIS_BASE.values(): all_cols.update(cs)
print("\nComputing percentile ranks ...")
for c in all_cols:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

# Axis scores (mean of ranks, NaN-tolerant)
for axis, cols in AXIS_BASE.items():
    rank_cols = [f"r_{c}" for c in cols]
    df[f"score_{axis}"] = df[rank_cols].mean(axis=1, skipna=True)

# ─── 4. Sector weight schemes ───────────────────────────────────────────────
# BANK: ROE+PB-driven; cash/Debt_Eq meaningless; growth on EPS not Revenue YoY
SCHEME_B = {
    "BANK":       {"quality":0.28, "stability":0.20, "cash":0.05, "shareholder":0.12,
                   "growth":0.13, "health":0.04, "valuation":0.18},
    "DEFAULT":    WEIGHTS,
}
# Financials full coverage
SCHEME_C = {
    "BANK":       {"quality":0.28, "stability":0.20, "cash":0.05, "shareholder":0.12,
                   "growth":0.13, "health":0.04, "valuation":0.18},
    "REIT":       {"quality":0.18, "stability":0.10, "cash":0.10, "shareholder":0.15,
                   "growth":0.10, "health":0.07, "valuation":0.30},
    "INSURANCE":  {"quality":0.25, "stability":0.20, "cash":0.05, "shareholder":0.15,
                   "growth":0.10, "health":0.10, "valuation":0.15},
    "SECURITIES": {"quality":0.22, "stability":0.15, "cash":0.05, "shareholder":0.13,
                   "growth":0.15, "health":0.10, "valuation":0.20},
    "DEFAULT":    WEIGHTS,
}
# Even more aggressive: REIT cuts growth/health further, ups valuation+shareholder
SCHEME_D = {
    "BANK":       {"quality":0.30, "stability":0.22, "cash":0.03, "shareholder":0.10,
                   "growth":0.12, "health":0.03, "valuation":0.20},
    "REIT":       {"quality":0.18, "stability":0.08, "cash":0.10, "shareholder":0.20,
                   "growth":0.07, "health":0.05, "valuation":0.32},
    "INSURANCE":  {"quality":0.27, "stability":0.22, "cash":0.03, "shareholder":0.15,
                   "growth":0.08, "health":0.08, "valuation":0.17},
    "SECURITIES": {"quality":0.25, "stability":0.15, "cash":0.03, "shareholder":0.12,
                   "growth":0.13, "health":0.08, "valuation":0.24},
    "DEFAULT":    WEIGHTS,
}

# All schemes must sum to 1 per sector
def check_sum(s, name):
    for sec, w in s.items():
        assert abs(sum(w.values()) - 1.0) < 1e-9, f"{name}.{sec} sums {sum(w.values())}"
for nm, s in [("B",SCHEME_B),("C",SCHEME_C),("D",SCHEME_D)]: check_sum(s, nm)

# ─── 5. Evaluator ───────────────────────────────────────────────────────────
def assign_tier(p):
    for n, lo, hi in TIERS:
        if lo <= p <= hi: return n
    return "E"

def evaluate(label, scheme_map=None, nan_fill_zero=False):
    """scheme_map: sector → axis_weights dict. If None → use WEIGHTS for all rows."""
    axis_scores = {a: df[f"score_{a}"].copy() for a in WEIGHTS}
    # Build per-row weight matrix
    if scheme_map is None:
        # uniform weights
        total = np.zeros(len(df))
        for a in WEIGHTS:
            s = axis_scores[a].fillna(0).values if nan_fill_zero else axis_scores[a].values
            total += s * WEIGHTS[a]
    else:
        total = np.zeros(len(df))
        for a in WEIGHTS:
            s = axis_scores[a].fillna(0).values if nan_fill_zero else axis_scores[a].values
            w = df["sector"].map(lambda sec: scheme_map.get(sec, scheme_map["DEFAULT"])[a]).values
            total += s * w
    tmp = df.copy()
    tmp["total_score"] = total
    if not nan_fill_zero:
        # drop rows where any axis fully NaN (baseline behaviour)
        full_nan = pd.concat([axis_scores[a].isna() for a in WEIGHTS], axis=1).any(axis=1)
        tmp.loc[full_nan, "total_score"] = np.nan
    tmp = tmp.dropna(subset=["total_score"])
    tmp["score_pct"] = tmp.groupby("quarter")["total_score"].rank(pct=True)
    tmp["tier"] = tmp["score_pct"].apply(assign_tier)
    v = tmp.dropna(subset=["profit_3M"])
    rows = []
    for tier in ["A","B","C","D","E"]:
        g = v[v["tier"]==tier]["profit_3M"]
        if len(g):
            rows.append({"variant":label,"tier":tier,"N":len(g),
                         "median":g.median(),"mean":g.mean(),"WR":(g>0).mean()*100})
    out = pd.DataFrame(rows)
    return out, tmp

variants = [
    ("baseline",          None,      False),
    ("T6a_nan0",          None,      True),
    ("T6b_bank_only",     SCHEME_B,  False),
    ("T6c_financials",    SCHEME_C,  False),
    ("T6d_aggressive",    SCHEME_D,  False),
]

all_out = []
base_spread = None
sector_tier = {}
for label, sch, nan0 in variants:
    out, tmp = evaluate(label, sch, nan0)
    meds = out["median"].values
    spread = meds[0] - meds[-1] if len(meds)==5 else np.nan
    inv = sum(1 for i in range(len(meds)-1) if meds[i] < meds[i+1])
    if label == "baseline": base_spread = spread
    delta = "" if base_spread is None else f" (Δ {spread-base_spread:+.2f})"
    print("\n" + "="*70); print(f"{label}  | A−E spread = {spread:.2f}pp{delta}, inversions={inv}"); print("="*70)
    print(out.to_string(index=False, float_format="%.2f"))
    all_out.append(out)
    sector_tier[label] = tmp

# ─── 6. Drilldown: how does T6c reshape tier composition per sector? ────────
print("\n" + "="*70); print("SECTOR DRILLDOWN: tier composition by sector for baseline vs T6c"); print("="*70)
for sec in ["BANK","REIT","INSURANCE","SECURITIES","DEFAULT"]:
    print(f"\n--- {sec} ---")
    for label in ["baseline","T6c_financials"]:
        t = sector_tier[label]
        sub = t[t["sector"] == sec]
        if len(sub) == 0: continue
        v = sub.dropna(subset=["profit_3M"])
        if len(v) == 0: continue
        row = f"{label:18s} N={len(sub):4d}  "
        for tier in ["A","B","C","D","E"]:
            g = v[v["tier"]==tier]["profit_3M"]
            row += f"{tier}:{len(g):3d}({g.median():+5.1f}%)  " if len(g) else f"{tier}: 0          "
        print(row)

# ─── 7. Save summary ────────────────────────────────────────────────────────
summary = pd.concat(all_out, ignore_index=True)
summary.to_csv("data/fa_t6_refined_results.csv", index=False)
print("\nSaved fa_t6_refined_results.csv")
piv = summary.pivot_table(index="tier", columns="variant", values="median").reindex(["A","B","C","D","E"])
print("\nMedian profit_3M by tier × variant:")
print(piv.to_string(float_format="%.2f"))
