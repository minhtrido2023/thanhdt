#!/usr/bin/env python3
"""
test_lh_v2_variants.py
======================
Tune LH v2c exit triggers to LET WINNERS RUN.

Variants:
  v2c_orig: original (TB=5d, trail=25%/+20%act, CRISIS_LOCK at +30%)
  v2c_no_crisis: drop CRISIS_LOCK
  v2c_slow_tb: trend_break needs 20d confirmation
  v2c_loose_trail: trail=35% (or disabled)
  v2c_combined: drop CRISIS_LOCK + slow_tb=20d + trail=35% activate at +50%
  v2c_pure_fa: only FA drop + MA200 break (drop trail + CRISIS)
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_v2 import run_lh_v2, _CACHE, compute_metrics

INIT_NAV = 50e9

VARIANTS = [
    ("v2c_orig",        dict()),
    ("v2c_no_crisis",   dict(crisis_lock_gain=99.0)),  # effectively disabled
    ("v2c_slow_tb20",   dict(trend_break_days=20, crisis_lock_gain=99.0)),
    ("v2c_loose_trail", dict(trail_pct=0.35, trail_activation=0.50, crisis_lock_gain=99.0)),
    ("v2c_pure_FA",     dict(trail_pct=0.99, crisis_lock_gain=99.0, trend_break_days=99)),  # only FA exit
    ("v2c_combined",    dict(trend_break_days=20, trail_pct=0.35, trail_activation=0.50, crisis_lock_gain=99.0)),
]

for label, cfg in VARIANTS:
    _CACHE.clear()
    res = run_lh_v2(init_nav=INIT_NAV, **cfg)
    m = res["metrics"]
    nav = res["nav"]["nav"]
    print(f"\n--- {label} ---  args: {cfg}")
    print(f"  12y: CAGR={m['CAGR']*100:.2f}%  Sharpe={m['Sharpe']:.2f}  DD={m['MaxDD']*100:.2f}%  Calmar={m['Calmar']:.2f}  avg_pos={m['avg_n_pos']:.2f}  n_trades={m['n_trades']}")
    # slices
    for w_name, ws, we in [("OOS_2024+","2024-01-01","2026-05-13"),
                            ("Y2022","2022-01-01","2022-12-31"),
                            ("Q1_2026","2025-12-30","2026-03-30")]:
        s = nav[(nav.index >= ws) & (nav.index <= we)]
        if len(s) < 30: continue
        mw = compute_metrics(INIT_NAV * s/s.iloc[0], pd.Timestamp(ws), pd.Timestamp(we))
        print(f"  {w_name:<10}: CAGR={mw['CAGR']*100:+.2f}%  Sharpe={mw['Sharpe']:+.2f}  DD={mw['MaxDD']*100:+.2f}%")
    # Exit breakdown
    tr = res["trades"]
    exits = tr[tr["side"] != "BUY"]["side"].value_counts().to_dict()
    print(f"  Exits: {exits}")
