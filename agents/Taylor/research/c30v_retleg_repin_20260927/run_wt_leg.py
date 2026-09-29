#!/usr/bin/env python3
"""Chay engine pin R3 voi custom_basket.py CUA WORKTREE, khong sua mot byte nao cua engine.

Vi sao can wrapper (doc truoc khi "don gian hoa"): `pt_v23_audit_2014.py:42` lam
`sys.path.insert(0, WORKDIR)` voi WORKDIR = /home/trido/thanhdt/WorkingClaude HARDCODE. Chay
`$DNA_PYEXE <worktree>/pt_v23_audit_2014.py` vi the van import `custom_basket` CANONICAL (chua
sua) — mot no-op IM LANG, dung lop loi §29/§28. Wrapper nay nap module da sua vao `sys.modules`
TRUOC khi engine chay, nen moi `import custom_basket` o bat ky tang nao deu tro ve dung ban do,
ma KHONG can sua sys.path cua engine (engine giu nguyen byte => data path = dung moi truong pin).

argv: run_wt_leg.py <wt_root> <engine_args...>
"""
import importlib.util
import runpy
import sys

wt = sys.argv[1]
spec = importlib.util.spec_from_file_location("custom_basket", f"{wt}/custom_basket.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["custom_basket"] = mod
spec.loader.exec_module(mod)
assert hasattr(mod, "retchain_legacy"), "worktree custom_basket thieu knob -> nap sai file"
print(f"[wrapper] custom_basket = {mod.__file__}  retchain_legacy={mod.retchain_legacy()}", flush=True)

sys.argv = [f"{wt}/pt_v23_audit_2014.py"] + sys.argv[2:]
runpy.run_path(f"{wt}/pt_v23_audit_2014.py", run_name="__main__")
