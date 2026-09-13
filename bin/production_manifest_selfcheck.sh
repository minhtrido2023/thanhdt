#!/usr/bin/env bash
# production_manifest_selfcheck.sh — kb/production_manifest.json (bản COMMIT) còn khớp thực tế không.
#
# Việc C review ARIA (job Wags_20260913_053331). Tái sinh manifest từ crontab + systemd + hook +
# bao đóng import/exec rồi so với bản đã commit trong repo mike: lệch (file vào/rời production,
# đổi tầng, gốc cron mới/mất, gốc chưa phân loại) = FAIL. Được run_selfchecks.sh tự khám phá theo
# glob ⇒ weekly_ops_audit.sh + bộ dò đỏ hằng ngày bắt drift. KHÔNG thêm cron riêng (§11).
#
# Trước khi so, tự chứng minh bộ so còn SỐNG (bài học 2026-08-29: harness hỏng thì "khớp" đọc
# ngược hoàn toàn): (1) các ca parse tối thiểu; (2) chèn 1 dòng cron giả trỏ tới file research
# thật ⇒ bộ so PHẢI báo lệch.
set -uo pipefail
MIKE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC="$(cd "$MIKE/.." && pwd)"
GEN="$MIKE/bin/production_manifest.py"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fail=0

if ! command -v crontab >/dev/null || ! crontab -l >"$TMP/crontab" 2>/dev/null; then
  echo "SKIP: không đọc được crontab -l trong môi trường này — manifest dựng từ crontab, không kiểm được"
  exit 0
fi
if ! git -C "$MIKE" show HEAD:kb/production_manifest.json >"$TMP/committed.json" 2>/dev/null; then
  echo "FAIL: kb/production_manifest.json chưa có trong HEAD repo mike — chạy '$GEN' rồi commit"
  exit 1
fi

# (1) ca parse — (loại, nội dung, file đích (basename), kind mong đợi; "none" = không được có cạnh)
cd "$WC" && python3 - "$GEN" <<'PY' || fail=1
import sys, os, tempfile, importlib.util
spec = importlib.util.spec_from_file_location("pm", sys.argv[1]); pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)
cases = [
  ("sh", '"$ROOT/bin/jobs.sh" status x', "jobs.sh", "exec"),
  ("sh", 'echo "chạy mike/bin/jobs.sh để xem"', "jobs.sh", "none"),
  ("sh", 'echo xem mike/bin/jobs.sh >&2; "$ROOT/bin/mike_json.py" get', "jobs.sh", "none"),
  ("sh", 'notify "🟡 lỗi — xem mike/bin/jobs.sh" || true', "jobs.sh", "none"),
  ("sh", '# comment mike/bin/jobs.sh', "jobs.sh", "none"),
  ("sh", 'case "$f" in\n  *jobs.sh|*x.py) t=1 ;;\nesac', "jobs.sh", "none"),
  ("sh", 'FILES=(\n  "$ROOT/bin/jobs.sh"\n)', "jobs.sh", "ref"),
  ("sh", "python3 - <<'PY'\nimport mike_json\nPY", "mike_json.py", "import"),
  # arch-review 2026-09-13 F2: prompt NHIỀU DÒNG gửi agent không phải lệnh
  ("sh", 'dispatch.sh Winston "sửa lỗi điều phối\n  chạy mike/bin/jobs.sh list\n  rồi báo lại" --bg', "jobs.sh", "none"),
  # F3: printf … | script — giữ vế sau pipe
  ("sh", 'printf \'%s\' "$p" | timeout 25 python3 "$ROOT/bin/jobs.sh"', "jobs.sh", "exec"),
  ("sh", 'out=$(echo "$j" | python3 "$ROOT/bin/mike_json.py" get)', "mike_json.py", "exec"),
  # thân bash -c '…' nhiều dòng có idiom '"$VAR"' vẫn là lệnh (wags_autofix.sh:147)
  ("sh", 'setsid bash -c \'\n  ROOT="\'"$ROOT"\'"; L=\'"$(printf %q "$L")"\'\n  "$ROOT/bin/jobs.sh" list\n\' &', "jobs.sh", "exec"),
  # heredoc mở bên trong "$(…" (eod_trading_report.sh:275)
  ("sh", 'R="$(python3 - "$A" << \'PYEOF\'\nimport mike_json\nPYEOF\n)"', "mike_json.py", "import"),
  ("py", 'import subprocess\nsubprocess.run([str(ROOT / "bin" / "jobs.sh")])', "jobs.sh", "exec"),
  ("py", 'ok = "jobs.sh" in text', "jobs.sh", "none"),
  ("py", 'print("xem jobs.sh")', "jobs.sh", "none"),
  # F4: import trong hàm tự-kiểm nội tuyến không phải đường production
  ("py", 'def _selfcheck():\n    import mike_json\n', "mike_json.py", "none"),
]
bad = 0
d = os.path.join(pm.MIKE, "bin")
for lang, src, tgt, want in cases:
    e = pm.edges_python_src(src, d) if lang == "py" else pm.edges_shell_src(src, d)
    kinds = {k for f, k in e if os.path.basename(f) == tgt}
    ok = (not kinds) if want == "none" else (kinds == {want})
    if not ok:
        bad += 1
        print(f"FAIL parse-case [{lang}] {src!r}: mong {tgt}:{want}, được {[(pm.rel(f), k) for f, k in e]}")
# F1: file có thật nhưng CHƯA track git không được vào manifest; file đã track thì được
with tempfile.NamedTemporaryFile(dir=os.path.join(pm.MIKE, "logs"), prefix=".pm_untracked_probe_", suffix=".py") as t:
    if pm.in_scope(t.name):
        bad += 1; print(f"FAIL untracked-probe: {pm.rel(t.name)} (untracked) lọt in_scope")
if not pm.in_scope(os.path.join(d, "jobs.sh")):
    bad += 1; print("FAIL tracked-probe: mike/bin/jobs.sh (tracked) bị in_scope loại")
n = len(cases) + 2
print(f"parse-cases: {n - bad}/{n} PASS")
sys.exit(1 if bad else 0)
PY

# (2) bộ so phải BẮT được drift giả: dòng cron trỏ tới file research thật (score_live_signals.py —
# không cron nào chạy) ⇒ phải báo '+ score_live_signals.py' và gốc chưa phân loại.
PROBE="$WC/score_live_signals.py"
if [ -f "$PROBE" ]; then
  cp "$TMP/crontab" "$TMP/crontab_mut"
  echo "0 0 * * * /usr/bin/python3 $PROBE" >>"$TMP/crontab_mut"
  out="$(cd "$WC" && python3 "$GEN" --crontab "$TMP/crontab_mut" --check "$TMP/committed.json" 2>&1)"; rc=$?
  if [ "$rc" -eq 1 ] && grep -q "^+ score_live_signals.py" <<<"$out" && grep -q "^? score_live_signals.py" <<<"$out"; then
    echo "drift-probe: PASS (bộ so bắt được dòng cron giả)"
  else
    echo "FAIL drift-probe: bộ so KHÔNG bắt được dòng cron giả (rc=$rc) — kết quả 'khớp' bên dưới không đáng tin"
    echo "$out" | head -5; fail=1
  fi
else
  echo "FAIL drift-probe: thiếu file dò $PROBE — chọn file research khác cho probe"; fail=1
fi

# (2b) bộ so phải BẮT được lệch TẦNG và lệch GỐC (arch-review F5: tắt so tầng/gốc mà probe (2) vẫn PASS):
# sửa bản committed tạm — hạ run_bot.sh T0->T2, đổi lịch 1 gốc cron — --check phải báo '~' và '+/- gốc'.
python3 - "$TMP/committed.json" "$TMP/committed_mut.json" <<'PY' || fail=1
import json, sys
m = json.load(open(sys.argv[1]))
m["files"]["mike/bin/run_bot.sh"]["tier"] = "T2"
r = next(r for r in m["roots"] if r["kind"] == "cron")
r["schedule"] = "9 9 9 9 9"
json.dump(m, open(sys.argv[2], "w"))
PY
out="$(cd "$WC" && python3 "$GEN" --crontab "$TMP/crontab" --check "$TMP/committed_mut.json" 2>&1)"; rc=$?
if [ "$rc" -eq 1 ] && grep -q "^~ mike/bin/run_bot.sh tầng T2 -> T0" <<<"$out" \
   && grep -q "^+ gốc" <<<"$out" && grep -q "^- gốc ('cron', '9 9 9 9 9'" <<<"$out"; then
  echo "tier/root-probe: PASS (bộ so bắt được lệch tầng + lệch gốc)"
else
  echo "FAIL tier/root-probe (rc=$rc) — bộ so không bắt lệch tầng/gốc"; echo "$out" | head -6; fail=1
fi

# (3) so thật
out="$(cd "$WC" && python3 "$GEN" --crontab "$TMP/crontab" --check "$TMP/committed.json" 2>&1)"; rc=$?
echo "$out"
[ "$rc" -eq 0 ] || fail=1

[ "$fail" -eq 0 ] && echo "PASS production_manifest_selfcheck" || echo "FAIL production_manifest_selfcheck"
exit "$fail"
