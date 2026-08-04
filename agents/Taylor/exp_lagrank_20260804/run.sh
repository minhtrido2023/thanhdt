#!/bin/bash
# LAG forward-window ranking research — job Taylor_20260804_051145.
# $1 = TAG (khong bao gio trung ten canonical), $2 = ENGINE (path .py), phan con lai = env KEY=VAL
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; ENGINE="$2"; shift 2
OUT=mike/agents/Taylor/exp_lagrank_20260804
env "$@" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$ENGINE" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $ENGINE $*)" >> "$OUT/$TAG.log"
