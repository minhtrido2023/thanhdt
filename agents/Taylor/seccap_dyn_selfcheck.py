# -*- coding: utf-8 -*-
"""seccap_dyn_selfcheck.py — guards the BASKET_SECCAP_MODE branch (job Taylor_20260714_095953).

Checks, in order of what could silently corrupt a result:
  1. flag OFF  -> build_pit is byte-identical to the pre-patch behaviour (level series unchanged)
  2. flag ON   -> the per-rebal cap is actually applied and DIFFERS from the fixed-cap path
  3. mktx<f>   -> parses and scales; mktx0 collapses sector to ~0 (sanity of the multiplier)
  4. guard     -> flag with weight_scheme!='sectorcap' raises (no silent no-op)
  5. _cap_sector algebra: caps the group, preserves sum=1, leaves an under-cap group untouched
"""
import os, sys
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb

FAILS = []
def chk(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok: FAILS.append(name)

# ---- 5. pure algebra of _cap_sector (no BQ) ----
print("\n[5] _cap_sector algebra")
w = np.array([0.4, 0.4, 0.1, 0.1]); sec = np.array([8, 8, 1, 2])
out = cb._cap_sector(w, sec, 8, 0.50)
chk("caps group to scap", abs(out[sec == 8].sum() - 0.50) < 1e-9, f"got {out[sec==8].sum():.4f}")
chk("weights still sum to 1", abs(out.sum() - 1.0) < 1e-9, f"got {out.sum():.6f}")
chk("intra-group ratio preserved", abs(out[0] - out[1]) < 1e-12)
out2 = cb._cap_sector(np.array([0.2, 0.2, 0.3, 0.3]), sec, 8, 0.50)
chk("under-cap group untouched", np.allclose(out2, [0.2, 0.2, 0.3, 0.3]), "no-op when already <= scap")

# ---- BQ-backed: a SHORT window keeps this cheap but still exercises >=2 rebal dates ----
S, E = "2024-01-02", "2025-06-30"
os.environ["BASKET_SELECT"] = "yieldcombo"
def run(**envs):
    save = {k: os.environ.get(k) for k in envs}
    os.environ.update({k: str(v) for k, v in envs.items() if v is not None})
    for k, v in envs.items():
        if v is None: os.environ.pop(k, None)
    try:
        lvl, _, _, _ = cb.build_pit(bq, S, E, quality="none", rebal="q2m5", gate_rating=3,
                                    weight_scheme="sectorcap")
        return pd.Series(lvl)
    finally:
        for k, v in save.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v

print("\n[1] flag OFF = fixed-cap path (unchanged)")
off1 = run(BASKET_SECCAP_MODE=None)
off2 = run(BASKET_SECCAP_MODE="")
chk("OFF is deterministic / '' == unset", off1.equals(off2), f"{len(off1)} days")

print("\n[2] flag ON (mktcap) differs from fixed cap 0.50")
dyn = run(BASKET_SECCAP_MODE="mktcap")
chk("same date index", list(dyn.index) == list(off1.index))
chk("levels DIFFER from fixed-cap", not np.allclose(dyn.values, off1.values),
    f"final {dyn.iloc[-1]:.2f} (dyn) vs {off1.iloc[-1]:.2f} (fix50)")

print("\n[3] mktx<f> multiplier")
x0 = run(BASKET_SECCAP_MODE="mktx0")
chk("mktx0 differs from mktcap", not np.allclose(x0.values, dyn.values),
    f"final {x0.iloc[-1]:.2f} (sector ~excluded)")
x15 = run(BASKET_SECCAP_MODE="mktx1.5")
chk("mktx1.5 differs from mktcap", not np.allclose(x15.values, dyn.values), f"final {x15.iloc[-1]:.2f}")

print("\n[4] guard: flag + wrong weight_scheme must RAISE")
os.environ["BASKET_SECCAP_MODE"] = "mktcap"
try:
    cb.build_pit(bq, S, E, quality="none", rebal="q2m5", gate_rating=3, weight_scheme="namecap")
    chk("raises on namecap", False, "NO raise — silent no-op risk")
except ValueError as e:
    chk("raises on namecap", True, str(e)[:60])
finally:
    os.environ.pop("BASKET_SECCAP_MODE", None)

print("\n" + ("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL: {FAILS}"))
sys.exit(1 if FAILS else 0)
