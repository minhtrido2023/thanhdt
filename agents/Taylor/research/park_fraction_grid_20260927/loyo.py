#!/usr/bin/env python3
"""Leave-one-calendar-year-out on each leg's daily NAV (PREREG §4c).

Drop every session of one calendar year, splice the remaining daily simple returns into one
chain, recompute CAGR / Sharpe / MaxDD / Calmar on it. Calendar years are annualized with the
leg's own sessions-per-calendar-year rate (same convention as bootstrap_nav.py, which reports
249.3 obs/yr on this ledger) so dropping a year shortens the horizon consistently.
Question answered: does the Calmar ranking across park levels survive removing any single year,
or is the winner an artefact of one year (= reshuffle luck)?
Usage: loyo.py <csv> [<csv> ...]
"""
import sys, pandas as pd, numpy as np

def nav_of(p):
    df = pd.read_csv(p, low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    return d.groupby(d["ymd"].dt.normalize())["combined_nav"].last().astype(float)

def metrics(ret, yrs):
    nav = np.cumprod(1 + ret)
    cagr = nav[-1] ** (1 / yrs) - 1
    mdd = (nav / np.maximum.accumulate(nav) - 1).min()
    sd = ret.std(ddof=1)
    sr = ret.mean() / sd * np.sqrt(len(ret) / yrs) if sd > 0 else np.nan
    return cagr * 100, sr, mdd * 100, (cagr / abs(mdd) if mdd < 0 else np.nan)

legs = {p.split("_exp_parkgrid_")[1].split("_univpit")[0]: nav_of(p) for p in sys.argv[1:]}
res = {}
for lab, nav in legs.items():
    ret = nav.pct_change().dropna()
    obs_per_yr = len(nav) / ((nav.index[-1] - nav.index[0]).days / 365.25)
    years = sorted(nav.index.year.unique())
    for drop in ["none"] + [str(y) for y in years]:
        r = ret if drop == "none" else ret[ret.index.year != int(drop)]
        res[(lab, drop)] = metrics(r.values, len(r) / obs_per_yr)

labs = list(legs)
drops = ["none"] + [str(y) for y in sorted(next(iter(legs.values())).index.year.unique())]
print("drop   " + "".join(f"{'x='+l:>28s}" for l in labs))
print("       " + "".join(f"{'CAGR%':>8s}{'MaxDD%':>8s}{'Sharpe':>7s}{'Calmar':>7s}" for _ in labs))
for d in drops:
    print(f"{d:6s} " + "".join(f"{res[(l,d)][0]:8.2f}{res[(l,d)][2]:8.1f}{res[(l,d)][1]:7.2f}{res[(l,d)][3]:7.3f}" for l in labs))
print("\nCalmar winner per dropped year (PREREG §4c: >1 switch => reshuffle-luck):")
wins = {}
for d in drops:
    v = {l: res[(l, d)][3] for l in labs}
    w = max(v, key=lambda l: v[l])
    wins[d] = w
    print(f"  drop {d:6s} -> x={w:4s}   " + "  ".join(f"{l}:{v[l]:.3f}" for l in labs))
from collections import Counter
c = Counter(wins[d] for d in drops if d != "none")
print(f"\nwinner counts over {len(drops)-1} leave-one-year-out runs: {dict(c)}")
print(f"switches away from the full-sample winner (x={wins['none']}): "
      f"{sum(1 for d in drops if d!='none' and wins[d]!=wins['none'])}/{len(drops)-1}")
