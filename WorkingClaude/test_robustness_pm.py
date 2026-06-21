"""Test slippage + position management improvements on BALANCED 10p 45d -20% (default).

Tests:
  A) Slippage 0/0.1/0.2/0.3%
  B) Trailing stop (activate at +15%, exit at -8% from peak)
  C) Partial profit-taking (sell 1/3 at +15%, 1/3 at +25%)
  D) Sector limit (max 3 per sector)
  E) Combined: trailing + partial + sector limit
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

# Sector lookup
print("Loading sector map...")
sec_query = """
SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code / 1000) AS INT64) AS sector_top
FROM tav2_bq.ticker AS t
WHERE t.ICB_Code IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
"""
sec_df = bq(sec_query)
sec_map = sec_df.set_index("ticker")["sector_top"].to_dict()

# Default config: BALANCED 10p 45d -20% (OOS-tuned winner)
TIERS = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
BASE_PARAMS = dict(
    allowed_tiers=TIERS,
    max_positions=10,
    hold_days=45,
    stop_loss=-0.20,
    min_hold=2,
)

# Test variants
VARIANTS = [
    # Slippage tests
    ("BASE_slip0",       {"slippage": 0.000}),
    ("BASE_slip0.1",     {"slippage": 0.001}),
    ("BASE_slip0.2",     {"slippage": 0.002}),
    ("BASE_slip0.3",     {"slippage": 0.003}),
    # Position management (with realistic slippage 0.1%)
    ("PM_trail",         {"slippage": 0.001,
                          "trailing_stop_activate": 0.15,
                          "trailing_stop_pct": 0.08}),
    ("PM_trail_tight",   {"slippage": 0.001,
                          "trailing_stop_activate": 0.10,
                          "trailing_stop_pct": 0.06}),
    ("PM_partial",       {"slippage": 0.001,
                          "partial_take_at": [(0.15, 1/3), (0.25, 0.5)]}),
    ("PM_partial_aggro", {"slippage": 0.001,
                          "partial_take_at": [(0.10, 0.25), (0.20, 1/3), (0.30, 0.5)]}),
    ("PM_sector3",       {"slippage": 0.001,
                          "sector_limit": 3,
                          "ticker_sector_map": sec_map}),
    ("PM_sector2",       {"slippage": 0.001,
                          "sector_limit": 2,
                          "ticker_sector_map": sec_map}),
    # Combined
    ("PM_ALL",           {"slippage": 0.001,
                          "trailing_stop_activate": 0.15,
                          "trailing_stop_pct": 0.08,
                          "partial_take_at": [(0.15, 1/3)],
                          "sector_limit": 3,
                          "ticker_sector_map": sec_map}),
]

results = []
for name, extra in VARIANTS:
    print(f"\nRunning {name}...")
    nav_df, trades_df = simulate(sig, prices, vni_dates, **BASE_PARAMS, **extra)
    m = metrics(nav_df, trades_df, name)
    # Reason mix
    reason_mix = trades_df["reason"].value_counts().to_dict() if len(trades_df) else {}
    m["reason_mix"] = reason_mix
    results.append({"name": name, **m})
    n_trades = m["n_trades"]
    print(f"  CAGR={m['cagr_pct']:.2f}% Sh={m['sharpe']:.2f} DD={m['max_dd_pct']:.1f}% "
          f"Cal={m['calmar']:.2f} trades={n_trades} reasons={reason_mix}")

# Summary table
print("\n" + "═" * 110)
print("  ROBUSTNESS + POSITION MANAGEMENT — BALANCED 10p 45d -20%")
print("═" * 110)
df = pd.DataFrame(results)
cols = ["name", "cagr_pct", "sharpe", "sortino", "max_dd_pct", "calmar",
        "n_trades", "win_rate_pct", "avg_trade_ret_pct", "avg_hold_days"]
print(df[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Slippage degradation
print("\n" + "═" * 110)
print("  SLIPPAGE DEGRADATION")
print("═" * 110)
slip_rows = df[df["name"].str.startswith("BASE_slip")][cols]
print(slip_rows.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
base_cagr = df[df["name"] == "BASE_slip0"]["cagr_pct"].iloc[0]
for _, r in slip_rows.iterrows():
    drop = r["cagr_pct"] - base_cagr
    print(f"  {r['name']:18}: ΔCAGR vs no-slip = {drop:+.2f}pp")

# PM improvements vs base (with slip 0.1%)
print("\n" + "═" * 110)
print("  POSITION MANAGEMENT vs BASE (slip 0.1%)")
print("═" * 110)
base_pm = df[df["name"] == "BASE_slip0.1"].iloc[0]
pm_rows = df[df["name"].str.startswith("PM_")][cols]
print(pm_rows.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
print()
for _, r in pm_rows.iterrows():
    print(f"  {r['name']:18}: ΔCAGR={r['cagr_pct']-base_pm['cagr_pct']:+5.2f}pp  "
          f"ΔSharpe={r['sharpe']-base_pm['sharpe']:+.3f}  "
          f"ΔDD={r['max_dd_pct']-base_pm['max_dd_pct']:+5.1f}pp  "
          f"ΔCalmar={r['calmar']-base_pm['calmar']:+.2f}")

df.to_csv(os.path.join(WORKDIR, "data/robustness_pm_results.csv"), index=False)
print("\n  Saved: robustness_pm_results.csv")
