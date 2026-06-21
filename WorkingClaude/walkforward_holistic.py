"""Walk-forward validation: IS (2014-2019) vs OOS (2020-2026).

Run identical strategy params on both periods, compare metrics.
If OOS ≈ IS → robust system, not overfit.
If OOS << IS → overfit.
"""
import os
import sys
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import (
    simulate, metrics, bq, SIGNAL_QUERY, VNI_QUERY, INIT_NAV
)

# Two evaluation periods
IS_START = "2014-01-01"
IS_END   = "2019-12-31"
OOS_START = "2020-01-01"
OOS_END   = "2026-01-16"

print("Loading IS (2014-2019)...")
is_sig = bq(SIGNAL_QUERY.format(start=IS_START, end=IS_END))
is_sig["time"] = pd.to_datetime(is_sig["time"])
is_vni = bq(VNI_QUERY.format(start=IS_START, end=IS_END))
is_vni["time"] = pd.to_datetime(is_vni["time"])
is_dates = sorted(is_vni["time"].unique())
is_prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in is_sig.groupby("ticker")}

print("Loading OOS (2020-2026)...")
oos_sig = bq(SIGNAL_QUERY.format(start=OOS_START, end=OOS_END))
oos_sig["time"] = pd.to_datetime(oos_sig["time"])
oos_vni = bq(VNI_QUERY.format(start=OOS_START, end=OOS_END))
oos_vni["time"] = pd.to_datetime(oos_vni["time"])
oos_dates = sorted(oos_vni["time"].unique())
oos_prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in oos_sig.groupby("ticker")}

# Test 5 representative configs from grid
TIER_SETS = {
    "MEGA":         ["MEGA"],
    "HIGH_CONV":    ["MEGA", "MOMENTUM", "MOMENTUM_N"],
    "BALANCED":     ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"],
    "AGGRESSIVE":   ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_A",
                     "MOMENTUM_S_N", "DEEP_VALUE_RECOVERY"],
}

CONFIGS = [
    ("AGGRESSIVE_7p_45d_15sl", "AGGRESSIVE", 7, 45, -0.15),
    ("HC_10p_30d_10sl",        "HIGH_CONV",  10, 30, -0.10),
    ("HC_10p_30d_20sl",        "HIGH_CONV",  10, 30, -0.20),
    ("BAL_10p_60d_15sl",       "BALANCED",   10, 60, -0.15),
    ("MEGA_5p_90d_15sl",       "MEGA",        5, 90, -0.15),
]


def vni_metrics_for(vni_df, label):
    nav = INIT_NAV * vni_df["Close"] / vni_df["Close"].iloc[0]
    n_yrs = (vni_df["time"].iloc[-1] - vni_df["time"].iloc[0]).days / 365.25
    rets = nav.pct_change().dropna()
    spy = len(rets) / n_yrs
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1/n_yrs) - 1
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (nav - nav.cummax()) / nav.cummax()
    return {
        "name": f"VNINDEX_{label}", "n_yrs": n_yrs,
        "cagr_pct": cagr * 100, "sharpe": sharpe,
        "max_dd_pct": dd.min() * 100,
        "calmar": cagr / abs(dd.min()) if dd.min() < 0 else 0,
        "n_trades": 0,
    }


print("\nRunning IS + OOS for all configs...\n")
all_results = []
for cfg_name, tier_name, mp, h, sl in CONFIGS:
    for period_name, sg, prc, dts in [
        ("IS", is_sig, is_prices, is_dates),
        ("OOS", oos_sig, oos_prices, oos_dates),
    ]:
        nav_df, trades_df = simulate(
            sg, prc, dts,
            allowed_tiers=TIER_SETS[tier_name],
            max_positions=mp, hold_days=h, stop_loss=sl,
            min_hold=2,
        )
        m = metrics(nav_df, trades_df, f"{cfg_name}_{period_name}")
        m.update({"config": cfg_name, "period": period_name})
        all_results.append(m)
        print(f"  {cfg_name:25} {period_name:3}: CAGR={m['cagr_pct']:5.1f}%  "
              f"Sh={m['sharpe']:.2f}  DD={m['max_dd_pct']:5.1f}%  Cal={m['calmar']:.2f}  "
              f"trades={m['n_trades']}")

# VNINDEX baseline IS / OOS
all_results.append({**vni_metrics_for(is_vni, "IS"), "config": "VNINDEX_BH", "period": "IS"})
all_results.append({**vni_metrics_for(oos_vni, "OOS"), "config": "VNINDEX_BH", "period": "OOS"})

df = pd.DataFrame(all_results)

# Compute IS vs OOS deltas
print("\n" + "═" * 110)
print("  WALK-FORWARD COMPARISON")
print("═" * 110)
pivot = df.pivot(index="config", columns="period",
                 values=["cagr_pct", "sharpe", "max_dd_pct", "calmar", "n_trades"])
print(pivot.to_string(float_format=lambda x: f"{x:.2f}"))

print("\n" + "═" * 110)
print("  IS vs OOS DELTA (negative = OOS worse than IS)")
print("═" * 110)
deltas = []
for cfg in df["config"].unique():
    is_row = df[(df["config"] == cfg) & (df["period"] == "IS")].iloc[0]
    oos_row = df[(df["config"] == cfg) & (df["period"] == "OOS")].iloc[0]
    deltas.append({
        "config": cfg,
        "IS_CAGR": is_row["cagr_pct"], "OOS_CAGR": oos_row["cagr_pct"],
        "Δ_CAGR": oos_row["cagr_pct"] - is_row["cagr_pct"],
        "IS_Sharpe": is_row["sharpe"], "OOS_Sharpe": oos_row["sharpe"],
        "Δ_Sharpe": oos_row["sharpe"] - is_row["sharpe"],
        "IS_DD": is_row["max_dd_pct"], "OOS_DD": oos_row["max_dd_pct"],
        "IS_Calmar": is_row["calmar"], "OOS_Calmar": oos_row["calmar"],
        "Δ_Calmar": oos_row["calmar"] - is_row["calmar"],
    })
delta_df = pd.DataFrame(deltas)
print(delta_df.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Verdict
print("\n" + "═" * 110)
print("  ROBUSTNESS VERDICT")
print("═" * 110)
for _, r in delta_df.iterrows():
    cfg = r["config"]
    cagr_change = r["Δ_CAGR"]
    sharpe_change = r["Δ_Sharpe"]
    if cfg.startswith("VNINDEX"):
        continue
    if cagr_change > -5 and sharpe_change > -0.2:
        verdict = "✓ ROBUST — OOS performs similarly or better"
    elif cagr_change > -10 and sharpe_change > -0.4:
        verdict = "⚠ MILD DEGRADATION — acceptable"
    else:
        verdict = "❌ POSSIBLE OVERFIT — significant OOS drop"
    print(f"  {cfg:30} ΔCAGR={cagr_change:+5.1f}pp ΔSharpe={sharpe_change:+.2f}  {verdict}")

df.to_csv(os.path.join(WORKDIR, "data/walkforward_results.csv"), index=False)
delta_df.to_csv(os.path.join(WORKDIR, "data/walkforward_deltas.csv"), index=False)
print("\n  Saved: walkforward_results.csv, walkforward_deltas.csv")
