#!/usr/bin/env bash
# G6 re-pin R3 A/B trên CACHE đã verified (job Taylor_20260722_112850).
# Lệnh pin nguyên văn (results_registry.md dòng 2800) + $DNA_PYEXE + BQ_LOCAL_CACHE bắt buộc;
# EXP_TAG giữ CẢ HAI chân khỏi CSV canonical (coding_guidelines.md §8).
set -u
cd /home/trido/thanhdt/WorkingClaude
source ./wc_env.sh
OUT=data/g6_repin

run_leg() {  # $1=UNIVERSE_SRC  $2=EXP_TAG  $3=logfile
  env BQ_LOCAL_CACHE=1 BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap \
      BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
      UNIVERSE_SRC="$1" EXP_TAG="$2" \
      "$DNA_PYEXE" pt_v23_audit_2014.py v23a none postbull 0 edge > "$OUT/$3" 2>&1
  echo "EXIT=$? ($1/$2)" >> "$OUT/$3"
}

run_leg prune repinR3control_c cache_control.log
run_leg pit   repinR3pit_c     cache_pit.log
touch $OUT/DONE_CACHE_AB
