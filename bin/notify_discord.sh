#!/usr/bin/env bash
# notify_discord.sh "message" ["title"] [color] ["thread_name"]
#
# Push a notification to Mike's Discord #mikefleet channel via ccdb-mike API.
# color: 3447003 (blue, default) | 16711680 (red, urgent) | 3066993 (green, success)
# thread_name: Discord forum/thread topic (e.g. "update task")
# Always exits 0 — never breaks the caller.
#
# Root cause (2026-08-02, found while investigating "Mike có vẻ ngừng bất thường"): a message
# over Discord's embed description cap (4096 chars) makes the bridge's /api/notify 500 with
# "Invalid Form Body" and the message is silently dropped — no retry, no fallback, caller never
# told. ~10 occurrences over 2026-07-30..08-01 in journalctl -u ccdb-mike. Fix: truncate
# CHARACTER-wise (Python str slicing, never a raw byte cut) to a safe margin before building the
# payload, so a long report/incident message degrades to "sent but shortened" instead of "not
# sent at all".
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIKE_DISCORD_API="${MIKE_DISCORD_API:-http://127.0.0.1:8199}"
# Kênh tra qua registry duy nhất kb/discord_channels.json (bin/discord_channel.sh). Biến môi
# trường vẫn override được và nay nhận CẢ tên lẫn ID trần.
MIKE_DISCORD_CHANNEL="$("$ROOT/bin/discord_channel.sh" "${MIKE_DISCORD_CHANNEL:-mikefleet}")"
EMBED_DESC_LIMIT=4000   # margin under Discord's hard 4096 cap

msg="${1:-}"
title="${2:-}"
color="${3:-3447003}"
thread_name="${4:-}"

[ -z "$msg" ] && exit 0

payload=$(python3 -c "
import json, sys
limit = int(sys.argv[6])
message = sys.argv[1]
if len(message) > limit:
    message = message[:limit - 20] + '\n… (cắt bớt, quá dài cho embed)'
d = {'message': message, 'channel_id': int(sys.argv[2]), 'format': 'embed', 'color': int(sys.argv[3])}
if sys.argv[4]:
    d['title'] = sys.argv[4]
if sys.argv[5]:
    d['thread_name'] = sys.argv[5]
print(json.dumps(d, ensure_ascii=False))
" "$msg" "$MIKE_DISCORD_CHANNEL" "$color" "$title" "$thread_name" "$EMBED_DESC_LIMIT" 2>/dev/null) || exit 0

curl -s -X POST "$MIKE_DISCORD_API/api/notify" \
  -H "Content-Type: application/json" \
  -d "$payload" \
  > /dev/null 2>&1 || true
