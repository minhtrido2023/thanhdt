#!/usr/bin/env python3
"""Chay MOT script bat ky voi custom_basket.py CUA WORKTREE, khong sua byte nao cua script do.

Cung ly do nhu run_wt_leg.py: cac selfcheck nay deu `sys.path.insert(0, WORKDIR)` voi WORKDIR
hardcode canonical, nen chay tu worktree van nap module CHUA SUA -> no-op im lang (§29).
argv: run_with_wt_basket.py <wt_root> <script.py> [args...]
"""
import importlib.util, runpy, sys
wt, script = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("custom_basket", f"{wt}/custom_basket.py")
mod = importlib.util.module_from_spec(spec); sys.modules["custom_basket"] = mod
spec.loader.exec_module(mod)
assert hasattr(mod, "retchain_legacy"), "nap sai file custom_basket"
print(f"[wrapper] custom_basket = {mod.__file__}  retchain_legacy={mod.retchain_legacy()}", flush=True)
sys.argv = [script] + sys.argv[3:]
runpy.run_path(script, run_name="__main__")
