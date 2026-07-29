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

# INTERACTIVE_TID — "this session IS the user's live Discord session, in that topic".
# Since 2026-07-22b, DISCORD_THREAD_ID carries TWO different meanings:
#   1. injected by the CCDB bridge  → the user's live session, topic = where they are chatting;
#   2. exported by bin/dispatch.sh  → merely "the topic this JOB's output belongs to", on a
#      headless `claude -p` run that no human is watching.
# The Mike-only branches below (global ccdb pointer write, job-board topic filter, "🟢 Đã
# resume xong" notice) are only ever correct for meaning 1 — arming them for meaning 2 makes a
# cron-dispatched Mike (daily_retro.sh, kb_nightly.sh) clobber the pointer, spray a resume
# notice into whatever topic the user last opened, and lose the deliberate fail-open of the
# job-board audit. Distinguish by JOB_ID, which bin/dispatch.sh exports for every dispatched
# run and nothing else sets.
# Self-heal (arch-reviewer round 2): a gate that keys on the ABSENCE of a variable fails
# SILENTLY if JOB_ID ever leaks into a long-lived process — the ccdb bridge copies its whole
# environment into every Mike session it spawns (runner.py `dict(os.environ)`), so a bridge
# restarted by hand from inside a dispatched shell would carry a dead JOB_ID forever and mute
# all three branches with no error. So the marker only counts while it still maps to a job
# record that is actually RUNNING; a stale/leaked one decays back to "interactive". A
# set-but-empty JOB_ID can never map to a running record, so it decays the same way.
INTERACTIVE_TID=""
_job_rec="$ROOT/bus/jobs/${JOB_ID:-}.json"
if [ -z "${JOB_ID+x}" ] || ! grep -qs '"status": *"running"' "$_job_rec"; then
  INTERACTIVE_TID="${DISCORD_THREAD_ID:-}"
fi

# Persist the active Discord thread so _bg_wrapper can post to it even after this session ends.
# DISCORD_THREAD_ID is injected by the CCDB bot when it launches Mike's session.
if [ "$id" = "Mike" ] && [ -n "$INTERACTIVE_TID" ]; then
  mkdir -p "$ROOT/agents/Mike/state"
  printf '%s' "$INTERACTIVE_TID" > "$ROOT/agents/Mike/state/ccdb_thread_id"
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
# Mike-only carve-out (2026-07-29, root cause of the recurring "trả lời nhầm task cũ" bug —
# RETRO 07-17/07-19/07-26/07-27, caught live again today as job Mike_20260729_173001):
# recap_prev.py's docstring assumes "project dir maps 1:1 to one logical agent" — true for
# every other agent (their cwd only ever holds sequential one-shot headless dispatches), but
# FALSE for Mike, who uniquely also has a long-lived live companion session sharing the same
# project dir. A headless dispatch (daily_retro.sh, kb_nightly.sh) started while the live
# companion is mid-conversation picks up the LIVE session's last turns as "your own previous
# session, continue this thread" instead of a genuine prior headless run — that's what made
# the retro draft job answer with Taylor-job-monitoring chatter instead of writing a draft.
# Headless Mike dispatches are fully self-contained one-shot prompts by design (see
# daily_retro.sh's own "viết xong draft là DỪNG" instruction) and were never meant to inherit
# prior-turn context, so skip recap for them entirely — only recap on a genuine live-companion
# restart (arch-reviewer note: this guard keys on the literal id "Mike" — the actual precondition
# is "a live daemon shares this cwd with headless dispatches", so if any other agent is ever
# re-enabled as a daemon via `systemctl --user enable --now mike@<id>`, revisit this guard for it too)
# restart (INTERACTIVE_TID non-empty, same signal the job-board/notice blocks above already use).
if [ -n "${MIKE_CWD:-}" ] && { [ "$id" != "Mike" ] || [ -n "$INTERACTIVE_TID" ]; }; then
  python3 "$ROOT/bin/recap_prev.py" "$MIKE_CWD" "${MIKE_SID:-}" 6 2>/dev/null || true
fi

# Job board audit: surface any OVERDUE jobs immediately on restart (Mike only — coordinator owns the board).
# TOPIC-SCOPED (2026-07-22): jobs are split by the topic they were dispatched from. Detail only
# for jobs belonging to THIS session's topic; jobs of other topics collapse to a count + routing
# rule. Root cause this fixes: the block used to dump EVERY overdue job into whatever topic Mike
# happened to start a session in, telling him to "xử lý trước khi nhận việc mới" — so Mike would
# narrate topic A's work inside topic B just because that's where the user was reading.
if [ "$id" = "Mike" ] && [ -d "$ROOT/bus/jobs" ]; then
  NOW="$(date +%s)"
  MY_TID="$INTERACTIVE_TID"   # empty on a dispatched/cron session → fail-open, show every job
  overdue_out=""
  other_n=0
  for _jf in "$ROOT/bus/jobs"/*.json; do
    [ -f "$_jf" ] || continue
    read -r _jst _jdl _jto _jtid _jprompt < <(python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
print(d.get('status','?'), d.get('deadline',0), d.get('to','?'),
      d.get('discord_thread_id') or '-', repr(d.get('prompt_summary','')[:80]))
" "$_jf" 2>/dev/null) || continue
    [ "$_jst" = "running" ] || continue
    [ "$_jdl" -gt 0 ] && [ "$NOW" -gt "$_jdl" ] || continue
    # Belongs to a DIFFERENT topic → count only, no detail (nothing to narrate here).
    if [ -n "$MY_TID" ] && [ "$_jtid" != "-" ] && [ "$_jtid" != "$MY_TID" ]; then
      other_n=$((other_n + 1)); continue
    fi
    _jid="$(basename "$_jf" .json)"
    _jmin="$(( (NOW - _jdl) / 60 ))"
    overdue_out="${overdue_out}  ⚠️ OVERDUE $_jid (→$_jto, ${_jmin}min quá hạn): $_jprompt\n"
  done
  if [ -n "$overdue_out" ]; then
    echo ""
    echo "[CẢNH BÁO — JOB BOARD CÓ TÁC VỤ QUÁ HẠN (thuộc ĐÚNG topic này) — xử lý trước khi nhận việc mới:]"
    printf '%b' "$overdue_out"
    echo "Kiểm tra: bin/jobs.sh list | Đánh xong: python3 bin/mike_json.py job-set bus/jobs <id> status=done"
  fi
  if [ "$other_n" -gt 0 ]; then
    echo ""
    echo "[$other_n job quá hạn thuộc TOPIC KHÁC — KHÔNG kể/báo cáo ở topic này. Cần xử lý thì gửi vào"
    echo " ĐÚNG topic của job: bin/notify_thread.sh \"<msg>\" \"\$(python3 bin/mike_json.py job-field bus/jobs <job_id> discord_thread_id)\"]"
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
# INTERACTIVE_TID (not DISCORD_THREAD_ID): a headless dispatched session has no human waiting
# on a "ready" signal — announcing there is pure noise in the user's topic.
if [ "$id" = "Mike" ] && [ -n "$INTERACTIVE_TID" ]; then
  "$ROOT/bin/notify_thread.sh" "🟢 Đã resume xong — sẵn sàng nhận việc tiếp." "$INTERACTIVE_TID" \
    >/dev/null 2>&1 || true
fi

exit 0
