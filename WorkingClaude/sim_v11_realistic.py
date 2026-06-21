# -*- coding: utf-8 -*-
"""V11 simulation with REALISTIC T+1 Open execution timing.

Workflow match:
  Day T close (15:00 VN)  → recommend_holistic.py generates watchlist
  Day T 18:00             → Telegram message sent
  Day T+1 09:00-15:00     → user executes orders → entries fill at T+1 OPEN price

For exits:
  Day T close             → TIME/STOP trigger detected
  Day T+1 OPEN            → actual sell at T+1 open price (gap risk modeled)

Run period: 2025-06-09 → 2026-05-15, NAV 50B, V11 stack
"""
import os
import sys
import io
import subprocess

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY

# Inline constants (avoid importing sim_v11_for_analyzer which has module-level side effects)
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}

# Read SQL constants from sim_v11_for_analyzer.py without executing the module
import re
_mod_path = os.path.join(WORKDIR, "sim_v11_for_analyzer.py")
with open(_mod_path, "r", encoding="utf-8") as f:
    _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
SIGNAL_V11_UNIFIED = '"""' + _extract("SIGNAL_V11_UNIFIED") + '"""'
SIGNAL_V11_UNIFIED = _extract("SIGNAL_V11_UNIFIED")
VNI_QUERY_UNIFIED = _extract("VNI_QUERY_UNIFIED")

START_DATE = "2025-06-09"
END_DATE = "2026-05-15"
TOTAL_NAV = 50_000_000_000
BOOK_NAV = TOTAL_NAV / 2

print("=" * 100)
print(f"  V11 Realistic Sim — T+1 OPEN execution (no look-ahead bias on exits)")
print(f"  Period: {START_DATE} → {END_DATE} | NAV: {TOTAL_NAV/1e9:.0f}B VND")
print("=" * 100)

print("\n[1/8] Loading V11 SV_TIGHT signals…")
sig = bq(SIGNAL_V11_UNIFIED.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows")

# Need OPEN prices — query separately
print("\n[2/8] Loading Open prices…")
OPEN_SQL = f"""
SELECT t.ticker, t.time, t.Open AS open_price
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL
UNION ALL
SELECT t.ticker, t.time, t.Open AS open_price
FROM tav2_bq.ticker_1m AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM tav2_bq.ticker AS t2
    WHERE t2.time = t.time AND t2.ticker = t.ticker AND t2.Open IS NOT NULL
  )
"""
opens_df = bq(OPEN_SQL)
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"]))
               for tk, g in opens_df.groupby("ticker")}
print(f"  {len(opens_df):,} (ticker, date) open prices")

# Quick sanity: compare Open vs Close for a sample
sample = opens_df.merge(sig[["ticker", "time", "Close"]], on=["ticker", "time"], how="left")
sample = sample.dropna(subset=["Close", "open_price"])
sample["gap_pct"] = (sample["open_price"] / sample["Close"].shift(1) - 1) * 100
print(f"  Avg overnight gap: {sample['gap_pct'].mean():+.3f}%, P5={sample['gap_pct'].quantile(0.05):+.2f}%, P95={sample['gap_pct'].quantile(0.95):+.2f}%")

# ─── P3 overheat filter ─────────────────────────────────────────────────
print("\n[3/8] Applying V11 P3 COMPOSITE overheat filter…")
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full["ratio"] = vni_full["Close"] / vni_full["MA200"]

state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

last_state = None
for idx, row in vni_full.iterrows():
    s = state_by_date.get(row["time"])
    if s is not None: last_state = s
    vni_full.at[idx, "state"] = last_state
vni_full["overheat"] = ((vni_full["ratio"] > 1.30)
                        & ((vni_full["state"] == 5) | (vni_full["D_RSI"] > 0.75)))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
print(f"  Overheat days: {len(overheat_dates)}")

mask = sig["time"].isin(overheat_dates) & sig["play_type"].isin(BUY_TIERS_V11)
sig.loc[mask, "play_type"] = "AVOID_overheated"
print(f"  Blocked {mask.sum()} signals via P3")

# ─── Common data ────────────────────────────────────────────────────────
print("\n[4/8] Loading universe…")
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY_UNIFIED.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
vn30_underlying = dict(zip(vni["time"], vni["Close"]))

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

state_by_date_ff = {}
last_state = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_state = s
    state_by_date_ff[d] = last_state

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
ETF_STATES = {3: 0.7}

# ─── Run TWO sims for comparison ────────────────────────────────────────
def run_book(label, sig_df, prices_d, liq_d, init_nav, sec_cap, t1_mode):
    LIQ = {**LIQ_FULL, "liquidity_lookup": liq_d}
    sec_kwargs = {"sector_limit_per_sector": sec_cap} if sec_cap else {}
    nav, trades = simulate(sig_df, prices_d, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=init_nav,
        ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_by_date_ff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
        open_prices=open_prices if t1_mode else None,
        t1_open_exec=t1_mode,
        **sec_kwargs, **LIQ, name=label)
    nav["time"] = pd.to_datetime(nav["time"])
    trades["entry_date"] = pd.to_datetime(trades["entry_date"])
    trades["exit_date"] = pd.to_datetime(trades["exit_date"])
    return nav, trades


sig_vn30 = sig[sig["ticker"].isin(top30)].copy()
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}

# Variant A: OLD timing (T+1 close entry, T close exit)
print("\n[5/8] Running A: OLD timing (T+1 close entry, same-day close exit)…")
nav_bal_A, trades_bal_A = run_book("BAL_OLD", sig, prices, liq_map, BOOK_NAV, {8: 4}, t1_mode=False)
nav_vn30_A, trades_vn30_A = run_book("VN30_OLD", sig_vn30, prices_vn30, liq_vn30, BOOK_NAV, None, t1_mode=False)
trades_A = pd.concat([trades_bal_A, trades_vn30_A], ignore_index=True)

# Variant B: NEW timing (T+1 Open for both entry + exit)
print("\n[6/8] Running B: NEW timing (T+1 OPEN entry + exit deferred to T+1 Open)…")
nav_bal_B, trades_bal_B = run_book("BAL_NEW", sig, prices, liq_map, BOOK_NAV, {8: 4}, t1_mode=True)
nav_vn30_B, trades_vn30_B = run_book("VN30_NEW", sig_vn30, prices_vn30, liq_vn30, BOOK_NAV, None, t1_mode=True)
trades_B = pd.concat([trades_bal_B, trades_vn30_B], ignore_index=True)

# Combine
def combine(nav_b, nav_v):
    nav_b_s = nav_b.set_index("time")["nav"]
    nav_v_s = nav_v.set_index("time")["nav"]
    common = nav_b_s.index.intersection(nav_v_s.index)
    return nav_b_s.loc[common] + nav_v_s.loc[common]

nav_A = combine(nav_bal_A, nav_vn30_A)
nav_B = combine(nav_bal_B, nav_vn30_B)

# Metrics
def m(nav):
    rets = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = ((nav - nav.cummax()) / nav.cummax()).min()
    return {"cagr": cagr*100, "sharpe": sharpe, "dd": dd*100,
            "calmar": cagr/abs(dd) if dd < 0 else 0,
            "final_b": nav.iloc[-1]/1e9}

print("\n[7/8] Building comparison…")
mA = m(nav_A)
mB = m(nav_B)

print("\n" + "=" * 100)
print("  📊 COMPARISON — OLD vs NEW (T+1 Open) execution timing")
print("=" * 100)
print()
print(f"  {'Variant':<45} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>7} {'NAV end':>10}")
print(f"  {'-'*45} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*10}")
print(f"  {'A) OLD: T+1 close entry, T close exit':<45} {mA['cagr']:>+7.2f}% {mA['sharpe']:>+7.2f} {mA['dd']:>+7.1f}% {mA['calmar']:>+7.2f} {mA['final_b']:>8.2f}B")
print(f"  {'B) NEW: T+1 Open entry + Open exit':<45} {mB['cagr']:>+7.2f}% {mB['sharpe']:>+7.2f} {mB['dd']:>+7.1f}% {mB['calmar']:>+7.2f} {mB['final_b']:>8.2f}B")
print()
print(f"  Δ NEW vs OLD:")
print(f"    ΔCAGR    : {mB['cagr']-mA['cagr']:+.2f}pp")
print(f"    ΔSharpe  : {mB['sharpe']-mA['sharpe']:+.2f}")
print(f"    ΔDD      : {mB['dd']-mA['dd']:+.1f}pp")
print(f"    ΔNAV end : {mB['final_b']-mA['final_b']:+.2f}B")

# STOP exit specific analysis
print(f"\n  STOP exit comparison (where gap-down risk most matters):")
stops_A = trades_A[trades_A["reason"] == "STOP"]
stops_B = trades_B[trades_B["reason"] == "STOP"]
if len(stops_A) and len(stops_B):
    print(f"    OLD: {len(stops_A)} STOPs, avg net ret {stops_A['ret_net'].mean()*100:+.2f}%")
    print(f"    NEW: {len(stops_B)} STOPs, avg net ret {stops_B['ret_net'].mean()*100:+.2f}%")
    print(f"    → Gap-down on STOP exits = {(stops_B['ret_net'].mean() - stops_A['ret_net'].mean())*100:+.2f}pp avg per STOP")

# ─── 8. Convert B (realistic) to analyzer format ────────────────────────
print("\n[8/8] Saving NEW timing variant for analyzer…")
nav_bal_s = nav_bal_B.set_index("time")["nav"]
nav_vn30_s = nav_vn30_B.set_index("time")["nav"]
common = nav_bal_s.index.intersection(nav_vn30_s.index)
nav_total = nav_bal_s.loc[common] + nav_vn30_s.loc[common]
n_pos_bal = nav_bal_B.set_index("time")["n_pos"].loc[common]
n_pos_vn30 = nav_vn30_B.set_index("time")["n_pos"].loc[common]

INIT_POSITION_SIZE = BOOK_NAV / 10
events = []
hid_counter = 0
trades_B = trades_B.sort_values(["entry_date", "ticker"]).reset_index(drop=True)
for _, t in trades_B.iterrows():
    hid_counter += 1
    hid = f"{t['ticker']}_{t['entry_date'].strftime('%Y%m%d')}_{hid_counter}"
    buy_amt = INIT_POSITION_SIZE
    events.append({"ymd": t["entry_date"], "ticker": t["ticker"], "action": "buy",
                    "buy_amount": buy_amt, "sell_amount": 0,
                    "fee": buy_amt * 0.002, "adj_price": t["entry_price"], "holding_id": hid})
    sell_amt = buy_amt * (1 + t["ret_net"])
    events.append({"ymd": t["exit_date"], "ticker": t["ticker"], "action": "sell",
                    "buy_amount": 0, "sell_amount": sell_amt,
                    "fee": sell_amt * 0.003, "adj_price": t["exit_price"], "holding_id": hid})

tx_df = pd.DataFrame(events).sort_values(["ymd", "action"]).reset_index(drop=True)

logs_df = pd.DataFrame({"ymd": common, "nav": nav_total.values,
                         "num_holdings": (n_pos_bal.values + n_pos_vn30.values)})
tx_counts = tx_df.groupby("ymd").size().to_dict()
last_count = 0
cum = []
for d in common:
    last_count += tx_counts.get(d, 0)
    cum.append(last_count)
logs_df["num_transactions"] = cum

os.makedirs(os.path.join(WORKDIR, "data"), exist_ok=True)
tx_path = os.path.join(WORKDIR, "data", "v11_realistic_transactions.csv")
logs_path = os.path.join(WORKDIR, "data", "v11_realistic_logs.csv")
report_path = os.path.join(WORKDIR, "data", "v11_realistic_report.md")
tx_df.to_csv(tx_path, index=False)
logs_df.to_csv(logs_path, index=False)

print(f"  Saved: {logs_path}")
print(f"  Saved: {tx_path}")

# Run analyzer
print("\nRunning analyze_portfolio.py on NEW realistic sim…")
result = subprocess.run([sys.executable, os.path.join(WORKDIR, "analyze_portfolio.py"),
                          "--logs", logs_path, "--transactions", tx_path,
                          "--output", report_path], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr)
print(f"\n  ✓ Realistic report: {report_path}")
