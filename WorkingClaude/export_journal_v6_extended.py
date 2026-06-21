# -*- coding: utf-8 -*-
"""Export BA-system v10.1 (with V6 ETF parking) journal — EXTENDED 2025-06-01 → 2026-04-30.

Uses UNIFIED ticker + ticker_1m UNION to cover full requested period:
  - ticker (canonical) for ≤ 2026-03-30
  - ticker_1m for 2026-03-31 → 2026-04-30
  - VNINDEX_RSI_Max3M frozen from latest ticker for ticker_1m dates
  - 5-state forward-fill for dates > vnindex_5state.MAX

Config: BA-system 50/50 + V6 ETF parking (70% NEU), 1% deposit, all friction.
"""
import os
import sys
import io
from datetime import timedelta

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY

START_DATE = "2025-06-01"
END_DATE   = "2026-04-30"
TOTAL_NAV  = 50_000_000_000
BOOK_NAV   = TOTAL_NAV / 2

# ─── UNIFIED v10 SQL: UNION ticker + ticker_1m ──────────────────────────────
# ticker_1m missing VNINDEX_RSI_Max3M → use latest known value from ticker
SIGNAL_V10_UNIFIED = """
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
-- Compute VNINDEX_RSI_Max3M from raw VNI D_RSI (UNION ticker VNINDEX + ticker_1m VNI),
-- rolling MAX over last 60 sessions per date.
vni_history AS (
  SELECT t.time, t.D_RSI FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL
  UNION ALL
  SELECT t.time, t.D_RSI FROM tav2_bq.ticker_1m AS t
  WHERE t.ticker = 'VNI' AND t.D_RSI IS NOT NULL
    AND NOT EXISTS (
      SELECT 1 FROM tav2_bq.ticker AS t2
      WHERE t2.time = t.time AND t2.ticker = 'VNINDEX' AND t2.D_RSI IS NOT NULL
    )
),
vni_max3m AS (
  SELECT time,
    MAX(D_RSI) OVER (ORDER BY time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS rsi_max3m
  FROM vni_history
),
ticker_data AS (
  -- Path A: ticker canonical (preferred, with D_RSI filter)
  SELECT t.ticker, t.time, t.Close, t.Volume, t.D_RSI, t.D_MACDdiff,
         t.MA20, t.MA50, t.MA200, t.MA50_T1, t.Close_T1,
         t.HI_3M_T1, t.ID_HI_3Y, t.D_RSI_Max1W,
         t.PE, t.PE_MA5Y, t.PE_SD5Y, t.FSCORE,
         t.NP_P0, t.NP_P1, t.NP_P4, t.ICB_Code, t.Volume_3M_P50
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE '{start}' AND DATE '{end}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.D_RSI IS NOT NULL

  UNION ALL

  -- Path B: ticker_1m — when ticker has NO D_RSI row for this (ticker, date)
  SELECT t.ticker, t.time, t.Close, t.Volume, t.D_RSI, t.D_MACDdiff,
         t.MA20, t.MA50, t.MA200, t.MA50_T1, t.Close_T1,
         t.HI_3M_T1, t.ID_HI_3Y, t.D_RSI_Max1W,
         t.PE, t.PE_MA5Y, t.PE_SD5Y, t.FSCORE,
         t.NP_P0, t.NP_P1, t.NP_P4, t.ICB_Code, t.Volume_3M_P50
  FROM tav2_bq.ticker_1m AS t
  WHERE t.time BETWEEN DATE '{start}' AND DATE '{end}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.D_RSI IS NOT NULL
    AND NOT EXISTS (
      SELECT 1 FROM tav2_bq.ticker AS t2
      WHERE t2.time = t.time AND t2.ticker = t.ticker AND t2.D_RSI IS NOT NULL
    )
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
    s5_ff.state AS state5, fa.fa_tier,
    SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1 AS np_yoy,
    fin.Revenue_YoY_P0 AS rev_yoy,
    (t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0) AS pe_z,
    (t.D_RSI > 0.90 OR (t.MA20 > 0 AND t.Close / t.MA20 > 1.25)) AS warn_ext,
    t.Volume_3M_P50 * t.Close AS liq,
    CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec,
    rel.days_since_release
  FROM ticker_data AS t
  LEFT JOIN fa_dated AS fa
    ON fa.ticker = t.ticker AND t.time >= fa.f_time
   AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
  LEFT JOIN fin_dated AS fin
    ON fin.ticker = t.ticker AND t.time >= fin.fin_time
   AND (fin.next_fin_time IS NULL OR t.time < fin.next_fin_time)
  LEFT JOIN vni_max3m AS vmax ON vmax.time = t.time
  -- Days since latest quarterly Release_Date (for Fresh-Q filter, round 19 adoption)
  LEFT JOIN (
    SELECT t2.ticker, t2.time,
      DATE_DIFF(t2.time, MAX(tf.Release_Date), DAY) AS days_since_release
    FROM (SELECT DISTINCT ticker, time FROM ticker_data) AS t2
    LEFT JOIN tav2_bq.ticker_financial AS tf
      ON tf.ticker = t2.ticker AND tf.Release_Date <= t2.time
    GROUP BY t2.ticker, t2.time
  ) AS rel ON rel.ticker = t.ticker AND rel.time = t.time
  -- Forward-filled 5-state: latest state on or before t.time
  LEFT JOIN (
    SELECT t2.time, ARRAY_AGG(s.state ORDER BY s.time DESC LIMIT 1)[OFFSET(0)] AS state
    FROM (SELECT DISTINCT time FROM ticker_data) AS t2
    LEFT JOIN tav2_bq.vnindex_5state AS s ON s.time <= t2.time
    GROUP BY t2.time
  ) AS s5_ff ON s5_ff.time = t.time
)
SELECT ticker, time, Close,
  CASE
    WHEN state5 IN (1, 2) THEN 'AVOID_bear'
    WHEN fa_tier = 'E' THEN 'AVOID_faE'
    -- BA-core tiers require Fresh-Q: days_since_release ≤ 60 (round 19 adoption)
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
  ta, liq, sec, days_since_release
FROM classified
WHERE liq >= 1e9
"""

# ─── VNI date list (UNION ticker + ticker_1m for VNINDEX in date range) ─────
VNI_QUERY_UNIFIED = """
WITH all_vni AS (
  SELECT t.time, t.Close FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{start}' AND DATE '{end}'
  UNION ALL
  -- ticker_1m uses symbol 'VNI' (not VNINDEX)
  SELECT t.time, t.Close FROM tav2_bq.ticker_1m AS t
  WHERE t.ticker = 'VNI' AND t.time BETWEEN DATE '{start}' AND DATE '{end}'
    AND t.time > (SELECT MAX(t2.time) FROM tav2_bq.ticker AS t2 WHERE t2.ticker = 'VNINDEX')
)
SELECT time, Close FROM all_vni ORDER BY time
"""

print("=" * 100)
print(f"  BA-SYSTEM v10.1 JOURNAL EXTENDED — {START_DATE} → {END_DATE}")
print(f"  NAV: {TOTAL_NAV/1e9:.1f}B ({BOOK_NAV/1e9:.1f}B/book × 2)")
print(f"  Data: ticker (canonical) + ticker_1m fallback for recent dates")
print("=" * 100)

# ─── 1. Load signals (unified) ──────────────────────────────────────────────
print("\n[1/6] Loading unified signals (ticker + ticker_1m)…")
sig = bq(SIGNAL_V10_UNIFIED.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"      {len(sig):,} signal rows; date range "
      f"{sig['time'].min().date()} → {sig['time'].max().date()}")

# Check coverage
date_count = sig.groupby("time")["ticker"].count()
print(f"      Unique trading dates: {len(date_count)}")
print(f"      Avg tickers/date: {date_count.mean():.0f}, "
      f"first {sig['time'].min().date()}, last {sig['time'].max().date()}")

# Verify recent dates (post 2026-03-30) come from ticker_1m
recent_dates = sorted(sig[sig["time"] > pd.Timestamp("2026-03-30")]["time"].unique())
print(f"      Recent dates from ticker_1m: {len(recent_dates)} sessions "
      f"({recent_dates[0].date()} → {recent_dates[-1].date()})" if recent_dates
      else "      No recent ticker_1m dates included")

prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

# ─── 2. VNI date list (for vni_dates) ───────────────────────────────────────
print("\n[2/6] Loading VNI date list…")
vni = bq(VNI_QUERY_UNIFIED.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
print(f"      {len(vni_dates)} trading sessions")

# VN30 underlying (use VNINDEX as proxy — same UNION)
vn30_underlying = dict(zip(vni["time"], vni["Close"]))

# ─── 3. Sector map + VN30 universe (from ticker) ────────────────────────────
print("\n[3/6] Loading sector + VN30 universe (from ticker)…")
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

# ─── 4. State series (forward-fill for dates > vnindex_5state.MAX) ──────────
print("\n[4/6] Loading 5-state series (with forward-fill)…")
state_df = bq(f"""
WITH s5_raw AS (
  SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
  WHERE s.time <= DATE '{END_DATE}'
)
SELECT time, state FROM s5_raw ORDER BY time
""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date_raw = dict(zip(state_df["time"], state_df["state"]))

# Forward-fill state for vni_dates not in state_df
state_by_date = {}
last_state = None
for d in vni_dates:
    if d in state_by_date_raw:
        last_state = state_by_date_raw[d]
    state_by_date[d] = last_state

ff_count = sum(1 for d in vni_dates if d not in state_by_date_raw)
print(f"      Raw state observations: {len(state_by_date_raw)}")
print(f"      Forward-filled: {ff_count} sessions (>= {state_df['time'].max().date()})")

# ─── 5. Run simulations ──────────────────────────────────────────────────────
TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
DEPOSIT = 0.01
ETF_STATES = {3: 0.7}

print("\n[5/6] Running BOOK A — BAL+Fin/RE-max-4 (25B) with V6 ETF…")
nav_bal, trades_bal = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, state_by_date=state_by_date,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    **LIQ_FULL, name="BAL_book")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
trades_bal["entry_date"] = pd.to_datetime(trades_bal["entry_date"])
trades_bal["exit_date"] = pd.to_datetime(trades_bal["exit_date"])
trades_bal["book"] = "BAL"
print(f"      {len(trades_bal)} closed stock trades")

print("\n      Running BOOK B — VN30_BAL (25B) with V6 ETF…")
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
    **LIQ_VN30, name="VN30_book")
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
trades_vn30["entry_date"] = pd.to_datetime(trades_vn30["entry_date"])
trades_vn30["exit_date"] = pd.to_datetime(trades_vn30["exit_date"])
trades_vn30["book"] = "VN30"
print(f"      {len(trades_vn30)} closed stock trades")

print("\n[6/6] Building combined NAV + event log…")

nav_bal_s = nav_bal.set_index("time")
nav_vn30_s = nav_vn30.set_index("time")
common = nav_bal_s.index.intersection(nav_vn30_s.index)

nav_total = nav_bal_s.loc[common]["nav"] + nav_vn30_s.loc[common]["nav"]
cash_etf_total = (nav_bal_s.loc[common].get("cash_etf_pct", pd.Series(0, index=common))
                   * nav_bal_s.loc[common]["nav"] / 100
                   + nav_vn30_s.loc[common].get("cash_etf_pct", pd.Series(0, index=common))
                   * nav_vn30_s.loc[common]["nav"] / 100)
stocks_value = (nav_bal_s.loc[common]["deployed_pct"] * nav_bal_s.loc[common]["nav"] / 100
                + nav_vn30_s.loc[common]["deployed_pct"] * nav_vn30_s.loc[common]["nav"] / 100)
cash_value = nav_total - cash_etf_total - stocks_value

running_peak = nav_total.cummax()
dd_pct = (nav_total - running_peak) / running_peak * 100

nav_daily = pd.DataFrame({
    "date": common,
    "nav_total_b": nav_total.values / 1e9,
    "state": [state_by_date.get(d) for d in common],
    "stocks_b": stocks_value.values / 1e9,
    "etf_b": cash_etf_total.values / 1e9,
    "cash_b": cash_value.values / 1e9,
    "drawdown_pct": dd_pct.values,
    "total_return_pct": (nav_total.values / TOTAL_NAV - 1) * 100,
})

# ─── ETF events derivation ───────────────────────────────────────────────────
def derive_etf_events(nav_df, book_label, book_nav_init):
    events = []
    nav_df_idx = nav_df.set_index("time")
    if "cash_etf_pct" not in nav_df_idx.columns:
        return events
    etf_value = nav_df_idx["cash_etf_pct"] * nav_df_idx["nav"] / 100
    etf_diff = etf_value.diff()
    threshold = book_nav_init * 0.01
    for d, delta in etf_diff.items():
        if pd.isna(delta) or abs(delta) < threshold:
            continue
        action = "ETF_BUY" if delta > 0 else "ETF_SELL"
        events.append({
            "action": action,
            "date": d,
            "ticker": "VN30_ETF",
            "book": book_label,
            "play_type": "ETF_PARKING",
            "price": None,
            "value_b": abs(delta) / 1e9,
            "etf_balance_after_b": etf_value.loc[d] / 1e9,
        })
    return events

etf_events = (derive_etf_events(nav_bal, "BAL", BOOK_NAV)
              + derive_etf_events(nav_vn30, "VN30", BOOK_NAV))

# ─── Build events ────────────────────────────────────────────────────────────
all_trades = pd.concat([trades_bal, trades_vn30], ignore_index=True)
stock_events = []
for _, t in all_trades.iterrows():
    stock_events.append({
        "action": "BUY", "date": t["entry_date"], "ticker": t["ticker"],
        "book": t["book"], "play_type": t["play_type"],
        "price": round(t["entry_price"], 0), "exit_reason": "",
        "ret_net_pct": None, "days_held": None,
    })
    stock_events.append({
        "action": "SELL", "date": t["exit_date"], "ticker": t["ticker"],
        "book": t["book"], "play_type": t["play_type"],
        "price": round(t["exit_price"], 0), "exit_reason": t["reason"],
        "ret_net_pct": round(t["ret_net"] * 100, 2),
        "days_held": int(t["days_held"]),
    })

stock_df = pd.DataFrame(stock_events)
etf_df = pd.DataFrame(etf_events)
if not etf_df.empty:
    etf_df["exit_reason"] = ""
    etf_df["ret_net_pct"] = None
    etf_df["days_held"] = None
all_cols = ["action", "date", "ticker", "book", "play_type", "price", "exit_reason",
             "ret_net_pct", "days_held"]
extra_cols = ["value_b", "etf_balance_after_b"]
for c in extra_cols:
    if c not in stock_df.columns:
        stock_df[c] = None
    if not etf_df.empty and c not in etf_df.columns:
        etf_df[c] = None
events_all = pd.concat([stock_df[all_cols + extra_cols],
                         etf_df[all_cols + extra_cols] if not etf_df.empty else pd.DataFrame()],
                         ignore_index=True)
events_all = events_all.sort_values(["date", "action", "book", "ticker"]).reset_index(drop=True)

nav_lookup = nav_daily.set_index("date")["nav_total_b"].to_dict()
events_all["nav_after_event_b"] = events_all["date"].map(lambda d: nav_lookup.get(d))
events_all["total_return_pct"] = events_all["nav_after_event_b"].apply(
    lambda v: (v * 1e9 / TOTAL_NAV - 1) * 100 if pd.notna(v) else None)
events_all["nav_after_event_b"] = events_all["nav_after_event_b"].round(2)
events_all["total_return_pct"] = events_all["total_return_pct"].round(2)

end_date = nav_daily["date"].max()
last_trades = all_trades[all_trades["exit_date"] == end_date]
open_positions = []
for _, t in last_trades.iterrows():
    open_positions.append({
        "ticker": t["ticker"], "book": t["book"],
        "play_type": t["play_type"],
        "entry_date": t["entry_date"].strftime("%Y-%m-%d"),
        "entry_price": round(t["entry_price"], 0),
        "last_price": round(t["exit_price"], 0),
        "ret_net_pct": round(t["ret_net"] * 100, 2),
        "days_held": int(t["days_held"]),
    })

# ─── Console summary ─────────────────────────────────────────────────────────
start_nav = TOTAL_NAV
end_nav = nav_daily.iloc[-1]["nav_total_b"] * 1e9
peak_nav = nav_daily["nav_total_b"].max() * 1e9
trough_nav = nav_daily["nav_total_b"].min() * 1e9
total_ret = (end_nav / start_nav - 1) * 100
peak_dd = nav_daily["drawdown_pct"].min()
n_days = len(nav_daily)
years = n_days / 252
cagr = (end_nav / start_nav) ** (1/years) - 1 if years > 0 else 0
n_stock_trades = len(all_trades)
win_count = (all_trades["ret_net"] > 0).sum()

print("\n" + "═" * 100)
print("  📊 PERIOD SUMMARY (extended to 2026-04-30 via ticker_1m fallback)")
print("═" * 100)
print(f"\n  Period            : {nav_daily.iloc[0]['date'].strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
print(f"  Trading sessions  : {n_days}")
print(f"  Period years      : {years:.2f}")
print(f"\n  💰 NAV TRACK")
print(f"  Starting NAV      : {start_nav/1e9:>9.2f} B VND")
print(f"  Ending NAV        : {end_nav/1e9:>9.2f} B VND")
print(f"  Peak NAV          : {peak_nav/1e9:>9.2f} B VND ({(peak_nav/start_nav-1)*100:+.2f}%)")
print(f"  Trough NAV        : {trough_nav/1e9:>9.2f} B VND ({(trough_nav/start_nav-1)*100:+.2f}%)")
print(f"  Total return      : {total_ret:>+9.2f}%")
print(f"  CAGR (annualized) : {cagr*100:>+9.2f}%")
print(f"  Max drawdown      : {peak_dd:>+9.2f}%")
print(f"\n  📈 STOCK TRADES")
print(f"  Total closed      : {n_stock_trades}")
print(f"  Stock BUYs        : {(events_all['action']=='BUY').sum()}")
print(f"  Stock SELLs       : {(events_all['action']=='SELL').sum()}")
print(f"  ETF BUYs          : {(events_all['action']=='ETF_BUY').sum()}")
print(f"  ETF SELLs         : {(events_all['action']=='ETF_SELL').sum()}")
if n_stock_trades:
    print(f"  Win rate          : {win_count/n_stock_trades*100:>+6.1f}% ({win_count}/{n_stock_trades})")
    print(f"  Avg ret/trade     : {all_trades['ret_net'].mean()*100:>+6.2f}%")
    print(f"  Best trade        : {all_trades['ret_net'].max()*100:>+6.2f}%  ({all_trades.loc[all_trades['ret_net'].idxmax(), 'ticker']})")
    print(f"  Worst trade       : {all_trades['ret_net'].min()*100:>+6.2f}%  ({all_trades.loc[all_trades['ret_net'].idxmin(), 'ticker']})")

print(f"\n  📋 EXIT REASONS")
exit_dist = all_trades["reason"].value_counts()
for r, n in exit_dist.items():
    avg = all_trades[all_trades["reason"] == r]["ret_net"].mean() * 100
    print(f"  {r:<10} : {n:>3d} trades, avg {avg:>+6.2f}%")

print(f"\n  📚 AVG CAPITAL ALLOCATION (% of total NAV)")
avg_stocks = nav_daily["stocks_b"].mean() / nav_daily["nav_total_b"].mean() * 100
avg_etf = nav_daily["etf_b"].mean() / nav_daily["nav_total_b"].mean() * 100
avg_cash = nav_daily["cash_b"].mean() / nav_daily["nav_total_b"].mean() * 100
print(f"  Stocks (BA active): {avg_stocks:>6.1f}%")
print(f"  ETF (VN30)        : {avg_etf:>6.1f}%")
print(f"  Cash deposit      : {avg_cash:>6.1f}%")

nav_bal_end = nav_bal_s.iloc[-1]["nav"]
nav_vn30_end = nav_vn30_s.iloc[-1]["nav"]
print(f"\n  📚 PER-BOOK NAV (end)")
print(f"  BAL book          : {nav_bal_end/1e9:>6.2f}B (start 25B → {(nav_bal_end/BOOK_NAV-1)*100:+.2f}%)")
print(f"  VN30 book         : {nav_vn30_end/1e9:>6.2f}B (start 25B → {(nav_vn30_end/BOOK_NAV-1)*100:+.2f}%)")

# State transitions during period
print(f"\n  📅 STATE TIMELINE during period")
prev_state = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s != prev_state:
        state_names = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
        print(f"     {d.strftime('%Y-%m-%d')}: → {state_names.get(int(s)) if s else '?'} (state={s})")
        prev_state = s

# Open positions
print(f"\n  📌 OPEN POSITIONS AT END (force closed {end_date.strftime('%Y-%m-%d')})")
if open_positions:
    print(f"  {'Ticker':<8} {'Book':<6} {'Tier':<22} {'Entry':<12} {'Days':>5} {'Cur P/L':>9}")
    for p in open_positions:
        print(f"  {p['ticker']:<8} {p['book']:<6} {p['play_type']:<22} {p['entry_date']:<12} "
              f"{p['days_held']:>5} {p['ret_net_pct']:>+8.2f}%")
else:
    print("  (no open positions)")

# Save files (with try/except per file in case any is open in Excel)
events_path = os.path.join(WORKDIR, "journal_v6_extended_events.csv")
nav_path = os.path.join(WORKDIR, "journal_v6_extended_nav_daily.csv")
open_path = os.path.join(WORKDIR, "journal_v6_extended_open_positions.csv")

def _safe_save(df, path):
    try:
        df.to_csv(path, index=False)
        return True
    except PermissionError:
        # File is open elsewhere; save with timestamp suffix
        alt = path.replace(".csv", "_alt.csv")
        df.to_csv(alt, index=False)
        print(f"  ⚠ Permission denied on {os.path.basename(path)} → saved to {os.path.basename(alt)}")
        return False

_safe_save(events_all, events_path)
_safe_save(nav_daily, nav_path)
_safe_save(pd.DataFrame(open_positions), open_path)

print(f"\n  💾 OUTPUT FILES")
print(f"  Events log        : {events_path}")
print(f"  Daily NAV         : {nav_path}")
print(f"  Open positions    : {open_path}")

# Preview April 2026 events (the NEW range)
print(f"\n  📖 EVENTS IN APRIL 2026 (new range via ticker_1m)")
print("─" * 120)
preview_cols = ["action", "date", "ticker", "book", "play_type", "price",
                 "exit_reason", "ret_net_pct", "days_held", "value_b",
                 "nav_after_event_b", "total_return_pct"]
events_all_t = events_all.copy()
events_all_t["date"] = pd.to_datetime(events_all_t["date"])
apr_events = events_all_t[(events_all_t["date"] >= "2026-04-01")
                            & (events_all_t["date"] <= "2026-04-30")]
if not apr_events.empty:
    print(apr_events[preview_cols].to_string(index=False,
        float_format=lambda x: f"{x:.2f}", na_rep=""))
else:
    print("  (no events in April 2026 — system in BEAR/cash mode through that period)")

print()
print("═" * 100)
