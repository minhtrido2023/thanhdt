# -*- coding: utf-8 -*-
"""Compare BA-system v10 + V6 ETF + F1 Fresh-Q filter with:
  A) Original 5-state (vnindex_5state_baseline_pre_v2g_20260517_144254)
  B) v2g 5-state (current vnindex_5state — earlier CRISIS exit, no smoothing)

Period: 2014-01-01 → 2026-03-30 (full history)
Config: 50/50 BAL+Fin/RE-max-4 + VN30_BAL at 50B, V6 ETF 70% NEUTRAL, 1% deposit,
        F1 Fresh-Q ≤60d filter via SQL
"""
import os
import sys
import io

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY

START_DATE = "2014-01-01"
END_DATE = "2026-03-30"
TOTAL_NAV = 50e9
BOOK_NAV = 25e9

# v10 SQL with F1 Fresh-Q filter baked in, using configurable state table
SIGNAL_V10_WITH_F1 = """
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
-- Compute VNINDEX_RSI_Max3M from raw VNI D_RSI (rolling MAX over 60 sessions)
vni_history AS (
  SELECT t.time, t.D_RSI
  FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL
),
vni_max3m AS (
  SELECT time,
    MAX(D_RSI) OVER (ORDER BY time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS rsi_max3m
  FROM vni_history
),
classified AS (
  SELECT t.ticker, t.time, t.Close,
    (CASE WHEN t.D_RSI > 0.50 THEN 25 ELSE 0 END
    + CASE WHEN t.Close > t.MA50 AND t.MA50 > t.MA200 THEN 25 ELSE 0 END
    + CASE WHEN t.Volume >= t.Volume_3M_P50 * 1.3 AND t.Close > t.Close_T1 THEN 20 ELSE 0 END
    + CASE WHEN t.D_MACDdiff > 0 THEN 15 ELSE 0 END
    + CASE WHEN t.Close > t.MA20 THEN 15 ELSE 0 END
    + CASE WHEN t.D_RSI > 0.75 THEN 5 ELSE 0 END
    + CASE WHEN t.D_RSI < 0.30 THEN -10 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE < t.PE_MA5Y - 0.5*t.PE_SD5Y THEN 15 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE > t.PE_MA5Y + 1.0*t.PE_SD5Y THEN -15 ELSE 0 END
    + CASE WHEN vmax.rsi_max3m > 0.65 THEN 10 ELSE 0 END
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
    + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64)=8 AND fa.fa_tier='D' THEN 10 ELSE 0 END
    + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64)=8 AND fa.fa_tier='A' THEN -10 ELSE 0 END) AS ta,
    s5.state AS state5, fa.fa_tier,
    SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1 AS np_yoy,
    fin.Revenue_YoY_P0 AS rev_yoy,
    (t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0) AS pe_z,
    (t.D_RSI > 0.90 OR (t.MA20 > 0 AND t.Close / t.MA20 > 1.25)) AS warn_ext,
    t.Volume_3M_P50 * t.Close AS liq,
    CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec,
    rel.days_since_release
  FROM tav2_bq.ticker AS t
  LEFT JOIN tav2_bq.{state_table} AS s5 ON s5.time = t.time
  LEFT JOIN vni_max3m AS vmax ON vmax.time = t.time
  LEFT JOIN fa_dated AS fa
    ON fa.ticker = t.ticker AND t.time >= fa.f_time
   AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
  LEFT JOIN fin_dated AS fin
    ON fin.ticker = t.ticker AND t.time >= fin.fin_time
   AND (fin.next_fin_time IS NULL OR t.time < fin.next_fin_time)
  LEFT JOIN (
    SELECT t2.ticker, t2.time,
      DATE_DIFF(t2.time, MAX(tf.Release_Date), DAY) AS days_since_release
    FROM (
      SELECT DISTINCT t3.ticker, t3.time
      FROM tav2_bq.ticker AS t3
      WHERE t3.time BETWEEN DATE '{start}' AND DATE '{end}'
        AND t3.ticker IN (SELECT DISTINCT t4.ticker FROM tav2_bq.ticker_prune AS t4)
    ) AS t2
    LEFT JOIN tav2_bq.ticker_financial AS tf
      ON tf.ticker = t2.ticker AND tf.Release_Date <= t2.time
    GROUP BY t2.ticker, t2.time
  ) AS rel ON rel.ticker = t.ticker AND rel.time = t.time
  WHERE t.time BETWEEN DATE '{start}' AND DATE '{end}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
)
SELECT ticker, time, Close,
  CASE
    WHEN state5 IN (1, 2) THEN 'AVOID_bear'
    WHEN fa_tier = 'E' THEN 'AVOID_faE'
    -- BA-core with F1 Fresh-Q filter (≤60d since release)
    WHEN ta >= 170 AND state5 IN (4,5) AND fa_tier IN ('C','D')
         AND days_since_release IS NOT NULL AND days_since_release <= 60 THEN 'MEGA'
    WHEN ta >= 170 AND state5 IN (4,5) THEN 'S_PRO'
    WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('C','D')
         AND days_since_release IS NOT NULL AND days_since_release <= 60 THEN 'MOMENTUM'
    WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('A','B') THEN 'MOMENTUM_QUALITY'
    WHEN ta >= 155 AND state5 = 3 AND fa_tier IN ('C','D')
         AND days_since_release IS NOT NULL AND days_since_release <= 60 THEN 'MOMENTUM_N'
    WHEN fa_tier IN ('A','B') AND pe_z < -0.5 AND ta >= 95 AND state5 IN (3,4,5) AND NOT warn_ext THEN 'COMPOUNDER_BUY'
    WHEN fa_tier = 'C' AND ta >= 100 AND state5 IN (4,5) AND ((np_yoy > 0.20) OR (rev_yoy > 0.20))
         AND days_since_release IS NOT NULL AND days_since_release <= 60 THEN 'DEEP_VALUE_RECOVERY'
    WHEN ta >= 140 AND state5 IN (4,5)
         AND days_since_release IS NOT NULL AND days_since_release <= 60 THEN 'MOMENTUM_S'
    WHEN ta >= 125 AND state5 IN (4,5) THEN 'MOMENTUM_A'
    WHEN ta >= 140 AND state5 = 3 THEN 'MOMENTUM_S_N'
    WHEN fa_tier IN ('A','B') AND ta >= 70 AND ta < 130 THEN 'COMPOUNDER_HOLD'
    WHEN fa_tier IN ('A','B') THEN 'WAIT'
    ELSE 'PASS'
  END AS play_type,
  ta, liq, sec
FROM classified WHERE liq >= 1e9
"""

print("=" * 100)
print("  v2g vs ORIGINAL 5-state — full BA-system v10 + V6 ETF + F1 stack")
print(f"  Period: {START_DATE} → {END_DATE} | NAV 50B (25B/book × 2)")
print("=" * 100)

# Common data (shared between 2 variants)
print("\n[Common] Loading prices + sector + VN30 + VNI dates…")
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

vn30_underlying = dict(zip(vni["time"], vni["Close"]))

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]


def run_variant(state_table_name: str, label: str):
    """Run full BA-system v10 + V6 + F1 with specified state table."""
    print(f"\n[{label}] Loading signals from state table: {state_table_name}…")
    sig = bq(SIGNAL_V10_WITH_F1.format(
        start=START_DATE, end=END_DATE, state_table=state_table_name))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"  {len(sig):,} signal rows")

    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

    # State by date for ETF parking
    state_df = bq(f"SELECT s.time, s.state FROM tav2_bq.{state_table_name} AS s "
                   f"WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time")
    state_df["time"] = pd.to_datetime(state_df["time"])
    state_by_date = dict(zip(state_df["time"], state_df["state"]))

    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
    DEPOSIT = 0.01
    ETF_STATES = {3: 0.7}

    # BAL book
    nav_bal, trades_bal = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=state_by_date,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
        **LIQ_FULL, name=f"{label}_BAL")
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    # VN30 book
    sig_vn30 = sig[sig["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=state_by_date,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
        **LIQ_VN30, name=f"{label}_VN30")
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    # Combine
    nav_bal_s = nav_bal.set_index("time")["nav"]
    nav_vn30_s = nav_vn30.set_index("time")["nav"]
    common = nav_bal_s.index.intersection(nav_vn30_s.index)
    nav_total = nav_bal_s.loc[common] + nav_vn30_s.loc[common]
    df_nav = pd.DataFrame({"time": common, "nav": nav_total.values})

    all_trades = pd.concat([trades_bal, trades_vn30], ignore_index=True)
    m = metrics(df_nav, all_trades, label)
    win = (all_trades["ret_net"] > 0).mean() * 100 if len(all_trades) else 0
    avg_ret = all_trades["ret_net"].mean() * 100 if len(all_trades) else 0
    stop_pct = (all_trades["reason"] == "STOP").mean() * 100 if len(all_trades) else 0

    return {
        "label": label, **m,
        "win_pct": win, "avg_ret_pct": avg_ret, "stop_pct": stop_pct,
        "final_nav_b": nav_total.iloc[-1] / 1e9,
    }, df_nav, all_trades


results = []
nav_traces = {}
trade_logs = {}

# Run Original first
r_orig, nav_orig, trades_orig = run_variant(
    "vnindex_5state_baseline_pre_v2g_20260517_144254",
    "ORIGINAL 5-state")
results.append(r_orig)
nav_traces["ORIGINAL"] = nav_orig
trade_logs["ORIGINAL"] = trades_orig

# Run v2g
r_v2g, nav_v2g, trades_v2g = run_variant(
    "vnindex_5state",
    "v2g 5-state (current production)")
results.append(r_v2g)
nav_traces["v2g"] = nav_v2g
trade_logs["v2g"] = trades_v2g

# Print summary
print("\n" + "=" * 100)
print("  📊 RESULTS")
print("=" * 100)
print()
print(f"  {'Variant':<45} {'CAGR':>8} {'Sharpe':>7} {'DD':>8} {'Calmar':>7} {'Trades':>7} {'Win%':>6} {'NAV end':>10}")
print(f"  {'-'*45} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*7} {'-'*6} {'-'*10}")
for r in results:
    print(f"  {r['label']:<45} {r['cagr_pct']:>+7.2f}% {r['sharpe']:>+7.2f} "
          f"{r['max_dd_pct']:>+7.1f}% {r['calmar']:>+7.2f} {r['n_trades']:>7d} "
          f"{r['win_pct']:>+5.1f}% {r['final_nav_b']:>+8.2f}B")

# Δ analysis
base = results[0]
v2g = results[1]
print(f"\n  Δ v2g vs ORIGINAL:")
print(f"    ΔCAGR    : {v2g['cagr_pct']-base['cagr_pct']:+.2f}pp")
print(f"    ΔSharpe  : {v2g['sharpe']-base['sharpe']:+.2f}")
print(f"    ΔDD      : {v2g['max_dd_pct']-base['max_dd_pct']:+.1f}pp")
print(f"    ΔCalmar  : {v2g['calmar']-base['calmar']:+.2f}")
print(f"    ΔTrades  : {v2g['n_trades']-base['n_trades']:+d}")
print(f"    ΔWin%    : {v2g['win_pct']-base['win_pct']:+.1f}pp")
print(f"    ΔNAV end : {v2g['final_nav_b']-base['final_nav_b']:+.2f}B (= {(v2g['final_nav_b']/base['final_nav_b']-1)*100:+.1f}% more wealth)")

# Yearly NAV evolution
print(f"\n  Yearly NAV multiplier (start 50B):")
print(f"  {'Year':<6} {'ORIGINAL':>12} {'v2g':>12} {'Δ':>10}")
y_orig = nav_orig.set_index("time")["nav"].resample("YE").last() / TOTAL_NAV
y_v2g = nav_v2g.set_index("time")["nav"].resample("YE").last() / TOTAL_NAV
for ts in y_orig.index:
    yr = ts.year
    if yr not in [t.year for t in y_v2g.index]:
        continue
    a = y_orig.get(ts, np.nan)
    matching = [t for t in y_v2g.index if t.year == yr]
    b = y_v2g.get(matching[0], np.nan) if matching else np.nan
    delta = b - a
    arrow = "↑" if delta > 0.05 else ("↓" if delta < -0.05 else "≈")
    print(f"  {yr:<6} {a:>+11.2f}× {b:>+11.2f}× {delta:>+8.2f}× {arrow}")

# Save
df_res = pd.DataFrame(results)
df_res.to_csv(os.path.join(WORKDIR, "data/v2g_vs_original_results.csv"), index=False)
print(f"\n  Saved: v2g_vs_original_results.csv")
