# -*- coding: utf-8 -*-
"""How much of an outlier is 2021, measured on the LAG sleeve itself? (Taylor_20260804_061252)

The rule only touches the LAG book (verified: `nav_bal_ref` is bit-identical across every leg), so
the sleeve's own per-year return isolates the effect with no blend/allocation noise mixed in.

Measure, per leg: the 13 annual LAG-sleeve deltas vs FIFO, their mean and sd, and where 2021 sits.
The sd across years IS the empirical year-to-year noise scale of this sleeve — no model needed.

NOTE ON A REJECTED APPROACH: a synthetic "random cohort" bootstrap (draw which candidates get funded,
compound cohort drift over the year) was written first and THROWN OUT — the concurrent-slot estimate
it needed came out at 1-3 names (implausible for a book running 56-77 entries a year), which made the
compounding explode to four-digit percentages. Reporting the cross-year sd instead: fewer assumptions,
and every input is an audited engine output.

Usage: python noise_band.py
"""
import numpy as np
import pandas as pd

PRE = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_"
       "edge_etfliqcustompitg_wtnamecap_advprice_exp_")
LEGS = ["A_dnpr_w0", "A_surprise_w0", "A_pahl3_w0", "A_fill_w0", "A_blend_w0",
        "B_surprise_w5", "B_pahl3_w5", "B_blend_w5", "B_dnpr_w5", "B_fill_w5"]
YEARS = list(range(2014, 2027))


def sleeve(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["date"] = pd.to_datetime(d["ymd"])
    d = d.sort_values("date").set_index("date")
    out = {}
    for y in YEARS:
        s = d.loc[d.index.year == y, "nav_lag_ref"].dropna()
        if len(s) > 5:
            out[y] = (s.iloc[-1] / s.iloc[0] - 1) * 100
    return out


for scale, suf, basef in (("1B", "_1B_univpit_nav1B.csv", "L0_ctrl1B_univpit_nav1B.csv"),
                          ("50B", "_50B_univpit.csv", "L0_ctrl50B_univpit.csv")):
    b = sleeve(PRE + basef)
    print(f"\n=== NAV {scale} — LAG-sleeve annual return delta vs FIFO (pp) ===")
    print(f"{'leg':<15}" + "".join(f"{y:>7}" for y in YEARS) +
          f"{'mean':>8}{'sd':>7}{'z(2021)':>9}")
    tab = {}
    for lab in LEGS:
        t = sleeve(PRE + lab + suf)
        d = {y: t[y] - b[y] for y in YEARS if y in t and y in b}
        v = np.array(list(d.values()))
        mu, sd = v.mean(), v.std(ddof=1)
        z21 = (d[2021] - mu) / sd if 2021 in d else np.nan
        tab[lab] = d
        print(f"{lab:<15}" + "".join(f"{d.get(y, float('nan')):7.1f}" for y in YEARS) +
              f"{mu:8.2f}{sd:7.2f}{z21:9.2f}")
    ex = {lab: [v for y, v in d.items() if y != 2021] for lab, d in tab.items()}
    print(f"\n  mean delta INCLUDING 2021: {np.mean([np.mean(list(d.values())) for d in tab.values()]):+.2f}pp"
          f"   |   EXCLUDING 2021: {np.mean([np.mean(v) for v in ex.values()]):+.2f}pp")
    n_pos_in = sum(1 for d in tab.values() if np.mean(list(d.values())) > 0)
    n_pos_ex = sum(1 for v in ex.values() if np.mean(v) > 0)
    print(f"  legs with a positive MEAN annual sleeve delta: {n_pos_in}/10 with 2021, "
          f"{n_pos_ex}/10 without 2021")
