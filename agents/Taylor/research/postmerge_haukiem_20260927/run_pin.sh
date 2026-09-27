#!/bin/bash
# PIN R3 sau merge ticket 1 — chay tren MAIN CANONICAL (code da merge @f2cfb124+).
# Env verbatim tu research/oshares_weight_exdate_20260927/run_leg.sh, BO phan worktree:
# main la canonical nen pt_v23_audit_2014.py hardcode sys.path vao dung cay nay.
# $1 = EXP_TAG ; rest = extra env assignments.
WC=/home/trido/thanhdt/WorkingClaude
OUT=$WC/mike/agents/Taylor/research/postmerge_haukiem_20260927
TAG="$1"; shift
cd "$WC" || exit 9
export WORKDIR_8L="$WC"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env "$@" \
BASKET_CA_SNAPSHOT=$WC/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$WC/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
