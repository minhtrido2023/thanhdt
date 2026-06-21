#!/usr/bin/env python3
"""
test_fa_t6_sectorrank.py
========================
Test sector-RELATIVE ranking (rank within sector × quarter) as the
T6 alternative, since industry-weight reshuffling didn't help.

Idea: instead of universe-wide ranking, rank percentile within each
(quarter, sector). Then assign tier within each sector independently.

Variants:
  baseline          - universe ranking (reference)
  T6e_sectorrank    - per (quarter, sector) ranking, all sectors
  T6f_exclude_finRE - drop REIT+SEC from universe (they're noisy)
  T6g_hybrid        - non-fin uses universe rank; financials use sector rank

Also test NaN=0 penalty separately:
  baseline_nan0     - universe + NaN=0 (the +1.52pp gain we discovered)
  T6e_nan0          - sector rank + NaN=0
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

print("Fetching ...")
df = bq_query(SQL); print(f"  {len(df):,} Q4 rows")

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

# ─── Standard indicator transforms ─────────────────────────────────────────
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
INV=["Debt_Eq_P0","PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","NP_CV","Rev_CV"]
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
all_cols = set()
for cs in AXIS.values(): all_cols.update(cs)

# ─── Rank computation helpers ──────────────────────────────────────────────
def rank_universe():
    """Per-quarter pct rank (universe-wide). Returns dict of axis→Series."""
    for c in all_cols:
        df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
    return {a: df[[f"r_{c}" for c in cs]].mean(axis=1, skipna=True) for a, cs in AXIS.items()}

def rank_sector():
    """Per (quarter, sector) pct rank."""
    for c in all_cols:
        df[f"rs_{c}"] = df.groupby(["quarter","sector"])[c].rank(pct=True, na_option="keep")
    return {a: df[[f"rs_{c}" for c in cs]].mean(axis=1, skipna=True) for a, cs in AXIS.items()}

def assign_tier(p):
    for n, lo, hi in TIERS:
        if lo <= p <= hi: return n
    return "E"

def score_and_tier(axis_scores, group_cols, nan_fill_zero, mask=None):
    """Compute weighted total, assign tier within group_cols."""
    if nan_fill_zero:
        scored = [axis_scores[a].fillna(0).values for a in WEIGHTS]
    else:
        scored = [axis_scores[a].values for a in WEIGHTS]
    weights = np.array([WEIGHTS[a] for a in WEIGHTS])
    total = sum(s * w for s, w in zip(scored, weights))
    tmp = df.copy(); tmp["total_score"] = total
    if not nan_fill_zero:
        full_nan = pd.concat([axis_scores[a].isna() for a in WEIGHTS], axis=1).any(axis=1)
        tmp.loc[full_nan, "total_score"] = np.nan
    if mask is not None:
        tmp.loc[~mask, "total_score"] = np.nan
    tmp = tmp.dropna(subset=["total_score"])
    tmp["score_pct"] = tmp.groupby(group_cols)["total_score"].rank(pct=True)
    tmp["tier"] = tmp["score_pct"].apply(assign_tier)
    return tmp

def report(label, tmp, base_spread=None):
    v = tmp.dropna(subset=["profit_3M"])
    rows=[]
    for tier in ["A","B","C","D","E"]:
        g = v[v["tier"]==tier]["profit_3M"]
        if len(g):
            rows.append({"variant":label,"tier":tier,"N":len(g),
                         "median":g.median(),"mean":g.mean(),"WR":(g>0).mean()*100})
    out = pd.DataFrame(rows)
    meds = out["median"].values
    spread = meds[0]-meds[-1] if len(meds)==5 else np.nan
    inv = sum(1 for i in range(len(meds)-1) if meds[i]<meds[i+1])
    delta = "" if base_spread is None else f" (Δ {spread-base_spread:+.2f})"
    print("\n"+"="*70); print(f"{label}  spread={spread:.2f}pp{delta}, inv={inv}"); print("="*70)
    print(out.to_string(index=False, float_format="%.2f"))
    return out, spread

# ─── Build universe ranks and sector ranks ─────────────────────────────────
print("Computing ranks ...")
ax_uni = rank_universe()
ax_sec = rank_sector()

# ─── 1. baseline ───────────────────────────────────────────────────────────
tmp_base = score_and_tier(ax_uni, "quarter", nan_fill_zero=False)
_, base_spread = report("baseline", tmp_base)

# ─── 2. baseline_nan0 ──────────────────────────────────────────────────────
tmp_b0 = score_and_tier(ax_uni, "quarter", nan_fill_zero=True)
report("baseline_nan0", tmp_b0, base_spread)

# ─── 3. T6e: sector-relative rank, tier within sector × quarter ────────────
tmp_e = score_and_tier(ax_sec, ["quarter","sector"], nan_fill_zero=False)
report("T6e_sectorrank", tmp_e, base_spread)

# ─── 4. T6e + nan0 ─────────────────────────────────────────────────────────
tmp_e0 = score_and_tier(ax_sec, ["quarter","sector"], nan_fill_zero=True)
report("T6e_sectorrank_nan0", tmp_e0, base_spread)

# ─── 5. T6f: exclude REIT + SECURITIES from universe ──────────────────────
mask_keep = ~df["sector"].isin(["REIT","SECURITIES"])
tmp_f = score_and_tier(ax_uni, "quarter", nan_fill_zero=False, mask=mask_keep)
report("T6f_exclude_REIT_SEC", tmp_f, base_spread)

# ─── 6. T6f + nan0 ─────────────────────────────────────────────────────────
tmp_f0 = score_and_tier(ax_uni, "quarter", nan_fill_zero=True, mask=mask_keep)
report("T6f_exclude_nan0", tmp_f0, base_spread)

# ─── 7. T6g: hybrid — non-fin universe rank; fin sector rank ───────────────
# Use universe rank for DEFAULT rows, sector rank for non-DEFAULT
is_default = (df["sector"] == "DEFAULT")
hybrid = {}
for a in WEIGHTS:
    s = np.where(is_default.values, ax_uni[a].values, ax_sec[a].values)
    hybrid[a] = pd.Series(s, index=df.index)
# For tiering we need a unified pct — rank globally within quarter for non-fin, within sector for fin
tmp_g = score_and_tier(hybrid, "quarter", nan_fill_zero=False)
# Re-tier: non-fin gets universe pct within quarter; financials get separate pct within sector
tmp_g["score_pct"] = np.nan
mask_def = tmp_g["sector"] == "DEFAULT"
tmp_g.loc[mask_def, "score_pct"] = tmp_g[mask_def].groupby("quarter")["total_score"].rank(pct=True)
tmp_g.loc[~mask_def, "score_pct"] = tmp_g[~mask_def].groupby(["quarter","sector"])["total_score"].rank(pct=True)
tmp_g["tier"] = tmp_g["score_pct"].apply(assign_tier)
report("T6g_hybrid", tmp_g, base_spread)

# Same with NaN=0
hybrid_for_nan0 = {}
for a in WEIGHTS:
    s = np.where(is_default.values, ax_uni[a].fillna(0).values, ax_sec[a].fillna(0).values)
    hybrid_for_nan0[a] = pd.Series(s, index=df.index)
total = sum(hybrid_for_nan0[a].values * WEIGHTS[a] for a in WEIGHTS)
tmp_g0 = df.copy(); tmp_g0["total_score"] = total
tmp_g0["score_pct"] = np.nan
mask_def = tmp_g0["sector"] == "DEFAULT"
tmp_g0.loc[mask_def, "score_pct"] = tmp_g0[mask_def].groupby("quarter")["total_score"].rank(pct=True)
tmp_g0.loc[~mask_def, "score_pct"] = tmp_g0[~mask_def].groupby(["quarter","sector"])["total_score"].rank(pct=True)
tmp_g0["tier"] = tmp_g0["score_pct"].apply(assign_tier)
report("T6g_hybrid_nan0", tmp_g0, base_spread)

# ─── Sector drilldown for T6e_sectorrank_nan0 (likely best) ────────────────
print("\n" + "="*70); print("SECTOR DRILLDOWN: baseline vs T6e_sectorrank_nan0 vs T6g_hybrid_nan0"); print("="*70)
for sec in ["BANK","REIT","INSURANCE","SECURITIES","DEFAULT"]:
    print(f"\n--- {sec} ---")
    for label, tmp in [("baseline",tmp_base),("T6e_sec_nan0",tmp_e0),("T6g_hyb_nan0",tmp_g0)]:
        sub = tmp[tmp["sector"]==sec]
        if len(sub)==0: continue
        v = sub.dropna(subset=["profit_3M"])
        if len(v)==0: continue
        row = f"{label:18s} N={len(sub):4d}  "
        for tier in ["A","B","C","D","E"]:
            g = v[v["tier"]==tier]["profit_3M"]
            row += f"{tier}:{len(g):3d}({g.median():+5.1f}%)  " if len(g) else f"{tier}: 0          "
        print(row)
