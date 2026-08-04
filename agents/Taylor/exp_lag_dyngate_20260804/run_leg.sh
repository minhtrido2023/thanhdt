#!/bin/bash
# Gate kha-thi-thi-hanh (dynamic executability) cho book LAG — job Taylor_20260804_085248.
# Lenh pin R3 nguyen van + snapshot asof20260729_postrestate + threads=1 + $DNA_PYEXE.
#   $1 = TAG (vao ten CSV qua EXP_TAG => KHONG dung CSV canonical)
#   $2 = LAG_EXEC_GATE_K (0 = TAT = production)
#   $3 = LIQ_ZERO_BLOCK ("" hoac "lag")
#   $4 = NAV_TOTAL_B (50 = thang pin; 1 = thang NAV that dang chay live)
set -u
cd /home/trido/thanhdt/WorkingClaude || exit 1
# shellcheck disable=SC1091
source ./wc_env.sh
TAG="$1"; K="$2"; LZB="$3"; NAVB="$4"
OUT=mike/agents/Taylor/exp_lag_dyngate_20260804
env LAG_EXEC_GATE_K="$K" LIQ_ZERO_BLOCK="$LZB" \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B="$NAVB" ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
  PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
  "$DNA_PYEXE" "$OUT/run_leg.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG K=$K LIQ_ZERO_BLOCK='$LZB' NAV=${NAVB}B)" >> "$OUT/$TAG.log"
