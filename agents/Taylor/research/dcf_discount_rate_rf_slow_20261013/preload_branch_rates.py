# -*- coding: utf-8 -*-
"""Run a selfcheck that lives in the MAIN checkout (needs the gitignored data/ that a worktree
lacks) against the BRANCH's deposit_rate_vn / cctg_rate_vn: pre-register the branch modules in
sys.modules, point them at the live CSVs, then run the target as __main__.
Limit: a target that re-loads these modules by file path, or shells out, bypasses the preload."""
import importlib.util, os, runpy, sys
WT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-dcffb-1013/WorkingClaude"
LIVE = "/home/trido/thanhdt/WorkingClaude/data"
for name in ("cctg_rate_vn", "deposit_rate_vn"):
    spec = importlib.util.spec_from_file_location(name, f"{WT}/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    mod._EVENTS_CSV = f"{LIVE}/{name}_events.csv"
assert "last_known_good_cctg" in dir(sys.modules["cctg_rate_vn"])
target = os.path.abspath(sys.argv[1])
sys.argv = sys.argv[1:]
sys.path.insert(0, os.path.dirname(target))
os.chdir(os.path.dirname(target))
try:
    runpy.run_path(target, run_name="__main__")
finally:
    used = sys.modules["deposit_rate_vn"].__file__
    print(f"\n[preload] deposit_rate_vn in use at exit: {used}", file=sys.stderr)
