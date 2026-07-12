#!/usr/bin/env python
"""DSR for Q-sleeve family N=5 (gate §7, plan_quality_sleeve_20260712.md).
Reuses dsr_pbo_annex.py functions verbatim (moments/expected_max_sr/dsr).
DSR computed (a) on each trial's own daily NAV, (b) on excess log-returns vs control
(the V2.5-verification convention). N=5 declared trials; PBO n/a (family<8, per plan)."""
import sys, glob, math
import numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import moments, expected_max_sr, dsr

DATA = "/home/trido/thanhdt/WorkingClaude/data"
ANN = 252.0

def load_nav(tag):
    g = glob.glob(f"{DATA}/v23_golive_audit_2014_now_*_exp_qsleeve_{tag}.csv")
    assert len(g) == 1, (tag, g)
    df = pd.read_csv(g[0], low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    return d.groupby("ymd")["combined_nav"].last().astype(float)

tags = ["q8neu", "q12neu", "qf8neu", "q12bullext"]
navs = {t: load_nav(t) for t in tags + ["ctrl"]}
rets = {t: np.diff(np.log(navs[t].values)) for t in navs}

# family SR spread (annualised) across the 4 executed trials, N declared = 5
srs = {t: rets[t].mean() / rets[t].std(ddof=1) * math.sqrt(ANN) for t in tags}
var_sr_daily = np.var([rets[t].mean() / rets[t].std(ddof=1) for t in tags], ddof=1)
N = 5
print("annualised SR per trial:", {k: round(v, 3) for k, v in srs.items()},
      " ctrl:", round(rets["ctrl"].mean()/rets["ctrl"].std(ddof=1)*math.sqrt(ANN), 3))
print(f"declared N={N} (plan: family đóng sổ; PBO n/a vì N<8, LOO thay thế)")

for t in tags:
    r = rets[t]
    sr_d, g3, g4 = moments(r)
    sr0 = expected_max_sr(var_sr_daily, N)
    p, stat = dsr(sr_d, sr0, g3, g4, len(r))
    flag = "  <<< RED FLAG (<0.95)" if p < 0.95 else ""
    print(f"[own NAV]  {t:12s} SR(ann)={sr_d*math.sqrt(ANN):5.3f}  SR0(ann)={sr0*math.sqrt(ANN):5.3f}  DSR={p:.4f}{flag}")

# excess vs control (aligned dates)
print("\n[excess vs ctrl] (V2.5-verification convention)")
exc_sr_daily = []
exc_r = {}
for t in tags:
    a, b = navs[t].align(navs["ctrl"], join="inner")
    r = np.diff(np.log(a.values)) - np.diff(np.log(b.values))
    exc_r[t] = r
    exc_sr_daily.append(r.mean() / r.std(ddof=1))
var_exc = np.var(exc_sr_daily, ddof=1)
for t in tags:
    r = exc_r[t]
    sr_d, g3, g4 = moments(r)
    sr0 = expected_max_sr(var_exc, N)
    p, stat = dsr(sr_d, sr0, g3, g4, len(r))
    flag = "  <<< RED FLAG (<0.95)" if p < 0.95 else ""
    print(f"  {t:12s} excessSR(ann)={sr_d*math.sqrt(ANN):+6.3f}  SR0(ann)={sr0*math.sqrt(ANN):5.3f}  DSR={p:.4f}{flag}")
