#!/usr/bin/env python3
"""
tests_growth_ta_filters.py
==========================
Investigate 2 deeper directions for fixing LH peak-reversal weakness:

  Direction 1: HARD growth exclude — entirely remove ticker when:
    G1: NP_TTM_YoY < 0 (any negative growth)
    G2: NP_TTM_YoY < -10% (severe decline)
    G3: NP_TTM_YoY < -20% (deep decline)

  Direction 2: TA momentum filter — skip new buys when:
    T1: Close < MA200 (below 200-day trend)
    T2: Close < MA200 × 0.85 (well below trend)
    T3: 6M return < -10%
    T4: 6M return < -15%
    T5: 6M return < 0 (any 6M decline)

  Combined: best growth + best TA stack

Backtest: LH-only standalone (50B, A+B staggered, CRISIS gated), 12y full + OOS + Q1 2026.
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, compute_metrics, _CACHE

INIT_NAV = 50e9
CASES = ["VCS", "DGC", "VNM", "FPT", "MWG"]

COMMON = dict(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
              refresh_mode="staggered", crisis_gate=True, init_nav=INIT_NAV)

VARIANTS = [
    ("BASELINE",          {"trail_pct": None}),
    # Direction 1: hard growth exclude
    ("G1_NP_neg",         {"growth_exclude": {"np_yoy_min": 0.0}}),
    ("G2_NP_lt_-10",      {"growth_exclude": {"np_yoy_min": -0.10}}),
    ("G3_NP_lt_-20",      {"growth_exclude": {"np_yoy_min": -0.20}}),
    # Direction 2: TA momentum filter
    ("T1_MA200",          {"ta_filter": {"ma200_thresh": 1.0}}),
    ("T2_MA200x085",      {"ta_filter": {"ma200_thresh": 0.85}}),
    ("T3_ret6m_lt_-10",   {"ta_filter": {"ret6m_min": -0.10}}),
    ("T4_ret6m_lt_-15",   {"ta_filter": {"ret6m_min": -0.15}}),
    ("T5_ret6m_neg",      {"ta_filter": {"ret6m_min": 0.0}}),
    ("T6_MA200+ret6m_-15", {"ta_filter": {"ma200_thresh": 1.0, "ret6m_min": -0.15}}),
    # Combined
    ("C1_G2+T4",          {"growth_exclude": {"np_yoy_min": -0.10}, "ta_filter": {"ret6m_min": -0.15}}),
    ("C2_G1+T1",          {"growth_exclude": {"np_yoy_min": 0.0}, "ta_filter": {"ma200_thresh": 1.0}}),
]

results = {}
for label, cfg in VARIANTS:
    print(f"\n→ {label}: {cfg}", flush=True)
    args = dict(COMMON)
    args.update(cfg)
    _CACHE.clear()
    res = run_lh(**args)
    results[label] = res

# ─── METRICS ─────────────────────────────────────────────────────────────
def slice_metrics(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    nav_v = INIT_NAV * s / s.iloc[0]
    return compute_metrics(nav_v, start, end)

periods = [
    ("FULL", pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("OOS_2024+", pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Q1_2026", pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
    ("Y2022", pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
]

print("\n" + "="*120)
print("LH STANDALONE RESULTS (50B, A+B staggered, CRISIS gated)")
print("="*120)
for pname, ps, pe in periods:
    print(f"\n─── {pname} ───")
    print(f"  {'Variant':<22}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}{'Calmar':>10}{'avg_pos':>10}")
    for label, _ in VARIANTS:
        m = slice_metrics(results[label]["nav"]["nav"], ps, pe)
        if m is None: continue
        avg_pos = results[label]["nav"]["n_pos"].mean()
        print(f"  {label:<22}{m['CAGR']:>+10.2%}{m['Sharpe']:>+10.2f}{m['MaxDD']:>+10.2%}{m['Calmar']:>+10.2f}{avg_pos:>+10.2f}")

# ─── 5-TICKER PICK ANALYSIS ──────────────────────────────────────────────
print("\n" + "="*120)
print("5-TICKER PICK / NO-PICK BREAKDOWN")
print("="*120)
print("How often does each variant BUY each case ticker over the 12y window?")
print(f"\n  {'Variant':<22}", end="")
for tk in CASES: print(f"{tk:>8}", end="")
print()
for label, _ in VARIANTS:
    print(f"  {label:<22}", end="")
    for tk in CASES:
        tr = results[label]["trades"]
        n_buy = (tr["ticker"]==tk).sum() if len(tr) else 0
        # Actually count buys only
        n_buy_only = ((tr["ticker"]==tk) & (tr["side"]=="BUY")).sum() if len(tr) else 0
        print(f"{n_buy_only:>8}", end="")
    print()

# ─── EXIT TIMING ON 5 CASES ──────────────────────────────────────────────
prices = pd.read_csv("data/prices_lh.csv", parse_dates=["time"])
print("\n" + "="*120)
print("5-TICKER LIFECYCLE — entry/exit timing relative to peak")
print("="*120)
for tk in CASES:
    p = prices[prices["ticker"] == tk].sort_values("time")
    peak_dt = p.loc[p["Close"].idxmax(), "time"]
    peak_px = p["Close"].max()
    print(f"\n--- {tk}  peak {peak_px:.0f} on {peak_dt.date()} ---")
    for label, _ in VARIANTS:
        tr = results[label]["trades"]
        if len(tr) == 0: continue
        tk_trades = tr[tr["ticker"] == tk]
        if len(tk_trades) == 0:
            print(f"  {label:<22}  (not picked)")
            continue
        buys = tk_trades[tk_trades["side"] == "BUY"]
        sells = tk_trades[tk_trades["side"].isin(["SELL","TRAIL_STOP"])]
        if len(buys) == 0: continue
        first_buy = buys.iloc[0]; last_sell = sells.iloc[-1] if len(sells) > 0 else None
        first_buy_to_peak = (peak_dt - first_buy["dt"]).days
        if last_sell is not None:
            last_sell_to_peak = (last_sell["dt"] - peak_dt).days
            print(f"  {label:<22}  buy {first_buy['dt'].strftime('%Y-%m-%d')} @ {first_buy['px']:>6.0f} "
                  f"(peak{first_buy_to_peak:+d}d)  exit {last_sell['dt'].strftime('%Y-%m-%d')} @ {last_sell['px']:>6.0f} "
                  f"(peak{last_sell_to_peak:+d}d) [{last_sell['side']}]")
        else:
            print(f"  {label:<22}  buy {first_buy['dt'].strftime('%Y-%m-%d')} @ {first_buy['px']:>6.0f} → STILL HOLDING")

print("\nDONE")
