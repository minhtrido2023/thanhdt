# -*- coding: utf-8 -*-
"""Adaptive Fresh Q Filter — only apply filter in Q1 earnings season (Apr-May).

Insight from per-season analysis: F1 (60d) helps Q1 massively (+12.96pp avg ret)
but hurts non-earnings months (-3.29pp). Solution: adaptive filter — only kick
in during Q1 season, leave other periods unfiltered.

Variants tested:
  F0  baseline (no filter)
  F1  60d everywhere (uniform)
  F2  60d only in Q1 (Apr-May) — ADAPTIVE proposal
  F3  60d only in Q1+Q4 (Apr-May + Jan-Feb)
  F4  60d in all 4 earnings seasons (Apr-May, Jul-Aug, Oct-Nov, Jan-Feb)
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
print("  ADAPTIVE F1 — apply 60d filter only in selected earnings seasons")
print(f"  Period: {START_DATE} → {END_DATE}")
print("=" * 100)

print("\n[1/3] Loading data + release dates…")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])

releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY tf.ticker, tf.Release_Date""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
# Defensive: explicit sort before groupby (BQ ORDER BY → preserved via pandas)
releases = releases.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
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


def apply_filter(sig, filter_months, max_days=60):
    """Apply 60d filter only in specified months; pass-through otherwise."""
    if not filter_months:
        return sig
    in_filter = sig["month"].isin(filter_months)
    # Filter rows: pass if (not in filter_months) OR (in filter_months AND days <= max_days)
    keep = (~in_filter) | (sig["days_since_release"].notna() & (sig["days_since_release"] <= max_days))
    return sig[keep].copy()


variants = [
    ("F0 baseline (no filter)",             []),
    ("F1 60d EVERYWHERE",                   [1,2,3,4,5,6,7,8,9,10,11,12]),
    ("F2 60d only Q1 (Apr-May)",            [4, 5]),
    ("F3 60d only Q1+Q4 (Apr-May, Jan-Feb)", [1, 2, 4, 5]),
    ("F4 60d in all 4 earnings seasons",    [1, 2, 4, 5, 7, 8, 10, 11]),
]

print("\n[2/3] Running 5 variants…\n")
print(f"  {'Variant':<45} {'CAGR':>8} {'Sharpe':>7} {'DD':>8} {'Calmar':>7} {'Trades':>7} {'Skipped':>9}")
print(f"  {'-'*45} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*7} {'-'*9}")

results = []
trade_logs = {}
for label, months in variants:
    sig_filt = apply_filter(sig, months)
    n_skipped = len(sig) - len(sig_filt)

    nav_df, trades_df = simulate(sig_filt, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_by_date,
        **LIQ, name=label)
    m = metrics(nav_df, trades_df, label)
    results.append({"variant": label, **m, "n_skipped": n_skipped})
    trades_df["entry_date"] = pd.to_datetime(trades_df["entry_date"])
    trades_df["entry_month"] = trades_df["entry_date"].dt.month
    trade_logs[label] = trades_df

    print(f"  {label:<45} {m['cagr_pct']:>+7.2f}% {m['sharpe']:>+7.2f} "
          f"{m['max_dd_pct']:>+7.1f}% {m['calmar']:>+7.2f} {m['n_trades']:>7d} "
          f"{n_skipped:>+8d}")

df_res = pd.DataFrame(results)
base = df_res.iloc[0]
print(f"\n[3/3] Δ vs F0 baseline (CAGR={base['cagr_pct']:.2f}%, Sh={base['sharpe']:.2f}):\n")
for _, r in df_res.iterrows():
    if r["variant"].startswith("F0"):
        continue
    delta_cagr = r["cagr_pct"] - base["cagr_pct"]
    delta_sh = r["sharpe"] - base["sharpe"]
    delta_dd = r["max_dd_pct"] - base["max_dd_pct"]
    print(f"  {r['variant']:<45}")
    print(f"    ΔCAGR {delta_cagr:+.2f}pp, ΔSharpe {delta_sh:+.2f}, "
          f"ΔDD {delta_dd:+.1f}pp, ΔTrades {int(r['n_trades']-base['n_trades']):+d}")

# Per-season trade detail for top variants
print(f"\n  Per-season win rate (top 3 variants):")
print(f"  {'Season':<35} {'F0':>10} {'F1 all':>10} {'F2 Q1-only':>12} {'F4 all-4':>10}")
seasons = {"Q1 (Apr-May)": [4,5], "Q2 (Jul-Aug)": [7,8], "Q3 (Oct-Nov)": [10,11],
            "Q4 (Jan-Feb)": [1,2], "Non-earnings": [3,6,9,12]}
for sname, months in seasons.items():
    line = f"  {sname:<35}"
    for v_label in ["F0 baseline (no filter)", "F1 60d EVERYWHERE",
                     "F2 60d only Q1 (Apr-May)", "F4 60d in all 4 earnings seasons"]:
        tdf = trade_logs[v_label]
        sub = tdf[tdf["entry_month"].isin(months)]
        wr = (sub["ret_net"] > 0).mean() * 100 if len(sub) else 0
        line += f" {wr:>+8.1f}% ({len(sub):>3})"
    print(line)

df_res.to_csv(os.path.join(WORKDIR, "data/fresh_q_adaptive_results.csv"), index=False)
print(f"\n  Saved: fresh_q_adaptive_results.csv")
