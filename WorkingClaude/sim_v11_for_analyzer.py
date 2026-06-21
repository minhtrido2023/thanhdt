# -*- coding: utf-8 -*-
"""Run V11 simulation + export CSVs in analyze_portfolio.py-compatible format.

Period: 2025-06-09 → latest available date (ticker_1m fallback for recent)
NAV: 50B VND (25B BAL book + 25B VN30 book)
Stack: BA v11 score + V11 SV_TIGHT Fresh-Q + V11 P3 COMPOSITE overheat + V6 ETF parking

Outputs:
  data/v11_logs.csv         — daily log (ymd, nav, num_holdings, num_transactions)
  data/v11_transactions.csv — buy/sell events (ymd, ticker, action, buy_amount, sell_amount, fee, adj_price, holding_id)
  data/v11_report.md         — final report via analyze_portfolio.py
"""
import os
import sys
import io
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY

START_DATE = "2025-06-09"
# Use latest available — ticker_1m updates daily; try to extend max range
END_DATE = "2026-05-15"
TOTAL_NAV = 50_000_000_000
BOOK_NAV = TOTAL_NAV / 2

# ─── V11 SIGNAL SQL — UNION ticker + ticker_1m + SV_TIGHT Fresh-Q ──────────
# State-conditional Fresh-Q: state 1 (CRISIS) ≤30d, state 2-3 (BEAR/NEU) ≤60d, state 4-5 (BULL) no filter
SIGNAL_V11_UNIFIED = """
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
latest_vni_max3m AS (
  SELECT t.D_RSI AS rsi_latest
  FROM tav2_bq.ticker AS t WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL
  ORDER BY t.time DESC LIMIT 1
),
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
ticker_data AS (
  -- ticker canonical
  SELECT t.ticker, t.time, t.Close, t.Price, t.Volume, t.D_RSI, t.D_MACDdiff,
         t.MA20, t.MA50, t.MA200, t.MA50_T1, t.Close_T1,
         t.HI_3M_T1, t.ID_HI_3Y, t.D_RSI_Max1W,
         t.PE, t.PE_MA5Y, t.PE_SD5Y, t.FSCORE,
         t.NP_P0, t.NP_P1, t.NP_P4, t.ICB_Code, t.Volume_3M_P50
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE '{start}' AND DATE '{end}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.D_RSI IS NOT NULL

  UNION ALL

  -- ticker_1m fallback for dates where ticker has no D_RSI
  SELECT t.ticker, t.time, t.Close, t.Price, t.Volume, t.D_RSI, t.D_MACDdiff,
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
    t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS liq,   -- real (unadjusted) traded notional
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
  LEFT JOIN (
    SELECT t2.time, ARRAY_AGG(s.state ORDER BY s.time DESC LIMIT 1)[OFFSET(0)] AS state
    FROM (SELECT DISTINCT time FROM ticker_data) AS t2
    LEFT JOIN tav2_bq.vnindex_5state AS s ON s.time <= t2.time
    GROUP BY t2.time
  ) AS s5_ff ON s5_ff.time = t.time
  LEFT JOIN (
    SELECT t2.ticker, t2.time,
      DATE_DIFF(t2.time, MAX(tf.Release_Date), DAY) AS days_since_release
    FROM (SELECT DISTINCT ticker, time FROM ticker_data) AS t2
    LEFT JOIN tav2_bq.ticker_financial AS tf
      ON tf.ticker = t2.ticker AND tf.Release_Date <= t2.time
    GROUP BY t2.ticker, t2.time
  ) AS rel ON rel.ticker = t.ticker AND rel.time = t.time
)
SELECT ticker, time, Close,
  CASE
    WHEN state5 IN (1, 2) THEN 'AVOID_bear'
    WHEN fa_tier = 'E' THEN 'AVOID_faE'
    -- V11 SV_TIGHT Fresh-Q: state 4-5 (BULL) no filter; state 3 (NEUTRAL) ≤60d
    -- State 1 (CRISIS) ≤30d but blocked anyway via AVOID_bear
    WHEN ta >= 170 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MEGA'
    WHEN ta >= 170 AND state5 IN (4,5) THEN 'S_PRO'
    WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MOMENTUM'
    WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('A','B') THEN 'MOMENTUM_QUALITY'
    WHEN ta >= 155 AND state5 = 3 AND fa_tier IN ('C','D')
         AND days_since_release IS NOT NULL AND days_since_release <= 60 THEN 'MOMENTUM_N'
    WHEN fa_tier IN ('A','B') AND pe_z < -0.5 AND ta >= 95 AND state5 IN (3,4,5) AND NOT warn_ext THEN 'COMPOUNDER_BUY'
    WHEN fa_tier = 'C' AND ta >= 100 AND state5 IN (4,5) AND ((np_yoy > 0.20) OR (rev_yoy > 0.20)) THEN 'DEEP_VALUE_RECOVERY'
    WHEN ta >= 140 AND state5 IN (4,5) THEN 'MOMENTUM_S'
    WHEN ta >= 125 AND state5 IN (4,5) THEN 'MOMENTUM_A'
    WHEN ta >= 140 AND state5 = 3 THEN 'MOMENTUM_S_N'
    WHEN fa_tier IN ('A','B') AND ta >= 70 AND ta < 130 THEN 'COMPOUNDER_HOLD'
    WHEN fa_tier IN ('A','B') THEN 'WAIT'
    ELSE 'PASS'
  END AS play_type,
  ta, liq, sec, days_since_release, state5
FROM classified WHERE liq >= 1e9
"""

VNI_QUERY_UNIFIED = """
WITH all_vni AS (
  SELECT t.time, t.Close FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{start}' AND DATE '{end}'
  UNION ALL
  SELECT t.time, t.Close FROM tav2_bq.ticker_1m AS t
  WHERE t.ticker = 'VNI' AND t.time BETWEEN DATE '{start}' AND DATE '{end}'
    AND t.time > (SELECT MAX(t2.time) FROM tav2_bq.ticker AS t2 WHERE t2.ticker = 'VNINDEX')
)
SELECT time, Close FROM all_vni ORDER BY time
"""

print("=" * 100)
print(f"  V11 Simulation for analyze_portfolio.py")
print(f"  Period: {START_DATE} → {END_DATE} | NAV: {TOTAL_NAV/1e9:.0f}B VND")
print("=" * 100)

# ─── 1. Load signals (V11 SV_TIGHT) ──────────────────────────────────────
print("\n[1/7] Loading V11 SV_TIGHT signals…")
sig = bq(SIGNAL_V11_UNIFIED.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows  ({sig['time'].min().date()} → {sig['time'].max().date()})")

# ─── 2. V11 P3 COMPOSITE overheat filter ─────────────────────────────────
print("\n[2/7] Computing V11 P3 COMPOSITE overheat dates…")
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full["ratio"] = vni_full["Close"] / vni_full["MA200"]
# Block: ratio > 1.30 AND (state==5 OR D_RSI > 0.75)
# State info: query
state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))
# Forward-fill state for vni_full dates
last_state = None
for idx, row in vni_full.iterrows():
    s = state_by_date.get(row["time"])
    if s is not None:
        last_state = s
    vni_full.at[idx, "state"] = last_state

vni_full["overheat"] = ((vni_full["ratio"] > 1.30)
                        & ((vni_full["state"] == 5) | (vni_full["D_RSI"] > 0.75)))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
print(f"  Overheat days: {len(overheat_dates)}")

# Apply P3: block buy signals on overheat dates
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
mask = sig["time"].isin(overheat_dates) & sig["play_type"].isin(BUY_TIERS_V11)
n_blocked = mask.sum()
sig.loc[mask, "play_type"] = "AVOID_overheated"
print(f"  Blocked {n_blocked} signals via P3 overheat filter")

# ─── 3. Common data ──────────────────────────────────────────────────────
print("\n[3/7] Loading prices + universe + state…")
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY_UNIFIED.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
vn30_underlying = dict(zip(vni["time"], vni["Close"]))
print(f"  {len(vni_dates)} trading sessions")

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * COALESCE(t.Price, t.Close)) DESC LIMIT 30""")["ticker"])

# Forward-fill state for all dates
state_by_date_ff = {}
last_state = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None:
        last_state = s
    state_by_date_ff[d] = last_state

# ─── 4. Run BAL + VN30 books at 25B each ────────────────────────────────
TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
DEPOSIT = 0.01
ETF_STATES = {3: 0.7}

print("\n[4/7] Running BOOK A — BAL+Fin/RE-max-4 (25B) with V6 ETF…")
nav_bal, trades_bal = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, state_by_date=state_by_date_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    **LIQ_FULL, name="BAL")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
trades_bal["entry_date"] = pd.to_datetime(trades_bal["entry_date"])
trades_bal["exit_date"] = pd.to_datetime(trades_bal["exit_date"])
trades_bal["book"] = "BAL"
print(f"  {len(trades_bal)} closed trades")

print("\n[5/7] Running BOOK B — VN30_BAL (25B) with V6 ETF…")
sig_vn30 = sig[sig["ticker"].isin(top30)].copy()
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, state_by_date=state_by_date_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    **LIQ_VN30, name="VN30")
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
trades_vn30["entry_date"] = pd.to_datetime(trades_vn30["entry_date"])
trades_vn30["exit_date"] = pd.to_datetime(trades_vn30["exit_date"])
trades_vn30["book"] = "VN30"
print(f"  {len(trades_vn30)} closed trades")

# ─── 6. Convert to analyze_portfolio.py format ───────────────────────────
print("\n[6/7] Converting to analyze_portfolio.py CSV format…")

# Combined NAV (sum of both books)
nav_bal_s = nav_bal.set_index("time")["nav"]
nav_vn30_s = nav_vn30.set_index("time")["nav"]
common = nav_bal_s.index.intersection(nav_vn30_s.index)
nav_total = nav_bal_s.loc[common] + nav_vn30_s.loc[common]
n_pos_bal = nav_bal.set_index("time")["n_pos"].loc[common]
n_pos_vn30 = nav_vn30.set_index("time")["n_pos"].loc[common]

all_trades = pd.concat([trades_bal, trades_vn30], ignore_index=True)
all_trades = all_trades.sort_values(["entry_date", "ticker"]).reset_index(drop=True)

# Build transactions (one row per buy + one row per sell)
TC_BUY = 0.001
TC_SELL = 0.001
CG_TAX = 0.001
SLIPPAGE = 0.001
INIT_POSITION_SIZE = BOOK_NAV / 10  # 2.5B per position (10% of book = 5% of total NAV)

events = []
holding_id_counter = 0
for _, t in all_trades.iterrows():
    holding_id_counter += 1
    hid = f"{t['ticker']}_{t['entry_date'].strftime('%Y%m%d')}_{holding_id_counter}"

    # Buy event
    # Use init position size approximation. Real position value computed by simulate engine
    # via NAV/max_positions. For analyzer, we use a reasonable estimate.
    # The trade dict doesn't have raw shares/cost, but ret_net=(proceeds/cost - 1).
    # We approximate cost_basis ≈ INIT_POSITION_SIZE.
    buy_amt = INIT_POSITION_SIZE
    buy_fee = buy_amt * (TC_BUY + SLIPPAGE)  # 0.2% combined

    events.append({
        "ymd": t["entry_date"],
        "ticker": t["ticker"],
        "action": "buy",
        "buy_amount": buy_amt,
        "sell_amount": 0.0,
        "fee": buy_fee,
        "adj_price": t["entry_price"],
        "holding_id": hid,
        "book": t["book"],
        "play_type": t["play_type"],
    })

    # Sell event
    sell_amt = buy_amt * (1 + t["ret_net"])
    sell_fee = sell_amt * (TC_SELL + CG_TAX + SLIPPAGE)  # 0.3% combined
    events.append({
        "ymd": t["exit_date"],
        "ticker": t["ticker"],
        "action": "sell",
        "buy_amount": 0.0,
        "sell_amount": sell_amt,
        "fee": sell_fee,
        "adj_price": t["exit_price"],
        "holding_id": hid,
        "book": t["book"],
        "play_type": t["play_type"],
    })

tx_df = pd.DataFrame(events)
tx_df = tx_df.sort_values(["ymd", "action"]).reset_index(drop=True)
print(f"  {len(tx_df)} transactions ({len(tx_df[tx_df['action']=='buy'])} buys, {len(tx_df[tx_df['action']=='sell'])} sells)")

# Build logs (daily)
logs_df = pd.DataFrame({"ymd": common})
logs_df["nav"] = nav_total.values
logs_df["num_holdings"] = (n_pos_bal.values + n_pos_vn30.values)

# num_transactions cumulative
tx_cum = tx_df.groupby("ymd").size().cumsum()
all_dates = pd.DataFrame({"ymd": common})
all_dates["cum_tx"] = 0
last_count = 0
tx_counts_by_date = tx_df.groupby("ymd").size().to_dict()
for idx, row in all_dates.iterrows():
    last_count += tx_counts_by_date.get(row["ymd"], 0)
    all_dates.at[idx, "cum_tx"] = last_count
logs_df["num_transactions"] = all_dates["cum_tx"].values
logs_df = logs_df.sort_values("ymd").reset_index(drop=True)
print(f"  {len(logs_df)} daily log rows")

# ─── 7. Save + run analyzer ──────────────────────────────────────────────
os.makedirs(os.path.join(WORKDIR, "data"), exist_ok=True)
tx_path = os.path.join(WORKDIR, "data", "v11_transactions.csv")
logs_path = os.path.join(WORKDIR, "data", "v11_logs.csv")
report_path = os.path.join(WORKDIR, "data", "v11_report.md")

tx_df.to_csv(tx_path, index=False)
logs_df.to_csv(logs_path, index=False)
print(f"\n[7/7] Saved:")
print(f"  Logs:         {logs_path}")
print(f"  Transactions: {tx_path}")

# Quick summary
print()
print("=" * 100)
print(f"  📊 V11 SIMULATION SUMMARY")
print("=" * 100)
print(f"  Period          : {logs_df['ymd'].min().strftime('%Y-%m-%d')} → {logs_df['ymd'].max().strftime('%Y-%m-%d')}")
print(f"  Starting NAV    : {logs_df['nav'].iloc[0]/1e9:.2f} B VND")
print(f"  Ending NAV      : {logs_df['nav'].iloc[-1]/1e9:.2f} B VND")
print(f"  Peak NAV        : {logs_df['nav'].max()/1e9:.2f} B VND")
print(f"  Total return    : {(logs_df['nav'].iloc[-1]/logs_df['nav'].iloc[0]-1)*100:+.2f}%")
yrs = (logs_df['ymd'].max() - logs_df['ymd'].min()).days / 365.25
cagr = (logs_df['nav'].iloc[-1]/logs_df['nav'].iloc[0])**(1/yrs) - 1 if yrs > 0 else 0
print(f"  CAGR annualized : {cagr*100:+.2f}%")
print(f"  Trades closed   : {len(all_trades)} ({len(trades_bal)} BAL + {len(trades_vn30)} VN30)")
print(f"  Win rate        : {(all_trades['ret_net']>0).mean()*100:.1f}%")

# Run analyzer
print()
print("=" * 100)
print(f"  🔍 RUNNING analyze_portfolio.py")
print("=" * 100)

analyzer = os.path.join(WORKDIR, "analyze_portfolio.py")
cmd = [sys.executable, analyzer,
       "--logs", logs_path,
       "--transactions", tx_path,
       "--output", report_path]
print(f"  Command: {' '.join(cmd)}")
print()

result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr)
    sys.exit(1)
print()
print(f"  ✓ Report saved: {report_path}")
