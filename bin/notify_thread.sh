#!/usr/bin/env bash
# notify_thread.sh "<message>" [thread_id]
# Post a message directly to the current Discord thread (the one that triggered this session).
# thread_id defaults to contents of state/ccdb_thread_id.
# Uses ccdb-mike's /api/notify with channel_id=thread_id (threads are channels in Discord).
#
# Discord messages cap at ~2000 chars; /api/notify has no file-attachment support (that path
# only exists for live bot-managed sessions via .ccdb-attachments-<thread_id>, unusable from a
# standalone cron script). Long messages (e.g. plan reports with many tickers) are CHUNKED at
# line boundaries into multiple sequential sends instead of being truncated/dropped — same
# strategy the Discord bridge itself uses for long assistant replies (chunk_message()).
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
LIMIT = 1900  # safety margin under Discord's ~2000-char message cap

def chunk(text, limit):
    """Split at line boundaries into pieces <= limit chars. Never breaks mid-line
    (a single line longer than limit is hard-cut as a last resort)."""
    lines = text.split("\n")
    chunks, cur = [], ""
    for line in lines:
        candidate = line if not cur else cur + "\n" + line
        if len(candidate) <= limit:
            cur = candidate
            continue
        if cur:
            chunks.append(cur)
        if len(line) <= limit:
            cur = line
        else:
            for i in range(0, len(line), limit):
                chunks.append(line[i:i + limit])
            cur = ""
    if cur:
        chunks.append(cur)
    return chunks or [""]

pieces = chunk(message, LIMIT) if len(message) > LIMIT else [message]

for i, piece in enumerate(pieces, 1):
    body = f"[{i}/{len(pieces)}]\n{piece}" if len(pieces) > 1 else piece
    payload = json.dumps({"message": body, "channel_id": int(thread_id), "format": "text"}).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:8199/api/notify",
        data=payload, method="POST",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        print(r.read().decode())
PY
