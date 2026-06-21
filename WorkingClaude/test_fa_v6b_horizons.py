#!/usr/bin/env python3
"""
test_fa_v6b_horizons.py
=======================
Test v6b composite (not just individual indicators) at longer horizons.

Forward horizons tested:
  profit_3M (canonical, full universe)
  O6M, O1Y, O2Y (from ticker_prune, ~2407 rows subset)

For each horizon: compute IC of total_score + tier-level forward returns.
Compare v4 baseline vs v6b at each horizon.

Hypothesis: v6b should strengthen MORE than v4 at longer horizons since
smoothed_EY (its strongest indicator) has IC 0.081→0.182 from 3M→2Y.
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
W_V4 = {"quality":0.18,"stability":0.18,"cash":0.18,"shareholder":0.15,
         "growth":0.13,"health":0.08,"valuation":0.10}

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
    f.ROIC5Y, f.ROE_Min5Y, f.FSCORE, f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y,
    SAFE_DIVIDE(f.CF_OA_5Y + f.CF_Invest_5Y, ABS(f.CF_OA_5Y)) AS FCF_OA_ratio,
    f.Debt_Eq_P0, f.IntCov_P0, f.CashR_P0,
    SAFE_DIVIDE(f.PE - f.PE_MA5Y, f.PE_SD5Y) AS PE_self_z,
    SAFE_DIVIDE(f.PB - f.PB_MA5Y, f.PB_SD5Y) AS PB_self_z,
    CASE WHEN f.PE > 0 THEN SAFE_DIVIDE(f.NP_R, f.PE) ELSE NULL END AS growth_yield,
    f.PE, f.PB, f.PCF, f.OShares,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
    f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3,
    f.StDebt_P0, f.LtDebt_P0, f.Cash_P0, f.EBITDA_P0,
    CASE WHEN GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0, GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    CASE WHEN GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                       f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7) > 0
         THEN SAFE_DIVIDE(f.Revenue_P0, GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                                                  f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7))
         ELSE NULL END AS Rev_peak_ratio,
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
df["ICB_Code"] = df["ICB_Code"].fillna(0)
df["year"] = pd.to_datetime(df["time"]).dt.year

# ─── v4 indicators ─────────────────────────────────────────────────────────
df["growth_yield"] = df["growth_yield"].clip(-0.15, 0.15)
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"]*_mult; df["DY_sust"]=_mult
np_arr=df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
rev_arr=df[[f"Revenue_P{i}" for i in range(8)]].values.astype(float)
np_n=np.sum(~np.isnan(np_arr),axis=1); rev_n=np.sum(~np.isnan(rev_arr),axis=1)
with np.errstate(divide="ignore",invalid="ignore"):
    np_m=np.nanmean(np_arr,axis=1); np_s=np.nanstd(np_arr,axis=1,ddof=1)
    rev_m=np.nanmean(rev_arr,axis=1); rev_s=np.nanstd(rev_arr,axis=1,ddof=1)
    df["NP_CV"]=np.where(np_n>=6,np_s/np.maximum(np.abs(np_m),1e6),np.nan).clip(max=10)
    df["Rev_CV"]=np.where(rev_n>=6,rev_s/np.maximum(np.abs(rev_m),1e6),np.nan).clip(max=10)
rev_p0=df["Revenue_P0"].values; rev_p7=df["Revenue_P7"].values
df["LT_CAGR"]=np.where((rev_p0>0)&(rev_p7>0),(rev_p0/rev_p7)**(4/7)-1,np.nan).clip(-0.95,5.0)
df["ICB_Code_raw"]=df["ICB_Code"].fillna("UNK")
for col in ["PE","PB","PCF"]:
    grp = df.groupby(["quarter","ICB_Code_raw"])[col]
    med=grp.transform("median"); sd=grp.transform("std")
    z_ind = (df[col]-med)/sd.replace(0,np.nan)
    z_global = df.groupby("quarter")[col].transform(lambda x: (x-x.median())/x.std())
    df[f"{col}_ind_z"] = z_ind.fillna(z_global)

# ─── v6b NEW indicators ────────────────────────────────────────────────────
df["NP_4Q_mean"]=df[[f"NP_P{i}" for i in range(4)]].mean(axis=1,skipna=True)
df["MktCap"]=df["Close"]*df["OShares"]
df["smoothed_EY"]=(df["NP_4Q_mean"]/df["OShares"].replace(0,np.nan)/df["Close"].replace(0,np.nan)).clip(-1,1)
df["EY"]=np.where(df["PE"]>0,1.0/df["PE"],np.nan)
df["FCF_4Q"]=(df["CF_OA_P0"]+df["CF_OA_P1"]+df["CF_OA_P2"]+df["CF_OA_P3"]
            +df["CF_Invest_P0"]+df["CF_Invest_P1"]+df["CF_Invest_P2"]+df["CF_Invest_P3"])
df["FCF_yield"]=(df["FCF_4Q"]/df["MktCap"]).clip(-1,1)
df["r_ROIC5Y_pre"]=df.groupby("quarter")["ROIC5Y"].rank(pct=True,na_option="keep")
df["r_EY_pre"]=df.groupby("quarter")["EY"].rank(pct=True,na_option="keep")
df["magic_formula"]=(df["r_ROIC5Y_pre"]+df["r_EY_pre"])/2.0
df["TotalDebt"]=df["StDebt_P0"].fillna(0)+df["LtDebt_P0"].fillna(0)
df["NetDebt"]=df["TotalDebt"]-df["Cash_P0"].fillna(0)
df["NetDebt_EBITDA_inv"]=-np.where(df["EBITDA_P0"]>0,df["NetDebt"]/df["EBITDA_P0"],np.nan).clip(-20,50)
df["Cash_MktCap"]=np.where(df["MktCap"]>0,df["Cash_P0"]/df["MktCap"],np.nan).clip(-1,5)
df["IntCov_inv"]=-df["IntCov_P0"]

# Inversions
INV_V4=["Debt_Eq_P0","PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z"]
for c in INV_V4: df[c] = -df[c]
df["NP_CV_v4"]  = -df["NP_CV"]   # negative for v4 (lower CV = better)
df["Rev_CV_v4"] = -df["Rev_CV"]

# Axis definitions
AXIS_V4 = {
    "quality":     ["ROIC5Y","ROE_Min5Y","FSCORE"],
    "stability":   ["NP_CV_v4","Rev_CV_v4","LT_CAGR"],
    "cash":        ["CF_OA_5Y","CFOA_NP"],
    "shareholder": ["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
    "growth":      ["NP_R","Revenue_YoY_P0","GPM_change","NP_peak_ratio","Rev_peak_ratio"],
    "health":      ["Debt_Eq_P0","IntCov_P0","CashR_P0"],
    "valuation":   ["PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","growth_yield"],
}
AXIS_V6B = {
    "quality":     ["ROIC5Y","ROE_Min5Y"],
    "stability":   ["NP_CV_v4","Rev_CV_v4","LT_CAGR"],
    "cash":        ["CF_OA_5Y","CFOA_NP"],
    "shareholder": ["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
    "growth":      ["GPM_change","NP_peak_ratio","Rev_peak_ratio"],
    "health":      ["Cash_MktCap","NetDebt_EBITDA_inv","IntCov_inv"],
    "valuation":   ["smoothed_EY","FCF_yield","magic_formula"],
}

# Compute ranks for everything we need
ALL_INDS = set()
for axes in (AXIS_V4, AXIS_V6B):
    for cs in axes.values(): ALL_INDS.update(cs)
print("Computing ranks ...")
for c in ALL_INDS:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

def compute_score(axis_schema, weights):
    score_axes = []
    for axis, cs in axis_schema.items():
        score_col = f"_axis_{axis}"
        df[score_col] = df[[f"r_{c}" for c in cs]].mean(axis=1, skipna=True)
        score_axes.append(score_col)
    w_arr = np.array([weights[a] for a in axis_schema.keys()])
    total = (df[score_axes].values * w_arr).sum(axis=1)
    nan_any = df[score_axes].isna().any(axis=1)
    return np.where(nan_any, np.nan, total), df[score_axes].copy()

print("Computing v4 and v6b total scores ...")
df["v4_score"], _   = compute_score(AXIS_V4,  W_V4)
df["v6b_score"], _  = compute_score(AXIS_V6B, W_V4)

# Tier per quarter for each variant
def assign_tiers(df_, score_col, name):
    out = df_.dropna(subset=[score_col]).copy()
    out[f"{name}_pct"] = out.groupby("quarter")[score_col].rank(pct=True)
    def tier_of(p):
        for n,lo,hi in TIERS:
            if lo<=p<=hi: return n
        return "E"
    out[f"{name}_tier"] = out[f"{name}_pct"].apply(tier_of)
    return out
df_v4  = assign_tiers(df, "v4_score",  "v4")
df_v6b = assign_tiers(df, "v6b_score", "v6b")

# ═══════════════════════════════════════════════════════════════════════════
# IC vs each horizon (full universe for 3M, prune subset for O6M+)
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("COMPOSITE IC vs FORWARD RETURNS"); print("="*80)
horizons = ["profit_3M","O6M","O1Y","O2Y"]
print(f"\n{'Horizon':<12}{'N v4':>8}{'IC v4':>10}{'N v6b':>8}{'IC v6b':>10}{'ΔIC':>10}")
print("-"*60)
for h in horizons:
    s4 = df_v4.dropna(subset=[h])
    s6 = df_v6b.dropna(subset=[h])
    ic4, n4 = spearman_ic(s4["v4_score"], s4[h])
    ic6, n6 = spearman_ic(s6["v6b_score"], s6[h])
    diff = ic6 - ic4
    print(f"{h:<12}{n4:>8}{ic4:>+10.4f}{n6:>8}{ic6:>+10.4f}{diff:>+10.4f}")

# ═══════════════════════════════════════════════════════════════════════════
# TIER-LEVEL forward return at each horizon
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("TIER MEDIAN forward return at each horizon"); print("="*80)

def tier_table(df_, tier_col, score_col, target):
    sub = df_.dropna(subset=[target])
    rows = []
    for tier in ["A","B","C","D","E"]:
        g = sub[sub[tier_col]==tier][target]
        if len(g):
            rows.append({"tier":tier,"N":len(g),"median":g.median(),
                         "mean":g.mean(),"WR":(g>0).mean()*100})
    return pd.DataFrame(rows)

for h in horizons:
    print(f"\n>>> TARGET: {h}")
    t4 = tier_table(df_v4,  "v4_tier",  "v4_score",  h)
    t6 = tier_table(df_v6b, "v6b_tier", "v6b_score", h)
    if len(t4) == 0 or len(t6) == 0:
        print("  insufficient sample"); continue
    print(f"  {'Tier':<5}{'v4 N':>7}{'v4 med':>10}{'v4 WR':>9}{'v6b N':>8}{'v6b med':>11}{'v6b WR':>10}{'Δmed':>9}{'ΔWR':>8}")
    for tier in ["A","B","C","D","E"]:
        r4 = t4[t4.tier==tier]; r6 = t6[t6.tier==tier]
        if len(r4)==0 or len(r6)==0: continue
        m4 = r4["median"].iloc[0]; w4 = r4["WR"].iloc[0]; n4 = r4["N"].iloc[0]
        m6 = r6["median"].iloc[0]; w6 = r6["WR"].iloc[0]; n6 = r6["N"].iloc[0]
        print(f"  {tier:<5}{n4:>7}{m4:>+9.3f}{w4:>+8.1f}%{n6:>8}{m6:>+10.3f}{w6:>+9.1f}%{m6-m4:>+9.3f}{w6-w4:>+8.1f}")

# Spread comparison
print("\n" + "="*80); print("A-E SPREAD by horizon"); print("="*80)
print(f"{'Horizon':<12}{'v4 spread':>12}{'v6b spread':>13}{'Δ':>10}")
for h in horizons:
    t4 = tier_table(df_v4,  "v4_tier",  "v4_score",  h)
    t6 = tier_table(df_v6b, "v6b_tier", "v6b_score", h)
    if len(t4)<5 or len(t6)<5: continue
    s4 = t4[t4.tier=="A"]["median"].iloc[0] - t4[t4.tier=="E"]["median"].iloc[0]
    s6 = t6[t6.tier=="A"]["median"].iloc[0] - t6[t6.tier=="E"]["median"].iloc[0]
    print(f"{h:<12}{s4:>+12.3f}{s6:>+13.3f}{s6-s4:>+10.3f}")

# ═══════════════════════════════════════════════════════════════════════════
# Sample data: what does O6M look like? Sanity check scale
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("Sanity check: forward returns distribution"); print("="*80)
for h in horizons:
    sub = df[h].dropna()
    print(f"  {h}: N={len(sub)}  min={sub.min():.3f}  p25={sub.quantile(0.25):.3f}  "
          f"median={sub.median():.3f}  p75={sub.quantile(0.75):.3f}  max={sub.max():.3f}  mean={sub.mean():.3f}")

print("\n" + "="*80); print("DONE"); print("="*80)
