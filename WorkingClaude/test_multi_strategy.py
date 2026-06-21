"""Multi-strategy portfolio: combine BAL + AGG + cash with different weights.

Each strategy runs on its own capital allocation; combined NAV = sum.
Tests if diversification reduces DD without sacrificing too much CAGR.
"""
import os
import sys
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import (
    simulate, metrics, bq, SIGNAL_QUERY, VNI_QUERY, START_DATE, END_DATE, INIT_NAV
)

print("Loading data...")
sig = bq(SIGNAL_QUERY.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
TIER_AGG = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
            "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"]
TIER_HC  = ["MEGA", "MOMENTUM", "MOMENTUM_N"]

print("\nRunning standalone strategies (slip 0.1%)...")
nav_bal, _ = simulate(sig, prices, vni_dates, allowed_tiers=TIER_BAL,
                      max_positions=10, hold_days=45, stop_loss=-0.20,
                      min_hold=2, slippage=0.001)
nav_bal = nav_bal.set_index(pd.to_datetime(nav_bal["time"]))["nav"] / INIT_NAV

nav_agg, _ = simulate(sig, prices, vni_dates, allowed_tiers=TIER_AGG,
                      max_positions=7, hold_days=45, stop_loss=-0.15,
                      min_hold=2, slippage=0.001)
nav_agg = nav_agg.set_index(pd.to_datetime(nav_agg["time"]))["nav"] / INIT_NAV

nav_hc, _ = simulate(sig, prices, vni_dates, allowed_tiers=TIER_HC,
                     max_positions=10, hold_days=30, stop_loss=-0.20,
                     min_hold=2, slippage=0.001)
nav_hc = nav_hc.set_index(pd.to_datetime(nav_hc["time"]))["nav"] / INIT_NAV

# Cash growth
DEPOSIT_R = 0.03 / 252
cash_growth = pd.Series(
    [(1 + DEPOSIT_R) ** i for i in range(len(vni_dates))],
    index=pd.to_datetime(vni_dates),
)

# VNINDEX baseline
vni_nav = vni.set_index(pd.to_datetime(vni["time"]))["Close"]
vni_nav = vni_nav / vni_nav.iloc[0]

# Align all to same index
common_idx = nav_bal.index.intersection(nav_agg.index).intersection(nav_hc.index)
nav_bal = nav_bal.loc[common_idx]
nav_agg = nav_agg.loc[common_idx]
nav_hc = nav_hc.loc[common_idx]
cash_growth = cash_growth.loc[common_idx]
vni_nav = vni_nav.reindex(common_idx, method="ffill")

print(f"  Aligned {len(common_idx)} trading days")

# Multi-strategy mixes
MIXES = {
    "100% BAL":              {"BAL": 1.0, "AGG": 0.0, "HC": 0.0, "cash": 0.0},
    "100% AGG":              {"BAL": 0.0, "AGG": 1.0, "HC": 0.0, "cash": 0.0},
    "100% HC":               {"BAL": 0.0, "AGG": 0.0, "HC": 1.0, "cash": 0.0},
    "60_BAL_30_AGG_10_cash": {"BAL": 0.6, "AGG": 0.3, "HC": 0.0, "cash": 0.1},
    "70_BAL_30_AGG":         {"BAL": 0.7, "AGG": 0.3, "HC": 0.0, "cash": 0.0},
    "50_BAL_50_AGG":         {"BAL": 0.5, "AGG": 0.5, "HC": 0.0, "cash": 0.0},
    "50_BAL_25_AGG_25_HC":   {"BAL": 0.5, "AGG": 0.25, "HC": 0.25, "cash": 0.0},
    "33_BAL_33_AGG_33_HC":   {"BAL": 0.34, "AGG": 0.33, "HC": 0.33, "cash": 0.0},
    "40_BAL_30_AGG_20_HC_10c":{"BAL": 0.4, "AGG": 0.3, "HC": 0.2, "cash": 0.1},
}


def metrics_from_nav(nav, name):
    ret = nav.pct_change().dropna()
    n_yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    sessions = len(ret) / n_yrs
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1/n_yrs) - 1
    sharpe = ret.mean() / ret.std() * np.sqrt(sessions) if ret.std() > 0 else 0
    downside = ret[ret < 0]
    sortino = (ret.mean() / downside.std() * np.sqrt(sessions)) if len(downside) and downside.std() > 0 else 0
    dd = (nav - nav.cummax()) / nav.cummax()
    return {
        "name": name,
        "cagr_pct": cagr * 100,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_dd_pct": dd.min() * 100,
        "calmar": cagr / abs(dd.min()) if dd.min() < 0 else 0,
        "wealth_x": nav.iloc[-1],
    }


# Compute mix NAVs
all_metrics = []
all_navs = {}
for name, w in MIXES.items():
    combined = (
        w["BAL"] * nav_bal +
        w["AGG"] * nav_agg +
        w["HC"]  * nav_hc +
        w["cash"] * cash_growth
    )
    all_navs[name] = combined
    m = metrics_from_nav(combined, name)
    all_metrics.append({**m, "weights": str(w)})

# VNINDEX baseline
vni_m = metrics_from_nav(vni_nav, "VNINDEX_BH")
all_metrics.append({**vni_m, "weights": "BH"})

print("\n" + "═" * 100)
print("  MULTI-STRATEGY PORTFOLIO COMPARISON (slip 0.1%)")
print("═" * 100)
df = pd.DataFrame(all_metrics)
cols = ["name", "cagr_pct", "sharpe", "sortino", "max_dd_pct", "calmar", "wealth_x"]
df_sorted = df.sort_values("sharpe", ascending=False)
print(df_sorted[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Year-by-year
print("\n" + "═" * 100)
print("  YEAR-BY-YEAR NAV WEALTH MULTIPLIER")
print("═" * 100)
yr_table = pd.DataFrame()
for name, nav in all_navs.items():
    yrs = nav.groupby(nav.index.year).last()
    yr_table[name] = yrs
yr_table["VNINDEX_BH"] = vni_nav.groupby(vni_nav.index.year).last()
print(yr_table.round(2).to_string())

# Crash defense
print("\n" + "═" * 100)
print("  2022 CRASH DEFENSE (NAV change 2021-end → 2022-end)")
print("═" * 100)
for name, nav in all_navs.items():
    n2021 = nav[nav.index.year == 2021].iloc[-1]
    n2022 = nav[nav.index.year == 2022].iloc[-1]
    chg = (n2022 / n2021 - 1) * 100
    print(f"  {name:30} {chg:+.2f}%")
v21 = vni_nav[vni_nav.index.year == 2021].iloc[-1]
v22 = vni_nav[vni_nav.index.year == 2022].iloc[-1]
print(f"  {'VNINDEX_BH':30} {(v22/v21-1)*100:+.2f}%")

df.to_csv(os.path.join(WORKDIR, "multi_strategy_results.csv"), index=False)
print("\n  Saved: multi_strategy_results.csv")
