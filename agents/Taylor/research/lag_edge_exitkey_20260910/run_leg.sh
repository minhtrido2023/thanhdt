#!/bin/bash
# Pinned R3 environment (verbatim from research/lag_repin_20260803/run_repin.sh, same as
# research/bal_edge_gate_20260910/run_leg.sh).
# $1 = EXP_TAG ; $2 = engine script ; rest = extra env assignments
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; ENGINE="$2"; shift 2
OUT=mike/agents/Taylor/research/lag_edge_exitkey_20260910
env "$@" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$ENGINE" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
