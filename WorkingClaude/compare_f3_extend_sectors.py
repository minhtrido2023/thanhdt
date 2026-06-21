#!/usr/bin/env python3
"""
compare_f3_extend_sectors.py
============================
F3: extend RE_BACKLOG logic to Construction (ICB 2357) and optionally
RE Services (8637). Both have meaningful AdvCust/Revenue ratios and
similar revenue-recognition lag patterns.

Two new tiers added:
  CONSTR_BACKLOG_BUY — ICB 2357 with advance billing surge
  RES_BACKLOG_BUY    — ICB 8637 (RE brokers/services, small universe)

Same criteria as RE_BACKLOG: adv_yoy>0.5, fa_tier IN ('C','D'), ta>=120,
state5 IN (3,4,5), (np_yoy>0 OR rev_yoy>0). All exempt from sector caps.

Compared against D1 (RE only) baseline.
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
shn.TIER_PRIORITY["RE_BACKLOG_BUY"]     = 55
shn.TIER_PRIORITY["CONSTR_BACKLOG_BUY"] = 50  # slightly lower (sector 2 is more cyclical/risky)
shn.TIER_PRIORITY["RES_BACKLOG_BUY"]    = 45

with open(os.path.join(WORKDIR, "test_round14_stability.py"), encoding="utf-8") as _f:
    _src = _f.read()
_m = _re.search(r'SIGNAL_V10\s*=\s*"""(.+?)"""', _src, _re.DOTALL)
SIGNAL_V10_BASE = _m.group(0).split('"""', 1)[1].rsplit('"""', 1)[0]
SIGNAL_V10_BASE = SIGNAL_V10_BASE.replace(
    "CASE WHEN t.VNINDEX_RSI_Max3M > 0.65 THEN 10 ELSE 0 END",
    "CASE WHEN FALSE THEN 10 ELSE 0 END")

V4_QUERY = SIGNAL_V10_BASE

# Common FA backbone modifications: AdvCust YoY + icb passthrough
_FA_MOD = SIGNAL_V10_BASE.replace(
    "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,",
    "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,\n"
    "    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4, 0)) - 1 AS adv_yoy,"
).replace(
    "fin.Revenue_YoY_P0 AS rev_yoy,",
    "fin.Revenue_YoY_P0 AS rev_yoy, fin.adv_yoy AS adv_yoy, t.ICB_Code AS icb,"
)

# D1 (RE only) — for reference
D1_RULE = ("WHEN icb = 8633.0 AND adv_yoy > 0.5 AND fa_tier IN ('C','D') "
           "AND ta >= 120 AND state5 IN (3,4,5) AND (np_yoy > 0 OR rev_yoy > 0) "
           "THEN 'RE_BACKLOG_BUY'\n"
           "    WHEN fa_tier = 'E' THEN 'AVOID_faE'")
D1_QUERY = _FA_MOD.replace("WHEN fa_tier = 'E' THEN 'AVOID_faE'", D1_RULE)

# F3a: D1 + Construction (2357)
F3A_RULE = ("WHEN icb = 8633.0 AND adv_yoy > 0.5 AND fa_tier IN ('C','D') "
            "AND ta >= 120 AND state5 IN (3,4,5) AND (np_yoy > 0 OR rev_yoy > 0) "
            "THEN 'RE_BACKLOG_BUY'\n"
            "    WHEN icb = 2357.0 AND adv_yoy > 0.5 AND fa_tier IN ('C','D') "
            "AND ta >= 120 AND state5 IN (3,4,5) AND (np_yoy > 0 OR rev_yoy > 0) "
            "THEN 'CONSTR_BACKLOG_BUY'\n"
            "    WHEN fa_tier = 'E' THEN 'AVOID_faE'")
F3A_QUERY = _FA_MOD.replace("WHEN fa_tier = 'E' THEN 'AVOID_faE'", F3A_RULE)

# F3b: D1 + Construction + RE Services (8637)
F3B_RULE = F3A_RULE.replace(
    "WHEN fa_tier = 'E' THEN 'AVOID_faE'",
    "WHEN icb = 8637.0 AND adv_yoy > 0.5 AND fa_tier IN ('C','D') "
    "AND ta >= 120 AND state5 IN (3,4,5) AND (np_yoy > 0 OR rev_yoy > 0) "
    "THEN 'RES_BACKLOG_BUY'\n"
    "    WHEN fa_tier = 'E' THEN 'AVOID_faE'"
)
F3B_QUERY = _FA_MOD.replace("WHEN fa_tier = 'E' THEN 'AVOID_faE'", F3B_RULE)

TIER_BAL_V4 = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
TIER_BAL_D1 = TIER_BAL_V4 + ["RE_BACKLOG_BUY"]
TIER_BAL_F3A = TIER_BAL_D1 + ["CONSTR_BACKLOG_BUY"]
TIER_BAL_F3B = TIER_BAL_F3A + ["RES_BACKLOG_BUY"]
EXEMPT_F3A = {"RE_BACKLOG_BUY", "CONSTR_BACKLOG_BUY"}
EXEMPT_F3B = {"RE_BACKLOG_BUY", "CONSTR_BACKLOG_BUY", "RES_BACKLOG_BUY"}
OOS_START = pd.Timestamp("2024-01-01")

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

def run(label, sig_query, tier_set, exempt):
    print(f"  {label} ...")
    sig = bq(sig_query.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    n_re = (sig["play_type"] == "RE_BACKLOG_BUY").sum()
    n_co = (sig["play_type"] == "CONSTR_BACKLOG_BUY").sum()
    n_rs = (sig["play_type"] == "RES_BACKLOG_BUY").sum()
    print(f"    signals: RE={n_re} CONSTR={n_co} RES={n_rs}")
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
    LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
           "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    nav_bal, tr_bal = simulate(sig, prices, _vni_dates,
        allowed_tiers=tier_set, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=_sec_map,
        sector_cap_exempt_tiers=exempt, **LIQ)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    sig_vn30 = sig[sig["ticker"].isin(_top30)]
    prices_vn30 = {tk: prices[tk] for tk in _top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in _top30}
    LIQ_VN30 = {**LIQ, "liquidity_lookup": liq_vn30}
    nav_vn30, tr_vn30 = simulate(sig_vn30, prices_vn30, _vni_dates,
        allowed_tiers=tier_set, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_cap_exempt_tiers=exempt, **LIQ_VN30)
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

print(f"\nWindow: {START_DATE} -> {END_DATE}\nRunning variants:")
ba_v4,  tr_v4b,  tr_v4v  = run("v4",      V4_QUERY,  TIER_BAL_V4, None)
ba_d1,  tr_d1b,  tr_d1v  = run("D1_RE",   D1_QUERY,  TIER_BAL_D1, {"RE_BACKLOG_BUY"})
ba_3a,  tr_3ab,  tr_3av  = run("F3a_+CO", F3A_QUERY, TIER_BAL_F3A, EXEMPT_F3A)
ba_3b,  tr_3bb,  tr_3bv  = run("F3b_+RS", F3B_QUERY, TIER_BAL_F3B, EXEMPT_F3B)

periods = [
    ("FULL_PERIOD", ba_v4.index.min(), ba_v4.index.max()),
    ("OOS_2024_2026", OOS_START, ba_v4.index.max()),
    ("OOS_2022_2026", pd.Timestamp("2022-01-01"), ba_v4.index.max()),
]

print("\n" + "="*100)
print("  F3 RESULTS — extend AdvCust signal to Construction (2357) + RE Services (8637)")
print("="*100)
hdr = f"{'Period':<16}{'Variant':<14}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'ΔvsV4':>8}{'ΔvsD1':>8}"
print(hdr); print("-"*len(hdr))

for label, st, en in periods:
    m4 = wm(ba_v4, st, en); m1 = wm(ba_d1, st, en)
    ma = wm(ba_3a, st, en); mb = wm(ba_3b, st, en)
    for var, m in [("v4",m4), ("D1_RE",m1), ("F3a_+CO",ma), ("F3b_+RS",mb)]:
        dv4 = m["cagr_pct"] - m4["cagr_pct"]
        dd1 = m["cagr_pct"] - m1["cagr_pct"]
        print(f"{label:<16}{var:<14}{m['cagr_pct']:>8.2f}{m['sharpe']:>8.2f}"
              f"{m['max_dd_pct']:>9.1f}{m['calmar']:>8.2f}{dv4:>+8.2f}{dd1:>+8.2f}")
    print()

print("Trade counts + per-tier breakdown:")
for nm, b, v in [("v4",tr_v4b,tr_v4v), ("D1_RE",tr_d1b,tr_d1v),
                 ("F3a_+CO",tr_3ab,tr_3av), ("F3b_+RS",tr_3bb,tr_3bv)]:
    re_n = (b["play_type"]=="RE_BACKLOG_BUY").sum() if "play_type" in b.columns else 0
    co_n = (b["play_type"]=="CONSTR_BACKLOG_BUY").sum() if "play_type" in b.columns else 0
    rs_n = (b["play_type"]=="RES_BACKLOG_BUY").sum() if "play_type" in b.columns else 0
    re_mn = b[b["play_type"]=="RE_BACKLOG_BUY"]["ret_net"].mean()*100 if re_n else 0
    co_mn = b[b["play_type"]=="CONSTR_BACKLOG_BUY"]["ret_net"].mean()*100 if co_n else 0
    rs_mn = b[b["play_type"]=="RES_BACKLOG_BUY"]["ret_net"].mean()*100 if rs_n else 0
    print(f"  {nm:<10}BAL={len(b):4d} VN30={len(v):4d} | RE_n={re_n:3d} mn={re_mn:+.1f}%  "
          f"CO_n={co_n:3d} mn={co_mn:+.1f}%  RS_n={rs_n:3d} mn={rs_mn:+.1f}%")

# Save CONSTR trades for inspection
co_trades = tr_3bb[tr_3bb["play_type"] == "CONSTR_BACKLOG_BUY"].copy() if "play_type" in tr_3bb.columns else pd.DataFrame()
if len(co_trades):
    co_trades.to_csv("constr_backlog_trades.csv", index=False)
    print(f"\n  Saved constr_backlog_trades.csv ({len(co_trades)} rows)")
