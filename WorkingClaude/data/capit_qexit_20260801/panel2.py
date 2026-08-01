#!/usr/bin/env python
"""CAPIT quality-exit — panel part 2 (job Taylor_20260801_073610).

Consumes holdings_panel.csv from panel.py. Adds:
  (d) trim-50% variant, (2) event-level sign test / bootstrap, (3) the "N quarters" degeneracy
  check, (4) the post-flag price path (is the flag early or late?).
"""
import os

import numpy as np
import pandas as pd

OUT = "/home/trido/thanhdt/WorkingClaude/data/capit_qexit_20260801"
P = pd.read_csv(os.path.join(OUT, "holdings_panel.csv"), parse_dates=["entry", "exit"])
for c in P.columns:
    if c.endswith("_date"):
        P[c] = pd.to_datetime(P[c])
w = P["cost"] / P["cost"].sum()
base = float((w * P.ret_hold).sum())

print("=" * 78)
print(f"N = {len(P)} CAPIT holdings across {P.event.nunique()} events "
      f"({P.entry.min().date()} → {P.exit.max().date()}).  Baseline cost-wt return {base*100:+.2f}%")
print("=" * 78)

print("\n[A] Strategy grid — cost-weighted sleeve return over all holdings")
print(f"{'strategy':38s} {'n_flag':>6s} {'ret':>8s} {'Δ vs (a)':>9s}")
print(f"{'(a) hold 60td [BASELINE]':38s} {0:6d} {base*100:+7.2f}% {0.0:+8.2f}pp")
grid = []
for metric in ("floor", "floornf", "fscore", "r8l"):
    for K in (1, 5, 20):
        n = int(P[f"{metric}_K{K}_date"].notna().sum())
        rf = P[f"{metric}_K{K}_ret"]
        for frac, lab in ((1.0, "exit"), (0.5, "trim50")):
            r = frac * rf + (1 - frac) * P.ret_hold
            v = float((w * r).sum())
            grid.append({"metric": metric, "K": K, "frac": frac, "n_flag": n, "ret": v,
                         "delta_pp": (v - base) * 100})
            print(f"{f'({lab}) {metric} K={K}':38s} {n:6d} {v*100:+7.2f}% {(v-base)*100:+8.2f}pp")
pd.DataFrame(grid).to_csv(os.path.join(OUT, "strategy_grid.csv"), index=False)

print("\n[B] Which leg of the CAPIT floor actually breaks?")
nf = int(P["floornf_K1_date"].notna().sum())
fs = int(P["fscore_K1_date"].notna().sum())
fl = int(P["floor_K1_date"].notna().sum())
print(f"    ROE_Min5Y>=0.12 AND ROIC5Y>=0.10 broken : {nf:3d}/{len(P)}")
print(f"    FSCORE>=6 broken                        : {fs:3d}/{len(P)}")
print(f"    full floor broken (either)              : {fl:3d}/{len(P)}")
print(f"    8L rating > 3                           : {int(P['r8l_K1_date'].notna().sum()):3d}/{len(P)}")
print("    → the 'quality drop' signal inside a 60-session CAPIT hold is 100% FSCORE.")

print("\n[C] 'N kỳ liên tiếp' (N quarters) — is it even reachable inside a 60-session hold?")
hold_len = (P["exit"] - P["entry"]).dt.days
print(f"    hold length: median {hold_len.median():.0f} calendar days "
      f"({hold_len.min():.0f}–{hold_len.max():.0f}) ≈ 60 sessions ≈ 1 quarter of releases.")
m = P["floor_K1_date"].notna()
lag = (P.loc[m, "floor_K1_date"] - P.loc[m, "entry"]).dt.days
print(f"    days entry→flag (flagged only): median {lag.median():.0f}, "
      f"p25 {lag.quantile(.25):.0f}, p75 {lag.quantile(.75):.0f}, max {lag.max():.0f}")
print("    → at most ONE quarterly release lands inside the window, so an N≥2-QUARTER confirmation")
print("      can never fire before the 60td TIME exit: strategy (c) at N=2 quarters ≡ strategy (a).")
print("      The only implementable confirmation is in SESSIONS (K), tested above.")

print("\n[D] Is the flag early or late? (metric=floor, K=1, flagged holdings only)")
print(f"    flagged   n={m.sum():3d}: hold-to-TIME {P.loc[m,'ret_hold'].mean()*100:+6.2f}%  "
      f"exit-at-flag {P.loc[m,'floor_K1_ret'].mean()*100:+6.2f}%  "
      f"→ forgone {((P.loc[m,'ret_hold']-P.loc[m,'floor_K1_ret']).mean())*100:+6.2f}pp")
print(f"    unflagged n={(~m).sum():3d}: hold-to-TIME {P.loc[~m,'ret_hold'].mean()*100:+6.2f}%")
print("    → the flag DOES select the weaker half (13.7% vs 22.8% to TIME), but it arrives AFTER")
print("      the damage and BEFORE the bounce: selling on it realises ~1/5 of the hold return.")
post = P.loc[m, "ret_hold"] - P.loc[m, "floor_K1_ret"]
print(f"    post-flag move: positive in {int((post>0).sum())}/{int(m.sum())} cases "
      f"(mean {post.mean()*100:+.2f}pp, median {post.median()*100:+.2f}pp)")

print("\n[E] Event-level significance (the honest N is EVENTS, not holdings)")
ev = []
for e, g in P.groupby("event"):
    ww = g["cost"] / g["cost"].sum()
    ev.append({"event": e, "date": g.entry.min().date(), "n": len(g),
               "n_flag": int(g["floor_K1_date"].notna().sum()),
               "hold": float((ww * g.ret_hold).sum()),
               "qexit": float((ww * g.floor_K1_ret).sum())})
E = pd.DataFrame(ev)
E["delta_pp"] = (E.qexit - E.hold) * 100
E.to_csv(os.path.join(OUT, "event_rollup.csv"), index=False)
act = E[E.n_flag > 0]
neg = int((act.delta_pp < -0.01).sum()); pos = int((act.delta_pp > 0.01).sum())
print(f"    events where the rule actually acted: {len(act)}/{len(E)}   "
      f"worse {neg}, better {pos}, ~flat {len(act)-neg-pos}")
# exact two-sided sign test
from math import comb
n_eff = neg + pos
p_two = min(1.0, 2 * sum(comb(n_eff, i) for i in range(0, min(neg, pos) + 1)) / 2 ** n_eff) if n_eff else 1.0
print(f"    sign test on {n_eff} decisive events: two-sided p = {p_two:.3f}")
rng = np.random.default_rng(20260801)
bs = [E.delta_pp.sample(len(E), replace=True, random_state=int(rng.integers(1e9))).mean()
      for _ in range(10000)]
bs = np.array(bs)
print(f"    bootstrap of per-event Δ (10k, resample EVENTS): mean {E.delta_pp.mean():+.2f}pp, "
      f"90% CI [{np.percentile(bs,5):+.2f}, {np.percentile(bs,95):+.2f}]pp, "
      f"P(Δ>0) = {float((bs>0).mean()):.3f}")
print(f"    worst single event: E{int(E.loc[E.delta_pp.idxmin(),'event'])} "
      f"{E.loc[E.delta_pp.idxmin(),'date']} {E.delta_pp.min():+.2f}pp | "
      f"best: E{int(E.loc[E.delta_pp.idxmax(),'event'])} {E.delta_pp.max():+.2f}pp")

print("\n[F] Leave-one-event-out on the total (floor K=1, exit): does one event carry the sign?")
tot = []
for e in sorted(P.event.unique()):
    q = P[P.event != e]
    ww = q["cost"] / q["cost"].sum()
    b = float((ww * q.ret_hold).sum()); v = float((ww * q.floor_K1_ret).sum())
    tot.append((e, (v - b) * 100))
loo = pd.DataFrame(tot, columns=["dropped_event", "delta_pp"])
print(f"    LOO Δ range: {loo.delta_pp.min():+.2f} … {loo.delta_pp.max():+.2f}pp "
      f"(full-sample {(float((w*P.floor_K1_ret).sum())-base)*100:+.2f}pp) — "
      f"sign flips on dropping any single event: {int((loo.delta_pp>0).sum())}/{len(loo)}")
