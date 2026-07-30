#!/usr/bin/env bash
# compact_done_watcher.sh <topic> <stamp_epoch> <transcript_path>
# Spawned detached (setsid+nohup, backgrounded) by session_start.sh's ready-notify block every
# time a SessionStart fires with source=="compact" — that event is now silenced at the source
# (2026-07-30 fix for the "Đã resume xong" spam incident, see session_start.sh's own comment),
# but it was ALSO the literal "your manual /compact just finished" signal the 2026-07-03 feature
# was built to provide. This restores that signal without reintroducing the spam:
#
# 1. Settle: sleep past the window a chained double-compact needs to reveal itself (structural
#    bound, not just observed — a chained rerun replays the SAME `/compact` prompt, so a second
#    compaction always starts from an already-tiny context and finishes fast; measured 102-175s
#    across every chained episode on record). Then check whether a NEWER compact re-stamped the
#    marker in the meantime. If so, silently stand down — the watcher spawned for THAT compact
#    owns the check instead. Only the actual last compact in a chain reaches step 2.
# 2. Trigger gate (checked once — it can't change): read the transcript's last `compact_boundary`
#    record. If `compactMetadata.trigger != "manual"` (an auto-compaction — context hit the size
#    ceiling mid-task, nothing the user asked for or is waiting to hear about), stand down. ccdb
#    already posts its own "-# 🗜️ Context compacted (auto|manual) — was N tokens" notice for
#    every compaction, so a second ping here would be pure noise for the auto case, not signal.
# 3. Idle gate (retried — the turn may genuinely still be running): the transcript's last entry
#    must be >=60s old before this is a truthful "ready" signal, not the exact mid-turn false-
#    ready this whole 2026-07-30 fix exists to remove. A single one-shot check at the settle
#    point under-delivers on the biggest compacts (measured: real manual compactions with a large
#    post-boundary tool-output burst can still be mid-turn at T+240s, going idle only tens of
#    seconds later) — so this polls every IDLE_RECHECK_SECONDS up to IDLE_MAX_WAIT_SECONDS total,
#    re-checking the supersede marker on every iteration (abort immediately if a newer compact
#    shows up mid-wait), before giving up silently.
#
# Reads only the TAIL of the transcript (not the whole file) — this file accumulates a live
# companion's entire multi-week history (tens of MB) and by the time this watcher checks
# everything relevant is necessarily near the end. TAIL_BYTES is sized well above the largest
# single record and largest post-boundary burst observed in production transcripts (up to ~740KB
# and ~1.5MB respectively) — err large; a live-conversation JSONL tail read is cheap either way.
#
# Does NOT survive a ccdb-mike.service restart mid-wait (setsid escapes the process group/session
# but not the systemd cgroup the hook's child processes run under) — an accepted silent-miss for
# a UX nicety, not a correctness issue; nothing downstream depends on this ping firing.
#
# Every skip reason is appended to a small local log (trimmed to the last LOG_MAX_LINES lines on
# each write) so a missing ping is distinguishable after the fact from a correctly-suppressed
# auto-compaction, instead of both looking identical from the outside (silence).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

topic="${1:?usage: compact_done_watcher.sh <topic> <stamp_epoch> <transcript_path>}"
stamp="${2:?usage: compact_done_watcher.sh <topic> <stamp_epoch> <transcript_path>}"
transcript="${3:-}"
SETTLE_SECONDS=240
IDLE_SECONDS=60
IDLE_RECHECK_SECONDS=60
IDLE_MAX_WAIT_SECONDS=1200
TAIL_BYTES=5000000
LOG_MAX_LINES=500

marker="$ROOT/agents/Mike/state/last_compact_${topic}.txt"
log="$ROOT/agents/Mike/state/compact_watcher.log"

_log() {
  mkdir -p "$(dirname "$log")"
  { printf '%s topic=%s stamp=%s %s\n' "$(date -Iseconds)" "$topic" "$stamp" "$1" >> "$log"
    tail -n "$LOG_MAX_LINES" "$log" > "${log}.tmp.$$" && mv -f "${log}.tmp.$$" "$log"
  } 2>/dev/null || true
}

_superseded() {
  [ "$(cat "$marker" 2>/dev/null || true)" = "$stamp" ] || return 0
  return 1
}

_check_transcript() {
  # Prints "manual-idle" / "manual-active" / "auto" / "unreadable" on stdout.
  [ -n "$transcript" ] && [ -f "$transcript" ] || { echo "unreadable"; return; }
  tail -c "$TAIL_BYTES" "$transcript" 2>/dev/null | python3 -c '
import sys, json
from datetime import datetime, timezone

try:
    sys.stdin.reconfigure(errors="replace")
except Exception:
    pass

last_trigger = None
last_ts = None
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    ts = d.get("timestamp")
    if ts:
        last_ts = ts
    if d.get("type") == "system" and d.get("subtype") == "compact_boundary":
        cm = d.get("compactMetadata") or {}
        last_trigger = cm.get("trigger")

if last_trigger is None:
    print("noboundary")
    sys.exit(0)
if last_trigger != "manual":
    print("auto")
    sys.exit(0)
if not last_ts:
    print("unreadable")
    sys.exit(0)
try:
    dt = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
except Exception:
    print("unreadable")
    sys.exit(0)
age = (datetime.now(timezone.utc) - dt).total_seconds()
print("manual-idle" if age >= '"$IDLE_SECONDS"' else "manual-active")
' 2>/dev/null || echo "unreadable"
}

sleep "$SETTLE_SECONDS"

if _superseded; then
  _log "skip:superseded"
  exit 0
fi

_verdict="$(_check_transcript)"
case "$_verdict" in
  auto) _log "skip:auto"; exit 0 ;;
  noboundary) _log "skip:noboundary"; exit 0 ;;
  unreadable) _log "skip:unreadable"; exit 0 ;;
esac

_waited=0
while [ "$_verdict" != "manual-idle" ]; do
  if [ "$_waited" -ge "$IDLE_MAX_WAIT_SECONDS" ]; then
    _log "skip:still-active-after-${_waited}s"
    exit 0
  fi
  sleep "$IDLE_RECHECK_SECONDS"
  _waited=$(( _waited + IDLE_RECHECK_SECONDS ))
  if _superseded; then
    _log "skip:superseded-during-idle-wait"
    exit 0
  fi
  _verdict="$(_check_transcript)"
  case "$_verdict" in
    auto) _log "skip:auto-during-idle-wait"; exit 0 ;;
    noboundary) _log "skip:noboundary-during-idle-wait"; exit 0 ;;
  esac
done

if "$ROOT/bin/notify_thread.sh" "🗜️ Compact xong — sẵn sàng nhận việc tiếp." "$topic" >/dev/null 2>&1; then
  _log "fire (waited ${_waited}s past settle)"
else
  _log "fire-attempt-failed (waited ${_waited}s past settle)"
fi
