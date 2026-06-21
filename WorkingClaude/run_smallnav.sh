#!/usr/bin/env bash
# Live-production config (V0 {3:0.7} neutral-only parking, custompitg, v23a+postbull+edge)
# at SMALL NAV: 1 / 5 / 10 / 20 tỷ VND, to compare vs 50 tỷ (already = 25.87%).
# Question: below 50B, are the books in the unconstrained regime (≈ flat CAGR) or does it
# still vary? Fresh shell, python -u, retry-once. Each run = audited harness (self-check inside).
set -u
cd "C:/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude"
LOGDIR="data/parksweep_logs"; mkdir -p "$LOGDIR"
export PYTHONUNBUFFERED=1

run_one () {
  local nav="$1"
  local log="$LOGDIR/smallnav${nav}.log"
  echo "=== $(date '+%H:%M:%S')  NAV=${nav}B (live-prod V0 {3:0.7}) -> $log ==="
  NAV_TOTAL_B="$nav" ETF_LIQ=custompitg PARK_STATES="3:0.7" \
    python -u pt_v23_audit_2014.py v23a none postbull 0.0 edge > "$log" 2>&1
  if ! grep -q "^Done\." "$log"; then
    echo "  !! no clean finish, retry once ..."
    NAV_TOTAL_B="$nav" ETF_LIQ=custompitg PARK_STATES="3:0.7" \
      python -u pt_v23_audit_2014.py v23a none postbull 0.0 edge > "$log" 2>&1
  fi
  grep -E "CAGR [0-9]|selfcheck|MaxDD" "$log" | tail -4
  echo "    done $(date '+%H:%M:%S')"
}

for nav in 1 5 10 20; do run_one "$nav"; sleep 3; done
echo "ALL SMALLNAV DONE"
