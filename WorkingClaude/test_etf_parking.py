# -*- coding: utf-8 -*-
"""Test: park idle cash into VN30 ETF during selected states.

Hypothesis: BA-system sits 71% in cash on average. If realistic deposit rate
is 0.5-1%, that's massive opportunity cost. Strategy: tactically park idle cash
into VN30 ETF (beta=1) during NEUTRAL/BULL/EX-BULL states, keep cash defensive
in BEAR/CRISIS.

Test variants (deposit rate = 1% baseline for non-ETF cash):
  V0  baseline (current, no ETF parking)
  V1  park 100% of cash in VN30 during NEUTRAL only
  V2  park 100% of cash in VN30 during NEUTRAL + BULL + EX-BULL (i.e., non-BEAR)
  V3  park 50% of cash in VN30 during NEUTRAL + BULL + EX-BULL
  V4  park 100% during NEUTRAL, 50% during BEAR (aggressive)

Friction: 0.05% per side on rebalance (ETF spread + management fee).

Each test runs BAL+Fin/RE-max-4 50B (single book) for 2014-01-01 → 2026-03-30.
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
print("  ETF PARKING — park idle cash into VN30 during benign states")
print(f"  Period: {START_DATE} → {END_DATE} | Deposit rate (non-ETF cash) = 1.0%/yr (realistic)")
print("=" * 100)

print("\nLoading v10 signals…")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

# Load VN30 underlying for ETF returns
print("Loading VN30 underlying…")
vn30_df = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
vn30_df["time"] = pd.to_datetime(vn30_df["time"])
vn30_underlying = dict(zip(vn30_df["time"], vn30_df["Close"]))
print(f"  {len(vn30_underlying):,} VN30 close prices (using VNINDEX as proxy)")

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

DEPOSIT_REALISTIC = 0.01  # 1%/yr realistic VN non-term

variants = [
    ("V0 baseline (1% deposit, no ETF)", None),
    ("V1 ETF 100% in NEUTRAL only",     {3: 1.0}),
    ("V2 ETF 100% in NEU+BULL+EXBULL",  {3: 1.0, 4: 1.0, 5: 1.0}),
    ("V3 ETF 50% in NEU+BULL+EXBULL",   {3: 0.5, 4: 0.5, 5: 0.5}),
    ("V4 ETF 100% NEU + 50% BEAR",      {3: 1.0, 4: 1.0, 5: 1.0, 2: 0.5}),
    ("V5 ETF 30% in NEUTRAL only",      {3: 0.3}),  # conservative
    ("V6 ETF 70% in NEUTRAL only",      {3: 0.7}),  # medium
]

# Also include 3% deposit baseline for comparison
variants_extra = [
    ("V0b baseline (3% deposit ref)", None, 0.03),
]

print(f"\n  Running {len(variants) + len(variants_extra)} variants…")
print(f"  {'Variant':<40} {'CAGR':>8} {'Sharpe':>8} {'DD':>8} {'Calmar':>8} {'Final NAV':>12}")
print(f"  {'-'*40} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*12}")

results = []
nav_traces = {}

for label, etf_states in variants:
    nav_df, _ = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT_REALISTIC,
        state_by_date=state_by_date,
        cash_etf_states=etf_states,
        vn30_underlying=vn30_underlying if etf_states else None,
        **LIQ, name=label)
    m = metrics(nav_df, pd.DataFrame(), label)
    final_nav = nav_df.iloc[-1]["nav"] / 1e9
    results.append({"variant": label, **m, "final_nav_b": final_nav})
    nav_traces[label] = nav_df
    print(f"  {label:<40} {m['cagr_pct']:>+7.2f}% {m['sharpe']:>+8.2f} "
          f"{m['max_dd_pct']:>+7.1f}% {m['calmar']:>+8.2f} {final_nav:>10.2f}B")

# Extra: also run 3% deposit baseline for reference
for label, etf_states, dep in variants_extra:
    nav_df, _ = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=dep,
        state_by_date=state_by_date,
        cash_etf_states=etf_states,
        vn30_underlying=vn30_underlying if etf_states else None,
        **LIQ, name=label)
    m = metrics(nav_df, pd.DataFrame(), label)
    final_nav = nav_df.iloc[-1]["nav"] / 1e9
    results.append({"variant": label, **m, "final_nav_b": final_nav})
    print(f"  {label:<40} {m['cagr_pct']:>+7.2f}% {m['sharpe']:>+8.2f} "
          f"{m['max_dd_pct']:>+7.1f}% {m['calmar']:>+8.2f} {final_nav:>10.2f}B")

df_res = pd.DataFrame(results)

# Δ vs baseline (V0 = 1% deposit, no ETF)
base = df_res[df_res["variant"] == "V0 baseline (1% deposit, no ETF)"].iloc[0]
print(f"\n  Δ vs V0 baseline (1% deposit, no ETF: CAGR={base['cagr_pct']:.2f}%, Sh={base['sharpe']:.2f}):")
for _, r in df_res.iterrows():
    if r["variant"].startswith("V0"):
        continue
    print(f"    {r['variant']:<40} ΔCAGR {r['cagr_pct']-base['cagr_pct']:+.2f}pp, "
          f"ΔSharpe {r['sharpe']-base['sharpe']:+.2f}, ΔDD {r['max_dd_pct']-base['max_dd_pct']:+.1f}pp")

# VN30 B&H reference for full period
print(f"\n  Reference benchmarks (same 50B / same period):")
print(f"    VNINDEX B&H historic CAGR ≈ 11.5%, Sharpe ≈ 0.69, DD -45%")

# Year-by-year for best variant
print(f"\n  Year-by-year NAV multiplier comparison:")
print(f"  {'Year':<8} {'V0 (no ETF)':>15} {'V2 (ETF NEU+BULL)':>20} {'V0b (3% dep)':>15}")
def yearly_mult(nav_df):
    nav_df = nav_df.copy()
    nav_df["time"] = pd.to_datetime(nav_df["time"])
    nav_df["year"] = nav_df["time"].dt.year
    return nav_df.groupby("year")["nav"].last() / 50e9

y_v0 = yearly_mult(nav_traces["V0 baseline (1% deposit, no ETF)"])
y_v2 = yearly_mult(nav_traces["V2 ETF 100% in NEU+BULL+EXBULL"])
# V0b NAV trace not stored — skip
for yr in sorted(set(y_v0.index)):
    a = y_v0.get(yr, np.nan)
    b = y_v2.get(yr, np.nan)
    print(f"  {yr:<8} {a:>14.2f}× {b:>19.2f}×")

# Save
df_res.to_csv(os.path.join(WORKDIR, "etf_parking_results.csv"), index=False)
print(f"\n  Saved: etf_parking_results.csv")
