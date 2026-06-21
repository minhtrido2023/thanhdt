#!/usr/bin/env python3
"""
stress_test_d1.py
=================
E2: stress test D1_exempt to confirm not overfit.

(a) Sensitivity grid: adv_yoy ∈ {0.3, 0.5, 0.7, 1.0} × ta ∈ {100, 120, 140}
    Each cell runs canonical BA sim with D1 exemption.
    Look for: is performance robust across thresholds, or fragile to specific picks?

(b) Per-year P&L breakdown for D1_exempt reference (adv_yoy=0.5, ta=120):
    - Annual CAGR vs v4 baseline
    - Annual RE_BACKLOG trade count + mean PnL
    - Look for: any year where D1 underperforms significantly
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

def build_query(adv_yoy_thr, ta_thr):
    """Build SIGNAL_V10 with parameterized RE_BACKLOG_BUY thresholds."""
    return SIGNAL_V10_BASE.replace(
        "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,",
        "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,\n"
        "    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4, 0)) - 1 AS adv_yoy,"
    ).replace(
        "fin.Revenue_YoY_P0 AS rev_yoy,",
        "fin.Revenue_YoY_P0 AS rev_yoy, fin.adv_yoy AS adv_yoy, t.ICB_Code AS icb,"
    ).replace(
        "WHEN fa_tier = 'E' THEN 'AVOID_faE'",
        f"WHEN icb = 8633.0 AND adv_yoy > {adv_yoy_thr} AND fa_tier IN ('C','D') "
        f"AND ta >= {ta_thr} AND state5 IN (3,4,5) AND (np_yoy > 0 OR rev_yoy > 0) "
        f"THEN 'RE_BACKLOG_BUY'\n"
        f"    WHEN fa_tier = 'E' THEN 'AVOID_faE'"
    )

V4_QUERY = SIGNAL_V10_BASE
TIER_BAL_V4 = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
TIER_BAL_RE = TIER_BAL_V4 + ["RE_BACKLOG_BUY"]
OOS_START = pd.Timestamp("2024-01-01")

# Cache common inputs
print("Loading common inputs (VNI, sec_map, top30) ...")
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

def run(label, sig_query, tier_set, exempt=None):
    sig = bq(sig_query.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    n_re = (sig["play_type"] == "RE_BACKLOG_BUY").sum()
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
    return ba_nav, tr_bal, tr_vn30, n_re

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

# ═══════════════════ (a) Sensitivity grid ══════════════════════════════════════
print("\n" + "="*100)
print("  (a) SENSITIVITY GRID: adv_yoy × ta thresholds (D1 exempt always on)")
print("="*100)
print("\nRunning v4 baseline ...")
ba_v4, tr_v4_b, tr_v4_v, _ = run("v4", V4_QUERY, TIER_BAL_V4, exempt=None)

ADV_GRID = [0.3, 0.5, 0.7, 1.0]
TA_GRID  = [100, 120, 140]

grid_results = []
for adv in ADV_GRID:
    for ta in TA_GRID:
        label = f"adv>{adv} ta>={ta}"
        print(f"Running {label} ...")
        sig_q = build_query(adv, ta)
        ba_d, tr_b, tr_v, n_re_sig = run(label, sig_q, TIER_BAL_RE, exempt={"RE_BACKLOG_BUY"})
        full = wm(ba_d, ba_d.index.min(), ba_d.index.max())
        oos  = wm(ba_d, OOS_START, ba_d.index.max())
        oos4 = wm(ba_d, pd.Timestamp("2022-01-01"), ba_d.index.max())
        v4_full = wm(ba_v4, ba_v4.index.min(), ba_v4.index.max())
        v4_oos  = wm(ba_v4, OOS_START, ba_v4.index.max())
        v4_oos4 = wm(ba_v4, pd.Timestamp("2022-01-01"), ba_v4.index.max())
        rebk = tr_b[tr_b["play_type"] == "RE_BACKLOG_BUY"] if "play_type" in tr_b.columns else pd.DataFrame()
        grid_results.append({
            "adv_yoy": adv, "ta": ta,
            "n_sig": n_re_sig, "n_trades": len(rebk),
            "trade_mean_pct": rebk["ret_net"].mean()*100 if len(rebk) else np.nan,
            "trade_wr": (rebk["ret_net"]>0).mean()*100 if len(rebk) else np.nan,
            "FULL_cagr": full["cagr_pct"],  "FULL_d_cagr": full["cagr_pct"]-v4_full["cagr_pct"],
            "FULL_sh": full["sharpe"],      "FULL_d_sh":   full["sharpe"]-v4_full["sharpe"],
            "FULL_dd": full["max_dd_pct"],
            "OOS_cagr": oos["cagr_pct"],    "OOS_d_cagr":  oos["cagr_pct"]-v4_oos["cagr_pct"],
            "OOS_sh": oos["sharpe"],        "OOS_d_sh":    oos["sharpe"]-v4_oos["sharpe"],
            "OOS_dd": oos["max_dd_pct"],
            "OOS4_cagr": oos4["cagr_pct"],  "OOS4_d_cagr": oos4["cagr_pct"]-v4_oos4["cagr_pct"],
        })

grid_df = pd.DataFrame(grid_results)
grid_df.to_csv("stress_d1_grid.csv", index=False)

print("\nSensitivity grid results (Δ vs v4 baseline):")
print(f"{'adv':>5}{'ta':>5}{'n_sig':>7}{'n_tr':>5}{'tr_mn%':>8}{'tr_WR':>7}"
      f"{'FULL_CAGR':>11}{'ΔF_CG':>8}{'ΔF_Sh':>8}"
      f"{'OOS_CAGR':>10}{'ΔO_CG':>8}{'ΔO_Sh':>8}"
      f"{'OOS4_CG':>9}{'ΔO4_CG':>9}")
print("-"*125)
for _, r in grid_df.iterrows():
    print(f"{r['adv_yoy']:>5.1f}{r['ta']:>5.0f}{r['n_sig']:>7.0f}{r['n_trades']:>5.0f}"
          f"{r['trade_mean_pct']:>+7.2f}%{r['trade_wr']:>6.1f}%"
          f"{r['FULL_cagr']:>10.2f}%{r['FULL_d_cagr']:>+7.2f}{r['FULL_d_sh']:>+8.2f}"
          f"{r['OOS_cagr']:>9.2f}%{r['OOS_d_cagr']:>+7.2f}{r['OOS_d_sh']:>+8.2f}"
          f"{r['OOS4_cagr']:>8.2f}%{r['OOS4_d_cagr']:>+8.2f}")

print(f"\nv4 baseline reference: FULL={v4_full['cagr_pct']:.2f}% / OOS={v4_oos['cagr_pct']:.2f}% / OOS4={v4_oos4['cagr_pct']:.2f}%")

# ═══════════════════ (b) Per-year P&L breakdown — reference D1 ════════════════
print("\n" + "="*100)
print("  (b) PER-YEAR BREAKDOWN — D1 reference (adv>0.5, ta>=120)")
print("="*100)
ba_d1_ref, tr_d1_b, tr_d1_v, _ = run("D1_ref", build_query(0.5, 120), TIER_BAL_RE, exempt={"RE_BACKLOG_BUY"})

# Annual NAV-based CAGR comparison
def yr_cagr(nav, yr):
    sub = nav[(nav.index.year == yr)]
    if len(sub) < 2: return np.nan
    return (sub.iloc[-1] / sub.iloc[0] - 1) * 100

yrs = sorted(set(ba_v4.index.year))
print(f"\n{'Year':>5}{'v4_ret%':>10}{'D1_ret%':>10}{'Δ%':>8}"
      f"{'RE_n':>6}{'RE_mean%':>10}{'RE_WR':>8}")
print("-"*60)
rebk_d1 = tr_d1_b[tr_d1_b["play_type"] == "RE_BACKLOG_BUY"].copy() if "play_type" in tr_d1_b.columns else pd.DataFrame()
if len(rebk_d1):
    rebk_d1["entry_date"] = pd.to_datetime(rebk_d1["entry_date"])
    rebk_d1["year"] = rebk_d1["entry_date"].dt.year
for y in yrs:
    v4r = yr_cagr(ba_v4, y); d1r = yr_cagr(ba_d1_ref, y)
    yr_re = rebk_d1[rebk_d1["year"] == y] if len(rebk_d1) else pd.DataFrame()
    re_n = len(yr_re); re_mn = yr_re["ret_net"].mean()*100 if re_n else np.nan
    re_wr = (yr_re["ret_net"]>0).mean()*100 if re_n else np.nan
    print(f"{y:>5}{v4r:>+9.2f}%{d1r:>+9.2f}%{d1r-v4r:>+7.2f}%"
          f"{re_n:>6}{re_mn:>+9.2f}%{re_wr:>+7.1f}%")

# Sector concentration check: max concurrent sector-8 positions
print("\n--- Concurrent sector-8 position counts (D1 BAL leg) ---")
# Reconstruct sector-8 holdings timeline
sec8_tickers = {tk for tk, s in _sec_map.items() if s == 8}
tr_d1_b["entry_date"] = pd.to_datetime(tr_d1_b["entry_date"])
tr_d1_b["exit_date"]  = pd.to_datetime(tr_d1_b["exit_date"])
sec8_trades = tr_d1_b[tr_d1_b["ticker"].isin(sec8_tickers)].copy()
print(f"Total sec-8 trades in D1 BAL: {len(sec8_trades)}")
# Count concurrent: for each entry, count overlapping sec-8 positions
peak_concurrent = 0; peak_date = None
events = []
for _, r in sec8_trades.iterrows():
    events.append((r["entry_date"], 1, r["ticker"], r["play_type"]))
    events.append((r["exit_date"], -1, r["ticker"], r["play_type"]))
events.sort()
cur = 0
for d, delta, tk, pt in events:
    cur += delta
    if cur > peak_concurrent:
        peak_concurrent = cur; peak_date = d
print(f"PEAK concurrent sec-8 positions in D1 BAL: {peak_concurrent} on {peak_date.date() if peak_date else 'n/a'}")
print(f"  (Reference: v4 cap=4 means max 4 in v4; D1 exempts RE_BACKLOG which adds slots)")
