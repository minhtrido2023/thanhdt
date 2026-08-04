#!/bin/bash
# Nhu run_leg.sh nhung them LIQ_ZERO_BLOCK (chan L1 = engine da chan ADV<=0) — do PHAN GIA TANG
# cua gate do-lon 2 ty TREN NEN gate ADV>0 da biet.
#   $1 = TAG, $2 = nguong VND, $3 = LIQ_ZERO_BLOCK (lag|"")
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; MIN="$2"; LZB="$3"
OUT=mike/agents/Taylor/exp_lag_advgate_20260804
PYTHONPATH=/home/trido/thanhdt/WorkingClaude \
LAG_ADV_MIN_VND="$MIN" LIQ_ZERO_BLOCK="$LZB" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$OUT/pt_v23_advgate.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG min=$MIN lzb=$LZB)" >> "$OUT/$TAG.log"
