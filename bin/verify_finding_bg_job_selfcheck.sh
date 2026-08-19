#!/usr/bin/env bash
# verify_finding_bg_job_selfcheck.sh — kiểm tra vòng đời job record của verify_finding.sh
# --bg (F3, 2026-08-19), KHÔNG gọi claude thật (tốn tiền/chậm) — chỉ tái tạo đúng chuỗi
# job-set mà run_and_record thực hiện, vì đó là chỗ 2 bug thật đã xảy ra và được sửa:
#
#   BUG 1 (đã sửa): stamp pid=$BASHPID từ BÊN TRONG subshell nền bị mike_json.py's
#   anti-lying guard từ chối (exit 3), vì đến lúc đó script top-level đã thoát và subshell
#   đã bị reparent — ancestry chain tới dispatcher_pid đứt. Sửa: stamp pid NGAY SAU khi
#   background, từ top-level script (còn sống, ancestry còn nguyên).
#   BUG 2 (đã sửa): record tạo không có `deadline` -> job-reap không bao giờ đóng được nếu
#   worker chết giữa chừng -> record kẹt running vĩnh viễn -> khoá cả claim-reply (F1) lẫn
#   trip circuit breaker (F2) mãi mãi.
#
# Chạy trên sandbox riêng (mktemp -d), KHÔNG đụng bus/jobs thật, KHÔNG gọi claude CLI.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT
JOBS="$SB/jobs"
mkdir -p "$JOBS"

FAIL=0
assert() { # assert <mô tả> <thực tế> <mong đợi>
  if [ "$2" = "$3" ]; then
    echo "  ok   $1 ($2)"
  else
    echo "  FAIL $1: được '$2', mong đợi '$3'"; FAIL=1
  fi
}
field() { python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get(sys.argv[2],""))' "$1" "$2" 2>/dev/null; }

echo "== CA 1: tạo record (status=running + dispatcher_pid + deadline trong CÙNG 1 lời gọi, record chưa tồn tại -> luôn được phép)"
job_id="qs_test1"
_deadline_s=900
_started="$(date +%s)"
python3 "$ROOT/bin/mike_json.py" job-set "$JOBS" "$job_id" \
  job_id="$job_id" from=Mike to=quant-skeptic status=running \
  started_at="$_started" deadline=$((_started + _deadline_s)) \
  logfile=/tmp/x.log discord_thread_id=1 dispatcher_pid="$$" prompt_summary="test" >/dev/null
assert "exit tạo record" "$?" "0"
assert "status=running" "$(field "$JOBS/$job_id.json" status)" "running"
assert "có deadline (BUG 2 đã sửa)" "$([ -n "$(field "$JOBS/$job_id.json" deadline)" ] && echo yes || echo no)" "yes"
assert "dispatcher_pid = script hiện tại" "$(field "$JOBS/$job_id.json" dispatcher_pid)" "$$"

echo "== CA 2 (BUG 1, mô phỏng ĐÚNG race thật): stamp pid TỪ BÊN TRONG subshell nền, SAU KHI script cha 'thoát' (subshell mồ côi) -> PHẢI bị từ chối exit 3"
job_id2="qs_test2"
python3 "$ROOT/bin/mike_json.py" job-set "$JOBS" "$job_id2" \
  job_id="$job_id2" from=Mike to=quant-skeptic status=running \
  started_at="$(date +%s)" deadline=$(($(date +%s)+900)) \
  logfile=/tmp/x2.log discord_thread_id=1 dispatcher_pid=999999999 prompt_summary="test" >/dev/null
# dispatcher_pid GIẢ (999999999, không tồn tại) mô phỏng "script cha đã thoát/bị reparent" —
# đúng tình huống bug thật: caller không còn là hậu duệ của dispatcher_pid trên record.
MIKE_JOB_OWNER="$job_id2" python3 "$ROOT/bin/mike_json.py" job-set "$JOBS" "$job_id2" pid="$BASHPID" >/dev/null 2>&1
assert "exit code (từ chối vì ancestry đứt)" "$?" "3"
assert "pid KHÔNG bị ghi" "$(field "$JOBS/$job_id2.json" pid)" ""

echo "== CA 3 (BUG 1, ĐÚNG cách sửa): stamp pid từ TOP-LEVEL script CÒN SỐNG (dispatcher_pid = chính script này) -> PHẢI thành công"
job_id3="qs_test3"
python3 "$ROOT/bin/mike_json.py" job-set "$JOBS" "$job_id3" \
  job_id="$job_id3" from=Mike to=quant-skeptic status=running \
  started_at="$(date +%s)" deadline=$(($(date +%s)+900)) \
  logfile=/tmp/x3.log discord_thread_id=1 dispatcher_pid="$$" prompt_summary="test" >/dev/null
run_bg() { sleep 0.2; }
run_bg &
_bg_pid=$!
MIKE_JOB_OWNER="$job_id3" python3 "$ROOT/bin/mike_json.py" job-set "$JOBS" "$job_id3" pid="$_bg_pid" >/dev/null
assert "exit code (thành công, dispatcher còn sống)" "$?" "0"
assert "pid được ghi đúng" "$(field "$JOBS/$job_id3.json" pid)" "$_bg_pid"
wait "$_bg_pid" 2>/dev/null

echo "== CA 4: đóng record (status=done) từ CHÍNH subshell đã stamp pid ở CA 3 -> PHẢI thành công (self-ancestry qua pid)"
run_bg2() {
  MIKE_JOB_OWNER="$job_id3" python3 "$ROOT/bin/mike_json.py" job-set "$JOBS" "$job_id3" pid="$BASHPID" >/dev/null 2>&1
  MIKE_JOB_OWNER="$job_id3" python3 "$ROOT/bin/mike_json.py" job-set "$JOBS" "$job_id3" \
    status=done ended_at="$(date +%s)" exit_code=0 result_summary="verdict=CONFIRMED" > "$SB/ca4_rc" 2>&1
  echo $? >> "$SB/ca4_rc"
}
run_bg2 &
wait
assert "exit code đóng record" "$(tail -1 "$SB/ca4_rc")" "0"
assert "status=done" "$(field "$JOBS/$job_id3.json" status)" "done"

echo "== CA 5 (BUG 2, reap thật): record CÓ deadline, quá hạn 2.2 ngày, KHÔNG heartbeat, pid không tồn tại -> job-reap PHẢI đóng thành orphaned"
job_id5="qs_reap_dead"
python3 "$ROOT/bin/mike_json.py" job-set "$JOBS" "$job_id5" \
  job_id="$job_id5" from=Mike to=quant-skeptic status=running \
  started_at=$(( $(date +%s) - 200000 )) deadline=$(( $(date +%s) - 190000 )) \
  logfile="$SB/nope.log" pid=999999998 dispatcher_pid=999999999 >/dev/null
python3 "$ROOT/bin/mike_json.py" job-reap "$JOBS" 60 >/dev/null
assert "status=orphaned (reap đóng được vì có deadline)" "$(field "$JOBS/$job_id5.json" status)" "orphaned"

echo "== CA 6 (đối chứng BUG 2, KHÔNG có deadline): record CHẾT y hệt CA 5 nhưng THIẾU deadline -> job-reap KHÔNG BAO GIỜ đóng được (kẹt running vĩnh viễn)"
job_id6="qs_reap_nodeadline"
python3 "$ROOT/bin/mike_json.py" job-set "$JOBS" "$job_id6" \
  job_id="$job_id6" from=Mike to=quant-skeptic status=running \
  started_at=$(( $(date +%s) - 200000 )) \
  logfile="$SB/nope2.log" pid=999999997 dispatcher_pid=999999996 >/dev/null
python3 "$ROOT/bin/mike_json.py" job-reap "$JOBS" 60 >/dev/null
assert "status vẫn running (KHÔNG deadline -> reap bó tay -> ĐÂY LÀ LÝ DO deadline bắt buộc)" "$(field "$JOBS/$job_id6.json" status)" "running"

echo
if [ "$FAIL" -eq 0 ]; then echo "verify_finding_bg_job_selfcheck: PASS"; else echo "verify_finding_bg_job_selfcheck: FAIL"; fi
exit "$FAIL"
