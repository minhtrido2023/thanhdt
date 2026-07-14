# -*- coding: utf-8 -*-
"""route_placebo.py — count-matched placebo for the v3route* family (job Taylor_20260714_121717).

The three route arms differ from the yieldcombo baseline in exactly one measurable way at the cut:
they hold FEWER financial names (9.27/30 -> 5.08/6.19/6.54). If a RANDOM financial underweight of the
same size, quarter by quarter, buys the same spread, then "route-aware repricing" is a costume on a
blind sector bet and WHICH banks get dropped is irrelevant.

Placebo = baseline yieldcombo ranking + exactly the real arm's financial count per rebal, with WHICH
financials kept chosen at random. 20 seeds. Same pattern as the DCF Pha-4 placebo.

Run: $DNA_PYEXE mike/agents/Taylor/route_exp/route_placebo.py [arm]   (default arm = v3route3)
"""
import os, sys
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq  # noqa: E402
import custom_basket as cb  # noqa: E402

ARM = sys.argv[1] if len(sys.argv) > 1 else "v3route3"
N_SEEDS = 20
START, END = "2014-01-02", "2026-06-19"
OUT = os.path.dirname(os.path.abspath(__file__))
FIN = {"BANK", "INSURANCE", "SECURITIES"}

PANEL = pd.read_csv(os.path.join(WORKDIR, "data", "value_panel_2014.csv"), parse_dates=["time"])
PANEL["qstart"] = PANEL["time"].dt.to_period("Q").dt.start_time
ROUTE = PANEL.sort_values("time").groupby("ticker")["route"].last().to_dict()


def build(mode, placebo=None):
    _save = {k: os.environ.get(k) for k in ("BASKET_SELECT", "BASKET_PLACEBO_FIN")}
    os.environ["BASKET_SELECT"] = mode
    if placebo: os.environ["BASKET_PLACEBO_FIN"] = placebo
    else: os.environ.pop("BASKET_PLACEBO_FIN", None)
    try:
        lvl, adv, mem, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                         gate_rating=3, weight_scheme="namecap",
                                         top_n=30, name_cap=0.10, qtilt=None)
    finally:
        for k, v in _save.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v
    s = pd.Series(lvl); s.index = pd.to_datetime(s.index)
    return s.sort_index(), mem


def cagr(s):
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    return 100 * ((s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1)


def maxdd(s):
    return 100 * (s / s.cummax() - 1).min()


# ---- 1. the real arm's financial count per rebal -> the placebo's count schedule ----
mem_arm = pd.read_csv(os.path.join(OUT, f"members_{ARM}.csv"), parse_dates=["rebal_date"])
mem_arm["route"] = mem_arm.ticker.map(ROUTE).fillna("?")
counts = (mem_arm.groupby("rebal_date").apply(lambda g: int(g.route.isin(FIN).sum()))
          .rename("n_fin").reset_index())
CPATH = os.path.join(OUT, f"placebo_counts_{ARM}.csv")
counts.to_csv(CPATH, index=False)
print(f"count schedule from {ARM}: {len(counts)} rebals, financial names/30 "
      f"mean {counts.n_fin.mean():.2f} (min {counts.n_fin.min()}, max {counts.n_fin.max()}) -> {CPATH}")

# ---- 2. reference levels ----
base = pd.read_csv(os.path.join(OUT, "vehicle_level_yieldcombo.csv"), parse_dates=["time"]).set_index("time").level
arm = pd.read_csv(os.path.join(OUT, f"vehicle_level_{ARM}.csv"), parse_dates=["time"]).set_index("time").level
C_BASE, C_ARM = cagr(base), cagr(arm)
print(f"\nreference: yieldcombo {C_BASE:.2f}%  |  {ARM} {C_ARM:.2f}%  |  real edge {C_ARM-C_BASE:+.2f}pp")

# ---- 3. placebo runs ----
print(f"\nrunning {N_SEEDS} count-matched placebo seeds (random financials, same count)...")
rows = []
for seed in range(N_SEEDS):
    lvl, mem = build("yieldcombo", placebo=f"{seed}:{CPATH}")
    m = mem.copy(); m["route"] = m.ticker.map(ROUTE).fillna("?")
    nf = m.groupby("rebal_date").apply(lambda g: g.route.isin(FIN).sum()).mean()
    c = cagr(lvl)
    rows.append(dict(seed=seed, CAGR=c, edge=c - C_BASE, MaxDD=maxdd(lvl), fin_per30=nf))
    print(f"  seed {seed:2d}: CAGR {c:6.2f}%  edge {c-C_BASE:+6.2f}pp  DD {maxdd(lvl):6.2f}%  fin {nf:.2f}/30")

P = pd.DataFrame(rows)
P.to_csv(os.path.join(OUT, f"placebo_{ARM}.csv"), index=False)

real_edge = C_ARM - C_BASE
print("\n" + "=" * 90)
print(f"PLACEBO RESULT — {ARM} vs {N_SEEDS} count-matched random-financial baskets")
print("=" * 90)
print(f"  placebo edge: mean {P.edge.mean():+.2f}pp | median {P.edge.median():+.2f}pp | "
      f"sd {P.edge.std():.2f} | min {P.edge.min():+.2f} | max {P.edge.max():+.2f}")
print(f"  REAL edge   : {real_edge:+.2f}pp")
pctile = (P.edge < real_edge).mean()
z = (real_edge - P.edge.mean()) / P.edge.std() if P.edge.std() > 0 else np.nan
print(f"  real edge beats {pctile:.0%} of placebos   (z = {z:+.2f})")
print(f"  fraction of the real edge reproduced by a RANDOM financial underweight: "
      f"{P.edge.mean()/real_edge:.0%}")
print("\n  VERDICT: " + (
    "PLACEBO REPRODUCES IT -> the edge is a blind financial underweight, not route-aware repricing."
    if P.edge.mean() >= 0.6 * real_edge else
    "placebo does NOT reproduce it -> WHICH names are dropped carries real information."))
print("\nDONE — artifacts in", OUT)
