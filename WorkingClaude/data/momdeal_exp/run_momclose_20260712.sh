#!/bin/bash
# MOM-channel closure measurement v2 (CACHE vintage = pin) — job Taylor_20260712_012515
set -u
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
run() {
  local drop="$1" log="$2"
  echo "=== START $drop $(date -u +%FT%TZ) ===" > "$log"
  env BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
      PARK_STATES="3:0.7" AUDIT_END=2026-06-19 BAL_DROP_TIERS="$drop" \
      $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge >> "$log" 2>&1
  echo "=== EXIT $? $(date -u +%FT%TZ) ===" >> "$log"
}
run "none" data/momdeal_exp/run_cache_dropnone.log
run "MOMENTUM_N,MOMENTUM_S" data/momdeal_exp/run_cache_dropMOMN-MOMS.log
run "MEGA,MOMENTUM,MOMENTUM_N,MOMENTUM_S" data/momdeal_exp/run_cache_dropFAMILY.log
touch data/momdeal_exp/ALL_RUNS_DONE
