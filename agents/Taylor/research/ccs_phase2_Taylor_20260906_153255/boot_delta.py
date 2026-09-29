# -*- coding: utf-8 -*-
"""CCS Phase 2 — supporting inference on the ONE variant: is the +0.91pp CAGR gap distinguishable
from noise once serial dependence is respected? Two block bootstraps, both PAIRED by date so the
two legs always see the same resampled market path (the delta is what is being tested, not the
level). Fixes a first-pass bug: circular_block_boot returns (CAGR, DD) as a TUPLE of arrays;
ravel()-ing it silently mixed drawdowns into the CAGR sample."""
import sys, os, math, json
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd
from dsr_pbo_annex import ANN, daily_logret, circular_block_boot

D = os.path.dirname(os.path.abspath(__file__))
def nav(leg):
    d = pd.read_csv(os.path.join(D, f"daily_{leg}_exp.csv"), parse_dates=["ymd"])
    return d.set_index("ymd")["combined_nav"].astype(float)
S = {l: nav(l) for l in ("ctrl", "trim50")}
rc, rt = daily_logret(S["ctrl"]), daily_logret(S["trim50"])
d = rt - rc
N = len(d)

# (a) unpaired: bootstrap the DELTA series itself, read its compounded annual rate
C, _ = circular_block_boot(d, L=21, B=4000, seed=20260906)
a = C * 100
print(f"(a) delta-series circular block boot (L=21, B=4000): point {100*(math.exp(d.mean()*ANN)-1):+.3f}pp")
print(f"    95% CI [{np.percentile(a,2.5):+.3f}pp, {np.percentile(a,97.5):+.3f}pp]  P(>0)={(a>0).mean():.3f}")

# (b) paired: resample the same date-blocks for BOTH legs, recompute each leg's CAGR, take delta
for L in (21, 63):
    rng = np.random.default_rng(20260906)
    nblk = int(np.ceil(N / L)); out = np.empty(4000)
    for b in range(4000):
        st = rng.integers(0, N, nblk)
        ix = np.concatenate([np.arange(s0, s0 + L) for s0 in st])[:N] % N
        yrs = N / ANN
        gc = math.exp(rc[ix].sum()) ** (1 / yrs) - 1
        gt = math.exp(rt[ix].sum()) ** (1 / yrs) - 1
        out[b] = (gt - gc) * 100
    print(f"(b) PAIRED date-block boot L={L}: median {np.median(out):+.3f}pp  "
          f"95% CI [{np.percentile(out,2.5):+.3f}pp, {np.percentile(out,97.5):+.3f}pp]  "
          f"P(>0)={(out>0).mean():.3f}")
    if L == 21:
        keep = {"paired_L21_ci": [float(np.percentile(out,2.5)), float(np.percentile(out,97.5))],
                "paired_L21_p_gt0": float((out > 0).mean()),
                "paired_L21_median": float(np.median(out))}

# (c) how many of the 3107 sessions actually differ at all between the legs?
same = np.isclose(S["ctrl"].values, S["trim50"].values, rtol=0, atol=1.0)
print(f"\n(c) sessions where the two NAV paths are within 1 VND: {same.sum()}/{len(same)} "
      f"({same.mean():.1%}) — first divergence {S['ctrl'].index[~same][0].date()}")
res = {"delta_series_ci": [float(np.percentile(a,2.5)), float(np.percentile(a,97.5))],
       "delta_series_p_gt0": float((a > 0).mean()), **keep,
       "n_sessions_identical": int(same.sum()), "n_sessions": int(len(same))}
json.dump(res, open(os.path.join(D, "boot_delta_exp.json"), "w"), indent=2)
print("wrote boot_delta_exp.json")
