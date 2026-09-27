#!/bin/bash
# Same pinned env as run_leg.sh, but engine is driven through run_wt_leg.py so the WORKTREE
# custom_basket.py is the one that runs. $1 = EXP_TAG ; rest = extra env assignments.
WT=/home/trido/thanhdt/wt-c30v-retfix/WorkingClaude
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_retleg_repin_20260927
TAG="$1"; shift
cd "$WT" || exit 9
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env "$@" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$OUT/run_wt_leg.py" "$WT" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
