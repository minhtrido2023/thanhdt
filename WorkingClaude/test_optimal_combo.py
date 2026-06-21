"""Test BAL with optimal combos found in rounds 5-7:
  - Base: BAL 10p 45d -20%, slip 0.1%
  - Add: blacklist 20d (round 7)
  - Add: trailing tight +10/-6 (round 5)
  - Add: sector limit 3 (round 5)
  - Multi-strategy 50 BAL + 25 AGG + 25 HC (round 7)
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

# Sector map
sec_query = """
SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code / 1000) AS INT64) AS sector_top
FROM tav2_bq.ticker AS t
WHERE t.ICB_Code IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
"""
sec_df = bq(sec_query)
sec_map = sec_df.set_index("ticker")["sector_top"].to_dict()

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
TIER_AGG = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
            "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"]
TIER_HC = ["MEGA", "MOMENTUM", "MOMENTUM_N"]

VARIANTS = [
    # Baseline
    ("BAL_baseline",            TIER_BAL, 10, 45, -0.20, {}),
    # Single overlays
    ("BAL_BL20",                TIER_BAL, 10, 45, -0.20, {"reentry_blacklist_days": 20}),
    ("BAL_trail",               TIER_BAL, 10, 45, -0.20, {"trailing_stop_activate": 0.10,
                                                          "trailing_stop_pct": 0.06}),
    ("BAL_sec3",                TIER_BAL, 10, 45, -0.20, {"sector_limit": 3,
                                                          "ticker_sector_map": sec_map}),
    # Pairs
    ("BAL_BL20_trail",          TIER_BAL, 10, 45, -0.20, {"reentry_blacklist_days": 20,
                                                          "trailing_stop_activate": 0.10,
                                                          "trailing_stop_pct": 0.06}),
    ("BAL_BL20_sec3",           TIER_BAL, 10, 45, -0.20, {"reentry_blacklist_days": 20,
                                                          "sector_limit": 3,
                                                          "ticker_sector_map": sec_map}),
    ("BAL_trail_sec3",          TIER_BAL, 10, 45, -0.20, {"trailing_stop_activate": 0.10,
                                                          "trailing_stop_pct": 0.06,
                                                          "sector_limit": 3,
                                                          "ticker_sector_map": sec_map}),
    # All combined
    ("BAL_ALL",                 TIER_BAL, 10, 45, -0.20, {"reentry_blacklist_days": 20,
                                                          "trailing_stop_activate": 0.10,
                                                          "trailing_stop_pct": 0.06,
                                                          "sector_limit": 3,
                                                          "ticker_sector_map": sec_map}),
]

results = []
all_navs = {}
for name, tiers, mp, h, sl, extra in VARIANTS:
    print(f"\n  Running {name}...")
    nav_df, trades_df = simulate(
        sig, prices, vni_dates,
        allowed_tiers=tiers, max_positions=mp, hold_days=h, stop_loss=sl,
        min_hold=2, slippage=0.001, **extra,
    )
    m = metrics(nav_df, trades_df, name)
    all_navs[name] = nav_df.set_index(pd.to_datetime(nav_df["time"]))["nav"]
    results.append({"name": name, **m})
    print(f"    CAGR={m['cagr_pct']:.2f}% Sh={m['sharpe']:.2f} DD={m['max_dd_pct']:.1f}% "
          f"Cal={m['calmar']:.2f} trades={m['n_trades']}")

# Multi-strategy with optimized BAL
print("\n  Running multi-strategy with optimized BAL_ALL...")
nav_bal_all = all_navs["BAL_ALL"]
nav_agg, _ = simulate(sig, prices, vni_dates,
                      allowed_tiers=TIER_AGG, max_positions=7, hold_days=45, stop_loss=-0.15,
                      min_hold=2, slippage=0.001, reentry_blacklist_days=10)
nav_agg = nav_agg.set_index(pd.to_datetime(nav_agg["time"]))["nav"] / INIT_NAV
nav_hc, _ = simulate(sig, prices, vni_dates,
                     allowed_tiers=TIER_HC, max_positions=10, hold_days=30, stop_loss=-0.20,
                     min_hold=2, slippage=0.001)
nav_hc = nav_hc.set_index(pd.to_datetime(nav_hc["time"]))["nav"] / INIT_NAV
nav_bal_all_norm = nav_bal_all / INIT_NAV

common_idx = nav_bal_all_norm.index.intersection(nav_agg.index).intersection(nav_hc.index)
nav_bal_all_norm = nav_bal_all_norm.loc[common_idx]
nav_agg = nav_agg.loc[common_idx]
nav_hc = nav_hc.loc[common_idx]

multi = 0.5 * nav_bal_all_norm + 0.25 * nav_agg + 0.25 * nav_hc
ret = multi.pct_change().dropna()
n_yrs = (multi.index[-1] - multi.index[0]).days / 365.25
spy = len(ret) / n_yrs
cagr = (multi.iloc[-1] / multi.iloc[0]) ** (1/n_yrs) - 1
sharpe = ret.mean() / ret.std() * np.sqrt(spy)
dd = (multi - multi.cummax()) / multi.cummax()
multi_metrics = {
    "name": "MULTI_50BALall_25AGG_25HC", "cagr_pct": cagr * 100, "sharpe": sharpe,
    "max_dd_pct": dd.min() * 100, "calmar": cagr / abs(dd.min()), "n_trades": 0,
    "win_rate_pct": 0, "avg_trade_ret_pct": 0,
}
results.append(multi_metrics)
print(f"    Multi: CAGR={cagr*100:.2f}% Sh={sharpe:.2f} DD={dd.min()*100:.1f}% Cal={cagr/abs(dd.min()):.2f}")

print("\n" + "═" * 100)
print("  OPTIMAL COMBINATION TEST")
print("═" * 100)
df = pd.DataFrame(results)
cols = ["name", "cagr_pct", "sharpe", "sortino", "max_dd_pct", "calmar",
        "n_trades", "win_rate_pct"]
df_sorted = df.sort_values("sharpe", ascending=False)
print(df_sorted[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Crash defense 2022
print("\n" + "═" * 100)
print("  2022 CRASH DEFENSE")
print("═" * 100)
for name, nav in all_navs.items():
    n2021 = nav[nav.index.year == 2021].iloc[-1]
    n2022 = nav[nav.index.year == 2022].iloc[-1]
    chg = (n2022 / n2021 - 1) * 100
    print(f"  {name:30} {chg:+.2f}%")
m2021 = multi[multi.index.year == 2021].iloc[-1]
m2022 = multi[multi.index.year == 2022].iloc[-1]
print(f"  {'MULTI_50BALall_25AGG_25HC':30} {(m2022/m2021-1)*100:+.2f}%")

df.to_csv(os.path.join(WORKDIR, "optimal_combo_results.csv"), index=False)
print("\n  Saved: optimal_combo_results.csv")
