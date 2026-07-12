# -*- coding: utf-8 -*-
"""DSR for the DVR-8L sizing winner (R2), N=5 declared trials (plan §4 N-ledger).
Reuses dsr_pbo_annex.py conventions (per-obs SR on daily log-returns of combined_nav,
BLdP expected-max SR under N trials, var_sr across the family's realized SRs).
Job Taylor_20260711_235305 — analysis only, no new trial."""
import math
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import moments, expected_max_sr, dsr

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
PAT = (WORKDIR + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
       "etfliqcustompitg_wtnamecap_exp_dvr8l{}.csv")
ANN = 252

def logret(tag):
    df = pd.read_csv(PAT.format(tag), low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"]); d = d.sort_values("ymd")
    s = d.groupby("ymd")["combined_nav"].last().astype(float)
    return np.log(s / s.shift(1)).dropna()

# family members actually simulated (R1/R2/R3 + R2 sensitivity h75); N for deflation = 5 declared
tags = ["r1", "r2", "r3", "r2h75"]
srs = {}
for t in tags:
    try:
        r = logret(t)
        sr, g3, g4 = moments(r)
        srs[t] = (sr, g3, g4, len(r))
        print(f"{t:>6}: per-obs SR {sr:.5f}  ann {sr*math.sqrt(ANN):.3f}  g3 {g3:.3f}  g4 {g4:.3f}  T {len(r)}")
    except FileNotFoundError:
        print(f"{t:>6}: CSV missing, skipped")

var_sr = float(np.var([v[0] for v in srs.values()], ddof=1))
print(f"var_sr across family = {var_sr:.3e}")
sr_hat, g3, g4, T = srs["r2"]
for N in (5, 8, 16):
    sr0 = expected_max_sr(var_sr, N)
    p, stat = dsr(sr_hat, sr0, g3, g4, T)
    flag = "  <<< RED FLAG (DSR<0.95)" if p < 0.95 else ""
    print(f"DSR(R2) @ N={N:>2}: SR0(ann)={sr0*math.sqrt(ANN):.3f}  DSR={p:.4f}{flag}")
