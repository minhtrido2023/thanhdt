#!/usr/bin/env python3
"""
test_fa_ic_elite_persistence.py
================================
Three parallel FA-system explorations on v4 baseline (canonical):

  EXPLORATION 1: Information Coefficient per indicator
    - Spearman corr of indicator rank vs forward profit_3M
    - Identify which indicators add alpha vs which are noise
    - Could justify dropping weak indicators or reweighting axes

  EXPLORATION 2: Sub-segment elite A tier
    - Hiện A tier WR 65%, median 6.67%. Find condition X such that
      A + X has WR >= 75% (or median >= 10%)
    - Test 10+ candidate conditions

  EXPLORATION 3: Multi-quarter persistence
    - Score persistent_4Q = mean(score_pct over last 4 quarters)
    - Or filter: A tier only if A for 2+/3+ consecutive quarters
    - Compare to single-quarter A tier
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd
# scipy not installed → use pandas built-in spearman
def spearman_corr(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 2: return float("nan"), float("nan"), 0
    # Spearman = Pearson of ranks
    rho = s["x"].rank().corr(s["y"].rank(), method="pearson")
    n = len(s)
    # t-stat for Spearman approximation (valid for n>30)
    t = rho * np.sqrt(n-2) / np.sqrt(1 - rho**2) if abs(rho) < 1 else float("inf")
    # two-sided p approx via normal (n>30)
    from math import erfc, sqrt
    p = erfc(abs(t)/sqrt(2)) if not np.isinf(t) else 0.0
    return rho, t, p

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

print("Fetching Q4 data ..."); df = bq_query(SQL); print(f"  {len(df):,} rows")

# ─── Compute v4 baseline indicators ─────────────────────────────────────────
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
mask_lt=(rev_p0>0)&(rev_p7>0)
df["LT_CAGR"] = np.where(mask_lt, (rev_p0/rev_p7)**(4/7)-1, np.nan).clip(min=-0.95, max=5.0)
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
ALL_INDICATORS = []
for cs in AXIS.values(): ALL_INDICATORS.extend(cs)

# Compute universe-rank for all indicators
print("Computing ranks ...")
for c in ALL_INDICATORS:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

# Axis scores (v4 mean-of-ranks, drop NaN axes)
for axis, cs in AXIS.items():
    df[f"score_{axis}"] = df[[f"r_{c}" for c in cs]].mean(axis=1, skipna=True)

# Total score (v4 baseline, drop-NaN behavior)
score_cols = [f"score_{a}" for a in WEIGHTS]
w = np.array([WEIGHTS[a] for a in WEIGHTS])
df["total_score"] = (df[score_cols].values * w).sum(axis=1)
full_nan = df[score_cols].isna().any(axis=1)
df.loc[full_nan, "total_score"] = np.nan
df_clean = df.dropna(subset=["total_score"]).copy()
df_clean["score_pct"] = df_clean.groupby("quarter")["total_score"].rank(pct=True)
def tier_of(p):
    for n, lo, hi in TIERS:
        if lo <= p <= hi: return n
    return "E"
df_clean["tier"] = df_clean["score_pct"].apply(tier_of)
print(f"  {len(df_clean):,} rows with full axis coverage (v4 baseline universe)")

# ═══════════════════════════════════════════════════════════════════════════
# EXPLORATION 1: Information Coefficient per indicator
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("EXPLORATION 1: Information Coefficient (Spearman) per indicator"); print("="*80)
v = df_clean.dropna(subset=["profit_3M"])
print(f"Sample N = {len(v):,}")
print(f"\n{'Indicator':<22}{'Axis':<13}{'IC':>8}{'t-stat':>9}{'p-val':>9}  Interpretation")
print("-"*80)

axis_of = {ind: ax for ax, cs in AXIS.items() for ind in cs}
ic_results = []
for ind in ALL_INDICATORS:
    rcol = f"r_{ind}"
    sub = v[[rcol, "profit_3M"]].dropna()
    if len(sub) < 100: continue
    rho, t_stat, p = spearman_corr(sub[rcol], sub["profit_3M"])
    n = len(sub)
    interp = ("STRONG" if abs(rho) > 0.10 else "weak" if abs(rho) > 0.05 else "noise")
    sign = "+" if rho > 0 else "-"
    ic_results.append({"indicator": ind, "axis": axis_of[ind], "IC": rho, "t": t_stat, "p": p, "interp": interp, "N": n})
    print(f"{ind:<22}{axis_of[ind]:<13}{rho:+8.4f}{t_stat:>+9.2f}{p:>9.4f}  {sign} {interp}")

ic_df = pd.DataFrame(ic_results).sort_values("IC", ascending=False)
print(f"\n  Top 5 strongest positive predictors:")
print(ic_df.head(5)[["indicator","axis","IC","t","interp"]].to_string(index=False, float_format="%.3f"))
print(f"\n  Top 5 strongest negative predictors (these are already INV-flipped, so + sign = good):")
print(ic_df.tail(5)[["indicator","axis","IC","t","interp"]].to_string(index=False, float_format="%.3f"))

# IC by axis (avg IC within axis)
print(f"\n  Average IC by axis:")
ic_by_axis = ic_df.groupby("axis")["IC"].agg(["mean","std","count"]).sort_values("mean", ascending=False)
print(ic_by_axis.to_string(float_format="%.4f"))

# Axis-level IC: rank by axis score directly
print(f"\n  AXIS-LEVEL IC (axis score vs profit_3M):")
for axis in WEIGHTS:
    sub = df_clean[[f"score_{axis}", "profit_3M"]].dropna()
    if len(sub) < 100: continue
    rho, t_stat, p = spearman_corr(sub[f"score_{axis}"], sub["profit_3M"])
    print(f"    {axis:<13}  IC={rho:+.4f}  t={t_stat:+.2f}  p={p:.4f}  current_weight={WEIGHTS[axis]:.2f}")

ic_df.to_csv("data/fa_ic_results.csv", index=False)
print("\n  Saved fa_ic_results.csv")

# ═══════════════════════════════════════════════════════════════════════════
# EXPLORATION 2: Sub-segment elite A tier
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("EXPLORATION 2: Sub-segment within A tier"); print("="*80)
A = df_clean[df_clean["tier"]=="A"].copy()
A_v = A.dropna(subset=["profit_3M"])
n_A = len(A_v)
med_A = A_v["profit_3M"].median()
wr_A  = (A_v["profit_3M"] > 0).mean() * 100
mean_A = A_v["profit_3M"].mean()
print(f"A tier baseline:  N={n_A}  median={med_A:.2f}%  mean={mean_A:.2f}%  WR={wr_A:.1f}%")

# Helper to compute axis-score quantiles globally
for axis in WEIGHTS:
    A_v[f"q_{axis}"] = pd.qcut(A_v[f"score_{axis}"], 4, labels=False, duplicates="drop")

candidates = [
    ("A + valuation top Q (top 25%)",        lambda d: d["score_valuation"] >= d["score_valuation"].quantile(0.75)),
    ("A + valuation top half",               lambda d: d["score_valuation"] >= d["score_valuation"].quantile(0.50)),
    ("A + valuation bottom Q (worst val)",   lambda d: d["score_valuation"] <  d["score_valuation"].quantile(0.25)),
    ("A + quality top Q",                    lambda d: d["score_quality"] >= d["score_quality"].quantile(0.75)),
    ("A + growth top Q",                     lambda d: d["score_growth"] >= d["score_growth"].quantile(0.75)),
    ("A + cash top Q",                       lambda d: d["score_cash"] >= d["score_cash"].quantile(0.75)),
    ("A + stability top Q (low NP_CV)",      lambda d: d["score_stability"] >= d["score_stability"].quantile(0.75)),
    ("A + FSCORE >= 8",                      lambda d: d["FSCORE"] >= 8),
    ("A + ROIC5Y top Q (>0.18 typically)",   lambda d: d["ROIC5Y"] >= d["ROIC5Y"].quantile(0.75)),
    ("A + NP_R > 0.20 (>20% YoY growth)",    lambda d: d["NP_R"] > 0.20),
    ("A + NP_R > 0",                         lambda d: d["NP_R"] > 0),
    ("A + NP_peak_ratio = 1 (at peak)",      lambda d: d["NP_peak_ratio"] >= 0.99),
    ("A + DY > 0.05 (5% dividend)",          lambda d: d["DY"] > 0.05),
    ("A + PE_self_z best Q (deep value)",    lambda d: d["PE_self_z"] >= d["PE_self_z"].quantile(0.75)),  # negated → high = cheap
    ("A + Quality top + Valuation top",      lambda d: (d["score_quality"]>=d["score_quality"].quantile(0.75)) & (d["score_valuation"]>=d["score_valuation"].quantile(0.75))),
    ("A + Quality top + Growth top",         lambda d: (d["score_quality"]>=d["score_quality"].quantile(0.75)) & (d["score_growth"]>=d["score_growth"].quantile(0.75))),
    ("A + Quality top + Stability top",      lambda d: (d["score_quality"]>=d["score_quality"].quantile(0.75)) & (d["score_stability"]>=d["score_stability"].quantile(0.75))),
    ("A + valuation top + growth top",       lambda d: (d["score_valuation"]>=d["score_valuation"].quantile(0.75)) & (d["score_growth"]>=d["score_growth"].quantile(0.75))),
    ("A + 5 axes >= median (well-rounded)",  lambda d: ((d["score_quality"]>=0.5).astype(int)+(d["score_growth"]>=0.5).astype(int)+(d["score_cash"]>=0.5).astype(int)+(d["score_valuation"]>=0.5).astype(int)+(d["score_stability"]>=0.5).astype(int)) >= 5),
    ("A + 6+ axes >= 0.6 (broad strong)",    lambda d: sum([(d[f"score_{ax}"]>=0.6).astype(int) for ax in WEIGHTS]) >= 6),
]

print(f"\n{'Condition':<45}{'N':>5}{'median':>9}{'mean':>9}{'WR%':>7}{'ΔWR':>7}{'Δmed':>8}")
print("-"*90)
elite_results = []
for name, cond_fn in candidates:
    mask = cond_fn(A_v)
    sub = A_v[mask]
    if len(sub) < 10: continue
    med = sub["profit_3M"].median()
    mean= sub["profit_3M"].mean()
    wr  = (sub["profit_3M"] > 0).mean() * 100
    d_wr  = wr - wr_A
    d_med = med - med_A
    marker = " 🟢" if (wr >= 75 and len(sub) >= 30) else (" 🔵" if wr >= 72 else "")
    print(f"{name:<45}{len(sub):>5}{med:>+8.2f}%{mean:>+8.2f}%{wr:>7.1f}{d_wr:>+7.1f}{d_med:>+7.2f}{marker}")
    elite_results.append({"condition": name, "N": len(sub), "median": med, "mean": mean, "WR": wr})

pd.DataFrame(elite_results).to_csv("data/fa_elite_a_subsegments.csv", index=False)
print(f"\n  Reference: A tier baseline WR={wr_A:.1f}%, median={med_A:.2f}%")
print("  Saved fa_elite_a_subsegments.csv")

# ═══════════════════════════════════════════════════════════════════════════
# EXPLORATION 3: Multi-quarter persistence
# ═══════════════════════════════════════════════════════════════════════════
# Need ALL quarters (not just Q4) for lookback. Re-pull.
print("\n" + "="*80); print("EXPLORATION 3: Multi-quarter persistence"); print("="*80)
print("Re-fetching ALL-quarters universe for lookback ...")
SQL_ALL = SQL.replace("AND f.quarter LIKE \"%Q4\"", "")
dfa = bq_query(SQL_ALL); print(f"  {len(dfa):,} all-quarter rows")

# Re-apply transforms on dfa
dfa["growth_yield"] = dfa["growth_yield"].clip(-0.15, 0.15)
_npa = dfa["NP_R"].fillna(0)
_mlta = np.where(_npa >= 0, 1.0, np.clip(1 + 2*_npa, 0.0, 1.0))
dfa["DY_adj"] = dfa["DY"]*_mlta; dfa["DY_sust"] = _mlta
np_a=dfa[NP_COLS].values.astype(float); rev_a=dfa[REV_COLS].values.astype(float)
np_na=np.sum(~np.isnan(np_a),axis=1); rev_na=np.sum(~np.isnan(rev_a),axis=1)
with np.errstate(divide="ignore",invalid="ignore"):
    np_ma=np.nanmean(np_a,axis=1); np_sa=np.nanstd(np_a,axis=1,ddof=1)
    rev_ma=np.nanmean(rev_a,axis=1); rev_sa=np.nanstd(rev_a,axis=1,ddof=1)
    dfa["NP_CV"]=np.where(np_na>=6, np_sa/np.maximum(np.abs(np_ma),1e6), np.nan).clip(max=10)
    dfa["Rev_CV"]=np.where(rev_na>=6, rev_sa/np.maximum(np.abs(rev_ma),1e6), np.nan).clip(max=10)
rva_p0=dfa["Revenue_P0"].values; rva_p7=dfa["Revenue_P7"].values
mask_lta=(rva_p0>0)&(rva_p7>0)
dfa["LT_CAGR"]=np.where(mask_lta,(rva_p0/rva_p7)**(4/7)-1,np.nan).clip(min=-0.95,max=5.0)
dfa["ICB_Code"]=dfa["ICB_Code"].fillna("UNK")
for col in ["PE","PB","PCF"]:
    grp = dfa.groupby(["quarter","ICB_Code"])[col]
    med=grp.transform("median"); sd=grp.transform("std")
    z_ind = (dfa[col]-med)/sd.replace(0,np.nan)
    z_global = dfa.groupby("quarter")[col].transform(lambda x: (x-x.median())/x.std())
    dfa[f"{col}_ind_z"] = z_ind.fillna(z_global)
for c in INV: dfa[c] = -dfa[c]
for c in ALL_INDICATORS:
    dfa[f"r_{c}"] = dfa.groupby("quarter")[c].rank(pct=True, na_option="keep")
for axis, cs in AXIS.items():
    dfa[f"score_{axis}"] = dfa[[f"r_{c}" for c in cs]].mean(axis=1, skipna=True)
dfa["total_score"] = (dfa[score_cols].values * w).sum(axis=1)
full_nan_a = dfa[score_cols].isna().any(axis=1)
dfa.loc[full_nan_a, "total_score"] = np.nan
dfa = dfa.dropna(subset=["total_score"]).copy()
dfa["score_pct"] = dfa.groupby("quarter")["total_score"].rank(pct=True)
dfa["tier"] = dfa["score_pct"].apply(tier_of)
dfa["time"] = pd.to_datetime(dfa["time"])
dfa = dfa.sort_values(["ticker","time"]).reset_index(drop=True)

# Build persistent score = mean(score_pct over last 4 quarters per ticker)
print("\nBuilding multi-quarter aggregates per ticker ...")
dfa["score_pct_T1"]  = dfa.groupby("ticker")["score_pct"].shift(1)
dfa["score_pct_T2"]  = dfa.groupby("ticker")["score_pct"].shift(2)
dfa["score_pct_T3"]  = dfa.groupby("ticker")["score_pct"].shift(3)
dfa["tier_T1"]       = dfa.groupby("ticker")["tier"].shift(1)
dfa["tier_T2"]       = dfa.groupby("ticker")["tier"].shift(2)
dfa["tier_T3"]       = dfa.groupby("ticker")["tier"].shift(3)
dfa["persistent_pct_4Q"] = dfa[["score_pct","score_pct_T1","score_pct_T2","score_pct_T3"]].mean(axis=1, skipna=True)
# Restrict to Q4 for comparison vs canonical Q4 baseline
q4 = dfa[dfa["quarter"].str.endswith("Q4")].copy()
print(f"  Q4 rows after persistence build: {len(q4):,}")

# Tier from persistent_pct
q4["persistent_tier"] = q4.groupby("quarter")["persistent_pct_4Q"].rank(pct=True).apply(tier_of)

# Filters: consecutive A
q4["A_streak"] = ((q4["tier"]=="A").astype(int) + (q4["tier_T1"]=="A").astype(int)
                  + (q4["tier_T2"]=="A").astype(int) + (q4["tier_T3"]=="A").astype(int))
q4["A_AB_streak"] = ((q4["tier"].isin(["A","B"])).astype(int)
                     + (q4["tier_T1"].isin(["A","B"])).astype(int)
                     + (q4["tier_T2"].isin(["A","B"])).astype(int)
                     + (q4["tier_T3"].isin(["A","B"])).astype(int))

# Validate each variant
def stats_for(label, sub):
    v = sub.dropna(subset=["profit_3M"])
    if len(v)==0: return None
    return {"variant":label,"N":len(v),
            "median":v["profit_3M"].median(),"mean":v["profit_3M"].mean(),
            "WR":(v["profit_3M"]>0).mean()*100}

variants = [
    ("Baseline A (current Q only)",           q4[q4["tier"]=="A"]),
    ("Persistent A (mean 4Q pct top 10%)",    q4[q4["persistent_tier"]=="A"]),
    ("A AND prev-Q A (2-quarter streak)",     q4[(q4["tier"]=="A") & (q4["tier_T1"]=="A")]),
    ("A AND 3-quarter A streak",              q4[q4["A_streak"]>=3]),
    ("A AND 4-quarter A streak",              q4[q4["A_streak"]==4]),
    ("A OR fallback (current OR T-1 A)",      q4[(q4["tier"]=="A") | (q4["tier_T1"]=="A")]),
    ("A AND prev-Q at least B (consistent)",  q4[(q4["tier"]=="A") & (q4["tier_T1"].isin(["A","B"]))]),
    ("Always A/B 4Q (very consistent)",       q4[q4["A_AB_streak"]==4]),
    ("Fresh A (current A, prev not A)",       q4[(q4["tier"]=="A") & (q4["tier_T1"]!="A") & (q4["tier_T1"].notna())]),
]
print(f"\n{'Variant':<48}{'N':>6}{'median':>10}{'mean':>10}{'WR%':>9}")
print("-"*85)
rows = []
for name, sub in variants:
    r = stats_for(name, sub)
    if r is None: continue
    marker = ""
    if r["WR"] >= 75: marker = " 🟢"
    elif r["WR"] >= 70: marker = " 🔵"
    print(f"{name:<48}{r['N']:>6}{r['median']:>+9.2f}%{r['mean']:>+9.2f}%{r['WR']:>+8.1f}%{marker}")
    rows.append(r)

pd.DataFrame(rows).to_csv("data/fa_persistence_results.csv", index=False)
print("\n  Saved fa_persistence_results.csv")

# Persistent tier ordering (compare to baseline tier)
print(f"\n  PERSISTENT-TIER ordering (4Q mean score percentile → tier):")
for tier in ["A","B","C","D","E"]:
    g = q4[q4["persistent_tier"]==tier].dropna(subset=["profit_3M"])
    if len(g):
        med = g["profit_3M"].median(); wr = (g["profit_3M"]>0).mean()*100
        print(f"    {tier}  N={len(g):4d}  median={med:+6.2f}%  WR={wr:5.1f}%")

print("\n" + "="*80); print("ALL 3 EXPLORATIONS DONE"); print("="*80)
