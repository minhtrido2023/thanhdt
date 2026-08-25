#!/bin/bash
# BULL parking sweep — job Taylor_20260825_142021.
# Tai su dung y het harness F1 (agg_F1_t80) cua exp_park_jit_20260803: PARK_JIT/PARK_PREFILL=on,
# PARK_BAND=0.005, chi doi PARK_STATES them entry state=4 (BULL).
#   run_bullpark.sh <tag> <PARK_STATES>
set -u
cd /home/trido/thanhdt/WorkingClaude || exit 1
# shellcheck disable=SC1091
source ./wc_env.sh
TAG="$1"; PSTATES="$2"
LEG2=mike/agents/Taylor/exp_park_jit_20260803/run_leg2.py
OUT=mike/agents/Taylor/exp_lag_bull_park_20260825
env PARK_JIT=on PARK_PREFILL=on PARK_BAND=0.005 PARK_STATES="$PSTATES" \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
  AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
  "$DNA_PYEXE" "$LEG2" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG PARK_STATES=$PSTATES)" >> "$OUT/$TAG.log"
