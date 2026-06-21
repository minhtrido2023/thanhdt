"""Compare full-history-tuned vs OOS-tuned configs on full history.

For each tier set, take both configs and run on full 2014-2026:
  - Full-history-tuned: e.g., BALANCED 10p 60d -15%
  - OOS-tuned: e.g., BALANCED 10p 45d -20%

Compare which is more robust + which has better forward expected metrics.
"""
import os
import sys
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import (
    simulate, metrics, bq, SIGNAL_QUERY, VNI_QUERY,
    START_DATE, END_DATE, INIT_NAV
)

print("Loading full-history data...")
sig = bq(SIGNAL_QUERY.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}

TIER_SETS = {
    "MEGA":         ["MEGA"],
    "HIGH_CONV":    ["MEGA", "MOMENTUM", "MOMENTUM_N"],
    "BALANCED":     ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"],
    "AGGRESSIVE":   ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
                     "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"],
}

# Configs: (name, tier_set, max_pos, hold, stop)
CONFIGS = [
    # Full-history-tuned (from finetune_holistic.py)
    ("FULL_BAL_10p_60d_15sl",  "BALANCED",  10, 60, -0.15),
    ("FULL_HC_10p_30d_10sl",   "HIGH_CONV", 10, 30, -0.10),
    ("FULL_HC_10p_30d_20sl",   "HIGH_CONV", 10, 30, -0.20),  # also good
    ("FULL_AGG_7p_45d_15sl",   "AGGRESSIVE", 7, 45, -0.15),
    # OOS-tuned (from finetune_oos.py)
    ("OOS_BAL_10p_45d_20sl",   "BALANCED",  10, 45, -0.20),  # ⭐ winner OOS
    ("OOS_HC_10p_30d_20sl",    "HIGH_CONV", 10, 30, -0.20),  # OOS Sh=1.26
    ("OOS_BAL_10p_60d_15sl",   "BALANCED",  10, 60, -0.15),  # OOS Sh=1.25
    ("OOS_AGG_7p_60d_10sl",    "AGGRESSIVE", 7, 60, -0.10),  # OOS AGG winner
]

results = []
for name, tier_name, mp, h, sl in CONFIGS:
    print(f"\n  Running {name}...")
    nav_df, trades_df = simulate(
        sig, prices, vni_dates,
        allowed_tiers=TIER_SETS[tier_name],
        max_positions=mp, hold_days=h, stop_loss=sl, min_hold=2,
    )
    m = metrics(nav_df, trades_df, name)
    results.append({"name": name, **m})
    print(f"    CAGR={m['cagr_pct']:.1f}%, Sh={m['sharpe']:.2f}, "
          f"DD={m['max_dd_pct']:.1f}%, Cal={m['calmar']:.2f}")

# Side-by-side
print("\n" + "═" * 110)
print("  COMPARISON ON FULL HISTORY (2014-2026)")
print("═" * 110)
df = pd.DataFrame(results)
cols = ["name", "cagr_pct", "sharpe", "sortino", "max_dd_pct", "calmar",
        "n_trades", "win_rate_pct", "avg_trade_ret_pct", "avg_hold_days"]
print(df[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Pair comparison
print("\n" + "═" * 110)
print("  PAIRWISE: FULL-HIST vs OOS-tuned (same tier set)")
print("═" * 110)
pairs = [
    ("BALANCED", "FULL_BAL_10p_60d_15sl", "OOS_BAL_10p_45d_20sl"),
    ("BALANCED", "FULL_BAL_10p_60d_15sl", "OOS_BAL_10p_60d_15sl"),
    ("HIGH_CONV", "FULL_HC_10p_30d_10sl", "OOS_HC_10p_30d_20sl"),
    ("HIGH_CONV", "FULL_HC_10p_30d_20sl", "OOS_HC_10p_30d_20sl"),  # same
    ("AGGRESSIVE", "FULL_AGG_7p_45d_15sl", "OOS_AGG_7p_60d_10sl"),
]
for tier_set, full_name, oos_name in pairs:
    full = df[df["name"] == full_name].iloc[0] if len(df[df["name"] == full_name]) else None
    oos = df[df["name"] == oos_name].iloc[0] if len(df[df["name"] == oos_name]) else None
    if full is not None and oos is not None:
        print(f"\n  {tier_set}:")
        print(f"    Full-hist params: {full_name}")
        print(f"      CAGR={full['cagr_pct']:.1f}%  Sh={full['sharpe']:.2f}  "
              f"DD={full['max_dd_pct']:.1f}%  Cal={full['calmar']:.2f}")
        print(f"    OOS-tuned params: {oos_name}")
        print(f"      CAGR={oos['cagr_pct']:.1f}%  Sh={oos['sharpe']:.2f}  "
              f"DD={oos['max_dd_pct']:.1f}%  Cal={oos['calmar']:.2f}")
        print(f"    Δ:  CAGR={oos['cagr_pct']-full['cagr_pct']:+.1f}pp  "
              f"Sh={oos['sharpe']-full['sharpe']:+.2f}  "
              f"DD={oos['max_dd_pct']-full['max_dd_pct']:+.1f}pp  "
              f"Cal={oos['calmar']-full['calmar']:+.2f}")

df.to_csv(os.path.join(WORKDIR, "compare_full_vs_oos.csv"), index=False)
