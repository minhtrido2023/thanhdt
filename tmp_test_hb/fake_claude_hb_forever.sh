#!/usr/bin/env bash
# fake claude heartbeat mãi nhưng không bao giờ xong (test trần N)
ROOT=/home/trido/thanhdt/WorkingClaude/mike
while :; do
  sleep 10
  "$ROOT/bin/append_event.sh" ZZTestHB heartbeat "$JOB_ID" '{"status":"in_progress","note":"hb-forever"}' "$JOB_ID" >/dev/null 2>&1
done
