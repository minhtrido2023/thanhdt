#!/bin/bash
# ABLATION JIT-unpark (job Taylor_20260803_165225) — chan control PHAI tai lap 28,86% (pin 08-03).
# Engine pt_v23_audit_2014.py = BAN PRODUCTION khong sua; chi simulate_holistic_nav.py trong
# thu muc nay (ban sao nghien cuu) duoc gate them env PARK_JIT, uu tien qua PYTHONPATH.
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; JIT="$2"
OUT=mike/agents/Taylor/exp_park_jit_20260803
env PYTHONPATH="$OUT" PARK_JIT="$JIT" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG PARK_JIT=$JIT)" >> "$OUT/$TAG.log"
