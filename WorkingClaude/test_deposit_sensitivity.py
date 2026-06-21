# -*- coding: utf-8 -*-
"""Test deposit rate sensitivity + measure actual deployment per state.

User concern: 3%/yr deposit rate is optimistic; realistic non-term VN rate is 0.5-1%.
Question: how much CAGR drops if deposit drops to 0.5-1%?
And: what's actual average deployment % per state?

Approach:
  1. Run BAL+Fin/RE-max-4 50B (single-book) at deposit rates [0.005, 0.01, 0.015, 0.03]
  2. Track daily deployment + state for full 2014-2026
  3. Compute avg deployment per state
  4. Compute CAGR drop magnitude
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
print("  DEPOSIT RATE SENSITIVITY + DEPLOYMENT ANALYSIS")
print(f"  Period: {START_DATE} → {END_DATE}")
print("=" * 100)

print("\nLoading v10 signals…")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
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

# ─── Test 1: deposit rate sensitivity ─────────────────────────────────────
print("\n" + "=" * 100)
print("  TEST 1 — Deposit rate sensitivity (BAL+Fin/RE-max-4 single book at 50B)")
print("=" * 100)
print()
print(f"  {'Deposit rate':<15} {'CAGR':>8} {'Sharpe':>8} {'DD':>8} {'Calmar':>8} {'Final NAV':>12}")
print(f"  {'-'*15} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*12}")

rate_results = []
nav_traces_by_rate = {}

for rate in [0.0, 0.005, 0.01, 0.015, 0.03, 0.05]:
    nav_df, trades_df = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=rate,
        state_by_date=state_by_date,  # for deployment-per-state analysis
        **LIQ, name=f"rate_{rate}")
    m = metrics(nav_df, trades_df, f"rate_{rate}")
    final_nav = nav_df.iloc[-1]["nav"] / 1e9
    rate_results.append({"rate": rate, **m, "final_nav_b": final_nav})
    nav_traces_by_rate[rate] = nav_df
    print(f"  {rate*100:>5.2f}%/yr      {m['cagr_pct']:>+7.2f}% {m['sharpe']:>+8.2f} "
          f"{m['max_dd_pct']:>+7.1f}% {m['calmar']:>+8.2f} {final_nav:>10.2f}B")

# Compare 3% baseline vs 0.5% realistic
df_rate = pd.DataFrame(rate_results)
base_3 = df_rate[df_rate["rate"] == 0.03].iloc[0]
print(f"\n  Δ vs 3% baseline:")
for _, r in df_rate.iterrows():
    if r["rate"] == 0.03:
        continue
    print(f"    {r['rate']*100:>5.2f}% → ΔCAGR {r['cagr_pct']-base_3['cagr_pct']:+.2f}pp, "
          f"ΔSharpe {r['sharpe']-base_3['sharpe']:+.2f}")

# ─── Test 2: Average deployment per state ──────────────────────────────────
print("\n" + "=" * 100)
print("  TEST 2 — Average deployment % per state (from 3% rate sim)")
print("=" * 100)
nav_baseline = nav_traces_by_rate[0.03].copy()
nav_baseline["time"] = pd.to_datetime(nav_baseline["time"])

# Aggregate deployment per state
state_names = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

print(f"\n  {'State':<10} {'Sessions':>10} {'% time':>8} {'Avg deployed':>15} "
      f"{'Avg cash':>12} {'Max deployed':>15}")
print(f"  {'-'*10} {'-'*10} {'-'*8} {'-'*15} {'-'*12} {'-'*15}")

n_total = len(nav_baseline)
state_stats = []
for s_int, s_name in state_names.items():
    sub = nav_baseline[nav_baseline["state"] == s_int]
    if len(sub) == 0:
        continue
    pct_time = len(sub) / n_total * 100
    avg_dep = sub["deployed_pct"].mean()
    avg_cash = sub["cash_pct"].mean()
    max_dep = sub["deployed_pct"].max()
    state_stats.append({"state": s_int, "state_name": s_name,
                         "n_sessions": len(sub), "pct_time": pct_time,
                         "avg_deployed_pct": avg_dep, "avg_cash_pct": avg_cash,
                         "max_deployed_pct": max_dep})
    print(f"  {s_name:<10} {len(sub):>10d} {pct_time:>7.1f}% {avg_dep:>13.1f}% "
          f"{avg_cash:>11.1f}% {max_dep:>13.1f}%")

# Overall
all_dep = nav_baseline["deployed_pct"].mean()
all_cash = nav_baseline["cash_pct"].mean()
print(f"\n  {'OVERALL':<10} {n_total:>10d} {100.0:>7.1f}% {all_dep:>13.1f}% "
      f"{all_cash:>11.1f}%")

# ─── Test 3: deployment evolution by year ──────────────────────────────────
print("\n" + "=" * 100)
print("  TEST 3 — Annual deployment evolution")
print("=" * 100)
nav_baseline["year"] = nav_baseline["time"].dt.year
yearly = nav_baseline.groupby("year").agg(
    sessions=("nav", "count"),
    avg_deployed_pct=("deployed_pct", "mean"),
    avg_cash_pct=("cash_pct", "mean"),
    dominant_state=("state", lambda x: state_names.get(int(x.mode().iloc[0]), "?") if x.notna().any() else "?"),
).round(1)
print()
print(yearly.to_string())

# ─── Test 4: lost CAGR from idle cash ──────────────────────────────────────
print("\n" + "=" * 100)
print("  TEST 4 — Theoretical max CAGR if cash earned VN30 B&H return instead")
print("=" * 100)

# Compare: what if we ALWAYS held VN30 B&H?
# VNINDEX B&H over 2014-2026 = ~11.5% CAGR per memory
# BA-system 50B = 17.97% / 1.12 / DD -20.4%
# If cash earned VN30 return (~11.5%) instead of 3% during deployment-light periods…

# Rough calc: if avg deployment 60% × system_alpha + 40% × cash_return = total CAGR
# Current: 60% × ?? + 40% × 3% = 17.97 → system_alpha ≈ 23.6%/yr on deployed capital
# Alt cash=VN30: 60% × 23.6% + 40% × 11.5% = 18.76% (small gain)
# Alt cash=1%: 60% × 23.6% + 40% × 1% = 14.56% (significant drop)
# Alt cash=0%: 60% × 23.6% + 40% × 0% = 14.16%

# Actually compute from real deployment data
avg_dep_decimal = all_dep / 100
# Effective deployment-weighted CAGR contribution
# Solve: 0.03 * (1 - avg_dep_decimal) + alpha * avg_dep_decimal = 17.97/100
implied_alpha = (base_3["cagr_pct"]/100 - 0.03 * (1 - avg_dep_decimal)) / avg_dep_decimal
print(f"\n  Avg deployment: {avg_dep_decimal*100:.1f}%")
print(f"  Implied gross alpha on deployed capital: {implied_alpha*100:.1f}%/yr")
print(f"  (Estimated under linear blend assumption)")

print()
print(f"  Counterfactual scenarios — what CAGR would be at deposit rate X?")
print(f"  {'Cash yield':<15} {'Est. CAGR':>10}")
for cash_y in [0.0, 0.005, 0.01, 0.03, 0.05, 0.08, 0.115]:
    est = cash_y * (1 - avg_dep_decimal) + implied_alpha * avg_dep_decimal
    if cash_y == 0.115:
        label = "VN30 B&H (~11.5%)"
    else:
        label = f"{cash_y*100:.1f}%/yr"
    print(f"  {label:<15} {est*100:>+9.2f}%")

# ─── Save ──────────────────────────────────────────────────────────────────
df_rate.to_csv(os.path.join(WORKDIR, "data/deposit_sensitivity.csv"), index=False)
pd.DataFrame(state_stats).to_csv(os.path.join(WORKDIR, "data/deployment_per_state.csv"), index=False)
yearly.to_csv(os.path.join(WORKDIR, "data/deployment_yearly.csv"))
nav_baseline.to_csv(os.path.join(WORKDIR, "data/nav_with_deployment.csv"), index=False)

print(f"\n  Saved:")
print(f"    deposit_sensitivity.csv")
print(f"    deployment_per_state.csv")
print(f"    deployment_yearly.csv")
print(f"    nav_with_deployment.csv (full daily trace)")
