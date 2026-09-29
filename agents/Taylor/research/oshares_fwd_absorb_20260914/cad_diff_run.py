"""Chạy corp_action_daily.run(asof) với OUT_DIR/STATE_PATH TẠM (tên phi-canonical, §8), không bus/notify.
OSH_ROOT = thư mục WorkingClaude chứa oshares_live.py cần dùng (tree thật = trước vá, worktree = sau vá).
gate_selfcheck bị thay bằng PASS giả — selfcheck được chạy RIÊNG, kết quả báo riêng."""
import glob, json, os, shutil, sys
ROOT = os.environ["OSH_ROOT"]; OUT = os.environ["OSH_TMP_OUT"]; ASOF = os.environ.get("OSH_ASOF", "2026-09-14")
REAL = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, ROOT)
import corp_action_lib, oshares_live, oshares_pit  # noqa
assert oshares_live.__file__.startswith(ROOT), oshares_live.__file__
sys.path.insert(1, os.path.join(REAL, "mike", "bin"))
import corp_action_daily as cad
assert cad.oshares_at.__module__ == "oshares_live" and sys.modules["oshares_live"].__file__.startswith(ROOT)
os.makedirs(OUT, exist_ok=True)
for p in sorted(glob.glob(os.path.join(REAL, "data", "corp_action_daily", "corp_action_daily_*.json"))):
    if os.path.basename(p) < f"corp_action_daily_{ASOF}":           # chỉ mốc TRƯỚC asof, bản sao
        shutil.copy2(p, OUT)
st = os.path.join(OUT, "state.json")
if os.path.exists(cad.STATE_PATH):
    shutil.copy2(cad.STATE_PATH, st)
cad.OUT_DIR, cad.STATE_PATH, cad.WC_ROOT = OUT, st, ROOT
cad.bus = lambda *a, **k: None
cad.notify = lambda *a, **k: print("[notify:suppressed]", str(a[0])[:160] if a else "")
cad.gate_selfcheck = lambda: (True, [{"module": "skipped-in-diff-run", "rc": 0, "tail": []}])
print("model_version", cad.model_version())
rc, snap = cad.run(asof=ASOF, dry_run=False, alert=False)
print("rc", rc, "status", snap.get("status"))
