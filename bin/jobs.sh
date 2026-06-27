#!/usr/bin/env bash
# jobs.sh — poll the dispatch job board (bus/jobs/<job_id>.json) WITHOUT blocking.
#
# A coordinator (Mike or Taylor) dispatches with --bg, then checks here instead of
# sitting idle. Read-only; depends only on python3 (via mike_json.py).
#
#   jobs.sh list [limit]              recent jobs, newest first (default 20)
#   jobs.sh status <job_id>           one job; exit 0=done 2=running 3=overdue
#                                     1=failed/timeout 4=not-found
#   jobs.sh wait <job_id> [--timeout SEC]   poll every 15s until the job leaves
#                                     'running' or SEC elapse (default 900); exits
#                                     with the job's status code (124 on wait-timeout)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JOBS_DIR="$ROOT/bus/jobs"
MJ() { python3 "$ROOT/bin/mike_json.py" "$@"; }

cmd="${1:-list}"
case "$cmd" in
  list)
    MJ job-list "$JOBS_DIR" "${2:-20}"
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
  *)
    echo "usage: jobs.sh {list [limit] | status <job_id> | wait <job_id> [--timeout SEC]}" >&2
    exit 2
    ;;
esac
