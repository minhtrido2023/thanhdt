#!/bin/bash
# ABLATION JIT-unpark v2 (job Taylor_20260803_171515).
# v1 (run_jit.sh) was a silent NO-OP: PYTHONPATH loses to pt_v23's own
# `sys.path.insert(0, WORKDIR)`. v2 goes through run_leg.py, which pre-seeds
# sys.modules. Chan A (control) PHAI tai lap CAGR 28,86% / NAV 1.178,01B.
# Production files unmodified; only this directory's engine copy is patched.
set -u
cd /home/trido/thanhdt/WorkingClaude || exit 1
# shellcheck disable=SC1091
source ./wc_env.sh
TAG="$1"; JIT="$2"
OUT=mike/agents/Taylor/exp_park_jit_20260803
env PARK_JIT="$JIT" \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
  PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
  "$DNA_PYEXE" "$OUT/run_leg.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG PARK_JIT=$JIT)" >> "$OUT/$TAG.log"
