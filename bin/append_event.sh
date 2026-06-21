#!/usr/bin/env bash
# append_event.sh <agent_id> <event_type> <topic> <payload_json_or_string>
# Appends one JSONL event to bus/inbox/<agent_id>.jsonl (append-only, one file per child).
# event_id is a real UUID; flock guards this child's own file only (no cross-child contention).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUS="$ROOT/bus"
PY="$ROOT/bin/mike_json.py"

id="${1:?usage: append_event.sh <agent_id> <event_type> <topic> <payload>}"
etype="${2:?event_type required (finding|status|question|answer|decision|error)}"
topic="${3:?topic required}"
payload="${4:?payload required (json object/array, or plain string)}"

kbver="$(tr -dc '0-9' < "$ROOT/kb/version.txt" 2>/dev/null || true)"; kbver="${kbver:-0}"
line="$(python3 "$PY" event "$id" "$etype" "$topic" "$payload" "$kbver")"

mkdir -p "$BUS/inbox"
exec 9>>"$BUS/inbox/$id.jsonl"
flock 9
printf '%s\n' "$line" >&9
echo "appended $etype/$topic for $id"
