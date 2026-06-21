#!/usr/bin/env python3
"""
verify_v10_drift.py
===================
Investigate why v10 baseline shows ~15.17% CAGR now vs memory's 17.15%.

Tests:
  A. v4_baseline with VNINDEX_RSI_Max3M patch DISABLED + END=2026-05-15 (current)
  B. v4_baseline with VNINDEX_RSI_Max3M patch DISABLED + END=2026-01-16 (compare scripts era)
  C. v4_baseline with VNINDEX_RSI_Max3M patch DISABLED + END=2025-12-31 (year-end snapshot)
  D. v4_baseline with VNINDEX_RSI_Max3M COMPUTED ON FLY + END=2026-05-15
  E. v4_baseline with VNINDEX_RSI_Max3M COMPUTED + END=2025-12-31
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, re as _re
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq, VNI_QUERY

START_DATE = "2014-01-01"

with open(os.path.join(WORKDIR, "test_round14_stability.py"), encoding="utf-8") as _f:
    _src = _f.read()
_m = _re.search(r'SIGNAL_V10\s*=\s*"""(.+?)"""', _src, _re.DOTALL)
SIGNAL_V10_RAW = _m.group(0).split('"""', 1)[1].rsplit('"""', 1)[0]

# Two variants of v10 SIGNAL:
SIGNAL_V10_PATCHED = SIGNAL_V10_RAW.replace(
    "CASE WHEN t.VNINDEX_RSI_Max3M > 0.65 THEN 10 ELSE 0 END",
    "CASE WHEN FALSE THEN 10 ELSE 0 END")

# Version with VNINDEX_RSI_Max3M computed on-the-fly (mirrors recommend_holistic.py)
SIGNAL_V10_COMPUTED = SIGNAL_V10_RAW.replace(
    "WITH fa_dated AS (",
    """WITH vni_history AS (
  SELECT t.time, t.D_RSI
  FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL
),
vni_max3m AS (
  SELECT time,
    MAX(D_RSI) OVER (ORDER BY time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS rsi_max3m
  FROM vni_history
),
fa_dated AS ("""
).replace(
    "CASE WHEN t.VNINDEX_RSI_Max3M > 0.65 THEN 10 ELSE 0 END",
    "CASE WHEN vmax.rsi_max3m > 0.65 THEN 10 ELSE 0 END"
).replace(
    "LEFT JOIN tav2_bq.vnindex_5state AS s5",
    "LEFT JOIN vni_max3m AS vmax ON vmax.time = t.time\n  LEFT JOIN tav2_bq.vnindex_5state AS s5"
)

TIER_BAL_V4 = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]

print("Loading static inputs ...")
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

def run(label, sig_query, end_date):
    print(f"  {label} (END={end_date}) ...")
    sig = bq(sig_query.format(start=START_DATE, end=end_date))
    sig["time"] = pd.to_datetime(sig["time"])
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
    vni = bq(VNI_QUERY.format(start=START_DATE, end=end_date))
    vni["time"] = pd.to_datetime(vni["time"])
    vni_dates = sorted(vni["time"].unique())
    LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
           "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    nav_bal, tr_bal = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL_V4, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=_sec_map, **LIQ)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])
    sig_vn30 = sig[sig["ticker"].isin(_top30)]
    prices_vn30 = {tk: prices[tk] for tk in _top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in _top30}
    LIQ_VN30 = {**LIQ, "liquidity_lookup": liq_vn30}
    nav_vn30, tr_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL_V4, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    return ba_nav, len(tr_bal) + len(tr_vn30), vni

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

print("\nRunning grid:")
results = []
for label, sig_q, end in [
    ("A: patched, end=2026-05-15", SIGNAL_V10_PATCHED,  "2026-05-15"),
    ("B: patched, end=2026-01-16", SIGNAL_V10_PATCHED,  "2026-01-16"),
    ("C: patched, end=2025-12-31", SIGNAL_V10_PATCHED,  "2025-12-31"),
    ("D: COMPUTED, end=2026-05-15", SIGNAL_V10_COMPUTED, "2026-05-15"),
    ("E: COMPUTED, end=2025-12-31", SIGNAL_V10_COMPUTED, "2025-12-31"),
]:
    try:
        nav, n_tr, vni = run(label, sig_q, end)
        m = wm(nav, nav.index.min(), nav.index.max())
        results.append((label, end, n_tr, m, vni))
    except Exception as e:
        print(f"    ERROR: {e}")
        results.append((label, end, 0, None, None))

print("\n" + "="*100)
print("  V10 BASELINE DRIFT INVESTIGATION")
print("="*100)
hdr = f"{'Variant':<32}{'End':<12}{'n_tr':>6}{'CAGR%':>9}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}"
print(hdr); print("-"*len(hdr))
for label, end, n_tr, m, vni in results:
    if m is None:
        print(f"{label:<32}{end:<12}{n_tr:>6}  ERROR")
        continue
    print(f"{label:<32}{end:<12}{n_tr:>6}{m['cagr']:>9.2f}{m['sharpe']:>8.2f}"
          f"{m['mdd']:>9.1f}{m['calmar']:>8.2f}{m['wealth']:>8.2f}")

print("\nMemory reference (ba_system_definition.md):")
print("  'at 50B: CAGR 17.15%, Sharpe 1.21, DD -14.5%, Calmar 1.18, wealth 6.73× (12yr)'")
print("  Date of memory observation: ~April-May 2026 (before recent ticker data refresh)")

print("\nVNI for context (FULL each period):")
for label, end, n_tr, m, vni in results:
    if vni is not None:
        vsub = vni.set_index("time")["Close"]
        yrs = (vsub.index[-1] - vsub.index[0]).days / 365.25
        cagr = (vsub.iloc[-1] / vsub.iloc[0]) ** (1/yrs) - 1
        print(f"  {end}: VNI CAGR={cagr*100:.2f}%, final={vsub.iloc[-1]:.0f}, yrs={yrs:.2f}")
        break  # All same VNI
