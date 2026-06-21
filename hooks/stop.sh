#!/usr/bin/env bash
# stop.sh <agent_id>
# Fires when the child finishes a turn. Records a heartbeat so the consolidator knows
# the agent is alive. Kept side-effect-only (no context injection) to avoid stop-loops;
# the "write durable knowledge to the bus" instruction lives in CHILD_TEMPLATE.md instead.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/hooks/_resolve_id.sh"   # sets $id from $1 or stdin session_id; exits 0 if excluded

"$ROOT/bin/heartbeat.sh" "$id" "" working || true
exit 0
