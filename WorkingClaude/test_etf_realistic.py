# -*- coding: utf-8 -*-
"""V6 ETF parking — REALISTIC E1VFVN30 model comparison.

Earlier sim used VNINDEX as proxy with only 0.05% rebalance friction.
This test compares against realistic E1VFVN30 ETF reality:
  - Management fee: 0.65%/year (Dragon Capital VFM standard)
  - Tracking error: -0.3%/year (typical for VN30 ETFs)
  - Bid-ask spread + commission: 0.15%/side on rebalance
  - Still uses VNINDEX as price proxy (VN30 returns ~similar long-term)

Variants:
  P_OPTIMISTIC: V6 70% ETF + minimal friction (current code default)
  P_REALISTIC:  V6 70% ETF + 0.65% mgmt fee + 0.3% tracking + 0.15% friction
  P_CONSERVATIVE: V6 70% ETF + 0.85% mgmt fee + 0.5% tracking + 0.2% friction
  P_NO_ETF:     baseline no ETF (1% deposit, realistic)

Each at NAV 50B, 50/50 BAL+VN30 production split.
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
END_DATE   = "2026-03-30"
TOTAL_NAV  = 50e9
BOOK_NAV   = 25e9

print("=" * 100)
print("  V6 ETF PARKING — REALISTIC E1VFVN30 MODEL")
print(f"  Period: {START_DATE} → {END_DATE} | 50/50 BAL+VN30 at 50B")
print("=" * 100)

print("\n[1/3] Loading data…")
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


def run_combo(label, deposit_rate, etf_states, etf_kwargs):
    """Run 50/50 combo. Returns NAV trace + metrics."""
    nav_bal, _ = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=deposit_rate, state_by_date=state_by_date,
        cash_etf_states=etf_states,
        vn30_underlying=vn30_underlying if etf_states else None,
        **etf_kwargs, **LIQ_FULL, name=f"{label}_BAL")
    nav_vn30, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        deposit_annual=deposit_rate, state_by_date=state_by_date,
        cash_etf_states=etf_states,
        vn30_underlying=vn30_underlying if etf_states else None,
        **etf_kwargs, **LIQ_VN30, name=f"{label}_VN30")

    nav_bal["time"] = pd.to_datetime(nav_bal["time"])
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
    nav_bal_s = nav_bal.set_index("time")["nav"]
    nav_vn30_s = nav_vn30.set_index("time")["nav"]
    common = nav_bal_s.index.intersection(nav_vn30_s.index)
    nav_total = nav_bal_s.loc[common] + nav_vn30_s.loc[common]
    df_nav = pd.DataFrame({"time": common, "nav": nav_total.values})

    m = metrics(df_nav, pd.DataFrame(), label)
    final = nav_total.iloc[-1]
    return {"label": label, **m, "final_nav_b": final / 1e9}


print("\n[2/3] Running 4 variants…\n")
print(f"  {'Variant':<55} {'CAGR':>8} {'Sharpe':>7} {'DD':>8} {'Calmar':>7} {'Final':>9}")
print(f"  {'-'*55} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*9}")

results = []

# Variant 1: NO ETF baseline (realistic 1% deposit, no parking)
r = run_combo("P_NO_ETF baseline (1% dep, no ETF)", 0.01, None, {})
results.append(r)

# Variant 2: V6 ETF OPTIMISTIC (current code: 0.05% friction, no fees)
r = run_combo("V6 OPTIMISTIC (0.05% rebal, no fees)", 0.01, {3: 0.7},
               {"etf_rebalance_friction": 0.0005})
results.append(r)

# Variant 3: V6 ETF REALISTIC (E1VFVN30: 0.65% mgmt + 0.3% tracking + 0.15% friction)
r = run_combo("V6 REALISTIC (0.65% mgmt + 0.3% TE + 0.15% fric)",
               0.01, {3: 0.7},
               {"etf_mgmt_fee_annual": 0.0065, "etf_tracking_drag_annual": 0.003,
                "etf_rebalance_friction": 0.0015})
results.append(r)

# Variant 4: V6 ETF CONSERVATIVE (worst case)
r = run_combo("V6 CONSERVATIVE (0.85% mgmt + 0.5% TE + 0.20% fric)",
               0.01, {3: 0.7},
               {"etf_mgmt_fee_annual": 0.0085, "etf_tracking_drag_annual": 0.005,
                "etf_rebalance_friction": 0.0020})
results.append(r)

for r in results:
    print(f"  {r['label']:<55} {r['cagr_pct']:>+7.2f}% {r['sharpe']:>+7.2f} "
          f"{r['max_dd_pct']:>+7.1f}% {r['calmar']:>+7.2f} {r['final_nav_b']:>7.2f}B")

# Δ table
print(f"\n[3/3] Δ vs P_NO_ETF baseline (CAGR={results[0]['cagr_pct']:.2f}%, "
      f"Sh={results[0]['sharpe']:.2f})")
base = results[0]
for r in results[1:]:
    print(f"  {r['label']:<55}")
    print(f"    ΔCAGR {r['cagr_pct']-base['cagr_pct']:+.2f}pp, "
          f"ΔSharpe {r['sharpe']-base['sharpe']:+.2f}, "
          f"ΔDD {r['max_dd_pct']-base['max_dd_pct']:+.1f}pp, "
          f"Final {r['final_nav_b']-base['final_nav_b']:+.2f}B vs {base['final_nav_b']:.2f}B")

# Save
df_out = pd.DataFrame(results)
df_out.to_csv(os.path.join(WORKDIR, "etf_realistic_comparison.csv"), index=False)
print(f"\n  Saved: etf_realistic_comparison.csv")

print()
print("═" * 100)
print("  NOTE ON ETF MODEL ASSUMPTIONS")
print("═" * 100)
print("""
  E1VFVN30 (Dragon Capital VFM VN30 ETF) — recommended for V6:
    Ticker:     E1VFVN30 trên HOSE
    AUM:        ~15,000 tỷ VND (lớn nhất VN ETF market)
    Mgmt fee:   0.65%/năm (deducted from NAV daily)
    Tracking:   ~0.2-0.4% deviation from VN30 index (~0.3% drag avg)
    Spread:     0.05-0.15% mỗi side
    T+:         T+2 (cùng cổ phiếu thường)
    Liquidity:  50-100B VND/day average
    Foreign:    không limit room
    Lot size:   10 chứng chỉ
    Distribution: reinvest (no cash dividends)

  Underlying note: simulation uses VNINDEX as proxy for VN30. Long-term returns
  similar (~11.5%/yr historic), short-term differ (VN30 = top 30 large-caps,
  VNINDEX = all HOSE).
""")
