"""Grid search fine-tune for Holistic portfolio simulation.

Tests combinations of (tier_set, max_positions, hold_days, stop_loss)
on full 2014-2026 history, ranks by Sharpe and CAGR.
"""
import os
import sys
import time
from itertools import product

import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

# Import sim engine
from simulate_holistic_nav import (
    simulate, metrics, bq, SIGNAL_QUERY, VNI_QUERY,
    START_DATE, END_DATE, INIT_NAV
)


def main():
    print("Loading data once...")
    sig = bq(SIGNAL_QUERY.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
    vni["time"] = pd.to_datetime(vni["time"])
    vni_dates = sorted(vni["time"].unique())
    prices = {}
    for tk, g in sig.groupby("ticker"):
        prices[tk] = dict(zip(g["time"], g["Close"]))
    print(f"  {len(sig):,} signals, {len(vni_dates):,} days, {len(prices):,} tickers")

    # ─── Grid definition ────────────────────────────────────────────
    tier_sets = {
        "MEGA":         ["MEGA"],
        "HIGH_CONV":    ["MEGA", "MOMENTUM", "MOMENTUM_N"],
        "BALANCED":     ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"],
        "AGGRESSIVE":   ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
                         "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"],
    }
    max_pos_grid    = [3, 5, 7, 10]
    hold_days_grid  = [30, 45, 60, 90]
    stop_loss_grid  = [-0.10, -0.15, -0.20]

    # Filter combinations: MEGA only n_signals < 200, doesn't make sense >5 pos
    combos = []
    for tier_name in tier_sets:
        for mp in max_pos_grid:
            if tier_name == "MEGA" and mp > 5:
                continue
            for h in hold_days_grid:
                for sl in stop_loss_grid:
                    combos.append((tier_name, mp, h, sl))
    print(f"  Running {len(combos)} configurations...\n")

    results = []
    t0 = time.time()
    for idx, (tier_name, mp, h, sl) in enumerate(combos):
        nav_df, trades_df = simulate(
            sig, prices, vni_dates,
            allowed_tiers=tier_sets[tier_name],
            max_positions=mp,
            hold_days=h,
            stop_loss=sl,
            min_hold=2,
            name=f"{tier_name}_{mp}p_{h}d_{int(sl*100)}sl",
        )
        m = metrics(nav_df, trades_df, f"{tier_name}_p{mp}_h{h}_sl{int(sl*100)}")
        m.update({"tier_set": tier_name, "max_pos": mp, "hold_days": h, "stop_loss": sl})
        results.append(m)
        elapsed = time.time() - t0
        eta = elapsed / (idx + 1) * (len(combos) - idx - 1)
        if (idx + 1) % 5 == 0:
            print(f"  [{idx+1}/{len(combos)}] {tier_name:10} mp={mp} h={h} sl={int(sl*100)} → "
                  f"CAGR={m['cagr_pct']:5.1f}%  Sh={m['sharpe']:.2f}  DD={m['max_dd_pct']:5.1f}%  "
                  f"(eta {eta:.0f}s)")

    df = pd.DataFrame(results)
    df = df.sort_values("sharpe", ascending=False)

    # Save full grid
    df.to_csv(os.path.join(WORKDIR, "data/finetune_full_grid.csv"), index=False)

    # Top 15 by Sharpe
    print("\n" + "═" * 110)
    print("  TOP 15 BY SHARPE (risk-adjusted)")
    print("═" * 110)
    cols = ["tier_set", "max_pos", "hold_days", "stop_loss",
            "cagr_pct", "sharpe", "sortino", "max_dd_pct", "calmar",
            "n_trades", "win_rate_pct", "avg_hold_days"]
    print(df.head(15)[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    # Top 15 by CAGR
    print("\n" + "═" * 110)
    print("  TOP 15 BY CAGR")
    print("═" * 110)
    df_cagr = df.sort_values("cagr_pct", ascending=False)
    print(df_cagr.head(15)[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    # Top 15 by Calmar (return per unit DD)
    print("\n" + "═" * 110)
    print("  TOP 15 BY CALMAR (return / max DD)")
    print("═" * 110)
    df_cal = df.sort_values("calmar", ascending=False)
    print(df_cal.head(15)[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    # Best per tier set
    print("\n" + "═" * 110)
    print("  BEST CONFIG PER TIER SET (by Sharpe)")
    print("═" * 110)
    for ts in tier_sets:
        sub = df[df["tier_set"] == ts]
        if not sub.empty:
            best = sub.iloc[0]
            print(f"  {ts:11}: max_pos={int(best['max_pos'])}, "
                  f"hold={int(best['hold_days'])}d, stop={best['stop_loss']:.0%}  →  "
                  f"CAGR={best['cagr_pct']:.1f}%  Sh={best['sharpe']:.2f}  "
                  f"DD={best['max_dd_pct']:.1f}%  Cal={best['calmar']:.2f}  "
                  f"trades={int(best['n_trades'])}")

    print(f"\n  Total runtime: {time.time()-t0:.1f}s")
    print(f"  Full grid saved: finetune_full_grid.csv")


if __name__ == "__main__":
    main()
