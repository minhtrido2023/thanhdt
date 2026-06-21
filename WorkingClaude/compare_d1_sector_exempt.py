#!/usr/bin/env python3
"""
compare_d1_sector_exempt.py
===========================
D1 hypothesis: in C1a, RE_BACKLOG_BUY was still competing for the 4-slot
sector-8 cap with banks/securities. Exempt it from the cap so it can fire
as ADDITIONAL slots beyond the standard 4.

Variants:
  v4_baseline    — production reference
  C1a            — C1a tight, no exemption (slot competition with banks)
  D1_exempt      — C1a tight + RE_BACKLOG exempt from sector-8 cap
  D1_exempt_cap6 — D1 + global sector-8 cap raised to 6 (extra safety)
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

# SIGNAL_V10 base + patches
with open(os.path.join(WORKDIR, "test_round14_stability.py"), encoding="utf-8") as _f:
    _src = _f.read()
_m = _re.search(r'SIGNAL_V10\s*=\s*"""(.+?)"""', _src, _re.DOTALL)
SIGNAL_V10_BASE = _m.group(0).split('"""', 1)[1].rsplit('"""', 1)[0]
SIGNAL_V10_BASE = SIGNAL_V10_BASE.replace(
    "CASE WHEN t.VNINDEX_RSI_Max3M > 0.65 THEN 10 ELSE 0 END",
    "CASE WHEN FALSE THEN 10 ELSE 0 END")

V4_QUERY = SIGNAL_V10_BASE
V4_RE_QUERY = SIGNAL_V10_BASE.replace(
    "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,",
    "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,\n"
    "    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4, 0)) - 1 AS adv_yoy,"
).replace(
    "fin.Revenue_YoY_P0 AS rev_yoy,",
    "fin.Revenue_YoY_P0 AS rev_yoy, fin.adv_yoy AS adv_yoy, t.ICB_Code AS icb,"
).replace(
    "WHEN fa_tier = 'E' THEN 'AVOID_faE'",
    "WHEN icb = 8633.0 AND adv_yoy > 0.5 AND fa_tier IN ('C','D') "
    "AND ta >= 120 AND state5 IN (3,4,5) AND (np_yoy > 0 OR rev_yoy > 0) "
    "THEN 'RE_BACKLOG_BUY'\n"
    "    WHEN fa_tier = 'E' THEN 'AVOID_faE'"
)

TIER_BAL_V4 = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
TIER_BAL_RE = TIER_BAL_V4 + ["RE_BACKLOG_BUY"]
OOS_START = pd.Timestamp("2024-01-01")

def run(label, sig_query, tier_set, sector_cap=4, exempt=None):
    print(f"\n{'='*70}\n  RUN: {label}  (sec8_cap={sector_cap}, exempt={exempt})\n{'='*70}")
    sig = bq(sig_query.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    n_re = (sig["play_type"] == "RE_BACKLOG_BUY").sum()
    print(f"  {len(sig):,} rows, RE_BACKLOG_BUY={n_re:,}")

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

    LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
           "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    print("  Sim BAL ...")
    nav_bal, tr_bal = simulate(sig, prices, vni_dates,
        allowed_tiers=tier_set, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: sector_cap}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=exempt, **LIQ)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    print("  Sim VN30 ...")
    sig_vn30 = sig[sig["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ, "liquidity_lookup": liq_vn30}
    nav_vn30, tr_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=tier_set, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_cap_exempt_tiers=exempt, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    return ba_nav, vni, tr_bal, tr_vn30

def wm(nav, st, en):
    sub = nav[(nav.index >= st) & (nav.index <= en)]
    if len(sub) < 30: return dict(cagr_pct=np.nan, sharpe=np.nan, max_dd_pct=np.nan, calmar=np.nan, wealth_x=np.nan)
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (sub - sub.cummax()) / sub.cummax(); mdd = dd.min()
    return dict(cagr_pct=cagr*100, sharpe=sharpe, max_dd_pct=mdd*100,
                calmar=cagr/abs(mdd) if mdd<0 else 0, wealth_x=sub.iloc[-1]/sub.iloc[0])

def vni_wm(vni, st, en):
    sub = vni[(vni["time"] >= st) & (vni["time"] <= en)].copy()
    if len(sub) < 30: return None
    sub["nav"] = sub["Close"] / sub["Close"].iloc[0]
    return wm(sub.set_index("time")["nav"], st, en)

print(f"Window: {START_DATE} -> {END_DATE}\n")
ba_v4,   vni, tr_v4_b,   tr_v4_v   = run("v4_baseline",     V4_QUERY,    TIER_BAL_V4, sector_cap=4, exempt=None)
ba_c1a,  _,   tr_c1a_b,  tr_c1a_v  = run("C1a",             V4_RE_QUERY, TIER_BAL_RE, sector_cap=4, exempt=None)
ba_d1,   _,   tr_d1_b,   tr_d1_v   = run("D1_exempt",       V4_RE_QUERY, TIER_BAL_RE, sector_cap=4, exempt={"RE_BACKLOG_BUY"})
ba_d1c6, _,   tr_d1c6_b, tr_d1c6_v = run("D1_exempt_cap6",  V4_RE_QUERY, TIER_BAL_RE, sector_cap=6, exempt={"RE_BACKLOG_BUY"})

periods = [
    ("FULL_PERIOD (2014-2026)", ba_v4.index.min(), ba_v4.index.max()),
    ("OOS_2024_2026",            OOS_START,         ba_v4.index.max()),
    ("OOS_2022_2026 (4y)",       pd.Timestamp("2022-01-01"), ba_v4.index.max()),
]

print("\n" + "="*108)
print("  BA-SYSTEM CANONICAL — D1 sector-cap exemption test")
print("="*108)
hdr = f"{'Period':<26}{'Variant':<18}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}"
print(hdr); print("-"*len(hdr))

for label, st, en in periods:
    m4 = wm(ba_v4, st, en); m1 = wm(ba_c1a, st, en); md = wm(ba_d1, st, en); mc = wm(ba_d1c6, st, en)
    vm = vni_wm(vni, st, en)
    for var, m in [("v4_baseline", m4), ("C1a", m1), ("D1_exempt", md), ("D1_cap6", mc)]:
        print(f"{label:<26}{var:<18}{m['cagr_pct']:>8.2f}{m['sharpe']:>8.2f}"
              f"{m['max_dd_pct']:>9.1f}{m['calmar']:>8.2f}{m['wealth_x']:>8.2f}")
    print(f"{label:<26}{'Δ D1-v4':<18}"
          f"{md['cagr_pct']-m4['cagr_pct']:>+8.2f}{md['sharpe']-m4['sharpe']:>+8.2f}"
          f"{md['max_dd_pct']-m4['max_dd_pct']:>+9.1f}{md['calmar']-m4['calmar']:>+8.2f}"
          f"{md['wealth_x']-m4['wealth_x']:>+8.2f}")
    print(f"{label:<26}{'Δ D1cap6-v4':<18}"
          f"{mc['cagr_pct']-m4['cagr_pct']:>+8.2f}{mc['sharpe']-m4['sharpe']:>+8.2f}"
          f"{mc['max_dd_pct']-m4['max_dd_pct']:>+9.1f}{mc['calmar']-m4['calmar']:>+8.2f}"
          f"{mc['wealth_x']-m4['wealth_x']:>+8.2f}")
    if vm:
        print(f"{label:<26}{'VNINDEX_BH':<18}{vm['cagr_pct']:>8.2f}{vm['sharpe']:>8.2f}"
              f"{vm['max_dd_pct']:>9.1f}{vm['calmar']:>8.2f}{vm['wealth_x']:>8.2f}")
    print()

print("Trade counts:")
for name, b, v in [("v4", tr_v4_b, tr_v4_v), ("C1a", tr_c1a_b, tr_c1a_v),
                   ("D1_exempt", tr_d1_b, tr_d1_v), ("D1_cap6", tr_d1c6_b, tr_d1c6_v)]:
    print(f"  {name:<14}BAL={len(b):4d}  VN30={len(v):4d}  total={len(b)+len(v)}")

# Drill RE_BACKLOG per variant
print()
for name, b in [("C1a", tr_c1a_b), ("D1_exempt", tr_d1_b), ("D1_cap6", tr_d1c6_b)]:
    rebk = b[b["play_type"] == "RE_BACKLOG_BUY"] if "play_type" in b.columns else pd.DataFrame()
    if len(rebk):
        print(f"  {name:<14}RE_BACKLOG BAL: n={len(rebk):3d}, mean={rebk['ret_net'].mean()*100:+.2f}%, "
              f"WR={(rebk['ret_net']>0).mean()*100:.1f}%, "
              f"STOPs={(rebk['reason']=='STOP').sum()}")
