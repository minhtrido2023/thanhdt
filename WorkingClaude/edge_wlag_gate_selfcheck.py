# -*- coding: utf-8 -*-
"""Regression self-check for the edge-conditional w_LAG gate in golive_recommend_v23.py
(spec-drift fix 2026-07-12, job Taylor_20260712_072039).

Root need: the money-path recommender (deploy_golive_dt5g_v4/golive_recommend_v23.py, read by
DollarBill to build real T+1 plans) hardcoded `w_tgt = STATE_LAG_WEIGHT.get(state_today, 0.5)`
— unconditional 65% in states 3/4/5 — while the pinned R3 baseline (argv `v23a none postbull 0
edge`, pt_v23_audit_2014.py:1738-1751) gates that tilt on LAG's own causal edge-health: 0.65
ONLY when trailing-12M mean LAG post-return (mean12, data/lag_edge_health.csv) >= 4%, else 0.50.
2026 data fails the gate, so the live recommender was emitting an unbacktested 65% target and a
spurious REBALANCE flag (target 65% vs current ~49% breached the ±10pp band; correct spec is
50% vs 49% = no rebalance).

The production file runs BQ queries at import, so the function under test is extracted from its
source via ast and exec'd with a controlled WORKDIR — this tests the REAL production code text,
not a copy that could drift.

Run: python edge_wlag_gate_selfcheck.py   (exit 0 = all pass)
"""
import ast
import os
import sys
import tempfile

import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.join(ROOT, "deploy_golive_dt5g_v4", "golive_recommend_v23.py")
PINNED_CSV = os.path.join(ROOT, "data",
    "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv")

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def extract_gate(workdir):
    """Extract STATE_LAG_WEIGHT / EDGE_THR / w_lag_target from the production source,
    exec'd with WORKDIR pointed at `workdir` (so tests control which csv it reads)."""
    src = open(PROD, encoding="utf-8").read()
    tree = ast.parse(src)
    ns = {"pd": pd, "os": os, "WORKDIR": workdir, "print": lambda *a, **k: None}
    found = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in (
                "STATE_LAG_WEIGHT", "EDGE_THR"):
            exec(compile(ast.Module([node], []), PROD, "exec"), ns)
            found.add(node.targets[0].id)
        elif isinstance(node, ast.FunctionDef) and node.name == "w_lag_target":
            exec(compile(ast.Module([node], []), PROD, "exec"), ns)
            found.add("w_lag_target")
    assert found == {"STATE_LAG_WEIGHT", "EDGE_THR", "w_lag_target"}, f"missing defs: {found}"
    return ns


def write_edge_csv(workdir, mean12):
    os.makedirs(os.path.join(workdir, "data"), exist_ok=True)
    pd.DataFrame({"entry": ["2020-01-06"], "ret": [1.0], "mean12": [mean12],
                  "win12": [50.0], "n12": [100.0]}).to_csv(
        os.path.join(workdir, "data", "lag_edge_health.csv"), index=False)


ASOF = pd.Timestamp("2020-06-01")

# A. Gate FAIL (mean12 below threshold) in good states -> 0.50, never 0.65.
with tempfile.TemporaryDirectory() as td:
    write_edge_csv(td, 0.5)
    f = extract_gate(td)["w_lag_target"]
    check("A. gate FAIL (mean12=0.5% < 4%) NEUTRAL -> 0.50", f(3, ASOF) == 0.50)
    check("A. gate FAIL BULL -> 0.50", f(4, ASOF) == 0.50)
    check("A. gate FAIL EX-BULL -> 0.50", f(5, ASOF) == 0.50)

# B. Gate PASS (mean12 >= threshold) in good states -> 0.65; boundary mean12==4.0 passes (>=).
with tempfile.TemporaryDirectory() as td:
    write_edge_csv(td, 7.2)
    f = extract_gate(td)["w_lag_target"]
    check("B. gate PASS (mean12=7.2%) NEUTRAL -> 0.65", f(3, ASOF) == 0.65)
    check("B. gate PASS BULL -> 0.65", f(4, ASOF) == 0.65)
with tempfile.TemporaryDirectory() as td:
    write_edge_csv(td, 4.0)
    f = extract_gate(td)["w_lag_target"]
    check("B. boundary mean12=4.0 (>= thr) -> 0.65", f(3, ASOF) == 0.65)

# C. BEAR/CRISIS unaffected by the gate regardless of edge-health.
with tempfile.TemporaryDirectory() as td:
    write_edge_csv(td, 99.0)
    f = extract_gate(td)["w_lag_target"]
    check("C. BEAR -> 0.00 even with huge mean12", f(2, ASOF) == 0.00)
    check("C. CRISIS -> 0.50 even with huge mean12", f(1, ASOF) == 0.50)

# D. Fail-safe: csv missing entirely -> 0.50 (the conservative gate-fail branch), no crash.
with tempfile.TemporaryDirectory() as td:
    f = extract_gate(td)["w_lag_target"]
    check("D. lag_edge_health.csv missing -> fail-safe 0.50", f(3, ASOF) == 0.50)

# E. asof BEFORE the first edge-health entry (NaN mean12) -> 0.50.
with tempfile.TemporaryDirectory() as td:
    write_edge_csv(td, 99.0)
    f = extract_gate(td)["w_lag_target"]
    check("E. asof pre-history (mean12 NaN) -> 0.50", f(3, pd.Timestamp("2019-01-01")) == 0.50)

# F. No unconditional hardcode left: the w_tgt assignment in section 5 must call w_lag_target.
src = open(PROD, encoding="utf-8").read()
check("F. w_tgt assignment calls w_lag_target(state_today, ...)",
      "w_tgt = w_lag_target(state_today" in src)
check("F. old hardcode `w_tgt = STATE_LAG_WEIGHT.get` removed",
      "w_tgt = STATE_LAG_WEIGHT.get" not in src)

# G. Equivalence vs the pinned R3 artifact: on every day the pinned CSV's w_lag_tgt CHANGES
#    (the hardest days — exactly where the gate flips), the production function must reproduce
#    the pinned value from the real data/lag_edge_health.csv.
if os.path.exists(PINNED_CSV):
    f = extract_gate(ROOT)["w_lag_target"]
    df = pd.read_csv(PINNED_CSV, low_memory=False)
    d = df[df["record_type"] == "DAILY"][["ymd", "state", "w_lag_tgt"]].dropna(subset=["w_lag_tgt"])
    d["ymd"] = pd.to_datetime(d["ymd"])
    flips = d[d["w_lag_tgt"].ne(d["w_lag_tgt"].shift())]
    bad = [(r["ymd"].date(), int(r["state"]), r["w_lag_tgt"], f(r["state"], r["ymd"]))
           for _, r in flips.iterrows()
           if abs(f(r["state"], r["ymd"]) - r["w_lag_tgt"]) > 1e-9]
    check(f"G. matches pinned R3 w_lag_tgt on all {len(flips)} flip days", not bad,
          f"first mismatches: {bad[:3]}" if bad else "")
else:
    check("G. pinned R3 CSV present for equivalence check", False, PINNED_CSV)

print()
if fails:
    print(f"SELF-CHECK FAILED ({len(fails)}): {fails}")
    sys.exit(1)
print("ALL CHECKS PASSED")
