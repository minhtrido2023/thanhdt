#!/usr/bin/env python3
"""
test_fa_ic_timedecay.py
=======================
IC time-stability analysis to validate findings from previous step:
  - Valuation axis IC = -0.007 (noise)
  - Health axis IC = -0.041 (anti-signal)
  - FSCORE IC = +0.003 (essentially zero)

Are these stable across regimes, or artifacts of recent period?

Tests:
  A) Period split: 2014-2019 (pre-COVID) vs 2020-2026 (post-COVID)
  B) Annual IC for each axis + top indicators
  C) Rolling 3Y IC for stability
  D) Forward window sensitivity (profit_3M vs profit_6M proxies)
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
    rho = s["x"].rank().corr(s["y"].rank(), method="pearson")
    return rho, len(s)

# Pull also profit_2M and profit_1M for window sensitivity (Section D)
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
    t.ICB_Code, t.profit_2W, t.profit_1M, t.profit_2M, t.profit_3M,
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

# Transforms
df["growth_yield"] = df["growth_yield"].clip(-0.15, 0.15)
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"]*_mult; df["DY_sust"] = _mult
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

print("Computing ranks ...")
for c in ALL_INDICATORS:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
for axis, cs in AXIS.items():
    df[f"score_{axis}"] = df[[f"r_{c}" for c in cs]].mean(axis=1, skipna=True)

axis_of = {ind: ax for ax, cs in AXIS.items() for ind in cs}
df["year"] = pd.to_datetime(df["time"]).dt.year

# ═══════════════════════════════════════════════════════════════════════════
# SECTION A: Period split 2014-2019 vs 2020-2026
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("SECTION A: Period split — 2014-2019 vs 2020-2026"); print("="*80)
periods = {
    "P1: 2014-2019": (2014, 2019),
    "P2: 2020-2026": (2020, 2026),
}

# Axis IC per period (most important)
print(f"\nAxis-level IC (target=profit_3M) per period:")
print(f"{'Axis':<13}{'Full IC':>10}{'P1 IC':>10}{'P2 IC':>10}{'Δ (P2-P1)':>12}{'Stable?':>10}")
print("-"*70)
axis_period = {}
for axis in WEIGHTS:
    rho_full, _ = spearman_ic(df[f"score_{axis}"], df["profit_3M"])
    row = [axis, rho_full]
    for plabel, (y0, y1) in periods.items():
        sub = df[(df["year"]>=y0) & (df["year"]<=y1)]
        rho, n = spearman_ic(sub[f"score_{axis}"], sub["profit_3M"])
        row.append((rho, n))
    p1_ic, p1_n = row[2]; p2_ic, p2_n = row[3]
    delta = p2_ic - p1_ic
    same_sign = (p1_ic * p2_ic > 0) and abs(p1_ic) > 0.02 and abs(p2_ic) > 0.02
    flag = "✓ stable" if same_sign else ("⚠ flipped" if p1_ic*p2_ic < 0 else "noise")
    print(f"{axis:<13}{rho_full:>+10.4f}{p1_ic:>+10.4f}{p2_ic:>+10.4f}{delta:>+12.4f}  {flag}")
    axis_period[axis] = (p1_ic, p2_ic, p1_n, p2_n)

# Indicator IC per period (focus on the ones that mattered)
print(f"\nIndicator-level IC per period (focus on top + weak signals):")
print(f"{'Indicator':<22}{'Axis':<13}{'P1 IC':>10}{'P2 IC':>10}{'Sign flip?':>13}")
print("-"*72)
for ind in ALL_INDICATORS:
    row = []
    for plabel, (y0, y1) in periods.items():
        sub = df[(df["year"]>=y0) & (df["year"]<=y1)]
        rho, n = spearman_ic(sub[f"r_{ind}"], sub["profit_3M"])
        row.append(rho)
    flip = "⚠ FLIP" if row[0]*row[1] < 0 and (abs(row[0])>0.03 or abs(row[1])>0.03) else ""
    strong = "🟢" if abs(row[0])>0.08 and abs(row[1])>0.08 and row[0]*row[1]>0 else ""
    print(f"{ind:<22}{axis_of[ind]:<13}{row[0]:>+10.4f}{row[1]:>+10.4f}  {flip}{strong}")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION B: Annual IC for each axis
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("SECTION B: Annual IC per axis (year by year, profit_3M)"); print("="*80)
years = sorted(df["year"].unique())
print(f"\n{'Axis':<13}" + "".join([f"{y:>8}" for y in years]))
print("-"*(13 + 8*len(years)))
for axis in WEIGHTS:
    row = f"{axis:<13}"
    for y in years:
        sub = df[df["year"]==y]
        rho, n = spearman_ic(sub[f"score_{axis}"], sub["profit_3M"])
        row += f"{rho:>+7.3f} " if not np.isnan(rho) else "    N/A "
    print(row)

# N per year
ns_row = f"{'(N)':<13}"
for y in years:
    sub = df[(df["year"]==y)].dropna(subset=["profit_3M"])
    ns_row += f"{len(sub):>8}"
print(ns_row)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION C: Health and Valuation deep-dive (why negative?)
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("SECTION C: Health and Valuation — why negative IC?"); print("="*80)
print("\nIndicator IC per year for HEALTH axis components:")
print(f"{'Indicator':<22}" + "".join([f"{y:>8}" for y in years]))
print("-"*(22 + 8*len(years)))
for ind in AXIS["health"]:
    row = f"{ind:<22}"
    for y in years:
        sub = df[df["year"]==y]
        rho, _ = spearman_ic(sub[f"r_{ind}"], sub["profit_3M"])
        row += f"{rho:>+7.3f} " if not np.isnan(rho) else "    N/A "
    print(row)
print("\nIndicator IC per year for VALUATION axis components:")
print(f"{'Indicator':<22}" + "".join([f"{y:>8}" for y in years]))
print("-"*(22 + 8*len(years)))
for ind in AXIS["valuation"]:
    row = f"{ind:<22}"
    for y in years:
        sub = df[df["year"]==y]
        rho, _ = spearman_ic(sub[f"r_{ind}"], sub["profit_3M"])
        row += f"{rho:>+7.3f} " if not np.isnan(rho) else "    N/A "
    print(row)

# Test reverse: does HIGH PE outperform LOW PE in some periods? (regime hypothesis)
print("\nIs there a regime where high-PE (anti-value) wins?")
print("(IC sign of PE_self_z BEFORE inversion: + would mean expensive = good)")
for plabel, (y0, y1) in periods.items():
    sub = df[(df["year"]>=y0) & (df["year"]<=y1)].copy()
    # Un-invert PE_self_z for clarity
    sub["pe_z_orig"] = -sub["PE_self_z"]  # back to original direction
    rho_orig, n = spearman_ic(sub["pe_z_orig"].rank(pct=True), sub["profit_3M"])
    print(f"  {plabel}  PE_self_z (original direction, + = expensive)  IC={rho_orig:+.4f}  N={n}")
print("  Note: in equity finance, + IC for expensive PE often indicates growth regime")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION D: Forward window sensitivity (profit_1M, 2M, 3M)
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("SECTION D: Forward window sensitivity"); print("="*80)
targets = ["profit_2W", "profit_1M", "profit_2M", "profit_3M"]
print(f"\nAxis IC across forward windows (full sample):")
print(f"{'Axis':<13}" + "".join([f"{t:>11}" for t in targets]))
print("-"*(13 + 11*len(targets)))
for axis in WEIGHTS:
    row = f"{axis:<13}"
    for t in targets:
        if t not in df.columns:
            row += f"{'N/A':>11}"
            continue
        rho, n = spearman_ic(df[f"score_{axis}"], df[t])
        row += f"{rho:>+10.4f} " if not np.isnan(rho) else f"{'N/A':>11}"
    print(row)

# Reweight schemes preview based on IC findings
print("\n" + "="*80); print("PREVIEW: IC-based reweighting alternatives"); print("="*80)
# Compute average abs(IC) per axis to assess weight rebalance candidates
ic_axis_full = {}
for axis in WEIGHTS:
    rho, _ = spearman_ic(df[f"score_{axis}"], df["profit_3M"])
    ic_axis_full[axis] = rho

print("\nv4 weight vs IC-implied weight:")
print(f"{'Axis':<13}{'v4 weight':>10}{'IC (full)':>10}{'IC-implied':>12}{'Diff':>8}")
print("-"*55)
# Implied weight = positive IC normalized; negative IC → weight 0
pos_ic = {a: max(ic, 0) for a, ic in ic_axis_full.items()}
total_pos = sum(pos_ic.values())
if total_pos > 0:
    implied = {a: pos_ic[a]/total_pos for a in WEIGHTS}
else:
    implied = WEIGHTS.copy()
for axis in WEIGHTS:
    v4 = WEIGHTS[axis]
    ic = ic_axis_full[axis]
    imp = implied[axis]
    print(f"{axis:<13}{v4:>10.3f}{ic:>+10.4f}{imp:>12.3f}{imp-v4:>+8.3f}")

print("\n" + "="*80); print("DONE"); print("="*80)
