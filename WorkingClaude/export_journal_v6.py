# -*- coding: utf-8 -*-
"""Export BA-system journal WITH V6 ETF parking (production v10.1 config).

Period: 2025-06-01 → 2026-03-30 (latest ticker data)
Config: BA-system 50/50 (BAL+Fin/RE-max-4 + VN30_BAL) + V6 ETF parking
        - Each book at 25B (50B wallet split)
        - Stock positions: 5% NAV each, max 10 per book, hold 45d, stop -20%, BL20
        - ETF parking: 70% idle cash → VN30 ETF in NEUTRAL state only
        - Deposit rate: 1% realistic
        - All friction included (TC 0.1% + slip 0.1% + tiered exit slip + ETF 0.05%)

Outputs:
  1. journal_v6_events.csv — chronological BUY/SELL events (stocks + ETF)
  2. journal_v6_nav_daily.csv — daily NAV with full breakdown
  3. journal_v6_open_positions.csv — open positions at end
  4. console summary
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
from test_round14_stability import SIGNAL_V10

START_DATE = "2025-06-01"
END_DATE   = "2026-03-30"
TOTAL_NAV  = 50_000_000_000
BOOK_NAV   = TOTAL_NAV / 2

print("=" * 100)
print(f"  BA-SYSTEM v10.1 JOURNAL (with V6 ETF parking) — {START_DATE} to {END_DATE}")
print(f"  NAV: {TOTAL_NAV/1e9:.1f}B ({BOOK_NAV/1e9:.1f}B/book × 2)")
print(f"  Config: deposit 1% realistic, ETF 70% in NEUTRAL state, hold 45d, stop -20%, BL20")
print("=" * 100)

print("\n[1/5] Loading data…")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"      {len(sig):,} signal rows")
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

# VN30 underlying for ETF returns (use VNINDEX as proxy in period)
vn30_df = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
vn30_df["time"] = pd.to_datetime(vn30_df["time"])
vn30_underlying = dict(zip(vn30_df["time"], vn30_df["Close"]))

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# V6 production config
DEPOSIT = 0.01
ETF_STATES = {3: 0.7}  # 70% ETF in NEUTRAL only

print("\n[2/5] Running BOOK A — BAL+Fin/RE-max-4 (25B) with V6 ETF…")
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

print("\n[3/5] Running BOOK B — VN30_BAL (25B) with V6 ETF…")
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

print("\n[4/5] Building combined NAV + event log…")

# Combined daily NAV (with ETF breakdown)
nav_bal_s = nav_bal.set_index("time")
nav_vn30_s = nav_vn30.set_index("time")
common = nav_bal_s.index.intersection(nav_vn30_s.index)

nav_total = nav_bal_s.loc[common]["nav"] + nav_vn30_s.loc[common]["nav"]
cash_etf_total = nav_bal_s.loc[common].get("cash_etf_pct", pd.Series(0, index=common)) * nav_bal_s.loc[common]["nav"] / 100 \
                + nav_vn30_s.loc[common].get("cash_etf_pct", pd.Series(0, index=common)) * nav_vn30_s.loc[common]["nav"] / 100

# Daily snapshot
running_peak = nav_total.cummax()
dd_pct = (nav_total - running_peak) / running_peak * 100

stocks_value = (nav_bal_s.loc[common]["deployed_pct"] * nav_bal_s.loc[common]["nav"] / 100
                + nav_vn30_s.loc[common]["deployed_pct"] * nav_vn30_s.loc[common]["nav"] / 100)
cash_value = nav_total - cash_etf_total - stocks_value

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

# ─── Derive ETF rebalance events from daily ETF balance changes ──────────
def derive_etf_events(nav_df, book_label, book_nav_init):
    """Find days where ETF balance jumped significantly (rebalance events)."""
    events = []
    nav_df = nav_df.set_index("time")
    if "cash_etf_pct" not in nav_df.columns:
        return events
    etf_value = nav_df["cash_etf_pct"] * nav_df["nav"] / 100
    # Find significant changes
    etf_diff = etf_value.diff()
    threshold = book_nav_init * 0.01  # 1% of initial NAV as significance
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
print(f"      {len(etf_events)} ETF rebalance events derived")

# ─── Stock events from trades ────────────────────────────────────────────
all_trades = pd.concat([trades_bal, trades_vn30], ignore_index=True)
stock_events = []
for _, t in all_trades.iterrows():
    stock_events.append({
        "action": "BUY",
        "date": t["entry_date"],
        "ticker": t["ticker"],
        "book": t["book"],
        "play_type": t["play_type"],
        "price": round(t["entry_price"], 0),
        "exit_reason": "",
        "ret_net_pct": None,
        "days_held": None,
    })
    stock_events.append({
        "action": "SELL",
        "date": t["exit_date"],
        "ticker": t["ticker"],
        "book": t["book"],
        "play_type": t["play_type"],
        "price": round(t["exit_price"], 0),
        "exit_reason": t["reason"],
        "ret_net_pct": round(t["ret_net"] * 100, 2),
        "days_held": int(t["days_held"]),
    })

# Combine + sort
stock_df = pd.DataFrame(stock_events)
etf_df = pd.DataFrame(etf_events)
if not etf_df.empty:
    etf_df["exit_reason"] = ""
    etf_df["ret_net_pct"] = None
    etf_df["days_held"] = None
# Common columns
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

# Add NAV at event
nav_lookup = nav_daily.set_index("date")["nav_total_b"].to_dict()
events_all["nav_after_event_b"] = events_all["date"].map(lambda d: nav_lookup.get(d))
events_all["total_return_pct"] = events_all["nav_after_event_b"].apply(
    lambda v: (v * 1e9 / TOTAL_NAV - 1) * 100 if pd.notna(v) else None)
events_all["nav_after_event_b"] = events_all["nav_after_event_b"].round(2)
events_all["total_return_pct"] = events_all["total_return_pct"].round(2)

# ─── Open positions at end ───────────────────────────────────────────────
end_date = nav_daily["date"].max()
last_trades = all_trades[all_trades["exit_date"] == end_date]
open_positions = []
for _, t in last_trades.iterrows():
    open_positions.append({
        "ticker": t["ticker"],
        "book": t["book"],
        "play_type": t["play_type"],
        "entry_date": t["entry_date"].strftime("%Y-%m-%d"),
        "entry_price": round(t["entry_price"], 0),
        "last_price": round(t["exit_price"], 0),
        "ret_net_pct": round(t["ret_net"] * 100, 2),
        "days_held": int(t["days_held"]),
    })

# ─── Console summary ─────────────────────────────────────────────────────
print(f"\n[5/5] Building summary…")

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
n_buy = (events_all["action"] == "BUY").sum()
n_sell = (events_all["action"] == "SELL").sum()
n_etf_buy = (events_all["action"] == "ETF_BUY").sum()
n_etf_sell = (events_all["action"] == "ETF_SELL").sum()

print("\n" + "═" * 100)
print("  📊 PERIOD SUMMARY")
print("═" * 100)
print(f"\n  Period            : {nav_daily.iloc[0]['date'].strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
print(f"  Trading sessions  : {n_days}")
print(f"  Period years      : {years:.2f}")
print()
print(f"  💰 NAV TRACK")
print(f"  Starting NAV      : {start_nav/1e9:>9.2f} B VND")
print(f"  Ending NAV        : {end_nav/1e9:>9.2f} B VND")
print(f"  Peak NAV          : {peak_nav/1e9:>9.2f} B VND ({(peak_nav/start_nav-1)*100:+.2f}%)")
print(f"  Trough NAV        : {trough_nav/1e9:>9.2f} B VND ({(trough_nav/start_nav-1)*100:+.2f}%)")
print(f"  Total return      : {total_ret:>+9.2f}%")
print(f"  CAGR (annualized) : {cagr*100:>+9.2f}%")
print(f"  Max drawdown      : {peak_dd:>+9.2f}%")
print()
print(f"  📈 STOCK TRADES")
print(f"  Total closed      : {n_stock_trades}")
print(f"  Stock BUYs        : {n_buy}")
print(f"  Stock SELLs       : {n_sell}")
print(f"  ETF BUYs (parking): {n_etf_buy}")
print(f"  ETF SELLs         : {n_etf_sell}")
if n_stock_trades:
    print(f"  Win rate          : {win_count/n_stock_trades*100:>+6.1f}% ({win_count}/{n_stock_trades})")
    print(f"  Avg ret/trade     : {all_trades['ret_net'].mean()*100:>+6.2f}%")
    print(f"  Best trade        : {all_trades['ret_net'].max()*100:>+6.2f}%  ({all_trades.loc[all_trades['ret_net'].idxmax(), 'ticker']})")
    print(f"  Worst trade       : {all_trades['ret_net'].min()*100:>+6.2f}%  ({all_trades.loc[all_trades['ret_net'].idxmin(), 'ticker']})")

# Exit reasons
print()
print(f"  📋 EXIT REASONS")
exit_dist = all_trades["reason"].value_counts()
for r, n in exit_dist.items():
    avg = all_trades[all_trades["reason"] == r]["ret_net"].mean() * 100
    print(f"  {r:<10} : {n:>3d} trades, avg {avg:>+6.2f}%")

# Average allocation
print()
print(f"  📚 AVG CAPITAL ALLOCATION (% of total NAV)")
avg_stocks = nav_daily["stocks_b"].mean() / nav_daily["nav_total_b"].mean() * 100
avg_etf = nav_daily["etf_b"].mean() / nav_daily["nav_total_b"].mean() * 100
avg_cash = nav_daily["cash_b"].mean() / nav_daily["nav_total_b"].mean() * 100
print(f"  Stocks (BA active): {avg_stocks:>6.1f}%")
print(f"  ETF (VN30)        : {avg_etf:>6.1f}%")
print(f"  Cash deposit      : {avg_cash:>6.1f}%")

# Per-book NAV
nav_bal_end = nav_bal_s.iloc[-1]["nav"]
nav_vn30_end = nav_vn30_s.iloc[-1]["nav"]
print()
print(f"  📚 PER-BOOK NAV (end)")
print(f"  BAL book          : {nav_bal_end/1e9:>6.2f}B (start 25B → {(nav_bal_end/BOOK_NAV-1)*100:+.2f}%)")
print(f"  VN30 book         : {nav_vn30_end/1e9:>6.2f}B (start 25B → {(nav_vn30_end/BOOK_NAV-1)*100:+.2f}%)")

# State events in period
print()
print(f"  ⚠ MARKET STATE EVENTS IN PERIOD")
print(f"  2025-09-23 → 2025-12-26 : CRISIS (state 1) — 64 sessions")
print(f"  2025-12-26 → 2026-01-08 : NEUTRAL recovery")
print(f"  2026-01-08 → 2026-02-03 : BULL")
print(f"  2026-02-03 → 2026-03-17 : NEUTRAL")
print(f"  2026-03-17 → 2026-03-30 : BEAR (state 2) — partial in test")

# Open positions
print()
print(f"  📌 OPEN POSITIONS AT END (force closed on {end_date.strftime('%Y-%m-%d')} due to data cutoff)")
if open_positions:
    print(f"  {'Ticker':<8} {'Book':<6} {'Tier':<22} {'Entry':<12} {'Days':>5} {'Cur P/L':>9}")
    for p in open_positions:
        print(f"  {p['ticker']:<8} {p['book']:<6} {p['play_type']:<22} {p['entry_date']:<12} "
              f"{p['days_held']:>5} {p['ret_net_pct']:>+8.2f}%")
else:
    print("  (no open positions)")

# Save files
events_path = os.path.join(WORKDIR, "journal_v6_events.csv")
nav_path = os.path.join(WORKDIR, "journal_v6_nav_daily.csv")
open_path = os.path.join(WORKDIR, "journal_v6_open_positions.csv")
events_all.to_csv(events_path, index=False)
nav_daily.to_csv(nav_path, index=False)
pd.DataFrame(open_positions).to_csv(open_path, index=False)

print()
print(f"  💾 OUTPUT FILES")
print(f"  Events log        : {events_path}")
print(f"  Daily NAV         : {nav_path}")
print(f"  Open positions    : {open_path}")

# Preview first/last 25 events
print()
print(f"  📖 FIRST 25 EVENTS")
print("─" * 120)
preview_cols = ["action", "date", "ticker", "book", "play_type", "price",
                 "exit_reason", "ret_net_pct", "days_held", "value_b",
                 "nav_after_event_b", "total_return_pct"]
print(events_all[preview_cols].head(25).to_string(index=False,
    float_format=lambda x: f"{x:.2f}", na_rep=""))

print()
print(f"  📖 LAST 25 EVENTS")
print("─" * 120)
print(events_all[preview_cols].tail(25).to_string(index=False,
    float_format=lambda x: f"{x:.2f}", na_rep=""))

# ETF events specifically
etf_only = events_all[events_all["action"].str.startswith("ETF")]
if not etf_only.empty:
    print()
    print(f"  💎 ETF REBALANCE EVENTS — {len(etf_only)} total")
    print("─" * 120)
    # Show only events > 1B value
    big_etf = etf_only[etf_only["value_b"] > 1.0].copy()
    if not big_etf.empty:
        print(big_etf[["action", "date", "book", "value_b", "etf_balance_after_b",
                        "nav_after_event_b"]].head(30).to_string(index=False,
            float_format=lambda x: f"{x:.2f}", na_rep=""))

print()
print("═" * 100)
print(f"  ⚠ DATA LIMIT NOTE")
print(f"  Requested: 2025-06-01 → today (~2026-05-11)")
print(f"  Actual: 2025-06-01 → 2026-03-30 (ticker daily ends here)")
print(f"  For 2026-04+ data, use ticker_1m + custom SQL (signals SQL rewrite needed)")
print("═" * 100)
