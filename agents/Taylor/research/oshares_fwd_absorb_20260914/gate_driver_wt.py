import os, sys, json
WT = os.environ["OSH_WT"]
sys.path.insert(0, WT)
import oshares_live, corp_action_lib
assert oshares_live.__file__.startswith(WT) and corp_action_lib.__file__.startswith(WT)
sys.path.insert(1, "/home/trido/thanhdt/WorkingClaude/mike/bin")
import corp_action_daily as cad
cad.WC_ROOT = WT        # đường cổng THẬT (gate_selfcheck + _model_files), chỉ trỏ gốc về worktree
print("model files:", cad._model_files(), flush=True)
ok, det = cad.gate_selfcheck()
print(json.dumps({"ok": ok, "detail": det}, ensure_ascii=False, indent=1))
sys.exit(0 if ok else 1)
