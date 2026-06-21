#!/usr/bin/env bash
# user_prompt_submit.sh <agent_id>
# Fires on every prompt the child submits. If the shared KB version changed since this
# child last saw it, inject ONLY the RECENT delta (between the RECENT markers in
# context_pack.md). This is how a child learns other children's results without anyone
# repeating them. Plain stdout is appended to the model's context for this turn.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KB="$ROOT/kb"
id="${1:-${AGENT_ID:-unknown}}"

cur="$(tr -dc '0-9' < "$KB/version.txt" 2>/dev/null || true)"; cur="${cur:-0}"
cache="${XDG_CACHE_HOME:-$HOME/.cache}/mike_kbver_$id"
mkdir -p "$(dirname "$cache")"
seen="$(cat "$cache" 2>/dev/null || echo -1)"

if [ "$cur" != "$seen" ]; then
  printf '%s' "$cur" > "$cache"
  recent="$(awk '/<!--RECENT-START-->/{f=1;next} /<!--RECENT-END-->/{f=0} f' "$KB/context_pack.md" 2>/dev/null || true)"
  if [ -n "${recent//[[:space:]]/}" ]; then
    echo "[Mike KB cập nhật → v$cur] Thay đổi chung kể từ lượt trước của bạn (kết quả từ các agent khác — dùng luôn, không hỏi lại):"
    printf '%s\n' "$recent"
  fi
fi
exit 0
