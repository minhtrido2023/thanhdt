# -*- coding: utf-8 -*-
"""LAG forward-window ranking — per-year leave-one-out (job Taylor_20260804_051145).

ZERO re-run: reads only the frozen DAILY combined_nav series of a baseline CSV and one or more
treatment CSVs. Method is a verbatim reuse of `loo_h8a_dnpr.py` (2026-07-05) so this job's LOO is
directly comparable to the Wave1/H8a LOO that closed the same mechanism's same-day form:
  - metrics from chained daily returns, Sharpe x sqrt(252), Calmar = CAGR/|MaxDD|
  - LOO annualises by retained-return-count / spy, spy estimated once from the FULL OOS calendar
    span (constant across subsets, so the treatment-minus-baseline delta is method-invariant)
Usage: python loo_lagrank.py <base.csv> <label>=<trt.csv> [...]
"""
import sys, pandas as pd, numpy as np

OOS_START = pd.Timestamp("2020-01-01")


def load_daily(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["date"] = pd.to_datetime(d["ymd"])
    return d.sort_values("date").set_index("date")["combined_nav"].astype(float)


base_s = load_daily(sys.argv[1])
trts = [(a.split("=", 1)[0], load_daily(a.split("=", 1)[1])) for a in sys.argv[2:]]

b_oos = base_s[base_s.index >= OOS_START]
oos_years = (b_oos.index[-1] - b_oos.index[0]).days / 365.25
spy = (len(b_oos) - 1) / oos_years
print(f"OOS {b_oos.index[0].date()} -> {b_oos.index[-1].date()}  years {oos_years:.2f}  spy {spy:.1f}\n")


def met(r):
    r = r.dropna()
    nav = (1 + r).cumprod()
    yrs = len(r) / spy
    cagr = nav.iloc[-1] ** (1 / yrs) - 1
    maxdd = (nav / nav.cummax() - 1).min()
    return cagr * 100, (cagr / abs(maxdd) if maxdd < 0 else 0)


base_r = b_oos.pct_change().dropna()
YEARS = sorted(set(base_r.index.year))

for label, t in trts:
    t_oos = t[t.index >= OOS_START]
    t_r = t_oos.pct_change().dropna()
    ri = base_r.index.intersection(t_r.index)
    br, tr = base_r.loc[ri], t_r.loc[ri]

    def row(name, drop):
        m = ~br.index.year.isin(drop)
        b, tt = met(br[m]), met(tr[m])
        return (f"  {name:<22} base {b[0]:6.2f}%/{b[1]:4.2f}  trt {tt[0]:6.2f}%/{tt[1]:4.2f}  "
                f"Δ {tt[0]-b[0]:+6.2f}pp / {tt[1]-b[1]:+5.2f}", tt[0] - b[0])

    print(f"=== {label} — OOS per-year leave-one-out (CAGR%/Calmar) ===")
    full_txt, full_d = row("full OOS", [])
    print(full_txt)
    deltas = {}
    for y in YEARS:
        txt, d = row(f"drop {y}", [y])
        deltas[y] = d
        print(txt)
    # the two years that carry the most edge, dropped together (the H8a "core test")
    top2 = sorted(deltas, key=lambda y: deltas[y])[:2]
    txt, d2 = row(f"drop {top2[0]}+{top2[1]}", top2)
    print(txt)
    n_pos = sum(1 for v in deltas.values() if v > 0)
    print(f"  -> full-OOS Δ {full_d:+.2f}pp | drop-one-year Δ POSITIVE in {n_pos}/{len(deltas)} years | "
          f"core test (drop {top2[0]}+{top2[1]}) Δ {d2:+.2f}pp"
          f"  => {'ROBUST' if (d2 > 0 and n_pos >= len(deltas)-1) else 'LUMPY / carried by a few years'}\n")
