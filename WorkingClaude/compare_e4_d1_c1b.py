#!/usr/bin/env python3
"""
compare_e4_d1_c1b.py
====================
E4: combine D1 (sector exempt) with user's max-positions idea.

C1b earlier: max_positions=20 + per_pos_weight=0.10 (uniform tier_weights)
  → standalone hurt OOS but helped FULL DD

E4 hypothesis: combining D1 (which has +alpha) with relaxed slots may
  amplify the diversification benefit without breaking OOS.

Variants:
  v4_baseline
  D1            — D1_exempt baseline (already winner)
  D1+slot15     — D1 + max_positions=15, per_pos_weight=0.10
  D1+slot20     — D1 + max_positions=20, per_pos_weight=0.10
  D1+slotState  — D1 + state-conditional: max=15 in state {1,2,3}, =10 in {4,5}
                  (Easier impl: just use max=15 uniform, since BEAR/CRISIS already
                  blocked by AVOID_bear; the relaxation effectively kicks in NEUTRAL+)
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

TIER_BAL_V4 = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
TIER_BAL_RE = TIER_BAL_V4 + ["RE_BACKLOG_BUY"]
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

def run(label, sig_query, tier_set, exempt=None, max_pos=10, per_pos_w=None):
    print(f"  {label} (max_pos={max_pos}, per_pos_w={per_pos_w}) ...")
    sig = bq(sig_query.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
    LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
           "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
    tw = {t: per_pos_w for t in tier_set} if per_pos_w else None

    nav_bal, tr_bal = simulate(sig, prices, _vni_dates,
        allowed_tiers=tier_set, max_positions=max_pos, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=_sec_map,
        sector_cap_exempt_tiers=exempt, tier_weights=tw, **LIQ)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    sig_vn30 = sig[sig["ticker"].isin(_top30)]
    prices_vn30 = {tk: prices[tk] for tk in _top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in _top30}
    LIQ_VN30 = {**LIQ, "liquidity_lookup": liq_vn30}
    nav_vn30, tr_vn30 = simulate(sig_vn30, prices_vn30, _vni_dates,
        allowed_tiers=tier_set, max_positions=max_pos, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_cap_exempt_tiers=exempt, tier_weights=tw, **LIQ_VN30)
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
ba_v4,  tr_v4b,  tr_v4v  = run("v4_baseline", V4_QUERY,    TIER_BAL_V4, max_pos=10)
ba_d1,  tr_d1b,  tr_d1v  = run("D1",          V4_RE_QUERY, TIER_BAL_RE, exempt={"RE_BACKLOG_BUY"}, max_pos=10)
ba_d15, tr_d15b, tr_d15v = run("D1+slot15",   V4_RE_QUERY, TIER_BAL_RE, exempt={"RE_BACKLOG_BUY"}, max_pos=15, per_pos_w=0.10)
ba_d20, tr_d20b, tr_d20v = run("D1+slot20",   V4_RE_QUERY, TIER_BAL_RE, exempt={"RE_BACKLOG_BUY"}, max_pos=20, per_pos_w=0.10)
ba_d12, tr_d12b, tr_d12v = run("D1+slot12",   V4_RE_QUERY, TIER_BAL_RE, exempt={"RE_BACKLOG_BUY"}, max_pos=12, per_pos_w=0.10)

periods = [
    ("FULL_PERIOD", ba_v4.index.min(), ba_v4.index.max()),
    ("OOS_2024_2026", OOS_START, ba_v4.index.max()),
    ("OOS_2022_2026", pd.Timestamp("2022-01-01"), ba_v4.index.max()),
]

print("\n" + "="*100)
print("  E4 RESULTS — D1 combined with relaxed slots (user's idea)")
print("="*100)
hdr = f"{'Period':<16}{'Variant':<14}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'ΔvsV4':>8}"
print(hdr); print("-"*len(hdr))

for label, st, en in periods:
    m4 = wm(ba_v4, st, en); m1 = wm(ba_d1, st, en); m15 = wm(ba_d15, st, en)
    m20 = wm(ba_d20, st, en); m12 = wm(ba_d12, st, en)
    for var, m in [("v4_baseline",m4), ("D1",m1), ("D1+slot12",m12), ("D1+slot15",m15), ("D1+slot20",m20)]:
        delta = m["cagr_pct"] - m4["cagr_pct"]
        print(f"{label:<16}{var:<14}{m['cagr_pct']:>8.2f}{m['sharpe']:>8.2f}"
              f"{m['max_dd_pct']:>9.1f}{m['calmar']:>8.2f}{delta:>+8.2f}")
    print()

print("Trade counts:")
for nm, b, v in [("v4",tr_v4b,tr_v4v), ("D1",tr_d1b,tr_d1v),
                 ("D1+slot12",tr_d12b,tr_d12v), ("D1+slot15",tr_d15b,tr_d15v),
                 ("D1+slot20",tr_d20b,tr_d20v)]:
    print(f"  {nm:<14}BAL={len(b):4d} VN30={len(v):4d} tot={len(b)+len(v)}")
