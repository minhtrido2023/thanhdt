#!/usr/bin/env python3
"""probe_fscore_exclude.py — H1 (R&D Q3 program) pre-backtest proxy: FSCORE BOTTOM-EXCLUSION gate,
NOT the additive FSCORE-tilt that thread (a) already refuted (registry: -0.27..-0.46pp all weights).
Piotroski (2000) alpha lives in AVOIDING low-F names, not in tilting toward high-F. So here we test
an EXCLUSION-GATE: within the top-60 liquid gated pool each quarter, DROP the bottom-q by FSCORE
BEFORE ranking yieldcombo = rank(1/PE)+rank(1/PCF), then pick top-30 as usual.

q in {10%, 20%} only (2 points, NOT a grid-sweep). Compared to base (no exclusion) on the same
frozen PIT panel: mean profit_2M per quarter, quarter win% vs base, split IS(2014-2019)/OOS(2020+).
Reuses ic_panel_8l.load() (same tribunal the thread-(a) proxy used). NOT the NAV backtest — a
directional screen to decide whether the full pt_v23 harness is worth building.

PASS = mean profit_2M >= base in BOTH IS AND OOS, and quarter win% >= 50%.
Fail at proxy tier = close H1, do NOT build the harness.
Usage: source ./wc_env.sh && $DNA_PYEXE probe_fscore_exclude.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import load

POOL_N, PICK_N = 60, 30
TGT = "profit_2M"
QS = [0.0, 0.10, 0.20]          # 0.0 = base (no exclusion); 10% and 20% bottom-FSCORE drop

def main():
    d = load()
    d = d[(d["rating"] <= 3)].copy()                       # the gated investable set V2.4 acts within
    d["liq"] = pd.to_numeric(d.get("turnover"), errors="coerce")
    d = d[d["liq"].notna() & d[TGT].notna()]
    rk = lambda s: s.rank(pct=True)
    perq = {q: [] for q in QS}; perq_yr = {q: [] for q in QS}
    dropped = {q: [] for q in QS}            # avg names excluded from the pool (diagnostic)
    nq = 0
    for qtr, g in d.groupby("q"):
        g = g.sort_values("liq", ascending=False).head(POOL_N)      # tradable pool (top-60 liquid gated)
        if len(g) < PICK_N + 5: continue
        ey_v  = pd.Series(np.where(g["PE"]  > 0, 1.0/g["PE"],  np.nan), index=g.index)
        cfy_v = pd.Series(np.where(g["PCF"] > 0, 1.0/g["PCF"], np.nan), index=g.index)
        yc = rk(ey_v).fillna(0.5) + rk(cfy_v).fillna(0.5)           # yieldcombo, identical to production
        fs = pd.to_numeric(g["FSCORE"], errors="coerce")
        fs_pct = fs.rank(pct=True)                                  # NaN FSCORE -> NaN pct (fail-safe: keep)
        nq += 1
        for q in QS:
            if q == 0.0:
                pool = g
            else:
                # fail-safe: exclude ONLY names whose FSCORE is known-low (rank pct <= q); keep NaN-FSCORE
                keep = ~(fs_pct <= q)                               # NaN -> keep (not known-low)
                pool = g[keep]
                dropped[q].append(int((~keep).sum()))
            if len(pool) < PICK_N: continue                         # safety; near-never with q<=0.2
            sc = yc.loc[pool.index]
            pick = pool.loc[sc.sort_values(ascending=False).head(PICK_N).index]
            m = pick[TGT].mean()
            perq[q].append(m); perq_yr[q].append((qtr.year, m))
    print(f"H1 FSCORE bottom-EXCLUSION gate — selected-basket forward {TGT} "
          f"(equal-weight top-{PICK_N} of top-{POOL_N} liquid, gate rating<=3), {nq} quarters\n")
    print(f"{'excl_q':>7} {'mean2M%':>9} {'vs base':>9} {'IS(14-19)':>10} {'OOS(20+)':>9} "
          f"{'win%q':>6} {'avg_drop':>9}")
    base_mean = np.mean(perq[0.0])
    base_is   = np.mean([m for (y, m) in perq_yr[0.0] if y <= 2019])
    base_oos  = np.mean([m for (y, m) in perq_yr[0.0] if y >= 2020])
    verdict = {}
    for q in QS:
        arr = np.array(perq[q]); ys = perq_yr[q]
        isv  = np.mean([m for (y, m) in ys if y <= 2019])
        oosv = np.mean([m for (y, m) in ys if y >= 2020])
        winq = (np.mean([1.0 if a > b else 0.0 for a, b in zip(perq[q], perq[0.0])])
                if q != 0 else np.nan)
        avgdrop = (np.mean(dropped[q]) if q != 0 else 0.0)
        print(f"{q:>7.2f} {arr.mean():>9.2f} {arr.mean()-base_mean:>+9.2f} {isv:>10.2f} {oosv:>9.2f} "
              f"{('   -  ' if q==0 else f'{winq:>5.0%}')} {avgdrop:>9.1f}")
        if q != 0:
            verdict[q] = dict(passes=(isv >= base_is and oosv >= base_oos and winq >= 0.50),
                              d_mean=arr.mean()-base_mean, d_is=isv-base_is, d_oos=oosv-base_oos, winq=winq)
    print(f"\nbase: mean {base_mean:.2f} | IS {base_is:.2f} | OOS {base_oos:.2f}")
    print("PASS rule = mean2M >= base in BOTH IS and OOS AND win%q >= 50%.")
    for q, v in verdict.items():
        tag = "PASS" if v["passes"] else "FAIL"
        print(f"  excl {q:.0%}: {tag}  (dIS {v['d_is']:+.2f}, dOOS {v['d_oos']:+.2f}, winq {v['winq']:.0%})")
    print("\nNOTE: directional proxy (no NAV sim/costs/T+1). Full pt_v23 harness (env BASKET_FS_FLOOR,")
    print("OFF-default) only worth building if a q PASSES here.")

if __name__ == "__main__":
    main()
