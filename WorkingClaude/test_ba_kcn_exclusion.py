#!/usr/bin/env python3
"""
test_ba_kcn_exclusion.py
========================
Validate: does excluding KCN tickers from BA-45d improve performance?

Hypothesis: KCN at 3M has negative-expected returns (-3.88% all-time mean).
BA-45d holds ~45 days. If KCN picks come into A tier and get selected,
they likely drag performance.

Test design:
  - Run BA canonical sim WITH KCN included (baseline = current)
  - Run BA canonical sim WITHOUT KCN (pre-filter signals)
  - Compare: full period (2014-2026) + OOS (2024-2026)

Uses SIGNAL_V10 + canonical config (50B, max=10, hold=45d, stop=-20%,
slip=0.1%, sec_lim 8:4, liq caps).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY, START_DATE, END_DATE
from test_round14_stability import SIGNAL_V10
from ba_ticker_filters import KCN_TICKERS, filter_signals_for_ba_45d

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
OOS_START = pd.Timestamp("2024-01-01")


def run_canonical(label, sig, prices, vni_dates, sec_map, top30, liq_map):
    """Run BA canonical: 50/50 BAL + VN30."""
    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    print(f"\n  Simulating BAL+Fin/RE-max-4 (50B) ...")
    nav_bal, trades_bal = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    print(f"  Simulating VN30_BAL (50B) ...")
    sig_vn30 = sig[sig["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    return ba_nav, trades_bal, trades_vn30


def window_metrics(nav, start, end, label):
    sub = nav[(nav.index >= start) & (nav.index <= end)]
    if len(sub) < 30: return None
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = ((sub - sub.cummax()) / sub.cummax()).min()
    cal = cagr / abs(dd) if dd < 0 else 0
    return {"label": label, "cagr": cagr*100, "sharpe": sharpe,
            "mdd": dd*100, "calmar": cal, "wealth": sub.iloc[-1] / sub.iloc[0]}


# ─── Load shared signals + prices once ────────────────────────────────────
print(f"Window: {START_DATE} → {END_DATE}")
print("Loading shared SIGNAL_V10 + prices + sectors + VN30 ...")
sig_all = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig_all["time"] = pd.to_datetime(sig_all["time"])
print(f"  signals: {len(sig_all):,} rows")
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_all.groupby("ticker")}
liq_map_all = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_all.iterrows()}
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
sec_map = bq("""SELECT DISTINCT t.ticker,
               CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
               FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
               AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
            """).set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
               WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
               AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
               GROUP BY t.ticker
               ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

# Diagnostic: how many KCN are in the signal universe
kcn_in_signals = set(sig_all["ticker"]) & KCN_TICKERS
print(f"\nKCN tickers in signal universe: {len(kcn_in_signals)} / {len(KCN_TICKERS)}")
print(f"  {sorted(kcn_in_signals)}")
n_kcn_signals = len(sig_all[sig_all["ticker"].isin(KCN_TICKERS)])
print(f"  Total KCN signal rows: {n_kcn_signals:,} ({n_kcn_signals/len(sig_all)*100:.1f}% of universe)")

# Filter signals
sig_with_kcn = sig_all
sig_no_kcn = filter_signals_for_ba_45d(sig_all)
print(f"\n  WITH_KCN signals: {len(sig_with_kcn):,}")
print(f"  NO_KCN  signals: {len(sig_no_kcn):,}  (diff: {len(sig_with_kcn)-len(sig_no_kcn):,})")

# ─── Run sims ───────────────────────────────────────────────────────────
print("\n" + "="*70 + "\n  RUN: WITH_KCN (baseline)\n" + "="*70)
ba_with, _, _ = run_canonical("WITH_KCN", sig_with_kcn, prices, vni_dates, sec_map, top30, liq_map_all)

print("\n" + "="*70 + "\n  RUN: NO_KCN (exclude KCN tickers)\n" + "="*70)
liq_map_no_kcn = {k: v for k, v in liq_map_all.items() if k[0] not in KCN_TICKERS}
# Note: filter prices too — to avoid simulate seeing KCN prices
prices_no_kcn = {tk: pr for tk, pr in prices.items() if tk not in KCN_TICKERS}
ba_no, _, _ = run_canonical("NO_KCN", sig_no_kcn, prices_no_kcn, vni_dates, sec_map, top30, liq_map_no_kcn)

# ─── Compare ────────────────────────────────────────────────────────────
periods = [
    ("FULL 2014-2026", ba_with.index.min(), ba_with.index.max()),
    ("OOS 2024-2026", OOS_START, ba_with.index.max()),
    ("Mid 2018-2023", pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
]
print("\n" + "═"*100)
print("  KCN EXCLUSION TEST — BA canonical 50/50 BAL+VN30")
print("═"*100)
print(f"  {'Period':<22}{'Variant':<14}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}")
print("  " + "-"*70)
for plabel, st, en in periods:
    mw = window_metrics(ba_with, st, en, "WITH_KCN")
    mn = window_metrics(ba_no, st, en, "NO_KCN")
    if mw is None or mn is None: continue
    print(f"  {plabel:<22}{'WITH_KCN':<14}{mw['cagr']:>8.2f}{mw['sharpe']:>8.2f}"
          f"{mw['mdd']:>9.1f}{mw['calmar']:>8.2f}{mw['wealth']:>8.2f}")
    print(f"  {plabel:<22}{'NO_KCN':<14}{mn['cagr']:>8.2f}{mn['sharpe']:>8.2f}"
          f"{mn['mdd']:>9.1f}{mn['calmar']:>8.2f}{mn['wealth']:>8.2f}")
    print(f"  {plabel:<22}{'Δ (no-with)':<14}{mn['cagr']-mw['cagr']:>+8.2f}"
          f"{mn['sharpe']-mw['sharpe']:>+8.2f}{mn['mdd']-mw['mdd']:>+9.1f}"
          f"{mn['calmar']-mw['calmar']:>+8.2f}{mn['wealth']-mw['wealth']:>+8.2f}")
    print()

print("\nDONE")
