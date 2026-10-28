#!/bin/bash
# job Taylor_20261020_122917 — ban sao run_leg.sh (survivorship_replay_20261020), CHI doi OUT; SRC = eng/ (ban sao engine).
# Usage: run_leg.sh <TAG> KEY=VAL...   (leg env + ZVF_MODE/V3 knobs)
O=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_volzero_20261020
for _a in "$@"; do case "$_a" in ENGDIR=*) ENGDIR="${_a#ENGDIR=}";; esac; done
SRC=$O/${ENGDIR:-eng}; CACHE=data/bq_cache_asof20260729_postrestate; TAG="$1"; shift 1
WC=/home/trido/thanhdt/WorkingClaude
OUT=$O/logs
cd "$WC" || exit 9
export WORKDIR_8L="$WC"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env "$@" \
BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE="$CACHE" BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$SRC/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $SRC $CACHE $*)" >> "$OUT/$TAG.log"
