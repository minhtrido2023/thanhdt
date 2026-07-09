#!/usr/bin/env bash
# fake claude: làm việc ~70s, heartbeat kiểu agent mỗi 15s (JOB_ID inherit từ dispatch.sh)
ROOT=/home/trido/thanhdt/WorkingClaude/mike
for i in 1 2 3 4; do
  sleep 15
  "$ROOT/bin/append_event.sh" ZZTestHB heartbeat "$JOB_ID" "{\"status\":\"in_progress\",\"note\":\"fake-work $i\"}" "$JOB_ID" >/dev/null 2>&1
done
sleep 10
echo "FAKE_DONE_ALIVE sau ~70s (job $JOB_ID)"
