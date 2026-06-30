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
exit 0
