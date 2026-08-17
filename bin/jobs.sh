#!/usr/bin/env bash
# jobs.sh — poll the dispatch job board (bus/jobs/<job_id>.json) WITHOUT blocking.
#
# A coordinator (Mike or Taylor) dispatches with --bg, then checks here instead of
# sitting idle. Read-only; depends only on python3 (via mike_json.py).
#
#   jobs.sh list [limit]              recent jobs, newest first (default 20)
#   jobs.sh status <job_id>           one job; exit 0=done 2=running 3=overdue 5=pending-resume
#                                     1=failed/timeout 4=not-found
#   jobs.sh wait <job_id> [--timeout SEC]   poll every 15s until the job leaves
#                                     'running' or SEC elapse (default 900); exits
#                                     with the job's status code (124 on wait-timeout)
#   jobs.sh reap [grace_sec] [--dry-run]   close records stuck at status=running whose
#                                     dispatcher died (deadline + grace passed AND pid
#                                     dead/absent) -> status=orphaned. Default grace 3600s.
#   jobs.sh cancel <job_id> [grace_sec]    STOP a running job for real: kill its whole
#                                     process tree, VERIFY it is dead, then stamp
#                                     status=cancelled. Use this instead of
#                                     `kill <pid>` + `job-set status=failed` — that
#                                     improvisation killed only the wrapper and left the
#                                     agent editing files while the board said "failed"
#                                     (incident 2026-08-09, 3rd duplicate-dispatch
#                                     collision, that one on executor.py).
#   jobs.sh mark-replied <job_id>     stamp replied_at on the job record so subsequent
#                                     wakeup turns (from ladder or a late push) know Mike
#                                     already posted the result — anti-double-reply guard.
#                                     Idempotent; safe to call multiple times.
#   jobs.sh is-replied <job_id>       exit 0 = replied_at is set (skip this wakeup turn);
#                                     exit 1 = not yet replied (proceed normally).
#                                     Call at the TOP of every wakeup turn before posting.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JOBS_DIR="$ROOT/bus/jobs"
MJ() { python3 "$ROOT/bin/mike_json.py" "$@"; }

cmd="${1:-list}"
case "$cmd" in
  list)
    MJ job-list "$JOBS_DIR" "${2:-20}"
    ;;
  reap)
    # Close records left status=running by a dispatcher that died (see job-reap docstring).
    MJ job-reap "$JOBS_DIR" "${2:-3600}" ${3:-}
    ;;
  cancel)
    # The missing primitive (added 2026-08-10). Everything that makes it safe — tree kill,
    # death verification, refusing to stamp a status it cannot back up — lives in
    # mike_json.py job-cancel; this is just the front door.
    job_id="${2:?usage: jobs.sh cancel <job_id> [grace_sec]}"
    MJ job-cancel "$JOBS_DIR" "$job_id" ${3:-}
    ;;
  status)
    job_id="${2:?usage: jobs.sh status <job_id>}"
    MJ job-get "$JOBS_DIR" "$job_id"
    ;;
  wait)
    job_id="${2:?usage: jobs.sh wait <job_id> [--timeout SEC]}"
    wtimeout=900
    if [ "${3:-}" = "--timeout" ]; then wtimeout="${4:?--timeout needs a value}"; fi
    deadline=$(( $(date +%s) + wtimeout ))
    while :; do
      set +e
      MJ job-get "$JOBS_DIR" "$job_id" >/dev/null 2>&1
      rc=$?
      set -e
      # 2=running keeps waiting; anything else (done/overdue/failed/not-found) is terminal
      if [ "$rc" -ne 2 ]; then
        MJ job-get "$JOBS_DIR" "$job_id"
        exit "$rc"
      fi
      if [ "$(date +%s)" -ge "$deadline" ]; then
        echo "wait timeout after ${wtimeout}s — job $job_id still running" >&2
        MJ job-get "$JOBS_DIR" "$job_id" || true
        exit 124
      fi
      sleep 15
    done
    ;;
  mark-replied)
    # Stamp replied_at on the job record — idempotent, safe to call multiple times.
    # Call immediately after posting a job's result to Discord, before ending the turn.
    # Prevents duplicate responses when push-wake + ladder-wake both fire for the same job.
    job_id="${2:?usage: jobs.sh mark-replied <job_id>}"
    MJ job-set "$JOBS_DIR" "$job_id" "replied_at=$(date -u +%FT%TZ)"
    ;;
  is-replied)
    # Exit 0 = replied_at is set (this job was already reported — stop the wakeup turn).
    # Exit 1 = not yet replied (proceed normally).
    # Call at the TOP of every wakeup turn, before reading job status or posting anything.
    job_id="${2:?usage: jobs.sh is-replied <job_id>}"
    val=$(MJ job-field "$JOBS_DIR" "$job_id" replied_at 2>/dev/null || true)
    [ -n "$val" ]
    ;;
  *)
    echo "usage: jobs.sh {list [limit] | status <job_id> | wait <job_id> [--timeout SEC] | cancel <job_id> [grace_sec] | reap [grace_sec] [--dry-run] | mark-replied <job_id> | is-replied <job_id>}" >&2
    exit 2
    ;;
esac
