#!/bin/bash
# Pinned R3 environment, verbatim from research/c30v_retleg_repin_20260927/run_leg.sh, run inside
# the WORKTREE /home/trido/thanhdt/wt-lagedge-causal so the canonical tree stays untouched.
# NOTE: pt_v23_audit_2014.py:41 hardcodes WORKDIR=canonical, so every IMPORT (custom_basket,
# simulate_holistic_nav) comes from the canonical tree — which already carries the merged
# custom30V return-leg fix (a808a613). Only the top-level engine script is the worktree copy.
# $1 = EXP_TAG ; rest = extra env assignments (e.g. EDGE_HEALTH_CSV=...)
WT=/home/trido/thanhdt/wt-lagedge-causal/WorkingClaude
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/lagedge_causal_20260927
TAG="$1"; shift
cd "$WT" || exit 9
export WORKDIR_8L="$WT"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env "$@" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$WT/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
