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
# +4 ca phụ thêm sau arch-review (job Wags_20260823_071251):
#   (e) đường auto-update+git-add PHẢI thực sự chạy nhánh đó (không rơi vào nhánh "baseline
#       dirty ⇒ bỏ qua") — round 2.
#   (f) commit từ 1 git worktree lồng PHẢI ra baseline-key "mike/<rel>", không lẫn tên thư mục
#       worktree — round 2.
#   (g) MIKE_CQ_GATE=warn PHẢI in tường minh baseline nâng lên (không chỉ âm thầm ghi JSON) —
#       round 3.
#   (h) file NGOÀI MIKE_ROOT PHẢI bị bỏ qua có cảnh báo, không sinh baseline-key rác — round 3.
#
# HERMETIC: script này tự `git init`/`commit`/`worktree add` trong SANDBOX — `git -C <dir>` đổi
# cwd nhưng KHÔNG override GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE nếu biến đó đã có sẵn trong môi
# trường gọi (vd tự chạy selfcheck NÀY từ bên trong một git hook khác đang set GIT_DIR). Nếu
# không unset, mọi lệnh git bên dưới có thể âm thầm thao tác lên REPO THẬT của caller thay vì
# sandbox — bug thật bắt được ở arch-review round 3 (tái hiện: GIT_DIR=<repo lạ>/.git bash
# code_quality_gate_selfcheck.sh ghi 2 commit thật vào repo lạ mà vẫn in "7/7 ca đúng").
#
# Usage: bash mike/bin/code_quality_gate_selfcheck.sh   (exit 0 = tất cả ca PASS)
set -uo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY \
      GIT_ALTERNATE_OBJECT_DIRECTORIES

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
echo "--- (e, phụ) sau ca (b) PASS, baseline tự cập nhật + được git-add THẬT (nhánh update, không phải nhánh bỏ qua) ---"
# git repo gốc là mike/ (không phải WC) — GIT_ROOT/kb/code_quality_baseline.json phải khớp để
# gate dùng đúng nhánh MIKE_ROOT=GIT_ROOT (giống production: mike/ là repo lồng riêng).
git -C "$WC/mike" init -q
git -C "$WC/mike" config user.email "t@t.local"
git -C "$WC/mike" config user.name "t"
# qux.py=2 (KHÁC số lỗi thật của file clean bên dưới, 0) — cố ý, để buộc gate phải đi qua
# nhánh "changed=True" (files_baseline.get(key,0) != new_n). Nếu seed = 0 y hệt thực tế thì
# 0 != 0 là False, không CHANGED, không git-add — test sẽ xanh mà chưa hề thử nhánh update
# (bug thật của round trước: seed=0 trùng thực tế 0, nên "PASS" của ca (e) không chứng minh
# được gì).
# dt5g_probe.py=5 seed sẵn cho ca (f) — file thật chỉ được tạo SAU trong worktree.
write_baseline "mike/bin/qux.py=2" "mike/bin/dt5g_probe.py=5"
cat > "$WC/mike/bin/qux.py" <<'PYEOF'
def clean2(x):
    return x + 2
PYEOF
# Baseline PHẢI được commit (không phải chỉ tồn tại trên disk) trước khi tạo file mới, để nó
# KHÔNG dirty lúc gate chạy — nếu không gate sẽ rẽ vào nhánh "bỏ qua auto-update" và ca này
# xanh giả (bug thật bị bỏ sót ở round 2: git add -A chạy TRƯỚC write_baseline nên baseline
# luôn dirty, chưa từng thật sự chạm nhánh update+git-add).
git -C "$WC/mike" add -A
git -C "$WC/mike" commit -q -m "seed baseline"
run_case "clean file, baseline update path (git repo present)" 0 "$WC/mike/bin/qux.py"
baseline_after_e="$(cat "$WC/mike/kb/code_quality_baseline.json")"
staged_e="$(git -C "$WC/mike" diff --cached --name-only -- kb/code_quality_baseline.json)"
if grep -q '"mike/bin/qux.py": 0' <<<"$baseline_after_e" && [ -n "$staged_e" ]; then
  echo "PASS  baseline hạ qux.py 2->0 (nhánh update thật sự chạy) VÀ đã được git add"
else
  echo "FAIL  ca (e) không đi qua nhánh update+git-add: baseline=$baseline_after_e staged='$staged_e'"
  FAILS=$((FAILS + 1))
fi
git -C "$WC/mike" commit -q -m "ratchet qux.py" --allow-empty

echo
echo "--- (f, phụ) commit từ 1 git worktree lồng -> baseline-key PHẢI ra 'mike/<rel>', không lẫn tên worktree ---"
WT="$WC/mike-wt"
git -C "$WC/mike" worktree add -q "$WT" -b wt-selfcheck-branch >/dev/null 2>&1
if [ -d "$WT" ]; then
  cat > "$WT/bin/dt5g_probe.py" <<'PYEOF'
def clean3(x):
    return x + 3
PYEOF
  out_f="$(cd "$WT" && bash bin/code_quality_gate.sh "$WT/bin/dt5g_probe.py" 2>&1)"
  rc_f=$?
  # MIKE_ROOT của gate = GIT_ROOT của checkout ĐANG chạy (ở đây là $WT, vì worktree có kb/
  # baseline riêng, tách khỏi canonical cho tới khi merge) — baseline cập nhật PHẢI nằm ở
  # $WT/kb/, không phải $WC/mike/kb/. Bài học round-2 review: assert nhầm file canonical sẽ
  # luôn thấy "không đổi" và không bắt được bug key sai.
  baseline_after_f="$(cat "$WT/kb/code_quality_baseline.json")"
  if [ "$rc_f" -eq 0 ] && grep -q '"mike/bin/dt5g_probe.py": 0' <<<"$baseline_after_f" \
     && ! grep -q 'mike-wt' <<<"$baseline_after_f"; then
    echo "PASS  commit từ worktree ra đúng key mike/bin/dt5g_probe.py=0 (seed 5, không lẫn 'mike-wt')"
  else
    printf 'FAIL  %-70s got exit=%s\n' "worktree baseline-key" "$rc_f"
    sed 's/^/        | /' <<<"$out_f"
    echo "        | baseline sau: $baseline_after_f"
    FAILS=$((FAILS + 1))
  fi
  git -C "$WC/mike" worktree remove -f "$WT" >/dev/null 2>&1 || true
else
  echo "FAIL  không tạo được worktree test (git worktree add lỗi) — môi trường thiếu, không phải bug gate"
  FAILS=$((FAILS + 1))
fi

echo
echo "--- (g, phụ) MIKE_CQ_GATE=warn: PHẢI in tường minh baseline nâng lên, không chỉ âm thầm ghi JSON ---"
write_baseline "mike/bin/warn_target.py=0"
cat > "$WC/mike/bin/warn_target.py" <<'PYEOF'
def broken_warn():
    return undefined_name_in_warn_case + 1
PYEOF
# $WC/mike đã là git repo thật từ ca (e)/(f) — write_baseline vừa rồi ghi đè baseline.json làm
# nó DIRTY so với commit gần nhất, mà gate.sh có nhánh "baseline dirty ⇒ bỏ qua auto-update"
# (đúng thiết kế, tránh đụng cơ chế stash của pre-commit) — phải commit lại baseline SẠCH
# trước, nếu không ca này sẽ rơi nhầm vào nhánh dirty-skip và never thấy update thật.
git -C "$WC/mike" add -A
git -C "$WC/mike" commit -q -m "seed warn case"
out_g="$(cd "$WC" && MIKE_CQ_GATE=warn bash mike/bin/code_quality_gate.sh "$WC/mike/bin/warn_target.py" 2>&1)"
rc_g=$?
baseline_after_g="$(cat "$WC/mike/kb/code_quality_baseline.json")"
if [ "$rc_g" -eq 0 ] \
   && grep -q 'mike/bin/warn_target.py: baseline 0 → 1' <<<"$out_g" \
   && grep -q '"mike/bin/warn_target.py": 1' <<<"$baseline_after_g"; then
  echo "PASS  warn mode: exit 0, in rõ 'baseline 0 → 1', baseline JSON cũng nâng lên 1"
else
  printf 'FAIL  %-70s got exit=%s\n' "MIKE_CQ_GATE=warn in rõ + nâng baseline" "$rc_g"
  sed 's/^/        | /' <<<"$out_g"
  echo "        | baseline sau: $baseline_after_g"
  FAILS=$((FAILS + 1))
fi

echo
echo "--- (h, phụ) file NGOÀI MIKE_ROOT -> PHẢI bỏ qua có cảnh báo, KHÔNG sinh baseline-key rác ---"
OUTSIDE_DIR="$SANDBOX/outside"
mkdir -p "$OUTSIDE_DIR"
cat > "$OUTSIDE_DIR/rogue.py" <<'PYEOF'
def rogue():
    return undefined_name_outside_root + 1
PYEOF
baseline_before_h="$(cat "$WC/mike/kb/code_quality_baseline.json")"
out_h="$(cd "$WC" && bash mike/bin/code_quality_gate.sh "$OUTSIDE_DIR/rogue.py" 2>&1)"
rc_h=$?
baseline_after_h="$(cat "$WC/mike/kb/code_quality_baseline.json")"
if [ "$rc_h" -eq 0 ] \
   && grep -q 'nằm ngoài MIKE_ROOT' <<<"$out_h" \
   && [ "$baseline_before_h" = "$baseline_after_h" ]; then
  echo "PASS  file ngoài MIKE_ROOT: exit 0, có cảnh báo, baseline không đổi (không sinh key rác)"
else
  printf 'FAIL  %-70s got exit=%s\n' "file ngoài MIKE_ROOT bị bỏ qua an toàn" "$rc_h"
  sed 's/^/        | /' <<<"$out_h"
  FAILS=$((FAILS + 1))
fi

echo
if [ "$FAILS" -eq 0 ]; then
  echo "=== SELFCHECK OK — 9/9 ca đúng ==="
  exit 0
fi
echo "=== SELFCHECK FAIL — $FAILS ca sai ==="
exit 1
