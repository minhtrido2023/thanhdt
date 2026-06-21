"""Test re-entry blacklist after STOP exit.

Hypothesis: stocks that hit -20% stop may be in downtrend, re-entering may compound losses.
But they may also rebound. Test to find optimal blacklist period.
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

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
TIER_AGG = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
            "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"]

# Test blacklist on BAL and AGG
BLACKLIST_DAYS = [0, 10, 20, 30, 45, 60, 90]

print("\nBALANCED 10p 45d -20% with re-entry blacklist...")
print(f"  {'BL_days':>10} {'CAGR':>8} {'Sharpe':>8} {'DD':>8} {'Calmar':>7} {'trades':>7} {'win%':>6} {'STOP%':>6}")
bal_results = []
for bd in BLACKLIST_DAYS:
    nav_df, trades_df = simulate(
        sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, reentry_blacklist_days=bd,
    )
    m = metrics(nav_df, trades_df, f"BAL_BL{bd}")
    m["bl_days"] = bd
    bal_results.append(m)
    print(f"  {bd:>10}d {m['cagr_pct']:>7.2f}% {m['sharpe']:>8.2f} "
          f"{m['max_dd_pct']:>7.1f}% {m['calmar']:>7.2f} "
          f"{m['n_trades']:>7d} {m['win_rate_pct']:>5.1f}% "
          f"{m['stop_pct']:>5.1f}%")

print("\nAGGRESSIVE 7p 45d -15% with re-entry blacklist...")
print(f"  {'BL_days':>10} {'CAGR':>8} {'Sharpe':>8} {'DD':>8} {'Calmar':>7} {'trades':>7} {'win%':>6} {'STOP%':>6}")
agg_results = []
for bd in BLACKLIST_DAYS:
    nav_df, trades_df = simulate(
        sig, prices, vni_dates,
        allowed_tiers=TIER_AGG, max_positions=7, hold_days=45, stop_loss=-0.15,
        min_hold=2, slippage=0.001, reentry_blacklist_days=bd,
    )
    m = metrics(nav_df, trades_df, f"AGG_BL{bd}")
    m["bl_days"] = bd
    agg_results.append(m)
    print(f"  {bd:>10}d {m['cagr_pct']:>7.2f}% {m['sharpe']:>8.2f} "
          f"{m['max_dd_pct']:>7.1f}% {m['calmar']:>7.2f} "
          f"{m['n_trades']:>7d} {m['win_rate_pct']:>5.1f}% "
          f"{m['stop_pct']:>5.1f}%")

# Summary
print("\n" + "═" * 100)
print("  BLACKLIST IMPACT — BAL")
print("═" * 100)
df_bal = pd.DataFrame(bal_results)
cols = ["bl_days", "cagr_pct", "sharpe", "sortino", "max_dd_pct", "calmar",
        "n_trades", "win_rate_pct", "avg_trade_ret_pct", "stop_pct"]
print(df_bal[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))
base_bal = df_bal[df_bal["bl_days"] == 0].iloc[0]
print("\n  Δ vs no blacklist:")
for _, r in df_bal.iterrows():
    if r["bl_days"] == 0:
        continue
    print(f"    BL={int(r['bl_days']):>3}d: ΔCAGR={r['cagr_pct']-base_bal['cagr_pct']:+.2f}pp "
          f"ΔSharpe={r['sharpe']-base_bal['sharpe']:+.3f} "
          f"ΔDD={r['max_dd_pct']-base_bal['max_dd_pct']:+.1f}pp "
          f"Δtrades={int(r['n_trades']-base_bal['n_trades']):+d}")

print("\n" + "═" * 100)
print("  BLACKLIST IMPACT — AGG")
print("═" * 100)
df_agg = pd.DataFrame(agg_results)
print(df_agg[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))
base_agg = df_agg[df_agg["bl_days"] == 0].iloc[0]
print("\n  Δ vs no blacklist:")
for _, r in df_agg.iterrows():
    if r["bl_days"] == 0:
        continue
    print(f"    BL={int(r['bl_days']):>3}d: ΔCAGR={r['cagr_pct']-base_agg['cagr_pct']:+.2f}pp "
          f"ΔSharpe={r['sharpe']-base_agg['sharpe']:+.3f} "
          f"ΔDD={r['max_dd_pct']-base_agg['max_dd_pct']:+.1f}pp "
          f"Δtrades={int(r['n_trades']-base_agg['n_trades']):+d}")

df_bal.to_csv(os.path.join(WORKDIR, "data/blacklist_results_BAL.csv"), index=False)
df_agg.to_csv(os.path.join(WORKDIR, "data/blacklist_results_AGG.csv"), index=False)
print("\n  Saved: blacklist_results_BAL.csv, blacklist_results_AGG.csv")
