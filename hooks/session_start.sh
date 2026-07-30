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
# restart (INTERACTIVE_TID non-empty, same signal the job-board/notice blocks above already use;
# arch-reviewer note: this guard keys on the literal id "Mike" — the actual precondition is "a
# live daemon shares this cwd with headless dispatches", so if any other agent is ever re-enabled
# as a daemon via `systemctl --user enable --now mike@<id>`, revisit this guard for it too).
#
# Mirror-direction carve-out (2026-07-30, arch-reviewer follow-up finding from the above fix):
# the SAME collision runs backwards. ccdb re-invokes `claude --resume <sid>` on every single user
# message (so SessionStart fires every turn, not just on a genuine restart), but MIKE_SID (the
# real Claude Code session_id) stays IDENTICAL across all those turns of ONE conversation — only a
# genuine restart (a fresh session, e.g. after a crash — NOT compaction, which keeps the same sid
# and transcript file; verified against real transcripts with 12-18 compact events each, still a
# single sessionId) produces a new one. Default recap_prev.py always excludes only "$MIKE_SID.jsonl"
# and picks the mtime-newest OTHER file in the shared agents/Mike project dir — on an ordinary
# turn that's most often harmless, but whenever a headless dispatch (daily_retro.sh, kb_nightly.sh,
# ops_autofix, ...) happens to be the most recently touched file at that instant, the LIVE companion
# inherits the HEADLESS job's one-shot task as "your own previous session, continue this thread" —
# same bug class, opposite direction (observed 245 non-empty recap injections across one live
# transcript, i.e. this was firing on nearly every turn, most wastefully re-printing stale content
# with no restart to justify it). Fix: track "our own last live session id" explicitly in a pointer
# file, and only recap — using recap_prev.py's explicit-sid mode, bypassing the mtime guess — when
# that id actually CHANGES (a genuine restart), never on an ordinary same-session resume.
#
# Pointer is keyed PER TOPIC ($INTERACTIVE_TID), not global (arch-reviewer caught this on the first
# draft): ccdb keeps one long-lived live session PER Discord topic, all sharing this same cwd
# (confirmed via ccdb's session DB — dozens of distinct topic sessions, several concurrently active
# within days of each other) — a single global pointer file would leak topic A's last turns into
# topic B on every topic switch (the exact cross-topic bleed the job-board audit block below this
# one was already hardened against), and would lose topic A's own recap on its next real restart if
# any other topic had a turn in between. Keying by topic makes each topic's pointer independent.
if [ -n "${MIKE_CWD:-}" ]; then
  if [ "$id" = "Mike" ] && [ -n "$INTERACTIVE_TID" ]; then
    _live_ptr="$ROOT/agents/Mike/state/live_session_ptr_${INTERACTIVE_TID}.txt"
    _prev_live_sid="$(cat "$_live_ptr" 2>/dev/null || true)"
    if [ -n "$_prev_live_sid" ] && [ "$_prev_live_sid" != "${MIKE_SID:-}" ]; then
      python3 "$ROOT/bin/recap_prev.py" "$MIKE_CWD" "${MIKE_SID:-}" 6 "$_prev_live_sid" 2>/dev/null || true
    fi
    mkdir -p "$(dirname "$_live_ptr")"
    printf '%s' "${MIKE_SID:-}" > "$_live_ptr"
  elif [ "$id" != "Mike" ]; then
    python3 "$ROOT/bin/recap_prev.py" "$MIKE_CWD" "${MIKE_SID:-}" 6 2>/dev/null || true
  fi
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
# Discord is unreachable.
# INTERACTIVE_TID (not DISCORD_THREAD_ID): a headless dispatched session has no human waiting
# on a "ready" signal — announcing there is pure noise in the user's topic.
#
# Dedupe guard (2026-07-30, fix for a real spam incident — root-caused via
# `journalctl -u ccdb-mike.service`, thread 1521475726329516122, 07:37-07:49 UTC = 14:37-14:49
# ICT, then cross-checked mechanically against the whole retained journal 06-24→07-30). The old
# version fired on EVERY SessionStart unconditionally; that premise was wrong in TWO distinct
# ways, found across two review rounds — both fixed here, together:
#
# (a) ccdb's "post-compact guardrail" (`_run_helper.py` ~407-415, intentional, has its own loop
#     guard — not itself a bug): when `compact_boundary` fires mid-stream, ccdb interrupts and
#     RERUNS `claude --resume <sid>` with a guardrail prompt appended. That in-process
#     compact_boundary event itself fires a SessionStart with `source: "compact"` (Claude Code's
#     hook payload field, confirmed against the installed CLI's own schema — enum
#     startup/resume/clear/compact/fork) — filtering `source == "compact"` kills this one.
# (b) The guardrail RERUN's own fresh process (`runner.py` → `--resume <sid>`) reports
#     `source: "resume"`, indistinguishable by field alone from a genuine new user turn — an
#     earlier version of this fix missed this and only closed (a), leaving the worse half of the
#     spam (a mid-turn "ready" ping while the turn is still actually running — measured via
#     journal timing: 18 of 28 guardrail reruns in the retained window fired a ping 11-19s after
#     the rerun's own `Claude CLI started`) unfixed. Since ccdb doesn't expose an env var for
#     "this launch is an internal rerun" (checked: `post_compact_rerun` only reaches the
#     subprocess as appended system-prompt text — exposing it as an env var would be the
#     precise fix but means patching `/workspace/claude-code-discord-bridge` and restarting the
#     shared ccdb-mike.service, which can interrupt OTHER topics' live sessions concurrently on
#     that same bridge (its own process-wide `asyncio.Semaphore(3)` allows up to 3 concurrent
#     live sessions across ALL topics — `_run_helper.py` ~41-54) — needs an explicit user
#     decision, not a unilateral edit here), this uses a same-topic proximity heuristic instead:
#     any `source == "compact"` firing stamps a per-topic marker (re-stamped on every compact, so
#     a chain of 2+ compacts just keeps refreshing it — chain length doesn't widen the window
#     needed); a following `resume`/`startup` firing within 60s is treated as "still the same
#     rerun chain" and suppressed too — measured against the full 06-24→07-30 journal, every
#     compact→rerun-ping gap was 8-23s (n=18), so 60s carries >2.5x margin while still letting a
#     genuinely independent user message through quickly (3 real user-turn pings in that same
#     window would have been wrongly swallowed at a naively "safe-looking" 600s — this constant
#     was deliberately re-measured down after review, not guessed). No lock is needed on the
#     marker file itself: it's 0-byte / mtime-only, so a concurrent truncating write can't corrupt
#     it — worst case from any overlap is one extra or one missing ping, not corruption (ccdb does
#     NOT serialize per-topic — the semaphore above is process-wide, not per-thread — so this
#     robustness-to-corruption property is what actually matters here, not serialization).
#     Negative age (marker mtime in the future — NTP step-back) is treated as stale/expired, not
#     "very recent" — an earlier marker-based attempt at this fix silently suppressed forever on
#     that path; this one fails toward notifying instead.
# AskUserQuestion-answer reruns and ScheduleWakeup resumes are unaffected by either clause (both
# are genuinely new user-facing input, source "resume", with no recent compact stamp) — they
# still get a "ready" ping.
#
# Distinct "compact xong" signal (2026-07-30, restores the 2026-07-03 use case the above filter
# silenced — user explicitly asked for this after reviewing the spam fix): `source == "compact"`
# IS the literal "a /compact just finished" event — suppressing its own "Đã resume xong" ping is
# right (mid-turn noise), but that event is the only place the fact is observable at all, so it
# can't just be deleted outright. Two things it must NOT do, found by arch-reviewer before this
# shipped:
#   1. Fire once per compact in a chain (back to spam) — a manual `/compact` that itself
#      immediately re-triggers ccdb's guardrail-rerun-then-recompact path produces exactly ONE
#      extra compact, never more (structural, not just observed: the rerun replays the SAME
#      `/compact` prompt — `_run_helper.py` `replace(config, session_id=..., prompt` unchanged —
#      and `event_processor.py`'s own loop guard blocks a third `compact_occurred`). Measured gap
#      between chained compacts across every episode on record: 102-175s, bounded because a
#      second-in-chain compaction always starts from a tiny already-compacted context (a few
#      thousand tokens vs hundreds of thousands for the first) so it finishes fast. So: stamp a
#      per-topic marker with a timestamp (content compared later — mtime alone can't tell one
#      compact's stamp from the next) and hand off to `bin/compact_done_watcher.sh`, spawned
#      fully detached (setsid+nohup+backgrounded — survives this hook process exiting; does NOT
#      survive a ccdb-mike.service restart mid-wait, since setsid escapes the process group but
#      not the systemd cgroup — acceptable silent-miss for a UX nicety, not a correctness issue).
#      It sleeps 240s (comfortable margin over the observed 102-175s) then fires only if no NEWER
#      compact re-stamped the marker meanwhile — i.e. only the actual last compact in a chain
#      ever produces a ping, exactly once.
#   2. Fire for a compact the user never asked for, or while the turn is still genuinely running
#      (recreating the exact false-"ready" problem this whole fix exists to remove) — auto-
#      compactions (context hit the size ceiling mid-task, no `/compact` typed) are common and
#      ccdb ALREADY posts its own "-# 🗜️ Context compacted (auto|manual) — was N tokens" notice
#      for every one, so signaling again here would be pure noise for those, not signal. The
#      watcher checks `compactMetadata.trigger == "manual"` from the transcript's own
#      `compact_boundary` record (passed `MIKE_TRANSCRIPT_PATH`, already parsed by
#      `_resolve_id.sh`) and an idle check (no transcript activity in the last 60s) before ever
#      notifying — see that script's own comment for the exact logic.
if [ "$id" = "Mike" ] && [ -n "$INTERACTIVE_TID" ]; then
  _compact_marker="$ROOT/agents/Mike/state/last_compact_${INTERACTIVE_TID}.txt"
  _should_notify=1
  if [ "${MIKE_HOOK_SOURCE:-}" = "compact" ]; then
    _should_notify=0
    mkdir -p "$(dirname "$_compact_marker")"
    _compact_stamp="$(date +%s)"
    _compact_marker_tmp="${_compact_marker}.tmp.$$"
    printf '%s' "$_compact_stamp" > "$_compact_marker_tmp" && mv -f "$_compact_marker_tmp" "$_compact_marker"
    nohup setsid "$ROOT/bin/compact_done_watcher.sh" "$INTERACTIVE_TID" "$_compact_stamp" "${MIKE_TRANSCRIPT_PATH:-}" \
      >/dev/null 2>&1 < /dev/null &
    disown 2>/dev/null || true
  elif [ -f "$_compact_marker" ]; then
    _compact_age=$(( $(date +%s) - $(stat -c %Y "$_compact_marker" 2>/dev/null || echo 0) ))
    if [ "$_compact_age" -ge 0 ] && [ "$_compact_age" -lt 60 ]; then
      _should_notify=0
    fi
  fi
  if [ "$_should_notify" = 1 ]; then
    "$ROOT/bin/notify_thread.sh" "🟢 Đã resume xong — sẵn sàng nhận việc tiếp." "$INTERACTIVE_TID" \
      >/dev/null 2>&1 || true
  fi
fi

exit 0
