#!/usr/bin/env bash
# Selfcheck cổng wakeup của dispatch.sh (exit 8). Không phát job: chỉ test nhánh bị CHẶN + đọc tĩnh.
#   bash bin/dispatch_wakeup_gate_selfcheck.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
D="$HERE/dispatch.sh"
fails=0
chk() { if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1 (got rc=$2, want $3)"; fails=$((fails+1)); fi; }
P="selfcheck prompt dài hơn tám byte"
run() { env -u JOB_ID -u DISPATCH_FROM -u MIKE_WAKEUP_GATE "$@" >/dev/null 2>&1; echo $?; }

chk "interactive --bg thiếu cờ ⇒ exit 8"       "$(run CLAUDECODE=1 bash "$D" Taylor "$P" --bg)" 8
chk "DISPATCH_FROM=Mike ⇒ vẫn chặn"            "$(run CLAUDECODE=1 DISPATCH_FROM=Mike bash "$D" Taylor "$P" --bg)" 8
chk "MIKE_WAKEUP_GATE=off ⇒ không chặn exit 8" "$([ "$(run CLAUDECODE=1 MIKE_WAKEUP_GATE=off bash "$D" Taylor "$P" --bg --timeout 1 --provider __nope__)" != 8 ] && echo ok)" ok
chk "có --wakeup-ack ⇒ qua cổng"               "$([ "$(run CLAUDECODE=1 bash "$D" Taylor "$P" --bg --wakeup-ack --provider __nope__)" != 8 ] && echo ok)" ok
chk "có --no-followup ⇒ qua cổng"              "$([ "$(run CLAUDECODE=1 bash "$D" Taylor "$P" --bg --no-followup --provider __nope__)" != 8 ] && echo ok)" ok
chk "không CLAUDECODE (cron) ⇒ qua cổng"       "$([ "$(env -u CLAUDECODE -u JOB_ID -u DISPATCH_FROM bash "$D" Taylor "$P" --bg --provider __nope__ >/dev/null 2>&1; echo $?)" != 8 ] && echo ok)" ok
chk "agent headless (JOB_ID) ⇒ qua cổng"       "$([ "$(env CLAUDECODE=1 JOB_ID=x -u DISPATCH_FROM bash "$D" Taylor "$P" --bg --provider __nope__ >/dev/null 2>&1; echo $?)" != 8 ] && echo ok)" ok
chk "DISPATCH_FROM=Wags ⇒ qua cổng"            "$([ "$(env CLAUDECODE=1 DISPATCH_FROM=Wags -u JOB_ID bash "$D" Taylor "$P" --bg --provider __nope__ >/dev/null 2>&1; echo $?)" != 8 ] && echo ok)" ok
chk "đồng bộ (không --bg) ⇒ qua cổng"          "$([ "$(run CLAUDECODE=1 bash "$D" Taylor "$P" --provider __nope__)" != 8 ] && echo ok)" ok
grep -q -- '--no-followup' "$HERE/wakeup_audit.py"; chk "wakeup_audit miễn --no-followup" "$?" 0
[ "$fails" -eq 0 ] && echo "ALL PASS" || { echo "$fails FAIL"; exit 1; }
