#!/usr/bin/env bash
# notify_discord.sh "message" ["title"] [color]
#
# Push a notification to Mike's Discord #mike channel via ccdb-mike API.
# color: 3447003 (blue, default) | 16711680 (red, urgent) | 3066993 (green, success)
# Always exits 0 — never breaks the caller.
set -euo pipefail

MIKE_DISCORD_API="${MIKE_DISCORD_API:-http://127.0.0.1:8199}"
MIKE_DISCORD_CHANNEL="${MIKE_DISCORD_CHANNEL:-1519342571812421753}"

msg="${1:-}"
title="${2:-}"
color="${3:-3447003}"

[ -z "$msg" ] && exit 0

payload=$(python3 -c "
import json, sys
d = {'message': sys.argv[1], 'channel_id': int(sys.argv[2]), 'format': 'embed', 'color': int(sys.argv[3])}
if sys.argv[4]:
    d['title'] = sys.argv[4]
print(json.dumps(d, ensure_ascii=False))
" "$msg" "$MIKE_DISCORD_CHANNEL" "$color" "$title" 2>/dev/null) || exit 0

curl -s -X POST "$MIKE_DISCORD_API/api/notify" \
  -H "Content-Type: application/json" \
  -d "$payload" \
  > /dev/null 2>&1 || true
