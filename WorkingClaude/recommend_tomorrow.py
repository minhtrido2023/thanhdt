# -*- coding: utf-8 -*-
"""Live BA-system recommendation for NEXT trading day, using ticker_1m
(rolling snapshot) when daily ticker data is stale.

Usage:  python recommend_tomorrow.py [signal_date_YYYY-MM-DD]
        (default: latest available date in ticker_1m)

Logic identical to recommend_holistic.py v10 but reads tav2_bq.ticker_1m
instead of tav2_bq.ticker. Forward-fills latest 5-state.
"""
import os
import sys

import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

# Note: recommend_holistic.py wraps sys.stdout at import; do not double-wrap.
from recommend_holistic import (bq, load_fa_full, classify_play_type,
                                 select_book, print_book, print_f_overlay,
                                 BA_CORE_TIERS)

# ─── v10 SQL but reading ticker_1m ──────────────────────────────────────────
SCORE_SQL_1M = """
WITH fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier_hist,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
latest_state AS (
  -- 2026-06-03: use vnindex_5state_dt5g_live (TRUE production DT5G regime) not the bare
  -- `vnindex_5state` table, which is the v3.4b BASE (TQ34b, no DT-gate/macro).
  SELECT s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s
  ORDER BY s.time DESC LIMIT 1
)
SELECT
  t.ticker, t.time, t.Close, t.Volume,
  ROUND(t.D_RSI, 2) AS rsi,
  ROUND(t.D_MACDdiff, 1) AS macd_diff,
  ROUND(t.Close / NULLIF(t.MA50,0) - 1, 3) AS vs_ma50,
  ROUND(t.MA50 / NULLIF(t.MA50_T1,0) - 1, 4) AS ma50_slope,
  ROUND(t.Close / NULLIF(t.HI_3M_T1,0) - 1, 3) AS vs_3m_high,
  ROUND(t.PE, 1) AS pe,
  ROUND((t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0), 2) AS pe_zscore,
  CAST(t.FSCORE AS INT64) AS fscore,
  ROUND(SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1, 2) AS np_yoy,
  ROUND(SAFE_DIVIDE(t.NP_P0, t.NP_P1) - 1, 2) AS np_qoq,
  CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sector_top,
  fa.fa_tier_hist,
  (SELECT state FROM latest_state) AS state5,
  ROUND(t.Volume_3M_P50 * t.Close / 1e9, 2) AS liq_b_vnd,
  -- v10 TA score
  CASE WHEN t.D_RSI > 0.50 THEN 25 ELSE 0 END
  + CASE WHEN t.Close > t.MA50 AND t.MA50 > t.MA200 THEN 25 ELSE 0 END
  + CASE WHEN t.Volume >= t.Volume_3M_P50 * 1.3 AND t.Close > t.Close_T1 THEN 20 ELSE 0 END
  + CASE WHEN t.D_MACDdiff > 0 THEN 15 ELSE 0 END
  + CASE WHEN t.Close > t.MA20 THEN 15 ELSE 0 END
  + CASE WHEN t.D_RSI > 0.75 THEN 5 ELSE 0 END
  + CASE WHEN t.D_RSI < 0.30 THEN -10 ELSE 0 END
  + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE < t.PE_MA5Y - 0.5*t.PE_SD5Y THEN 15 ELSE 0 END
  + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE > t.PE_MA5Y + 1.0*t.PE_SD5Y THEN -15 ELSE 0 END
  -- VNINDEX_RSI_Max3M not in ticker_1m; condition omitted (max -10pt)
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
  + CASE WHEN t.NP_P0 > t.NP_P1 * 1.2 AND t.NP_P1 > 0 THEN 8 ELSE 0 END
  + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64) = 8 AND fa.fa_tier_hist = 'D' THEN 10 ELSE 0 END
  + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64) = 8 AND fa.fa_tier_hist = 'A' THEN -10 ELSE 0 END
  AS ta_score,
  CASE WHEN t.D_RSI > 0.90 THEN 1 ELSE 0 END AS warn_rsi_blowoff,
  CASE WHEN t.MA20 > 0 AND t.Close / t.MA20 > 1.25 THEN 1 ELSE 0 END AS warn_extended_ma20,
  CASE WHEN t.HI_3M_T1 > 0 AND t.Close / t.HI_3M_T1 < 0.85 THEN 1 ELSE 0 END AS warn_dd_deep
FROM tav2_bq.ticker_1m AS t
LEFT JOIN fa_dated AS fa
  ON fa.ticker = t.ticker AND t.time >= fa.f_time
 AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
WHERE t.time = DATE '{day}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.D_RSI IS NOT NULL
ORDER BY ta_score DESC
"""

LATEST_DATE_SQL_1M = ("SELECT MAX(t.time) AS d FROM tav2_bq.ticker_1m AS t "
                      "WHERE t.D_RSI IS NOT NULL")

VN30_QUERY = """
SELECT t.ticker
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker
ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC
LIMIT 30
"""


def main():
    target = (sys.argv[1] if len(sys.argv) > 1
              else str(bq(LATEST_DATE_SQL_1M)["d"].iloc[0]))

    print("=" * 88)
    print(f"  🏆 BA-SYSTEM TOMORROW WATCHLIST — signal close {target} (T+1 entry next session)")
    print(f"     Source: tav2_bq.ticker_1m (rolling snapshot)")
    print(f"     Strategy: 50% BAL+Fin/RE-max-4 + 50% VN30_BAL")
    print(f"     PM: max=10pos, hold=45d, stop=-20%, BL20, T+3 min hold")
    print("=" * 88)

    print("\n[1/4] Loading TA v10 scoring + latest 5-state…")
    ta_df = bq(SCORE_SQL_1M.format(day=target))
    print(f"      {len(ta_df)} tickers scored")

    print("[2/4] Loading FA 7-axis breakdown…")
    fa_df = load_fa_full(target)
    print(f"      {len(fa_df)} tickers with FA snapshot")

    print("[3/4] Loading VN30 universe (top 30 by avg liq 2020-2025)…")
    vn30_set = set(bq(VN30_QUERY)["ticker"])
    print(f"      {len(vn30_set)} VN30 tickers: "
          f"{', '.join(sorted(vn30_set)[:10])}, …")

    print("[4/4] Cross-referencing & classifying…")
    fa_cols = ["ticker", "tier", "total_score", "score_quality", "score_stability",
               "score_cash", "score_shareholder", "score_growth", "score_health",
               "score_valuation", "NP_R", "Revenue_YoY_P0", "NP_peak_ratio",
               "Rev_peak_ratio"]
    fa_subset = fa_df[fa_cols].rename(columns={"tier": "fa_tier",
                                                "total_score": "fa_total_score"})
    df = ta_df.merge(fa_subset, on="ticker", how="left")

    LIQ_FLOOR = 1.0
    df_liq = df[df["liq_b_vnd"] >= LIQ_FLOOR].copy()

    play_results = df_liq.apply(classify_play_type, axis=1, result_type="expand")
    play_results.columns = ["play_type", "conviction", "action_note"]
    df_liq = pd.concat([df_liq, play_results], axis=1)
    df_liq = df_liq.sort_values("conviction", ascending=False).reset_index(drop=True)

    state5 = df_liq["state5"].dropna().iloc[0] if df_liq["state5"].notna().any() else None
    state_names = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
    state_label = state_names.get(int(state5)) if state5 else "?"
    print(f"\n  Market regime (5-state, latest available): {state_label} (state={state5})")
    print(f"  Note: 5-state data may be older than {target} signal date.")

    if state5 is not None and int(state5) in (1, 2):
        print("\n  ❌ BEAR/CRISIS regime — BA-system goes to cash. No new entries.")
        print_f_overlay(state5)
        out_path = os.path.join(WORKDIR, f"holistic_tomorrow_{target}.csv")
        df_liq.to_csv(out_path, index=False)
        return

    bal_universe = df_liq.copy()
    vn30_universe = df_liq[df_liq["ticker"].isin(vn30_set)].copy()

    bal_book = select_book(bal_universe, max_positions=10, fin_re_cap=4)
    vn30_book = select_book(vn30_universe, max_positions=10, fin_re_cap=None)

    print_book(bal_book, "BOOK A — BAL+Fin/RE-max-4 (full ticker_prune)", 50)
    print_book(vn30_book, "BOOK B — VN30_BAL (top 30 liquidity)", 50)
    print_f_overlay(state5)

    # Distribution summary
    print(f"\n{'═' * 88}")
    print("  PLAY TYPE DISTRIBUTION (entire scored universe)")
    print(f"{'═' * 88}")
    pt_counts = df_liq["play_type"].value_counts()
    order = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY",
             "MOMENTUM_S_N", "MOMENTUM_A", "MOMENTUM_QUALITY", "S_PRO",
             "COMPOUNDER_BUY", "COMPOUNDER_HOLD", "WAIT", "PASS",
             "AVOID_bear", "AVOID_faE"]
    for pt in order:
        n = pt_counts.get(pt, 0)
        if n:
            tag = " ⭐ BA-core" if pt in BA_CORE_TIERS else ""
            print(f"  {pt:22} {n:4d}{tag}")

    cols_show = ["ticker", "Close", "ta_score", "fa_tier", "fa_total_score",
                 "rsi", "ma50_slope", "vs_3m_high", "pe_zscore",
                 "np_yoy", "sector_top", "liq_b_vnd"]
    HIGH_CONV = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S",
                 "DEEP_VALUE_RECOVERY", "MOMENTUM_QUALITY", "COMPOUNDER_BUY"]
    for pt in HIGH_CONV:
        sub = df_liq[df_liq["play_type"] == pt]
        if sub.empty:
            continue
        print(f"\n{'─' * 88}")
        print(f"  {pt}  ({len(sub)} mã)  → {sub.iloc[0]['action_note']}")
        print(f"{'─' * 88}")
        print(sub[cols_show].head(15).to_string(index=False,
            float_format=lambda x: f"{x:.2f}"))

    out_path = os.path.join(WORKDIR, f"holistic_tomorrow_{target}.csv")
    df_liq.to_csv(out_path, index=False)
    bal_path = os.path.join(WORKDIR, f"ba_book_bal_tomorrow_{target}.csv")
    vn30_path = os.path.join(WORKDIR, f"ba_book_vn30_tomorrow_{target}.csv")
    if not bal_book.empty:
        bal_book.to_csv(bal_path, index=False)
    if not vn30_book.empty:
        vn30_book.to_csv(vn30_path, index=False)

    print(f"\n  Full universe saved: {out_path}")
    if not bal_book.empty:
        print(f"  BAL book saved:      {bal_path}")
    if not vn30_book.empty:
        print(f"  VN30 book saved:     {vn30_path}")

    print(f"\n  ┌{'─' * 86}┐")
    print(f"  │  💡 Execution checklist for next session (T+1 entry):")
    print(f"  │    • BAL book: {len(bal_book)} positions × 5% NAV = {len(bal_book) * 5}% deployed")
    print(f"  │    • VN30 book: {len(vn30_book)} positions × 5% NAV = {len(vn30_book) * 5}% deployed")
    print(f"  │    • Each position ~5% NAV (with 50B wallet, ~2.5B per position)")
    print(f"  │    • Stop loss -20% from entry, hold 45d, BL20 after stop")
    print(f"  │    • If T-3 ago you stopped a ticker, do NOT re-enter")
    print(f"  └{'─' * 86}┘")


if __name__ == "__main__":
    main()
