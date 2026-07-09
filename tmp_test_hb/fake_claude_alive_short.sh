#!/usr/bin/env bash
ROOT=/home/trido/thanhdt/WorkingClaude/mike
for i in 1 2 3; do
  sleep 12
  "$ROOT/bin/append_event.sh" ZZTestHB heartbeat "$JOB_ID" "{\"status\":\"in_progress\",\"note\":\"fake-short $i\"}" "$JOB_ID" >/dev/null 2>&1
done
echo "FAKE_DONE_SHORT ~36s (job $JOB_ID)"
