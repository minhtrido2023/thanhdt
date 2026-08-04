"""Ablation launcher v2 (job Taylor_20260804_012953) — same sys.modules pre-seed trick as
run_leg.py, plus a hard gate on the two NEW knobs of this round:

  PARK_BAND    — deadband cua khoi 4c (mac dinh 0.005 = hang so goc => byte-identical)
  PARK_STATES  — target park theo state (mac dinh "3:0.7" = so da pin)

Vi sao van can file rieng: `pt_v23_audit_2014.py:42` lam `sys.path.insert(0, WORKDIR)` TRUOC
`import simulate_holistic_nav`, nen WORKDIR luon thang PYTHONPATH. Pre-seed sys.modules mien
nhiem voi thu tu sys.path. Production files KHONG bi sua.
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

# Hard gate: neu 4 dong duoi khong in dung config yeu cau -> run la no-op, so PHAI vut bo.
assert _mod.__file__ == _shn_path, f"wrong module loaded: {_mod.__file__}"
assert _mod._PARK_JIT == os.environ.get("PARK_JIT", "on").lower()
assert _mod._PARK_PREFILL == os.environ.get("PARK_PREFILL", "on").lower()
assert abs(_mod._PARK_BAND - float(os.environ.get("PARK_BAND", "0.005"))) < 1e-12
print(f"[ABLATION] shn = {_mod.__file__}", flush=True)
print(f"[ABLATION] PARK_JIT={_mod._PARK_JIT}  PARK_PREFILL={_mod._PARK_PREFILL}  "
      f"PARK_BAND={_mod._PARK_BAND}  PARK_STATES={os.environ.get('PARK_STATES', '(unset)')}",
      flush=True)

_target = os.path.join(WORKDIR, "pt_v23_audit_2014.py")
sys.argv = [_target] + sys.argv[1:]
runpy.run_path(_target, run_name="__main__")
print(f"[ABLATION] done PARK_BAND={_mod._PARK_BAND} skipped_buys={_mod._PARK_JIT_SKIPPED[0]}", flush=True)
