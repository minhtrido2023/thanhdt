# -*- coding: utf-8 -*-
"""Test variant: require FRESH quarterly report at entry time.

Hypothesis: during earnings season (Apr-May, Oct-Nov), ~94% of companies still
use stale Q4 data in early-mid window. Filter out entries where last report is
older than X days → only trade on companies with confirmed recent fundamentals.

Variants tested (BAL+Fin/RE-max-4 50B, 1% deposit):
  F0 baseline (no filter — current production)
  F1 max 60d since release (very strict — only post-earnings)
  F2 max 90d since release (moderate — allows Q4 in early Q1 reporting cycle)
  F3 max 120d since release (lenient — allows full Q4 cycle)
  F4 max 150d since release (very lenient — almost no filter)

For each variant: CAGR, Sharpe, MaxDD, trades, n_skipped_for_staleness.
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

print("=" * 100)
print("  FRESH QUARTERLY REPORT FILTER — test variant")
print(f"  Period: {START_DATE} → {END_DATE} | 50B BAL+Fin/RE-max-4")
print("=" * 100)

print("\n[1/4] Loading signals + ticker_financial release dates…")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows")

# Build (ticker, time) → days_since_release mapping via JOIN
print("  Computing days_since_release per (ticker, date)…")
releases_sql = f"""
WITH releases AS (
  SELECT tf.ticker, tf.Release_Date
  FROM tav2_bq.ticker_financial AS tf
  WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
)
SELECT ticker, Release_Date FROM releases
ORDER BY ticker, Release_Date
"""
releases = bq(releases_sql)
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])

# Build per-ticker sorted release list
release_by_ticker = releases.groupby("ticker")["Release_Date"].apply(list).to_dict()

def days_since_release(ticker, signal_date):
    """Return days from latest release <= signal_date for ticker, or NaN."""
    rels = release_by_ticker.get(ticker, [])
    eligible = [r for r in rels if r <= signal_date]
    if not eligible:
        return np.nan
    return (signal_date - eligible[-1]).days

print("  Computing days_since_release for each signal row (this takes ~1 min)…")
sig["days_since_release"] = [days_since_release(r["ticker"], r["time"])
                              for _, r in sig.iterrows()]
print(f"  Done. Missing release info: {sig['days_since_release'].isna().sum():,} rows")

# Stats
print()
print(f"  Distribution of days_since_release across all signals:")
print(f"    median: {sig['days_since_release'].median():.0f} days")
print(f"    p25:    {sig['days_since_release'].quantile(0.25):.0f}")
print(f"    p75:    {sig['days_since_release'].quantile(0.75):.0f}")
print(f"    p90:    {sig['days_since_release'].quantile(0.90):.0f}")
print(f"    max:    {sig['days_since_release'].max():.0f}")

# How many signals fire DURING earnings season (Q1: Apr-May, Q3: Oct-Nov)
sig["month"] = sig["time"].dt.month
earnings_season = sig[sig["month"].isin([4, 5, 10, 11])]
print(f"\n  Earnings season signals (Apr-May + Oct-Nov):")
print(f"    n total = {len(earnings_season):,}")
print(f"    median days_since = {earnings_season['days_since_release'].median():.0f}")
print(f"    % with stale (>60d) = {(earnings_season['days_since_release']>60).mean()*100:.1f}%")
print(f"    % with very stale (>90d) = {(earnings_season['days_since_release']>90).mean()*100:.1f}%")
print(f"    % with >120d = {(earnings_season['days_since_release']>120).mean()*100:.1f}%")

# ─── Load other necessary data ───────────────────────────────────────────────
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

# ─── Run variants ────────────────────────────────────────────────────────────
print("\n[2/4] Running 5 variants…\n")
print(f"  {'Variant':<45} {'CAGR':>8} {'Sharpe':>7} {'DD':>8} {'Calmar':>7} {'Trades':>7} {'%Skipped':>10}")
print(f"  {'-'*45} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*7} {'-'*10}")

results = []
for label, max_days in [
    ("F0 baseline (no filter)",  None),
    ("F1 max 60d since release", 60),
    ("F2 max 90d since release", 90),
    ("F3 max 120d since release", 120),
    ("F4 max 150d since release", 150),
]:
    # Filter signals
    if max_days is None:
        sig_filtered = sig
        n_skipped = 0
    else:
        # Keep signals with days_since_release ≤ max_days, OR NaN (no release info → conservatively skip)
        mask = sig["days_since_release"].notna() & (sig["days_since_release"] <= max_days)
        sig_filtered = sig[mask].copy()
        n_skipped = len(sig) - len(sig_filtered)

    pct_skipped = n_skipped / len(sig) * 100

    nav_df, trades_df = simulate(sig_filtered, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_by_date,
        **LIQ, name=label)
    m = metrics(nav_df, trades_df, label)
    results.append({"variant": label, "max_days": max_days, **m,
                     "pct_skipped": pct_skipped})

    print(f"  {label:<45} {m['cagr_pct']:>+7.2f}% {m['sharpe']:>+7.2f} "
          f"{m['max_dd_pct']:>+7.1f}% {m['calmar']:>+7.2f} {m['n_trades']:>7d} "
          f"{pct_skipped:>+9.1f}%")

# ─── Δ analysis ──────────────────────────────────────────────────────────────
df_res = pd.DataFrame(results)
base = df_res.iloc[0]
print(f"\n[3/4] Δ vs F0 baseline (CAGR={base['cagr_pct']:.2f}%, Sh={base['sharpe']:.2f}):\n")
for _, r in df_res.iterrows():
    if r["variant"].startswith("F0"):
        continue
    print(f"  {r['variant']:<45}")
    print(f"    ΔCAGR {r['cagr_pct']-base['cagr_pct']:+.2f}pp, "
          f"ΔSharpe {r['sharpe']-base['sharpe']:+.2f}, "
          f"ΔDD {r['max_dd_pct']-base['max_dd_pct']:+.1f}pp, "
          f"Trades {int(r['n_trades']-base['n_trades']):+d}")

# ─── Earnings-season specific analysis ───────────────────────────────────────
print(f"\n[4/4] Earnings season (Apr-May + Oct-Nov) — specific impact:\n")

# For each variant, count trades that entered during earnings season
for label, max_days in [
    ("F0 baseline (no filter)",  None),
    ("F2 max 90d since release", 90),
    ("F4 max 150d since release", 150),
]:
    if max_days is None:
        sig_filtered = sig
    else:
        mask = sig["days_since_release"].notna() & (sig["days_since_release"] <= max_days)
        sig_filtered = sig[mask].copy()

    nav_df, trades_df = simulate(sig_filtered, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_by_date,
        **LIQ, name=label)
    trades_df["entry_date"] = pd.to_datetime(trades_df["entry_date"])
    trades_df["entry_month"] = trades_df["entry_date"].dt.month
    es_trades = trades_df[trades_df["entry_month"].isin([4, 5, 10, 11])]
    print(f"  {label}")
    print(f"    Total trades: {len(trades_df)}")
    print(f"    Earnings season entries: {len(es_trades)} "
          f"({len(es_trades)/len(trades_df)*100:.1f}%)")
    if len(es_trades) > 0:
        print(f"    Avg ret (earnings entries): {es_trades['ret_net'].mean()*100:+.2f}%")
        print(f"    Win rate (earnings entries): {(es_trades['ret_net']>0).mean()*100:.1f}%")
        stops = (es_trades["reason"] == "STOP").sum()
        print(f"    STOP hits (earnings entries): {stops} ({stops/len(es_trades)*100:.1f}%)")

# Save
df_res.to_csv(os.path.join(WORKDIR, "data/fresh_q_filter_results.csv"), index=False)
print(f"\n  Saved: fresh_q_filter_results.csv")
