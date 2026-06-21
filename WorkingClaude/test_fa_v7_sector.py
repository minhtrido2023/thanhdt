#!/usr/bin/env python3
"""
test_fa_v7_sector.py
====================
v7 = v6b with sector-conditional axis weights.

Based on PART 2 sector IC findings:
  Banks (8): ROE focus, NO growth (NP_TTM -0.125 anti-signal!)
  Tech (9): FCF + stability, value SAI
  Cyclicals (0): peak detection extreme
  Materials (1): ROIC strong, value zero
  Industrials (2): balanced + value strong
  ConsServ (5): value + growth both strong
  Utility (7): ROIC, NOT cash flow
  ConsGoods (3): standard v4-like

Variants:
  v6b              (baseline) — uniform weights
  v7_simple        — 3 buckets (Financials / Tech / Other) — easy maintenance
  v7_full          — 8 sector groups, fully tuned
  v7_extreme       — full + drop bad indicators per sector

Validation: profit_3M (full Q4 universe) + O6M, O1Y, O2Y (ticker_prune subset)
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
W_V6B = {"quality":0.18,"stability":0.18,"cash":0.18,"shareholder":0.15,
         "growth":0.13,"health":0.08,"valuation":0.10}

# Sector-tuned weights from PART 2 findings.
# Logic: boost axes with strong IC for that sector, reduce weak/negative ones.
# Each row sums to 1.0.
W_SECTOR_FULL = {
    0: {"quality":0.12,"stability":0.12,"cash":0.13,"shareholder":0.12,  # Energy/Cyclical
        "growth":0.22,"health":0.09,"valuation":0.20},                    # peak_ratio strong
    1: {"quality":0.28,"stability":0.10,"cash":0.18,"shareholder":0.14,  # Materials
        "growth":0.10,"health":0.10,"valuation":0.10},                    # ROIC strong, value zero
    2: {"quality":0.16,"stability":0.14,"cash":0.14,"shareholder":0.12,  # Industrials
        "growth":0.10,"health":0.10,"valuation":0.24},                    # value+ROE strong
    3: {"quality":0.18,"stability":0.18,"cash":0.18,"shareholder":0.15,  # ConsGoods (v4-like)
        "growth":0.13,"health":0.08,"valuation":0.10},
    4: W_V6B,  # unknown — default
    5: {"quality":0.10,"stability":0.16,"cash":0.12,"shareholder":0.10,  # ConsServices
        "growth":0.18,"health":0.08,"valuation":0.26},                    # both value AND growth
    6: W_V6B,
    7: {"quality":0.25,"stability":0.15,"cash":0.08,"shareholder":0.15,  # Utility
        "growth":0.10,"health":0.10,"valuation":0.17},                    # ROIC matters, FCF negative
    8: {"quality":0.25,"stability":0.20,"cash":0.10,"shareholder":0.15,  # Financials
        "growth":0.05,"health":0.10,"valuation":0.15},                    # ROE + AVOID growth
    9: {"quality":0.12,"stability":0.22,"cash":0.22,"shareholder":0.13,  # Tech
        "growth":0.13,"health":0.10,"valuation":0.08},                    # FCF+stab; no value
}
# Sanity: all sum to 1.0
for s, w in W_SECTOR_FULL.items():
    s_total = sum(w.values())
    assert abs(s_total - 1.0) < 1e-9, f"sector {s} weights sum to {s_total}"

# Simpler 3-bucket version: Financials / Tech / Other
W_SECTOR_SIMPLE = {
    "FIN":   W_SECTOR_FULL[8],     # 8
    "TECH":  W_SECTOR_FULL[9],     # 9
    "OTHER": W_V6B,                # 0,1,2,3,4,5,6,7
}
def simple_bucket(s):
    if s == 8: return "FIN"
    if s == 9: return "TECH"
    return "OTHER"

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
    f.ROIC5Y, f.ROE_Min5Y, f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y,
    SAFE_DIVIDE(f.CF_OA_5Y + f.CF_Invest_5Y, ABS(f.CF_OA_5Y)) AS FCF_OA_ratio,
    f.IntCov_P0,
    f.PE, f.PB, f.PCF, f.EVEB, f.OShares,
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

print("Fetching Q4 data ..."); df = bq_query(SQL); print(f"  {len(df):,} rows")
df["ICB_Code"] = df["ICB_Code"].fillna(0)
df["sector_top"] = (df["ICB_Code"] / 1000).astype(int)

# ─── Build v6b indicators ──────────────────────────────────────────────────
# Shareholder helpers
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2*_np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"]*_mult; df["DY_sust"] = _mult

# Stability
np_arr = df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
rev_arr = df[[f"Revenue_P{i}" for i in range(8)]].values.astype(float)
np_n = np.sum(~np.isnan(np_arr), axis=1); rev_n = np.sum(~np.isnan(rev_arr), axis=1)
with np.errstate(divide="ignore", invalid="ignore"):
    np_m = np.nanmean(np_arr, axis=1); np_s = np.nanstd(np_arr, axis=1, ddof=1)
    rev_m = np.nanmean(rev_arr, axis=1); rev_s = np.nanstd(rev_arr, axis=1, ddof=1)
    df["NP_CV"]  = np.where(np_n>=6,  np_s/np.maximum(np.abs(np_m), 1e6), np.nan).clip(max=10)
    df["Rev_CV"] = np.where(rev_n>=6, rev_s/np.maximum(np.abs(rev_m),1e6), np.nan).clip(max=10)
rev_p0 = df["Revenue_P0"].values; rev_p7 = df["Revenue_P7"].values
mask_lt = (rev_p0>0) & (rev_p7>0)
df["LT_CAGR"] = np.where(mask_lt, (rev_p0/rev_p7)**(4/7)-1, np.nan).clip(-0.95, 5.0)

# Valuation (Opt B)
df["NP_4Q_mean"] = df[[f"NP_P{i}" for i in range(4)]].mean(axis=1, skipna=True)
df["MktCap"] = df["Close"] * df["OShares"]
df["smoothed_EY"] = (df["NP_4Q_mean"] / df["OShares"].replace(0,np.nan) / df["Close"].replace(0,np.nan)).clip(-1,1)
df["EY"] = np.where(df["PE"]>0, 1.0/df["PE"], np.nan)
df["FCF_4Q"] = (df["CF_OA_P0"] + df["CF_OA_P1"] + df["CF_OA_P2"] + df["CF_OA_P3"]
              + df["CF_Invest_P0"] + df["CF_Invest_P1"] + df["CF_Invest_P2"] + df["CF_Invest_P3"])
df["FCF_yield"] = (df["FCF_4Q"] / df["MktCap"]).clip(-1, 1)
df["r_ROIC5Y_pre"] = df.groupby("quarter")["ROIC5Y"].rank(pct=True, na_option="keep")
df["r_EY_pre"]    = df.groupby("quarter")["EY"].rank(pct=True, na_option="keep")
df["magic_formula"] = (df["r_ROIC5Y_pre"] + df["r_EY_pre"]) / 2.0

# Health (rescued)
df["TotalDebt"] = df["StDebt_P0"].fillna(0) + df["LtDebt_P0"].fillna(0)
df["NetDebt"] = df["TotalDebt"] - df["Cash_P0"].fillna(0)
df["NetDebt_EBITDA_inv"] = -np.where(df["EBITDA_P0"]>0, df["NetDebt"]/df["EBITDA_P0"], np.nan).clip(-20, 50)
df["Cash_MktCap"] = np.where(df["MktCap"]>0, df["Cash_P0"]/df["MktCap"], np.nan).clip(-1, 5)
df["IntCov_inv"] = -df["IntCov_P0"]

# Inversions for stability (CV lower = better)
df["NP_CV"]  = -df["NP_CV"]
df["Rev_CV"] = -df["Rev_CV"]

# Axis schema (same as v6b)
AXIS = {
    "quality":     ["ROIC5Y","ROE_Min5Y"],
    "stability":   ["NP_CV","Rev_CV","LT_CAGR"],
    "cash":        ["CF_OA_5Y","CFOA_NP"],
    "shareholder": ["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
    "growth":      ["GPM_change","NP_peak_ratio","Rev_peak_ratio"],
    "health":      ["Cash_MktCap","NetDebt_EBITDA_inv","IntCov_inv"],
    "valuation":   ["smoothed_EY","FCF_yield","magic_formula"],
}
ALL_INDS = set()
for cs in AXIS.values(): ALL_INDS.update(cs)
print("Computing ranks ...")
for c in ALL_INDS:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")
for axis, cs in AXIS.items():
    df[f"_score_{axis}"] = df[[f"r_{c}" for c in cs]].mean(axis=1, skipna=True)

def tier_of(p):
    for n, lo, hi in TIERS:
        if lo <= p <= hi: return n
    return "E"

def score_variant(label, weights_fn):
    """weights_fn: callable(row) -> dict of axis weights, OR a single dict (uniform)."""
    score_axes = [f"_score_{a}" for a in AXIS.keys()]
    if isinstance(weights_fn, dict):
        # uniform weights
        w_arr = np.array([weights_fn[a] for a in AXIS.keys()])
        total = (df[score_axes].values * w_arr).sum(axis=1)
    else:
        # per-row weights based on sector
        total = np.zeros(len(df))
        for a in AXIS.keys():
            s = df[f"_score_{a}"].values
            w = df["sector_top"].map(lambda sec: weights_fn(sec)[a]).values
            total += np.nan_to_num(s, nan=0.0) * w
    nan_any = df[score_axes].isna().any(axis=1)
    tmp = df.copy()
    tmp["total_score"] = np.where(nan_any, np.nan, total)
    tmp = tmp.dropna(subset=["total_score"])
    tmp["score_pct"] = tmp.groupby("quarter")["total_score"].rank(pct=True)
    tmp["tier"] = tmp["score_pct"].apply(tier_of)
    return tmp

def report(label, tmp, target="profit_3M", base_spread=None):
    v = tmp.dropna(subset=[target])
    rows = []
    for tier in ["A","B","C","D","E"]:
        g = v[v["tier"]==tier][target]
        if len(g):
            rows.append({"tier":tier,"N":len(g),"median":g.median(),
                         "mean":g.mean(),"WR":(g>0).mean()*100})
    out = pd.DataFrame(rows)
    meds = out["median"].values
    spread = meds[0]-meds[-1] if len(meds)==5 else np.nan
    inv = sum(1 for i in range(len(meds)-1) if meds[i]<meds[i+1])
    a_med = out[out.tier=="A"]["median"].iloc[0] if (out.tier=="A").any() else np.nan
    a_wr  = out[out.tier=="A"]["WR"].iloc[0] if (out.tier=="A").any() else np.nan
    a_n   = int(out[out.tier=="A"]["N"].iloc[0]) if (out.tier=="A").any() else 0
    delta_str = "" if base_spread is None else f" (Δ {spread-base_spread:+.2f})"
    print(f"  {label:<30} A:{a_n}|{a_med:+.2f}%/WR{a_wr:.1f}%  spread={spread:.2f}{delta_str}  inv={inv}")
    return spread, out

# ═══════════════════════════════════════════════════════════════════════════
# Run variants for each horizon
# ═══════════════════════════════════════════════════════════════════════════
def w_simple(s): return W_SECTOR_SIMPLE[simple_bucket(s)]
def w_full(s):   return W_SECTOR_FULL.get(s, W_V6B)

print("\n" + "="*80); print("SCORING VARIANTS (universe = Q4, 3M target)"); print("="*80)
tmp_v6b   = score_variant("v6b", W_V6B)
tmp_v7s   = score_variant("v7_simple", w_simple)
tmp_v7f   = score_variant("v7_full", w_full)

for target in ["profit_3M","O6M","O1Y","O2Y"]:
    has_data = df[target].notna().sum() if target != "profit_3M" else len(df.dropna(subset=["profit_3M"]))
    print(f"\n--- TARGET: {target}  (N={has_data}) ---")
    base_spread = None
    for label, tmp in [("v6b (baseline)", tmp_v6b),
                       ("v7_simple (3-bucket)", tmp_v7s),
                       ("v7_full (8-bucket)", tmp_v7f)]:
        v = tmp.dropna(subset=[target])
        if len(v) < 50:
            print(f"  {label:<30} insufficient sample"); continue
        spread, out = report(label, v, target=target, base_spread=base_spread)
        if base_spread is None: base_spread = spread

# Sector composition of A tier (do financials/tech get a fair shake?)
print("\n" + "="*80); print("SECTOR COMPOSITION OF A TIER (profit_3M validation)"); print("="*80)
for label, tmp in [("v6b", tmp_v6b), ("v7_simple", tmp_v7s), ("v7_full", tmp_v7f)]:
    A = tmp[tmp["tier"]=="A"]
    print(f"\n{label} — A tier total: {len(A)}")
    composition = A.groupby("sector_top").size().sort_index()
    for s in [0,1,2,3,4,5,6,7,8,9]:
        if s in composition.index:
            print(f"  sector {s}: {composition[s]}")

# Sector-level performance: median profit per A-tier per sector
print("\n" + "="*80); print("A-TIER MEDIAN PROFIT_3M BY SECTOR"); print("="*80)
print(f"{'Sector':<10}{'v6b':>13}{'v7_simple':>13}{'v7_full':>13}{'Δ_full v6b':>14}")
print("-"*60)
for s in [0,1,2,3,5,7,8,9]:
    row = f"sector {s:<3}"
    res = {}
    for label, tmp in [("v6b", tmp_v6b), ("v7_simple", tmp_v7s), ("v7_full", tmp_v7f)]:
        A = tmp[(tmp["tier"]=="A") & (tmp["sector_top"]==s)].dropna(subset=["profit_3M"])
        med = A["profit_3M"].median() if len(A) >= 3 else np.nan
        res[label] = (med, len(A))
        row += f"  {med:+5.2f}%(n={len(A):2d})" if not np.isnan(med) else f"  {'N/A':>12}"
    d = res["v7_full"][0] - res["v6b"][0] if not (np.isnan(res["v7_full"][0]) or np.isnan(res["v6b"][0])) else np.nan
    row += f"  {d:+5.2f}pp" if not np.isnan(d) else f"  {'N/A':>9}"
    print(row)

print("\n" + "="*80); print("DONE"); print("="*80)
