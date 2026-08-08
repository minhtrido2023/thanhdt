# -*- coding: utf-8 -*-
"""eyrisk_selector_selfcheck.py — guards for BASKET_SELECT=eyrisk (risk-adjusted earnings yield).
Job Taylor_20260715_025346. Research-only; asserts, writes nothing production reads.

RUNTIME BUDGET: ~178s (measured solo, 2026-08-08) — run it with `timeout 400`, NOT the suite's
default 150s, or it reports a false TIMEOUT (it did, in the 2026-08-08 inventory). The cost is real
BQ round-trips against the live feature panel, and that is the point: every guard below is an
identity/negative-control on the REAL panel, so a mocked BQ would assert against the mock instead of
the selector. Slow-but-honest beats fast-but-vacuous here; do not "fix" this by stubbing BQ.

  [1] OFF is BYTE-IDENTICAL — eyonly (and yieldcombo) membership from the edited module equals the
      PRE-EDIT module (`git show HEAD:custom_basket.py`), so the eyrisk branches are inert when off.
  [2] FAIL-OPEN identity — eyrisk(all) on a doctored panel whose ROE_Min5Y is ALL NaN must pick
      exactly what eyonly picks (missing floor -> m=1.0 -> ey_adj == ey, rank unchanged).
  [3] WIRING — eyrisk(all) on the REAL panel must differ from eyonly on >=1 rebal; if it never
      differs the penalty never binds in the top-30 and the arms measure nothing (report, not run).
  [4] NEGATIVE CONTROL — doctored panel with ROE_Min5Y=-1 for FINANCIAL routes only: eyrisk(all)
      must move names (non-uniform multiplier MUST reorder; a no-op here voids [2]/[3]).
  [5] SCOPE — doctored panel with ROE_Min5Y=-1 for NON-financial routes only: eyrisk(fin) must
      equal eyonly (fin scope never reads a non-financial's floor), while eyrisk(all) must differ.
  [6] MULTIPLIER UNIT — clip(0.5 + 5r, 0.5, 1.0): r<=0 -> 0.5, 0.05 -> 0.75, >=0.10 -> 1.0.

Run: $DNA_PYEXE eyrisk_selector_selfcheck.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
import types

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq as _bq_real  # noqa: E402
import custom_basket as cb  # noqa: E402

START, END = "2022-01-04", "2026-06-19"
PIT = dict(quality="none", rebal="q2m5", gate_rating=3, top_n=30, name_cap=0.10, qtilt=None)
FIN_ROUTES = {"BANK", "INSURANCE", "SECURITIES"}
PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def build(mod, select, **env):
    saved = {k: os.environ.get(k) for k in list(env) + ["BASKET_SELECT"]}
    os.environ["BASKET_SELECT"] = select
    for k, v in env.items():
        os.environ[k] = str(v)
    try:
        lvl, adv, mem, bx = mod.build_pit(_bq_real, START, END, weight_scheme="namecap", **PIT)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return lvl, mem


def memkey(mem):
    m = mem.copy()
    m["rebal_date"] = pd.to_datetime(m["rebal_date"])
    return {d: tuple(sorted(g["ticker"])) for d, g in m.groupby("rebal_date")}


def ndiff(a, b):
    """Number of rebals whose MEMBERSHIP SET differs (order-insensitive: set semantics)."""
    ka, kb = memkey(a), memkey(b)
    return sum(1 for d in ka if ka[d] != kb.get(d))


def load_module_with_panel(doctor=None):
    """Exec custom_basket source with __file__ in a tmpdir whose data/value_panel_2014.csv is
    doctored by `doctor(df)->df`; every other data file the module touches is symlinked real."""
    tmp = tempfile.mkdtemp(prefix="eyrisk_sc_")
    os.makedirs(os.path.join(tmp, "data"))
    for f in ("forensic_flags.csv",):
        src = os.path.join(WORKDIR, "data", f)
        if os.path.exists(src):
            os.symlink(src, os.path.join(tmp, "data", f))
    pan = pd.read_csv(os.path.join(WORKDIR, "data", "value_panel_2014.csv"))
    if doctor is not None:
        pan = doctor(pan)
    pan.to_csv(os.path.join(tmp, "data", "value_panel_2014.csv"), index=False)
    src = open(os.path.join(WORKDIR, "custom_basket.py")).read()
    m = types.ModuleType(f"custom_basket_doct_{os.path.basename(tmp)}")
    m.__file__ = os.path.join(tmp, "custom_basket.py")
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m, tmp


def load_pre_edit():
    src = subprocess.run(["git", "show", "HEAD:./custom_basket.py"], cwd=WORKDIR,
                         capture_output=True, text=True, check=True).stdout
    m = types.ModuleType("custom_basket_preedit")
    m.__file__ = os.path.join(WORKDIR, "custom_basket.py")
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


print("== [6] multiplier unit test (formula fixed a priori — no grid) ==")
f = lambda r: float(np.clip(0.5 + 5.0 * r, 0.5, 1.0))
check("6a r=-0.5 -> 0.5", f(-0.5) == 0.5)
check("6b r=0    -> 0.5", f(0.0) == 0.5)
check("6c r=0.05 -> 0.75", abs(f(0.05) - 0.75) < 1e-12)
check("6d r=0.10 -> 1.0", abs(f(0.10) - 1.0) < 1e-12)
check("6e r=0.30 -> 1.0 (cap)", f(0.30) == 1.0)

print("== [1] OFF-path byte-identical vs pre-edit (eyonly + yieldcombo) ==")
pre = load_pre_edit()
_, mem_eyonly_pre = build(pre, "eyonly")
_, mem_eyonly = build(cb, "eyonly")
check("1a eyonly identical", memkey(mem_eyonly) == memkey(mem_eyonly_pre))
_, mem_yc_pre = build(pre, "yieldcombo")
_, mem_yc = build(cb, "yieldcombo")
check("1b yieldcombo identical", memkey(mem_yc) == memkey(mem_yc_pre))

print("== [2] fail-open identity: all-NaN ROE_Min5Y -> eyrisk(all) == eyonly ==")
m_nan, tmp1 = load_module_with_panel(lambda p: p.assign(ROE_Min5Y=np.nan))
_, mem_r_nan = build(m_nan, "eyrisk", BASKET_RISK_SCOPE="all")
check("2 fail-open identity", memkey(mem_r_nan) == memkey(mem_eyonly),
      f"diff rebals={ndiff(mem_r_nan, mem_eyonly)}")

print("== [3] wiring: eyrisk(all) real panel differs from eyonly ==")
_, mem_r_all = build(cb, "eyrisk", BASKET_RISK_SCOPE="all")
d3 = ndiff(mem_r_all, mem_eyonly)
check("3 penalty binds somewhere", d3 >= 1, f"membership differs on {d3} rebals")

print("== [4] negative control: ROE=-1 on FINANCIAL routes moves eyrisk(all) ==")


def _doct_fin(p):
    p = p.copy()
    p.loc[p["route"].isin(FIN_ROUTES), "ROE_Min5Y"] = -1.0
    return p


m_fin, tmp2 = load_module_with_panel(_doct_fin)
_, mem_r_finpen = build(m_fin, "eyrisk", BASKET_RISK_SCOPE="all")
d4 = ndiff(mem_r_finpen, mem_eyonly)
check("4 non-uniform penalty reorders", d4 >= 1, f"differs on {d4} rebals")

print("== [5] scope: ROE=-1 on NON-financials -> eyrisk(fin) inert, eyrisk(all) not ==")


def _doct_nonfin(p):
    p = p.copy()
    p.loc[~p["route"].isin(FIN_ROUTES), "ROE_Min5Y"] = -1.0
    return p


m_nf, tmp3 = load_module_with_panel(_doct_nonfin)
_, mem_fin_scope = build(m_nf, "eyrisk", BASKET_RISK_SCOPE="fin")
# fin scope on this panel: financial floors are REAL panel values -> penalty may still bind on
# financials exactly as it does on the real panel with scope=fin. So the identity reference is
# eyrisk(fin) on the REAL panel, not eyonly.
_, mem_fin_real = build(cb, "eyrisk", BASKET_RISK_SCOPE="fin")
check("5a fin scope ignores non-fin floors", memkey(mem_fin_scope) == memkey(mem_fin_real),
      f"diff rebals={ndiff(mem_fin_scope, mem_fin_real)}")
_, mem_all_scope = build(m_nf, "eyrisk", BASKET_RISK_SCOPE="all")
d5 = ndiff(mem_all_scope, mem_fin_real)
check("5b all scope DOES read them", d5 >= 1, f"differs on {d5} rebals")

for t in (tmp1, tmp2, tmp3):
    shutil.rmtree(t, ignore_errors=True)

print(f"\n== SUMMARY: {len(PASS)} PASS / {len(FAIL)} FAIL ==")
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)
