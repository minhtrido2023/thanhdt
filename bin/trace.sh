#!/usr/bin/env bash
# trace.sh <job_id> — pull the full story of ONE dispatch job into a single timeline:
# the job record (bus/jobs/<job_id>.json) + every bus event (any agent's inbox) carrying
# that job_id as trace_id, sorted chronologically.
#
# Motivation (2026-07-02 fleet review): the trace_id correlation mechanism existed in code
# (append_event.sh falls back to $JOB_ID, mike_json.py writes the field) but was NEVER
# populated in practice — 0/1301 historical bus events had a trace_id, because the
# dispatch_prompt template told agents to call append_event.sh with only 4 args and never
# mentioned passing job_id as the 5th. Fixed in dispatch.sh (job_id now baked in as a
# literal in the dispatch prompt) — this script is the payoff: one command instead of
# grepping logs/dispatch_*.log + bus/inbox/*.jsonl by hand to reconstruct what happened.
#
# Read-only. Depends only on python3 (via mike_json.py).
#
#   trace.sh <job_id>              print job record + matching bus events
#   trace.sh <job_id> --log        also tail the dispatch log file (from the job record)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUS="$ROOT/bus"

job_id="${1:?usage: trace.sh <job_id> [--log]}"
show_log="${2:-}"

rc=0
python3 "$ROOT/bin/mike_json.py" trace "$BUS" "$job_id" || rc=$?

if [ "$show_log" = "--log" ]; then
  logfile="$(python3 "$ROOT/bin/mike_json.py" job-get "$ROOT/bus/jobs" "$job_id" 2>/dev/null \
    | awk -F': +' '/^logfile:/{print $2}')" || true
  if [ -n "$logfile" ] && [ -f "$logfile" ]; then
    echo
    echo "=== log tail: $logfile ==="
    tail -n 100 "$logfile"
  fi
fi

exit "$rc"
