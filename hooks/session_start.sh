#!/usr/bin/env bash
# session_start.sh <agent_id>
# Fires when a child session starts/resumes. Injects the current shared context_pack
# (plain stdout is added to the session context) and primes the version cache so the
# first UserPromptSubmit won't re-inject the same thing.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KB="$ROOT/kb"
source "$ROOT/hooks/_resolve_id.sh"   # sets $id from $1 or stdin session_id; exits 0 if excluded

cur="$(tr -dc '0-9' < "$KB/version.txt" 2>/dev/null || true)"; cur="${cur:-0}"
cache="${XDG_CACHE_HOME:-$HOME/.cache}/mike_kbver_$id"
mkdir -p "$(dirname "$cache")"
printf '%s' "$cur" > "$cache"

if [ -s "$KB/context_pack.md" ]; then
  echo "[Mike KB v$cur] Bối cảnh chung của fleet (đọc trước khi làm, không hỏi lại điều đã ghi ở đây):"
  cat "$KB/context_pack.md"
fi

# Personal working memory (curated by the agent via remember.sh) — durable across restarts,
# higher-signal than the raw recap below. The agent's own priorities / open threads / next steps.
if [ -s "$KB/memory/$id.md" ]; then
  echo "[Working memory CỦA BẠN — ưu tiên & việc đang mở bạn tự ghi; tiếp tục từ đây:]"
  cat "$KB/memory/$id.md"
fi

# Continuity: recap this agent's OWN previous session so a restart continues the thread
# (the durable KB above is fleet-wide facts; this is the in-flight conversation/work).
if [ -n "${MIKE_CWD:-}" ]; then
  python3 "$ROOT/bin/recap_prev.py" "$MIKE_CWD" "${MIKE_SID:-}" 12 2>/dev/null || true
fi

# Surface any NEW directive Mike assigned to this agent (once, via offset cache).
source "$ROOT/hooks/_directives.sh"
exit 0
