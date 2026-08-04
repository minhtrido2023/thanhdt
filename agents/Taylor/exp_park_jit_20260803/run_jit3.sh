#!/bin/bash
# ABLATION v3 (job Taylor_20260803_180602) — 2x2 tach L1 (khoi 4c PREFILL_STATE_REBAL)
# khoi L2 (JIT_FOR_BA_BUY). Chan A phai tai lap md5 7d053e62... (gate no-op cua switch moi).
set -u
cd /home/trido/thanhdt/WorkingClaude || exit 1
# shellcheck disable=SC1091
source ./wc_env.sh
TAG="$1"; JIT="$2"; PREFILL="$3"
OUT=mike/agents/Taylor/exp_park_jit_20260803
env PARK_JIT="$JIT" PARK_PREFILL="$PREFILL" \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
  PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
  "$DNA_PYEXE" "$OUT/run_leg.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG PARK_JIT=$JIT PARK_PREFILL=$PREFILL)" >> "$OUT/$TAG.log"
