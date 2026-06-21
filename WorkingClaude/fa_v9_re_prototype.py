#!/usr/bin/env python3
"""
fa_v9_re_prototype.py
=====================
Prototype: FA-system v9 for Real Estate / Industrial Park (ICB 8633).

Goal: validate whether adding 3 new indicators (AdvCust_YoY, AdvCust_QoQ,
RevCoverage) + sector-conditional axis re-weighting improves tier ranking
for RE/KCN tickers — specifically does TCH 2023Q2-Q3 and 2025Q3+ get
upgraded out of D/E?

Universe: ICB_Code = 8633 (Real Estate including KCN), liquidity >= 1B/day.
Compared against: tav2_bq.fa_ratings (old v4 tier).

Output:
  fa_v9_re_prototype.csv           — per-row (ticker × quarter) old vs new tier
  fa_v9_re_prototype_summary.txt   — TCH detail + forward profit_3M validation
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, sys, tempfile, io
from io import StringIO
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"
ICB_RE  = 8633.0

# Sector-conditional weights for RE/KCN (vs v4 default)
WEIGHTS_RE = {
    "quality":     0.18,   # unchanged
    "stability":   0.10,   # 0.18 → 0.10 (cyclical-aware: don't punish lumpy NP)
    "cash":        0.22,   # 0.18 → 0.22 (boost: includes RevCoverage)
    "shareholder": 0.15,   # unchanged
    "growth":      0.17,   # 0.13 → 0.17 (boost: includes AdvCust_YoY/QoQ)
    "health":      0.08,   # unchanged
    "valuation":   0.10,   # unchanged
}

TIERS = [("A", 0.90, 1.00), ("B", 0.70, 0.90), ("C", 0.40, 0.70),
         ("D", 0.15, 0.40), ("E", 0.00, 0.15)]

def bq_query(sql, label=""):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = (f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
               f'--project_id={PROJECT} --format=csv --max_rows=10000000')
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0:
        raise RuntimeError(f"[BQ ERROR] {label}: {(r.stdout or r.stderr)[:600]}")
    txt = r.stdout.strip()
    return pd.read_csv(StringIO(txt)) if txt else pd.DataFrame()

# ─── 1. Pull RE/KCN universe with full schema + new fields ─────────────────────
SQL = f"""
WITH joined AS (
  SELECT
    f.ticker, f.quarter, f.time,
    -- standard FA inputs (mirrors fundamental_rating.py)
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
    CASE WHEN GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0,GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    CASE WHEN GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                       f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7) > 0
         THEN SAFE_DIVIDE(f.Revenue_P0,GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                                                 f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7))
         ELSE NULL END AS Rev_peak_ratio,
    -- NEW: advance from customers + unearned revenue
    f.AdvCust_P0, f.AdvCust_P1, f.AdvCust_P4, f.UnearnRev_P0,
    -- price/sector/liquidity
    t.ICB_Code,
    t.Volume_3M_P50 * t.Close AS trading_value_1M,
    t.profit_3M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker
    AND t.time <= f.time
    AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2018-01-01"
    AND t.ICB_Code = {ICB_RE}
    AND t.Volume_3M_P50 IS NOT NULL
    AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching RE/KCN universe ...")
df = bq_query(SQL, "re_pull")
print(f"  {len(df):,} (ticker, quarter) rows, {df['ticker'].nunique()} tickers")

# ─── 2. Compute new RE-specific indicators ────────────────────────────────────
# Revenue TTM = last 4 quarters
df["Revenue_TTM"] = df[["Revenue_P0","Revenue_P1","Revenue_P2","Revenue_P3"]].sum(axis=1, min_count=2)
# Forward revenue coverage: AdvCust + UnearnRev as % of TTM revenue. Higher = stronger backlog
df["RevCoverage"] = ((df["AdvCust_P0"].fillna(0) + df["UnearnRev_P0"].fillna(0))
                     / df["Revenue_TTM"].replace(0, np.nan)).clip(lower=0, upper=20)
# AdvCust growth: YoY and QoQ. Clip to ±5 to handle base=0 explosions
def _safe_growth(num, den):
    den = den.replace(0, np.nan)
    return (num / den - 1).clip(lower=-1.0, upper=5.0)
df["AdvCust_YoY"] = _safe_growth(df["AdvCust_P0"], df["AdvCust_P4"])
df["AdvCust_QoQ"] = _safe_growth(df["AdvCust_P0"], df["AdvCust_P1"])

print(f"  Coverage: AdvCust_YoY {df['AdvCust_YoY'].notna().sum()}, "
      f"RevCoverage {df['RevCoverage'].notna().sum()}, "
      f"AdvCust_QoQ {df['AdvCust_QoQ'].notna().sum()}")

# ─── 3. Standard transforms (DY adj, CV, industry-relative valuation) ─────────
_np_r = df["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2 * _np_r, 0.0, 1.0))
df["DY_adj"]  = df["DY"] * _mult
df["DY_sust"] = _mult

NP_COLS  = [f"NP_P{i}"      for i in range(8)]
REV_COLS = [f"Revenue_P{i}" for i in range(8)]
np_arr  = df[NP_COLS].values.astype(float)
rev_arr = df[REV_COLS].values.astype(float)
np_n  = np.sum(~np.isnan(np_arr),  axis=1)
rev_n = np.sum(~np.isnan(rev_arr), axis=1)
with np.errstate(divide="ignore", invalid="ignore"):
    np_mean  = np.nanmean(np_arr,  axis=1)
    np_std   = np.nanstd(np_arr,   axis=1, ddof=1)
    rev_mean = np.nanmean(rev_arr, axis=1)
    rev_std  = np.nanstd(rev_arr,  axis=1, ddof=1)
    df["NP_CV"]  = np.where(np_n  >= 6, np_std  / np.maximum(np.abs(np_mean),  1e6), np.nan)
    df["Rev_CV"] = np.where(rev_n >= 6, rev_std / np.maximum(np.abs(rev_mean), 1e6), np.nan)
    df["NP_CV"]  = df["NP_CV"].clip(upper=10)
    df["Rev_CV"] = df["Rev_CV"].clip(upper=10)

rev_p0 = df["Revenue_P0"].values; rev_p7 = df["Revenue_P7"].values
mask = (rev_p0 > 0) & (rev_p7 > 0)
df["LT_CAGR"] = np.where(mask, (rev_p0 / rev_p7) ** (4/7) - 1, np.nan)
df["LT_CAGR"] = df["LT_CAGR"].clip(lower=-0.95, upper=5.0)

df["growth_yield"] = df["growth_yield"].clip(lower=-0.15, upper=0.15)

# Industry-relative valuation z (within RE cohort × quarter)
for col in ["PE", "PB", "PCF"]:
    grp = df.groupby("quarter")[col]
    med = grp.transform("median")
    sd  = grp.transform("std")
    df[f"{col}_ind_z"] = (df[col] - med) / sd.replace(0, np.nan)

# Invert lower-is-better
INV = ["Debt_Eq_P0","PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","NP_CV","Rev_CV"]
for c in INV: df[c] = -df[c]

# ─── 4. Axis definitions (v9 with new indicators in cash + growth) ────────────
AXIS_COLS = {
    "quality":     ["ROIC5Y","ROE_Min5Y","FSCORE"],
    "stability":   ["NP_CV","Rev_CV","LT_CAGR"],
    "cash":        ["CF_OA_5Y","CFOA_NP","RevCoverage"],          # +RevCoverage
    "shareholder": ["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
    "growth":      ["NP_R","Revenue_YoY_P0","GPM_change","NP_peak_ratio","Rev_peak_ratio",
                    "AdvCust_YoY","AdvCust_QoQ"],                  # +2
    "health":      ["Debt_Eq_P0","IntCov_P0","CashR_P0"],
    "valuation":   ["PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","growth_yield"],
}

# Per-quarter percentile rank for each indicator (within RE cohort)
for cols in AXIS_COLS.values():
    for c in cols:
        df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

# Axis composite
for axis, cols in AXIS_COLS.items():
    rank_cols = [f"r_{c}" for c in cols]
    df[f"score_{axis}"] = df[rank_cols].mean(axis=1, skipna=True)

score_cols = [f"score_{a}" for a in WEIGHTS_RE]
weights = np.array([WEIGHTS_RE[a] for a in WEIGHTS_RE])
df["total_score_v9"] = (df[score_cols].values * weights).sum(axis=1)
df = df.dropna(subset=score_cols, how="any").copy()
print(f"  {len(df):,} rows with full axis coverage after v9")

df["score_pct_v9"] = df.groupby("quarter")["total_score_v9"].rank(pct=True)

def tier_of(p):
    for name, lo, hi in TIERS:
        if lo <= p <= hi: return name
    return "E"
df["tier_v9"] = df["score_pct_v9"].apply(tier_of)

# ─── 5. Pull old tier from fa_ratings for direct comparison ────────────────────
print("\nPulling old fa_ratings tiers for same (ticker, quarter) ...")
tk_list = "','".join(df["ticker"].unique())
SQL_OLD = f"""
SELECT ticker, quarter, tier AS tier_old, total_score AS total_score_old,
       score_pct AS score_pct_old
FROM `lithe-record-440915-m9.tav2_bq.fa_ratings`
WHERE ticker IN ('{tk_list}')
"""
old = bq_query(SQL_OLD, "old_tier")
print(f"  Pulled {len(old):,} old-tier rows")

m = df.merge(old, on=["ticker","quarter"], how="left")

# ─── 6. Save full comparison ───────────────────────────────────────────────────
out_cols = ["ticker","quarter","time","tier_old","tier_v9",
            "score_pct_old","score_pct_v9","total_score_old","total_score_v9",
            "score_quality","score_stability","score_cash","score_shareholder",
            "score_growth","score_health","score_valuation",
            "AdvCust_P0","AdvCust_YoY","AdvCust_QoQ","RevCoverage","UnearnRev_P0",
            "Revenue_P0","NP_R","profit_3M"]
m[out_cols].sort_values(["ticker","time"]).to_csv("data/fa_v9_re_prototype.csv", index=False)
print("  Saved fa_v9_re_prototype.csv")

# ─── 7. Validation summary ─────────────────────────────────────────────────────
with open("fa_v9_re_prototype_summary.txt", "w", encoding="utf-8") as fp:
    def w(s): fp.write(s + "\n"); print(s)

    w("="*72)
    w("FA v9 PROTOTYPE — RE/KCN (ICB 8633) SUMMARY")
    w("="*72)
    w(f"Universe: {m['ticker'].nunique()} tickers, {len(m):,} (ticker,quarter) rows, "
      f"quarters {m['quarter'].min()} -> {m['quarter'].max()}")

    # 7a. Tier transition matrix
    w("\n--- Tier transition matrix (old → v9, RE/KCN only) ---")
    valid = m.dropna(subset=["tier_old","tier_v9"])
    ct = pd.crosstab(valid["tier_old"], valid["tier_v9"]).reindex(
        index=["A","B","C","D","E"], columns=["A","B","C","D","E"], fill_value=0)
    w(ct.to_string())
    n_up = sum(valid.apply(lambda r: "ABCDE".index(r["tier_v9"]) < "ABCDE".index(r["tier_old"]), axis=1))
    n_dn = sum(valid.apply(lambda r: "ABCDE".index(r["tier_v9"]) > "ABCDE".index(r["tier_old"]), axis=1))
    n_eq = len(valid) - n_up - n_dn
    w(f"\nUpgraded: {n_up} ({n_up/len(valid)*100:.1f}%)  "
      f"Same: {n_eq} ({n_eq/len(valid)*100:.1f}%)  "
      f"Downgraded: {n_dn} ({n_dn/len(valid)*100:.1f}%)")

    # 7b. Forward profit_3M by tier (validation: A > B > C > D > E should hold)
    w("\n--- Forward profit_3M by NEW v9 tier (RE/KCN) ---")
    v = m.dropna(subset=["profit_3M"])
    w(f"{'Tier':<6}{'N':>8}{'Median':>10}{'Mean':>10}{'WinRate':>10}")
    for t in ["A","B","C","D","E"]:
        g = v[v["tier_v9"] == t]["profit_3M"]
        if len(g):
            w(f"{t:<6}{len(g):>8,}{g.median():>9.2f}%{g.mean():>9.2f}%{(g>0).mean()*100:>9.1f}%")

    w("\n--- Forward profit_3M by OLD v4 tier (RE/KCN, same rows) ---")
    w(f"{'Tier':<6}{'N':>8}{'Median':>10}{'Mean':>10}{'WinRate':>10}")
    v2 = v.dropna(subset=["tier_old"])
    for t in ["A","B","C","D","E"]:
        g = v2[v2["tier_old"] == t]["profit_3M"]
        if len(g):
            w(f"{t:<6}{len(g):>8,}{g.median():>9.2f}%{g.mean():>9.2f}%{(g>0).mean()*100:>9.1f}%")

    # 7c. TCH detail
    w("\n--- TCH quarter-by-quarter: old vs new tier ---")
    tch = m[m["ticker"] == "TCH"].sort_values("time")
    w(f"{'Quarter':<8}{'Time':<12}{'OLD':>5}{'NEW':>5}  {'AdvCust(B)':>11}{'AdvYoY':>9}"
      f"{'AdvQoQ':>9}{'RevCov':>8}{'profit_3M':>11}")
    for _, r in tch.iterrows():
        adv_b = (r['AdvCust_P0'] or 0) / 1e9
        yoy   = r['AdvCust_YoY'] if pd.notna(r['AdvCust_YoY']) else float('nan')
        qoq   = r['AdvCust_QoQ'] if pd.notna(r['AdvCust_QoQ']) else float('nan')
        rcov  = r['RevCoverage'] if pd.notna(r['RevCoverage']) else float('nan')
        p3m   = r['profit_3M'] if pd.notna(r['profit_3M']) else float('nan')
        w(f"{r['quarter']:<8}{str(r['time'])[:10]:<12}"
          f"{str(r['tier_old']):>5}{str(r['tier_v9']):>5}"
          f"  {adv_b:>10,.0f} {yoy:>+8.2f} {qoq:>+8.2f} {rcov:>7.2f} {p3m:>10.1f}%")

print("\nDone. See fa_v9_re_prototype.csv + fa_v9_re_prototype_summary.txt")
