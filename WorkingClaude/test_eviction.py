"""Test AGGRESSIVE strategy with vs without priority eviction."""
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

TIERS_AGG = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
             "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"]
TIERS_HC = ["MEGA", "MOMENTUM", "MOMENTUM_N"]
TIERS_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]

CONFIGS = [
    ("AGG_7p_45d_15sl_NoEvict", TIERS_AGG, 7, 45, -0.15, False),
    ("AGG_7p_45d_15sl_Evict",   TIERS_AGG, 7, 45, -0.15, True),
    ("HC_10p_30d_20sl_NoEvict", TIERS_HC, 10, 30, -0.20, False),
    ("HC_10p_30d_20sl_Evict",   TIERS_HC, 10, 30, -0.20, True),
    ("BAL_10p_60d_15sl_NoEvict",TIERS_BAL,10, 60, -0.15, False),
    ("BAL_10p_60d_15sl_Evict",  TIERS_BAL,10, 60, -0.15, True),
]

results = []
for name, tiers, mp, h, sl, evict in CONFIGS:
    print(f"\nRunning {name}...")
    nav_df, trades_df = simulate(
        sig, prices, vni_dates,
        allowed_tiers=tiers, max_positions=mp,
        hold_days=h, stop_loss=sl, min_hold=2,
        eviction=evict, eviction_priority_gap=15,
    )
    m = metrics(nav_df, trades_df, name)
    # Tier mix
    tier_mix = trades_df.groupby("play_type").agg(
        n=("ret_net", "count"), avg=("ret_net", "mean")
    ).sort_values("n", ascending=False)
    m["tier_mix"] = tier_mix
    results.append((name, nav_df, trades_df, m))
    print(f"  CAGR={m['cagr_pct']:.1f}%  Sh={m['sharpe']:.2f}  DD={m['max_dd_pct']:.1f}%  "
          f"trades={m['n_trades']}")

# Compare side-by-side
print("\n" + "═" * 110)
print("  EVICTION vs NO-EVICTION COMPARISON")
print("═" * 110)
cols = ["name", "cagr_pct", "sharpe", "sortino", "max_dd_pct", "calmar",
        "n_trades", "win_rate_pct", "avg_trade_ret_pct"]
summary = pd.DataFrame([r[3] for r in results])
print(summary[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Tier mix comparison for AGG
print("\n" + "═" * 110)
print("  AGG TIER MIX: NO_EVICT vs EVICT")
print("═" * 110)
for name, _, _, m in results:
    if "AGG_7p" in name:
        print(f"\n  {name}:")
        print(m["tier_mix"].to_string(float_format=lambda x: f"{x:.3f}"))

# Eviction events
print("\n" + "═" * 110)
print("  EVICTION TRADES (AGG_Evict)")
print("═" * 110)
for name, _, trades_df, _ in results:
    if "AGG" in name and "Evict" in name and "NoEvict" not in name:
        evicts = trades_df[trades_df["reason"] == "EVICT"]
        print(f"  {name}: {len(evicts)} evictions")
        if len(evicts):
            print(f"  Avg ret of evicted positions: {evicts['ret_net'].mean()*100:+.2f}%")
            print(f"  Eviction breakdown by tier:")
            print(evicts.groupby("play_type")["ret_net"].agg(["count", "mean"]).to_string())

print("\n  Saved tier_mix and detailed comparison")
