# -*- coding: utf-8 -*-
"""
run_phase2_states.py
====================
Phase 2: for each candidate EW-gate config, run the FULL state chain
(ew_v1 -> concentration -> dual_v3 -> v3.1 -> v3.4b), save the candidate v3.4b state,
then measure how much survives to PRODUCTION level vs current prod (Close-500M):
  - v3.4b state agreement vs prod, transitions
  - DT5G pure-index NAV (1B, dep 0%, borrow 10%) via test_dt5g_nav_dep0.py
Canonical ew/v3.4b files are restored from .bak_closegate_20260601 at the end.
Integrated V4/V5 is run separately only for candidates that move the production state materially.
"""
import sys, io, os, subprocess
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
PY = sys.executable

CANDIDATES = [
    # label, env(TV_PRICE,LIQ_MIN,TOPN)
    ("price_250m", {"TV_PRICE":"1","LIQ_MIN":str(2.5e8),"TOPN":"0"}),
    ("price_500m", {"TV_PRICE":"1","LIQ_MIN":str(5e8),"TOPN":"0"}),
    ("topn_100",   {"TV_PRICE":"1","LIQ_MIN":"0","TOPN":"100"}),
]
V34B = "vnindex_5state_tam_quan_v3_4b_full_history.csv"
EWF  = "vnindex_5state_ew_full.csv"; EWS = "vnindex_5state_ew_staging.csv"
PROD = V34B + ".bak_closegate_20260601"   # current prod (close-500M) state

def run(cmd, env=None):
    e = dict(os.environ);
    if env: e.update(env)
    e["STATE_WORKDIR"] = WORKDIR
    r = subprocess.run(cmd, env=e, capture_output=True, text=True, shell=isinstance(cmd,str))
    if r.returncode != 0:
        print(f"  [FAIL] {cmd}\n{r.stderr[-1200:]}"); raise SystemExit(1)
    return r.stdout

def build_chain(env):
    run([PY,"vnindex_5state_ew_v1.py"], env)                              # -> canonical ew_full/staging
    run([PY,"build_concentration_history.py"])
    run([PY,"vnindex_5state_dual_v3.py"])
    run([PY,"deploy_v3_4b_package/build_v3_1_clean.py"])
    run("cp vnindex_5state_tam_quan_v3_1_clean.csv vnindex_5state_tam_quan_v3_1_full_history.csv")
    run([PY,"deploy_v3_4b_package/build_v3_4_bull_aware.py"])

prod = pd.read_csv(PROD, parse_dates=["time"])
def agree(c):
    m = prod.merge(c, on="time", suffixes=("_p","_c"))
    post = m[m.time>="2014-01-01"]
    return (post.state_p==post.state_c).mean()*100, int((c[c.time>="2014-01-01"].state.diff().fillna(0)!=0).sum())

results=[]
for label, env in CANDIDATES:
    print(f"\n===== building {label} =====")
    build_chain(env)
    cand_path = f"vnindex_5state_tam_quan_v3_4b_full_history.{label}.csv"
    run(f"cp {V34B} {cand_path}")
    c = pd.read_csv(cand_path, parse_dates=["time"])
    ag, tr = agree(c)
    # DT5G NAV on this candidate state
    out = run([PY,"test_dt5g_nav_dep0.py"], {"STATE_CSV":cand_path, "OUT_TAG":"_"+label})
    nav_lines = [l for l in out.splitlines() if "FULL 2000-now" in l or "Since 2011" in l or "MODERN" in l]
    print(f"  {label}: v3.4b agreement vs prod={ag:.1f}%  transitions={tr}")
    for l in nav_lines: print("   ", l.strip())
    results.append((label, ag, tr, nav_lines))

# restore canonical
run(f"cp {PROD} {V34B}")
run(f"cp {EWF}.bak_closegate_20260601 {EWF}")
run(f"cp {EWS}.bak_closegate_20260601 {EWS}")
print("\n[restored canonical ew/v3.4b to close-gate prod]")

print("\n"+"="*70+"\nSUMMARY (vs PROD Close-500M)\n"+"="*70)
for label, ag, tr, nav in results:
    print(f"{label:<12} v3.4b-agreement {ag:5.1f}%  trans {tr}")
