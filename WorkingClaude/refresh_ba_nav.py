#!/usr/bin/env python3
"""
refresh_ba_nav.py
=================
Rerun BA canonical simulation through latest data (2026-05) and save NAV trace
for QWF refresh. Same config as compare_ba_canonical_v4_vs_v5.py (v4 production).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

# Override END_DATE before importing
import simulate_holistic_nav as shn
shn.END_DATE = "2026-05-13"

from simulate_holistic_nav import simulate, bq, VNI_QUERY, START_DATE
from test_round14_stability import SIGNAL_V10

END_DATE = shn.END_DATE
TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]

print(f"Window: {START_DATE} → {END_DATE}")
print("Loading signals + prices ...")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows, dates {sig['time'].min().date()} → {sig['time'].max().date()}")

prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

sec_map = bq("""SELECT DISTINCT t.ticker,
                CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                """).set_index("ticker")["s"].to_dict()

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
                WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                GROUP BY t.ticker
                ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

print("\nSimulating BAL+Fin/RE-max-4 (50B) ...")
nav_bal, trades_bal = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
nav_bal["time"] = pd.to_datetime(nav_bal["time"])

print("Simulating VN30_BAL (50B) ...")
sig_vn30 = sig[sig["ticker"].isin(top30)]
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

# 50/50 combined NAV
nav_bal_s = nav_bal.set_index("time")["nav"] / 50e9
nav_vn30_s = nav_vn30.set_index("time")["nav"] / 50e9
common = nav_bal_s.index.intersection(nav_vn30_s.index)
ba_nav = 0.5 * nav_bal_s.loc[common] + 0.5 * nav_vn30_s.loc[common]
ba_nav.name = "BA_50_50"

# Save
out = pd.DataFrame({"time": ba_nav.index, "BA_50_50": ba_nav.values})
out.to_csv("data/ba_nav_refresh_2026-05.csv", index=False)
print(f"\nSaved ba_nav_refresh_2026-05.csv: {len(out)} rows, {out.time.min().date()} → {out.time.max().date()}")
print(f"Final wealth: {ba_nav.iloc[-1]:.3f}x")

# Quick summary
yrs = (ba_nav.index[-1] - ba_nav.index[0]).days / 365.25
cagr = (ba_nav.iloc[-1] / ba_nav.iloc[0]) ** (1/yrs) - 1
rets = ba_nav.pct_change().dropna()
spy = len(rets) / yrs
sharpe = rets.mean()/rets.std() * np.sqrt(spy)
dd = (ba_nav - ba_nav.cummax()) / ba_nav.cummax()
print(f"BA refreshed: CAGR={cagr:.2%}, Sharpe={sharpe:.2f}, MaxDD={dd.min():.2%}")
