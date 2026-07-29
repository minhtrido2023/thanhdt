# -*- coding: utf-8 -*-
"""POST-MERGE self-check — runs against the MERGED production module itself.

Catches a copy/paste error in the merge (quant-skeptic's recommendation, bus
verify_20260729_153007). Every expected number below is the pre-registered one
from research/dt5g_breadth_guard_universe_pit_20260729.md — any mismatch = STOP + revert.

T1  production (default BREADTH_SOURCE="pit") == harness dt5g_pit.csv      (0 diffs, 4 cols)
T2  production BREADTH_SOURCE="prune"         == harness dt5g_prune.csv    (0 diffs) -> rollback exact
T3  production BREADTH_SOURCE="prune"         == PRE-MERGE production file (0 diffs) -> no behaviour drift
T4  pit vs prune on the merged module: state 0 diffs / cap 13 / guard 229 over 3135 sessions
T5  breadth SQL of the "prune" branch is TEXTUALLY the pre-merge production SQL
T6  get_gated_state today unchanged: NEUTRAL(3), source DT5G_macro
"""
import os, sys, importlib.util, re
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WORKDIR, "mike/agents/Taylor/exp_dt5g_breadth_pit")
PREMERGE = "/tmp/macro_state_live.PREMERGE.py"
sys.path.insert(0, WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)
from simulate_holistic_nav import bq  # noqa: E402
import macro_state_live as prod       # noqa: E402  <- the MERGED production module

START, END = "2014-01-01", "2026-07-29"
COLS = ["state", "state_dt4", "cap", "easing"]
res = []


def diff(x, y, label, expect=0):
    mg = x.merge(y, on="time", suffixes=("_a", "_b"))
    assert len(mg) == len(x) == len(y), f"{label}: row mismatch {len(x)}/{len(y)}/{len(mg)}"
    bad = {c: int((mg[f"{c}_a"] != mg[f"{c}_b"]).sum()) for c in COLS}
    ok = all(v == expect for v in bad.values())
    print(f"[{'PASS' if ok else 'FAIL'}] {label}: {bad}  (n={len(mg)})")
    res.append(ok)
    return mg


assert prod.BREADTH_SOURCE == "pit", f"merged default must be 'pit', got {prod.BREADTH_SOURCE!r}"

# T1 — merged production, default source
d_pit = prod.get_macro_state(START, END, bq=bq)
h_pit = pd.read_csv(os.path.join(OUT, "dt5g_pit.csv"), parse_dates=["time"])
diff(d_pit, h_pit[["time"] + COLS], "T1 PROD(pit, merged) vs harness(pit)")

# T2 — one-word rollback
prod.BREADTH_SOURCE = "prune"
d_pr = prod.get_macro_state(START, END, bq=bq)
h_pr = pd.read_csv(os.path.join(OUT, "dt5g_prune.csv"), parse_dates=["time"])
diff(d_pr, h_pr[["time"] + COLS], "T2 PROD(prune rollback) vs harness(prune)")

# T3 — rollback vs the ACTUAL pre-merge production file
spec = importlib.util.spec_from_file_location("premerge_prod", PREMERGE)
pm = importlib.util.module_from_spec(spec); spec.loader.exec_module(pm)
d_pm = pm.get_macro_state(START, END, bq=bq)
diff(d_pr, d_pm, "T3 PROD(prune rollback) vs PRE-MERGE production file")
prod.BREADTH_SOURCE = "pit"

# T4 — the headline A/B claim, recomputed on the merged module
mg = d_pit.merge(d_pr, on="time", suffixes=("_pit", "_pr"))
n_state = int((mg["state_pit"] != mg["state_pr"]).sum())
n_dt4 = int((mg["state_dt4_pit"] != mg["state_dt4_pr"]).sum())
n_cap = int((mg["cap_pit"] != mg["cap_pr"]).sum())
n_guard = int((h_pit["decoup"].values != h_pr["decoup"].values).sum())
ok4 = (len(mg) == 3135 and n_state == 0 and n_dt4 == 0 and n_cap == 13 and n_guard == 229)
print(f"[{'PASS' if ok4 else 'FAIL'}] T4 pit-vs-prune on merged module: sessions={len(mg)} (exp 3135) "
      f"state={n_state} (exp 0) dt4={n_dt4} (exp 0) cap={n_cap} (exp 13) guard={n_guard} (exp 229)")
res.append(ok4)

# T5 — rollback SQL textually == pre-merge production SQL
m = re.search(r'bd = bq\(f"""(.*?)"""\)', open(PREMERGE, encoding="utf-8").read(), re.S)
old_sql = m.group(1).replace("{qstart}", "QS").replace("{end}", "EN").split("SELECT t.time", 1)[1]
prod.BREADTH_SOURCE = "prune"
new_sql = prod._breadth_sql("QS", "EN").split("SELECT t.time", 1)[1]
prod.BREADTH_SOURCE = "pit"
ok5 = old_sql.strip() == new_sql.strip()
print(f"[{'PASS' if ok5 else 'FAIL'}] T5 rollback SQL identical to pre-merge production SQL")
res.append(ok5)

# T6 — live gated path today
g = prod.get_gated_state("2026-06-01", END, bq=bq, alert=False)
last = g.iloc[-1]
ok6 = int(last["state"]) == 3 and last["source"] == "DT5G_macro"
print(f"[{'PASS' if ok6 else 'FAIL'}] T6 get_gated_state today={last['time'].date()} "
      f"state={int(last['state'])} (exp 3=NEUTRAL) source={last['source']} (exp DT5G_macro)")
res.append(ok6)

print(f"\n{sum(res)}/{len(res)} PASS")
sys.exit(0 if all(res) else 1)
