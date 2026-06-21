#!/usr/bin/env python3
"""
test_fa_t6_combo.py
===================
Combine the two real findings from finetune:
  H3 = indicator-level NaN fill 0 (boosts A tier median)
  H4 = T6g + Beneish-lite restricted to DEFAULT sector (boosts spread)

Variants tested:
  baseline_drop          - canonical drop-NaN baseline (for true reference)
  T6g_hybrid_nan0        - current best with sector fairness
  H3_only                - hybrid + indicator-level NaN fill
  H4_only                - hybrid + Beneish on DEFAULT
  H3+H4_combo            - both combined
  H3+H4+sector_strict    - both + drop rows with <5 axes coverage

Also: test on ALL quarters (not just Q4) for robustness check.
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
TIERS = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]

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

# Pull both Q4 and all quarters in one go; filter in Python.
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
  WHERE f.time >= "2014-01-01"
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching ALL quarters ...")
df_all = bq_query(SQL); print(f"  {len(df_all):,} rows (all quarters)")

def sector_bucket(icb):
    if pd.isna(icb): return "DEFAULT"
    try: code = int(float(icb))
    except: return "DEFAULT"
    if code == 8355: return "BANK"
    if code in (8633, 8637): return "REIT"
    if code == 8536: return "INSURANCE"
    if code in (8775, 8777): return "SECURITIES"
    return "DEFAULT"
df_all["sector"] = df_all["ICB_Code"].apply(sector_bucket)

def prep_indicators(df):
    df = df.copy()
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
        df["NP_CV"]=np.where(np_n>=6,  np_std/np.maximum(np.abs(np_mean), 1e6), np.nan)
        df["Rev_CV"]=np.where(rev_n>=6, rev_std/np.maximum(np.abs(rev_mean),1e6), np.nan)
        df["NP_CV"]=df["NP_CV"].clip(upper=10); df["Rev_CV"]=df["Rev_CV"].clip(upper=10)
    rev_p0=df["Revenue_P0"].values; rev_p7=df["Revenue_P7"].values
    mask=(rev_p0>0)&(rev_p7>0)
    df["LT_CAGR"] = np.where(mask, (rev_p0/rev_p7)**(4/7)-1, np.nan)
    df["LT_CAGR"] = df["LT_CAGR"].clip(-0.95, 5.0)
    df["ICB_Code"] = df["ICB_Code"].fillna("UNK")
    for col in ["PE","PB","PCF"]:
        grp = df.groupby(["quarter","ICB_Code"])[col]
        med=grp.transform("median"); sd=grp.transform("std")
        z_ind = (df[col]-med)/sd.replace(0,np.nan)
        z_global = df.groupby("quarter")[col].transform(lambda x: (x-x.median())/x.std())
        df[f"{col}_ind_z"] = z_ind.fillna(z_global)
    df["DSO_delta"]    = df["DSO_P0"] - df["DSO_P4"]
    df["FinLev_delta"] = df["FinLev_P0"] - df["FinLev_P4"]
    df["GPM_delta_abs"]= df["GPM_P4"] - df["GPM_P0"]
    df["AT_delta"]     = df["AssetTurn_P4"] - df["AssetTurn_P0"]
    INV=["Debt_Eq_P0","PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","NP_CV","Rev_CV",
         "DSO_delta","FinLev_delta","GPM_delta_abs","AT_delta"]
    for c in INV: df[c] = -df[c]
    return df

AXIS_BASE = {
    "quality":     ["ROIC5Y","ROE_Min5Y","FSCORE"],
    "stability":   ["NP_CV","Rev_CV","LT_CAGR"],
    "cash":        ["CF_OA_5Y","CFOA_NP"],
    "shareholder": ["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
    "growth":      ["NP_R","Revenue_YoY_P0","GPM_change","NP_peak_ratio","Rev_peak_ratio"],
    "health":      ["Debt_Eq_P0","IntCov_P0","CashR_P0"],
    "valuation":   ["PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","growth_yield"],
}
AXIS_H4 = dict(AXIS_BASE)
AXIS_H4["health"] = AXIS_BASE["health"] + ["DSO_delta","FinLev_delta","GPM_delta_abs","AT_delta"]

def assign_tier(p):
    for n, lo, hi in TIERS:
        if lo <= p <= hi: return n
    return "E"

def compute_ranks(df, axis_schema):
    all_cols = set()
    for cs in axis_schema.values(): all_cols.update(cs)
    for c in all_cols:
        df[f"_u_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
        df[f"_s_{c}"] = df.groupby(["quarter","sector"])[c].rank(pct=True, na_option="keep")
    return df

def axis_score(df, axis_schema, rank_prefix, indicator_nan_fill=None, axis_nan_fill=None):
    out = {}
    for a, cs in axis_schema.items():
        rcols = [f"{rank_prefix}_{c}" for c in cs]
        sub = df[rcols].copy()
        if indicator_nan_fill is not None:
            sub = sub.fillna(indicator_nan_fill)
        s = sub.mean(axis=1, skipna=True)
        if axis_nan_fill is not None:
            s = s.fillna(axis_nan_fill)
        out[a] = s
    return out

def score_variant(df, label, mode, axis_schema_default, axis_schema_fin,
                  indicator_nan_fill=None, axis_nan_fill=None, min_coverage=None):
    """
    mode: 'universe' (rank by quarter only), 'sector' (rank by quarter+sector),
          'hybrid' (universe for DEFAULT, sector for fin)
    axis_schema_default / axis_schema_fin: separate axis sets per sector group
    """
    is_default = (df["sector"] == "DEFAULT").values

    ax_u_def = axis_score(df, axis_schema_default, "_u", indicator_nan_fill, axis_nan_fill)
    ax_u_fin = axis_score(df, axis_schema_fin,     "_u", indicator_nan_fill, axis_nan_fill)
    ax_s_def = axis_score(df, axis_schema_default, "_s", indicator_nan_fill, axis_nan_fill)
    ax_s_fin = axis_score(df, axis_schema_fin,     "_s", indicator_nan_fill, axis_nan_fill)

    # Pick scores per row based on sector
    if mode == "universe":
        ax = {a: pd.Series(np.where(is_default, ax_u_def[a].values, ax_u_fin[a].values), index=df.index)
              for a in WEIGHTS}
    elif mode == "sector":
        ax = {a: pd.Series(np.where(is_default, ax_s_def[a].values, ax_s_fin[a].values), index=df.index)
              for a in WEIGHTS}
    elif mode == "hybrid":
        ax = {a: pd.Series(np.where(is_default, ax_u_def[a].values, ax_s_fin[a].values), index=df.index)
              for a in WEIGHTS}
    else:
        raise ValueError(mode)

    # Compose
    total = np.zeros(len(df))
    nan_mat = []
    for a in WEIGHTS:
        s = ax[a].values
        nan_mat.append(np.isnan(s))
        total += np.nan_to_num(s, nan=0.0) * WEIGHTS[a]
    nan_mat = np.array(nan_mat)

    tmp = df.copy(); tmp["total_score"] = total
    if min_coverage is not None:
        cov = (~nan_mat).sum(axis=0)
        tmp.loc[cov < min_coverage, "total_score"] = np.nan
    tmp = tmp.dropna(subset=["total_score"])

    if mode == "hybrid":
        is_def = tmp["sector"] == "DEFAULT"
        tmp["score_pct"] = np.nan
        tmp.loc[is_def, "score_pct"] = tmp[is_def].groupby("quarter")["total_score"].rank(pct=True)
        tmp.loc[~is_def, "score_pct"] = tmp[~is_def].groupby(["quarter","sector"])["total_score"].rank(pct=True)
    elif mode == "sector":
        tmp["score_pct"] = tmp.groupby(["quarter","sector"])["total_score"].rank(pct=True)
    else:
        tmp["score_pct"] = tmp.groupby("quarter")["total_score"].rank(pct=True)
    tmp["tier"] = tmp["score_pct"].apply(assign_tier)
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
    a_med  = out[out.tier=="A"]["median"].iloc[0] if (out.tier=="A").any() else np.nan
    a_wr   = out[out.tier=="A"]["WR"].iloc[0] if (out.tier=="A").any() else np.nan
    a_n    = int(out[out.tier=="A"]["N"].iloc[0]) if (out.tier=="A").any() else 0
    inv = sum(1 for i in range(len(meds)-1) if meds[i]<meds[i+1])
    delta = "" if base_spread is None else f" (Δ {spread-base_spread:+.2f})"
    print(f"\n>>> {label}  spread={spread:.2f}pp{delta}  A: N={a_n} med={a_med:.2f}% WR={a_wr:.1f}%  inv={inv}")
    print(out.to_string(index=False, float_format="%.2f"))
    return spread, a_med, a_wr

# Filter to Q4
df = df_all[df_all["quarter"].str.endswith("Q4")].copy().reset_index(drop=True)
df = prep_indicators(df)
print(f"\nQ4 subset: {len(df):,} rows")
print("Computing ranks ...")
df = compute_ranks(df, AXIS_H4)  # ranks for all cols incl. Beneish

# ─── A) True baseline: drop rows with full-NaN axis (no NaN fill) ──────────
# Use axis_score with no fill, then drop tmp where total_score is NaN due to all-NaN axes
print("\n" + "="*70); print("Q4 RESULTS"); print("="*70)
ax = axis_score(df, AXIS_BASE, "_u", indicator_nan_fill=None, axis_nan_fill=None)
total_b = np.zeros(len(df)); any_nan = np.zeros(len(df), dtype=bool)
for a in WEIGHTS:
    s = ax[a].values
    any_nan |= np.isnan(s)
    total_b += np.nan_to_num(s, nan=0.0) * WEIGHTS[a]
tmp_b = df.copy(); tmp_b["total_score"] = np.where(any_nan, np.nan, total_b)
tmp_b = tmp_b.dropna(subset=["total_score"])
tmp_b["score_pct"] = tmp_b.groupby("quarter")["total_score"].rank(pct=True)
tmp_b["tier"] = tmp_b["score_pct"].apply(assign_tier)
base_spread, _, _ = report("A_baseline_drop", tmp_b)

# ─── B) T6g_hybrid_nan0 ───────────────────────────────────────────────────
tmp = score_variant(df, "T6g_hybrid_nan0", mode="hybrid",
                    axis_schema_default=AXIS_BASE, axis_schema_fin=AXIS_BASE,
                    indicator_nan_fill=None, axis_nan_fill=0.0)
report("B_T6g_hybrid_nan0", tmp, base_spread)

# ─── C) H3 only: indicator-level NaN fill 0 (hybrid) ──────────────────────
tmp = score_variant(df, "H3_only", mode="hybrid",
                    axis_schema_default=AXIS_BASE, axis_schema_fin=AXIS_BASE,
                    indicator_nan_fill=0.0, axis_nan_fill=None)
report("C_H3_only_indfill0", tmp, base_spread)

# ─── D) H4 only: T6g with Beneish on DEFAULT ──────────────────────────────
tmp = score_variant(df, "H4_only", mode="hybrid",
                    axis_schema_default=AXIS_H4, axis_schema_fin=AXIS_BASE,
                    indicator_nan_fill=None, axis_nan_fill=0.0)
report("D_H4_only_beneish_default", tmp, base_spread)

# ─── E) H3 + H4 combined ──────────────────────────────────────────────────
tmp = score_variant(df, "H3+H4", mode="hybrid",
                    axis_schema_default=AXIS_H4, axis_schema_fin=AXIS_BASE,
                    indicator_nan_fill=0.0, axis_nan_fill=None)
report("E_H3+H4_combo", tmp, base_spread)

# ─── F) H3 + H4 + min_coverage=5 ──────────────────────────────────────────
tmp = score_variant(df, "H3+H4_minK5", mode="hybrid",
                    axis_schema_default=AXIS_H4, axis_schema_fin=AXIS_BASE,
                    indicator_nan_fill=0.0, axis_nan_fill=None, min_coverage=5)
report("F_H3+H4_minK=5", tmp, base_spread)

# ─── ROBUSTNESS: rerun B/C/D/E on ALL quarters ────────────────────────────
print("\n" + "="*70); print("ALL-QUARTERS ROBUSTNESS"); print("="*70)
dfa = prep_indicators(df_all.copy())
print(f"All-quarters: {len(dfa):,} rows")
dfa = compute_ranks(dfa, AXIS_H4)

# Re-bind ax_score functions to the all-quarters frame by passing dfa
# Recreate the global `df` reference inside score_variant — refactor by inline
def score_variant_on(df_local, **kw):
    return score_variant(df_local, **kw)

# baseline on all quarters
ax = axis_score(dfa, AXIS_BASE, "_u", indicator_nan_fill=None, axis_nan_fill=None)
total_b = np.zeros(len(dfa)); any_nan = np.zeros(len(dfa), dtype=bool)
for a in WEIGHTS:
    s = ax[a].values
    any_nan |= np.isnan(s)
    total_b += np.nan_to_num(s, nan=0.0) * WEIGHTS[a]
tmp_b = dfa.copy(); tmp_b["total_score"] = np.where(any_nan, np.nan, total_b)
tmp_b = tmp_b.dropna(subset=["total_score"])
tmp_b["score_pct"] = tmp_b.groupby("quarter")["total_score"].rank(pct=True)
tmp_b["tier"] = tmp_b["score_pct"].apply(assign_tier)
all_base_spread, _, _ = report("AQ_baseline_drop", tmp_b)

tmp = score_variant(dfa, "T6g_hybrid_nan0", mode="hybrid",
                    axis_schema_default=AXIS_BASE, axis_schema_fin=AXIS_BASE,
                    indicator_nan_fill=None, axis_nan_fill=0.0)
report("AQ_T6g_hybrid_nan0", tmp, all_base_spread)

tmp = score_variant(dfa, "H3+H4", mode="hybrid",
                    axis_schema_default=AXIS_H4, axis_schema_fin=AXIS_BASE,
                    indicator_nan_fill=0.0, axis_nan_fill=None)
report("AQ_H3+H4_combo", tmp, all_base_spread)
