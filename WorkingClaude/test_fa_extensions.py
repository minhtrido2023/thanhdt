#!/usr/bin/env python3
"""
test_fa_extensions.py
=====================
Unified test harness for 6 candidate FA-system extensions.

For each candidate, recompute total_score with the extension added,
re-bucket into tiers, and measure tier ordering on forward profit_3M.

Compare vs baseline (current 7-axis system).

Extensions tested:
  1) Margin trajectory  (GPM 8Q slope, NPM_delta, EBITM_delta)
  2) Beneish-lite       (DSO_delta, GPM_delta, FinLev_delta, AssetTurn_delta)
  3) Working capital    (CashCycle improvement, AssetTurn improvement, InvTurn)
  4) Solvency depth     (NetDebt/EBITDA, ST/Total Debt, Altman Z'')
  5) ROIC trend         (ROIC_Trailing vs ROIC5Y — ROIIC proxy)
  6) Industry modifier  (per-ICB axis weights)

Output: fa_ext_results.csv + console table
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

def bq_query(sql, label=""):
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
        raise RuntimeError(f"[BQ ERROR] {label}: {(r.stdout or r.stderr)[:800]}")
    txt = r.stdout.strip()
    return pd.read_csv(StringIO(txt)) if txt else pd.DataFrame()

# ─── 1. Pull raw + all candidate columns in one big query ───────────────────
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
    -- Margin 8Q series
    f.GPM_P0, f.GPM_P1, f.GPM_P2, f.GPM_P3, f.GPM_P4, f.GPM_P5, f.GPM_P6, f.GPM_P7,
    f.NPM_P0, f.NPM_P4, f.EBITM_P0, f.EBITM_P4,
    -- Working capital / efficiency
    f.DSO_P0, f.DSO_P4, f.DIO_P0, f.DIO_P4, f.DPO_P0, f.DPO_P4,
    f.CashCycle_P0, f.CashCycle_P4,
    f.AssetTurn_P0, f.AssetTurn_P4, f.InvTurn_P0, f.InvTurn_P4,
    f.FinLev_P0, f.FinLev_P4,
    -- Solvency raw
    f.StDebt_P0, f.LtDebt_P0, f.StLiab_P0, f.LtLiab_P0,
    f.Cash_P0, f.EBITDA_P0, f.totalAsset_P0,
    f.AR_P0,
    -- ROIC trend (Trailing vs 5Y)
    f.ROIC_Trailing, f.ROE_Trailing,
    -- Peak ratios
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
    t.Volume_3M_P50 * t.Close AS trading_value_1M,
    t.profit_3M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker
    AND t.time <= f.time
    AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2014-01-01"
    AND f.quarter LIKE "%Q4"
    AND t.Volume_3M_P50 IS NOT NULL
    AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching raw + candidate columns ...")
df = bq_query(SQL, "raw")
print(f"  {len(df):,} Q4 rows after liquidity filter")
df["ICB_Code"] = df["ICB_Code"].fillna("UNK")

# ─── 2. Compute baseline indicators (same as fundamental_rating.py) ─────────
df["growth_yield"] = df["growth_yield"].clip(-0.15, 0.15)
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"]  = df["DY"] * _mult
df["DY_sust"] = _mult

NP_COLS  = [f"NP_P{i}"      for i in range(8)]
REV_COLS = [f"Revenue_P{i}" for i in range(8)]
np_arr  = df[NP_COLS].values.astype(float)
rev_arr = df[REV_COLS].values.astype(float)
np_n  = np.sum(~np.isnan(np_arr),  axis=1)
rev_n = np.sum(~np.isnan(rev_arr), axis=1)
with np.errstate(divide="ignore", invalid="ignore"):
    np_mean  = np.nanmean(np_arr,  axis=1);  np_std  = np.nanstd(np_arr,  axis=1, ddof=1)
    rev_mean = np.nanmean(rev_arr, axis=1);  rev_std = np.nanstd(rev_arr, axis=1, ddof=1)
    df["NP_CV"]  = np.where(np_n  >= 6, np_std  / np.maximum(np.abs(np_mean),  1e6), np.nan)
    df["Rev_CV"] = np.where(rev_n >= 6, rev_std / np.maximum(np.abs(rev_mean), 1e6), np.nan)
    df["NP_CV"]  = df["NP_CV"].clip(upper=10)
    df["Rev_CV"] = df["Rev_CV"].clip(upper=10)
rev_p0 = df["Revenue_P0"].values; rev_p7 = df["Revenue_P7"].values
mask = (rev_p0 > 0) & (rev_p7 > 0)
df["LT_CAGR"] = np.where(mask, (rev_p0 / rev_p7) ** (4/7) - 1, np.nan)
df["LT_CAGR"] = df["LT_CAGR"].clip(-0.95, 5.0)

# Industry-relative valuation z
for col in ["PE", "PB", "PCF"]:
    grp = df.groupby(["quarter", "ICB_Code"])[col]
    med = grp.transform("median"); sd = grp.transform("std")
    z_ind = (df[col] - med) / sd.replace(0, np.nan)
    z_global = df.groupby("quarter")[col].transform(lambda x: (x - x.median()) / x.std())
    df[f"{col}_ind_z"] = z_ind.fillna(z_global)

# ─── 3. Compute candidate indicators ────────────────────────────────────────
print("Computing candidate indicators ...")

# 3.1 Margin trajectory — GPM slope over 8 quarters (P7 oldest → P0 newest)
GPM_COLS_ORDERED = [f"GPM_P{i}" for i in [7,6,5,4,3,2,1,0]]   # time index 0..7
gpm_mat = df[GPM_COLS_ORDERED].values.astype(float)
x = np.arange(8)
# vectorised linear regression slope per row, NaN-aware
def slope_row(y):
    m = ~np.isnan(y)
    if m.sum() < 4: return np.nan
    xx = x[m]; yy = y[m]
    n = len(xx); sx = xx.sum(); sy = yy.sum()
    sxx = (xx*xx).sum(); sxy = (xx*yy).sum()
    denom = n*sxx - sx*sx
    return np.nan if denom == 0 else (n*sxy - sx*sy) / denom
df["GPM_slope"] = np.array([slope_row(r) for r in gpm_mat])
df["NPM_delta"]  = df["NPM_P0"]  - df["NPM_P4"]
df["EBITM_delta"]= df["EBITM_P0"]- df["EBITM_P4"]

# 3.2 Beneish-lite: weighted sum of red flags (negative = red flag count)
# Higher M = more manipulation likely. We invert so r_M higher = cleaner.
df["DSO_delta"]   = df["DSO_P0"] - df["DSO_P4"]            # +ve = worsening collection
df["FinLev_delta"]= df["FinLev_P0"] - df["FinLev_P4"]      # +ve = more leverage
df["GPM_delta_abs"] = df["GPM_P4"] - df["GPM_P0"]          # +ve = margin shrinking
df["AT_delta"]    = df["AssetTurn_P4"] - df["AssetTurn_P0"]# +ve = efficiency declining
# Beneish-lite composite (clip extremes to avoid one-row dominance)
for c in ["DSO_delta","FinLev_delta","GPM_delta_abs","AT_delta"]:
    df[c] = df[c].clip(df[c].quantile(0.01), df[c].quantile(0.99))
# rank: lower (better) → high rank. We negate the column then rank pct.

# 3.3 Working capital
df["CashCycle_impr"] = df["CashCycle_P4"] - df["CashCycle_P0"]   # +ve = improved
df["AssetTurn_impr"] = df["AssetTurn_P0"] - df["AssetTurn_P4"]   # +ve = improved
df["InvTurn_impr"]   = df["InvTurn_P0"]   - df["InvTurn_P4"]

# 3.4 Solvency depth
df["NetDebt_EBITDA"] = (df["StDebt_P0"] + df["LtDebt_P0"] - df["Cash_P0"]) / df["EBITDA_P0"].replace(0, np.nan)
df["NetDebt_EBITDA"] = df["NetDebt_EBITDA"].clip(-10, 50)
total_debt = (df["StDebt_P0"] + df["LtDebt_P0"]).replace(0, np.nan)
df["ST_Total_Debt"] = (df["StDebt_P0"] / total_debt).clip(0, 1)
# Altman Z'' (private firm version): 6.56(WC/TA) + 3.26(RE/TA) + 6.72(EBIT/TA) + 1.05(BVeq/TL)
# Approximate: WC = (totalAsset - StLiab) is wrong; WC = CurrAssets - StLiab. We don't have CA.
# Use simpler proxy: 6.72*(EBITDA/TA) + 1.05*(BVeq/(StLiab+LtLiab))
total_liab = (df["StLiab_P0"] + df["LtLiab_P0"]).replace(0, np.nan)
bv_eq = df["totalAsset_P0"] - df["StLiab_P0"] - df["LtLiab_P0"]
df["Altman_Z_proxy"] = (6.72 * df["EBITDA_P0"] / df["totalAsset_P0"].replace(0, np.nan)
                       + 1.05 * bv_eq / total_liab).clip(-10, 30)

# 3.5 ROIC trend (ROIIC proxy) — Trailing minus 5Y average
df["ROIC_trend"] = df["ROIC_Trailing"] - df["ROIC5Y"]

# ─── 4. Direction adjustment (lower-is-better → negate) ─────────────────────
INV_COLS = ["Debt_Eq_P0",
            "PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z",
            "NP_CV","Rev_CV",
            # candidates: lower = better
            "DSO_delta","FinLev_delta","GPM_delta_abs","AT_delta",
            "NetDebt_EBITDA","ST_Total_Debt"]
for c in INV_COLS:
    df[c] = -df[c]

# ─── 5. Baseline axis composite ─────────────────────────────────────────────
AXIS_BASE = {
    "quality":     ["ROIC5Y","ROE_Min5Y","FSCORE"],
    "stability":   ["NP_CV","Rev_CV","LT_CAGR"],
    "cash":        ["CF_OA_5Y","CFOA_NP"],
    "shareholder": ["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
    "growth":      ["NP_R","Revenue_YoY_P0","GPM_change","NP_peak_ratio","Rev_peak_ratio"],
    "health":      ["Debt_Eq_P0","IntCov_P0","CashR_P0"],
    "valuation":   ["PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","growth_yield"],
}

# Pre-rank every column we'll ever need (per quarter pct rank)
ALL_COLS = set()
for cols in AXIS_BASE.values(): ALL_COLS.update(cols)
ALL_COLS.update(["GPM_slope","NPM_delta","EBITM_delta",
                 "DSO_delta","FinLev_delta","GPM_delta_abs","AT_delta",
                 "CashCycle_impr","AssetTurn_impr","InvTurn_impr",
                 "NetDebt_EBITDA","ST_Total_Debt","Altman_Z_proxy",
                 "ROIC_trend"])
print("Computing percentile ranks ...")
for c in ALL_COLS:
    if c in df.columns:
        df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

def assign_tier(p):
    for name, lo, hi in TIERS:
        if lo <= p <= hi: return name
    return "E"

def compute_score(axis_cols, weights):
    """Given axis→[cols] mapping and axis→weight, return total_score series."""
    score_axis = {}
    for axis, cols in axis_cols.items():
        rank_cols = [f"r_{c}" for c in cols if f"r_{c}" in df.columns]
        if not rank_cols:
            score_axis[axis] = pd.Series(np.nan, index=df.index)
        else:
            score_axis[axis] = df[rank_cols].mean(axis=1, skipna=True)
    score_df = pd.DataFrame(score_axis)
    w = np.array([weights[a] for a in axis_cols.keys()])
    return (score_df.values * w).sum(axis=1), score_df

def evaluate(label, axis_cols, weights):
    """Compute scores, assign tiers, return validation table."""
    total, _ = compute_score(axis_cols, weights)
    tmp = df.copy()
    tmp["total_score"] = total
    tmp = tmp.dropna(subset=["total_score"])
    tmp["score_pct"] = tmp.groupby("quarter")["total_score"].rank(pct=True)
    tmp["tier"] = tmp["score_pct"].apply(assign_tier)
    v = tmp.dropna(subset=["profit_3M"])
    rows = []
    for tier in ["A","B","C","D","E"]:
        g = v[v["tier"] == tier]["profit_3M"]
        if len(g):
            rows.append({"variant":label,"tier":tier,"N":len(g),
                         "median":g.median(),"mean":g.mean(),"WR":(g>0).mean()*100})
    out = pd.DataFrame(rows)
    # tier separation
    med_a = out[out["tier"]=="A"]["median"].iloc[0] if (out["tier"]=="A").any() else np.nan
    med_e = out[out["tier"]=="E"]["median"].iloc[0] if (out["tier"]=="E").any() else np.nan
    spread = med_a - med_e
    # monotonicity (count adjacent inversions)
    meds = out["median"].values
    inv = sum(1 for i in range(len(meds)-1) if meds[i] < meds[i+1])
    return out, spread, inv

# ─── 6. Run baseline + each variant ─────────────────────────────────────────
results = []
print("\n" + "="*70)
print("BASELINE (current 7-axis FA-system)")
print("="*70)
base_out, base_spread, base_inv = evaluate("baseline", AXIS_BASE, WEIGHTS)
print(base_out.to_string(index=False, float_format="%.2f"))
print(f"  → A−E median spread: {base_spread:.2f}pp, inversions: {base_inv}")
results.append(base_out)

variants = {
    "T1_margin_slope": {
        "growth": AXIS_BASE["growth"] + ["GPM_slope","NPM_delta","EBITM_delta"],
    },
    "T2_beneish_lite": {
        "health": AXIS_BASE["health"] + ["DSO_delta","FinLev_delta","GPM_delta_abs","AT_delta"],
    },
    "T3_working_capital": {
        "quality": AXIS_BASE["quality"] + ["CashCycle_impr","AssetTurn_impr","InvTurn_impr"],
    },
    "T4_solvency_depth": {
        "health": AXIS_BASE["health"] + ["NetDebt_EBITDA","ST_Total_Debt","Altman_Z_proxy"],
    },
    "T5_roic_trend": {
        "quality": AXIS_BASE["quality"] + ["ROIC_trend"],
    },
}

for label, override in variants.items():
    axis_cols = dict(AXIS_BASE)
    axis_cols.update(override)
    print("\n" + "="*70); print(label); print("="*70)
    out, spread, inv = evaluate(label, axis_cols, WEIGHTS)
    print(out.to_string(index=False, float_format="%.2f"))
    print(f"  → A−E median spread: {spread:.2f}pp (Δ vs base: {spread-base_spread:+.2f}pp), inversions: {inv}")
    results.append(out)

# T6 Industry modifier — keep base axes but re-weight per ICB sector
print("\n" + "="*70); print("T6_industry_modifier"); print("="*70)
SECTOR_WEIGHTS = {
    # Banks: emphasize health, valuation; drop GPM-like signals
    "NH": {"quality":0.25,"stability":0.20,"cash":0.05,"shareholder":0.15,
           "growth":0.10,"health":0.15,"valuation":0.10},
    # Securities: similar to banks
    "CK": {"quality":0.22,"stability":0.20,"cash":0.05,"shareholder":0.15,
           "growth":0.13,"health":0.10,"valuation":0.15},
    # Insurance
    "BH": {"quality":0.22,"stability":0.22,"cash":0.05,"shareholder":0.15,
           "growth":0.13,"health":0.10,"valuation":0.13},
    # Real estate (often grouped under CT but BĐS industry code differs in VN; for now keep CT default)
    # Industrials/Consumer/everything else: baseline
    "CT": WEIGHTS,
}
total = np.zeros(len(df))
for axis in WEIGHTS.keys():
    rank_cols = [f"r_{c}" for c in AXIS_BASE[axis] if f"r_{c}" in df.columns]
    axis_score = df[rank_cols].mean(axis=1, skipna=True).fillna(0).values
    # per-row weight based on ICB_Code
    w = df["ICB_Code"].map(lambda code: SECTOR_WEIGHTS.get(str(code), WEIGHTS).get(axis, WEIGHTS[axis])).values
    total += axis_score * w

tmp = df.copy()
tmp["total_score"] = total
tmp = tmp.dropna(subset=["total_score"])
tmp["score_pct"] = tmp.groupby("quarter")["total_score"].rank(pct=True)
tmp["tier"] = tmp["score_pct"].apply(assign_tier)
v = tmp.dropna(subset=["profit_3M"])
rows = []
for tier in ["A","B","C","D","E"]:
    g = v[v["tier"]==tier]["profit_3M"]
    if len(g):
        rows.append({"variant":"T6_industry_modifier","tier":tier,"N":len(g),
                     "median":g.median(),"mean":g.mean(),"WR":(g>0).mean()*100})
t6_out = pd.DataFrame(rows)
print(t6_out.to_string(index=False, float_format="%.2f"))
meds = t6_out["median"].values
t6_spread = meds[0] - meds[-1] if len(meds)==5 else np.nan
t6_inv = sum(1 for i in range(len(meds)-1) if meds[i] < meds[i+1])
print(f"  → A−E median spread: {t6_spread:.2f}pp (Δ vs base: {t6_spread-base_spread:+.2f}pp), inversions: {t6_inv}")
results.append(t6_out)

# ─── 7. Consolidated summary ────────────────────────────────────────────────
print("\n" + "="*70); print("CONSOLIDATED SUMMARY"); print("="*70)
all_df = pd.concat(results, ignore_index=True)
all_df.to_csv("data/fa_ext_results.csv", index=False)
print("Saved fa_ext_results.csv")
# Pivot for quick comparison
piv = all_df.pivot_table(index="tier", columns="variant", values="median").reindex(["A","B","C","D","E"])
print("\nMedian profit_3M by tier × variant:")
print(piv.to_string(float_format="%.2f"))
