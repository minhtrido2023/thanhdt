#!/usr/bin/env python3
"""
compare_ba_canonical_v4_vs_v5.py
================================
Validate FA-system v5 (H3+H4) on BA canonical production config:
  - SIGNAL_V10 (v10 scoring: +10 Fin/RE-D bonus, -10 Fin/RE-A penalty)
  - max_pos=10, hold=45d, stop=-0.20, min_hold=2, slippage=0.001
  - sector_limit_per_sector={8: 4}  (Fin/RE max 4 positions)
  - liquidity_volume_pct=0.20, max_fill_days=5, exit_slippage_tiered=True
  - init_nav=50B VND
  - 50/50 BAL+Fin/RE-max-4 + VN30_BAL combined

Runs full-period (2014-2026) + slices OOS window (2024-2026) for both
v4 and v5 FA tables.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY, START_DATE, END_DATE
from test_round14_stability import SIGNAL_V10

# Canonical BA-system params (from quarterly_walkforward.py)
TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
OOS_START = pd.Timestamp("2024-01-01")

def run_canonical(label, sig_query):
    print(f"\n{'='*70}\n  RUN: {label}\n{'='*70}")
    print("Loading signals + prices ...")
    sig = bq(sig_query.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"  {len(sig):,} signal rows")

    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

    vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
    vni["time"] = pd.to_datetime(vni["time"])
    vni_dates = sorted(vni["time"].unique())

    # Sector map (ICB top digit)
    sec_map = bq("""SELECT DISTINCT t.ticker,
                    CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                    FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
                    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                    """).set_index("ticker")["s"].to_dict()

    # Top30 by liquidity (VN30 proxy)
    top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
                    WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
                    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                    GROUP BY t.ticker
                    ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    print("\n  Simulating BAL+Fin/RE-max-4 (50B) ...")
    nav_bal, trades_bal = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    print("  Simulating VN30_BAL (50B) ...")
    sig_vn30 = sig[sig["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    # 50/50 combined NAV
    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    ba_nav.name = "ba_nav"

    return ba_nav, vni, trades_bal, trades_vn30

def window_metrics(nav, start, end, label):
    sub = nav[(nav.index >= start) & (nav.index <= end)]
    if len(sub) < 30:
        return {"label": label, "n": len(sub), "cagr_pct": np.nan,
                "sharpe": np.nan, "max_dd_pct": np.nan, "calmar": np.nan, "wealth_x": np.nan}
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (sub - sub.cummax()) / sub.cummax()
    mdd = dd.min()
    cal = cagr / abs(mdd) if mdd < 0 else 0
    return {"label": label, "n": len(sub),
            "cagr_pct": cagr*100, "sharpe": sharpe,
            "max_dd_pct": mdd*100, "calmar": cal,
            "wealth_x": sub.iloc[-1] / sub.iloc[0]}

def vni_metrics_window(vni, start, end, label):
    sub = vni[(vni["time"] >= start) & (vni["time"] <= end)].copy()
    if len(sub) < 30: return None
    sub["nav"] = sub["Close"] / sub["Close"].iloc[0]
    nav = sub.set_index("time")["nav"]
    return window_metrics(nav, start, end, label)

# Build v5 SIGNAL_V10
V4_QUERY = SIGNAL_V10
V5_QUERY = SIGNAL_V10.replace("tav2_bq.fa_ratings", "tav2_bq.fa_ratings_v5")

# Run both
print(f"Window: {START_DATE} → {END_DATE}")
ba_v4, vni, trades_v4_bal, trades_v4_vn30 = run_canonical("v4_baseline", V4_QUERY)
ba_v5, _,   trades_v5_bal, trades_v5_vn30 = run_canonical("v5_H3H4",    V5_QUERY)

# Periods to evaluate
periods = [
    ("FULL_PERIOD (2014–2026)", ba_v4.index.min(), ba_v4.index.max()),
    ("OOS_2024_2026",            OOS_START,         ba_v4.index.max()),
    ("OOS_2022_2026 (4y)",       pd.Timestamp("2022-01-01"), ba_v4.index.max()),
]

print("\n" + "═"*100)
print("  BA-SYSTEM CANONICAL (50B, max=10, hold=45d, stop=-20%, slip=0.1%, sec_lim 8:4, liq caps)")
print("═"*100)
hdr = f"{'Period':<26}{'Variant':<14}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}"
print(hdr); print("-"*len(hdr))

rows = []
for label, st, en in periods:
    m4 = window_metrics(ba_v4, st, en, f"{label}_v4")
    m5 = window_metrics(ba_v5, st, en, f"{label}_v5")
    vm = vni_metrics_window(vni, st, en, f"{label}_VNI")
    print(f"{label:<26}{'v4_baseline':<14}{m4['cagr_pct']:>8.2f}{m4['sharpe']:>8.2f}"
          f"{m4['max_dd_pct']:>9.1f}{m4['calmar']:>8.2f}{m4['wealth_x']:>8.2f}")
    print(f"{label:<26}{'v5_H3H4':<14}{m5['cagr_pct']:>8.2f}{m5['sharpe']:>8.2f}"
          f"{m5['max_dd_pct']:>9.1f}{m5['calmar']:>8.2f}{m5['wealth_x']:>8.2f}")
    print(f"{label:<26}{'Δ (v5−v4)':<14}"
          f"{m5['cagr_pct']-m4['cagr_pct']:>+8.2f}"
          f"{m5['sharpe']-m4['sharpe']:>+8.2f}"
          f"{m5['max_dd_pct']-m4['max_dd_pct']:>+9.1f}"
          f"{m5['calmar']-m4['calmar']:>+8.2f}"
          f"{m5['wealth_x']-m4['wealth_x']:>+8.2f}")
    if vm:
        print(f"{label:<26}{'VNINDEX_BH':<14}{vm['cagr_pct']:>8.2f}{vm['sharpe']:>8.2f}"
              f"{vm['max_dd_pct']:>9.1f}{vm['calmar']:>8.2f}{vm['wealth_x']:>8.2f}")
    print()
    rows.append({"period": label, "v4_cagr": m4["cagr_pct"], "v5_cagr": m5["cagr_pct"],
                 "v4_sharpe": m4["sharpe"], "v5_sharpe": m5["sharpe"],
                 "v4_mdd": m4["max_dd_pct"], "v5_mdd": m5["max_dd_pct"],
                 "v4_calmar": m4["calmar"], "v5_calmar": m5["calmar"],
                 "v4_wealth": m4["wealth_x"], "v5_wealth": m5["wealth_x"]})

pd.DataFrame(rows).to_csv("ba_canonical_v4_v5_compare.csv", index=False)
print("Saved ba_canonical_v4_v5_compare.csv")

# Trade counts
print("\n  Trade counts (BAL leg + VN30 leg):")
print(f"    v4: BAL={len(trades_v4_bal):4d}  VN30={len(trades_v4_vn30):4d}  total={len(trades_v4_bal)+len(trades_v4_vn30)}")
print(f"    v5: BAL={len(trades_v5_bal):4d}  VN30={len(trades_v5_vn30):4d}  total={len(trades_v5_bal)+len(trades_v5_vn30)}")
