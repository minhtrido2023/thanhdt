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

# Persist the active Discord thread so _bg_wrapper can post to it even after this session ends.
# DISCORD_THREAD_ID is injected by the CCDB bot when it launches Mike's session.
if [ "$id" = "Mike" ] && [ -n "${DISCORD_THREAD_ID:-}" ]; then
  mkdir -p "$ROOT/agents/Mike/state"
  printf '%s' "$DISCORD_THREAD_ID" > "$ROOT/agents/Mike/state/ccdb_thread_id"
fi

# NOTE (cost-opt #1b, 2026-07-17): this hook used to `cat` context_pack.md /
# context_ops_mini.md here too — found to be a pure duplicate of what
# agents/<id>/CLAUDE.md's own `@kb/context_*.md` import already delivers on every
# fresh session (every headless dispatch is a fresh `claude -p` process, so CLAUDE.md
# is read fresh off disk every time; no staleness risk from removing this). Removed:
# it was literally injecting the same ~48KB (or ~4KB for Wags's mini tier, which
# CLAUDE.md's own import wasn't even matching until this same fix) a second time,
# every single dispatch. CLAUDE.md is now the SOLE source of the shared context pack,
# which also keeps it framed as authoritative "project instructions" rather than
# lower-priority hook stdout.

# Personal working memory (curated by the agent via remember.sh) — durable across restarts,
# higher-signal than the raw recap below. The agent's own priorities / open threads / next steps.
if [ -s "$KB/memory/$id.md" ]; then
  echo "[Working memory CỦA BẠN — ưu tiên & việc đang mở bạn tự ghi; tiếp tục từ đây:]"
  cat "$KB/memory/$id.md"
fi

# Continuity: recap this agent's OWN previous session so a restart continues the thread
# (the durable KB above is fleet-wide facts; this is the in-flight conversation/work).
if [ -n "${MIKE_CWD:-}" ]; then
  python3 "$ROOT/bin/recap_prev.py" "$MIKE_CWD" "${MIKE_SID:-}" 6 2>/dev/null || true
fi

# Job board audit: surface any OVERDUE jobs immediately on restart (Mike only — coordinator owns the board).
if [ "$id" = "Mike" ] && [ -d "$ROOT/bus/jobs" ]; then
  NOW="$(date +%s)"
  overdue_out=""
  for _jf in "$ROOT/bus/jobs"/*.json; do
    [ -f "$_jf" ] || continue
    read -r _jst _jdl _jto _jprompt < <(python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
print(d.get('status','?'), d.get('deadline',0), d.get('to','?'), repr(d.get('prompt_summary','')[:80]))
" "$_jf" 2>/dev/null) || continue
    [ "$_jst" = "running" ] || continue
    [ "$_jdl" -gt 0 ] && [ "$NOW" -gt "$_jdl" ] || continue
    _jid="$(basename "$_jf" .json)"
    _jmin="$(( (NOW - _jdl) / 60 ))"
    overdue_out="${overdue_out}  ⚠️ OVERDUE $_jid (→$_jto, ${_jmin}min quá hạn): $_jprompt\n"
  done
  if [ -n "$overdue_out" ]; then
    echo ""
    echo "[CẢNH BÁO — JOB BOARD CÓ TÁC VỤ QUÁ HẠN — xử lý trước khi nhận việc mới:]"
    printf '%b' "$overdue_out"
    echo "Kiểm tra: bin/jobs.sh list | Đánh xong: python3 bin/mike_json.py job-set bus/jobs <id> status=done"
  fi
fi

# Surface any NEW directive Mike assigned to this agent (once, via offset cache).
source "$ROOT/hooks/_directives.sh"

# Explicit "ready" confirmation (user feedback 2026-07-03): the host's own "Compacting...
# vẫn đang xử lý Xm" progress UI stops updating before giving an unambiguous final signal,
# so after a big compact the user has no way to tell "still working" from "done and idle"
# apart from just trying a new message. This fires LAST in the hook — after KB/memory/job
# board/directives are all loaded — so it's a truthful "actually ready" signal, not a guess
# fired before startup work is done. Fire-and-forget: never blocks/breaks session start if
# Discord is unreachable. Fires on every SessionStart (fresh start, compact-resume, or a
# watchdog-triggered restart) — all of those are cases where the user benefits from knowing
# Mike just became ready again.
if [ "$id" = "Mike" ] && [ -n "${DISCORD_THREAD_ID:-}" ]; then
  "$ROOT/bin/notify_thread.sh" "🟢 Đã resume xong — sẵn sàng nhận việc tiếp." "$DISCORD_THREAD_ID" \
    >/dev/null 2>&1 || true
fi

exit 0
