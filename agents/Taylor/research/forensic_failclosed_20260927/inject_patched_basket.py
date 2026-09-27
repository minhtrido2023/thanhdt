"""Chạy engine pin (file CANONICAL, byte-identical) nhưng với `custom_basket` = bản VÁ ở worktree.

Vì sao cần: `pt_v23_audit_2014.py:41-42` HARDCODE `WORKDIR="/home/trido/thanhdt/WorkingClaude"`
rồi `sys.path.insert(0, WORKDIR)` ⇒ chạy engine từ worktree vẫn import `custom_basket` của cây
CANONICAL. Không có cách nào để cây worktree tự thắng (sys.path[0] bị chèn trước PYTHONPATH và
trước cả dir của script). Nên: nạp module VÁ vào `sys.modules["custom_basket"]` TRƯỚC, rồi
`runpy` engine canonical — engine không sửa một byte, `import custom_basket` thành no-op.
"""
import importlib.util
import runpy
import sys

patched, engine = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("custom_basket", patched)
mod = importlib.util.module_from_spec(spec)
sys.modules["custom_basket"] = mod
spec.loader.exec_module(mod)
print(f"[inject] custom_basket <- {mod.__file__}", flush=True)
sys.argv = [engine] + sys.argv[3:]
runpy.run_path(engine, run_name="__main__")
