#!/usr/bin/env python3
"""Stage 3 — focused LOO + DSR on winners (c4/c5 DT5G-proportional sizing). $DNA_PYEXE."""
import warnings; warnings.filterwarnings("ignore")
import os, sys, math
import pandas as pd, numpy as np
os.chdir("/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, "research/lag_regime_gate")
from lag_common import simulate_nav, metrics, _load_prices
sys.path.insert(0, ".")
from dsr_pbo_annex import moments, expected_max_sr, dsr

E = pd.read_pickle("research/lag_regime_gate/lag_events_attributed.pkl")
prices = _load_prices()

def m_state_le2(r): return 0.5 if r["dt5g_state"] <= 2 else 1.0
def m_state_le1(r): return 0.5 if r["dt5g_state"] <= 1 else 1.0
WIN = [("a_BASELINE", None), ("c4_half_state<=2", m_state_le2), ("c5_half_state<=1", m_state_le1)]

navs = {}
print("=== self-check + LOO for winners ===")
for name, mf in WIN:
    nav, tr = simulate_nav(E, prices, mult_fn=mf)
    navs[name] = nav
    neg = (nav <= 0).any()
    print(f"{name:<20} CAGR {metrics(nav)['CAGR']:.2f}%  min_NAV {nav.min():,.0f} VND  neg?={neg}  trades {len(tr)}")

base_full = metrics(navs["a_BASELINE"])["CAGR"]
print("\nLOO-by-year edge (variant CAGR − baseline CAGR, drop each year's entries):")
print(f"  {'drop':<8}{'c4':>9}{'c5':>9}")
def cagr_drop(mf, y):
    nav, _ = simulate_nav(E[E["year"] != y], prices, mult_fn=mf)
    return metrics(nav)["CAGR"]
# NONE row
print(f"  {'NONE':<8}{metrics(navs['c4_half_state<=2'])['CAGR']-base_full:>+9.2f}"
      f"{metrics(navs['c5_half_state<=1'])['CAGR']-base_full:>+9.2f}")
for y in range(2014, 2027):
    b = cagr_drop(None, y)
    e4 = cagr_drop(m_state_le2, y) - b
    e5 = cagr_drop(m_state_le1, y) - b
    print(f"  {y:<8}{e4:>+9.2f}{e5:>+9.2f}")

# ---- DSR (per-obs daily Sharpe, N_trials=10) ----
print("\n=== DSR (N_trials=10 declared) ===")
N_TRIALS = 10
for name in navs:
    r = navs[name].pct_change().dropna().values
    sr, g3, g4 = moments(pd.Series(r))
    T = len(r)
    var_sr = 1.0 / (T - 1)          # variance of SR estimate under null ~ 1/(T-1) per-obs
    sr0 = expected_max_sr(var_sr, N_TRIALS)
    p, stat = dsr(sr, sr0, g3, g4, T)
    ann = sr * math.sqrt(252)
    print(f"  {name:<20} SR/day {sr:+.4f} (ann {ann:+.2f})  skew {g3:+.2f} kurt {g4:.1f}  "
          f"sr0 {sr0:.4f}  DSR {p:.3f}")
