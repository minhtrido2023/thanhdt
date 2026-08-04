"""Ablation launcher — force pt_v23_audit_2014.py to import the RESEARCH copy of
simulate_holistic_nav.py (the one carrying the PARK_JIT switch).

Why this file exists: `pt_v23_audit_2014.py:42` does `sys.path.insert(0, WORKDIR)`
BEFORE `import simulate_holistic_nav`, so WORKDIR always wins over PYTHONPATH.
The first ablation attempt (run_jit.sh, 2026-08-03 23:57) used PYTHONPATH and was a
silent no-op: all three legs produced byte-identical CSVs (md5 7d053e62...).
Pre-seeding sys.modules is immune to sys.path order.

Production files are NOT modified. Usage mirrors pt_v23_audit_2014.py's own argv.
"""
import importlib.util
import os
import runpy
import sys

EXP = os.path.dirname(os.path.abspath(__file__))
WORKDIR = "/home/trido/thanhdt/WorkingClaude"

_shn_path = os.path.join(EXP, "simulate_holistic_nav.py")
_spec = importlib.util.spec_from_file_location("simulate_holistic_nav", _shn_path)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["simulate_holistic_nav"] = _mod
_spec.loader.exec_module(_mod)

# Hard gate: if these two lines don't print the RESEARCH path + the requested leg,
# the run is a no-op and its numbers must be discarded.
assert _mod.__file__ == _shn_path, f"wrong module loaded: {_mod.__file__}"
assert _mod._PARK_JIT == os.environ.get("PARK_JIT", "on").lower()
assert _mod._PARK_PREFILL == os.environ.get("PARK_PREFILL", "on").lower()
print(f"[ABLATION] shn = {_mod.__file__}", flush=True)
print(f"[ABLATION] PARK_JIT = {_mod._PARK_JIT}  PARK_PREFILL = {_mod._PARK_PREFILL}", flush=True)

_target = os.path.join(WORKDIR, "pt_v23_audit_2014.py")
sys.argv = [_target] + sys.argv[1:]
runpy.run_path(_target, run_name="__main__")
print(f"[ABLATION] PARK_JIT={_mod._PARK_JIT} skipped_buys={_mod._PARK_JIT_SKIPPED[0]}", flush=True)
