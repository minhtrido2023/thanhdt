#!/usr/bin/env python3
"""
compare_k2_state_partial_exit.py
================================
K2: state-transition partial exit. Per memory, full state-exit was rejected
(round 17 -1.07pp CAGR). Test PARTIAL exit fractions (30/50/70%) to find
risk-cushion balance without cutting too much upside.

Variants (all on D1+slot12 base):
  D1+slot12 (no exit)
  K2_50_BEAR     = 50% exit when state goes to BEAR(2) or CRISIS(1)
  K2_50_BEAR_CR  = 50% exit on BEAR, 100% exit on CRISIS
  K2_30_BEAR_CR  = 30% exit on BEAR, 50% on CRISIS (milder)
  K2_50_NEUT     = 50% exit when state goes NEUTRAL(3) or lower (earliest signal)
  K2_70_BEAR     = 70% exit on BEAR (aggressive)

Existing simulate() infrastructure: state_by_date={date:state} +
state_exit_map={state:exit_fraction}. Each position triggered once per
exit threshold via partial_taken set.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, re as _re
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate, bq, VNI_QUERY

START_DATE = "2014-01-01"
END_DATE   = "2026-05-15"

with open(os.path.join(WORKDIR, "test_round14_stability.py"), encoding="utf-8") as _f:
    _src = _f.read()
_m = _re.search(r'SIGNAL_V10\s*=\s*"""(.+?)"""', _src, _re.DOTALL)
SIGNAL_V10_BASE = _m.group(0).split('"""', 1)[1].rsplit('"""', 1)[0]
SIGNAL_V10_BASE = SIGNAL_V10_BASE.replace(
    "CASE WHEN t.VNINDEX_RSI_Max3M > 0.65 THEN 10 ELSE 0 END",
    "CASE WHEN FALSE THEN 10 ELSE 0 END")

V4_QUERY = SIGNAL_V10_BASE
D1_QUERY = SIGNAL_V10_BASE.replace(
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
TIER_BAL_D1 = TIER_BAL_V4 + ["RE_BACKLOG_BUY"]
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

# Load state5 as dict {date: state}
print("Loading state5 timeline ...")
s5 = bq('SELECT time, state FROM `lithe-record-440915-m9.tav2_bq.vnindex_5state` ORDER BY time')
s5["time"] = pd.to_datetime(s5["time"])
# Forward-fill to all vni_dates (state5 may have gaps)
s5_idx = s5.set_index("time")["state"]
all_dates = pd.DatetimeIndex(_vni_dates)
state_by_date = s5_idx.reindex(all_dates, method="ffill").to_dict()
print(f"  {len(state_by_date)} dates with state data, "
      f"states distribution: {pd.Series(state_by_date).value_counts().sort_index().to_dict()}")

def run(label, sig_query, tier_set, exempt=None, max_pos=10, per_pos_w=None,
        state_exit_map=None):
    print(f"  {label} (exit_map={state_exit_map}) ...")
    sig = bq(sig_query.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
    LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
           "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
    tw = {t: per_pos_w for t in tier_set} if per_pos_w else None

    kwargs = dict(
        allowed_tiers=tier_set, max_positions=max_pos, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=_sec_map,
        sector_cap_exempt_tiers=exempt, tier_weights=tw,
    )
    if state_exit_map is not None:
        kwargs["state_by_date"] = state_by_date
        kwargs["state_exit_map"] = state_exit_map

    nav_bal, tr_bal = simulate(sig, prices, _vni_dates, **kwargs, **LIQ)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    sig_vn30 = sig[sig["ticker"].isin(_top30)]
    prices_vn30 = {tk: prices[tk] for tk in _top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in _top30}
    LIQ_VN30 = {**LIQ, "liquidity_lookup": liq_vn30}
    kwargs_vn30 = {**kwargs, "ticker_sector_map": None, "sector_limit_per_sector": None}
    nav_vn30, tr_vn30 = simulate(sig_vn30, prices_vn30, _vni_dates, **kwargs_vn30, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    return ba_nav, tr_bal, tr_vn30

def wm(nav, st, en):
    sub = nav[(nav.index >= st) & (nav.index <= en)]
    if len(sub) < 30: return None
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (sub - sub.cummax()) / sub.cummax(); mdd = dd.min()
    return dict(cagr=cagr*100, sharpe=sharpe, mdd=mdd*100,
                calmar=cagr/abs(mdd) if mdd<0 else 0,
                wealth=sub.iloc[-1]/sub.iloc[0])

def vni_wm(vni, st, en):
    sub = vni[(vni["time"] >= st) & (vni["time"] <= en)].copy()
    if len(sub) < 30: return None
    sub["nav"] = sub["Close"] / sub["Close"].iloc[0]
    return wm(sub.set_index("time")["nav"], st, en)

D1_KW = dict(exempt={"RE_BACKLOG_BUY"}, max_pos=12, per_pos_w=0.10)

print(f"\nRunning variants:")
ba_v4,   tr_v4b,  tr_v4v  = run("v4_baseline",     V4_QUERY, TIER_BAL_V4)
ba_d1,   tr_d1b,  tr_d1v  = run("D1+slot12",       D1_QUERY, TIER_BAL_D1, **D1_KW)
ba_k2a,  tr_k2ab, tr_k2av = run("K2_50_BEAR",      D1_QUERY, TIER_BAL_D1, **D1_KW,
                                state_exit_map={2: 0.5, 1: 0.5})
ba_k2b,  tr_k2bb, tr_k2bv = run("K2_50_BEAR_CR",   D1_QUERY, TIER_BAL_D1, **D1_KW,
                                state_exit_map={2: 0.5, 1: 1.0})
ba_k2c,  tr_k2cb, tr_k2cv = run("K2_30_BEAR_CR",   D1_QUERY, TIER_BAL_D1, **D1_KW,
                                state_exit_map={2: 0.3, 1: 0.5})
ba_k2d,  tr_k2db, tr_k2dv = run("K2_50_NEUT",      D1_QUERY, TIER_BAL_D1, **D1_KW,
                                state_exit_map={3: 0.5, 2: 0.5, 1: 0.5})
ba_k2e,  tr_k2eb, tr_k2ev = run("K2_70_BEAR",      D1_QUERY, TIER_BAL_D1, **D1_KW,
                                state_exit_map={2: 0.7, 1: 0.7})

periods = [
    ("FULL (2014-now)", ba_v4.index.min(), ba_v4.index.max()),
    ("Last 5Y",         ba_v4.index.max() - pd.DateOffset(years=5), ba_v4.index.max()),
    ("Last 3Y",         ba_v4.index.max() - pd.DateOffset(years=3), ba_v4.index.max()),
    ("Last 1Y",         ba_v4.index.max() - pd.DateOffset(years=1), ba_v4.index.max()),
    ("YTD 2026",        pd.Timestamp("2026-01-01"), ba_v4.index.max()),
    ("OOS 2024-now",    OOS_START, ba_v4.index.max()),
]

print("\n" + "="*125)
print("  K2 STATE-PARTIAL-EXIT — D1+slot12 base, variants of exit fractions")
print("="*125)
hdr = f"{'Period':<16}{'Variant':<18}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}{'ΔvsD1':>9}"
print(hdr); print("-"*len(hdr))

variants = [
    ("v4_baseline", ba_v4), ("D1+slot12 ★", ba_d1),
    ("K2_50_BEAR", ba_k2a), ("K2_50_BEAR_CR", ba_k2b), ("K2_30_BEAR_CR", ba_k2c),
    ("K2_50_NEUT", ba_k2d), ("K2_70_BEAR", ba_k2e),
]
for label, st, en in periods:
    m1 = wm(ba_d1, st, en)
    for var, nav in variants:
        m = wm(nav, st, en)
        if m is None: continue
        d = m["cagr"] - m1["cagr"] if "K2" in var else 0
        d_str = f"{d:+.2f}pp" if "K2" in var else "-"
        print(f"{label:<16}{var:<18}{m['cagr']:>8.2f}{m['sharpe']:>8.2f}"
              f"{m['mdd']:>9.1f}{m['calmar']:>8.2f}{m['wealth']:>8.2f}{d_str:>9}")
    mv = vni_wm(_vni, st, en)
    if mv:
        print(f"{label:<16}{'VNINDEX_BH':<18}{mv['cagr']:>8.2f}{mv['sharpe']:>8.2f}"
              f"{mv['mdd']:>9.1f}{mv['calmar']:>8.2f}{mv['wealth']:>8.2f}{'-':>9}")
    print()

# 2026 detail
print("2026 YTD per variant (trade-level):")
for nm, b, v in [("D1+slot12",tr_d1b,tr_d1v), ("K2_50_BEAR",tr_k2ab,tr_k2av),
                 ("K2_50_BEAR_CR",tr_k2bb,tr_k2bv), ("K2_30_BEAR_CR",tr_k2cb,tr_k2cv),
                 ("K2_50_NEUT",tr_k2db,tr_k2dv), ("K2_70_BEAR",tr_k2eb,tr_k2ev)]:
    all_t = pd.concat([b, v], ignore_index=True)
    all_t["entry_date"] = pd.to_datetime(all_t["entry_date"])
    t26 = all_t[all_t["entry_date"].dt.year == 2026]
    state_exits = all_t[all_t["reason"].str.startswith("STATE_", na=False)]
    if len(t26):
        print(f"  {nm:<16}n2026={len(t26):3d} mean26={t26['ret_net'].mean()*100:+.2f}%  "
              f"WR={(t26['ret_net']>0).mean()*100:.1f}% | total state-exits ever: {len(state_exits)}")

# Trade reason breakdown for best K2 variant
print("\nReason distribution (best K2 variant D1+K2_50_BEAR):")
all_t = pd.concat([tr_k2ab, tr_k2av], ignore_index=True)
print(all_t["reason"].value_counts().to_string())
