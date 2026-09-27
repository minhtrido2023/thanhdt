#!/usr/bin/env python3
"""W2b step 3 — the engine's PATH-NOISE FLOOR (quant-skeptic recommended_rerun #2).

8 engine legs: vehicles {D = park 0.0, A = custom30V park 0.3} x FLAT idle-carry
{3.0, 3.5, 4.0, 4.5}%/yr. A flat scalar is used on purpose: it has no month-to-month structure, so
any metric movement across the 4 rates CANNOT be a property of the rate series -- it is the
simulator taking a different discrete trade path because the cash level moved.

Two rulers are reported because two different comparisons need them:
  range_1p5pp  = max-min over the whole 3.0->4.5 sweep (1.5pp of rate)
  step_0p5pp   = largest jump between ADJACENT rates (0.5pp of rate) -- this is the directly
                 comparable unit, because the tier1<->tier2 gap the W2 conclusion rested on is
                 0.55pp of average rate.
A vehicle gap smaller than step_0p5pp is a TIE: the engine cannot resolve it.

Same paired bootstrap as W2 (L=21, B=4000, seed=12345, ONE block-index world for all legs).
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from paired_w2 import leg_path, load_nav, metrics, boot

RATES = [300, 350, 400, 450]
VEH = {"D": "d", "A": "a"}

if __name__ == "__main__":
    legs = [(f"{v}@{r/100:.1f}%", leg_path(f"w2bn_{k}{r}")) for v, k in VEH.items() for r in RATES]
    navs = {nm: load_nav(p) for nm, p in legs}
    names = [nm for nm, _ in legs]
    ix = navs[names[0]].index
    for nm in names:
        assert navs[nm].index.equals(ix), f"{nm}: date index differs — paired bootstrap invalid"
    R = np.column_stack([np.diff(np.log(navs[nm].values)) for nm in names])
    N = R.shape[0]; YRS = (ix[-1]-ix[0]).days/365.25; ANN = N/YRS
    ACT = metrics(R, ANN)
    C, S, D, K = boot(R, ANN, N)
    EK = K.mean(axis=0); D5 = np.percentile(D, 5, axis=0)
    res = {"_legs": dict(legs), "_n_daily": int(len(ix)), "_n_ret": int(N),
           "_yrs": round(float(YRS), 4), "_obs_per_yr": round(float(ANN), 1),
           "_window": [str(ix[0].date()), str(ix[-1].date())], "legs": {}}
    print(f"{'leg':<10} {'CAGR':>7} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'E[Calmar]':>9} {'DD5th':>7}")
    for i, nm in enumerate(names):
        row = {"cagr_pct": round(float(ACT[0][i])*100, 3), "sharpe": round(float(ACT[1][i]), 3),
               "maxdd_pct": round(float(ACT[2][i])*100, 2), "calmar": round(float(ACT[3][i]), 4),
               "E_calmar": round(float(EK[i]), 4), "dd5th_pct": round(float(D5[i])*100, 2)}
        res["legs"][nm] = row
        print(f"{nm:<10} {row['cagr_pct']:6.2f}% {row['sharpe']:7.2f} {row['maxdd_pct']:6.1f}% "
              f"{row['calmar']:7.3f} {row['E_calmar']:9.3f} {row['dd5th_pct']:6.1f}%")
    # per-vehicle noise floor
    res["noise_floor"] = {}
    for v in VEH:
        sub = [res["legs"][f"{v}@{r/100:.1f}%"] for r in RATES]
        nf = {}
        for m in ("cagr_pct", "maxdd_pct", "calmar", "E_calmar", "sharpe", "dd5th_pct"):
            vals = [s[m] for s in sub]
            nf[m] = {"values": vals, "range_1p5pp": round(max(vals)-min(vals), 4),
                     "step_0p5pp_max": round(max(abs(vals[i+1]-vals[i]) for i in range(3)), 4),
                     "monotone_in_rate": bool(all(vals[i] <= vals[i+1] for i in range(3))
                                              or all(vals[i] >= vals[i+1] for i in range(3)))}
        res["noise_floor"][v] = nf
    # vehicle gap A-D at each rate, vs the noise floor
    res["vehicle_gap_A_minus_D"] = {}
    for r in RATES:
        a, d = res["legs"][f"A@{r/100:.1f}%"], res["legs"][f"D@{r/100:.1f}%"]
        ja, jd = names.index(f"A@{r/100:.1f}%"), names.index(f"D@{r/100:.1f}%")
        res["vehicle_gap_A_minus_D"][f"{r/100:.1f}%"] = {
            "cagr_pp": round(a["cagr_pct"]-d["cagr_pct"], 3),
            "E_calmar": round(a["E_calmar"]-d["E_calmar"], 4),
            "maxdd_pp": round(a["maxdd_pct"]-d["maxdd_pct"], 2),
            "P_A_gt_D_calmar": round(float((K[:, ja] > K[:, jd]).mean()), 4)}
    out = os.path.join(HERE, "w2b_noise.json")
    json.dump(res, open(out, "w"), indent=1)
    print("\n--- noise floor per vehicle ---")
    for v, nf in res["noise_floor"].items():
        for m in ("cagr_pct", "E_calmar", "maxdd_pct"):
            print(f"{v} {m:<10} vals={nf[m]['values']} range(1.5pp)={nf[m]['range_1p5pp']} "
                  f"maxstep(0.5pp)={nf[m]['step_0p5pp_max']} monotone={nf[m]['monotone_in_rate']}")
    print("\n--- vehicle gap A-D vs noise ---")
    for r, g in res["vehicle_gap_A_minus_D"].items():
        print(f"  rate {r}: dCAGR {g['cagr_pp']:+.2f}pp  dE[Calmar] {g['E_calmar']:+.4f}  "
              f"dMaxDD {g['maxdd_pp']:+.2f}pp  P(A>D)={g['P_A_gt_D_calmar']:.3f}")
    print("->", out)
