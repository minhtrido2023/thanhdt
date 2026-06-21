# -*- coding: utf-8 -*-
"""F1 (60d Fresh Q Filter) — analysis across ALL 4 earnings seasons.

VN reporting cycle:
  Q1 reports → Apr-May  (quarter ends Mar 31, deadline 30-45d)
  Q2 reports → Jul-Aug  (quarter ends Jun 30)
  Q3 reports → Oct-Nov  (quarter ends Sep 30)
  Q4 reports → Jan-Feb  (year-end + Q4, quarter ends Dec 31, audited deadline ~Mar 31)

Non-earnings months: Mar, Jun, Sep, Dec (transitional).

For each season: compare F0 (no filter) vs F1 (60d max since release).
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

START_DATE = "2014-01-01"
END_DATE = "2026-03-30"

SEASONS = {
    "Q1 (Apr-May)": [4, 5],
    "Q2 (Jul-Aug)": [7, 8],
    "Q3 (Oct-Nov)": [10, 11],
    "Q4 (Jan-Feb)": [1, 2],
    "Non-earnings (Mar/Jun/Sep/Dec)": [3, 6, 9, 12],
}

print("=" * 100)
print("  F1 60d Filter — Per-Season Analysis (4 earnings + 1 non-earnings)")
print(f"  Period: {START_DATE} → {END_DATE}")
print("=" * 100)

print("\n[1/3] Loading signals + release dates…")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows")

releases_sql = f"""
SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY tf.ticker, tf.Release_Date
"""
releases = bq(releases_sql)
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = releases.groupby("ticker")["Release_Date"].apply(list).to_dict()

def days_since_release(ticker, signal_date):
    rels = release_by_ticker.get(ticker, [])
    eligible = [r for r in rels if r <= signal_date]
    if not eligible:
        return np.nan
    return (signal_date - eligible[-1]).days

print("  Computing days_since_release…")
sig["days_since_release"] = [days_since_release(r["ticker"], r["time"])
                              for _, r in sig.iterrows()]
sig["month"] = sig["time"].dt.month

# Print signal-level distribution per season
print(f"\n  SIGNAL distribution per season (days_since_release):")
print(f"  {'Season':<35} {'n_signals':>12} {'median':>8} {'>60d %':>8} {'>90d %':>8}")
print(f"  {'-'*35} {'-'*12} {'-'*8} {'-'*8} {'-'*8}")
for season_name, months in SEASONS.items():
    sub = sig[sig["month"].isin(months)]
    pct_60 = (sub["days_since_release"] > 60).mean() * 100
    pct_90 = (sub["days_since_release"] > 90).mean() * 100
    print(f"  {season_name:<35} {len(sub):>12,} "
          f"{sub['days_since_release'].median():>+7.0f}d "
          f"{pct_60:>+7.1f}% {pct_90:>+7.1f}%")

# ─── Run F0 + F1 ─────────────────────────────────────────────────────────────
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
       "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

print("\n[2/3] Running F0 (no filter) + F1 (60d max)…")
variants = {}
for label, max_days in [("F0 baseline", None), ("F1 max 60d", 60)]:
    if max_days is None:
        sig_filt = sig
    else:
        mask = sig["days_since_release"].notna() & (sig["days_since_release"] <= max_days)
        sig_filt = sig[mask].copy()

    nav_df, trades_df = simulate(sig_filt, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_by_date,
        **LIQ, name=label)
    trades_df["entry_date"] = pd.to_datetime(trades_df["entry_date"])
    trades_df["entry_month"] = trades_df["entry_date"].dt.month
    m = metrics(nav_df, trades_df, label)
    variants[label] = {"nav": nav_df, "trades": trades_df, "metrics": m}
    print(f"  {label}: CAGR={m['cagr_pct']:+.2f}% Sh={m['sharpe']:+.2f} "
          f"DD={m['max_dd_pct']:+.1f}% trades={m['n_trades']}")

# ─── Per-season trade analysis ───────────────────────────────────────────────
print(f"\n[3/3] Per-season TRADE results (F0 vs F1)")
print()

for label in ["F0 baseline", "F1 max 60d"]:
    tdf = variants[label]["trades"]
    print(f"  ┌{'─' * 95}┐")
    print(f"  │  {label}")
    print(f"  └{'─' * 95}┘")
    print(f"  {'Season':<35} {'n_trades':>10} {'avg_ret':>10} {'win%':>8} {'stop%':>8} {'time%':>8}")
    print(f"  {'-'*35} {'-'*10} {'-'*10} {'-'*8} {'-'*8} {'-'*8}")
    for season_name, months in SEASONS.items():
        sub = tdf[tdf["entry_month"].isin(months)]
        if len(sub) == 0:
            print(f"  {season_name:<35} {'(none)':>10}")
            continue
        avg_ret = sub["ret_net"].mean() * 100
        win_rate = (sub["ret_net"] > 0).mean() * 100
        stop_pct = (sub["reason"] == "STOP").mean() * 100
        time_pct = (sub["reason"] == "TIME").mean() * 100
        print(f"  {season_name:<35} {len(sub):>10} {avg_ret:>+9.2f}% "
              f"{win_rate:>+7.1f}% {stop_pct:>+7.1f}% {time_pct:>+7.1f}%")
    print()

# ─── Side-by-side comparison F0 vs F1 ────────────────────────────────────────
print(f"\n  COMPARISON F0 vs F1 per season:")
print(f"  {'Season':<35} {'F0 trades':>10} {'F1 trades':>10} {'F0 win%':>9} {'F1 win%':>9} "
      f"{'F0 avg':>9} {'F1 avg':>9}")
print(f"  {'-'*35} {'-'*10} {'-'*10} {'-'*9} {'-'*9} {'-'*9} {'-'*9}")
f0_t = variants["F0 baseline"]["trades"]
f1_t = variants["F1 max 60d"]["trades"]
for season_name, months in SEASONS.items():
    s0 = f0_t[f0_t["entry_month"].isin(months)]
    s1 = f1_t[f1_t["entry_month"].isin(months)]
    if len(s0) == 0:
        continue
    w0 = (s0["ret_net"] > 0).mean() * 100
    w1 = (s1["ret_net"] > 0).mean() * 100 if len(s1) else np.nan
    a0 = s0["ret_net"].mean() * 100
    a1 = s1["ret_net"].mean() * 100 if len(s1) else np.nan
    print(f"  {season_name:<35} {len(s0):>10} {len(s1):>10} "
          f"{w0:>+8.1f}% {w1:>+8.1f}% {a0:>+8.2f}% {a1:>+8.2f}%")

# ─── F1 vs F0 net effect per season ──────────────────────────────────────────
print(f"\n  F1 improvement per season:")
print(f"  {'Season':<35} {'F0 ret':>10} {'F1 ret':>10} {'Δ avg ret':>11} {'Skipped':>10}")
for season_name, months in SEASONS.items():
    s0 = f0_t[f0_t["entry_month"].isin(months)]
    s1 = f1_t[f1_t["entry_month"].isin(months)]
    if len(s0) == 0:
        continue
    a0 = s0["ret_net"].mean() * 100 if len(s0) else 0
    a1 = s1["ret_net"].mean() * 100 if len(s1) else 0
    skipped = len(s0) - len(s1)
    delta = a1 - a0
    arrow = "↑" if delta > 0.5 else ("↓" if delta < -0.5 else "≈")
    print(f"  {season_name:<35} {a0:>+9.2f}% {a1:>+9.2f}% "
          f"{delta:>+9.2f}pp {arrow}  {skipped:>+5d} trades")

# Save trade logs per variant
f0_t.to_csv(os.path.join(WORKDIR, "fresh_q_f0_trades.csv"), index=False)
f1_t.to_csv(os.path.join(WORKDIR, "fresh_q_f1_trades.csv"), index=False)
print(f"\n  Saved: fresh_q_f0_trades.csv, fresh_q_f1_trades.csv")
