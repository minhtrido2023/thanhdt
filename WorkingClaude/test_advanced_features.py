"""Test advanced features: exit slippage tiered, sector rotation, HC vs BAL."""
import os
import sys
import numpy as np
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

sec_query = """
SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code / 1000) AS INT64) AS sector_top
FROM tav2_bq.ticker AS t
WHERE t.ICB_Code IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
"""
sec_map = bq(sec_query).set_index("ticker")["sector_top"].to_dict()

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
TIER_AGG = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
            "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"]
TIER_HC = ["MEGA", "MOMENTUM", "MOMENTUM_N"]

LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
       "liquidity_lookup": liquidity_lookup}


# ─── PART A: Exit slippage tiered ──────────────────────────────────────
print("\n" + "═" * 100)
print("  PART A — TIERED EXIT SLIPPAGE TEST (extra slip when >5/10/20% ADV)")
print("═" * 100)

for nav in [1e9, 50e9, 100e9]:
    print(f"\n  NAV = {nav/1e9:.0f}B")
    for label, exit_slip_tiered in [("no exit slip extra", False),
                                     ("tiered exit slip", True)]:
        nav_df, trades_df = simulate(
            sig, prices, vni_dates, allowed_tiers=TIER_BAL,
            max_positions=10, hold_days=45, stop_loss=-0.20, min_hold=2,
            slippage=0.001, init_nav=nav, exit_slippage_tiered=exit_slip_tiered,
            **LIQ,
        )
        m = metrics(nav_df, trades_df, f"{nav/1e9:.0f}B_{label}")
        # Count trades that triggered extra slippage
        extra_slip_n = (trades_df["exit_extra_slip"] > 0).sum() if "exit_extra_slip" in trades_df else 0
        print(f"    {label:25}: CAGR={m['cagr_pct']:5.2f}%  Sh={m['sharpe']:.2f}  "
              f"DD={m['max_dd_pct']:.1f}%  trades={m['n_trades']}  "
              f"slip-tiered exits={extra_slip_n}")

# ─── PART B: Sector rotation tests ────────────────────────────────────
print("\n" + "═" * 100)
print("  PART B — SECTOR ROTATION (cap Fin/RE specifically)")
print("═" * 100)

VARIANTS = [
    ("base (no caps)", {"sector_limit": None}),
    ("global lim 3", {"sector_limit": 3, "ticker_sector_map": sec_map}),
    ("global lim 2", {"sector_limit": 2, "ticker_sector_map": sec_map}),
    ("Fin/RE max 4", {"sector_limit_per_sector": {8: 4}, "ticker_sector_map": sec_map}),
    ("Fin/RE max 3", {"sector_limit_per_sector": {8: 3}, "ticker_sector_map": sec_map}),
    ("Fin/RE max 2", {"sector_limit_per_sector": {8: 2}, "ticker_sector_map": sec_map}),
    ("Excl Fin/RE entirely", {"sector_limit_per_sector": {8: 0}, "ticker_sector_map": sec_map}),
]

print(f"\n  Running BAL_50B with various sector controls...")
print(f"  {'Config':30} | {'CAGR':>7} {'Sh':>6} {'DD':>7} {'Cal':>5} {'trades':>7} {'win%':>6}")
sec_rot_results = []
for name, extra in VARIANTS:
    nav_df, trades_df = simulate(
        sig, prices, vni_dates, allowed_tiers=TIER_BAL,
        max_positions=10, hold_days=45, stop_loss=-0.20, min_hold=2,
        slippage=0.001, init_nav=50e9, exit_slippage_tiered=True,
        **LIQ, **extra,
    )
    m = metrics(nav_df, trades_df, name)
    # Sector mix
    trades_df["sector_top"] = trades_df["ticker"].map(sec_map).fillna(-1).astype(int)
    fin_pct = (trades_df["sector_top"] == 8).mean() * 100 if len(trades_df) else 0
    m["fin_pct"] = fin_pct
    sec_rot_results.append({"name": name, **m})
    print(f"  {name:30} | {m['cagr_pct']:>6.2f}% {m['sharpe']:>6.2f} "
          f"{m['max_dd_pct']:>6.1f}% {m['calmar']:>5.2f} "
          f"{m['n_trades']:>7d} {m['win_rate_pct']:>5.1f}%  Fin/RE={fin_pct:.0f}%")

# ─── PART C: HC vs BAL at multiple NAVs ────────────────────────────────
print("\n" + "═" * 100)
print("  PART C — HC vs BAL at 1B / 50B / 100B (with realistic exit slippage)")
print("═" * 100)

print(f"\n  {'Config':25} | {'CAGR':>7} {'Sh':>6} {'DD':>7} {'Cal':>5} {'Wealth':>7}")
hc_bal_results = []
for nav in [1e9, 30e9, 50e9, 100e9, 200e9]:
    for tier_name, tiers, mp, h, sl in [
        ("BAL", TIER_BAL, 10, 45, -0.20),
        ("HC", TIER_HC, 10, 30, -0.20),
    ]:
        nav_df, trades_df = simulate(
            sig, prices, vni_dates, allowed_tiers=tiers,
            max_positions=mp, hold_days=h, stop_loss=sl, min_hold=2,
            slippage=0.001, init_nav=nav, exit_slippage_tiered=True,
            **LIQ,
        )
        m = metrics(nav_df, trades_df, f"{tier_name}_{nav/1e9:.0f}B")
        m["nav_B"] = nav / 1e9
        m["strategy"] = tier_name
        m["wealth_x"] = nav_df["nav"].iloc[-1] / nav
        hc_bal_results.append({"name": m["name"], **m})
        print(f"  {tier_name}_{nav/1e9:.0f}B".ljust(27) + f"| "
              f"{m['cagr_pct']:>6.2f}% {m['sharpe']:>6.2f} "
              f"{m['max_dd_pct']:>6.1f}% {m['calmar']:>5.2f} "
              f"{m['wealth_x']:>6.2f}×")

# ─── PART D: Exit signal effectiveness ────────────────────────────────
print("\n" + "═" * 100)
print("  PART D — EXIT SIGNAL ANALYSIS (BAL_50B with tiered slip)")
print("═" * 100)

nav_df, trades_df = simulate(
    sig, prices, vni_dates, allowed_tiers=TIER_BAL,
    max_positions=10, hold_days=45, stop_loss=-0.20, min_hold=2,
    slippage=0.001, init_nav=50e9, exit_slippage_tiered=True,
    **LIQ,
)
print(f"\n  Total trades: {len(trades_df)}")
print(f"\n  Exit reason mix:")
reason_stats = trades_df.groupby("reason").agg(
    n=("ret_net", "count"),
    avg_ret=("ret_net", "mean"),
    median_ret=("ret_net", "median"),
    win=("ret_net", lambda x: (x > 0).mean() * 100),
    avg_hold=("days_held", "mean"),
).sort_values("n", ascending=False)
print(reason_stats.to_string(float_format=lambda x: f"{x:.3f}"))

# Exit slip magnitude
if "exit_extra_slip" in trades_df.columns:
    slip_dist = trades_df["exit_extra_slip"]
    print(f"\n  Exit slip distribution:")
    print(f"    No slip (0%): {(slip_dist == 0).sum()} trades")
    print(f"    Small (0.1%): {(slip_dist == 0.001).sum()} trades")
    print(f"    Medium (0.3%): {(slip_dist == 0.003).sum()} trades")
    print(f"    Large (0.5%): {(slip_dist == 0.005).sum()} trades")

# Forward-looking outcomes by exit reason: did we exit too early/late?
# Check: for STOP exits, did the stock recover by T+10/T+20?
print("\n  STOP exits — recovery analysis (would we have benefited from holding?):")
stop_trades = trades_df[trades_df["reason"] == "STOP"].head(20)
print(f"    n_stops shown: {len(stop_trades)}, total stops: {(trades_df['reason']=='STOP').sum()}")

# Save
df_a = pd.DataFrame(sec_rot_results)
df_a.to_csv(os.path.join(WORKDIR, "sector_rotation_50B.csv"), index=False)
df_b = pd.DataFrame(hc_bal_results)
df_b.to_csv(os.path.join(WORKDIR, "hc_vs_bal_scaling.csv"), index=False)
trades_df.to_csv(os.path.join(WORKDIR, "exit_analysis_trades.csv"), index=False)
print(f"\n  Saved: sector_rotation_50B.csv, hc_vs_bal_scaling.csv, exit_analysis_trades.csv")
