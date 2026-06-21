"""Test how Holistic engine scales from 1B to 50B capital with realistic constraints.

Adds:
  - Multi-day fills (max 5 days) when daily liquidity insufficient
  - Cap per-day buy at 20% of daily turnover (no market impact)
  - 30% min fill ratio (abandon order if can't fill enough)
  - BL20 default

Compares:
  A) 1B baseline (no liquidity constraint, current behavior)
  B) 1B with liquidity constraints (verify backwards compatible)
  C) 50B with liquidity constraints (real-world test)
  D) 50B with stricter constraints (10% volume cap)
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
liquidity_lookup = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
print(f"  {len(sig):,} signals, {len(liquidity_lookup):,} liquidity entries")

# Liquidity stats
print("\nLiquidity (Volume_3M_P50 × Close, VND/day):")
liq_series = pd.Series(list(liquidity_lookup.values()))
print(f"  Median: {liq_series.median()/1e9:.2f}B")
print(f"  P25: {liq_series.quantile(0.25)/1e9:.2f}B  P75: {liq_series.quantile(0.75)/1e9:.2f}B")
print(f"  P90: {liq_series.quantile(0.90)/1e9:.2f}B  P95: {liq_series.quantile(0.95)/1e9:.2f}B")
print(f"  Max:  {liq_series.max()/1e9:.2f}B")

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
COMMON = dict(allowed_tiers=TIER_BAL, max_positions=10, hold_days=45,
              stop_loss=-0.20, min_hold=2, slippage=0.001)

VARIANTS = [
    ("A_1B_no_liq",        {"init_nav": 1e9}),
    ("B_1B_with_liq_20pct", {"init_nav": 1e9,
                              "liquidity_volume_pct": 0.20,
                              "max_fill_days": 5,
                              "liquidity_lookup": liquidity_lookup}),
    ("C_50B_liq_20pct",    {"init_nav": 5e10,
                              "liquidity_volume_pct": 0.20,
                              "max_fill_days": 5,
                              "liquidity_lookup": liquidity_lookup}),
    ("D_50B_liq_10pct",    {"init_nav": 5e10,
                              "liquidity_volume_pct": 0.10,
                              "max_fill_days": 5,
                              "liquidity_lookup": liquidity_lookup}),
    ("E_50B_liq_20pct_10d", {"init_nav": 5e10,
                              "liquidity_volume_pct": 0.20,
                              "max_fill_days": 10,
                              "liquidity_lookup": liquidity_lookup}),
    ("F_50B_liq_5pct",     {"init_nav": 5e10,
                              "liquidity_volume_pct": 0.05,
                              "max_fill_days": 5,
                              "liquidity_lookup": liquidity_lookup}),
]

results = []
all_navs = {}
for name, extra in VARIANTS:
    print(f"\n=== Running {name} ===")
    nav_df, trades_df = simulate(sig, prices, vni_dates, **COMMON, **extra)
    m = metrics(nav_df, trades_df, name)
    init = extra.get("init_nav", 1e9)
    final = nav_df["nav"].iloc[-1]
    m["init_B"] = init / 1e9
    m["final_B"] = final / 1e9
    m["wealth_x"] = final / init
    all_navs[name] = nav_df.set_index(pd.to_datetime(nav_df["time"]))["nav"] / init
    results.append(m)
    print(f"  Init={init/1e9:.0f}B → Final={final/1e9:.1f}B (×{final/init:.2f})")
    print(f"  CAGR={m['cagr_pct']:.2f}%  Sh={m['sharpe']:.2f}  DD={m['max_dd_pct']:.1f}%  "
          f"trades={m['n_trades']}  WinRate={m['win_rate_pct']:.1f}%")

# Summary
print("\n" + "═" * 110)
print("  CAPITAL SCALING TEST — BAL 10p 45d -20% + BL20 + slip 0.1%")
print("═" * 110)
df = pd.DataFrame(results)
cols = ["name", "init_B", "wealth_x", "cagr_pct", "sharpe", "sortino", "max_dd_pct",
        "calmar", "n_trades", "win_rate_pct", "avg_trade_ret_pct"]
print(df[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Pairwise: 1B vs 50B
print("\n" + "═" * 110)
print("  CAPITAL SCALING IMPACT (1B baseline vs 50B realistic)")
print("═" * 110)
base = df[df["name"] == "B_1B_with_liq_20pct"].iloc[0]
print(f"  1B with liq constraint: CAGR={base['cagr_pct']:.2f}% Sh={base['sharpe']:.2f}")
for _, r in df.iterrows():
    if r["name"] == base["name"]:
        continue
    if "50B" in r["name"]:
        print(f"  {r['name']}: ΔCAGR={r['cagr_pct']-base['cagr_pct']:+.2f}pp  "
              f"ΔSharpe={r['sharpe']-base['sharpe']:+.3f}  "
              f"ΔDD={r['max_dd_pct']-base['max_dd_pct']:+.1f}pp  "
              f"trades={int(r['n_trades'])} (vs {int(base['n_trades'])})")

# 2022 crash
print("\n" + "═" * 110)
print("  2022 CRASH DEFENSE")
print("═" * 110)
for name, nav in all_navs.items():
    n2021 = nav[nav.index.year == 2021].iloc[-1]
    n2022 = nav[nav.index.year == 2022].iloc[-1]
    chg = (n2022 / n2021 - 1) * 100
    print(f"  {name:30} {chg:+.2f}%")

df.to_csv(os.path.join(WORKDIR, "capital_scaling_results.csv"), index=False)
print("\n  Saved: capital_scaling_results.csv")
