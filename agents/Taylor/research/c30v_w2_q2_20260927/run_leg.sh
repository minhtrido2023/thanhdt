#!/bin/bash
# W2/Q2 leg runner — job Taylor_20260927_141318.
# Every env below except the ones passed on the command line is copied VERBATIM from the anchor-R3
# pin command (job Taylor_20260927_131635). Usage:  run_leg.sh <TAG> KEY=VAL ...
WC=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-w2q2-2709/WorkingClaude
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_w2_q2_20260927/logs
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
NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$WC/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
