"""Round 11 — combine winning configs + VN30 universe + rolling window."""
import os
import sys
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import (
    simulate, metrics, bq, SIGNAL_QUERY, VNI_QUERY, START_DATE, END_DATE
)

print("Loading data...")
sig = bq(SIGNAL_QUERY.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liquidity_lookup = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

sec_query = """
SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code / 1000) AS INT64) AS sector_top
FROM tav2_bq.ticker AS t
WHERE t.ICB_Code IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
"""
sec_map = bq(sec_query).set_index("ticker")["sector_top"].to_dict()

# Top 30 by liquidity (proxy for VN30)
print("\nIdentifying VN30 proxy (top 30 by avg liquidity)...")
top30_query = """
SELECT t.ticker, AVG(t.Volume_3M_P50 * t.Close) AS avg_liq
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker
ORDER BY avg_liq DESC
LIMIT 30
"""
top30_df = bq(top30_query)
TOP30 = set(top30_df["ticker"])
print(f"  Top 30 by liquidity: {sorted(TOP30)}")

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
TIER_HC  = ["MEGA", "MOMENTUM", "MOMENTUM_N"]

LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
       "liquidity_lookup": liquidity_lookup,
       "exit_slippage_tiered": True}


# ─── PART A: Multi-strategy with optimal configs ───────────────────────
print("\n" + "═" * 100)
print("  PART A — MULTI-STRATEGY: BAL+Fin/RE-max-4 vs HC mix at 50B")
print("═" * 100)

# Run individual strategies
print("\n  Running individual configs at 50B (slip 0.1% + tiered exit)...")
nav_bal_winner, _ = simulate(
    sig, prices, vni_dates, allowed_tiers=TIER_BAL,
    max_positions=10, hold_days=45, stop_loss=-0.20, min_hold=2,
    slippage=0.001, init_nav=50e9,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
    **LIQ,
)
nav_hc, _ = simulate(
    sig, prices, vni_dates, allowed_tiers=TIER_HC,
    max_positions=10, hold_days=30, stop_loss=-0.20, min_hold=2,
    slippage=0.001, init_nav=50e9, **LIQ,
)
nav_bal_winner["time"] = pd.to_datetime(nav_bal_winner["time"])
nav_hc["time"] = pd.to_datetime(nav_hc["time"])
nav_bw = nav_bal_winner.set_index("time")["nav"] / 50e9
nav_hc_n = nav_hc.set_index("time")["nav"] / 50e9
common = nav_bw.index.intersection(nav_hc_n.index)
nav_bw = nav_bw.loc[common]
nav_hc_n = nav_hc_n.loc[common]


def metrics_from_nav(nav, name):
    rets = nav.pct_change().dropna()
    n_yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets) / n_yrs
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1/n_yrs) - 1
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (nav - nav.cummax()) / nav.cummax()
    return {
        "name": name, "cagr_pct": cagr * 100, "sharpe": sharpe,
        "max_dd_pct": dd.min() * 100,
        "calmar": cagr / abs(dd.min()) if dd.min() < 0 else 0,
        "wealth_x": nav.iloc[-1],
    }


MIXES = [
    ("100% BAL+Fin4", {"BW": 1.0, "HC": 0.0}),
    ("100% HC", {"BW": 0.0, "HC": 1.0}),
    ("70_BW_30_HC", {"BW": 0.7, "HC": 0.3}),
    ("60_BW_40_HC", {"BW": 0.6, "HC": 0.4}),
    ("50_BW_50_HC", {"BW": 0.5, "HC": 0.5}),
    ("40_BW_60_HC", {"BW": 0.4, "HC": 0.6}),
    ("30_BW_70_HC", {"BW": 0.3, "HC": 0.7}),
]
multi_results = []
print(f"\n  {'Mix':25} | {'CAGR':>7} {'Sh':>6} {'DD':>7} {'Cal':>5}")
for name, w in MIXES:
    combined = w["BW"] * nav_bw + w["HC"] * nav_hc_n
    m = metrics_from_nav(combined, name)
    multi_results.append(m)
    print(f"  {name:25} | {m['cagr_pct']:>6.2f}% {m['sharpe']:>6.2f} "
          f"{m['max_dd_pct']:>6.1f}% {m['calmar']:>5.2f}")


# ─── PART B: VN30-only universe ──────────────────────────────────────
print("\n" + "═" * 100)
print("  PART B — VN30-ONLY UNIVERSE (top 30 liquidity)")
print("═" * 100)

# Filter signals to top30 only
sig_vn30 = sig[sig["ticker"].isin(TOP30)].copy()
prices_vn30 = {tk: prices[tk] for tk in TOP30 if tk in prices}
liq_vn30 = {k: v for k, v in liquidity_lookup.items() if k[0] in TOP30}

LIQ_VN30 = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_vn30,
            "exit_slippage_tiered": True}

print(f"\n  VN30 signals: {len(sig_vn30):,}/{len(sig):,} ({len(sig_vn30)/len(sig)*100:.1f}%)")
print(f"  {'Config':35} | {'CAGR':>7} {'Sh':>6} {'DD':>7} {'Cal':>5} {'trades':>7}")

vn30_results = []
for nav_lvl in [50e9, 100e9, 200e9, 500e9]:
    for tier_name, tiers, mp, h, sl in [
        ("BAL", TIER_BAL, 10, 45, -0.20),
        ("HC", TIER_HC, 10, 30, -0.20),
    ]:
        nav_df, trades_df = simulate(
            sig_vn30, prices_vn30, vni_dates, allowed_tiers=tiers,
            max_positions=mp, hold_days=h, stop_loss=sl, min_hold=2,
            slippage=0.001, init_nav=nav_lvl, **LIQ_VN30,
        )
        m = metrics(nav_df, trades_df, f"VN30_{tier_name}_{nav_lvl/1e9:.0f}B")
        m["nav_B"] = nav_lvl / 1e9
        m["wealth_x"] = nav_df["nav"].iloc[-1] / nav_lvl
        vn30_results.append({**m})
        print(f"  VN30_{tier_name}_{nav_lvl/1e9:.0f}B".ljust(37) +
              f"| {m['cagr_pct']:>6.2f}% {m['sharpe']:>6.2f} "
              f"{m['max_dd_pct']:>6.1f}% {m['calmar']:>5.2f} "
              f"{m['n_trades']:>7d}")


# ─── PART C: Rolling 3-year window stability ─────────────────────────
print("\n" + "═" * 100)
print("  PART C — ROLLING 3-YEAR WINDOW STABILITY (BAL+Fin/RE max 4 at 50B)")
print("═" * 100)

# Use already-loaded BAL+Fin/RE-max-4 NAV
nav_bw_full = pd.Series(nav_bal_winner["nav"].values, index=nav_bal_winner["time"]) / 50e9
print(f"\n  Computing rolling 3-year metrics (window step: 1 year)...")
yrs = sorted(set(nav_bw_full.index.year))
roll_results = []
for start_yr in yrs[:-2]:
    end_yr = start_yr + 2  # 3-year window inclusive
    window = nav_bw_full[(nav_bw_full.index.year >= start_yr) &
                          (nav_bw_full.index.year <= end_yr)]
    if len(window) < 200:
        continue
    rets = window.pct_change().dropna()
    n_yrs = (window.index[-1] - window.index[0]).days / 365.25
    spy = len(rets) / n_yrs
    cagr = (window.iloc[-1] / window.iloc[0]) ** (1/n_yrs) - 1
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (window - window.cummax()) / window.cummax()
    roll_results.append({
        "window": f"{start_yr}-{end_yr}",
        "n_days": len(window),
        "cagr_pct": cagr * 100,
        "sharpe": sharpe,
        "max_dd_pct": dd.min() * 100,
        "calmar": cagr / abs(dd.min()) if dd.min() < 0 else 0,
    })
df_roll = pd.DataFrame(roll_results)
print(df_roll.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Save
pd.DataFrame(multi_results).to_csv(os.path.join(WORKDIR, "data/round11_multistrategy.csv"), index=False)
pd.DataFrame(vn30_results).to_csv(os.path.join(WORKDIR, "data/round11_vn30.csv"), index=False)
df_roll.to_csv(os.path.join(WORKDIR, "data/round11_rolling.csv"), index=False)
print(f"\n  Saved: round11_*.csv")
