"""Test alternative tier compositions to fix capacity issue.

Strategy: instead of eviction, exclude weak tiers so slots free up for higher conviction.
"""
import os
import sys
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import (
    simulate, metrics, bq, SIGNAL_QUERY, VNI_QUERY, START_DATE, END_DATE
)

print("Loading data...")
sig = bq(SIGNAL_QUERY.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}

# Test variants
TIER_VARIANTS = {
    "AGG_full": ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
                 "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"],
    "AGG_no_SN": ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
                  "DEEP_VALUE_RECOVERY"],   # drop MOMENTUM_S_N
    "AGG_no_SN_no_A": ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S",
                       "DEEP_VALUE_RECOVERY"],   # drop A and S_N
    "TOP3": ["MEGA", "MOMENTUM", "MOMENTUM_N"],   # top 3 tiers only
    "TOP3+S": ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S"],
    "BAL_no_DVR": ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S"],   # bal w/o DVR
}

# Same params (max_pos=7, hold=45d, stop=-15%)
PARAMS = {"max_positions": 7, "hold_days": 45, "stop_loss": -0.15, "min_hold": 2}

results = []
for name, tiers in TIER_VARIANTS.items():
    print(f"\nRunning {name} (n_tiers={len(tiers)})...")
    nav_df, trades_df = simulate(sig, prices, vni_dates, allowed_tiers=tiers, **PARAMS)
    m = metrics(nav_df, trades_df, name)
    tier_mix = trades_df.groupby("play_type").agg(
        n=("ret_net", "count"), avg_ret=("ret_net", "mean")
    ).sort_values("n", ascending=False) if len(trades_df) else pd.DataFrame()
    results.append({"name": name, "metrics": m, "tier_mix": tier_mix,
                    "trades": trades_df, "nav": nav_df})
    print(f"  CAGR={m['cagr_pct']:.1f}%  Sh={m['sharpe']:.2f}  DD={m['max_dd_pct']:.1f}%  "
          f"trades={m['n_trades']}  WinRate={m['win_rate_pct']:.1f}%")

print("\n" + "═" * 100)
print("  COMPARISON")
print("═" * 100)
cols = ["name", "cagr_pct", "sharpe", "sortino", "max_dd_pct", "calmar",
        "n_trades", "win_rate_pct", "avg_trade_ret_pct"]
summary = pd.DataFrame([{"name": r["name"], **r["metrics"]} for r in results])
print(summary[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Tier mix details
print("\n" + "═" * 100)
print("  TIER MIX BY VARIANT")
print("═" * 100)
for r in results:
    print(f"\n  {r['name']}:")
    if not r["tier_mix"].empty:
        print(r["tier_mix"].to_string(float_format=lambda x: f"{x:.3f}"))

# Per-tier capture rate
print("\n" + "═" * 100)
print("  CAPTURE RATE — n_trades per tier vs available signals")
print("═" * 100)
tier_signals = sig.groupby("play_type").size()
print(f"\n  Available signals (full history):")
print(tier_signals.sort_values(ascending=False).head(10).to_string())

print("\n  Capture rate by variant:")
header = f"  {'Tier':25}{'#Signals':>10} | "
for r in results:
    header += f"{r['name'][:14]:>14} | "
print(header)
for tier in ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
             "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"]:
    n_sig = tier_signals.get(tier, 0)
    line = f"  {tier:25}{n_sig:>10} | "
    for r in results:
        n_cap = r["tier_mix"].get("n", {}).get(tier, 0)
        rate = n_cap / n_sig * 100 if n_sig > 0 else 0
        line += f"{n_cap:>5} ({rate:4.1f}%) | "
    print(line)
