"""Chạy một script/selfcheck với oshares_live/oshares_pit/corp_action_lib NẠP TỪ WORKTREE (không chạm tree thật)."""
import os, runpy, sys
WT = os.environ["OSH_WT"]
sys.path.insert(0, WT)
import corp_action_lib, oshares_live, oshares_pit  # noqa
for m in (corp_action_lib, oshares_live, oshares_pit):
    assert m.__file__.startswith(WT), m.__file__
print(f"[run_with_wt] modules from {WT}", flush=True)
script = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name="__main__")
