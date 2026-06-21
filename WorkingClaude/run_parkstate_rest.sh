#!/usr/bin/env bash
# Remaining 4 park-state combos after the hang at run 6 (fresh shell per handoff §6).
# Done already: V0/V1@50, V0/V1/V2@200, V0@500. Remaining: V3@200, V1/V2/V3@500.
# Fixes vs first orchestrator: proper log tag (no broken `tr`), python -u (unbuffered ->
# realtime log flush), 3s inter-run pause to let Windows reclaim handles (anti spawn-exhaustion).
set -u
cd "C:/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude"
LOGDIR="data/parksweep_logs"; mkdir -p "$LOGDIR"
export PYTHONUNBUFFERED=1

run_one () {
  local nav="$1" park="$2"
  local tag="${park//[:,.]/_}"
  local log="$LOGDIR/nav${nav}_park${tag}.log"
  echo "=== $(date '+%H:%M:%S')  NAV=${nav}B  PARK=${park}  -> $log ==="
  NAV_TOTAL_B="$nav" ETF_LIQ=custompitg PARK_STATES="$park" \
    python -u pt_v23_audit_2014.py v23a none postbull 0.0 edge > "$log" 2>&1
  if ! grep -q "^Done\." "$log"; then
    echo "  !! no clean finish, retry once (fresh process) ..."
    NAV_TOTAL_B="$nav" ETF_LIQ=custompitg PARK_STATES="$park" \
      python -u pt_v23_audit_2014.py v23a none postbull 0.0 edge > "$log" 2>&1
  fi
  grep -E "CAGR [0-9]|selfcheck|MaxDD" "$log" | tail -4
  echo "    done $(date '+%H:%M:%S')"
}

COMBOS=(
  "200 3:0.7,4:1.0,5:0.5"
  "500 3:0.7,4:1.0"
  "500 3:0.7,4:0.7"
  "500 3:0.7,4:1.0,5:0.5"
)
for combo in "${COMBOS[@]}"; do
  set -- $combo
  run_one "$1" "$2"
  sleep 3
done
echo "ALL REST DONE"
