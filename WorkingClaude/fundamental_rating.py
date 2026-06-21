#!/usr/bin/env python3
"""
fundamental_rating.py
=====================
7-axis composite rating for Vietnamese stocks (cycle-aware + shareholder-aware).

Q4 reports = annual cumulative ("báo cáo năm"); Q1/Q2/Q3 = standalone quarter.
Default canonical CSV uses Q4 only; full all-quarters CSV exported for quarterly
rebalance variant.

Axes (weighted): Quality 18 | Stability 18 | Cash 18 | Shareholder 15 | Growth 13 | Health 8 | Valuation 10

Key cycle-aware + shareholder-aware additions vs the original 5-axis version:
  - **Stability axis**: penalizes lumpy earnings (BĐS, khoáng sản) using
    CV(NP_P0..P7), CV(Revenue_P0..P7), and 7-quarter Revenue CAGR
  - **Industry-relative valuation**: PE/PB/PCF z-score within ICB_Code peers
    (catches structural-cheap traps like coal/mining where low PE is chronic,
    not a discount)
  - **Shareholder Yield axis**: catches "profits don't reach shareholders" trap
    (e.g. mining where lợi nhuận chia cho công nhân viên) using DY,
    Dividend_Min3Y consistency floor, and FCF/CF_OA cash retention ratio

Universe: tickers with Volume_1M * Close >= 1B VND on report-active date.
Tiers per quarter cohort: A (top 10%) | B (10-30%) | C (30-60%) | D (60-85%) | E (bottom 15%)
Validation: median forward profit_3M by tier should rank A > B > C > D > E.

Output: fundamental_rating.csv (Q4 canonical) + fundamental_rating_all.csv (all quarters)
        + fundamental_rating_latest.csv
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"
OUT_CSV    = "data/fundamental_rating.csv"
OUT_ALL    = "data/fundamental_rating_all.csv"
OUT_LATEST = "data/fundamental_rating_latest.csv"

WEIGHTS = {
    "quality":     0.18,
    "stability":   0.18,   # cycle awareness
    "cash":        0.18,
    "shareholder": 0.15,   # NEW: catches "profits don't reach shareholders" trap
    "growth":      0.13,
    "health":      0.08,
    "valuation":   0.10,
}

TIERS = [
    ("A", 0.90, 1.00),
    ("B", 0.70, 0.90),
    ("C", 0.40, 0.70),
    ("D", 0.15, 0.40),
    ("E", 0.00, 0.15),
]

# ─── BQ helper ───────────────────────────────────────────────────────────────
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

# ─── Pull raw indicators ─────────────────────────────────────────────────────
# Join uses latest `ticker` row at-or-before f.time (within 30 days). This
# handles f.time falling on weekends/holidays AND Q4 reports whose time is set
# slightly after the latest available daily price (e.g. f.time = 2026-04-03 but
# ticker data ends 2026-03-30 → still want to use 2026-03-30 row).
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
    -- Growth-adjusted valuation: NP_R / PE = earnings growth per PE unit (1/PEG in decimal)
    -- Higher = growth is cheap relative to price; negative = shrinking earnings at positive PE
    CASE WHEN f.PE > 0 THEN SAFE_DIVIDE(f.NP_R, f.PE) ELSE NULL END AS growth_yield,
    f.PE, f.PB, f.PCF,
    f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
    f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
    f.Revenue_P4, f.Revenue_P5, f.Revenue_P6, f.Revenue_P7,
    -- Profitability-at-peak ratios: current vs 8Q max (1.0 = at peak, <0.5 = structural decline)
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
    t.time AS t_time, t.ICB_Code,
    t.Volume_3M_P50 * t.Close AS trading_value_1M,
    t.profit_3M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker
    AND t.time <= f.time
    AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2014-01-01"
    AND t.Volume_3M_P50 IS NOT NULL
    AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn, t_time) FROM joined WHERE rn = 1
"""

print("Fetching raw indicators ...")
df = bq_query(SQL, "raw")
print(f"  {len(df):,} (ticker, quarter) rows after liquidity filter")

# ─── Clip growth_yield to prevent outliers (e.g. PE=0.1 inflating ratio) ────
# growth_yield = NP_R / PE: typical range [-0.05, +0.10]; cap at ±0.15
df["growth_yield"] = df["growth_yield"].clip(lower=-0.15, upper=0.15)

# ─── DY sustainability discount: khi NP suy giam, DY ko con dang tin ─────────
# Logic: cong ty tra co tuc nhieu nhung loi nhuan dang giam -> DY tang ao do gia giam
#   NP_R >= 0          : DY_adj = DY            (no discount, earnings growing)
#   NP_R in [-0.5, 0)  : DY_adj = DY * (1 + 2*NP_R)   linear fade to 0
#   NP_R <= -0.5       : DY_adj = 0             (earnings halved YoY, dividend unsustainable)
# Formula: mult = clip(1 + 2*NP_R, 0, 1)  when NP_R < 0, else 1.0
_np_r        = df["NP_R"].fillna(0)
_mult        = np.where(_np_r >= 0, 1.0, np.clip(1 + 2 * _np_r, 0.0, 1.0))
df["DY_adj"] = df["DY"] * _mult          # DY discounted proportionally by NP_R decline
df["DY_sust"] = _mult                    # Standalone sustainability score (0-1)
# DY_sust is ADDED as a separate indicator in the Shareholder axis so that
# even when DY=0 (no dividend payers), NP decline still penalizes Sh score.
# Examples at key NP_R levels (applies to both DY_adj discount and DY_sust rank):
#   NP_R =  0%  -> mult=1.00  no penalty   (earnings flat/growing)
#   NP_R = -10% -> mult=0.80  20% discount
#   NP_R = -20% -> mult=0.60  40% discount
#   NP_R = -30% -> mult=0.40  60% discount
#   NP_R = -50% -> mult=0.00  fully eliminated (earnings halved YoY)

# ─── Stability metrics: CV of NP_P0..P7, Rev_P0..P7, and long-term CAGR ─────
NP_COLS  = [f"NP_P{i}"      for i in range(8)]
REV_COLS = [f"Revenue_P{i}" for i in range(8)]

np_arr  = df[NP_COLS].values.astype(float)
rev_arr = df[REV_COLS].values.astype(float)

# Need at least 6/8 quarters of data to compute reliable CV
np_n  = np.sum(~np.isnan(np_arr),  axis=1)
rev_n = np.sum(~np.isnan(rev_arr), axis=1)

with np.errstate(divide="ignore", invalid="ignore"):
    np_mean  = np.nanmean(np_arr,  axis=1)
    np_std   = np.nanstd(np_arr,   axis=1, ddof=1)
    rev_mean = np.nanmean(rev_arr, axis=1)
    rev_std  = np.nanstd(rev_arr,  axis=1, ddof=1)
    # CV uses |mean| to handle negatives; clamp tiny means to avoid blow-up
    df["NP_CV"]  = np.where(np_n  >= 6, np_std  / np.maximum(np.abs(np_mean),  1e6), np.nan)
    df["Rev_CV"] = np.where(rev_n >= 6, rev_std / np.maximum(np.abs(rev_mean), 1e6), np.nan)
    df["NP_CV"]  = df["NP_CV"].clip(upper=10)   # cap at 10 (any higher is "extreme volatile")
    df["Rev_CV"] = df["Rev_CV"].clip(upper=10)

# Long-term Revenue CAGR (annualized, 7 quarters span)
rev_p0 = df["Revenue_P0"].values; rev_p7 = df["Revenue_P7"].values
mask = (rev_p0 > 0) & (rev_p7 > 0)
df["LT_CAGR"] = np.where(mask, (rev_p0 / rev_p7) ** (4/7) - 1, np.nan)
df["LT_CAGR"] = df["LT_CAGR"].clip(lower=-0.95, upper=5.0)   # cap extremes

# ─── Industry-relative valuation z-scores (peer-aware) ──────────────────────
print("Computing industry-relative valuations ...")
df["ICB_Code"] = df["ICB_Code"].fillna("UNK")
for col in ["PE", "PB", "PCF"]:
    grp = df.groupby(["quarter", "ICB_Code"])[col]
    med = grp.transform("median")
    sd  = grp.transform("std")
    # If group too small (sd is NaN) fall back to global per-quarter z
    z_ind = (df[col] - med) / sd.replace(0, np.nan)
    z_global = df.groupby("quarter")[col].transform(
        lambda x: (x - x.median()) / x.std()
    )
    df[f"{col}_ind_z"] = z_ind.fillna(z_global)

# ─── Direction adjustment: lower-is-better cols negated so rank ascending=good ─
INV_COLS = ["Debt_Eq_P0",
            "PE_self_z", "PB_self_z",
            "PE_ind_z", "PB_ind_z", "PCF_ind_z",
            "NP_CV", "Rev_CV"]
for c in INV_COLS:
    df[c] = -df[c]

AXIS_COLS = {
    "quality":     ["ROIC5Y", "ROE_Min5Y", "FSCORE"],
    "stability":   ["NP_CV", "Rev_CV", "LT_CAGR"],
    "cash":        ["CF_OA_5Y", "CFOA_NP"],
    "shareholder": ["DY_adj", "Dividend_Min3Y", "FCF_OA_ratio", "DY_sust"],
    # DY_adj  = DY discounted by NP_R decline (absolute level)
    # DY_sust = sustainability multiplier 0-1 (relative rank; 0 = NP halved, 1 = growing)
    "growth":      ["NP_R", "Revenue_YoY_P0", "GPM_change", "NP_peak_ratio", "Rev_peak_ratio"],
    "health":      ["Debt_Eq_P0", "IntCov_P0", "CashR_P0"],
    "valuation":   ["PE_self_z", "PB_self_z", "PE_ind_z", "PB_ind_z", "PCF_ind_z",
                    "growth_yield"],   # NP_R/PE = growth per PE unit; catches PEG trap
}

# ─── Per-quarter percentile rank for each indicator ──────────────────────────
print("Computing per-quarter percentile ranks ...")
for cols in AXIS_COLS.values():
    for c in cols:
        df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

# ─── Axis composite (mean of available ranks; NaN-tolerant) ──────────────────
for axis, cols in AXIS_COLS.items():
    rank_cols = [f"r_{c}" for c in cols]
    df[f"score_{axis}"] = df[rank_cols].mean(axis=1, skipna=True)

# ─── Total weighted score ────────────────────────────────────────────────────
score_cols = [f"score_{a}" for a in WEIGHTS]
weights = np.array([WEIGHTS[a] for a in WEIGHTS])
df["total_score"] = (df[score_cols].values * weights).sum(axis=1)

# Drop rows where any axis is fully NaN
df = df.dropna(subset=score_cols, how="any").copy()
print(f"  {len(df):,} rows with full axis coverage")

# ─── Per-quarter total-score percentile → tier ───────────────────────────────
df["score_pct"] = df.groupby("quarter")["total_score"].rank(pct=True)

def tier_of(p):
    for name, lo, hi in TIERS:
        if lo <= p <= hi:
            return name
    return "E"
df["tier"] = df["score_pct"].apply(tier_of)

# ─── Save (both all-quarters and Q4-only) ────────────────────────────────────
keep = ["ticker", "quarter", "time", "trading_value_1M", "ICB_Code",
        "score_quality", "score_stability", "score_cash", "score_shareholder",
        "score_growth", "score_health", "score_valuation",
        "total_score", "score_pct", "tier", "profit_3M",
        "NP_CV", "Rev_CV", "LT_CAGR", "DY", "DY_adj", "DY_sust", "Dividend_Min3Y", "FCF_OA_ratio",
        "NP_R", "Revenue_YoY_P0", "NP_peak_ratio", "Rev_peak_ratio"]
out_all = df[keep].sort_values(["time", "tier", "ticker"], ascending=[False, True, True])
out_all.to_csv(OUT_ALL, index=False)
print(f"  Saved {OUT_ALL}    ({len(out_all):,} rows, all quarters)")

out_q4 = out_all[out_all["quarter"].str.endswith("Q4")].copy()
out_q4.to_csv(OUT_CSV, index=False)
print(f"  Saved {OUT_CSV}        ({len(out_q4):,} rows, Q4 only)")

# Use Q4-only for the validation block below
df = df[df["quarter"].str.endswith("Q4")].copy()

# ─── Validation: forward profit_3M by tier ──────────────────────────────────
print("\n=== Validation: forward profit_3M by tier (Q4-only history) ===")
print(f"{'Tier':<6}{'N':>8}{'Median':>10}{'Mean':>10}{'WinRate':>10}")
v = df.dropna(subset=["profit_3M"])
for tier in ["A", "B", "C", "D", "E"]:
    g = v[v["tier"] == tier]["profit_3M"]
    if len(g):
        print(f"{tier:<6}{len(g):>8,}{g.median():>9.2f}%{g.mean():>9.2f}%{(g>0).mean()*100:>9.1f}%")

# ─── Latest rating per ticker ────────────────────────────────────────────────
latest_per_tk = df.sort_values("time").groupby("ticker", as_index=False).tail(1)
latest_per_tk = latest_per_tk.sort_values(["tier", "total_score"],
                                          ascending=[True, False])
keep_latest = ["ticker", "quarter", "time", "trading_value_1M", "ICB_Code",
               "score_quality", "score_stability", "score_cash", "score_shareholder",
               "score_growth", "score_health", "score_valuation",
               "total_score", "score_pct", "tier",
               "NP_CV", "Rev_CV", "LT_CAGR", "DY", "DY_adj", "Dividend_Min3Y", "FCF_OA_ratio",
               "NP_R", "Revenue_YoY_P0", "NP_peak_ratio", "Rev_peak_ratio"]
latest_per_tk[keep_latest].to_csv(OUT_LATEST, index=False)
print(f"\n  Saved {OUT_LATEST}  ({len(latest_per_tk):,} tickers)")

print(f"\n=== Latest rating distribution (per ticker, latest report) ===")
print(f"{'Tier':<6}{'N':>6}{'MedScore':>10}{'MedTV(B)':>10}")
for tier in ["A", "B", "C", "D", "E"]:
    g = latest_per_tk[latest_per_tk["tier"] == tier]
    if len(g):
        print(f"{tier:<6}{len(g):>6}{g['total_score'].median():>10.3f}"
              f"{g['trading_value_1M'].median()/1e9:>10.2f}")

print(f"\nTop 20 A-tier picks (sorted by total_score):")
top = latest_per_tk[latest_per_tk["tier"] == "A"].head(20)
print(f"  {'Tkr':<6}{'Q':<8}{'ICB':<5}{'Score':>7}  Q    St   Cs   Sh   Gr   H    V   DY% DYadj NPpk RevPk")
for _, r in top.iterrows():
    dy_pct   = r.get("DY",     float("nan")) * 100
    dy_adj   = r.get("DY_adj", float("nan")) * 100      # discounted DY
    np_pk    = r.get("NP_peak_ratio", float("nan"))
    rev_pk   = r.get("Rev_peak_ratio", float("nan"))
    print(f"  {r['ticker']:<6}{r['quarter']:<8}{str(r['ICB_Code']):<5}"
          f"{r['total_score']:>7.3f}  "
          f"{r['score_quality']:.2f} {r['score_stability']:.2f} "
          f"{r['score_cash']:.2f} {r['score_shareholder']:.2f} "
          f"{r['score_growth']:.2f} {r['score_health']:.2f} "
          f"{r['score_valuation']:.2f}  {dy_pct:>4.1f} {dy_adj:>5.1f} {np_pk:>5.2f} {rev_pk:>5.2f}")

# ─── Data freshness warning (2-quarter rule) ──────────────────────────────────
# Tickers with rating > 180 days old are excluded from live picks.
# 180-400d range: likely data pipeline gap — investigate.
# >400d: likely delisted/inactive — informational only.
STALE_DAYS  = 180
LIKELY_DEAD = 400   # beyond this, assume delisted rather than pipeline error
TODAY_TS = pd.Timestamp.today().normalize()
latest_per_tk["rating_age"] = (TODAY_TS - latest_per_tk["time"]).dt.days

ab_mask = latest_per_tk["tier"].isin(["A", "B"])
pipeline_gap = latest_per_tk[ab_mask & (latest_per_tk["rating_age"].between(STALE_DAYS+1, LIKELY_DEAD))
                             ].sort_values(["tier", "total_score"], ascending=[True, False])
likely_dead  = latest_per_tk[ab_mask & (latest_per_tk["rating_age"] > LIKELY_DEAD)
                             ].sort_values("rating_age", ascending=False)

print(f"\n{'='*70}")
if len(pipeline_gap):
    print(f"=== DATA WARNING: {len(pipeline_gap)} A/B-tier tickers — PIPELINE GAP? ===")
    print(f"{'='*70}")
    print(f"  Rating age {STALE_DAYS+1}-{LIKELY_DEAD}d: missing Q3/Q4 data but still active.")
    print(f"  EXCLUDED from live_picks. Check BQ data for these tickers.\n")
    print(f"  {'Tkr':<7}{'Quarter':<9}{'LastReport':<12}{'Age(d)':>7}  Tier  Score")
    print(f"  {'-'*52}")
    for _, r in pipeline_gap.iterrows():
        print(f"  {r['ticker']:<7}{r['quarter']:<9}{str(r['time'].date()):<12}"
              f"{int(r['rating_age']):>7}  {r['tier']:<5} {r['total_score']:.3f}")
else:
    print(f"=== Data freshness OK: all A/B-tier tickers within {STALE_DAYS} days ===")
print(f"{'='*70}")
if len(likely_dead):
    print(f"  (Informational: {len(likely_dead)} A/B tickers with data >{LIKELY_DEAD}d old"
          f" — likely delisted/inactive, not actionable)")
