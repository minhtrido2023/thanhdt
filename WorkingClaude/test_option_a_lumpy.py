#!/usr/bin/env python3
"""
test_option_a_lumpy.py
======================
Test Option A: lumpy initial deploy (all 10 positions at first rebal, then 4Q lumpy rotation).

Compare:
  - Staggered (corrected sizing) — current production candidate
  - Lumpy (all-at-once, refresh_mode="lumpy")

Two scenarios:
  - Full 12y backtest (50B canonical)
  - Fresh start 2025-06-01 (25B for LH = 50% of 50B hybrid)
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, compute_metrics, _CACHE

INIT_NAV_FULL = 50e9
INIT_NAV_FRESH = 25e9

def metrics_window(nav, start, end, init_nav):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    nav_v = init_nav * s / s.iloc[0]
    return compute_metrics(nav_v, start, end)

print("="*100)
print("  PART 1 — FULL 12y BACKTEST: staggered vs lumpy")
print("="*100)

modes = [("staggered", "staggered"), ("lumpy", "lumpy")]
for label, mode in modes:
    _CACHE.clear()
    res = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                  refresh_mode=mode, crisis_gate=True, init_nav=INIT_NAV_FULL)
    m = res["metrics"]
    nav = res["nav"]["nav"]
    print(f"\n--- {label} mode (corrected sizing) ---")
    print(f"  full 12y: CAGR={m['CAGR']*100:.2f}%  Sharpe={m['Sharpe']:.2f}  MaxDD={m['MaxDD']*100:.2f}%  Calmar={m['Calmar']:.2f}")
    print(f"  avg_n_pos={m['avg_n_pos']:.2f}  n_trades={m['n_trades']}")
    for w_name, ws, we in [("PRE_2024","2014-04-01","2023-12-31"),
                            ("OOS_2024+","2024-01-01","2026-05-13"),
                            ("Y2022","2022-01-01","2022-12-31"),
                            ("Q1_2026","2025-12-30","2026-03-30")]:
        mw = metrics_window(nav, pd.Timestamp(ws), pd.Timestamp(we), INIT_NAV_FULL)
        if mw: print(f"  {w_name:<10}: CAGR={mw['CAGR']*100:+.2f}%  Sharpe={mw['Sharpe']:+.2f}  DD={mw['MaxDD']*100:+.2f}%")

print("\n\n" + "="*100)
print("  PART 2 — FRESH START 2025-06-01 (25B LH leg): staggered vs lumpy")
print("="*100)

for label, mode in modes:
    _CACHE.clear()
    res = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                  refresh_mode=mode, crisis_gate=True, init_nav=INIT_NAV_FRESH,
                  start="2025-06-01", end="2026-05-15")
    m = res["metrics"]
    nav = res["nav"]["nav"]
    trades = res["trades"]
    print(f"\n--- {label} mode (fresh start) ---")
    print(f"  Final NAV: {nav.iloc[-1]/1e9:.3f}B ({(nav.iloc[-1]/INIT_NAV_FRESH - 1)*100:+.2f}%)")
    print(f"  avg_n_pos: {m['avg_n_pos']:.2f}")
    print(f"  n_trades: {len(trades)} ({(trades['side']=='BUY').sum() if len(trades)>0 else 0} buys)")
    if len(trades) > 0:
        print("  Trades:")
        for _, t in trades.sort_values("dt").iterrows():
            print(f"    {t['dt'].strftime('%Y-%m-%d')}  {t['side']:<5}{t['ticker']:<6}{t['px']:>8.0f}  cohort={t.get('q','')}")

    # Monthly NAV trajectory
    print("  Monthly NAV:")
    months = pd.date_range("2025-06-30", "2026-04-30", freq="ME")
    for dt in months:
        sub = nav[nav.index <= dt]
        if len(sub) == 0: continue
        actual = sub.index[-1]
        npos = int(res["nav"]["n_pos"].loc[actual])
        cash = res["nav"]["cash"].loc[actual]
        nav_v = sub.iloc[-1]
        chg = (nav_v / INIT_NAV_FRESH - 1) * 100
        deploy = (1 - cash/nav_v) * 100
        print(f"    {actual.strftime('%Y-%m-%d')}: NAV={nav_v/1e9:.2f}B ({chg:+.2f}%), n_pos={npos}, deploy={deploy:.0f}%")

print("\nDONE")
