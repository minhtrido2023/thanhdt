#!/usr/bin/env bash
# session_start.sh <agent_id>
# Fires when a child session starts/resumes. Injects the current shared context_pack
# (plain stdout is added to the session context) and primes the version cache so the
# first UserPromptSubmit won't re-inject the same thing.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KB="$ROOT/kb"
id="${1:-${AGENT_ID:-unknown}}"

cur="$(tr -dc '0-9' < "$KB/version.txt" 2>/dev/null || true)"; cur="${cur:-0}"
cache="${XDG_CACHE_HOME:-$HOME/.cache}/mike_kbver_$id"
mkdir -p "$(dirname "$cache")"
printf '%s' "$cur" > "$cache"

if [ -s "$KB/context_pack.md" ]; then
  echo "[Mike KB v$cur] Bối cảnh chung của fleet (đọc trước khi làm, không hỏi lại điều đã ghi ở đây):"
  cat "$KB/context_pack.md"
fi
exit 0
