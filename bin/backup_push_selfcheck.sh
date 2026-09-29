#!/usr/bin/env bash
# backup_push_selfcheck.sh — extract-and-test the staging/commit/push decision block of
# /home/trido/thanhdt/backup.sh against 5 constructed git states, in a throwaway sandbox
# (bare "remote" + clone under mktemp -d, works under `env -u TZ`).
#
# Why extract instead of duplicate: the block under test is sed-extracted from the REAL
# file at run time (extract_block below), not retyped here — if someone edits backup.sh's
# push logic without keeping the anchor lines in sync, this script breaks LOUDLY (grep -q
# markers below fail) instead of silently testing stale duplicated code.
#
# Built coord-2026-09-10 (arch-review Wags_20260909_012007 required_changes #5: "0 file
# selfcheck trong files_changed dù bin/ đã có 77 cái" — coding_guidelines §19/§23 mandate).
# Covers exactly the 5 cases the review named: (a) commit chưa push [-> push existing],
# (b) negative control [code cũ của chính lỗi 2026-09-09, tái hiện bug], (c) đã khớp,
# (d) phân nhánh, (e) remote không tới được.
set -uo pipefail
REAL=/home/trido/thanhdt/backup.sh
TD="$(mktemp -d)"
trap 'rm -rf "$TD"' EXIT
PASS=0
FAIL=0

extract_block() {
  awk '/^echo "==> Staging \+ committing…"$/{f=1} f' "$REAL"
}

# The pre-2026-09-09 code (shape-4 bug: "nothing to COMMIT" treated as "nothing to PUSH",
# see kb/incidents/2026-09/2026-09-09-backup-silent-failure-4th-shape-unpushed-commit.md).
# Kept here verbatim as the negative control — it must still exhibit the bug forever.
OLD_BUGGY_BLOCK='
echo "==> Staging + committing…"
git add -A
if git diff --cached --quiet; then
  echo "Nothing changed — already up to date."
  exit 0
fi
git commit -q -m "$MSG"
echo "==> Pushing to origin/main…"
git push -q origin main
echo "✅ Backup pushed: $(git rev-parse --short HEAD) — $MSG"
'

# --- sandbox factory -------------------------------------------------------
# Each setup_* creates: $TD/<name>/remote.git (bare) + $TD/<name>/work (clone, origin set).
new_repo() {
  local name="$1-$RANDOM"  # unique dir per call — same base name is reused (negative control)
  local bare="$TD/$name/remote.git" work="$TD/$name/work"
  mkdir -p "$bare" "$work"
  git init -q --bare -b main "$bare"
  git init -q -b main "$work"
  git -C "$work" config user.email selfcheck@test
  git -C "$work" config user.name selfcheck
  git -C "$work" remote add origin "$bare"
  echo v0 > "$work/f.txt"
  git -C "$work" add f.txt
  git -C "$work" commit -q -m "v0"
  git -C "$work" push -q origin main
  echo "$work"
}

setup_matched() {  # local HEAD == remote tip, clean tree
  new_repo matched
}

setup_behind_ancestor() {  # local has 1 extra commit remote doesn't have yet, tree clean
  local work; work="$(new_repo behind)"
  echo v1 > "$work/f.txt"
  git -C "$work" add f.txt
  git -C "$work" commit -q -m "v1 (chưa push)"
  echo "$work"
}

setup_matched_but_new_change() {  # local has real uncommitted change -> normal commit+push path
  local work; work="$(new_repo newchange)"
  echo v1 > "$work/f.txt"
  echo "$work"
}

setup_diverged() {  # remote gets a commit backup.sh never saw; local also has its own
  local work; work="$(new_repo diverged)"
  local bare; bare="$(git -C "$work" remote get-url origin)"
  local other; other="$(mktemp -d)"
  git clone -q "$bare" "$other"
  git -C "$other" checkout -q -B main origin/main
  git -C "$other" config user.email x@test; git -C "$other" config user.name x
  echo remote_side > "$other/f.txt"
  git -C "$other" add f.txt; git -C "$other" commit -q -m "remote-side change"
  git -C "$other" push -q origin main
  echo local_side > "$work/f.txt"
  git -C "$work" add f.txt
  git -C "$work" commit -q -m "local-side change"
  echo "$work"
}

setup_unreachable() {  # origin points at a path that doesn't exist
  local work; work="$(new_repo unreachable)"
  local bare; bare="$(git -C "$work" remote get-url origin)"
  git -C "$work" remote set-url origin "${bare}-DOES-NOT-EXIST"
  echo "$work"
}

# --- runner ------------------------------------------------------------
run_case() {
  local name="$1" work="$2" code="$3" expect_rc="$4" expect_grep="$5" expect_pushed="$6"
  local out rc before_remote after_remote
  before_remote="$(git -C "$work" ls-remote origin main 2>/dev/null | awk '{print $1}')"
  out="$(cd "$work" && MSG="selfcheck $name" bash -c "set -euo pipefail
$code" 2>&1)"
  rc=$?
  after_remote="$(git -C "$work" ls-remote origin main 2>/dev/null | awk '{print $1}')"
  local ok=1
  [ "$rc" = "$expect_rc" ] || ok=0
  grep -q "$expect_grep" <<<"$out" || ok=0
  if [ "$expect_pushed" = "yes" ]; then
    [ -n "$after_remote" ] && [ "$after_remote" = "$(git -C "$work" rev-parse HEAD)" ] || ok=0
  elif [ "$expect_pushed" = "no" ]; then
    [ "$before_remote" = "$after_remote" ] || ok=0
  fi
  if [ "$ok" = 1 ]; then
    echo "PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $name (rc=$rc expect=$expect_rc, pushed check=$expect_pushed)"
    echo "$out" | sed 's/^/    /'
    FAIL=$((FAIL + 1))
  fi
}

BLOCK="$(extract_block)"
if [ -z "$BLOCK" ]; then
  echo "FAIL: extraction anchor not found in $REAL — backup.sh's staging block was renamed, this selfcheck is stale" >&2
  exit 1
fi

# (c) đã khớp — local == remote, tree sạch -> "Nothing changed", rc0, không push (không có gì để push).
w="$(setup_matched)"
run_case "matched-no-op" "$w" "$BLOCK" 0 "Nothing changed" no

# (a) commit chưa push, tree sạch -> phải PUSH commit đã có, rc0.
w="$(setup_behind_ancestor)"
run_case "unpushed-commit-gets-pushed" "$w" "$BLOCK" 0 "existing commits" yes

# (e) thay đổi thật mới -> path commit+push bình thường, rc0.
w="$(setup_matched_but_new_change)"
run_case "new-change-commit-and-push" "$w" "$BLOCK" 0 "Backup pushed:" yes

# (d) phân nhánh -> KHÔNG tự push, cảnh báo, rc1.
w="$(setup_diverged)"
run_case "diverged-refuses-to-push" "$w" "$BLOCK" 1 "PHÂN NHÁNH" no

# (e) remote không tới được -> chẩn đoán rõ + rc1 (KHÔNG chết im lặng).
w="$(setup_unreachable)"
run_case "unreachable-remote-diagnoses" "$w" "$BLOCK" 1 "không đọc được origin/main" no

# (b) NEGATIVE CONTROL — code CŨ (trước fix 2026-09-09) trên đúng state "commit chưa push":
# phải VẪN reo báo "Nothing changed" (bug thật, không tự lành) để chứng minh bài test này
# thật sự phân biệt được code cũ/mới, không phải lúc nào cũng PASS.
w="$(setup_behind_ancestor)"
out="$(cd "$w" && MSG="negctrl" bash -c "set -euo pipefail
$OLD_BUGGY_BLOCK" 2>&1)"
after="$(git -C "$w" ls-remote origin main 2>/dev/null | awk '{print $1}')"
if grep -q "Nothing changed" <<<"$out" && [ "$after" != "$(git -C "$w" rev-parse HEAD)" ]; then
  echo "PASS: negative-control-old-code-still-has-shape4-bug"
  PASS=$((PASS + 1))
else
  echo "FAIL: negative-control-old-code-still-has-shape4-bug (bug đã tự lành hoặc test hỏng — điều tra lại)"
  echo "$out" | sed 's/^/    /'
  FAIL=$((FAIL + 1))
fi

echo
echo "backup_push_selfcheck: $PASS PASS, $FAIL FAIL"
[ "$FAIL" = 0 ]
