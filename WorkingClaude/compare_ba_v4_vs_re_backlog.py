#!/usr/bin/env python3
"""
compare_ba_v4_vs_re_backlog.py
==============================
B2 hypothesis: instead of refactoring FA scoring (which broke at canonical sim
in v5/v9), add a NEW play_type 'RE_BACKLOG_BUY' that fires when an RE ticker
(ICB 8633) has AdvCust_YoY > 0.5 AND fa_tier IN ('C','D','E') AND ta >= 90.

Logic: capture the TCH-pattern (advance-customer surge as leading indicator)
WITHOUT disturbing v4 FA tier distribution or v10 sector tilt rules.

Compares:
  - v4 baseline (current production)
  - v4 + RE_BACKLOG_BUY (new tier added to allowed_tiers)

Both runs use tav2_bq.fa_ratings (unchanged v4).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, re as _re, io
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate, bq, VNI_QUERY, START_DATE, END_DATE

# Inject RE_BACKLOG_BUY priority (same as DEEP_VALUE_RECOVERY — recovery on cyclical)
shn.TIER_PRIORITY["RE_BACKLOG_BUY"] = 55

# ─── Inline SIGNAL_V10 and patch ──────────────────────────────────────────────
with open(os.path.join(WORKDIR, "test_round14_stability.py"), encoding="utf-8") as _f:
    _src = _f.read()
_m = _re.search(r'SIGNAL_V10\s*=\s*"""(.+?)"""', _src, _re.DOTALL)
SIGNAL_V10_BASE = _m.group(0).split('"""', 1)[1].rsplit('"""', 1)[0]
SIGNAL_V10_BASE = SIGNAL_V10_BASE.replace(
    "CASE WHEN t.VNINDEX_RSI_Max3M > 0.65 THEN 10 ELSE 0 END",
    "CASE WHEN FALSE THEN 10 ELSE 0 END")

# v4 baseline = unchanged
V4_QUERY = SIGNAL_V10_BASE

# v4 + RE_BACKLOG: add AdvCust to fin_dated CTE, expose adv_yoy, add play_type rule
V4_RE_QUERY = SIGNAL_V10_BASE.replace(
    "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,",
    "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,\n"
    "    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4, 0)) - 1 AS adv_yoy,"
).replace(
    "fin.Revenue_YoY_P0 AS rev_yoy,",
    "fin.Revenue_YoY_P0 AS rev_yoy, fin.adv_yoy AS adv_yoy, t.ICB_Code AS icb,"
).replace(
    # Insert RE_BACKLOG_BUY rule BEFORE AVOID_faE so it can fire on E tier too
    "WHEN fa_tier = 'E' THEN 'AVOID_faE'",
    "WHEN icb = 8633.0 AND adv_yoy > 0.5 AND fa_tier IN ('C','D','E') AND ta >= 90 THEN 'RE_BACKLOG_BUY'\n"
    "    WHEN fa_tier = 'E' THEN 'AVOID_faE'"
)

# Canonical config (mirrors compare_ba_canonical_v4_vs_v5.py)
TIER_BAL_V4 = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
TIER_BAL_RE = TIER_BAL_V4 + ["RE_BACKLOG_BUY"]
OOS_START = pd.Timestamp("2024-01-01")

def run_canonical(label, sig_query, tier_set):
    print(f"\n{'='*70}\n  RUN: {label} (tiers={tier_set})\n{'='*70}")
    print("Loading signals + prices ...")
    sig = bq(sig_query.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"  {len(sig):,} signal rows")
    n_re_bk = (sig["play_type"] == "RE_BACKLOG_BUY").sum()
    print(f"  RE_BACKLOG_BUY signal rows: {n_re_bk:,}")

    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

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

    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    print("  Simulating BAL+Fin/RE-max-4 (50B) ...")
    nav_bal, trades_bal = simulate(sig, prices, vni_dates,
        allowed_tiers=tier_set, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    print("  Simulating VN30_BAL (50B) ...")
    sig_vn30 = sig[sig["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=tier_set, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    ba_nav.name = "ba_nav"
    return ba_nav, vni, trades_bal, trades_vn30

def window_metrics(nav, start, end, label):
    sub = nav[(nav.index >= start) & (nav.index <= end)]
    if len(sub) < 30:
        return {"label": label, "n": len(sub), "cagr_pct": np.nan,
                "sharpe": np.nan, "max_dd_pct": np.nan, "calmar": np.nan, "wealth_x": np.nan}
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (sub - sub.cummax()) / sub.cummax()
    mdd = dd.min()
    cal = cagr / abs(mdd) if mdd < 0 else 0
    return {"label": label, "n": len(sub),
            "cagr_pct": cagr*100, "sharpe": sharpe,
            "max_dd_pct": mdd*100, "calmar": cal,
            "wealth_x": sub.iloc[-1] / sub.iloc[0]}

def vni_metrics_window(vni, start, end, label):
    sub = vni[(vni["time"] >= start) & (vni["time"] <= end)].copy()
    if len(sub) < 30: return None
    sub["nav"] = sub["Close"] / sub["Close"].iloc[0]
    nav = sub.set_index("time")["nav"]
    return window_metrics(nav, start, end, label)

print(f"Window: {START_DATE} -> {END_DATE}")
ba_v4,  vni, trades_v4_bal,  trades_v4_vn30  = run_canonical("v4_baseline",      V4_QUERY,    TIER_BAL_V4)
ba_v4r, _,   trades_v4r_bal, trades_v4r_vn30 = run_canonical("v4+RE_BACKLOG",    V4_RE_QUERY, TIER_BAL_RE)

periods = [
    ("FULL_PERIOD (2014-2026)", ba_v4.index.min(), ba_v4.index.max()),
    ("OOS_2024_2026",            OOS_START,         ba_v4.index.max()),
    ("OOS_2022_2026 (4y)",       pd.Timestamp("2022-01-01"), ba_v4.index.max()),
]

print("\n" + "="*100)
print("  BA-SYSTEM CANONICAL — v4 baseline vs v4+RE_BACKLOG_BUY")
print("="*100)
hdr = f"{'Period':<26}{'Variant':<18}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}"
print(hdr); print("-"*len(hdr))

rows = []
for label, st, en in periods:
    m4  = window_metrics(ba_v4,  st, en, f"{label}_v4")
    m4r = window_metrics(ba_v4r, st, en, f"{label}_v4r")
    vm  = vni_metrics_window(vni, st, en, f"{label}_VNI")
    print(f"{label:<26}{'v4_baseline':<18}{m4['cagr_pct']:>8.2f}{m4['sharpe']:>8.2f}"
          f"{m4['max_dd_pct']:>9.1f}{m4['calmar']:>8.2f}{m4['wealth_x']:>8.2f}")
    print(f"{label:<26}{'v4+RE_BACKLOG':<18}{m4r['cagr_pct']:>8.2f}{m4r['sharpe']:>8.2f}"
          f"{m4r['max_dd_pct']:>9.1f}{m4r['calmar']:>8.2f}{m4r['wealth_x']:>8.2f}")
    print(f"{label:<26}{'Delta':<18}"
          f"{m4r['cagr_pct']-m4['cagr_pct']:>+8.2f}"
          f"{m4r['sharpe']-m4['sharpe']:>+8.2f}"
          f"{m4r['max_dd_pct']-m4['max_dd_pct']:>+9.1f}"
          f"{m4r['calmar']-m4['calmar']:>+8.2f}"
          f"{m4r['wealth_x']-m4['wealth_x']:>+8.2f}")
    if vm:
        print(f"{label:<26}{'VNINDEX_BH':<18}{vm['cagr_pct']:>8.2f}{vm['sharpe']:>8.2f}"
              f"{vm['max_dd_pct']:>9.1f}{vm['calmar']:>8.2f}{vm['wealth_x']:>8.2f}")
    print()
    rows.append({"period": label, "v4_cagr": m4["cagr_pct"], "v4re_cagr": m4r["cagr_pct"],
                 "v4_sharpe": m4["sharpe"], "v4re_sharpe": m4r["sharpe"],
                 "v4_mdd": m4["max_dd_pct"], "v4re_mdd": m4r["max_dd_pct"]})

pd.DataFrame(rows).to_csv("ba_canonical_v4_vs_re_backlog.csv", index=False)
print("Saved ba_canonical_v4_vs_re_backlog.csv")

print("\nTrade counts:")
print(f"  v4:            BAL={len(trades_v4_bal):4d}  VN30={len(trades_v4_vn30):4d}  total={len(trades_v4_bal)+len(trades_v4_vn30)}")
print(f"  v4+RE_BACKLOG: BAL={len(trades_v4r_bal):4d}  VN30={len(trades_v4r_vn30):4d}  total={len(trades_v4r_bal)+len(trades_v4r_vn30)}")

# Drill: which RE_BACKLOG_BUY trades fired and what was their PnL?
re_bk_trades = trades_v4r_bal[trades_v4r_bal["play_type"] == "RE_BACKLOG_BUY"].copy() if "play_type" in trades_v4r_bal.columns else pd.DataFrame()
if len(re_bk_trades):
    print(f"\n  RE_BACKLOG_BUY trades in BAL leg: {len(re_bk_trades)}")
    pnl_col = "pnl_pct" if "pnl_pct" in re_bk_trades.columns else ("return_pct" if "return_pct" in re_bk_trades.columns else None)
    if pnl_col:
        print(f"  Mean PnL: {re_bk_trades[pnl_col].mean():.2f}%  Median: {re_bk_trades[pnl_col].median():.2f}%  WR: {(re_bk_trades[pnl_col]>0).mean()*100:.1f}%")
    re_bk_trades.to_csv("re_backlog_trades.csv", index=False)
    print("  Saved re_backlog_trades.csv")
else:
    print("\n  (No RE_BACKLOG_BUY trades fired — signal may be too restrictive)")
