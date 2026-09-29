#!/usr/bin/env bash
# stop.sh <agent_id>
# Fires when the child finishes a turn. Records a heartbeat so the consolidator knows
# the agent is alive (unconditionally — that part is unrelated to the check below and must
# always run).
#
# F2 (2026-08-19, after 2 missed-wakeup incidents — 08-13 04:44 and 08-19 05:46/05:13):
# ALSO acts as a circuit breaker for Mike's own session — refuses to let a turn end on a
# Discord thread that still has a Mike-dispatched job running/retrying with NO ScheduleWakeup
# pending to resume it. That exact gap (async job left in flight, no wakeup scheduled, no one
# ever resumes the session) is what caused both incidents; this hook is the mechanical
# enforcement MIKE.md §8's prose discipline was relying on humans/the model to remember.
#
# Scoped to $id == Mike ONLY (see guard below): DISCORD_THREAD_ID is also exported for
# headless dispatched agent sessions (dispatch.sh:~1140), so without this guard a Wags/
# Taylor/... session ending its OWN one-shot turn could get blocked over a Mike job it has
# no ability to act on (no ScheduleWakeup loop of its own) — pure false-positive noise.
#
# Fail-open at EVERY step (missing binary, unreachable API, malformed JSON, ...): this hook
# must NEVER block a normal turn from ending because of an error here. Errors get logged
# where they land naturally (stderr/exit code), never silently promoted to a block.
#
# Must respect stop_hook_active (bool, in the hook's own stdin JSON): if a Stop hook is
# ALREADY blocking this turn, this run must NOT block again — that is exactly the
# unbounded-loop shape stop_hook_active exists to let hooks avoid.
set -uo pipefail   # deliberately NOT -e: every risky step below carries its own fail-open
                   # fallback: an uncaught `-e` abort could exit with something other than a
                   # clean 0, which is itself a fail-CLOSED failure mode for this hook.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/hooks/_resolve_id.sh"   # sets $id (+ $_payload = raw stdin JSON) from $1 or
                                       # stdin session_id; exits 0 if excluded/MIKE_SKIP

"$ROOT/bin/heartbeat.sh" "$id" "" working || true

# --- anti-loop: never block a turn that is already being blocked by a Stop hook ---
_stop_active="$(printf '%s' "${_payload:-}" | python3 -c '
import sys, json
try:
    print("1" if json.load(sys.stdin).get("stop_hook_active") else "0")
except Exception:
    print("0")
' 2>/dev/null)"
[ -n "$_stop_active" ] || _stop_active="0"
[ "$_stop_active" = "1" ] && exit 0

# --- scope: only Mike's own session runs the circuit-breaker check (see header) ---
[ "$id" = "Mike" ] || exit 0

# --- fail-open: no (numeric) Discord thread on this session -> nothing to correlate ---
_tid="${DISCORD_THREAD_ID:-}"
[ -n "$_tid" ] || exit 0
case "$_tid" in
  ''|*[!0-9]*) exit 0 ;;   # non-numeric/garbage -> fail open, don't guess
esac

# 1) any job Mike itself dispatched, still running/retrying, pinned to THIS thread (and not
#    a stale zombie — see job-live-for-thread's HB_LIVE_BOUND_S)?
_live_jobs="$(python3 "$ROOT/bin/mike_json.py" job-live-for-thread "$ROOT/bus/jobs" Mike "$_tid" 2>/dev/null)"
[ -n "$_live_jobs" ] || exit 0
_live_jobs_csv="$(printf '%s' "$_live_jobs" | tr '\n' ',' | sed 's/,$//')"

# 2) did THIS turn itself just call ScheduleWakeup? Read the turn's own transcript, not
#    ccdb's task DB — arch-review coord-mechanism-08-19 caught that ccdb only writes the
#    one-shot row AFTER the CLI process exits (claude_discord/cogs/_run_helper.py), while
#    this Stop hook fires WHILE the CLI is still running (before that write happens). Reading
#    ccdb for THIS turn's own call is therefore a guaranteed miss — it would block every
#    turn that correctly called ScheduleWakeup, not just the ones that forgot to.
#    Heuristic: scan backward from the end of the transcript for the last genuine turn
#    boundary (a "user" message carrying real text, not a tool_result echo — tool results
#    are ALSO role="user" in this transcript format, so content must be checked, not just
#    role) and look for a ScheduleWakeup tool_use anywhere after that boundary.
_sched_this_turn="unknown"
if [ -n "${MIKE_TRANSCRIPT_PATH:-}" ] && [ -r "${MIKE_TRANSCRIPT_PATH:-}" ]; then
  _sched_this_turn="$(python3 - "$MIKE_TRANSCRIPT_PATH" <<'PY' 2>/dev/null
import sys, json
path = sys.argv[1]
try:
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
except Exception:
    print("unknown"); sys.exit(0)
TAIL = 400   # bounded scan-back; a single turn is never remotely this long
lines = lines[-TAIL:]
boundary = 0
for i in range(len(lines) - 1, -1, -1):
    try:
        e = json.loads(lines[i])
    except Exception:
        continue
    msg = e.get("message", {})
    if msg.get("role") != "user":
        continue
    content = msg.get("content")
    is_real_user_text = isinstance(content, str) and content.strip() != ""
    if isinstance(content, list):
        is_real_user_text = any(isinstance(c, dict) and c.get("type") == "text"
                                 and c.get("text", "").strip() for c in content)
    if is_real_user_text:
        boundary = i
        break
found = False
for i in range(boundary, len(lines)):
    try:
        e = json.loads(lines[i])
    except Exception:
        continue
    content = e.get("message", {}).get("content", [])
    if not isinstance(content, list):
        continue
    for c in content:
        if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "ScheduleWakeup":
            found = True
            break
    if found:
        break
print("1" if found else "0")
PY
)"
fi
[ -n "$_sched_this_turn" ] || _sched_this_turn="unknown"
[ "$_sched_this_turn" = "1" ] && exit 0

# 3) does ccdb already have a PRIOR pending one-shot wakeup task for this thread (scheduled
#    by an earlier turn, not yet fired)? Read-only GET, same unauthenticated localhost API
#    bin/wake_thread.sh already POSTs to — see ext/api_server.py (list_tasks) /
#    database/task_repo.py (thread_id, one_shot, enabled columns) in the ccdb bridge repo.
#    A fired one-shot row is DELETEd (task_repo.delete_pending_one_shot_by_thread), not
#    disabled — enabled=1 AND one_shot=1 for this thread_id IS "still pending".
_has_pending="$(python3 - "$_tid" "${WAGS_STOP_TASKS_API:-http://127.0.0.1:8199/api/tasks}" <<'PY' 2>/dev/null
import sys, json, urllib.request
thread_id, api_url = sys.argv[1], sys.argv[2]
try:
    with urllib.request.urlopen(api_url, timeout=5) as r:
        body = json.load(r)
    tasks = body.get("tasks")
    if not isinstance(tasks, list):
        print("unknown"); sys.exit(0)   # key absent/wrong type = evidence gone, not "empty"
    hit = any(t.get("enabled") and t.get("one_shot") and str(t.get("thread_id")) == thread_id
              for t in tasks)
    print("1" if hit else "0")
except Exception:
    print("unknown")
PY
)"
[ -n "$_has_pending" ] || _has_pending="unknown"

case "$_has_pending" in
  1)
    exit 0 ;;                 # a wakeup is already scheduled -> nothing to do
  0)
    : ;;                      # confirmed NO pending wakeup -> fall through and block
  *)
    exit 0 ;;                 # API unreachable / bad data / anything else -> fail OPEN
esac

# Output contract: Claude Code's Stop hook reads `decision`/`reason` at the TOP LEVEL of the
# JSON on stdout (NOT wrapped in hookSpecificOutput — that wrapper's Stop variant only
# carries additionalContext and is silently ignored for blocking). Verified against the
# installed CLI by live A/B (arch-review coord-mechanism-08-19): the hookSpecificOutput shape
# fired the hook once and let the turn end normally; this top-level shape fires the hook a
# SECOND time with stop_hook_active=true and forces the model to continue — which is the
# entire point of this circuit breaker.
_reason="con job ${_live_jobs_csv} dang chay (from=Mike, thread nay) nhung khong co ScheduleWakeup pending — dat ScheduleWakeup truoc khi ket thuc luot (MIKE.md §8)."
python3 -c '
import json, sys
print(json.dumps({"decision": "block", "reason": sys.argv[1]}))
' "$_reason"
exit 0
