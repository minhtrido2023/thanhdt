#!/usr/bin/env python3
"""probe_fscore_select.py — fast pre-backtest proxy for thread (a): does adding FSCORE to the
custom30V yieldcombo selection score [rank(1/PE)+rank(1/PCF)] lift the SELECTED basket's forward
return? Mini-backtest proxy on the frozen PIT panel (no NAV sim): per quarter, within the as-of
rating<=3 gate, take the top-60 by liquidity (turnover) as the tradable pool (mirrors CFO_POOL=60),
pick top-30 by each score variant, equal-weight mean profit_2M. Average across quarters + IS/OOS.
NOT the production NAV backtest (no T+1/costs/weights) — a directional screen to decide if the full
pt_v23 backtest is worth running and which FS_W to try. Faithful inputs via ic_panel_8l.load().
Usage: source ./wc_env.sh && $DNA_PYEXE probe_fscore_select.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import load

POOL_N, PICK_N = 60, 30
TGT = "profit_2M"

def main():
    d = load()
    d = d[(d["rating"] <= 3)].copy()                       # the gated investable set V2.4 acts within
    d["liq"] = pd.to_numeric(d.get("turnover"), errors="coerce")
    d = d[d["liq"].notna() & d[TGT].notna()]
    rk = lambda s: s.rank(pct=True)
    # selection score variants: base = yieldcombo [rank(1/PE)+rank(1/PCF)]; + w*rank(FSCORE)
    WEIGHTS = [0.0, 0.25, 0.5, 0.75, 1.0]
    rows = []
    perq = {w: [] for w in WEIGHTS}; perq_yr = {w: [] for w in WEIGHTS}
    nq = 0
    for q, g in d.groupby("q"):
        g = g.sort_values("liq", ascending=False).head(POOL_N)      # tradable pool (top-60 liquid gated)
        if len(g) < PICK_N + 5: continue
        ey_v  = pd.Series(np.where(g["PE"]  > 0, 1.0/g["PE"],  np.nan), index=g.index)
        cfy_v = pd.Series(np.where(g["PCF"] > 0, 1.0/g["PCF"], np.nan), index=g.index)
        ey  = rk(ey_v).fillna(0.5)
        cfy = rk(cfy_v).fillna(0.5)
        fs  = pd.Series(rk(pd.to_numeric(g["FSCORE"], errors="coerce")), index=g.index).fillna(0.5)
        base = ey + cfy
        nq += 1
        for w in WEIGHTS:
            score = base + w * fs
            pick = g.loc[score.sort_values(ascending=False).head(PICK_N).index]
            m = pick[TGT].mean()
            perq[w].append(m); perq_yr[w].append((q.year, m))
    print(f"selected-basket forward {TGT} (equal-weight top-{PICK_N} of top-{POOL_N} liquid, gate rating<=3), {nq} quarters\n")
    print(f"{'FS_W':>6} {'mean_fwd2M%':>11} {'vs base':>9} {'IS(14-19)':>10} {'OOS(20+)':>9} {'win%q':>6}")
    base_mean = np.mean(perq[0.0])
    for w in WEIGHTS:
        arr = np.array(perq[w]); ys = perq_yr[w]
        isv  = np.mean([m for (y, m) in ys if y <= 2019])
        oosv = np.mean([m for (y, m) in ys if y >= 2020])
        # quarter-level win vs base
        winq = np.mean([1.0 if a > b else 0.0 for a, b in zip(perq[w], perq[0.0])]) if w != 0 else np.nan
        d_ = arr.mean() - base_mean
        print(f"{w:>6.2f} {arr.mean():>11.2f} {d_:>+9.2f} {isv:>10.2f} {oosv:>9.2f} "
              f"{('  -  ' if w==0 else f'{winq:>5.0%}')}")
    print("\nNOTE: directional proxy (no NAV sim/costs). If +FS_W lifts mean & both IS/OOS, the full")
    print("pt_v23 backtest (BASKET_FS_W knob in custom_basket yieldcombo) is worth running.")

if __name__ == "__main__":
    main()
