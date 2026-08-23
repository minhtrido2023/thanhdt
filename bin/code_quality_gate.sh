#!/usr/bin/env bash
# code_quality_gate.sh <file.py> [...]
#
# Pre-commit gate — Tầng 1 của kế hoạch code-quality review 3 tầng (user duyệt 2026-08-23,
# kb/projects/code-quality-review-plan-20260823.md §3). Chạy ruff (rule set HẸP — chỉ F
# (pyflakes: import thừa, tên chưa định nghĩa, biến không dùng…), E9 (lỗi cú pháp), B006/B008
# (mutable default argument); cấu hình ở WorkingClaude/pyproject.toml, KHÔNG bật style) trên
# các file .py THAY ĐỔI trong commit này, so với kb/code_quality_baseline.json của CHÍNH file
# đó.
#
# RATCHET, không phải chặn tuyệt đối: chỉ BLOCK nếu số lỗi TĂNG so với baseline của file đó.
# File mới (không có trong baseline) → baseline ngầm định = 0. Nợ cũ không bị bắt sửa ngay —
# chỉ không được phép tăng thêm (đúng "enforcement policy" đã có trong coding_guidelines,
# không phải backlog cleanup ép buộc ngày 1 — cùng lý do bin/shellcheck_gate.sh curated thay
# vì block-on-any-finding).
#
# Sau khi TẤT CẢ file trong commit pass, script TỰ CẬP NHẬT baseline cho các file đó về số lỗi
# MỚI (tiến, không lùi) và `git add` lại kb/code_quality_baseline.json để nó nằm trong CÙNG
# commit — nếu không baseline sẽ lệch khỏi HEAD ngay sau lần ratchet đầu tiên.
#
# Loại trừ (không chạy gate, không tính vào baseline): test_*.py ở root WorkingClaude (165
# file artifact R&D/backtest — coding_guidelines.md §23 hệ luận 2, KHÔNG phải test suite),
# exp_*.py/probe_*.py/stress_*.py (quy ước R&D mới), agents/*/research/**, archive/**,
# wc_venv/** — đồng bộ với extend-exclude trong pyproject.toml.
set -uo pipefail

MIKE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$MIKE_ROOT/.." && pwd)"
COUNTER="$MIKE_ROOT/bin/code_quality_ruff_count.py"
BASELINE="$MIKE_ROOT/kb/code_quality_baseline.json"
PYEXE="/home/trido/thanhdt/wc_venv/bin/python"

[ "$#" -eq 0 ] && exit 0

is_excluded() {
  local rel="$1"
  local base
  base="$(basename "$rel")"
  case "$base" in
    test_*.py|exp_*.py|probe_*.py|stress_*.py) return 0 ;;
  esac
  case "$rel" in
    agents/*/research/*|archive/*|wc_venv/*) return 0 ;;
  esac
  return 1
}

# Chuẩn hoá mọi arg thành đường dẫn tương đối WC_ROOT + lọc file tồn tại (đã bỏ file bị xoá).
declare -a TARGETS=()
declare -A REL_OF_ABS=()
for f in "$@"; do
  [ -f "$f" ] || continue
  abs="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
  rel="${abs#"$WC_ROOT"/}"
  if is_excluded "$rel"; then
    echo "  ⏭️  $rel — loại trừ (R&D/test artifact, xem pyproject.toml extend-exclude)"
    continue
  fi
  TARGETS+=("$abs")
  REL_OF_ABS["$abs"]="$rel"
done

[ "${#TARGETS[@]}" -eq 0 ] && exit 0

if [ ! -x "$PYEXE" ]; then
  echo "⚠️  code_quality_gate: DNA_PYEXE ($PYEXE) không tồn tại — bỏ qua gate, không chặn commit." >&2
  exit 0
fi

counts_json="$("$PYEXE" "$COUNTER" "${TARGETS[@]}" 2>/tmp/code_quality_gate_err.$$)"
rc=$?
if [ "$rc" -ne 0 ]; then
  echo "⚠️  code_quality_gate: ruff lỗi ($(cat /tmp/code_quality_gate_err.$$)) — bỏ qua gate, không chặn commit." >&2
  rm -f /tmp/code_quality_gate_err.$$
  exit 0
fi
rm -f /tmp/code_quality_gate_err.$$

BLOCKED=0
result="$("$PYEXE" - "$BASELINE" "$counts_json" <<'PYEOF'
import json, sys
baseline_path, counts_json = sys.argv[1], sys.argv[2]
try:
    with open(baseline_path) as fh:
        baseline = json.load(fh)
except FileNotFoundError:
    baseline = {"files": {}}
files_baseline = baseline.get("files", {})
counts = json.loads(counts_json)
blocked = []
to_update = {}
for rel, new_n in counts.items():
    old_n = files_baseline.get(rel, 0)
    to_update[rel] = new_n
    if new_n > old_n:
        blocked.append((rel, old_n, new_n))
for rel, old_n, new_n in blocked:
    print(f"BLOCK|{rel}|{old_n}|{new_n}")
for rel, new_n in to_update.items():
    print(f"UPDATE|{rel}|{new_n}")
PYEOF
)"

while IFS='|' read -r kind rel a b; do
  [ -z "${kind:-}" ] && continue
  if [ "$kind" = "BLOCK" ]; then
    BLOCKED=$((BLOCKED + 1))
    echo "  🔴 $rel: ruff lỗi $b (baseline $a) — TĂNG so với baseline [HARD-BLOCK] (code_quality_gate.sh)"
  fi
done <<< "$result"

if [ "$BLOCKED" -gt 0 ]; then
  echo
  echo "code_quality_gate: $BLOCKED file tăng lỗi ruff (F/E9/B006/B008) so với baseline."
  echo "  Xem chi tiết:  /home/trido/thanhdt/wc_venv/bin/ruff check <file>"
  echo "  Ratchet: nợ cũ không bắt sửa ngay, chỉ không được tăng thêm."
  exit 1
fi

# Tất cả pass — tự cập nhật baseline (tiến, không lùi) và stage lại cùng commit.
"$PYEXE" - "$BASELINE" "$result" <<'PYEOF'
import json, sys
baseline_path, result = sys.argv[1], sys.argv[2]
try:
    with open(baseline_path) as fh:
        baseline = json.load(fh)
except FileNotFoundError:
    baseline = {"files": {}}
files_baseline = baseline.setdefault("files", {})
changed = False
for line in result.splitlines():
    parts = line.split("|")
    if parts[0] != "UPDATE":
        continue
    rel, new_n = parts[1], int(parts[2])
    if files_baseline.get(rel, 0) != new_n:
        files_baseline[rel] = new_n
        changed = True
if changed:
    with open(baseline_path, "w") as fh:
        json.dump(baseline, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("baseline updated", file=sys.stderr)
PYEOF

# BASELINE nằm dưới mike/kb/ — repo git của nó là MIKE_ROOT (mike/ là repo lồng, tách khỏi
# WorkingClaude repo — CLAUDE.md § .gitignore ẩn mike/ khỏi repo WorkingClaude). `git -C
# "$WC_ROOT"` ở đây sẽ SAI repo và add() sẽ no-op im lặng.
if git -C "$MIKE_ROOT" diff --name-only -- "$BASELINE" 2>/dev/null | grep -q .; then
  git -C "$MIKE_ROOT" add "$BASELINE" 2>/dev/null || true
fi

exit 0
