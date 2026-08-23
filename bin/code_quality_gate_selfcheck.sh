#!/usr/bin/env bash
# code_quality_gate_selfcheck.sh — self-check cho bin/code_quality_gate.sh (Tầng 1 code-quality
# review, kb/projects/code-quality-review-plan-20260823.md §3).
#
# CÁCH TEST: sandbox mô phỏng cây thư mục WC_ROOT thật (wc/pyproject.toml + wc/mike/bin/ +
# wc/mike/kb/) rồi COPY NGUYÊN VĂN 2 script thật vào (code_quality_gate.sh +
# code_quality_ruff_count.py) — sửa gate mà quên sửa test thì test chạy trên đúng code mới,
# không trôi khỏi nhau (cùng kỷ luật dt5g_publisher_gate_selfcheck.sh). ruff THẬT chạy trong
# sandbox (không mock logic lint) — chỉ path/baseline là giả.
#
# 3 bất biến bắt buộc (theo dispatch job Wags_20260823_071251):
#   (a) file có baseline=0, thêm F821 mới → gate PHẢI CHẶN (exit non-zero)
#   (b) file sạch, không lỗi mới → gate PHẢI CHO QUA (exit 0)
#   (c) file trong danh sách loại trừ (test_*.py) có F821 → gate PHẢI BỎ QUA (exit 0)
#
# Usage: bash mike/bin/code_quality_gate_selfcheck.sh   (exit 0 = tất cả ca PASS)
set -uo pipefail

REAL_MIKE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REAL_WC="$(cd "$REAL_MIKE/.." && pwd)"

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
WC="$SANDBOX/wc"
mkdir -p "$WC/mike/bin" "$WC/mike/kb"
cp "$REAL_WC/pyproject.toml" "$WC/pyproject.toml"
cp "$REAL_MIKE/bin/code_quality_gate.sh" "$WC/mike/bin/code_quality_gate.sh"
cp "$REAL_MIKE/bin/code_quality_ruff_count.py" "$WC/mike/bin/code_quality_ruff_count.py"
chmod +x "$WC/mike/bin/code_quality_gate.sh" "$WC/mike/bin/code_quality_ruff_count.py"

FAILS=0

write_baseline() {
  # write_baseline <file_rel>=<count> [<file_rel>=<count> ...]
  local py='import json,sys
pairs = sys.argv[1:]
files = {}
for p in pairs:
    rel, n = p.rsplit("=", 1)
    files[rel] = int(n)
print(json.dumps({"files": files}))'
  /usr/bin/env python3 -c "$py" "$@" > "$WC/mike/kb/code_quality_baseline.json"
}

run_case() {
  # run_case <name> <exp_exit> <files...>
  local name="$1" exp_exit="$2"; shift 2
  local out rc
  out="$(cd "$WC" && bash mike/bin/code_quality_gate.sh "$@" 2>&1)"
  rc=$?
  if [ "$rc" = "$exp_exit" ]; then
    printf 'PASS  %-70s exit=%s\n' "$name" "$rc"
  else
    printf 'FAIL  %-70s got exit=%s, muốn exit=%s\n' "$name" "$rc" "$exp_exit"
    sed 's/^/        | /' <<<"$out"
    FAILS=$((FAILS + 1))
  fi
}

echo "--- (a) baseline=0, thêm F821 mới -> PHẢI CHẶN ---"
write_baseline "mike/bin/foo.py=0"
cat > "$WC/mike/bin/foo.py" <<'PYEOF'
def broken():
    return undefined_name_here + 1
PYEOF
run_case "F821 mới trên file baseline=0" 1 "$WC/mike/bin/foo.py"

echo
echo "--- (b) file sạch, không lỗi mới -> PHẢI CHO QUA ---"
write_baseline "mike/bin/bar.py=0"
cat > "$WC/mike/bin/bar.py" <<'PYEOF'
def clean(x):
    return x + 1
PYEOF
run_case "file sạch" 0 "$WC/mike/bin/bar.py"

echo
echo "--- (c) file loại trừ (test_*.py) có F821 -> PHẢI BỎ QUA ---"
write_baseline "test_something.py=0"
cat > "$WC/test_something.py" <<'PYEOF'
def broken():
    return undefined_name_here + 1
PYEOF
run_case "test_*.py bị loại trừ dù có F821" 0 "$WC/test_something.py"

echo
echo "--- (d, phụ) ratchet: lỗi cũ đã có trong baseline, không TĂNG -> PHẢI CHO QUA ---"
write_baseline "mike/bin/foo.py=1"
run_case "F821 đã có sẵn trong baseline, không tăng" 0 "$WC/mike/bin/foo.py"
baseline_after="$(cat "$WC/mike/kb/code_quality_baseline.json")"
if grep -q '"mike/bin/foo.py": 1' <<<"$baseline_after"; then
  echo "PASS  baseline giữ nguyên 1 sau ca (d) (không lùi, không tăng oan)"
else
  echo "FAIL  baseline SAI sau ca (d): $baseline_after"
  FAILS=$((FAILS + 1))
fi

echo
echo "--- (e, phụ) sau ca (b) PASS, baseline tự cập nhật + được git-add (nếu là repo git) ---"
git -C "$WC" init -q 2>/dev/null || true
git -C "$WC" add -A 2>/dev/null || true
write_baseline "mike/bin/qux.py=0"
cat > "$WC/mike/bin/qux.py" <<'PYEOF'
def clean2(x):
    return x + 2
PYEOF
run_case "clean file, baseline update path (git repo present)" 0 "$WC/mike/bin/qux.py"

echo
if [ "$FAILS" -eq 0 ]; then
  echo "=== SELFCHECK OK — 5/5 ca đúng ==="
  exit 0
fi
echo "=== SELFCHECK FAIL — $FAILS ca sai ==="
exit 1
