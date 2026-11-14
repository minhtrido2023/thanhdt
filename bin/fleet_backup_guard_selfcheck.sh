#!/usr/bin/env bash
# Selfcheck cho unstage_oversized() trong fleet_backup.sh (extract-and-test; sandbox mktemp -d).
# Chạy được dưới `env -u TZ`. Ca: new / modified-tracked / rename >limit, tên có dấu cách, file nhỏ.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/fleet_backup.sh"
fn="$(awk '/^unstage_oversized\(\) \{/{p=1} p{print} p&&/^\}/{exit}' "$SRC")"
[ -n "$fn" ] || { echo "FAIL không extract được unstage_oversized từ $SRC"; exit 1; }
eval "$fn"
export FLEET_BACKUP_MAX_BYTES=1000   # nhỏ để test nhanh; logic y hệt 95MB
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
git -C "$T" init -q && git -C "$T" config user.email t@t && git -C "$T" config user.name t
head -c 100 /dev/zero >"$T/tracked_small.bin"; head -c 100 /dev/zero >"$T/orig_big.bin"
git -C "$T" add -A && git -C "$T" commit -q -m init
# tracked-modified GREW past limit, new big, renamed big, name with spaces, small new
head -c 5000 /dev/zero >"$T/tracked_small.bin"
head -c 5000 /dev/zero >"$T/new_big.bin"
head -c 5000 /dev/zero >"$T/has space big.bin"
head -c 50 /dev/zero >"$T/small_new.txt"
git -C "$T" mv orig_big.bin renamed_big.bin && head -c 5000 /dev/zero >"$T/renamed_big.bin"
git -C "$T" add -A
out="$(unstage_oversized "$T")"
pass=0; fail=0
ck(){ if eval "$2"; then pass=$((pass+1)); echo "  ok   $1"; else fail=$((fail+1)); echo "  FAIL $1"; fi; }
staged="$(git -C "$T" diff --cached --name-status --no-renames)"
ck "new >limit unstaged"           '! grep -q "new_big.bin" <<<"$staged"'
ck "name with spaces unstaged"     '! grep -q "has space big.bin" <<<"$staged"'
ck "renamed big unstaged (A seen via --no-renames)" '! grep -q "renamed_big.bin" <<<"$staged"'
ck "tracked-modified NOT staged as deletion" '! grep -qE "^D\s+tracked_small.bin" <<<"$staged"'
ck "tracked-modified stays at HEAD version in index" 'git -C "$T" diff --cached --quiet -- tracked_small.bin'
ck "tracked-modified file still on disk"  '[ "$(stat -c %s "$T/tracked_small.bin")" = 5000 ]'
ck "big files still on disk"       '[ -f "$T/new_big.bin" ] && [ -f "$T/has space big.bin" ] && [ -f "$T/renamed_big.bin" ]'
ck "small file kept staged"        'grep -q "small_new.txt" <<<"$staged"'
ck "WARN lines emitted (>=3)"      '[ "$(grep -c "WARN: unstaged" <<<"$out")" -ge 3 ]'
# classifier của push stderr: tồn tại trong fleet_backup.sh
ck "GH001 classifier present"      'grep -q "GH001|large file" "$SRC"'
ck "auth classifier present"       'grep -q "authentication|401|403" "$SRC"'
echo; echo "$pass/$((pass+fail)) PASS"; [ "$fail" = 0 ]
