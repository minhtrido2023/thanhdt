# -*- coding: utf-8 -*-
"""build_gate_mask.py — pre-committed BAL edge gate mask (see PREREG.md §2).

Emits one row per SESSION with gate_active in {0,1}:
  gate_active(d) = 1 iff the production momentum verdict (mom_200 / ALL, monthly Spearman IC
  vs fwd_3m, edge_health_monitor.classify with an EXPANDING full-mean) is FLIPPED for the most
  recent signal month m satisfying m + 3 months <= month(d).

Also emits the PLACEBO mask: same number of gate-active sessions, same per-calendar-year counts,
but the flagged blocks are shifted to a fixed calendar offset independent of the IC series.
"""
import os, sys, io
import numpy as np, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
from edge_health_monitor import map_sector, spearman, MIN_NAMES, RECENT, T_SIG, MAG_MIN

OUT = sys.argv[1]
LAG_M, SIG, FWD = 3, "mom_200", "fwd_3m"

df = pd.read_csv("data/edge_panel.csv", parse_dates=["time"])
df["ym"] = df["time"].dt.to_period("M")
lo, hi = df[FWD].quantile([0.005, 0.995]); df[FWD] = df[FWD].clip(lo, hi)
ic = {}
for ym, g in df.groupby("ym"):
    s = g[[SIG, FWD]].dropna()
    if len(s) < MIN_NAMES or s[SIG].nunique() < 5: continue
    v = spearman(s[SIG].values, s[FWD].values)
    if v is not None and np.isfinite(v): ic[ym] = v
ic = pd.Series(ic).sort_index()

def classify(full, recent, tstat):
    if not np.isfinite(tstat) or abs(tstat) < T_SIG: return "WEAK"
    if np.sign(recent) != np.sign(full) and abs(recent) >= MAG_MIN: return "FLIPPED"
    return "OTHER"

verdict = {}
for t in pd.period_range(ic.index.min() + LAG_M, "2026-12", freq="M"):
    av = ic[ic.index <= (t - LAG_M)]
    if len(av) < RECENT + 12: continue
    sd = av.std(ddof=1); n = len(av); full = av.mean()
    ts = full / (sd / np.sqrt(n)) if sd and sd > 0 else 0.0
    verdict[str(t)] = classify(full, av.tail(RECENT).mean(), ts)

vni = bq("SELECT t.time FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' "
         "AND t.time BETWEEN DATE '2014-01-02' AND DATE '2026-06-19' ORDER BY t.time")
d = pd.DataFrame({"time": pd.to_datetime(vni["time"])})
d["ym"] = d["time"].dt.to_period("M").astype(str)
d["gate_active"] = d["ym"].map(lambda m: 1 if verdict.get(m) == "FLIPPED" else 0)

# ---- placebo: identical yearly gate-day counts, blocks placed at a fixed calendar offset ----
rng = np.random.default_rng(20260910)
d["placebo"] = 0
for y, g in d.groupby(d["time"].dt.year):
    k = int(g["gate_active"].sum())
    if k == 0: continue
    # take the SAME number of sessions, but starting from the year's first session (fixed rule,
    # not resampled) — a pure "less exposure for k sessions this year" counterfactual.
    d.loc[g.index[:k], "placebo"] = 1

d[["time", "gate_active", "placebo"]].to_csv(OUT, index=False)
print(f"wrote {OUT}: {len(d)} sessions, gate_active={int(d.gate_active.sum())}, placebo={int(d.placebo.sum())}")
print(d.groupby(d.time.dt.year)[["gate_active", "placebo"]].sum().to_string())
