#!/usr/bin/env bash
# remember.sh — an agent's curated WORKING MEMORY (current priorities / open threads / who
# it's waiting on / next steps). Stored at kb/memory/<id>.md and injected at that agent's
# SessionStart. Unlike the auto-recap (raw tail of the previous transcript), this is durable
# and survives ANY number of restarts — the agent keeps it current on purpose.
#
# Usage:
#   remember.sh <id> "<note>"     append a timestamped bullet (keeps last $MIKE_MEMORY_CAP=40)
#   remember.sh <id> --set        replace the whole memory body with stdin (full rewrite)
#   remember.sh <id> --clear      empty it
#   remember.sh <id> --show       print it
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEM="$ROOT/kb/memory"
mkdir -p "$MEM"

id="${1:?usage: remember.sh <agent_id> <note|--set|--clear|--show>}"
shift || true
f="$MEM/$id.md"
CAP="${MIKE_MEMORY_CAP:-40}"
header() { printf '# Working memory — %s\n> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của %s.\n\n' "$id" "$id"; }

case "${1:-}" in
  --show)  [ -s "$f" ] && cat "$f" || echo "(working memory trống cho $id)"; exit 0 ;;
  --clear) header > "$f"; echo "cleared working memory for $id"; exit 0 ;;
  --set)
    tmp="$(mktemp)"; { header; cat; printf '\n'; } > "$tmp"; mv -f "$tmp" "$f"
    echo "set working memory for $id"; exit 0 ;;
  "")      echo "usage: remember.sh <agent_id> <note|--set|--clear|--show>" >&2; exit 2 ;;
esac

note="$*"
ts="$(date -u +%FT%TZ)"
[ -s "$f" ] || header > "$f"
printf -- '- [%s] %s\n' "$ts" "$note" >> "$f"

# Cap: keep the header + the most recent $CAP bullets so it stays a scratchpad, not a log.
nb="$(grep -c '^- ' "$f" 2>/dev/null || echo 0)"
if [ "${nb:-0}" -gt "$CAP" ]; then
  tmp="$(mktemp)"; { header; grep '^- ' "$f" | tail -n "$CAP"; } > "$tmp"; mv -f "$tmp" "$f"
fi
echo "remembered for $id"
