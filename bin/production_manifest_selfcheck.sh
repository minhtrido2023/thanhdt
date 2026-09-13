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

# (1) ca parse — mỗi ca: loại file | nội dung | file đích | kind mong đợi ("none" = không được có cạnh)
cd "$WC" && python3 - "$GEN" <<'PY' || fail=1
import sys, os, importlib.util
spec = importlib.util.spec_from_file_location("pm", sys.argv[1]); pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)
J = os.path.join(pm.WC, "mike/bin/jobs.sh")
cases = [
  ("sh", '"$ROOT/bin/jobs.sh" status x', "exec"),
  ("sh", 'echo "chạy mike/bin/jobs.sh để xem"', "none"),
  ("sh", 'notify "🟡 lỗi — xem mike/bin/jobs.sh" || true', "none"),
  ("sh", '# comment mike/bin/jobs.sh', "none"),
  ("sh", 'case "$f" in\n  *jobs.sh|*x.py) t=1 ;;\nesac', "none"),
  ("sh", 'FILES=(\n  "$ROOT/bin/jobs.sh"\n)', "ref"),
  ("sh", 'python3 - <<\'PY\'\nimport mike_json\nPY', None),   # heredoc python -> import mike_json
  ("py", 'import subprocess\nsubprocess.run([str(ROOT / "bin" / "jobs.sh")])', "exec"),
  ("py", 'ok = "jobs.sh" in text', "none"),
  ("py", 'print("xem jobs.sh")', "none"),
]
bad = 0
for lang, src, want in cases:
    d = os.path.join(pm.MIKE, "bin")
    e = pm.edges_python_src(src, d) if lang == "py" else pm.edges_shell_src(src, d)
    if want is None:
        got_ok = any(os.path.basename(f) == "mike_json.py" and k == "import" for f, k in e)
    else:
        kinds = {k for f, k in e if f == J}
        got_ok = (not kinds) if want == "none" else (kinds == {want})
    if not got_ok:
        bad += 1
        print(f"FAIL parse-case [{lang}] {src!r}: mong {want}, được {[(pm.rel(f), k) for f, k in e]}")
print(f"parse-cases: {len(cases) - bad}/{len(cases)} PASS")
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

# (3) so thật
out="$(cd "$WC" && python3 "$GEN" --crontab "$TMP/crontab" --check "$TMP/committed.json" 2>&1)"; rc=$?
echo "$out"
[ "$rc" -eq 0 ] || fail=1

[ "$fail" -eq 0 ] && echo "PASS production_manifest_selfcheck" || echo "FAIL production_manifest_selfcheck"
exit "$fail"
