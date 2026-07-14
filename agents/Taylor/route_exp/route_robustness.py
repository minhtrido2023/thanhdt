# -*- coding: utf-8 -*-
"""route_robustness.py — the multiple-testing battery for BASKET_SELECT=v3route
(job Taylor_20260714_112932). KB §5: any production wire must declare N trials + DSR, and a
per-year leave-one-out when the OOS edge is thin in places (the Wave1/H8a lesson 2026-07-05:
an edge that obeys every rule but lives entirely in 1-2 years is reshuffle luck, not signal).

Both arms were run TODAY on the same data vintage, so the DELTA is apples-to-apples even though
neither arm reproduces the 2026-07-12 pinned R3 (see the vintage-drift note in the finding).

Outputs: annual delta table, per-year LOO on the system-level edge, DSR for the v3route NAV.
"""
import os, sys, glob, math
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from dsr_pbo_annex import load_nav, expected_max_sr, dsr as dsr_fn  # reuse pinned implementations

BASE = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_selbaseline20260714.csv"
VAR  = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_selv3route.csv"

nb, nv = load_nav(BASE), load_nav(VAR)
idx = nb.index.intersection(nv.index)
nb, nv = nb.loc[idx], nv.loc[idx]
print(f"aligned trading days: {len(idx)}  {idx[0].date()} -> {idx[-1].date()}")

rb = pd.Series(np.diff(np.log(nb.values)), index=idx[1:])
rv = pd.Series(np.diff(np.log(nv.values)), index=idx[1:])


def ann_cagr(r):
    """Annualised return from daily log-returns over their own calendar span."""
    yrs = len(r) / 252.0
    return math.expm1(r.sum() / yrs)


def maxdd(r):
    p = np.exp(r.cumsum()); return float((p / np.maximum.accumulate(p) - 1).min())


def sharpe(r):
    return float(r.mean() / r.std(ddof=1) * math.sqrt(252)) if r.std(ddof=1) > 0 else float("nan")


def calmar(r):
    dd = maxdd(r); return ann_cagr(r) / abs(dd) if dd < 0 else float("nan")


print("\n" + "=" * 78)
print("ANNUAL system-level (v3route - baseline), pp")
print("=" * 78)
rows = []
for y, g in rv.groupby(rv.index.year):
    b = rb[rb.index.year == y]
    rows.append({"year": y, "base": math.expm1(b.sum()) * 100, "v3route": math.expm1(g.sum()) * 100})
A = pd.DataFrame(rows).set_index("year")
A["delta"] = A["v3route"] - A["base"]
print(A.round(2).to_string())
print(f"\nyears v3route WINS: {(A.delta > 0).sum()}/{len(A)}   mean delta {A.delta.mean():+.2f}pp  "
      f"median {A.delta.median():+.2f}pp")
print(f"last 3 calendar years (2024-2026) delta: {A.loc[2024:2026,'delta'].round(2).to_dict()}")

print("\n" + "=" * 78)
print("PER-YEAR LEAVE-ONE-OUT — drop year Y, recompute the FULL-period edge without it")
print("=" * 78)
full_b, full_v = ann_cagr(rb) * 100, ann_cagr(rv) * 100
print(f"FULL: base CAGR {full_b:.2f}%  v3route {full_v:.2f}%  edge {full_v-full_b:+.2f}pp | "
      f"Calmar {calmar(rb):.2f} -> {calmar(rv):.2f}")
loo = []
for y in sorted(A.index):
    mb, mv = rb[rb.index.year != y], rv[rv.index.year != y]
    eb, ev = ann_cagr(mb) * 100, ann_cagr(mv) * 100
    loo.append({"drop_year": y, "base": eb, "v3route": ev, "edge_pp": ev - eb,
                "calmar_base": calmar(mb), "calmar_v3route": calmar(mv),
                "calmar_edge": calmar(mv) - calmar(mb)})
L = pd.DataFrame(loo).set_index("drop_year")
print(L.round(2).to_string())
n_pos = (L.edge_pp > 0).sum()
print(f"\nLOO CAGR edge stays POSITIVE in {n_pos}/{len(L)} drops "
      f"(min {L.edge_pp.min():+.2f}pp @drop {L.edge_pp.idxmin()}, max {L.edge_pp.max():+.2f}pp)")
n_pos_c = (L.calmar_edge > 0).sum()
print(f"LOO Calmar edge stays POSITIVE in {n_pos_c}/{len(L)} drops "
      f"(min {L.calmar_edge.min():+.3f} @drop {L.calmar_edge.idxmin()})")

print("\n" + "=" * 78)
print("DSR — Deflated Sharpe for the v3route config (Bailey & Lopez de Prado)")
print("=" * 78)
# Trial family = every full-harness variant CSV at this same config family (the annex's own
# definition). var(SR) across trials is what deflates: a wide spread of trial Sharpes means a
# high SR is cheaper to hit by luck.
fam = sorted(glob.glob(f"{WORKDIR}/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap*.csv"))
srs = []
for p in fam:
    try:
        s = load_nav(p)
        if s is None or len(s) < 500: continue
        r = np.diff(np.log(s.values))
        if r.std(ddof=1) > 0: srs.append(r.mean() / r.std(ddof=1))
    except Exception:
        pass
srs = np.array(srs)
var_sr = float(srs.var(ddof=1))
sr_hat = float(rv.mean() / rv.std(ddof=1))          # per-observation SR of v3route
g3 = float(pd.Series(rv).skew()); g4 = float(pd.Series(rv).kurt() + 3.0)
print(f"empirical trial family: N={len(srs)} CSVs; per-day SR spread sd={math.sqrt(var_sr):.5f}")
print(f"v3route per-day SR {sr_hat:.5f} (annualised {sr_hat*math.sqrt(252):.2f}); skew {g3:.3f} kurt {g4:.3f}")
for N in (len(srs), 10, 25, 50):
    if N < 2: continue
    sr0 = expected_max_sr(var_sr, N)
    d, stat = dsr_fn(sr_hat, sr0, g3, g4, len(rv))
    tag = ("empirical family" if N == len(srs) else
           "selector modes coded in custom_basket.py" if N == 10 else "conservative")
    print(f"  N={N:3d} ({tag}): SR0={sr0:.5f}  DSR={d:.4f}  {'PASS' if d >= 0.95 else 'RED FLAG'}")
print("\nNOTE: DSR here judges the v3route NAV as a standalone strategy (its Sharpe is dominated by")
print("the V2.4 system it sits in, NOT by the selector swap). The honest test of the SWAP is the")
print("LOO edge table above + the vehicle-level delta, not this DSR.")
