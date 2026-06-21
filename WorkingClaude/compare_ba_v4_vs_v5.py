#!/usr/bin/env python3
"""
compare_ba_v4_vs_v5.py
======================
Validate H3+H4 FA-system upgrade impact on BA-system.

Imports simulate_holistic_nav as a module, monkey-patches SIGNAL_QUERY
to read from fa_ratings_v5 (vs fa_ratings v4), runs same strategies,
and compares CAGR / Sharpe / DD / Calmar / WinRate side-by-side.

Output: stdout comparison table + ba_v4_v5_compare.csv
"""
import warnings; warnings.filterwarnings("ignore")
import sys, os
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import importlib, pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

import simulate_holistic_nav as sim

ORIG_QUERY = sim.SIGNAL_QUERY
V5_QUERY   = ORIG_QUERY.replace("tav2_bq.fa_ratings", "tav2_bq.fa_ratings_v5")

START_DATE = sim.START_DATE
END_DATE   = sim.END_DATE
print(f"Window: {START_DATE} → {END_DATE}")

STRATEGIES = {
    "BALANCED_8pos": {
        "tiers": ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"],
        "max_pos": 8,
    },
    "HIGH_CONV_5pos": {
        "tiers": ["MEGA","MOMENTUM","MOMENTUM_N"],
        "max_pos": 5,
    },
}

def run_with_table(label, query_text):
    print(f"\n{'='*70}\n  RUNNING {label}\n{'='*70}")
    sim.SIGNAL_QUERY = query_text
    print("Loading signals + prices from BigQuery ...")
    sig = sim.bq(query_text.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"  {len(sig):,} signal rows")
    # Tier diagnostic
    play_dist = sig.groupby("play_type").size().sort_values(ascending=False)
    print("\nplay_type distribution (top 10):")
    print(play_dist.head(10).to_string())

    # Pull VNI baseline once (same regardless of FA table)
    vni = sim.bq(sim.VNI_QUERY.format(start=START_DATE, end=END_DATE))
    vni["time"] = pd.to_datetime(vni["time"])
    vni_dates = sorted(vni["time"].unique())

    prices = {}
    for tk, g in sig.groupby("ticker"):
        prices[tk] = dict(zip(g["time"], g["Close"]))

    out = {}
    for name, cfg in STRATEGIES.items():
        print(f"\nSimulating {name} (max_pos={cfg['max_pos']}) ...")
        nav_df, trades_df = sim.simulate(sig, prices, vni_dates,
                                          allowed_tiers=cfg["tiers"],
                                          max_positions=cfg["max_pos"],
                                          name=f"{name}_{label}")
        m = sim.metrics(nav_df, trades_df, f"{name}_{label}")
        out[name] = m
        print(f"  trades={m['n_trades']}  CAGR={m['cagr_pct']:.2f}%  "
              f"Sharpe={m['sharpe']:.2f}  MaxDD={m['max_dd_pct']:.1f}%  "
              f"Calmar={m['calmar']:.2f}  WR={m['win_rate_pct']:.1f}%")
    return out, vni

# Run v4 (baseline)
res_v4, vni = run_with_table("v4_baseline", ORIG_QUERY)
res_v5, _   = run_with_table("v5_H3H4",     V5_QUERY)

# VNINDEX B&H
vni_nav = sim.INIT_NAV * vni["Close"] / vni["Close"].iloc[0]
vni_rets = vni_nav.pct_change().dropna()
n_yrs = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days / 365.25
spy = len(vni_rets) / n_yrs
vni_cagr = (vni_nav.iloc[-1] / vni_nav.iloc[0]) ** (1/n_yrs) - 1
vni_sharpe = vni_rets.mean() / vni_rets.std() * np.sqrt(spy)
vni_dd = ((vni_nav - vni_nav.cummax()) / vni_nav.cummax()).min()

# Side-by-side
print("\n" + "═"*100)
print("  BA-SYSTEM IMPACT: H3+H4 FA-system upgrade (default sim config)")
print("═"*100)
print(f"{'Strategy':<22}{'Variant':<14}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}"
      f"{'Trades':>8}{'WR%':>7}{'AvgRet%':>8}{'AvgHold':>9}")
rows = []
for strat in STRATEGIES:
    for tag, res in [("v4_baseline", res_v4), ("v5_H3H4", res_v5)]:
        m = res[strat]
        print(f"{strat:<22}{tag:<14}{m['cagr_pct']:>8.2f}{m['sharpe']:>8.2f}"
              f"{m['max_dd_pct']:>9.1f}{m['calmar']:>8.2f}{m['n_trades']:>8}"
              f"{m['win_rate_pct']:>7.1f}{m['avg_trade_ret_pct']:>8.2f}{m['avg_hold_days']:>9.1f}")
        rows.append({"strategy": strat, "variant": tag, **m})
    # delta row
    m4 = res_v4[strat]; m5 = res_v5[strat]
    print(f"{strat:<22}{'Δ (v5−v4)':<14}{m5['cagr_pct']-m4['cagr_pct']:>+8.2f}"
          f"{m5['sharpe']-m4['sharpe']:>+8.2f}{m5['max_dd_pct']-m4['max_dd_pct']:>+9.1f}"
          f"{m5['calmar']-m4['calmar']:>+8.2f}{m5['n_trades']-m4['n_trades']:>+8}"
          f"{m5['win_rate_pct']-m4['win_rate_pct']:>+7.1f}"
          f"{m5['avg_trade_ret_pct']-m4['avg_trade_ret_pct']:>+8.2f}"
          f"{m5['avg_hold_days']-m4['avg_hold_days']:>+9.1f}")
    print()

print(f"{'VNINDEX_BH':<22}{'baseline':<14}{vni_cagr*100:>8.2f}{vni_sharpe:>8.2f}"
      f"{vni_dd*100:>9.1f}{(vni_cagr/abs(vni_dd) if vni_dd<0 else 0):>8.2f}")

pd.DataFrame(rows).to_csv("ba_v4_v5_compare.csv", index=False)
print("\nSaved ba_v4_v5_compare.csv")
