#!/usr/bin/env python3
"""
system_current_results.py
=========================
Canonical BA-system sim cập nhật đến ngày 2026-05-15 (latest ticker data).
Configuration: D1+slot12 (just deployed 2026-05-16).
Benchmark: VNINDEX (E1VFVN30/VN30 không có trong BQ).
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
END_DATE   = "2026-05-15"  # latest available

with open(os.path.join(WORKDIR, "test_round14_stability.py"), encoding="utf-8") as _f:
    _src = _f.read()
_m = _re.search(r'SIGNAL_V10\s*=\s*"""(.+?)"""', _src, _re.DOTALL)
SIGNAL_V10_BASE = _m.group(0).split('"""', 1)[1].rsplit('"""', 1)[0]
# NOTE: previously patched VNINDEX_RSI_Max3M to FALSE (column missing).
# Fixed 2026-05-17: test_round14_stability.py now computes rsi_max3m on-the-fly.
# Patch removed — restores ~1.2pp CAGR vs prior weakened baseline.

# D1+slot12 SIGNAL_V10 (deployed config)
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

print("Loading common inputs ...")
_vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
_vni["time"] = pd.to_datetime(_vni["time"])
_vni_dates = sorted(_vni["time"].unique())
print(f"  VNINDEX: {len(_vni)} rows, {_vni['time'].min().date()} -> {_vni['time'].max().date()}")

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
    print(f"  {label} ...")
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
    if len(sub) < 30: return None
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    sortino_denom = rets[rets<0].std()
    sortino = rets.mean() / sortino_denom * np.sqrt(spy) if sortino_denom and sortino_denom > 0 else 0
    dd = (sub - sub.cummax()) / sub.cummax(); mdd = dd.min()
    return dict(n=len(sub), cagr=cagr*100, sharpe=sharpe, sortino=sortino,
                mdd=mdd*100, calmar=cagr/abs(mdd) if mdd<0 else 0,
                wealth=sub.iloc[-1]/sub.iloc[0], yrs=yrs)

def vni_wm(vni, st, en):
    sub = vni[(vni["time"] >= st) & (vni["time"] <= en)].copy()
    if len(sub) < 30: return None
    sub["nav"] = sub["Close"] / sub["Close"].iloc[0]
    return wm(sub.set_index("time")["nav"], st, en)

print("\nRunning canonical sim (50B init):")
ba_v4,  tr_v4b,  tr_v4v  = run("v4_baseline",   V4_QUERY, TIER_BAL_V4)
ba_d1,  tr_d1b,  tr_d1v  = run("D1+slot12",     D1_QUERY, TIER_BAL_D1,
                               exempt={"RE_BACKLOG_BUY"}, max_pos=12, per_pos_w=0.10)

last_dt = ba_v4.index.max()
print(f"\nSim end: {last_dt.date()}")

periods = [
    ("FULL (2014-now)",     ba_v4.index.min(), last_dt),
    ("Last 5Y",             last_dt - pd.DateOffset(years=5), last_dt),
    ("Last 3Y",             last_dt - pd.DateOffset(years=3), last_dt),
    ("Last 1Y",             last_dt - pd.DateOffset(years=1), last_dt),
    ("YTD 2026",            pd.Timestamp("2026-01-01"), last_dt),
    ("OOS 2024-now",        pd.Timestamp("2024-01-01"), last_dt),
]

print("\n" + "="*114)
print(f"  BA-SYSTEM CURRENT (D1+slot12 deployed) — Performance to {last_dt.date()}")
print(f"  50B init NAV, 50/50 BAL+VN30, hold=45d, stop=-20%, max=12pos, 10%/pos cap")
print(f"  Benchmark: VNINDEX (E1VFVN30/VN30 không có trong BQ)")
print("="*114)
hdr = f"{'Period':<20}{'Variant':<14}{'CAGR%':>8}{'Sharpe':>8}{'Sortino':>9}{'MaxDD%':>9}{'Calmar':>8}{'Wealth×':>9}{'vs VNI':>9}"
print(hdr); print("-"*len(hdr))

for label, st, en in periods:
    m4 = wm(ba_v4, st, en); md = wm(ba_d1, st, en); mv = vni_wm(_vni, st, en)
    if md is None or mv is None: continue
    for var, m in [("v4_baseline",m4), ("D1+slot12 ★",md), ("VNINDEX_BH",mv)]:
        delta_cagr = (m["cagr"] - mv["cagr"]) if var != "VNINDEX_BH" else 0
        delta_str = f"{delta_cagr:+.2f}pp" if var != "VNINDEX_BH" else "-"
        print(f"{label:<20}{var:<14}{m['cagr']:>8.2f}{m['sharpe']:>8.2f}{m['sortino']:>9.2f}"
              f"{m['mdd']:>9.1f}{m['calmar']:>8.2f}{m['wealth']:>9.2f}{delta_str:>9}")
    print()

# Trade stats summary
print("="*114)
print("  Trade-level statistics (D1+slot12 BAL+VN30 combined)")
print("="*114)
all_trades = pd.concat([tr_d1b, tr_d1v], ignore_index=True)
all_trades["entry_date"] = pd.to_datetime(all_trades["entry_date"])
print(f"  Total trades: {len(all_trades)}  |  Mean ret_net: {all_trades['ret_net'].mean()*100:+.2f}%  "
      f"|  WR: {(all_trades['ret_net']>0).mean()*100:.1f}%")
print(f"  Median ret_net: {all_trades['ret_net'].median()*100:+.2f}%  "
      f"|  Mean days_held: {all_trades['days_held'].mean():.1f}")

print(f"\n  Per play_type breakdown:")
gb = all_trades.groupby("play_type").agg(
    n=("ret_net","count"),
    mean=("ret_net", lambda x: x.mean()*100),
    median=("ret_net", lambda x: x.median()*100),
    wr=("ret_net", lambda x: (x>0).mean()*100),
).sort_values("n", ascending=False)
print(gb.round(2).to_string())

print(f"\n  Per exit reason:")
gb = all_trades.groupby("reason").agg(
    n=("ret_net","count"),
    mean=("ret_net", lambda x: x.mean()*100),
    wr=("ret_net", lambda x: (x>0).mean()*100),
)
print(gb.round(2).to_string())

# Recent year detail
print("\n" + "="*114)
print("  Year-by-year P&L breakdown")
print("="*114)
print(f"{'Year':>6}{'v4 ret%':>10}{'D1 ret%':>10}{'Δ%':>8}{'VNI ret%':>10}{'D1-VNI':>9}{'trades':>8}")
print("-"*70)
for yr in sorted(set(ba_v4.index.year)):
    s_v4 = ba_v4[ba_v4.index.year == yr]
    s_d1 = ba_d1[ba_d1.index.year == yr]
    s_vn = _vni[_vni["time"].dt.year == yr].set_index("time")["Close"]
    if len(s_v4) < 2 or len(s_vn) < 2: continue
    r_v4 = (s_v4.iloc[-1]/s_v4.iloc[0]-1)*100
    r_d1 = (s_d1.iloc[-1]/s_d1.iloc[0]-1)*100
    r_vn = (s_vn.iloc[-1]/s_vn.iloc[0]-1)*100
    n_tr = ((all_trades["entry_date"].dt.year == yr)).sum()
    print(f"{yr:>6}{r_v4:>+9.2f}%{r_d1:>+9.2f}%{r_d1-r_v4:>+7.2f}%{r_vn:>+9.2f}%{r_d1-r_vn:>+8.2f}%{n_tr:>8}")

# RE_BACKLOG trades specifically
rebk = all_trades[all_trades["play_type"]=="RE_BACKLOG_BUY"]
if len(rebk):
    print(f"\n  RE_BACKLOG_BUY trades (D1 specific tier):")
    print(f"    N={len(rebk)}, mean={rebk['ret_net'].mean()*100:+.2f}%, "
          f"median={rebk['ret_net'].median()*100:+.2f}%, WR={(rebk['ret_net']>0).mean()*100:.1f}%")

print(f"\nFull NAV series saved: system_current_nav.csv")
out = pd.DataFrame({
    "time": ba_v4.index,
    "v4_baseline": ba_v4.values,
    "d1_slot12": ba_d1.values,
}).set_index("time")
out["vni_norm"] = _vni.set_index("time")["Close"].reindex(out.index, method="ffill")
out["vni_norm"] = out["vni_norm"] / out["vni_norm"].iloc[0]
out.to_csv("system_current_nav.csv")
