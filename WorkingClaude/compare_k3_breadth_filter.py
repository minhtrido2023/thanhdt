#!/usr/bin/env python3
"""
compare_k3_breadth_filter.py
============================
K3: VNI breadth filter — pause new buys when % ticker_prune > MA50 drops
below 30% within last 5 sessions (recent peak >= 50%).

Variants tested:
  v4_baseline           — reference (no D1, no K3)
  D1+slot12             — current production winner
  D1+slot12+K3_strict   — K3 fires when curr<0.30 AND prev5d_max>=0.50
  D1+slot12+K3_loose    — K3 fires when curr<0.30 (no recency check)
  D1+slot12+K3_v40      — variant: curr<0.40 AND prev5d_max>=0.55

Method: build breadth dates CTE in SQL, JOIN to ticker_data, exclude
buy play_types when k3_block=true. NO change to position management.
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
D1_QUERY_BASE = SIGNAL_V10_BASE.replace(
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

def build_k3_query(curr_thr: float, peak_thr: float, peak_window: int = 5):
    """Wrap D1_QUERY_BASE adding K3 breadth filter.
    Block buy tiers (turn them into 'AVOID_breadth') when:
      pct_above_ma50 < curr_thr AND MAX over last peak_window sessions >= peak_thr
    """
    # SIGNAL_V10 base output cols: ticker, time, Close, play_type, ta, liq, sec
    # We wrap it: compute breadth at the outer level, join, override play_type.
    inner = D1_QUERY_BASE.format(start=START_DATE, end=END_DATE)
    return f"""
WITH base AS ({inner}),
breadth_raw AS (
  SELECT t.time,
    COUNTIF(t.Close > t.MA50) / COUNT(*) AS br
  FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
  WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM `lithe-record-440915-m9.tav2_bq.ticker_prune` AS t2)
    AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
    AND t.MA50 IS NOT NULL AND t.Close IS NOT NULL
  GROUP BY t.time
),
breadth_with_peak AS (
  SELECT time, br,
    MAX(br) OVER (ORDER BY time ROWS BETWEEN {peak_window} PRECEDING AND CURRENT ROW) AS br_peak,
    (br < {curr_thr} AND
     MAX(br) OVER (ORDER BY time ROWS BETWEEN {peak_window} PRECEDING AND CURRENT ROW) >= {peak_thr}
    ) AS k3_block
  FROM breadth_raw
)
SELECT b.ticker, b.time, b.Close,
  CASE WHEN bw.k3_block AND b.play_type IN (
    'MEGA','MOMENTUM','MOMENTUM_N','MOMENTUM_S','DEEP_VALUE_RECOVERY','RE_BACKLOG_BUY',
    'MOMENTUM_QUALITY','MOMENTUM_A','MOMENTUM_S_N','COMPOUNDER_BUY','S_PRO'
  ) THEN 'K3_BLOCKED' ELSE b.play_type END AS play_type,
  b.ta, b.liq, b.sec
FROM base AS b
LEFT JOIN breadth_with_peak AS bw ON bw.time = b.time
"""

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

def run(label, raw_query, tier_set, exempt=None, max_pos=10, per_pos_w=None,
        format_args=True):
    print(f"  {label} ...")
    sql = raw_query.format(start=START_DATE, end=END_DATE) if format_args else raw_query
    sig = bq(sql)
    sig["time"] = pd.to_datetime(sig["time"])
    n_blk = (sig["play_type"] == "K3_BLOCKED").sum()
    if n_blk: print(f"    K3_BLOCKED rows: {n_blk:,}")
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
    dd = (sub - sub.cummax()) / sub.cummax(); mdd = dd.min()
    return dict(cagr=cagr*100, sharpe=sharpe, mdd=mdd*100,
                calmar=cagr/abs(mdd) if mdd<0 else 0,
                wealth=sub.iloc[-1]/sub.iloc[0])

def vni_wm(vni, st, en):
    sub = vni[(vni["time"] >= st) & (vni["time"] <= en)].copy()
    if len(sub) < 30: return None
    sub["nav"] = sub["Close"] / sub["Close"].iloc[0]
    return wm(sub.set_index("time")["nav"], st, en)

print(f"\nWindow: {START_DATE} -> {END_DATE}")
print("\nRunning variants:")
ba_v4,   tr_v4b,  tr_v4v  = run("v4",                V4_QUERY, TIER_BAL_V4)
ba_d1,   tr_d1b,  tr_d1v  = run("D1+slot12",         D1_QUERY_BASE, TIER_BAL_D1,
                                exempt={"RE_BACKLOG_BUY"}, max_pos=12, per_pos_w=0.10)
ba_k3s,  tr_ksb,  tr_ksv  = run("D1+K3_strict30/50", build_k3_query(0.30, 0.50, 5),
                                TIER_BAL_D1, exempt={"RE_BACKLOG_BUY"}, max_pos=12, per_pos_w=0.10,
                                format_args=False)
ba_k3l,  tr_klb,  tr_klv  = run("D1+K3_loose30",     build_k3_query(0.30, 0.00, 1),
                                TIER_BAL_D1, exempt={"RE_BACKLOG_BUY"}, max_pos=12, per_pos_w=0.10,
                                format_args=False)
ba_k3v40,tr_kvb,  tr_kvv  = run("D1+K3_v40/55",      build_k3_query(0.40, 0.55, 5),
                                TIER_BAL_D1, exempt={"RE_BACKLOG_BUY"}, max_pos=12, per_pos_w=0.10,
                                format_args=False)

periods = [
    ("FULL (2014-now)", ba_v4.index.min(), ba_v4.index.max()),
    ("Last 5Y",         ba_v4.index.max() - pd.DateOffset(years=5), ba_v4.index.max()),
    ("Last 1Y",         ba_v4.index.max() - pd.DateOffset(years=1), ba_v4.index.max()),
    ("YTD 2026",        pd.Timestamp("2026-01-01"), ba_v4.index.max()),
    ("OOS 2024-now",    OOS_START, ba_v4.index.max()),
]

print("\n" + "="*114)
print("  K3 BREADTH FILTER — D1+slot12 base, variants of breadth threshold")
print("="*114)
hdr = f"{'Period':<16}{'Variant':<20}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}{'ΔvsD1':>9}"
print(hdr); print("-"*len(hdr))

for label, st, en in periods:
    m4  = wm(ba_v4, st, en)
    m1  = wm(ba_d1, st, en)
    ms  = wm(ba_k3s, st, en)
    ml  = wm(ba_k3l, st, en)
    mv40= wm(ba_k3v40, st, en)
    mvni= vni_wm(_vni, st, en)
    rows = [("v4_baseline",m4), ("D1+slot12 ★",m1),
            ("D1+K3_30/50",ms), ("D1+K3_loose30",ml), ("D1+K3_40/55",mv40)]
    for var, m in rows:
        if m is None: continue
        d = m["cagr"] - m1["cagr"] if var != "D1+slot12 ★" and var != "v4_baseline" else 0
        d_str = f"{d:+.2f}pp" if var.startswith("D1+K3") else "-"
        print(f"{label:<16}{var:<20}{m['cagr']:>8.2f}{m['sharpe']:>8.2f}"
              f"{m['mdd']:>9.1f}{m['calmar']:>8.2f}{m['wealth']:>8.2f}{d_str:>9}")
    if mvni:
        print(f"{label:<16}{'VNINDEX_BH':<20}{mvni['cagr']:>8.2f}{mvni['sharpe']:>8.2f}"
              f"{mvni['mdd']:>9.1f}{mvni['calmar']:>8.2f}{mvni['wealth']:>8.2f}{'-':>9}")
    print()

# Trade count comparison
print("Trade counts:")
for nm, b, v in [("v4",tr_v4b,tr_v4v), ("D1+slot12",tr_d1b,tr_d1v),
                 ("D1+K3_strict",tr_ksb,tr_ksv), ("D1+K3_loose",tr_klb,tr_klv),
                 ("D1+K3_v40",tr_kvb,tr_kvv)]:
    print(f"  {nm:<14}BAL={len(b):4d}  VN30={len(v):4d}  total={len(b)+len(v)}")

# YTD 2026 detail per variant
print("\n2026 YTD trade counts + P&L:")
for nm, b, v in [("D1+slot12",tr_d1b,tr_d1v), ("D1+K3_strict",tr_ksb,tr_ksv),
                 ("D1+K3_loose",tr_klb,tr_klv), ("D1+K3_v40",tr_kvb,tr_kvv)]:
    all_t = pd.concat([b, v], ignore_index=True)
    all_t["entry_date"] = pd.to_datetime(all_t["entry_date"])
    t26 = all_t[all_t["entry_date"].dt.year == 2026]
    if len(t26):
        print(f"  {nm:<14}n={len(t26):3d}  mean={t26['ret_net'].mean()*100:+.2f}%  "
              f"sum_ret={t26['ret_net'].sum()*100:+.2f}%  WR={(t26['ret_net']>0).mean()*100:.1f}%")
    else:
        print(f"  {nm:<14}no 2026 trades")
