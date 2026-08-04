"""Launcher — buoc pt_v23_audit_2014.py (BAN PRODUCTION, KHONG sua) import BAN SAO
nghien cuu cua simulate_holistic_nav.py (ban mang gate kha-thi-thi-hanh LAG_EXEC_GATE_K).

Vi sao can file nay: pt_v23_audit_2014.py:42 goi `sys.path.insert(0, WORKDIR)` TRUOC khi
`import simulate_holistic_nav`, nen WORKDIR luon thang PYTHONPATH (bai hoc run_jit.sh
2026-08-03: mot lan ablation im lang thanh no-op). Pre-seed sys.modules mien nhiem voi
thu tu sys.path.

Job Taylor_20260804_085248. Production files KHONG bi sua.
"""
import importlib.util
import json
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

# Cong cung: neu 2 dong nay khong in ra duong dan BAN SAO + dung K yeu cau thi lan chay la
# no-op va moi con so cua no phai bi vut bo.
assert _mod.__file__ == _shn_path, f"wrong module loaded: {_mod.__file__}"
_K = float(os.environ.get("LAG_EXEC_GATE_K", "0") or 0)
assert _mod._LAG_EXEC_GATE_K == _K, f"knob mismatch: {_mod._LAG_EXEC_GATE_K} != {_K}"
print(f"[DYNGATE] shn = {_mod.__file__}", flush=True)
print(f"[DYNGATE] LAG_EXEC_GATE_K = {_mod._LAG_EXEC_GATE_K}", flush=True)

_target = os.path.join(WORKDIR, "pt_v23_audit_2014.py")
sys.argv = [_target] + sys.argv[1:]
runpy.run_path(_target, run_name="__main__")

_drops = _mod._LAG_EXEC_GATE_DROPS
print(f"[DYNGATE] K={_mod._LAG_EXEC_GATE_K} dropped_entries={len(_drops)} "
      f"distinct_tickers={len(set(d['ticker'] for d in _drops))}", flush=True)
if _drops:
    _dp = os.path.join(EXP, f"drops_{os.environ.get('EXP_TAG', 'notag')}.json")
    with open(_dp, "w", encoding="utf-8") as _f:
        json.dump(_drops, _f, ensure_ascii=False, indent=1)
    print(f"[DYNGATE] -> {_dp}", flush=True)
