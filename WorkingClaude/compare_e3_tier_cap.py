#!/usr/bin/env python3
"""
compare_e3_tier_cap.py
======================
E3: D1_exempt revealed peak 11 concurrent sec-8 positions (2018-02-01).
Add per-tier concurrent cap for RE_BACKLOG_BUY to limit concentration.

Variants (reference D1 settings: adv>0.5, ta>=120, sector exempt):
  D1_uncapped  — current (no per-tier cap)
  D1_cap2      — max 2 RE_BACKLOG concurrent
  D1_cap3      — max 3 RE_BACKLOG concurrent
  D1_cap4      — max 4 RE_BACKLOG concurrent
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

# Cache common
print("Loading common inputs ...")
_vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
_vni["time"] = pd.to_datetime(_vni["time"])
_vni_dates = sorted(_vni["time"].unique())
_sec_map = bq("""SELECT DISTINCT t.ticker,
                CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                """).set_index("ticker")["s"].to_dict()
_top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
                WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                GROUP BY t.ticker
                ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

def run(label, sig_query, tier_set, exempt=None, tier_cap=None):
    print(f"  {label} (tier_cap={tier_cap}) ...")
    sig = bq(sig_query.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
    LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
           "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    nav_bal, tr_bal = simulate(sig, prices, _vni_dates,
        allowed_tiers=tier_set, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=_sec_map,
        sector_cap_exempt_tiers=exempt, tier_position_limit=tier_cap, **LIQ)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    sig_vn30 = sig[sig["ticker"].isin(_top30)]
    prices_vn30 = {tk: prices[tk] for tk in _top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in _top30}
    LIQ_VN30 = {**LIQ, "liquidity_lookup": liq_vn30}
    nav_vn30, tr_vn30 = simulate(sig_vn30, prices_vn30, _vni_dates,
        allowed_tiers=tier_set, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_cap_exempt_tiers=exempt, tier_position_limit=tier_cap, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    return ba_nav, tr_bal, tr_vn30

def wm(nav, st, en):
    sub = nav[(nav.index >= st) & (nav.index <= en)]
    if len(sub) < 30: return dict(cagr_pct=np.nan, sharpe=np.nan, max_dd_pct=np.nan, calmar=np.nan)
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (sub - sub.cummax()) / sub.cummax(); mdd = dd.min()
    return dict(cagr_pct=cagr*100, sharpe=sharpe, max_dd_pct=mdd*100,
                calmar=cagr/abs(mdd) if mdd<0 else 0)

def peak_concurrent_sec8(tr_bal):
    sec8_tk = {tk for tk, s in _sec_map.items() if s == 8}
    s8 = tr_bal[tr_bal["ticker"].isin(sec8_tk)].copy()
    if len(s8) == 0: return 0, None
    s8["entry_date"] = pd.to_datetime(s8["entry_date"])
    s8["exit_date"]  = pd.to_datetime(s8["exit_date"])
    ev = []
    for _, r in s8.iterrows():
        ev.append((r["entry_date"], 1)); ev.append((r["exit_date"], -1))
    ev.sort(); cur = 0; pk = 0; pk_d = None
    for d, delta in ev:
        cur += delta
        if cur > pk: pk = cur; pk_d = d
    return pk, pk_d

def peak_concurrent_tier(tr_bal, tier):
    rebk = tr_bal[tr_bal["play_type"] == tier].copy() if "play_type" in tr_bal.columns else pd.DataFrame()
    if len(rebk) == 0: return 0
    rebk["entry_date"] = pd.to_datetime(rebk["entry_date"])
    rebk["exit_date"]  = pd.to_datetime(rebk["exit_date"])
    ev = []
    for _, r in rebk.iterrows():
        ev.append((r["entry_date"], 1)); ev.append((r["exit_date"], -1))
    ev.sort(); cur = 0; pk = 0
    for d, delta in ev:
        cur += delta
        if cur > pk: pk = cur
    return pk

print(f"\nWindow: {START_DATE} -> {END_DATE}")
print("\nRunning variants:")
ba_v4,   tr_v4b,   tr_v4v   = run("v4_baseline", V4_QUERY,    TIER_BAL_V4)
ba_un,   tr_unb,   tr_unv   = run("D1_uncap",    V4_RE_QUERY, TIER_BAL_RE, exempt={"RE_BACKLOG_BUY"})
ba_c2,   tr_c2b,   tr_c2v   = run("D1_cap2",     V4_RE_QUERY, TIER_BAL_RE, exempt={"RE_BACKLOG_BUY"}, tier_cap={"RE_BACKLOG_BUY":2})
ba_c3,   tr_c3b,   tr_c3v   = run("D1_cap3",     V4_RE_QUERY, TIER_BAL_RE, exempt={"RE_BACKLOG_BUY"}, tier_cap={"RE_BACKLOG_BUY":3})
ba_c4,   tr_c4b,   tr_c4v   = run("D1_cap4",     V4_RE_QUERY, TIER_BAL_RE, exempt={"RE_BACKLOG_BUY"}, tier_cap={"RE_BACKLOG_BUY":4})

periods = [
    ("FULL_PERIOD", ba_v4.index.min(), ba_v4.index.max()),
    ("OOS_2024_2026", OOS_START, ba_v4.index.max()),
    ("OOS_2022_2026", pd.Timestamp("2022-01-01"), ba_v4.index.max()),
]

print("\n" + "="*100)
print("  E3 RESULTS — D1 with per-tier concurrent cap on RE_BACKLOG_BUY")
print("="*100)
hdr = f"{'Period':<16}{'Variant':<14}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'PeakRE':>8}{'PkSec8':>8}"
print(hdr); print("-"*len(hdr))

for label, st, en in periods:
    m4 = wm(ba_v4, st, en); m_un = wm(ba_un, st, en)
    m2 = wm(ba_c2, st, en); m3 = wm(ba_c3, st, en); m4c = wm(ba_c4, st, en)
    rows_to_print = [
        ("v4_baseline", m4, tr_v4b, "n/a"),
        ("D1_uncap", m_un, tr_unb, peak_concurrent_tier(tr_unb, "RE_BACKLOG_BUY")),
        ("D1_cap2", m2, tr_c2b, peak_concurrent_tier(tr_c2b, "RE_BACKLOG_BUY")),
        ("D1_cap3", m3, tr_c3b, peak_concurrent_tier(tr_c3b, "RE_BACKLOG_BUY")),
        ("D1_cap4", m4c, tr_c4b, peak_concurrent_tier(tr_c4b, "RE_BACKLOG_BUY")),
    ]
    for var, m, trb, pkre in rows_to_print:
        pks8, _ = peak_concurrent_sec8(trb)
        print(f"{label:<16}{var:<14}{m['cagr_pct']:>8.2f}{m['sharpe']:>8.2f}"
              f"{m['max_dd_pct']:>9.1f}{m['calmar']:>8.2f}"
              f"{str(pkre):>8}{pks8:>8}")
    print()

print("Trade counts:")
for nm, b, v in [("v4", tr_v4b, tr_v4v), ("D1_uncap", tr_unb, tr_unv),
                  ("D1_cap2", tr_c2b, tr_c2v), ("D1_cap3", tr_c3b, tr_c3v),
                  ("D1_cap4", tr_c4b, tr_c4v)]:
    pkre = peak_concurrent_tier(b, "RE_BACKLOG_BUY") if nm != "v4" else 0
    rebk_n = (b["play_type"] == "RE_BACKLOG_BUY").sum() if "play_type" in b.columns else 0
    rebk_mn = b[b["play_type"]=="RE_BACKLOG_BUY"]["ret_net"].mean()*100 if rebk_n else 0
    print(f"  {nm:<10}BAL={len(b):4d} VN30={len(v):4d} tot={len(b)+len(v):4d} | "
          f"RE_n={rebk_n:3d} RE_mn={rebk_mn:+.2f}% peak_RE={pkre}")
