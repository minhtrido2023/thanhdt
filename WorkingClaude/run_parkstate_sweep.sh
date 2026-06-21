#!/usr/bin/env bash
# =============================================================================
# Park-state experiment (2026-06-14): does extending idle-cash parking beyond
# NEUTRAL into BULL/EX-BULL help at large NAV (where the 2 books cap ~35% stk%)?
# Vehicle=custompitg, deploy config (v23a + postbull HARD-BLOCK[shrink0] + edge).
# Each run = the audited pt_v23_audit_2014.py harness (cash-flow self-check +
# members_match INSIDE). Sequential, fresh process each (dodges 0xC0000142
# spawn-exhaustion, handoff §6), one retry on failure.
#   policies: V0 "3:0.7" (NEUTRAL-only, prod) | V1 +BULL1.0 | V2 +BULL0.7 | V3 +BULL1.0+EXBULL0.5
#   matrix:   full 4 @ {200,500}B + safety pair (V0,V1) @ 50B; baseline@500 already done.
# =============================================================================
set -u
cd "C:/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude"
LOGDIR="data/parksweep_logs"
mkdir -p "$LOGDIR"

run_one () {
  local nav="$1" park="$2" log="$3"
  echo "=== $(date '+%H:%M:%S')  NAV=${nav}B  PARK=${park}  -> $log ==="
  NAV_TOTAL_B="$nav" ETF_LIQ=custompitg PARK_STATES="$park" \
    python pt_v23_audit_2014.py v23a none postbull 0.0 edge > "$log" 2>&1
  if ! grep -q "^Done\." "$log"; then
    echo "  !! no clean finish, retry once (fresh process) ..."
    NAV_TOTAL_B="$nav" ETF_LIQ=custompitg PARK_STATES="$park" \
      python pt_v23_audit_2014.py v23a none postbull 0.0 edge > "$log" 2>&1
  fi
  grep -E "CAGR [0-9]|selfcheck|MaxDD" "$log" | tail -4
}

COMBOS=(
  "50 3:0.7"
  "50 3:0.7,4:1.0"
  "200 3:0.7"
  "200 3:0.7,4:1.0"
  "200 3:0.7,4:0.7"
  "200 3:0.7,4:1.0,5:0.5"
  "500 3:0.7,4:1.0"
  "500 3:0.7,4:0.7"
  "500 3:0.7,4:1.0,5:0.5"
)
for combo in "${COMBOS[@]}"; do
  set -- $combo
  nav="$1"; park="$2"
  tag=$(echo "$park" | tr ':,.' 'p-d')
  run_one "$nav" "$park" "$LOGDIR/nav${nav}_${tag}.log"
done
echo "ALL PARKSWEEP DONE"
