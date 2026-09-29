#!/usr/bin/env python3
"""Ma tran P(X > Y) day du tren E[Calmar] paired — job Taylor_20260927_141318.

`paired_w2.py` chi in P(X>D) (cot ma PREREG §1 doi). Cay quyet dinh ke hoach §4 nhanh 2 lai can
P(B>A) / P(C>A) >= 0,60, nen file nay tai dung NGUYEN khuon bootstrap cua paired_w2 (import, khong
copy so hoc) roi in ca ma tran. Cung SEED/L/B ⇒ cung mot "the gioi resample".
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paired_w2 as P

for tier in ("baseline", "floor"):
    legs = [(nm, P.leg_path(f"w2{k}_{tier}"))
            for nm, k in [("D", "d"), ("A", "a"), ("B", "b"), ("C6", "c6"), ("C10", "c10")]]
    navs = {nm: P.load_nav(p) for nm, p in legs}
    names = [nm for nm, _ in legs]
    R = np.column_stack([np.diff(np.log(navs[nm].values)) for nm in names])
    N = R.shape[0]
    idx0 = navs[names[0]].index
    ANN = N / ((idx0[-1] - idx0[0]).days / 365.25)
    _, _, D, K = P.boot(R, ANN, N)
    print(f"\n=== tier={tier} — P(hang > cot) tren Calmar bootstrap (B={P.B}, L={P.L}, seed={P.SEED}) ===")
    print("        " + "".join(f"{c:>8}" for c in names))
    M = {}
    for i, a in enumerate(names):
        row = [(K[:, i] > K[:, j]).mean() for j in range(len(names))]
        M[a] = {names[j]: round(float(row[j]), 4) for j in range(len(names))}
        print(f"{a:<8}" + "".join(f"{v:8.3f}" for v in row))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"pairwise_{tier}.json")
    json.dump({"tier": tier, "P_row_gt_col_calmar": M,
               "E_calmar": {nm: round(float(K.mean(axis=0)[i]), 4) for i, nm in enumerate(names)},
               "dd5th_pct": {nm: round(float(np.percentile(D, 5, axis=0)[i])*100, 2) for i, nm in enumerate(names)}},
              open(out, "w"), indent=1)
    print(f"-> {out}")
