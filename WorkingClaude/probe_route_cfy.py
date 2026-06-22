#!/usr/bin/env python3
"""probe_route_cfy.py — (c1) verify the per-route value-lens IC with IS/OOS split, esp. the
SECURITIES cfy=+0.246 lead. Reuses ic_panel_8l.load() (faithful PIT panel). Pooled per-route IC
+ IS(2014-19)/OOS(2020+), for ey & cfy & ps. Usage: source ./wc_env.sh && $DNA_PYEXE probe_route_cfy.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import load, ic_series, summ, N_MIN

TGT = "profit_2M"

def route_ic(d, lens, route, sub=None):
    m = d["route"] == route
    if sub is not None: m = m & sub
    ics, n = ic_series(d, lens, TGT, m)
    return summ(ics)["ic"], summ(ics)["n"], n

def main():
    d = load()
    d["yr"] = d["q"].dt.year
    IS, OOS = d["yr"] <= 2019, d["yr"] >= 2020
    fmt = lambda v: f"{v:+.3f}" if pd.notna(v) else "  -  "
    print(f"per-route raw IC ({TGT}), pooled + IS/OOS — N_MIN={N_MIN}/quarter\n")
    print(f"{'route':11} {'lens':5} | {'IC_all':>7} {'nq':>3} {'avgN':>5} | {'IC_IS':>7} {'IC_OOS':>7}")
    for rt in ["SECURITIES","BANK","CYCLICAL","COMPOUNDER","POWER","REALESTATE","INSURANCE"]:
        for L in ["ey","cfy","ps"]:
            ic, nq, avgn = route_ic(d, L, rt)
            icis  = route_ic(d, L, rt, IS)[0]
            icoos = route_ic(d, L, rt, OOS)[0]
            print(f"{rt:11} {L:5} | {fmt(ic):>7} {nq:>3} {avgn:>5.0f} | {fmt(icis):>7} {fmt(icoos):>7}")
        print()

if __name__ == "__main__":
    main()
