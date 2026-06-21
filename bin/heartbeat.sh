#!/usr/bin/env bash
# heartbeat.sh <agent_id> [current_task] [status]
# Writes bus/registry/<agent_id>.json atomically (temp-file + rename on the same filesystem).
# status defaults to "working"; consolidator's fleet_status flips stale entries to "dead".
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUS="$ROOT/bus"
PY="$ROOT/bin/mike_json.py"

id="${1:?usage: heartbeat.sh <agent_id> [current_task] [status]}"
task="${2:-}"
status="${3:-working}"

mkdir -p "$BUS/registry"
tmp="$(mktemp "$BUS/registry/.$id.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
python3 "$PY" heartbeat "$id" "$task" "$status" > "$tmp"
mv -f "$tmp" "$BUS/registry/$id.json"
trap - EXIT
