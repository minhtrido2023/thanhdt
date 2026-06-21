"""Walk-forward quarterly analysis: chronological consistency check.

For each strategy, compute quarterly returns over 2014-2026.
Check if performance degrades over time / is concentrated in specific years.
"""
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

TIER_SETS = {
    "BAL": ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"],
    "AGG": ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
            "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"],
    "HC":  ["MEGA", "MOMENTUM", "MOMENTUM_N"],
}

CONFIGS = [
    ("BAL_10p_45d_20sl", "BAL", 10, 45, -0.20, 0.001),
    ("AGG_7p_45d_15sl",  "AGG",  7, 45, -0.15, 0.001),
    ("HC_10p_30d_20sl",  "HC",  10, 30, -0.20, 0.001),
]

results = {}
for name, ts, mp, h, sl, slip in CONFIGS:
    print(f"\nRunning {name}...")
    nav_df, _ = simulate(
        sig, prices, vni_dates,
        allowed_tiers=TIER_SETS[ts], max_positions=mp,
        hold_days=h, stop_loss=sl, min_hold=2, slippage=slip,
    )
    nav_df["time"] = pd.to_datetime(nav_df["time"])
    nav_df = nav_df.set_index("time")
    quarterly = nav_df["nav"].resample("QE").last()
    qrets = quarterly.pct_change().dropna() * 100
    qrets.name = name
    results[name] = qrets
    print(f"  Quarterly mean={qrets.mean():.2f}%, std={qrets.std():.2f}%, "
          f"win={(qrets>0).mean()*100:.0f}%")

# Add VNINDEX baseline
print("\nVNINDEX baseline...")
vni_idx = vni.set_index("time")["Close"]
vni_q = vni_idx.resample("QE").last()
vni_qrets = vni_q.pct_change().dropna() * 100
vni_qrets.name = "VNINDEX_BH"
results["VNINDEX_BH"] = vni_qrets

# Quarterly returns table
print("\n" + "═" * 100)
print("  QUARTERLY RETURNS (%) — CHRONOLOGICAL")
print("═" * 100)
qdf = pd.DataFrame(results).round(2)
qdf.index = qdf.index.strftime("%Y-Q%q")
qdf.index = qdf.index.str.replace(r"Q1$", "Q1", regex=True).str.replace(r"^(\d+)-Q", "Y\\1-Q")
# Quick fix: use period
qdf2 = pd.DataFrame(results)
qdf2.index = qdf2.index.to_period("Q").astype(str)
print(qdf2.to_string(float_format=lambda x: f"{x:>+7.2f}"))

# Year-by-year aggregate
print("\n" + "═" * 100)
print("  YEAR-BY-YEAR AGGREGATE")
print("═" * 100)
qdf2["yr"] = pd.PeriodIndex(qdf2.index, freq="Q").year
yr_agg = qdf2.groupby("yr").apply(
    lambda g: ((1 + g.iloc[:, :-1].fillna(0)/100).prod() - 1) * 100
)
print(yr_agg.to_string(float_format=lambda x: f"{x:>+7.2f}"))

# Statistics
print("\n" + "═" * 100)
print("  QUARTERLY STATISTICS")
print("═" * 100)
stats = pd.DataFrame({
    name: {
        "n_qtrs": len(s.dropna()),
        "mean_q": s.mean(),
        "median_q": s.median(),
        "std_q": s.std(),
        "win_rate%": (s > 0).mean() * 100,
        "best_q": s.max(),
        "worst_q": s.min(),
        "P5": s.quantile(0.05),
        "P25": s.quantile(0.25),
        "P75": s.quantile(0.75),
        "P95": s.quantile(0.95),
    }
    for name, s in results.items()
}).T
print(stats.to_string(float_format=lambda x: f"{x:.2f}"))

# Rolling 4-quarter (1-year) Sharpe
print("\n" + "═" * 100)
print("  ROLLING 4-QUARTER (1-YEAR) MEAN RETURN")
print("═" * 100)
roll = pd.DataFrame()
for name, s in results.items():
    roll[name] = s.rolling(4).mean()
print(roll.dropna().to_string(float_format=lambda x: f"{x:>+7.2f}"))

# Worst quarters detail
print("\n" + "═" * 100)
print("  WORST 5 QUARTERS PER STRATEGY")
print("═" * 100)
for name, s in results.items():
    worst = s.nsmallest(5)
    print(f"\n  {name}:")
    for q, r in worst.items():
        print(f"    {q}: {r:+.2f}%")

qdf2.to_csv(os.path.join(WORKDIR, "data/quarterly_returns.csv"))
yr_agg.to_csv(os.path.join(WORKDIR, "data/yearly_returns.csv"))
print("\n  Saved: quarterly_returns.csv, yearly_returns.csv")
