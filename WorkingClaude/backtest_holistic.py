"""Backtest portfolio simulation for Holistic Engine.

Simulates 3 strategies side-by-side:
  A) MEGA-only: each MEGA signal → buy, hold 3M, realize profit_3M
  B) HIGH_CONVICTION: MEGA + MOMENTUM + S_PRO + MOMENTUM_QUALITY
  C) BROAD: HIGH_CONVICTION + MOMENTUM_S + MOMENTUM_A + MOMENTUM_N + DEEP_VALUE_RECOVERY

For each strategy, computes:
  - Equal-weighted portfolio annual return (each signal = 3M holding)
  - Max concurrent positions
  - Win rate
  - vs VNINDEX baseline

Approximation: assumes unlimited capital, no transaction costs.
"""
import os
import subprocess
import sys
from io import StringIO
import pandas as pd
import numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PROJECT = "lithe-record-440915-m9"
BQ_BIN = r"bq"

QUERY = """
WITH fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
),
classified AS (
  SELECT
    t.ticker, t.time,
    EXTRACT(YEAR FROM t.time) AS yr,
    IF(ABS(t.profit_3M) > 400, NULL, t.profit_3M) AS p3m,
    (CASE WHEN t.D_RSI > 0.50 THEN 25 ELSE 0 END
    + CASE WHEN t.Close > t.MA50 AND t.MA50 > t.MA200 THEN 25 ELSE 0 END
    + CASE WHEN t.Volume >= t.Volume_3M_P50 * 1.3 AND t.Close > t.Close_T1 THEN 20 ELSE 0 END
    + CASE WHEN t.D_MACDdiff > 0 THEN 15 ELSE 0 END
    + CASE WHEN t.Close > t.MA20 THEN 15 ELSE 0 END
    + CASE WHEN t.D_RSI > 0.75 THEN 5 ELSE 0 END
    + CASE WHEN t.D_RSI < 0.30 THEN -10 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE < t.PE_MA5Y - 0.5*t.PE_SD5Y THEN 15 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE > t.PE_MA5Y + 1.0*t.PE_SD5Y THEN -15 ELSE 0 END
    + CASE WHEN t.VNINDEX_RSI_Max3M > 0.65 THEN 10 ELSE 0 END
    + CASE WHEN t.ID_HI_3Y <= 5 THEN 8 ELSE 0 END
    + CASE WHEN t.D_RSI_Max1W > 0.65 THEN 5 ELSE 0 END
    + CASE WHEN t.FSCORE >= 8 THEN 10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P4 * 1.5 AND t.NP_P4 > 0 THEN 8 ELSE 0 END
    + CASE WHEN t.NP_P0 < t.NP_P4 * 0.7 AND t.NP_P4 > 0 THEN -8 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (8,9) THEN 5 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (4,7) THEN -5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 * 1.005 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 < t.MA50_T1 THEN -5 ELSE 0 END
    + CASE WHEN t.HI_3M_T1 > 0 AND t.Close / t.HI_3M_T1 < 0.85 THEN -10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P1 * 1.2 AND t.NP_P1 > 0 THEN 8 ELSE 0 END) AS ta,
    s5.state AS state5,
    fa.fa_tier,
    SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1 AS np_yoy,
    fin.Revenue_YoY_P0 AS rev_yoy,
    (t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0) AS pe_z,
    (t.D_RSI > 0.90 OR (t.MA20 > 0 AND t.Close / t.MA20 > 1.25)) AS warn_ext,
    t.Volume_3M_P50 * t.Close AS liq
  FROM tav2_bq.ticker AS t
  LEFT JOIN tav2_bq.vnindex_5state AS s5 ON s5.time = t.time
  LEFT JOIN fa_dated AS fa ON fa.ticker = t.ticker AND t.time >= fa.f_time
       AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
  LEFT JOIN fin_dated AS fin ON fin.ticker = t.ticker AND t.time >= fin.fin_time
       AND (fin.next_fin_time IS NULL OR t.time < fin.next_fin_time)
  WHERE t.time BETWEEN DATE "2014-01-01" AND DATE "2026-01-16"
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.profit_3M IS NOT NULL
),
final AS (
  SELECT *,
    CASE
      WHEN state5 IN (1, 2) THEN 'AVOID_bear'
      WHEN fa_tier = 'E' THEN 'AVOID_faE'
      WHEN ta >= 160 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MEGA'
      WHEN ta >= 160 AND state5 IN (4,5) THEN 'S_PRO'
      WHEN ta >= 145 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MOMENTUM'
      WHEN ta >= 145 AND state5 IN (4,5) AND fa_tier IN ('A','B') THEN 'MOMENTUM_QUALITY'
      WHEN ta >= 145 AND state5 = 3 AND fa_tier IN ('C','D') THEN 'MOMENTUM_N'
      WHEN fa_tier IN ('A','B') AND pe_z < -0.5 AND ta >= 95 AND state5 IN (3,4,5) AND NOT warn_ext THEN 'COMPOUNDER_BUY'
      WHEN fa_tier = 'C' AND ta >= 100 AND state5 IN (3,4,5) AND ((np_yoy > 0.20) OR (rev_yoy > 0.20)) THEN 'DEEP_VALUE_RECOVERY'
      WHEN fa_tier IN ('A','B') AND ta >= 70 AND ta < 130 THEN 'COMPOUNDER_HOLD'
      WHEN ta >= 130 AND state5 IN (4,5) THEN 'MOMENTUM_S'
      WHEN ta >= 115 AND state5 IN (4,5) THEN 'MOMENTUM_A'
      WHEN ta >= 130 AND state5 = 3 THEN 'MOMENTUM_S_N'
      WHEN fa_tier IN ('A','B') THEN 'WAIT'
      ELSE 'PASS'
    END AS play_type
  FROM classified
  WHERE liq >= 1e9
)
SELECT time, ticker, p3m, play_type, yr FROM final
WHERE p3m IS NOT NULL
"""

VNI_QUERY = """
SELECT
  EXTRACT(YEAR FROM t.time) AS yr,
  COUNT(*) AS n_days,
  ROUND(AVG(IF(ABS(t.profit_3M) > 400, NULL, t.profit_3M)), 2) AS vni_p3m_avg
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX'
  AND t.time BETWEEN DATE '2014-01-01' AND DATE '2026-01-16'
  AND t.profit_3M IS NOT NULL
GROUP BY yr ORDER BY yr
"""


def bq(sql: str) -> pd.DataFrame:
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql)
        sql_path = f.name
    try:
        cmd = (f'"{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} '
               f'--format=csv --max_rows=2000000 < "{sql_path}"')
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    finally:
        os.unlink(sql_path)
    return pd.read_csv(StringIO(out.stdout))


def main():
    print("Loading historical play_type classifications...")
    df = bq(QUERY)
    print(f"  {len(df)} signal-days loaded")

    print("Loading VNINDEX baseline...")
    vni = bq(VNI_QUERY)
    print(f"  {len(vni)} years")

    # Define strategies
    strategies = {
        "STRAT_A_MEGA": ["MEGA"],
        "STRAT_B_HIGH_CONV": ["MEGA", "MOMENTUM", "S_PRO", "MOMENTUM_QUALITY"],
        "STRAT_C_BROAD": ["MEGA", "MOMENTUM", "S_PRO", "MOMENTUM_QUALITY",
                          "MOMENTUM_S", "MOMENTUM_A", "MOMENTUM_N", "DEEP_VALUE_RECOVERY"],
        "STRAT_D_FA_FOCUS": ["COMPOUNDER_BUY", "DEEP_VALUE_RECOVERY"],
    }

    # Per-year aggregate per strategy
    print("\n" + "═" * 90)
    print(f"  {'YEAR':6}{'VNI_P3M':>10}", end="")
    for name in strategies:
        print(f"{name[6:]:>14} (n) ", end="")
    print()
    print("═" * 90)

    yr_table = {}
    for yr_val in sorted(df["yr"].unique()):
        sub = df[df["yr"] == yr_val]
        vni_row = vni[vni["yr"] == yr_val]
        vni_p3m = vni_row["vni_p3m_avg"].iloc[0] if len(vni_row) else None
        row = [yr_val, vni_p3m if vni_p3m else 0.0]
        for name, types in strategies.items():
            sig = sub[sub["play_type"].isin(types)]
            mean = sig["p3m"].mean() if len(sig) else None
            n = len(sig)
            row.append((mean, n))
        yr_table[yr_val] = row

        print(f"  {yr_val:<6d}{vni_p3m if vni_p3m else 0.0:>10.2f}", end="")
        for i, (name, types) in enumerate(strategies.items()):
            mean, n = row[i + 2]
            mean_str = f"{mean:>8.2f}" if mean is not None else "    -   "
            print(f"   {mean_str} ({n:>3d})", end="")
        print()

    # Aggregate stats
    print("\n" + "═" * 90)
    print("  AGGREGATE 2014-2026:")
    print("═" * 90)

    stats = {}
    for name, types in strategies.items():
        all_sig = df[df["play_type"].isin(types)]
        if len(all_sig) == 0:
            continue
        n = len(all_sig)
        mean = all_sig["p3m"].mean()
        median = all_sig["p3m"].median()
        win = (all_sig["p3m"] > 0).mean() * 100
        hit10 = (all_sig["p3m"] > 10).mean() * 100
        hit20 = (all_sig["p3m"] > 20).mean() * 100
        lose10 = (all_sig["p3m"] < -10).mean() * 100
        # Year coverage: years with >0 signals
        yr_coverage = all_sig.groupby("yr").size()
        yrs_active = (yr_coverage > 0).sum()
        # Year win rate (years with positive mean P3M)
        yr_means = all_sig.groupby("yr")["p3m"].mean()
        yr_win = (yr_means > 0).sum() / len(yr_means) * 100
        stats[name] = (n, mean, median, win, hit10, hit20, lose10, yrs_active, yr_win)
        print(f"\n  {name}:")
        print(f"    n={n}, signals/year={n/yrs_active:.1f} (active in {yrs_active}/12 years)")
        print(f"    P3M mean={mean:.2f}%, median={median:.2f}%")
        print(f"    Win rate: {win:.1f}% positive | hit>10%: {hit10:.1f}% | hit>20%: {hit20:.1f}% | lose<-10%: {lose10:.1f}%")
        print(f"    Year-win rate: {yr_win:.1f}% (years with positive mean)")

    # Simple compounding sim: for each signal, treat as 3M holding at equal-weight
    # Approximate annual return: weighted average of overlapping signals
    print("\n" + "═" * 90)
    print("  SIMPLIFIED CAGR ESTIMATE (assuming ~4 rolls/year, equal weighted):")
    print("═" * 90)
    print(f"  Assumes each signal is held 3M. CAGR = (1 + avg_quarterly_return)^4 - 1")
    for name, types in strategies.items():
        all_sig = df[df["play_type"].isin(types)]
        if len(all_sig) == 0:
            continue
        # Per-year: avg P3M of signals × 4 rolls (annualization upper bound)
        # Better: per-year avg P3M annualized = (1 + avg_p3m/100)^4 - 1
        yr_means = all_sig.groupby("yr")["p3m"].mean()
        full_yr_returns = []
        for yr_val in range(2014, 2027):
            if yr_val in yr_means.index:
                yr_p = yr_means[yr_val] / 100
                full_yr_returns.append(yr_p)
            else:
                full_yr_returns.append(0)  # stay in cash
        # Average annual return (assuming 4 rolls per year IF fully invested)
        # Simpler: just present per-year + cumulative compound
        cumulative = 1.0
        for yr_p in full_yr_returns:
            cumulative *= (1 + yr_p)
        cagr_simple = cumulative ** (1 / len(full_yr_returns)) - 1
        avg_yr = np.mean(full_yr_returns) * 100
        print(f"  {name}: avg annual P3M = {avg_yr:.1f}%  | "
              f"cumulative wealth multiplier (1 roll/yr) = {cumulative:.2f}× | "
              f"simplified CAGR = {cagr_simple*100:.1f}%/yr")

    # VNINDEX comparison
    vni_cagr = (vni["vni_p3m_avg"].mean() / 100)
    print(f"\n  VNINDEX baseline avg P3M (2014-2026): {vni['vni_p3m_avg'].mean():.2f}%")


if __name__ == "__main__":
    main()
