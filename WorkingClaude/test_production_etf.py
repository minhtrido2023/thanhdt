# -*- coding: utf-8 -*-
"""Final production test: BA-system 50/50 (BAL_Fin4 + VN30_BAL) WITH V6 ETF parking.

Compare:
  P0  Current production (50/50 BAL+VN30, no ETF, 3% deposit assumption)
  P1  Production at 1% deposit (realistic, no ETF) — shows degradation
  P2  Production at 1% deposit + V6 ETF 70% NEUTRAL — proposed new config

Each book runs at 25B (= 50B wallet × 50% split).
Combined NAV = NAV_BAL + NAV_VN30.
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
TOTAL_NAV = 50e9
BOOK_NAV = 25e9

print("=" * 100)
print("  PRODUCTION TEST — V6 ETF parking IN 50/50 BAL+VN30 SETUP")
print(f"  Period: {START_DATE} → {END_DATE}, Total NAV {TOTAL_NAV/1e9:.0f}B (25B/book)")
print("=" * 100)

print("\nLoading data…")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

vn30_df = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
vn30_df["time"] = pd.to_datetime(vn30_df["time"])
vn30_underlying = dict(zip(vn30_df["time"], vn30_df["Close"]))

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

sig_vn30 = sig[sig["ticker"].isin(top30)].copy()
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}


def run_combo(deposit_rate, etf_states, label):
    """Run both books at BOOK_NAV each, combine. Return combined NAV trace + metrics."""
    nav_bal, _ = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=deposit_rate, state_by_date=state_by_date,
        cash_etf_states=etf_states,
        vn30_underlying=vn30_underlying if etf_states else None,
        **LIQ_FULL, name=f"{label}_BAL")
    nav_vn30, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        deposit_annual=deposit_rate, state_by_date=state_by_date,
        cash_etf_states=etf_states,
        vn30_underlying=vn30_underlying if etf_states else None,
        **LIQ_VN30, name=f"{label}_VN30")

    nav_bal["time"] = pd.to_datetime(nav_bal["time"])
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
    nav_bal_s = nav_bal.set_index("time")["nav"]
    nav_vn30_s = nav_vn30.set_index("time")["nav"]
    common = nav_bal_s.index.intersection(nav_vn30_s.index)
    nav_total = nav_bal_s.loc[common] + nav_vn30_s.loc[common]
    nav_total_df = nav_total.reset_index()
    nav_total_df.columns = ["time", "nav"]

    m = metrics(nav_total_df, pd.DataFrame(), label)
    # Approximate AvgDep using BAL's deployed_pct (simplified)
    avg_dep_bal = nav_bal["deployed_pct"].mean()
    avg_dep_vn30 = nav_vn30["deployed_pct"].mean()
    avg_etf_bal = nav_bal["cash_etf_pct"].mean() if "cash_etf_pct" in nav_bal.columns else 0
    avg_etf_vn30 = nav_vn30["cash_etf_pct"].mean() if "cash_etf_pct" in nav_vn30.columns else 0
    return {"label": label, **m,
            "avg_dep_bal": avg_dep_bal, "avg_dep_vn30": avg_dep_vn30,
            "avg_etf_bal": avg_etf_bal, "avg_etf_vn30": avg_etf_vn30,
            "final_nav_b": nav_total.iloc[-1] / 1e9}, nav_total


print("\nRunning 3 production variants…\n")

p0, n0 = run_combo(0.03, None, "P0 production (3% dep, no ETF) [original assumption]")
p1, n1 = run_combo(0.01, None, "P1 production (1% dep, no ETF) [realistic, current]")
p2, n2 = run_combo(0.01, {3: 0.7}, "P2 production (1% dep + V6 ETF 70% NEU) [PROPOSED]")

for r in [p0, p1, p2]:
    print(f"  {r['label']:<60}")
    print(f"     CAGR {r['cagr_pct']:+.2f}%  Sh {r['sharpe']:.2f}  DD {r['max_dd_pct']:+.1f}%  "
          f"Calmar {r['calmar']:.2f}  NAV cuối {r['final_nav_b']:.2f}B")
    print(f"     AvgDep BAL {r['avg_dep_bal']:.1f}%  VN30 {r['avg_dep_vn30']:.1f}%  "
          f"AvgETF BAL {r['avg_etf_bal']:.1f}%  VN30 {r['avg_etf_vn30']:.1f}%")
    print()

print("\n  Δ vs P0 (original 3% deposit assumption):")
for r in [p1, p2]:
    print(f"    {r['label']:<60}")
    print(f"      ΔCAGR {r['cagr_pct']-p0['cagr_pct']:+.2f}pp, "
          f"ΔSharpe {r['sharpe']-p0['sharpe']:+.2f}, "
          f"ΔDD {r['max_dd_pct']-p0['max_dd_pct']:+.1f}pp")

print("\n  Δ P2 vs P1 (ETF improvement at realistic deposit):")
print(f"    ΔCAGR {p2['cagr_pct']-p1['cagr_pct']:+.2f}pp, "
      f"ΔSharpe {p2['sharpe']-p1['sharpe']:+.2f}, "
      f"ΔDD {p2['max_dd_pct']-p1['max_dd_pct']:+.1f}pp")

# Yearly comparison
print(f"\n{'=' * 100}")
print(f"  YEARLY NAV MULTIPLIER (start 50B)")
print(f"{'=' * 100}")
def yearly_mult(nav_series):
    df = nav_series.reset_index()
    df.columns = ["time", "nav"]
    df["year"] = pd.to_datetime(df["time"]).dt.year
    return (df.groupby("year")["nav"].last() / TOTAL_NAV).round(2)

y0 = yearly_mult(n0)
y1 = yearly_mult(n1)
y2 = yearly_mult(n2)
print(f"\n  {'Year':<6} {'P0 (3% dep)':>15} {'P1 (1% dep)':>15} {'P2 (1% dep + ETF)':>20}")
for yr in sorted(set(y0.index) | set(y1.index) | set(y2.index)):
    a = y0.get(yr, np.nan)
    b = y1.get(yr, np.nan)
    c = y2.get(yr, np.nan)
    print(f"  {yr:<6} {a:>14.2f}× {b:>14.2f}× {c:>19.2f}×")

# Save
out_df = pd.DataFrame([p0, p1, p2])
out_df.to_csv(os.path.join(WORKDIR, "production_etf_results.csv"), index=False)
print(f"\n  Saved: production_etf_results.csv")

# Also save NAV traces
nav_traces = pd.DataFrame({
    "time": n0.index,
    "P0_nav_b": n0.values / 1e9,
    "P1_nav_b": n1.values / 1e9,
    "P2_nav_b": n2.values / 1e9,
})
nav_traces.to_csv(os.path.join(WORKDIR, "production_etf_nav_traces.csv"), index=False)
print(f"  NAV traces: production_etf_nav_traces.csv")
