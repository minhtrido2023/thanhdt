#!/usr/bin/env bash
# notify_thread.sh "<message>" [thread_id]
# Post a message directly to the current Discord thread (the one that triggered this session).
# thread_id defaults to contents of state/ccdb_thread_id.
# Uses ccdb-mike's /api/notify with channel_id=thread_id (threads are channels in Discord).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

msg="${1:?usage: notify_thread.sh \"<message>\" [thread_id]}"
thread_id="${2:-}"

if [ -z "$thread_id" ]; then
  state_file="$ROOT/agents/Mike/state/ccdb_thread_id"
  [ -f "$state_file" ] || { echo "notify_thread: no thread_id and state file missing" >&2; exit 1; }
  thread_id="$(cat "$state_file")"
fi

[ -n "$thread_id" ] || { echo "notify_thread: empty thread_id" >&2; exit 1; }

python3 - "$thread_id" "$msg" << 'PY'
import sys, json, urllib.request
thread_id, message = sys.argv[1], sys.argv[2]
payload = json.dumps({"message": message, "channel_id": int(thread_id), "format": "text"}).encode()
req = urllib.request.Request(
    "http://127.0.0.1:8199/api/notify",
    data=payload, method="POST",
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=10) as r:
    print(r.read().decode())
PY
