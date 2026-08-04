#!/bin/bash
# Aggressive-family sweep (job Taylor_20260804_012953).
#   run_agg.sh <tag> <PARK_STATES> <PARK_BAND>
# Cung cau hinh voi vong 2x2 (§E) de so sanh duoc: AUDIT_END=2026-06-19, NAV=50B,
# universe_pit, BQ_LOCAL_CACHE=bq_cache_asof20260729_postrestate, threads=1.
# Chan A0 (3:0.7 / 0.005) la GATE no-op: phai tai lap md5 cua chan A vong truoc.
set -u
cd /home/trido/thanhdt/WorkingClaude || exit 1
# shellcheck disable=SC1091
source ./wc_env.sh
TAG="$1"; PSTATES="$2"; PBAND="$3"
OUT=mike/agents/Taylor/exp_park_jit_20260803
env PARK_JIT=on PARK_PREFILL=on PARK_BAND="$PBAND" PARK_STATES="$PSTATES" \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
  AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
  "$DNA_PYEXE" "$OUT/run_leg2.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG PARK_STATES=$PSTATES PARK_BAND=$PBAND)" >> "$OUT/$TAG.log"
