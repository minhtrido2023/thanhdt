#!/bin/bash
# Pinned R3 environment for TICKET 1 (job Taylor_20260927_043542), verbatim from
# research/c30v_retleg_repin_20260927/run_leg.sh + run_wt.sh (itself verbatim from the R3 pin),
# run inside the worktree /home/trido/thanhdt/wt-c30v-wexdate so the canonical tree is untouched.
# The engine is driven through run_wt_leg.py so the WORKTREE custom_basket.py is the one that runs
# (pt_v23_audit_2014.py hardcodes sys.path to the canonical tree -> silent no-op otherwise, §29).
# BASKET_CA_SNAPSHOT pins the corp-action vintage: that table is upserted in place.
# $1 = EXP_TAG ; rest = extra env assignments (e.g. BASKET_OSHARES_STEP=quarter).
WT=/home/trido/thanhdt/wt-c30v-wexdate/WorkingClaude
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/oshares_weight_exdate_20260927
TAG="$1"; shift
cd "$WT" || exit 9
export WORKDIR_8L="$WT"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env "$@" \
BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$OUT/run_wt_leg.py" "$WT" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
