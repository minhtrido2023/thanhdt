#!/bin/bash
# CAPIT ENTRY-gate A/B legs (job Taylor_20260801_082823). Same pinned config as the qexit study
# => the ctrl leg reproduces the R3 pin (27.60/1.84/-17.5/1.58) exactly.
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
ENGINE="$1"; TAG="$2"
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
EXP_TAG="$TAG" AUDIT_EXP_TAG="$TAG" \
$DNA_PYEXE "$ENGINE" v23a none postbull 0 edge \
  > data/fscore_review_20260801/$TAG.log 2>&1
echo "EXIT=$? ($TAG engine=$ENGINE)" >> data/fscore_review_20260801/$TAG.log
