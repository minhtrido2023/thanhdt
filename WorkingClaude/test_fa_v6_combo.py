#!/usr/bin/env python3
"""
test_fa_v6_combo.py
===================
v6 comprehensive: incorporate all findings from session.

Variants tested (cumulative):
  v6a = v4 axis structure + REDESIGNED valuation (Opt B) + REDESIGNED health
  v6b = v6a + drop noise indicators (FSCORE, NP_R, Revenue_YoY_P0)
  v6c = v6b + IC-implied axis weights
  v6d = v6c + Elite-A sub-tier (MEGA-A = A + stability top quartile)

Each variant: validate tier ordering (forward profit_3M Q4) vs v4 baseline.

Spec for valuation (Opt B): smoothed_EY + FCF_yield + Magic_Formula
Spec for health: Cash/MktCap + NetDebt/EBITDA (inverted) + IntCov (inverted)
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"

WEIGHTS_V4 = {"quality":0.18,"stability":0.18,"cash":0.18,"shareholder":0.15,
              "growth":0.13,"health":0.08,"valuation":0.10}
# IC-implied weights (rough rounding to sum 1.00)
WEIGHTS_V6_IC = {"quality":0.16,"stability":0.18,"cash":0.16,"shareholder":0.16,
                 "growth":0.08,"health":0.12,"valuation":0.14}
TIERS = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]
assert abs(sum(WEIGHTS_V4.values()) - 1.0) < 1e-9
assert abs(sum(WEIGHTS_V6_IC.values()) - 1.0) < 1e-9

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
    f.PE, f.PB, f.PCF, f.EVEB, f.EPS, f.BVPS, f.OShares,
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
df["year"] = pd.to_datetime(df["time"]).dt.year
df["ICB_Code"] = df["ICB_Code"].fillna(0)

# ─── v4 indicators ──────────────────────────────────────────────────────────
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
for col in ["PE","PB","PCF"]:
    grp = df.groupby(["quarter","ICB_Code"])[col]
    med=grp.transform("median"); sd=grp.transform("std")
    z_ind = (df[col]-med)/sd.replace(0,np.nan)
    z_global = df.groupby("quarter")[col].transform(lambda x: (x-x.median())/x.std())
    df[f"{col}_ind_z"] = z_ind.fillna(z_global)

# ─── v6 NEW indicators ──────────────────────────────────────────────────────
# Valuation (Option B)
df["NP_4Q_mean"] = df[NP_COLS[:4]].mean(axis=1, skipna=True)
df["MktCap"] = df["Close"] * df["OShares"]
df["smoothed_EPS"] = df["NP_4Q_mean"] / df["OShares"].replace(0, np.nan)
df["smoothed_EY"]  = (df["smoothed_EPS"] / df["Close"].replace(0, np.nan)).clip(-1, 1)
df["EY"]  = np.where(df["PE"] > 0,  1.0 / df["PE"],  np.nan)
df["FCF_4Q"] = (df["CF_OA_P0"] + df["CF_OA_P1"] + df["CF_OA_P2"] + df["CF_OA_P3"]
              + df["CF_Invest_P0"] + df["CF_Invest_P1"] + df["CF_Invest_P2"] + df["CF_Invest_P3"])
df["FCF_yield"] = np.where(df["MktCap"] > 0, df["FCF_4Q"] / df["MktCap"], np.nan)
df["FCF_yield"] = df["FCF_yield"].clip(-1, 1)
df["r_ROIC5Y_for_mf"] = df.groupby("quarter")["ROIC5Y"].rank(pct=True, na_option="keep")
df["r_EY_for_mf"]      = df.groupby("quarter")["EY"].rank(pct=True, na_option="keep")
df["magic_formula"] = (df["r_ROIC5Y_for_mf"] + df["r_EY_for_mf"]) / 2.0

# Health (rescued)
df["TotalDebt"] = df["StDebt_P0"].fillna(0) + df["LtDebt_P0"].fillna(0)
df["NetDebt"]   = df["TotalDebt"] - df["Cash_P0"].fillna(0)
df["NetDebt_EBITDA_raw"] = np.where(df["EBITDA_P0"] > 0,
                                    df["NetDebt"] / df["EBITDA_P0"], np.nan).clip(-20, 50)
df["Cash_MktCap"] = np.where(df["MktCap"] > 0, df["Cash_P0"] / df["MktCap"], np.nan).clip(-1, 5)
# Invert NetDebt and IntCov for v6 (lower-debt-good and low-IntCov-good are both "high rank = good")
df["NetDebt_EBITDA_inv"] = -df["NetDebt_EBITDA_raw"]
df["IntCov_inv"]         = -df["IntCov_P0"]

# Inversions (lower-is-better for v4)
INV_V4=["Debt_Eq_P0","PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","NP_CV","Rev_CV"]
for c in INV_V4: df[c] = -df[c]

# ─── Axis definitions ──────────────────────────────────────────────────────
AXIS_V4 = {
    "quality":     ["ROIC5Y","ROE_Min5Y","FSCORE"],
    "stability":   ["NP_CV","Rev_CV","LT_CAGR"],
    "cash":        ["CF_OA_5Y","CFOA_NP"],
    "shareholder": ["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
    "growth":      ["NP_R","Revenue_YoY_P0","GPM_change","NP_peak_ratio","Rev_peak_ratio"],
    "health":      ["Debt_Eq_P0","IntCov_P0","CashR_P0"],
    "valuation":   ["PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","growth_yield"],
}
# v6a: redesigned valuation + health, rest unchanged
AXIS_V6A = dict(AXIS_V4)
AXIS_V6A["valuation"] = ["smoothed_EY","FCF_yield","magic_formula"]
AXIS_V6A["health"]    = ["Cash_MktCap","NetDebt_EBITDA_inv","IntCov_inv"]
# v6b: v6a + drop noise indicators (FSCORE in quality, NP_R/Revenue_YoY in growth)
AXIS_V6B = dict(AXIS_V6A)
AXIS_V6B["quality"] = ["ROIC5Y","ROE_Min5Y"]                        # drop FSCORE
AXIS_V6B["growth"]  = ["GPM_change","NP_peak_ratio","Rev_peak_ratio"] # drop NP_R, Revenue_YoY

# Collect all columns we need to rank
ALL_COLS = set()
for axes in (AXIS_V4, AXIS_V6A, AXIS_V6B):
    for cs in axes.values(): ALL_COLS.update(cs)

print("Computing percentile ranks ...")
for c in ALL_COLS:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

def tier_of(p):
    for n, lo, hi in TIERS:
        if lo <= p <= hi: return n
    return "E"

def score_variant(axis_schema, weights, label):
    """Compute total_score using axis schema + weights. Returns df with tier assigned."""
    score_cols = []
    for axis, cs in axis_schema.items():
        rcols = [f"r_{c}" for c in cs]
        df[f"_score_{axis}"] = df[rcols].mean(axis=1, skipna=True)
        score_cols.append(f"_score_{axis}")
    w_arr = np.array([weights[a] for a in axis_schema.keys()])
    total = (df[score_cols].values * w_arr).sum(axis=1)
    nan_any = df[score_cols].isna().any(axis=1)
    tmp = df.copy()
    tmp["total_score"] = np.where(nan_any, np.nan, total)
    tmp = tmp.dropna(subset=["total_score"])
    tmp["score_pct"] = tmp.groupby("quarter")["total_score"].rank(pct=True)
    tmp["tier"] = tmp["score_pct"].apply(tier_of)
    return tmp

def report(label, tmp, base_spread=None, extra_A_mega=None):
    v = tmp.dropna(subset=["profit_3M"])
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
    a_med = out[out.tier=="A"]["median"].iloc[0] if (out.tier=="A").any() else np.nan
    a_mean = out[out.tier=="A"]["mean"].iloc[0] if (out.tier=="A").any() else np.nan
    a_wr  = out[out.tier=="A"]["WR"].iloc[0] if (out.tier=="A").any() else np.nan
    a_n   = int(out[out.tier=="A"]["N"].iloc[0]) if (out.tier=="A").any() else 0
    delta = "" if base_spread is None else f" (Δ {spread-base_spread:+.2f})"
    print(f"\n>>> {label}")
    print(f"    A: N={a_n} med={a_med:.2f}% mean={a_mean:.2f}% WR={a_wr:.1f}% | spread={spread:.2f}pp{delta} | inv={inv}")
    print("    " + out.to_string(index=False, float_format="%.2f").replace("\n","\n    "))
    if extra_A_mega is not None:
        m = extra_A_mega
        print(f"    🏆 MEGA-A: N={m['N']} med={m['median']:.2f}% mean={m['mean']:.2f}% WR={m['WR']:.1f}%")
    return spread

# ═══════════════════════════════════════════════════════════════════════════
# Run variants
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("VARIANT TESTS"); print("="*80)

# Baseline (v4)
tmp_base = score_variant(AXIS_V4, WEIGHTS_V4, "v4_baseline")
base_spread = report("v4_baseline", tmp_base)

# v6a: redesigned valuation + health only, same axis weights
tmp_v6a = score_variant(AXIS_V6A, WEIGHTS_V4, "v6a")
report("v6a: redesigned valuation + health, v4 weights", tmp_v6a, base_spread)

# v6b: v6a + drop noise indicators
tmp_v6b = score_variant(AXIS_V6B, WEIGHTS_V4, "v6b")
report("v6b: v6a + drop FSCORE/NP_R/Revenue_YoY (noise)", tmp_v6b, base_spread)

# v6c: v6b + IC-implied axis weights
tmp_v6c = score_variant(AXIS_V6B, WEIGHTS_V6_IC, "v6c")
report("v6c: v6b + IC-implied weights", tmp_v6c, base_spread)

# v6d: v6c + Elite-A sub-tier (MEGA-A = A AND stability score top quartile)
# Compute stability score top quartile cutoff (per quarter)
tmp_v6d = tmp_v6c.copy()
# Use the _score_stability column from v6c run
stab_quartile = tmp_v6d.groupby("quarter")["_score_stability"].transform(lambda x: x.quantile(0.75))
tmp_v6d["mega_a"] = (tmp_v6d["tier"]=="A") & (tmp_v6d["_score_stability"] >= stab_quartile)
mega = tmp_v6d[tmp_v6d["mega_a"]].dropna(subset=["profit_3M"])
mega_info = {"N":len(mega),"median":mega["profit_3M"].median(),"mean":mega["profit_3M"].mean(),
             "WR":(mega["profit_3M"]>0).mean()*100} if len(mega) else None
report("v6d: v6c + MEGA-A elite sub-tier (A + stability top-Q)", tmp_v6d, base_spread, extra_A_mega=mega_info)

# Alt MEGA-A: A AND (stability top-Q OR DY > 5%)
mega_alt = tmp_v6d[(tmp_v6d["tier"]=="A") &
                    ((tmp_v6d["_score_stability"] >= stab_quartile) | (tmp_v6d["DY"] > 0.05))]
mega_alt = mega_alt.dropna(subset=["profit_3M"])
print(f"\n    🏆 MEGA-A (alt: A + stab_top OR DY>5%): N={len(mega_alt)}  med={mega_alt['profit_3M'].median():.2f}%  WR={(mega_alt['profit_3M']>0).mean()*100:.1f}%")

# Most aggressive: A + Quality top + Stability top (smaller sample but highest WR previously)
q_quartile = tmp_v6d.groupby("quarter")["_score_quality"].transform(lambda x: x.quantile(0.75))
ultra = tmp_v6d[(tmp_v6d["tier"]=="A")
                & (tmp_v6d["_score_quality"] >= q_quartile)
                & (tmp_v6d["_score_stability"] >= stab_quartile)]
ultra = ultra.dropna(subset=["profit_3M"])
if len(ultra):
    print(f"    🏆 ULTRA-A (A + qual_top + stab_top):       N={len(ultra)}  med={ultra['profit_3M'].median():.2f}%  WR={(ultra['profit_3M']>0).mean()*100:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════
# Sub-axis individual IC checks (part b verification)
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("PART (b) verification: indicator IC after v6 redesign"); print("="*80)
print("\nValuation (v6 Opt B) per-indicator IC:")
for c in AXIS_V6A["valuation"]:
    rho, n = spearman_ic(df[f"r_{c}"], df["profit_3M"])
    print(f"  {c:<20} IC={rho:+.4f}  N={n}")
print("\nHealth (v6 rescued) per-indicator IC:")
for c in AXIS_V6A["health"]:
    rho, n = spearman_ic(df[f"r_{c}"], df["profit_3M"])
    print(f"  {c:<20} IC={rho:+.4f}  N={n}")
print("\nAxis-level IC after v6 redesign:")
for axis in AXIS_V6B:
    rho, n = spearman_ic(tmp_v6c[f"_score_{axis}"], tmp_v6c["profit_3M"])
    print(f"  {axis:<13} IC={rho:+.4f}  N={n}")

print("\n" + "="*80); print("DONE"); print("="*80)
