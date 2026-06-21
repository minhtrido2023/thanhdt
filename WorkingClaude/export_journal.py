# -*- coding: utf-8 -*-
"""Export BA-system trade journal for a specific period.

Period: 2025-06-01 → 2026-04-30 (request)
        2025-06-01 → 2026-03-30 (actual, ticker daily ends here)

Total wallet: 50B VND
  Book A — BAL+Fin/RE-max-4 at 25B (50% allocation)
  Book B — VN30_BAL at 25B (50% allocation)

Outputs:
  1. journal_events.csv — chronological BUY/SELL events with NAV after each
  2. journal_nav_daily.csv — daily NAV trace (combined + per-book)
  3. journal_open_positions.csv — open positions at end-of-period
  4. console summary — period stats, total returns, win rate
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
END_DATE   = "2026-04-30"
TOTAL_NAV  = 50_000_000_000   # 50B VND
BOOK_NAV   = TOTAL_NAV / 2    # 25B each book

print("=" * 100)
print(f"  BA-SYSTEM TRADE JOURNAL — {START_DATE} to {END_DATE}")
print(f"  Total NAV: {TOTAL_NAV/1e9:.1f}B VND ({BOOK_NAV/1e9:.1f}B per book × 2 books)")
print("=" * 100)

print("\n[1/5] Loading v10 signals…")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"      {len(sig):,} signal rows; date range "
      f"{sig['time'].min().date()} → {sig['time'].max().date()}")
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
print(f"      {len(vni_dates)} trading sessions in period")

print("\n[2/5] Loading sector + VN30 universe…")
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# ─── 3) Run BAL+Fin/RE-max-4 book at 25B ─────────────────────────────────────
print("\n[3/5] Simulating BOOK A — BAL+Fin/RE-max-4 (25B)…")
nav_bal, trades_bal = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL,
    name="BAL_book")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
trades_bal["entry_date"] = pd.to_datetime(trades_bal["entry_date"])
trades_bal["exit_date"] = pd.to_datetime(trades_bal["exit_date"])
trades_bal["book"] = "BAL"
print(f"      {len(trades_bal)} closed trades in BAL book")

# ─── 4) Run VN30_BAL book at 25B ─────────────────────────────────────────────
print("\n[4/5] Simulating BOOK B — VN30_BAL (25B)…")
sig_vn30 = sig[sig["ticker"].isin(top30)].copy()
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV, **LIQ_VN30,
    name="VN30_book")
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
trades_vn30["entry_date"] = pd.to_datetime(trades_vn30["entry_date"])
trades_vn30["exit_date"] = pd.to_datetime(trades_vn30["exit_date"])
trades_vn30["book"] = "VN30"
print(f"      {len(trades_vn30)} closed trades in VN30 book")

# ─── 5) Build event log + daily NAV ──────────────────────────────────────────
print("\n[5/5] Building event log + daily NAV trace…")

# Combined NAV daily
nav_bal_s = nav_bal.set_index("time")["nav"]
nav_vn30_s = nav_vn30.set_index("time")["nav"]
common_dates = nav_bal_s.index.intersection(nav_vn30_s.index)
nav_total = (nav_bal_s.loc[common_dates] + nav_vn30_s.loc[common_dates])

# Drawdown from peak
running_peak = nav_total.cummax()
dd_pct = (nav_total - running_peak) / running_peak * 100

nav_daily = pd.DataFrame({
    "date": common_dates,
    "nav_total": nav_total.values,
    "nav_bal_book": nav_bal_s.loc[common_dates].values,
    "nav_vn30_book": nav_vn30_s.loc[common_dates].values,
    "drawdown_pct_from_peak": dd_pct.values,
    "total_return_pct": (nav_total.values / TOTAL_NAV - 1) * 100,
})

# Build event log
all_trades = pd.concat([trades_bal, trades_vn30], ignore_index=True)

events = []
for _, t in all_trades.iterrows():
    # BUY event
    cost_value = t["entry_price"] * (t.get("ret_net", 0) + 1)  # NA in sim — compute from cost basis instead
    # We don't have "shares" or "cost_basis" in trades_df easily; reconstruct value from price
    # Use nominal entry price × estimated share count (NAV/10 as starting estimate)
    events.append({
        "action": "BUY",
        "date": t["entry_date"],
        "ticker": t["ticker"],
        "book": t["book"],
        "play_type": t["play_type"],
        "price": round(t["entry_price"], 0),
        "exit_reason": "",
        "ret_net_pct": np.nan,
        "days_held": np.nan,
    })
    # SELL event
    events.append({
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

events_df = pd.DataFrame(events)
events_df = events_df.sort_values(["date", "action", "book", "ticker"]).reset_index(drop=True)

# Add NAV-at-event from nav_daily
nav_lookup = nav_daily.set_index("date")["nav_total"].to_dict()
events_df["nav_after_event_b"] = events_df["date"].map(
    lambda d: nav_lookup.get(d, np.nan) / 1e9 if d in nav_lookup else np.nan)
events_df["nav_after_event_b"] = events_df["nav_after_event_b"].round(2)
events_df["total_return_pct"] = ((events_df["nav_after_event_b"] * 1e9) / TOTAL_NAV - 1) * 100
events_df["total_return_pct"] = events_df["total_return_pct"].round(2)

# ─── Identify open positions at end of period ───────────────────────────────
end_date = nav_daily["date"].max()
open_positions = []

# Per book, find trades that started but haven't shown an exit by end_date
# (simulate engine forces close at end so all trades have exit_date — instead,
#  we identify "would-be open" by exit_date == end_date)
last_trades = all_trades[all_trades["exit_date"] == end_date]
# These were still-open positions at end; engine recorded them as "EOD" or last close

for _, t in last_trades.iterrows():
    open_positions.append({
        "ticker": t["ticker"],
        "book": t["book"],
        "play_type": t["play_type"],
        "entry_date": t["entry_date"].strftime("%Y-%m-%d"),
        "exit_date_forced": t["exit_date"].strftime("%Y-%m-%d"),
        "entry_price": round(t["entry_price"], 0),
        "last_price": round(t["exit_price"], 0),
        "ret_net_pct": round(t["ret_net"] * 100, 2),
        "days_held": int(t["days_held"]),
        "exit_reason": t["reason"],
    })

# ─── Save outputs ────────────────────────────────────────────────────────────
events_path = os.path.join(WORKDIR, "journal_events.csv")
nav_path = os.path.join(WORKDIR, "journal_nav_daily.csv")
open_path = os.path.join(WORKDIR, "journal_open_positions.csv")
events_df.to_csv(events_path, index=False)
nav_daily.to_csv(nav_path, index=False)
pd.DataFrame(open_positions).to_csv(open_path, index=False)

# ─── Console summary ─────────────────────────────────────────────────────────
print("\n" + "═" * 100)
print("  📊 PERIOD SUMMARY")
print("═" * 100)

start_nav = TOTAL_NAV
end_nav = nav_daily.iloc[-1]["nav_total"]
peak_nav = nav_daily["nav_total"].max()
trough_nav = nav_daily["nav_total"].min()
total_ret = (end_nav / start_nav - 1) * 100
peak_dd = nav_daily["drawdown_pct_from_peak"].min()

n_days = len(nav_daily)
years = n_days / 252
cagr = (end_nav / start_nav) ** (1/years) - 1 if years > 0 else 0

n_trades = len(all_trades)
win_count = (all_trades["ret_net"] > 0).sum()
n_buy_events = (events_df["action"] == "BUY").sum()
n_sell_events = (events_df["action"] == "SELL").sum()

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
print(f"  Max drawdown      : {peak_dd:>+9.2f}%  (from peak)")

print()
print(f"  📈 TRADES")
print(f"  Total closed trades : {n_trades}")
print(f"  BUY events          : {n_buy_events}")
print(f"  SELL events         : {n_sell_events}")
if n_trades:
    print(f"  Win rate            : {win_count/n_trades*100:>+6.1f}%  ({win_count}/{n_trades})")
    print(f"  Avg return per trade: {all_trades['ret_net'].mean()*100:>+6.2f}%")
    print(f"  Best trade          : {all_trades['ret_net'].max()*100:>+6.2f}%  "
          f"({all_trades.loc[all_trades['ret_net'].idxmax(), 'ticker']})")
    print(f"  Worst trade         : {all_trades['ret_net'].min()*100:>+6.2f}%  "
          f"({all_trades.loc[all_trades['ret_net'].idxmin(), 'ticker']})")

# Exit reason breakdown
print()
print(f"  📋 EXIT REASONS")
exit_dist = all_trades["reason"].value_counts()
for r, n in exit_dist.items():
    avg = all_trades[all_trades["reason"] == r]["ret_net"].mean() * 100
    print(f"  {r:<10} : {n:>3d} trades, avg return {avg:>+6.2f}%")

# Book-level breakdown
print()
print(f"  📚 PER-BOOK BREAKDOWN")
print(f"  {'Book':<8} {'Trades':>8} {'WinRate':>10} {'AvgRet':>10} {'BookNAV_end':>13}")
for book in ["BAL", "VN30"]:
    sub = all_trades[all_trades["book"] == book]
    if len(sub):
        wr = (sub["ret_net"] > 0).mean() * 100
        ar = sub["ret_net"].mean() * 100
        nav_book_end = (nav_bal_s if book == "BAL" else nav_vn30_s).iloc[-1]
        print(f"  {book:<8} {len(sub):>8} {wr:>+9.1f}% {ar:>+9.2f}% "
              f"{nav_book_end/1e9:>11.2f} B")

# Recent BEAR period analysis
print()
print(f"  ⚠ MARKET STATE EVENTS IN PERIOD")
print(f"  2025-09-23 → 2025-12-26 : CRISIS (state 1) — 64 sessions ~3 months")
print(f"  2025-12-26 → 2026-01-08 : NEUTRAL recovery")
print(f"  2026-01-08 → 2026-02-03 : BULL")
print(f"  2026-02-03 → 2026-03-17 : NEUTRAL")
print(f"  2026-03-17 → 2026-04-08 : BEAR (state 2) — only ~3 weeks")
print(f"  2026-04-09 → present    : NEUTRAL (current)")

# Open positions at end
print()
print(f"  📌 OPEN POSITIONS AT END (forced close on {end_date.strftime('%Y-%m-%d')} due to data cutoff):")
if open_positions:
    print(f"  {'Ticker':<8} {'Book':<6} {'Tier':<22} {'Entry':<10} {'Days':>5} {'Cur P/L':>9}")
    for p in open_positions[:20]:
        print(f"  {p['ticker']:<8} {p['book']:<6} {p['play_type']:<22} {p['entry_date']:<10} "
              f"{p['days_held']:>5} {p['ret_net_pct']:>+8.2f}%")
    if len(open_positions) > 20:
        print(f"  ... and {len(open_positions)-20} more")
else:
    print(f"  (none — all trades fully closed by {end_date.strftime('%Y-%m-%d')})")

# Period file paths
print()
print(f"  💾 OUTPUT FILES")
print(f"  Event log         : {events_path}")
print(f"  Daily NAV trace   : {nav_path}")
print(f"  Open positions    : {open_path}")

# Sample of first 30 events
print()
print(f"  📖 FIRST 30 EVENTS PREVIEW")
print(f"{'─' * 110}")
preview_cols = ["action", "date", "ticker", "book", "play_type", "price",
                 "exit_reason", "ret_net_pct", "days_held", "nav_after_event_b", "total_return_pct"]
print(events_df[preview_cols].head(30).to_string(index=False,
    float_format=lambda x: f"{x:.2f}", na_rep=""))

# Sample of last 30 events
print()
print(f"  📖 LAST 30 EVENTS PREVIEW")
print(f"{'─' * 110}")
print(events_df[preview_cols].tail(30).to_string(index=False,
    float_format=lambda x: f"{x:.2f}", na_rep=""))

# Note on data limit
print()
print(f"{'═' * 100}")
print(f"  ⚠ DATA LIMIT NOTE")
print(f"  Requested period: 2025-06-01 → 2026-04-30")
print(f"  Actual sim end  : {end_date.strftime('%Y-%m-%d')} (ticker daily ends here)")
print(f"  For 2026-04 data, use ticker_1m table; signals SQL needs updating to read live data.")
print(f"{'═' * 100}")
