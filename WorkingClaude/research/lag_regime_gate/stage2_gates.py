#!/usr/bin/env python3
"""Stage 2 — Q3 gate NAV backtests (baseline / quality / regime / combo) with
IS-OOS + LOO-by-year. Run with $DNA_PYEXE."""
import warnings; warnings.filterwarnings("ignore")
import os, sys
import pandas as pd, numpy as np
os.chdir("/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, "research/lag_regime_gate")
from lag_common import build_events, simulate_nav, metrics, SIM_START, SIM_END

# load cached attributed events; rebuild prices only (fast-ish)
import pickle
E = pd.read_pickle("research/lag_regime_gate/lag_events_attributed.pkl")
from lag_common import _load_prices
prices = _load_prices()

# ---- gate definitions: (name, admit_fn or None, mult_fn or None) ----
def q_admit(r):   return r["rating"] <= 3                      # name-quality gate
def below_ma200(r): return 0.5 if r["vni_vs_ma200"] < 0 else 1.0
def neg_6m(r):    return 0.5 if r["vni_6m"] < 0 else 1.0
def deep_dd_skip(r): return 0.0 if r["vni_dd"] <= -20 else 1.0
def state_le2(r): return 0.5 if r["dt5g_state"] <= 2 else 1.0   # BEAR / low-neutral half
def state_le1(r): return 0.5 if r["dt5g_state"] <= 1 else 1.0   # BEAR/CRISIS half

def combo_admit(r): return r["rating"] <= 3
def combo_mult(r):  return 0.5 if r["vni_vs_ma200"] < 0 else 1.0

VARIANTS = [
    ("a_BASELINE",          None,        None),
    ("b_QUALITY_rate<=3",   q_admit,     None),
    ("c1_half_belowMA200",  None,        below_ma200),
    ("c2_half_neg6m",       None,        neg_6m),
    ("c3_skip_deepDD<=-20", None,        deep_dd_skip),
    ("c4_half_state<=2",    None,        state_le2),
    ("c5_half_state<=1",    None,        state_le1),
    ("d_QUAL+halfMA200",    combo_admit, combo_mult),
]

def full(nav):
    m = metrics(nav); return m

def window(nav, y1, y2):
    n = nav[(nav.index.year >= y1) & (nav.index.year <= y2)]
    return metrics(n)

print("="*104)
print("  Q3 — GATE VARIANTS: full-period + IS(2014-19)/OOS(2020-26) NAV metrics")
print("="*104)
print(f"  {'variant':<22}{'CAGR':>8}{'Shrp':>7}{'MaxDD':>8}{'Calm':>7}"
      f"{'|OOS_CAGR':>10}{'OOS_Shrp':>9}{'OOS_Calm':>9}{'|trades':>8}")
print("  " + "-"*100)
navs = {}
for name, af, mf in VARIANTS:
    nav, tr = simulate_nav(E, prices, admit_fn=af, mult_fn=mf)
    navs[name] = nav
    f = full(nav); o = window(nav, 2020, 2026)
    print(f"  {name:<22}{f['CAGR']:>7.2f}%{f['Sharpe']:>7.2f}{f['MaxDD']:>7.1f}%{f['Calmar']:>7.2f}"
          f"{o['CAGR']:>9.2f}%{o['Sharpe']:>9.2f}{o['Calmar']:>9.2f}{len(tr):>8}")

# IS window too, for the shortlist
print("\n  IS(2014-2019) window:")
print(f"  {'variant':<22}{'IS_CAGR':>9}{'IS_Shrp':>9}{'IS_Calm':>9}")
for name in navs:
    i = window(navs[name], 2014, 2019)
    print(f"  {name:<22}{i['CAGR']:>8.2f}%{i['Sharpe']:>9.2f}{i['Calmar']:>9.2f}")

# ---- LOO-by-year: full-period CAGR of variant minus baseline, dropping each year ----
print("\n" + "="*104)
print("  LOO-by-year: (variant CAGR − baseline CAGR), full period with one year's TRADES removed")
print("  (edge must stay same-sign across all drops → not carried by 1-2 years)")
print("="*104)
base_nav = navs["a_BASELINE"]
def cagr_drop_year(name, drop_y):
    # recompute NAV over sim window but exclude entries in drop_y
    Efilt = E[E["year"] != drop_y]
    af = dict(VARIANTS_MAP)[name][0]; mf = dict(VARIANTS_MAP)[name][1]
    nav, _ = simulate_nav(Efilt, prices, admit_fn=af, mult_fn=mf)
    return metrics(nav)["CAGR"]

VARIANTS_MAP = {n: (af, mf) for n, af, mf in VARIANTS}
shortlist = ["b_QUALITY_rate<=3", "c1_half_belowMA200", "c2_half_neg6m", "d_QUAL+halfMA200"]
years = list(range(2014, 2027))
print(f"  {'drop_yr':<9}" + "".join(f"{s.split('_')[0]:>10}" for s in shortlist))
# full (no drop) baseline & variant
base_full = metrics(base_nav)["CAGR"]
full_edges = {}
for s in shortlist:
    full_edges[s] = metrics(navs[s])["CAGR"] - base_full
print(f"  {'NONE':<9}" + "".join(f"{full_edges[s]:>+9.2f}" for s in shortlist))
for y in years:
    base_y = cagr_drop_year("a_BASELINE", y)
    row = []
    for s in shortlist:
        var_y = cagr_drop_year(s, y)
        row.append(var_y - base_y)
    print(f"  {y:<9}" + "".join(f"{e:>+9.2f}" for e in row))

# ---- per-year event-level: does quality gate & regime gate help each year? ----
print("\n  Per-year event-level avg post_ret: baseline vs rating<=3 vs (rating<=3 & aboveMA200):")
print(f"  {'yr':<6}{'base':>9}{'rate<=3':>10}{'q+aboveMA':>11}{'N_base':>8}")
for y in years:
    g = E[E["year"] == y]
    if len(g) < 10: continue
    b = g["post_ret"].mean()
    q = g[g["rating"] <= 3]["post_ret"].mean()
    qm = g[(g["rating"] <= 3) & (g["vni_vs_ma200"] >= 0)]["post_ret"].mean()
    print(f"  {y:<6}{b:>+8.2f}%{q:>+9.2f}%{qm:>+10.2f}%{len(g):>8}")
