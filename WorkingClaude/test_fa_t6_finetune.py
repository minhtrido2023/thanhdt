#!/usr/bin/env python3
"""
test_fa_t6_finetune.py
======================
Further refinements after T6g_hybrid_nan0 (+1.25pp) was identified.
Goal: keep T6g's sector fairness while recovering the 0.27pp gap vs
baseline_nan0 (+1.52pp), OR find new alpha.

Five directions:
  H1. min_axis_coverage filter (require >= K axes non-NaN; drop rest)
  H2. NaN penalty intensity sweep (fill 0 / 0.1 / 0.2 / 0.3)
  H3. Indicator-level NaN fill (fill within axis BEFORE mean)
  H4. T6g + T2 Beneish-lite restricted to DEFAULT sector
  H5. Tighter top tier (top 5% instead of 10%)
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"

WEIGHTS = {"quality":0.18,"stability":0.18,"cash":0.18,"shareholder":0.15,
           "growth":0.13,"health":0.08,"valuation":0.10}
TIERS_DEFAULT = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]
TIERS_TIGHT   = [("A",0.95,1.00),("B",0.75,0.95),("C",0.40,0.75),("D",0.15,0.40),("E",0.00,0.15)]

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
    t.ICB_Code, t.profit_3M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2014-01-01" AND f.quarter LIKE "%Q4"
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching ..."); df = bq_query(SQL); print(f"  {len(df):,} Q4 rows")

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

# Indicators
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
    df["NP_CV"]=np.where(np_n>=6,  np_std/np.maximum(np.abs(np_mean), 1e6), np.nan).clip(max=10)
    df["Rev_CV"]=np.where(rev_n>=6, rev_std/np.maximum(np.abs(rev_mean),1e6), np.nan).clip(max=10)
rev_p0=df["Revenue_P0"].values; rev_p7=df["Revenue_P7"].values
mask=(rev_p0>0)&(rev_p7>0)
df["LT_CAGR"] = np.where(mask, (rev_p0/rev_p7)**(4/7)-1, np.nan).clip(min=-0.95, max=5.0)
df["ICB_Code"] = df["ICB_Code"].fillna("UNK")
for col in ["PE","PB","PCF"]:
    grp = df.groupby(["quarter","ICB_Code"])[col]
    med=grp.transform("median"); sd=grp.transform("std")
    z_ind = (df[col]-med)/sd.replace(0,np.nan)
    z_global = df.groupby("quarter")[col].transform(lambda x: (x-x.median())/x.std())
    df[f"{col}_ind_z"] = z_ind.fillna(z_global)

# Beneish-lite indicators (for H4)
df["DSO_delta"]   = df["DSO_P0"] - df["DSO_P4"]
df["FinLev_delta"]= df["FinLev_P0"] - df["FinLev_P4"]
df["GPM_delta_abs"] = df["GPM_P4"] - df["GPM_P0"]
df["AT_delta"]    = df["AssetTurn_P4"] - df["AssetTurn_P0"]

INV=["Debt_Eq_P0","PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","NP_CV","Rev_CV",
     "DSO_delta","FinLev_delta","GPM_delta_abs","AT_delta"]
for c in INV: df[c] = -df[c]

AXIS = {
    "quality":     ["ROIC5Y","ROE_Min5Y","FSCORE"],
    "stability":   ["NP_CV","Rev_CV","LT_CAGR"],
    "cash":        ["CF_OA_5Y","CFOA_NP"],
    "shareholder": ["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
    "growth":      ["NP_R","Revenue_YoY_P0","GPM_change","NP_peak_ratio","Rev_peak_ratio"],
    "health":      ["Debt_Eq_P0","IntCov_P0","CashR_P0"],
    "valuation":   ["PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","growth_yield"],
}
# health-with-beneish (for H4)
AXIS_H4 = dict(AXIS)
AXIS_H4["health"] = AXIS["health"] + ["DSO_delta","FinLev_delta","GPM_delta_abs","AT_delta"]

# Rank universe + rank sector for both axis schemas
def make_ranks(axis_schema):
    all_cols = set()
    for cs in axis_schema.values(): all_cols.update(cs)
    uni = {}
    sec_r = {}
    for c in all_cols:
        u = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
        s = df.groupby(["quarter","sector"])[c].rank(pct=True, na_option="keep")
        df[f"_u_{c}"] = u; df[f"_s_{c}"] = s
    return all_cols

print("Computing ranks (default + H4 axis schemas) ...")
all_cols_h4 = make_ranks(AXIS_H4)  # also covers AXIS

def axis_scores(rank_prefix, axis_schema, nan_fill=None, indicator_nan_fill=None):
    """Compute axis score with two NaN strategies:
       - indicator_nan_fill: fill NaN at indicator-level (within axis) BEFORE mean
       - nan_fill: fill NaN at axis-level AFTER mean
       (Use exactly one — set the other to None)
    """
    out = {}
    for a, cs in axis_schema.items():
        rcols = [f"{rank_prefix}_{c}" for c in cs]
        sub = df[rcols].copy()
        if indicator_nan_fill is not None:
            sub = sub.fillna(indicator_nan_fill)
        s = sub.mean(axis=1, skipna=True)
        if nan_fill is not None:
            s = s.fillna(nan_fill)
        out[a] = s
    return out

def assign_tier_fn(tiers):
    def f(p):
        for n, lo, hi in tiers:
            if lo <= p <= hi: return n
        return "E"
    return f

def score_tier(ax_score, group_cols, mode_hybrid=False, min_coverage=None, axis_schema=None, tiers=TIERS_DEFAULT):
    """If mode_hybrid: use universe for DEFAULT rows, sector for others (assumes ax_score is per-mode dict pair)"""
    if mode_hybrid:
        ax_uni, ax_sec = ax_score
        is_default = (df["sector"] == "DEFAULT").values
        total = np.zeros(len(df))
        nan_per_axis = []
        for a in WEIGHTS:
            s_u = ax_uni[a].values; s_s = ax_sec[a].values
            s = np.where(is_default, s_u, s_s)
            nan_per_axis.append(np.isnan(s))
            total += np.nan_to_num(s, nan=0.0) * WEIGHTS[a]
        nan_per_axis = np.array(nan_per_axis)
    else:
        total = np.zeros(len(df))
        nan_per_axis = []
        for a in WEIGHTS:
            s = ax_score[a].values
            nan_per_axis.append(np.isnan(s))
            total += np.nan_to_num(s, nan=0.0) * WEIGHTS[a]
        nan_per_axis = np.array(nan_per_axis)

    tmp = df.copy()
    tmp["total_score"] = total
    # min_coverage: require at least K axes non-NaN (across rows)
    if min_coverage is not None:
        cov = (~nan_per_axis).sum(axis=0)
        tmp.loc[cov < min_coverage, "total_score"] = np.nan
    tmp = tmp.dropna(subset=["total_score"])
    # tier within group_cols
    if isinstance(group_cols, list) and len(group_cols) == 2:
        tmp["score_pct"] = tmp.groupby(group_cols)["total_score"].rank(pct=True)
    elif group_cols == "hybrid":
        # non-fin universe-rank within quarter, fin sector-rank within (quarter, sector)
        is_def = tmp["sector"] == "DEFAULT"
        tmp["score_pct"] = np.nan
        tmp.loc[is_def, "score_pct"] = tmp[is_def].groupby("quarter")["total_score"].rank(pct=True)
        tmp.loc[~is_def, "score_pct"] = tmp[~is_def].groupby(["quarter","sector"])["total_score"].rank(pct=True)
    else:
        tmp["score_pct"] = tmp.groupby(group_cols)["total_score"].rank(pct=True)
    tmp["tier"] = tmp["score_pct"].apply(assign_tier_fn(tiers))
    return tmp

def report(label, tmp, base_spread=None):
    v = tmp.dropna(subset=["profit_3M"])
    rows=[]
    for tier in ["A","B","C","D","E"]:
        g = v[v["tier"]==tier]["profit_3M"]
        if len(g):
            rows.append({"tier":tier,"N":len(g),"median":g.median(),
                         "mean":g.mean(),"WR":(g>0).mean()*100})
    out = pd.DataFrame(rows)
    meds = out["median"].values
    spread = meds[0]-meds[-1] if len(meds)==5 else np.nan
    inv = sum(1 for i in range(len(meds)-1) if meds[i]<meds[i+1])
    delta = "" if base_spread is None else f" (Δ {spread-base_spread:+.2f})"
    print(f"\n>>> {label}  spread={spread:.2f}pp{delta}, inv={inv}, N(A)={out[out.tier=='A'].N.iloc[0] if (out.tier=='A').any() else 0}")
    print(out.to_string(index=False, float_format="%.2f"))
    return spread, out

# ─── Setup baseline axis scores using AXIS (no Beneish) ────────────────────
ax_uni_base = axis_scores("_u", AXIS, nan_fill=None)
ax_uni_nan0 = axis_scores("_u", AXIS, nan_fill=0.0)
ax_sec_base = axis_scores("_s", AXIS, nan_fill=None)
ax_sec_nan0 = axis_scores("_s", AXIS, nan_fill=0.0)

# Reference 1: baseline
print("\n" + "="*70); print("REFERENCES"); print("="*70)
tmp_base = score_tier(ax_uni_base, "quarter")
base_spread, _ = report("baseline", tmp_base)

# Reference 2: T6g_hybrid_nan0 (current best with sector fairness)
tmp_t6g = score_tier((ax_uni_nan0, ax_sec_nan0), group_cols="hybrid", mode_hybrid=True)
report("T6g_hybrid_nan0 (REF)", tmp_t6g, base_spread)

# Reference 3: baseline_nan0
tmp_bn0 = score_tier(ax_uni_nan0, "quarter")
report("baseline_nan0 (REF)", tmp_bn0, base_spread)

# ─── H1: min_axis_coverage ────────────────────────────────────────────────
print("\n" + "="*70); print("H1: min_axis_coverage filter"); print("="*70)
for K in [5, 6, 7]:
    tmp = score_tier((ax_uni_nan0, ax_sec_nan0), "hybrid", mode_hybrid=True, min_coverage=K)
    report(f"H1_hybrid_minK={K}", tmp, base_spread)

# ─── H2: NaN penalty intensity (axis-level) ────────────────────────────────
print("\n" + "="*70); print("H2: axis-level NaN fill intensity"); print("="*70)
for fill in [0.0, 0.1, 0.2, 0.3]:
    ax_u = axis_scores("_u", AXIS, nan_fill=fill)
    ax_s = axis_scores("_s", AXIS, nan_fill=fill)
    tmp = score_tier((ax_u, ax_s), "hybrid", mode_hybrid=True)
    report(f"H2_hybrid_fill={fill:.1f}", tmp, base_spread)

# ─── H3: Indicator-level NaN fill (within axis BEFORE mean) ───────────────
# Test: fill indicator rank NaN with various values, then compute axis mean normally
print("\n" + "="*70); print("H3: indicator-level NaN fill (within axis)"); print("="*70)
for fill in [0.0, 0.3, 0.5]:
    ax_u = axis_scores("_u", AXIS, indicator_nan_fill=fill)  # fill indicator, NOT axis
    ax_s = axis_scores("_s", AXIS, indicator_nan_fill=fill)
    tmp = score_tier((ax_u, ax_s), "hybrid", mode_hybrid=True)
    report(f"H3_hybrid_indfill={fill:.1f}", tmp, base_spread)

# ─── H4: T6g + Beneish-lite restricted to DEFAULT sector ──────────────────
print("\n" + "="*70); print("H4: T6g + Beneish only for DEFAULT sector"); print("="*70)
# For DEFAULT rows: use AXIS_H4 (health with Beneish); for financials: use AXIS
def axis_scores_per_sector(rank_prefix):
    """DEFAULT rows use AXIS_H4 health; non-DEFAULT use AXIS health."""
    out = {}
    is_default = (df["sector"] == "DEFAULT").values
    for a in WEIGHTS:
        cs_def = AXIS_H4[a]; cs_oth = AXIS[a]
        # Compute both axis means
        rcols_def = [f"{rank_prefix}_{c}" for c in cs_def]
        rcols_oth = [f"{rank_prefix}_{c}" for c in cs_oth]
        s_def = df[rcols_def].mean(axis=1, skipna=True).fillna(0).values
        s_oth = df[rcols_oth].mean(axis=1, skipna=True).fillna(0).values
        out[a] = pd.Series(np.where(is_default, s_def, s_oth), index=df.index)
    return out

ax_u_h4 = axis_scores_per_sector("_u")
ax_s_h4 = axis_scores_per_sector("_s")
tmp = score_tier((ax_u_h4, ax_s_h4), "hybrid", mode_hybrid=True)
report("H4_hybrid_beneish_on_DEFAULT", tmp, base_spread)

# ─── H5: Tighter top tier (top 5%) ─────────────────────────────────────────
print("\n" + "="*70); print("H5: tighter A tier (top 5%)"); print("="*70)
tmp = score_tier((ax_uni_nan0, ax_sec_nan0), "hybrid", mode_hybrid=True, tiers=TIERS_TIGHT)
report("H5_hybrid_top5pct", tmp, base_spread)

print("\n" + "="*70); print("DONE"); print("="*70)
