"""Final comparison of best fine-tuned configs side-by-side."""
import os
import sys
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import (
    simulate, metrics, bq, SIGNAL_QUERY, VNI_QUERY,
    START_DATE, END_DATE, INIT_NAV
)

print("Loading data...")
sig = bq(SIGNAL_QUERY.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
prices = {}
for tk, g in sig.groupby("ticker"):
    prices[tk] = dict(zip(g["time"], g["Close"]))

# Top configs from fine-tune
TIER_SETS = {
    "MEGA":         ["MEGA"],
    "HIGH_CONV":    ["MEGA", "MOMENTUM", "MOMENTUM_N"],
    "BALANCED":     ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"],
    "AGGRESSIVE":   ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
                     "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"],
}

CONFIGS = [
    ("MaxCAGR_AGG_7p_45d_15sl",  "AGGRESSIVE", 7,  45, -0.15),
    ("BestSharpe_HC_10p_30d_10sl","HIGH_CONV", 10, 30, -0.10),
    ("BestCalmar_HC_10p_30d_20sl","HIGH_CONV", 10, 30, -0.20),
    ("Balanced_BAL_10p_60d_15sl","BALANCED",  10, 60, -0.15),
    ("Passive_MEGA_5p_90d_15sl", "MEGA",       5, 90, -0.15),
]

results = {}
for name, tier_name, mp, h, sl in CONFIGS:
    print(f"\nSimulating {name}...")
    nav_df, trades_df = simulate(
        sig, prices, vni_dates,
        allowed_tiers=TIER_SETS[tier_name],
        max_positions=mp,
        hold_days=h,
        stop_loss=sl,
        min_hold=2,
        name=name,
    )
    m = metrics(nav_df, trades_df, name)
    results[name] = (nav_df, trades_df, m)
    print(f"  {m['n_trades']} trades, CAGR={m['cagr_pct']:.1f}%, Sharpe={m['sharpe']:.2f}, "
          f"MaxDD={m['max_dd_pct']:.1f}%, Calmar={m['calmar']:.2f}")

print("\n" + "═" * 110)
print("  FINAL COMPARISON (T+1 entry, T+3 min hold, TC 0.1%/side + tax 0.1%/sell)")
print("═" * 110)
cols = ["name", "cagr_pct", "sharpe", "sortino", "max_dd_pct", "calmar",
        "n_trades", "trades_per_year", "win_rate_pct", "avg_hold_days",
        "stop_pct", "time_pct"]
summary = pd.DataFrame([results[n][2] for n in results.keys()])

# Add VNINDEX baseline
import numpy as np
vni_nav = INIT_NAV * vni["Close"] / vni["Close"].iloc[0]
n_yrs = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days / 365.25
vni_rets = vni_nav.pct_change().dropna()
spy = len(vni_rets) / n_yrs
vni_cagr = (vni_nav.iloc[-1] / vni_nav.iloc[0]) ** (1/n_yrs) - 1
vni_sharpe = vni_rets.mean() / vni_rets.std() * np.sqrt(spy)
vni_dd = (vni_nav - vni_nav.cummax()) / vni_nav.cummax()
vni_metrics = {
    "name": "VNINDEX_BH",
    "cagr_pct": vni_cagr * 100, "sharpe": vni_sharpe,
    "sortino": vni_rets[vni_rets<0].std() and vni_rets.mean()/vni_rets[vni_rets<0].std()*np.sqrt(spy) or 0,
    "max_dd_pct": vni_dd.min() * 100,
    "calmar": vni_cagr / abs(vni_dd.min()),
    "n_trades": 0, "trades_per_year": 0, "win_rate_pct": 0, "avg_hold_days": 0,
    "stop_pct": 0, "time_pct": 0,
}
summary = pd.concat([summary, pd.DataFrame([vni_metrics])], ignore_index=True)
print(summary[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Year-by-year
print("\n" + "═" * 110)
print("  YEAR-BY-YEAR NAV (M VND, start 1B)")
print("═" * 110)
yr_table = pd.DataFrame()
for name, (nav_df, _, _) in results.items():
    nav_df["yr"] = pd.to_datetime(nav_df["time"]).dt.year
    yr_table[name] = (nav_df.groupby("yr")["nav"].last() / 1e6).astype(int)
yr_table["VNINDEX"] = ((INIT_NAV * vni["Close"] / vni["Close"].iloc[0] / 1e6)
                       .groupby(vni["time"].dt.year).last()).astype(int)
print(yr_table.to_string())

# 2022 crash test
print("\n" + "═" * 110)
print("  2022 CRASH DEFENSE (NAV change from 2021 end → 2022 end)")
print("═" * 110)
for name, (nav_df, _, _) in results.items():
    nav_df["yr"] = pd.to_datetime(nav_df["time"]).dt.year
    nav_2021 = nav_df[nav_df["yr"] == 2021]["nav"].iloc[-1]
    nav_2022 = nav_df[nav_df["yr"] == 2022]["nav"].iloc[-1]
    chg = (nav_2022 / nav_2021 - 1) * 100
    print(f"  {name:35} {chg:+.1f}%   ({nav_2021/1e6:,.0f} → {nav_2022/1e6:,.0f}M)")
vni_2021 = (INIT_NAV * vni["Close"] / vni["Close"].iloc[0])[vni["time"].dt.year==2021].iloc[-1]
vni_2022 = (INIT_NAV * vni["Close"] / vni["Close"].iloc[0])[vni["time"].dt.year==2022].iloc[-1]
print(f"  {'VNINDEX_BH':35} {(vni_2022/vni_2021-1)*100:+.1f}%   "
      f"({vni_2021/1e6:,.0f} → {vni_2022/1e6:,.0f}M)")

# Save outputs
for name, (nav_df, trades_df, _) in results.items():
    nav_df.to_csv(os.path.join(WORKDIR, f"final_{name}_nav.csv"), index=False)
    trades_df.to_csv(os.path.join(WORKDIR, f"final_{name}_trades.csv"), index=False)
summary.to_csv(os.path.join(WORKDIR, "data/final_holistic_summary.csv"), index=False)
print("\n  Saved: final_*.csv")
