# -*- coding: utf-8 -*-
"""Self-check on the PROPOSED production file itself (not the harness variant).

T1  PROPOSED(BREADTH_SOURCE="pit")   == harness `pit` run     (0 diffs, all 4 state columns)
T2  PROPOSED(BREADTH_SOURCE="prune") == LIVE macro_state_live (0 diffs) -> rollback is exact
T3  breadth SQL of PROPOSED-"prune"  == the SQL string currently in production (textual)
T4  today's gated state unchanged (get_gated_state, live path)
"""
import os, sys, importlib.util, re
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WORKDIR, "mike/agents/Taylor/exp_dt5g_breadth_pit")
sys.path.insert(0, WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)
from simulate_holistic_nav import bq  # noqa: E402
import macro_state_live as prod       # noqa: E402

START, END = "2014-01-01", "2026-07-29"
COLS = ["state", "state_dt4", "cap", "easing"]


def load_proposed(src):
    spec = importlib.util.spec_from_file_location(
        f"proposed_{src}", os.path.join(OUT, "macro_state_live.PROPOSED.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.BREADTH_SOURCE = src
    return m


def diff(x, y, label):
    mg = x.merge(y, on="time", suffixes=("_a", "_b"))
    assert len(mg) == len(x) == len(y), f"{label}: row mismatch {len(x)}/{len(y)}/{len(mg)}"
    bad = {c: int((mg[f"{c}_a"] != mg[f"{c}_b"]).sum()) for c in COLS}
    ok = all(v == 0 for v in bad.values())
    print(f"[{'PASS' if ok else 'FAIL'}] {label}: {bad}")
    return ok

res = []

# T1 — proposed(pit) vs harness pit
mp = load_proposed("pit")
dp = mp.get_macro_state(START, END, bq=bq)
harness = pd.read_csv(os.path.join(OUT, "dt5g_pit.csv"), parse_dates=["time"])
res.append(diff(dp, harness[["time"] + COLS], "T1 PROPOSED(pit) vs harness(pit)"))

# T2 — proposed(prune) rollback vs live production
mr = load_proposed("prune")
dr = mr.get_macro_state(START, END, bq=bq)
pp = prod.get_macro_state(START, END, bq=bq)
res.append(diff(dr, pp, "T2 PROPOSED(prune rollback) vs LIVE production"))

# T3 — the rollback SQL is textually the production SQL
prod_src = open(os.path.join(WORKDIR, "macro_state_live.py"), encoding="utf-8").read()
m = re.search(r'bd = bq\(f"""(.*?)"""\)', prod_src, re.S)
prod_sql = m.group(1).replace("{qstart}", "QS").replace("{end}", "EN")
new_sql = mr._breadth_sql("QS", "EN").split("SELECT t.time", 1)[1]
prod_sql_body = prod_sql.split("SELECT t.time", 1)[1]
ok3 = prod_sql_body.strip() == new_sql.strip()
print(f"[{'PASS' if ok3 else 'FAIL'}] T3 rollback SQL identical to production SQL")
res.append(ok3)

# T4 — today's gated state, live path, both sources
g_old = prod.get_gated_state("2026-06-01", END, bq=bq, alert=False)
g_new = mp.get_gated_state("2026-06-01", END, bq=bq, alert=False)
mg = g_old.merge(g_new, on="time", suffixes=("_o", "_n"))
nd = int((mg["state_o"] != mg["state_n"]).sum())
src_o, src_n = g_old["source"].iloc[-1], g_new["source"].iloc[-1]
ok4 = nd == 0 and src_o == src_n
print(f"[{'PASS' if ok4 else 'FAIL'}] T4 get_gated_state: {nd} diffs over {len(mg)} sessions; "
      f"today={g_old['time'].iloc[-1].date()} state {g_old['state'].iloc[-1]}->{g_new['state'].iloc[-1]} "
      f"source {src_o}/{src_n}")
res.append(ok4)

print(f"\n{sum(res)}/{len(res)} PASS")
sys.exit(0 if all(res) else 1)
