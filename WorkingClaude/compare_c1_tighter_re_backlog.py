#!/usr/bin/env python3
"""
compare_c1_tighter_re_backlog.py
================================
C1 hypothesis: B2 failed due to slot contention, NOT bad signal.
RE_BACKLOG_BUY had +5.81% mean expectancy but displaced higher-quality trades.

Two variants tested:
  C1a: TIGHTER signal, max_positions=10 (unchanged)
        - Drop fa_tier='E' (only C/D)
        - ta >= 120 (was 90)
        - state5 IN (3,4,5) (skip BEAR/CRISIS)
        - np_yoy > 0 OR rev_yoy > 0 (avoid mua đỉnh khi earnings rớt)
  C1b: TIGHTER signal + RELAXED slots (max_positions=20, per-pos cap 10% NAV)
        - User's idea: don't cap slot count, cap per-position size at NAV/10
        - Implementation: tier_weights={tier: 0.10 for all} + max_positions=20

Both compared against v4 baseline (fa_ratings, max_positions=10).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, re as _re
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate, bq, VNI_QUERY, START_DATE, END_DATE

shn.TIER_PRIORITY["RE_BACKLOG_BUY"] = 55

# ─── SIGNAL_V10 base + VNINDEX patch ──────────────────────────────────────────
with open(os.path.join(WORKDIR, "test_round14_stability.py"), encoding="utf-8") as _f:
    _src = _f.read()
_m = _re.search(r'SIGNAL_V10\s*=\s*"""(.+?)"""', _src, _re.DOTALL)
SIGNAL_V10_BASE = _m.group(0).split('"""', 1)[1].rsplit('"""', 1)[0]
SIGNAL_V10_BASE = SIGNAL_V10_BASE.replace(
    "CASE WHEN t.VNINDEX_RSI_Max3M > 0.65 THEN 10 ELSE 0 END",
    "CASE WHEN FALSE THEN 10 ELSE 0 END")

V4_QUERY = SIGNAL_V10_BASE

# v4 + TIGHTER RE_BACKLOG (C1)
V4_RE_QUERY = SIGNAL_V10_BASE.replace(
    "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,",
    "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,\n"
    "    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4, 0)) - 1 AS adv_yoy,"
).replace(
    "fin.Revenue_YoY_P0 AS rev_yoy,",
    "fin.Revenue_YoY_P0 AS rev_yoy, fin.adv_yoy AS adv_yoy, t.ICB_Code AS icb,"
).replace(
    "WHEN fa_tier = 'E' THEN 'AVOID_faE'",
    # C1 TIGHTER: drop E, ta>=120, state in (3,4,5), require earnings momentum
    "WHEN icb = 8633.0 AND adv_yoy > 0.5 AND fa_tier IN ('C','D') "
    "AND ta >= 120 AND state5 IN (3,4,5) AND (np_yoy > 0 OR rev_yoy > 0) "
    "THEN 'RE_BACKLOG_BUY'\n"
    "    WHEN fa_tier = 'E' THEN 'AVOID_faE'"
)

TIER_BAL_V4 = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
TIER_BAL_RE = TIER_BAL_V4 + ["RE_BACKLOG_BUY"]
OOS_START = pd.Timestamp("2024-01-01")

def run_canonical(label, sig_query, tier_set, max_positions=10, per_pos_weight=None):
    print(f"\n{'='*70}\n  RUN: {label} (max_pos={max_positions}, "
          f"per_pos_w={per_pos_weight})\n{'='*70}")
    sig = bq(sig_query.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    n_re_bk = (sig["play_type"] == "RE_BACKLOG_BUY").sum()
    print(f"  {len(sig):,} signal rows, RE_BACKLOG_BUY={n_re_bk:,}")

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

    # If per_pos_weight set, build tier_weights for all tiers in tier_set
    tw = {t: per_pos_weight for t in tier_set} if per_pos_weight else None

    print("  Sim BAL ...")
    nav_bal, trades_bal = simulate(sig, prices, vni_dates,
        allowed_tiers=tier_set, max_positions=max_positions, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        tier_weights=tw, **LIQ_FULL)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    print("  Sim VN30 ...")
    sig_vn30 = sig[sig["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=tier_set, max_positions=max_positions, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=0.001, init_nav=50e9,
        tier_weights=tw, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    return ba_nav, vni, trades_bal, trades_vn30

def window_metrics(nav, start, end):
    sub = nav[(nav.index >= start) & (nav.index <= end)]
    if len(sub) < 30: return dict(cagr_pct=np.nan, sharpe=np.nan, max_dd_pct=np.nan, calmar=np.nan, wealth_x=np.nan)
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (sub - sub.cummax()) / sub.cummax(); mdd = dd.min()
    return dict(cagr_pct=cagr*100, sharpe=sharpe, max_dd_pct=mdd*100,
                calmar=cagr/abs(mdd) if mdd<0 else 0, wealth_x=sub.iloc[-1]/sub.iloc[0])

def vni_metrics_window(vni, start, end):
    sub = vni[(vni["time"] >= start) & (vni["time"] <= end)].copy()
    if len(sub) < 30: return None
    sub["nav"] = sub["Close"] / sub["Close"].iloc[0]
    return window_metrics(sub.set_index("time")["nav"], start, end)

print(f"Window: {START_DATE} -> {END_DATE}\n")
ba_v4,  vni, tr_v4_bal,  tr_v4_vn30  = run_canonical("v4_baseline",  V4_QUERY,    TIER_BAL_V4, max_positions=10, per_pos_weight=None)
ba_c1a, _,   tr_c1a_bal, tr_c1a_vn30 = run_canonical("C1a_tight10",  V4_RE_QUERY, TIER_BAL_RE, max_positions=10, per_pos_weight=None)
ba_c1b, _,   tr_c1b_bal, tr_c1b_vn30 = run_canonical("C1b_tight20",  V4_RE_QUERY, TIER_BAL_RE, max_positions=20, per_pos_weight=0.10)

periods = [
    ("FULL_PERIOD (2014-2026)", ba_v4.index.min(), ba_v4.index.max()),
    ("OOS_2024_2026",            OOS_START,         ba_v4.index.max()),
    ("OOS_2022_2026 (4y)",       pd.Timestamp("2022-01-01"), ba_v4.index.max()),
]

print("\n" + "="*108)
print("  BA-SYSTEM CANONICAL — v4 vs C1a (tight+max=10) vs C1b (tight+max=20+10%/pos)")
print("="*108)
hdr = f"{'Period':<26}{'Variant':<18}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}"
print(hdr); print("-"*len(hdr))

for label, st, en in periods:
    m4  = window_metrics(ba_v4,  st, en)
    m1a = window_metrics(ba_c1a, st, en)
    m1b = window_metrics(ba_c1b, st, en)
    vm  = vni_metrics_window(vni, st, en)
    for var, m in [("v4_baseline", m4), ("C1a_tight10", m1a), ("C1b_tight20", m1b)]:
        print(f"{label:<26}{var:<18}{m['cagr_pct']:>8.2f}{m['sharpe']:>8.2f}"
              f"{m['max_dd_pct']:>9.1f}{m['calmar']:>8.2f}{m['wealth_x']:>8.2f}")
    print(f"{label:<26}{'Δ C1a-v4':<18}"
          f"{m1a['cagr_pct']-m4['cagr_pct']:>+8.2f}{m1a['sharpe']-m4['sharpe']:>+8.2f}"
          f"{m1a['max_dd_pct']-m4['max_dd_pct']:>+9.1f}{m1a['calmar']-m4['calmar']:>+8.2f}"
          f"{m1a['wealth_x']-m4['wealth_x']:>+8.2f}")
    print(f"{label:<26}{'Δ C1b-v4':<18}"
          f"{m1b['cagr_pct']-m4['cagr_pct']:>+8.2f}{m1b['sharpe']-m4['sharpe']:>+8.2f}"
          f"{m1b['max_dd_pct']-m4['max_dd_pct']:>+9.1f}{m1b['calmar']-m4['calmar']:>+8.2f}"
          f"{m1b['wealth_x']-m4['wealth_x']:>+8.2f}")
    if vm:
        print(f"{label:<26}{'VNINDEX_BH':<18}{vm['cagr_pct']:>8.2f}{vm['sharpe']:>8.2f}"
              f"{vm['max_dd_pct']:>9.1f}{vm['calmar']:>8.2f}{vm['wealth_x']:>8.2f}")
    print()

print("Trade counts:")
print(f"  v4:           BAL={len(tr_v4_bal):4d}  VN30={len(tr_v4_vn30):4d}  total={len(tr_v4_bal)+len(tr_v4_vn30)}")
print(f"  C1a_tight10:  BAL={len(tr_c1a_bal):4d}  VN30={len(tr_c1a_vn30):4d}  total={len(tr_c1a_bal)+len(tr_c1a_vn30)}")
print(f"  C1b_tight20:  BAL={len(tr_c1b_bal):4d}  VN30={len(tr_c1b_vn30):4d}  total={len(tr_c1b_bal)+len(tr_c1b_vn30)}")

# Drill RE_BACKLOG trades in C1a
for label, df in [("C1a", tr_c1a_bal), ("C1b", tr_c1b_bal)]:
    rebk = df[df["play_type"] == "RE_BACKLOG_BUY"] if "play_type" in df.columns else pd.DataFrame()
    if len(rebk):
        print(f"\n  {label} RE_BACKLOG_BUY trades (BAL): n={len(rebk)}, "
              f"mean_ret_net={rebk['ret_net'].mean()*100:+.2f}%, "
              f"WR={(rebk['ret_net']>0).mean()*100:.1f}%")
        rebk.to_csv(f"re_backlog_trades_{label}.csv", index=False)
