#!/bin/bash
# rerun-groupB leg runner — job Taylor_20261008_172556 (copy of repin_park0_dep1m_20261008/run_leg.sh; OUT + BASKET_WDUMP only).
# Every env below except the ones on the command line is copied VERBATIM from the anchor-R3 pin
# command (job Taylor_20260927_131635), same as W2/Q2's run_leg.sh. Usage: run_leg.sh <TAG> KEY=VAL...
# CODE from the repin worktree (tier dep1m); DATA/CWD from canonical WC — identical to the pin cmd.
SRC=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-repin-dep1m-2809/WorkingClaude
WC=/home/trido/thanhdt/WorkingClaude
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/rerun_groupB_fixed_20261009/logs
TAG="$1"; shift
cd "$WC" || exit 9
export WORKDIR_8L="$WC"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env BASKET_WDUMP=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/rerun_groupB_fixed_20261009/w/$TAG.csv "$@" \
BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$SRC/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
