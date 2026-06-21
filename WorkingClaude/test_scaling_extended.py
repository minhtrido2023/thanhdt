"""Extended capital scaling: 1B/10B/50B/100B/200B + sector concentration + multi-strategy."""
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
TIER_HC  = ["MEGA", "MOMENTUM", "MOMENTUM_N"]

LIQ_BASE = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liquidity_lookup}

# ── Step 1: Capital scaling 1B → 200B ──────────────────────────────────
print("\n" + "═" * 90)
print("  STEP 1 — CAPITAL SCALING (BAL 10p 45d -20% + BL20 + slip 0.1%)")
print("═" * 90)
NAVS = [1e9, 10e9, 30e9, 50e9, 100e9, 200e9, 500e9]
scaling = []
trade_logs = {}
for nav_init in NAVS:
    print(f"\n  Running NAV={nav_init/1e9:.0f}B...")
    nav_df, trades_df = simulate(
        sig, prices, vni_dates, allowed_tiers=TIER_BAL,
        max_positions=10, hold_days=45, stop_loss=-0.20, min_hold=2,
        slippage=0.001, init_nav=nav_init, **LIQ_BASE,
    )
    m = metrics(nav_df, trades_df, f"BAL_{nav_init/1e9:.0f}B")
    m["init_B"] = nav_init / 1e9
    m["wealth_x"] = nav_df["nav"].iloc[-1] / nav_init
    scaling.append(m)
    trades_df["sector_top"] = trades_df["ticker"].map(sec_map).fillna(-1).astype(int)
    trade_logs[nav_init / 1e9] = trades_df
    print(f"    CAGR={m['cagr_pct']:.2f}%  Sh={m['sharpe']:.2f}  "
          f"DD={m['max_dd_pct']:.1f}%  trades={m['n_trades']}")

print("\n" + "═" * 90)
print("  CAPITAL SCALING SUMMARY")
print("═" * 90)
df_scale = pd.DataFrame(scaling)
cols = ["init_B", "wealth_x", "cagr_pct", "sharpe", "max_dd_pct", "calmar",
        "n_trades", "win_rate_pct", "avg_trade_ret_pct", "avg_hold_days"]
print(df_scale[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# ── Step 2: Sector concentration analysis ──────────────────────────────
print("\n" + "═" * 90)
print("  STEP 2 — SECTOR CONCENTRATION ANALYSIS")
print("═" * 90)
sec_names = {0: "Misc/Oil", 1: "Materials", 2: "Industrials", 3: "ConsGoods",
             4: "Health", 5: "ConsServ", 7: "Utilities", 8: "Fin/RE", 9: "Tech/Tel"}

print("\n  Sector mix of executed trades by capital size:")
header = f"  {'Sector':>15} | "
for nav in [1, 10, 50, 100, 200, 500]:
    header += f"{nav:>3}B  | "
print(header)
print("  " + "-" * 90)
for sec in sorted(sec_names.keys()):
    line = f"  {sec_names.get(sec, str(sec)):>15} | "
    for nav in [1, 10, 50, 100, 200, 500]:
        if nav in trade_logs:
            df = trade_logs[nav]
            n = (df["sector_top"] == sec).sum()
            pct = n / len(df) * 100 if len(df) else 0
            line += f"{n:3d}/{pct:4.0f}%| "
        else:
            line += " ---  | "
    print(line)

# Avg ticker liquidity captured per NAV
print("\n  Avg liquidity of captured tickers by capital size:")
for nav in sorted(trade_logs):
    df = trade_logs[nav]
    if len(df) == 0:
        continue
    # Build ticker liquidity (use first signal date for each ticker)
    tk_liq = {}
    for tk in df["ticker"].unique():
        liq_vals = [v for k, v in liquidity_lookup.items() if k[0] == tk]
        if liq_vals:
            tk_liq[tk] = np.median(liq_vals)
    df["liq_B"] = df["ticker"].map(tk_liq) / 1e9
    print(f"  NAV={nav:.0f}B: median_liq={df['liq_B'].median():.1f}B "
          f"(P25={df['liq_B'].quantile(0.25):.1f}B, P75={df['liq_B'].quantile(0.75):.1f}B)")

# ── Step 3: Sector limit at 50B ────────────────────────────────────────
print("\n" + "═" * 90)
print("  STEP 3 — SECTOR LIMIT AT 50B")
print("═" * 90)
print("\n  Running 50B with various sector limits...")
sec_results = []
for sec_lim in [None, 4, 3, 2]:
    sec_extra = {**LIQ_BASE, "init_nav": 50e9}
    if sec_lim:
        sec_extra["sector_limit"] = sec_lim
        sec_extra["ticker_sector_map"] = sec_map
    nav_df, trades_df = simulate(
        sig, prices, vni_dates, allowed_tiers=TIER_BAL,
        max_positions=10, hold_days=45, stop_loss=-0.20, min_hold=2,
        slippage=0.001, **sec_extra,
    )
    m = metrics(nav_df, trades_df, f"50B_secLim{sec_lim}")
    m["sec_lim"] = sec_lim or "none"
    sec_results.append(m)
    print(f"  sec_lim={str(sec_lim):>5}: CAGR={m['cagr_pct']:.2f}%  Sh={m['sharpe']:.2f}  "
          f"DD={m['max_dd_pct']:.1f}%  trades={m['n_trades']}")

df_sec = pd.DataFrame(sec_results)
sec_cols = ["sec_lim", "cagr_pct", "sharpe", "max_dd_pct", "calmar",
            "n_trades", "win_rate_pct"]
print("\n  " + df_sec[sec_cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# ── Step 4: Multi-strategy at 50B ──────────────────────────────────────
print("\n" + "═" * 90)
print("  STEP 4 — MULTI-STRATEGY AT 50B")
print("═" * 90)
print("\n  Running each strategy standalone at 50B...")
strat_navs = {}
for name, tiers, mp, h, sl in [
    ("BAL_50B", TIER_BAL, 10, 45, -0.20),
    ("AGG_50B", TIER_AGG, 7, 45, -0.15),
    ("HC_50B",  TIER_HC, 10, 30, -0.20),
]:
    nav_df, _ = simulate(sig, prices, vni_dates,
        allowed_tiers=tiers, max_positions=mp, hold_days=h, stop_loss=sl,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_BASE)
    nav_df["time"] = pd.to_datetime(nav_df["time"])
    strat_navs[name] = nav_df.set_index("time")["nav"] / 50e9

# Mix
common_idx = strat_navs["BAL_50B"].index.intersection(strat_navs["AGG_50B"].index).intersection(strat_navs["HC_50B"].index)
nav_bal = strat_navs["BAL_50B"].loc[common_idx]
nav_agg = strat_navs["AGG_50B"].loc[common_idx]
nav_hc  = strat_navs["HC_50B"].loc[common_idx]
DEPOSIT_R = 0.03 / 252
cash_growth = pd.Series([(1 + DEPOSIT_R) ** i for i in range(len(common_idx))], index=common_idx)

MIXES = {
    "100% BAL_50B": {"BAL": 1.0, "AGG": 0.0, "HC": 0.0, "cash": 0.0},
    "100% AGG_50B": {"BAL": 0.0, "AGG": 1.0, "HC": 0.0, "cash": 0.0},
    "100% HC_50B":  {"BAL": 0.0, "AGG": 0.0, "HC": 1.0, "cash": 0.0},
    "50_BAL_25_AGG_25_HC_50B":  {"BAL": 0.5, "AGG": 0.25, "HC": 0.25, "cash": 0.0},
    "60_BAL_30_AGG_10_cash_50B":{"BAL": 0.6, "AGG": 0.30, "HC": 0.0, "cash": 0.10},
    "70_BAL_30_AGG_50B":        {"BAL": 0.7, "AGG": 0.30, "HC": 0.0, "cash": 0.0},
}


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
        "wealth_x": nav.iloc[-1]
    }


multi_results = []
for name, w in MIXES.items():
    combined = (w["BAL"] * nav_bal + w["AGG"] * nav_agg +
                w["HC"] * nav_hc + w["cash"] * cash_growth)
    m = metrics_from_nav(combined, name)
    multi_results.append(m)

print("\n  Multi-strategy at 50B:")
df_multi = pd.DataFrame(multi_results)
print(df_multi[["name", "cagr_pct", "sharpe", "max_dd_pct", "calmar", "wealth_x"]
    ].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# Save
df_scale.to_csv(os.path.join(WORKDIR, "scaling_extended.csv"), index=False)
df_sec.to_csv(os.path.join(WORKDIR, "sector_limit_50B.csv"), index=False)
df_multi.to_csv(os.path.join(WORKDIR, "multi_strategy_50B.csv"), index=False)
print("\n  Saved: scaling_extended.csv, sector_limit_50B.csv, multi_strategy_50B.csv")
