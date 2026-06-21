#!/usr/bin/env bash
# Basket construction review (2026-06-15): does de-concentrating the parking vehicle help/hurt
# V2.3 at scale? 3 schemes (ew/namecap/sectorcap) x {500,200}B, V0 policy {3:0.7} (isolate the
# construction effect). capwt baseline already done (500B 18.83 / 200B 21.28). Each = audited
# pt_v23 harness (self-check inside). timeout 1000s/run breaks any hang -> retry fresh.
set -u
cd "C:/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude"
LOGDIR="data/parksweep_logs"; mkdir -p "$LOGDIR"
export PYTHONUNBUFFERED=1

run_one () {
  local nav="$1"; local wt="$2"; local log="$LOGDIR/wt_${wt}_nav${nav}.log"
  echo "=== $(date '+%H:%M:%S')  NAV=${nav}B  BASKET_WT=${wt}  -> $log ==="
  NAV_TOTAL_B="$nav" ETF_LIQ=custompitg PARK_STATES="3:0.7" BASKET_WT="$wt" \
    timeout 1000 python -u pt_v23_audit_2014.py v23a none postbull 0.0 edge > "$log" 2>&1
  if ! grep -q "^Done\." "$log"; then
    echo "  !! no clean finish (timeout/crash), retry once fresh ..."
    NAV_TOTAL_B="$nav" ETF_LIQ=custompitg PARK_STATES="3:0.7" BASKET_WT="$wt" \
      timeout 1000 python -u pt_v23_audit_2014.py v23a none postbull 0.0 edge > "$log" 2>&1
  fi
  grep -E "weight=|CAGR [0-9]|selfcheck|MaxDD" "$log" | tail -5
  echo "    done $(date '+%H:%M:%S')"
}

# 500B first (construction effect largest where parking heaviest), then 200B
for combo in "500 ew" "500 namecap" "500 sectorcap" "200 ew" "200 namecap" "200 sectorcap"; do
  set -- $combo
  run_one "$1" "$2"
  sleep 3
done
echo "ALL BASKET_WT DONE"
