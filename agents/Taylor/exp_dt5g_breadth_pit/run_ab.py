# -*- coding: utf-8 -*-
"""A/B harness: DT5G breadth-decoupling guard, ticker_prune (prod) vs universe_pit (candidate).

Job Taylor_20260729_152031. Runs the SAME copied engine twice, only the breadth SQL differs,
so any diff is attributable to the data source alone. Also runs a PARITY self-check that the
copy on "prune" reproduces the live production module byte-for-byte.
"""
import os, sys, importlib
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WORKDIR, "mike/agents/Taylor/exp_dt5g_breadth_pit")
sys.path.insert(0, WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)          # publish-path discipline: live BQ only
from simulate_holistic_nav import bq            # noqa: E402

START, END = "2014-01-01", "2026-07-29"


def run(src):
    os.environ["BREADTH_SRC"] = src
    sys.path.insert(0, OUT)
    for m in [m for m in list(sys.modules) if m == "macro_variant"]:
        del sys.modules[m]
    mv = importlib.import_module("macro_variant")
    assert mv.BREADTH_SOURCE == src, (mv.BREADTH_SOURCE, src)
    df = mv.get_macro_state(START, END, bq=bq)
    df.to_csv(os.path.join(OUT, f"dt5g_{src}.csv"), index=False)
    return df


a = run("prune")
b = run("pit")

# ── PARITY: copy-on-prune must equal the LIVE production module exactly ──
import macro_state_live as prod                 # noqa: E402
p = prod.get_macro_state(START, END, bq=bq)
merged = p.merge(a, on="time", suffixes=("_prod", "_copy"))
assert len(merged) == len(p) == len(a), (len(p), len(a), len(merged))
for c in ["state", "state_dt4", "cap", "easing"]:
    nd = int((merged[f"{c}_prod"] != merged[f"{c}_copy"]).sum())
    print(f"PARITY prod-vs-copy(prune) {c}: {nd} diffs")
    assert nd == 0, c

m = a.merge(b, on="time", suffixes=("_old", "_new"))
assert len(m) == len(a) == len(b)
n = len(m)
print(f"\nsessions={n}  {m['time'].min().date()} -> {m['time'].max().date()}")
for c, lab in [("b200", "breadth"), ("decoup", "guard(decoup)"), ("cap", "macro cap"),
               ("state_dt4", "DT4 base"), ("state", "DT5G state")]:
    if c == "b200":
        d = (m["b200_old"].round(6) != m["b200_new"].round(6))
    else:
        d = (m[f"{c}_old"] != m[f"{c}_new"])
    print(f"  {lab:16s}: {int(d.sum())} diffs ({100*d.mean():.2f}%)")

d = m[m["state_old"] != m["state_new"]]
print(f"\nSTATE-diff sessions: {len(d)}")
if len(d):
    d[["time", "state_old", "state_new", "cap_old", "cap_new", "decoup_old", "decoup_new",
       "b200_old", "b200_new", "univ_old", "univ_new"]].to_csv(
        os.path.join(OUT, "state_diffs.csv"), index=False)
    print(d[["time", "state_old", "state_new", "cap_old", "cap_new"]].to_string(index=False))

dg = m[m["decoup_old"] != m["decoup_new"]]
print(f"\nGUARD-diff sessions: {len(dg)}")
if len(dg):
    dg.to_csv(os.path.join(OUT, "guard_diffs.csv"), index=False)
    print(dg.groupby(dg["time"].dt.year).size().to_string())
    # only matters where a US cap could actually be suppressed
    print("\nguard-diff sessions where macro cap ALSO differs:",
          int((dg["cap_old"] != dg["cap_new"]).sum()))

last = m.tail(3)
print("\nLAST 3 SESSIONS:")
print(last[["time", "state_old", "state_new", "state_dt4_old", "cap_old", "cap_new",
            "decoup_old", "decoup_new", "b200_old", "b200_new", "univ_old", "univ_new"]].to_string(index=False))
