#!/usr/bin/env bash
# Selfcheck khối MORNING MODE của daily_refresh_v34b_linux.sh: trích bằng marker BOUNDED (MORNING-BEGIN/END)
# + dòng `if` bao ngoài rồi chạy trong harness. Phủ: bật -> TODAY_ICT=phiên; tắt -> giữ nguyên;
# helper hỏng -> die kèm output thật. Chạy dưới env -u TZ (§16).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; SRC="${SRC_OVERRIDE:-$HERE/daily_refresh_v34b_linux.sh}"
MIKE_HELPER="${MIKE_HELPER:-/home/trido/thanhdt/WorkingClaude/mike/bin/expected_session.py}"
fail=0; chk() { if [ "$2" = "$3" ]; then echo "OK   $1"; else echo "FAIL $1: got '$2' want '$3'"; fail=1; fi; }
b=$(grep -n 'MORNING-BEGIN' "$SRC" | head -1 | cut -d: -f1); e=$(grep -n 'MORNING-END' "$SRC" | head -1 | cut -d: -f1)
[ -n "$b" ] && [ -n "$e" ] && [ "$e" -gt "$b" ] && [ $((e-b)) -lt 15 ] || { echo "FAIL không trích được khối MORNING (marker đổi/không bounded)"; exit 1; }
BLK="$(sed -n "$((b-1)),$((e+1))p" "$SRC")"   # gồm dòng `if [ ... MIKE_MORNING_RUN ... ]` và `fi`
head -1 <<<"$BLK" | grep -q 'MIKE_MORNING_RUN' || { echo "FAIL dòng if bao ngoài không phải MIKE_MORNING_RUN"; exit 1; }
SB="$(mktemp -d)"; trap 'rm -rf "$SB"' EXIT; mkdir -p "$SB/mike/bin"; ln -s "$MIKE_HELPER" "$SB/mike/bin/expected_session.py"
run() { # $1 morning $2 now $3 helper-broken(0/1)
  [ "$3" = 1 ] && { rm -f "$SB/mike/bin/expected_session.py"; printf 'import sys; sys.stderr.write("ImportError boom"); sys.exit(1)\n' > "$SB/mike/bin/expected_session.py"; }
  env -u TZ MIKE_NOW_ICT="$2" MIKE_MORNING_RUN="$1" WORKDIR_8L="${WC_ROOT:-/home/trido/thanhdt/WorkingClaude}" SBX="$SB" bash -c '
die() { echo "DIE: $*"; exit 1; }
WORKDIR_8L_HELPER="$SBX/mike/bin/expected_session.py"
TODAY_ICT=CAL
'"$(sed "s#\$WORKDIR_8L/mike/bin/expected_session.py#\$WORKDIR_8L_HELPER#" <<<"$BLK")"'
echo "TODAY_ICT=$TODAY_ICT"' 2>&1 | tail -1; [ "$3" = 1 ] && ln -sf "$MIKE_HELPER" "$SB/mike/bin/expected_session.py"; }
chk "bật, 07:30 T5 -> TODAY_ICT=phiên 10-14" "$(run 1 2026-10-15T07:30:00 0)" "TODAY_ICT=2026-10-14"
chk "bật, 18:30 T4 -> TODAY_ICT=10-14 (hôm nay)" "$(run 1 2026-10-14T18:30:00 0)" "TODAY_ICT=2026-10-14"
chk "tắt -> TODAY_ICT giữ nguyên" "$(run 0 2026-10-15T07:30:00 0)" "TODAY_ICT=CAL"
chk "helper hỏng -> DIE kèm output thật" "$(run 1 2026-10-15T07:30:00 1 | grep -c 'DIE:.*ImportError boom')" "1"
[ "$fail" = 0 ] && echo "selfcheck: PASS" || { echo "selfcheck: FAIL"; exit 1; }
