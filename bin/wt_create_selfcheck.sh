#!/usr/bin/env bash
# Selfcheck for bin/wt_create.sh in an isolated temp git repo.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT_CREATE="$HERE/wt_create.sh"
FAIL=0

ok() { echo "PASS $1"; }
bad() { echo "FAIL $1"; FAIL=1; }

SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT

REPO="$SB/repo"
mkdir -p "$REPO/bin" "$REPO/kb/archive" "$REPO/reports" "$REPO/agents/Taylor/research/dd_ABC"
echo "print('hi')" > "$REPO/bin/tool.py"
echo "# core" > "$REPO/kb/context.md"
echo "old" > "$REPO/kb/archive/old.md"
echo "rep" > "$REPO/reports/r.md"
echo "heavy" > "$REPO/agents/Taylor/research/dd_ABC/REPORT.md"

git -C "$REPO" init -q
git -C "$REPO" config user.email "test@example.com"
git -C "$REPO" config user.name "Test"
git -C "$REPO" add -A
git -C "$REPO" commit -q -m "init"

WT1="$SB/wt-small"
bash "$WT_CREATE" "$WT1" "session/small" --repo "$REPO" >/dev/null
[ -f "$WT1/bin/tool.py" ] && [ -f "$WT1/kb/context.md" ] && ok "1_core_checked_out" || bad "1_core_checked_out"
[ ! -e "$WT1/agents/Taylor/research/dd_ABC/REPORT.md" ] && [ ! -e "$WT1/reports/r.md" ] && [ ! -e "$WT1/kb/archive/old.md" ] \
  && ok "2_heavy_dirs_excluded" || bad "2_heavy_dirs_excluded"

WT2="$SB/wt-inc"
bash "$WT_CREATE" "$WT2" "session/inc" --repo "$REPO" --include "agents/Taylor/research/dd_ABC" >/dev/null
[ -f "$WT2/agents/Taylor/research/dd_ABC/REPORT.md" ] && [ ! -e "$WT2/reports/r.md" ] \
  && ok "3_include_subpath_works" || bad "3_include_subpath_works"

if [ "$FAIL" -eq 0 ]; then
  echo "ALL PASS"
else
  exit 1
fi
