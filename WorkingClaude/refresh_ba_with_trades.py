#!/usr/bin/env python3
"""Same as refresh_ba_nav.py but also saves trades log for Q1 2026 investigation."""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

import simulate_holistic_nav as shn
shn.END_DATE = "2026-05-13"

from simulate_holistic_nav import simulate, bq, VNI_QUERY, START_DATE
from test_round14_stability import SIGNAL_V10

END_DATE = shn.END_DATE
TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]

print(f"Window: {START_DATE} → {END_DATE}", flush=True)
print("Loading signals + prices ...", flush=True)
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows", flush=True)

prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
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

print("Simulating BAL+Fin/RE-max-4 (50B) ...", flush=True)
nav_bal, trades_bal = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
nav_bal["time"] = pd.to_datetime(nav_bal["time"])

print("Simulating VN30_BAL (50B) ...", flush=True)
sig_vn30 = sig[sig["ticker"].isin(top30)]
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

# Save trades + individual NAVs
trades_bal.to_csv("data/ba_trades_bal_refresh.csv", index=False)
trades_vn30.to_csv("data/ba_trades_vn30_refresh.csv", index=False)
nav_bal.to_csv("data/ba_nav_bal_refresh.csv", index=False)
nav_vn30.to_csv("data/ba_nav_vn30_refresh.csv", index=False)
print(f"Saved: ba_trades_bal_refresh.csv ({len(trades_bal)} trades), ba_trades_vn30_refresh.csv ({len(trades_vn30)} trades)", flush=True)
print(f"       ba_nav_bal_refresh.csv ({len(nav_bal)} days), ba_nav_vn30_refresh.csv ({len(nav_vn30)} days)", flush=True)
print("DONE", flush=True)
