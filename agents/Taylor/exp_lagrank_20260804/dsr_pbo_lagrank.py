# -*- coding: utf-8 -*-
"""LAG forward-window ranking — DSR / PBO for THIS job's config family (Taylor_20260804_051145).

Reuses the canonical implementations in `dsr_pbo_annex.py` VERBATIM (import, not re-derive) so the
numbers are directly comparable to the V2.4 annex pinned in data/results_registry.md. Only the
config FAMILY differs: here it is the 11-leg lagrank grid at one NAV scale, not the V2.3A search.

N_trials is passed in explicitly — it is the number of configs COMPARED to pick the winner, which
is a fact about the search, not something inferable from the CSVs on disk.

Usage: python dsr_pbo_lagrank.py <ntrials> <label>=<csv> [<label>=<csv> ...]
       (first leg = the config being deflated; all legs form the PBO matrix)
"""
import sys, os
import numpy as np

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import load_nav, daily_logret, moments, expected_max_sr, dsr, cscv_pbo

ANN = 252.0

n_trials = int(sys.argv[1])
legs = [(a.split("=", 1)[0], a.split("=", 1)[1]) for a in sys.argv[2:]]

series = {}
for lab, p in legs:
    s = load_nav(p)
    if s is None:
        sys.exit(f"FATAL: no combined_nav in {p}")
    series[lab] = s

# ---- align every leg on the common calendar (PBO needs one matrix) ----
idx = None
for s in series.values():
    idx = s.index if idx is None else idx.intersection(s.index)
R = {lab: daily_logret(s.loc[idx]) for lab, s in series.items()}
T = len(next(iter(R.values())))
print(f"legs {len(R)}  common sessions {len(idx)}  returns {T}\n")

# ---- DSR on each leg, deflated by the SAME N_trials (the search that produced them) ----
sr_all = np.array([moments(r)[0] for r in R.values()])
var_sr = float(np.var(sr_all, ddof=1)) if len(sr_all) > 1 else 0.0
sr0 = expected_max_sr(var_sr, n_trials)
print(f"N_trials={n_trials}  var(SR across trials)={var_sr:.3e}  SR_0(expected max under null)={sr0:.5f}"
      f"  [annualised SR_0 = {sr0*np.sqrt(ANN):.3f}]\n")
print(f"{'leg':<20} {'SR/day':>9} {'SR ann':>7} {'skew':>7} {'kurt':>7} {'DSR':>7}  verdict")
for lab, r in R.items():
    sr, g3, g4 = moments(r)
    d, stat = dsr(sr, sr0, g3, g4, T)
    print(f"{lab:<20} {sr:9.5f} {sr*np.sqrt(ANN):7.3f} {g3:7.3f} {g4:7.2f} {d:7.4f}  "
          f"{'PASS >=0.95' if d >= 0.95 else 'RED FLAG <0.95'}")

# ---- CSCV / PBO over the whole family ----
M = np.column_stack([R[lab] for lab, _ in legs])
out = cscv_pbo(M, S=16)
pbo = out[0] if isinstance(out, tuple) else out
print(f"\nCSCV PBO (S=16, {len(R)} configs) = {pbo:.4f}   "
      f"{'>=0.5 -> prefer robust-median config, NOT the IS-best' if pbo >= 0.5 else '<0.5'}")
