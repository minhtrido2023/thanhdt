#!/usr/bin/env python3
"""probe_select_variants.py — (b) fast proxy: does adding PCF and/or PS to the production yieldcombo
selection help the CONCENTRATED top-30 pick (vs ey alone)? Mirrors custom30V: within as-of rating<=3
gate, top-60 by liquidity (turnover) pool, pick top-30 by each score, equal-wt mean profit_2M, IS/OOS.
Variants: ey_only=rank(1/PE) | yieldcombo=rank(1/PE)+rank(1/PCF) [PROD] | +ps=+rank(1/PS).
The full route-aware v3 composite is tested separately by the real pt_v23 backtest (BASKET_SELECT=v3latest).
Usage: source ./wc_env.sh && $DNA_PYEXE probe_select_variants.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import load

POOL_N, PICK_N, TGT = 60, 30, "profit_2M"

def main():
    d = load()
    d = d[d["rating"] <= 3].copy()
    d["liq"] = pd.to_numeric(d.get("turnover"), errors="coerce")
    d = d[d["liq"].notna() & d[TGT].notna()]
    rk = lambda s: s.rank(pct=True)
    VARIANTS = ["ey_only", "yieldcombo", "+ps"]
    perq = {v: [] for v in VARIANTS}; perq_yr = {v: [] for v in VARIANTS}
    nq = 0
    for q, g in d.groupby("q"):
        g = g.sort_values("liq", ascending=False).head(POOL_N)
        if len(g) < PICK_N + 5: continue
        ey  = rk(pd.Series(np.where(g["PE"]  > 0, 1.0/g["PE"],  np.nan), index=g.index)).fillna(0.5)
        cfy = rk(pd.Series(np.where(g["PCF"] > 0, 1.0/g["PCF"], np.nan), index=g.index)).fillna(0.5)
        ps  = rk(pd.Series(np.where(g["PS"]  > 0, 1.0/g["PS"],  np.nan), index=g.index)).fillna(0.5)
        scores = {"ey_only": ey, "yieldcombo": ey + cfy, "+ps": ey + cfy + ps}
        nq += 1
        for v in VARIANTS:
            pick = g.loc[scores[v].sort_values(ascending=False).head(PICK_N).index]
            perq[v].append(pick[TGT].mean()); perq_yr[v].append((q.year, pick[TGT].mean()))
    print(f"selected-basket forward {TGT} (eq-wt top-{PICK_N} of top-{POOL_N} liquid, gate<=3), {nq} quarters\n")
    print(f"{'variant':12} {'mean%':>7} {'vs combo':>9} {'IS%':>7} {'OOS%':>7} {'win%q vs combo':>15}")
    base = np.mean(perq["yieldcombo"])
    for v in VARIANTS:
        arr = np.array(perq[v]); ys = perq_yr[v]
        isv  = np.mean([m for (y, m) in ys if y <= 2019]); oosv = np.mean([m for (y, m) in ys if y >= 2020])
        winq = np.mean([1.0 if a > b else 0.0 for a, b in zip(perq[v], perq["yieldcombo"])])
        print(f"{v:12} {arr.mean():>7.2f} {arr.mean()-base:>+9.2f} {isv:>7.2f} {oosv:>7.2f} "
              f"{('  -  ' if v=='yieldcombo' else f'{winq:>13.0%}')}")
    print("\nread: if ey_only ~= yieldcombo ~= +ps, the extra lenses don't earn their keep in the")
    print("concentrated pick -> keep simple. Real v3 composite verdict = pt_v23 BASKET_SELECT=v3latest.")

if __name__ == "__main__":
    main()
