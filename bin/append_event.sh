#!/usr/bin/env bash
# append_event.sh <agent_id> <event_type> <topic> <payload_json_or_string> [trace_id]
# Appends one JSONL event to bus/inbox/<agent_id>.jsonl (append-only, one file per child).
# event_id is a real UUID; flock guards this child's own file only (no cross-child contention).
#
# trace_id (optional 5th arg): correlates every event produced during ONE dispatch chain
# (caller -> agent -> auto-callback) so a job's full story can be pulled with one grep
# instead of matching on prompt_summary text. Falls back to $JOB_ID if set (dispatch.sh
# exports it into the headless agent's environment) — an agent calling this script with only
# 4 args still gets traced automatically as long as it's running inside a dispatch job.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUS="$ROOT/bus"
PY="$ROOT/bin/mike_json.py"

id="${1:?usage: append_event.sh <agent_id> <event_type> <topic> <payload> [trace_id]}"
etype="${2:?event_type required (finding|status|question|answer|decision|error)}"
topic="${3:?topic required}"
payload="${4:?payload required (json object/array, or plain string)}"
trace_id="${5:-${JOB_ID:-}}"

kbver="$(tr -dc '0-9' < "$ROOT/kb/version.txt" 2>/dev/null || true)"; kbver="${kbver:-0}"
line="$(python3 "$PY" event "$id" "$etype" "$topic" "$payload" "$kbver" "$trace_id")"

mkdir -p "$BUS/inbox"
exec 9>>"$BUS/inbox/$id.jsonl"
flock 9
printf '%s\n' "$line" >&9
echo "appended $etype/$topic for $id"
