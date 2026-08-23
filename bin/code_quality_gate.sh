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
# commit — nếu không baseline sẽ lệch khỏi HEAD ngay sau lần ratchet đầu tiên. Bỏ qua bước này
# (không tự ghi/`git add`) nếu baseline.json đã có sửa đổi CHƯA STAGE từ trước khi gate chạy —
# tránh đụng cơ chế "stash unstaged rồi restore" của pre-commit (staged_files_only.py), có thể
# làm patch không apply lại được nếu ta ghi đè file đó giữa chừng.
#
# WORKTREE: repo mike/ có nhiều worktree (mike/agents/wt-<thread>/...), mỗi cái là 1 git
# checkout riêng với `git rev-parse --show-toplevel` khác nhau. Baseline-key PHẢI chuẩn hoá về
# dạng "mike/<path-trong-repo>" (repo-root-relative, gắn tiền tố "mike/" cố định) — KHÔNG được
# suy từ dirname(MIKE_ROOT) — để cùng 1 file logic (vd bin/dt5g_writer_watch.py) khớp đúng
# baseline dù commit từ checkout canonical hay từ 1 worktree bất kỳ (đã đo thật: suy WC_ROOT =
# dirname(MIKE_ROOT) cho ra "mike/agents" khi MIKE_ROOT là 1 worktree, làm rel-key sai hoàn
# toàn ⇒ hard-block file không sửa gì — xem arch-review job Wags_20260823_071251).
#
# Loại trừ (không chạy gate, không tính vào baseline): test_*.py ở root WorkingClaude (165
# file artifact R&D/backtest — coding_guidelines.md §23 hệ luận 2, KHÔNG phải test suite),
# exp_*.py/probe_*.py/stress_*.py (quy ước R&D mới), */agents/*/research/**, */archive/**,
# */wc_venv/** (wildcard theo BẤT KỲ tiền tố nào — canonical hay worktree) — đồng bộ với
# extend-exclude trong pyproject.toml. `--force-exclude` cũng được truyền cho ruff (trong
# code_quality_ruff_count.py) làm hàng rào thứ hai, vì ruff mặc định KHÔNG tự áp exclude cho
# path truyền tường minh trên command line.
#
# Escape hatch (cùng khuôn MIKE_COMMIT_GATE trong bin/repo_commit_gate.sh): env
# MIKE_CQ_GATE=warn hạ mọi BLOCK xuống cảnh báo không chặn; =off tắt hẳn gate.
set -uo pipefail

[ "${MIKE_CQ_GATE:-block}" = "off" ] && exit 0

# Repo root của CHECKOUT ĐANG CHẠY (canonical mike/ hoặc 1 worktree) — dùng git, không suy từ
# BASH_SOURCE, để đúng cả khi script này được copy/chạy từ nơi khác (vd sandbox selfcheck).
GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -n "$GIT_ROOT" ] && [ -f "$GIT_ROOT/kb/code_quality_baseline.json" ]; then
  MIKE_ROOT="$GIT_ROOT"
else
  MIKE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
COUNTER="$MIKE_ROOT/bin/code_quality_ruff_count.py"
BASELINE="$MIKE_ROOT/kb/code_quality_baseline.json"
PYEXE="${DNA_PYEXE:-/home/trido/thanhdt/wc_venv/bin/python}"

[ "$#" -eq 0 ] && exit 0

is_excluded() {
  # $1 = path repo-root-relative (KHÔNG có tiền tố "mike/"), vd "bin/foo.py" hoặc
  # "agents/Taylor/research/x.py".
  local rel="$1"
  local base
  base="$(basename "$rel")"
  case "$base" in
    test_*.py|exp_*.py|probe_*.py|stress_*.py) return 0 ;;
  esac
  case "$rel" in
    agents/*/research/*|*/agents/*/research/*) return 0 ;;
    archive/*|*/archive/*) return 0 ;;
    wc_venv/*|*/wc_venv/*) return 0 ;;
  esac
  return 1
}

# Chuẩn hoá mọi arg: abs path (tồn tại) + rel-trong-repo (loại trừ theo) + baseline-key
# ("mike/" + rel-trong-repo, luôn khớp baseline bất kể canonical hay worktree).
declare -a TARGETS=()
declare -A BASELINE_KEY_OF_ABS=()
for f in "$@"; do
  [ -f "$f" ] || continue
  abs="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
  case "$abs" in
    "$MIKE_ROOT"/*) rel_in_repo="${abs#"$MIKE_ROOT"/}" ;;
    *)
      echo "⚠️  code_quality_gate: $abs nằm ngoài MIKE_ROOT ($MIKE_ROOT) — bỏ qua, không tính baseline-key." >&2
      continue
      ;;
  esac
  if is_excluded "$rel_in_repo"; then
    echo "  ⏭️  $rel_in_repo — loại trừ (R&D/test artifact, xem pyproject.toml extend-exclude)"
    continue
  fi
  TARGETS+=("$abs")
  BASELINE_KEY_OF_ABS["$abs"]="mike/${rel_in_repo}"
done

[ "${#TARGETS[@]}" -eq 0 ] && exit 0

if [ ! -x "$PYEXE" ]; then
  echo "⚠️  code_quality_gate: python venv ($PYEXE, DNA_PYEXE override được) không tồn tại — bỏ qua gate, không chặn commit." >&2
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

# Map abs-path -> baseline-key TRƯỚC khi giao cho Python so baseline (Python không biết gì về
# worktree/rel-key, chỉ nhận đúng key cuối cùng).
declare -a KEYED_PAIRS=()
for abs in "${!BASELINE_KEY_OF_ABS[@]}"; do
  KEYED_PAIRS+=("${BASELINE_KEY_OF_ABS[$abs]}|$abs")
done

BLOCKED=0
result="$("$PYEXE" - "$BASELINE" "$counts_json" "${KEYED_PAIRS[@]}" <<'PYEOF'
import json, sys
baseline_path, counts_json = sys.argv[1], sys.argv[2]
keyed_pairs = sys.argv[3:]
try:
    with open(baseline_path) as fh:
        baseline = json.load(fh)
except FileNotFoundError:
    baseline = {"files": {}}
files_baseline = baseline.get("files", {})
counts_by_abs = json.loads(counts_json)
blocked = []
to_update = {}
for pair in keyed_pairs:
    key, abs_path = pair.split("|", 1)
    new_n = counts_by_abs.get(abs_path, 0)
    old_n = files_baseline.get(key, 0)
    to_update[key] = new_n
    if new_n > old_n:
        blocked.append((key, old_n, new_n))
for key, old_n, new_n in blocked:
    print(f"BLOCK|{key}|{old_n}|{new_n}")
for key, new_n in to_update.items():
    print(f"UPDATE|{key}|{new_n}")
PYEOF
)"

declare -a BLOCK_LINES=()
while IFS='|' read -r kind rel a b; do
  [ -z "${kind:-}" ] && continue
  if [ "$kind" = "BLOCK" ]; then
    BLOCKED=$((BLOCKED + 1))
    BLOCK_LINES+=("$rel|$a|$b")
    echo "  🔴 $rel: ruff lỗi $b (baseline $a) — TĂNG so với baseline [HARD-BLOCK] (code_quality_gate.sh)"
  fi
done <<< "$result"

if [ "$BLOCKED" -gt 0 ] && [ "${MIKE_CQ_GATE:-block}" = "block" ]; then
  echo
  echo "code_quality_gate: $BLOCKED file tăng lỗi ruff (F/E9/B006/B008) so với baseline."
  echo "  Xem chi tiết:  /home/trido/thanhdt/wc_venv/bin/ruff check <file>"
  echo "  Ratchet: nợ cũ không bắt sửa ngay, chỉ không được tăng thêm."
  echo "  Escape hatch (nếu chắc chắn false-block): MIKE_CQ_GATE=warn git commit ..."
  exit 1
elif [ "$BLOCKED" -gt 0 ]; then
  echo
  echo "⚠️  code_quality_gate: $BLOCKED file tăng lỗi ruff (downgraded — MIKE_CQ_GATE=warn), commit vẫn qua."
  echo "  Baseline SẼ được nâng lên số lỗi mới (ratchet coi nợ mới này là hợp lệ từ nay):"
  for line in "${BLOCK_LINES[@]}"; do
    IFS='|' read -r brel ba bb <<< "$line"
    echo "    $brel: baseline $ba → $bb"
  done
fi

# Bỏ qua auto-update baseline nếu file baseline đã có sửa đổi CHƯA STAGE từ trước (vd vừa chạy
# tay code_quality_baseline_build.py) — ghi đè giữa chừng có thể đụng cơ chế stash-restore của
# pre-commit (staged_files_only.py) và làm rách patch.
if git -C "$MIKE_ROOT" diff --name-only -- "$BASELINE" 2>/dev/null | grep -q .; then
  echo "⚠️  code_quality_gate: kb/code_quality_baseline.json có sửa đổi chưa stage — bỏ qua auto-update lần này." >&2
  exit 0
fi

# Tất cả pass — tự cập nhật baseline (tiến, không lùi), ghi ATOMIC (tmp + mv) rồi stage lại
# cùng commit.
TMP_BASELINE="${BASELINE}.tmp.$$"
status_line="$("$PYEXE" - "$BASELINE" "$TMP_BASELINE" "$result" <<'PYEOF'
import json, sys
baseline_path, tmp_path, result = sys.argv[1], sys.argv[2], sys.argv[3]
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
    key, new_n = parts[1], int(parts[2])
    if files_baseline.get(key, 0) != new_n:
        files_baseline[key] = new_n
        changed = True
if changed:
    with open(tmp_path, "w") as fh:
        json.dump(baseline, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("CHANGED")
else:
    print("UNCHANGED")
PYEOF
)"
if [ "$status_line" = "CHANGED" ] && [ -f "$TMP_BASELINE" ]; then
  mv -f "$TMP_BASELINE" "$BASELINE"
  # BASELINE nằm dưới kb/ của CHÍNH repo đang chạy (canonical hoặc worktree) — `git -C
  # "$MIKE_ROOT" add` luôn đúng repo vì MIKE_ROOT giờ tính bằng git rev-parse, không phải suy
  # diễn đường dẫn tĩnh.
  git -C "$MIKE_ROOT" add "$BASELINE" || echo "⚠️  code_quality_gate: git add baseline thất bại — baseline đã ghi nhưng CHƯA stage, commit có thể lệch khỏi HEAD." >&2
else
  rm -f "$TMP_BASELINE"
fi

exit 0
