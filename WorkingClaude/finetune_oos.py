"""Grid search optimized for OOS period (2020-2026) — newer market dynamics.

Tests same grid as full-history but on post-2020 only.
Compare top OOS configs vs full-history winners.
"""
import os
import sys
import time
from itertools import product

import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import (
    simulate, metrics, bq, SIGNAL_QUERY, VNI_QUERY, INIT_NAV
)

# OOS period only
OOS_START = "2020-01-01"
OOS_END   = "2026-01-16"

print("Loading OOS data (2020-2026)...")
sig = bq(SIGNAL_QUERY.format(start=OOS_START, end=OOS_END))
sig["time"] = pd.to_datetime(sig["time"])
vni = bq(VNI_QUERY.format(start=OOS_START, end=OOS_END))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
print(f"  {len(sig):,} signals, {len(vni_dates):,} days")

TIER_SETS = {
    "MEGA":         ["MEGA"],
    "HIGH_CONV":    ["MEGA", "MOMENTUM", "MOMENTUM_N"],
    "BALANCED":     ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"],
    "AGGRESSIVE":   ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
                     "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"],
}

# Same grid as full-history finetune
max_pos_grid    = [3, 5, 7, 10]
hold_days_grid  = [30, 45, 60, 90]
stop_loss_grid  = [-0.10, -0.15, -0.20]

combos = []
for tier_name in TIER_SETS:
    for mp in max_pos_grid:
        if tier_name == "MEGA" and mp > 5:
            continue
        for h in hold_days_grid:
            for sl in stop_loss_grid:
                combos.append((tier_name, mp, h, sl))
print(f"  Running {len(combos)} configurations on OOS period...\n")

results = []
t0 = time.time()
for idx, (tier_name, mp, h, sl) in enumerate(combos):
    nav_df, trades_df = simulate(
        sig, prices, vni_dates,
        allowed_tiers=TIER_SETS[tier_name],
        max_positions=mp, hold_days=h, stop_loss=sl, min_hold=2,
    )
    m = metrics(nav_df, trades_df, f"{tier_name}_p{mp}_h{h}_sl{int(sl*100)}")
    m.update({"tier_set": tier_name, "max_pos": mp, "hold_days": h, "stop_loss": sl})
    results.append(m)
    if (idx + 1) % 10 == 0:
        eta = (time.time() - t0) / (idx + 1) * (len(combos) - idx - 1)
        print(f"  [{idx+1}/{len(combos)}] eta={eta:.0f}s")

df = pd.DataFrame(results).sort_values("sharpe", ascending=False)
df.to_csv(os.path.join(WORKDIR, "data/finetune_oos_grid.csv"), index=False)

print("\n" + "═" * 110)
print("  OOS (2020-2026) — TOP 15 BY SHARPE")
print("═" * 110)
cols = ["tier_set", "max_pos", "hold_days", "stop_loss",
        "cagr_pct", "sharpe", "sortino", "max_dd_pct", "calmar",
        "n_trades", "win_rate_pct", "avg_hold_days"]
print(df.head(15)[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

print("\n" + "═" * 110)
print("  OOS — TOP 15 BY CAGR")
print("═" * 110)
df_cagr = df.sort_values("cagr_pct", ascending=False)
print(df_cagr.head(15)[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

print("\n" + "═" * 110)
print("  OOS — TOP 15 BY CALMAR (return / max DD)")
print("═" * 110)
df_cal = df.sort_values("calmar", ascending=False)
print(df_cal.head(15)[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Best per tier set
print("\n" + "═" * 110)
print("  OOS BEST CONFIG PER TIER SET (by Sharpe)")
print("═" * 110)
for ts in TIER_SETS:
    sub = df[df["tier_set"] == ts]
    if not sub.empty:
        best = sub.iloc[0]
        print(f"  {ts:11}: max_pos={int(best['max_pos'])}, "
              f"hold={int(best['hold_days'])}d, stop={best['stop_loss']:.0%}  →  "
              f"CAGR={best['cagr_pct']:.1f}%  Sh={best['sharpe']:.2f}  "
              f"DD={best['max_dd_pct']:.1f}%  Cal={best['calmar']:.2f}")

print(f"\n  Runtime: {time.time()-t0:.1f}s")
