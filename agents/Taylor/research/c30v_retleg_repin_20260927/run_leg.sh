#!/bin/bash
# Pinned R3 environment, verbatim from research/lag_edge_exitkey_20260910/run_leg.sh
# (itself verbatim from lag_repin_20260803/run_repin.sh), run inside the WORKTREE
# /home/trido/thanhdt/wt-c30v-retfix so the canonical tree stays untouched.
# NOTE: we deliberately do NOT `source wc_env.sh` — it ends with `cd "$WORKDIR_8L"`
# (= the CANONICAL tree) which would silently run the UNFIXED engine. Env is set
# explicitly instead; that is the whole point of running from a worktree.
# $1 = EXP_TAG ; rest = extra env assignments (e.g. BASKET_RETURN_OSHARES=legacy)
WT=/home/trido/thanhdt/wt-c30v-retfix/WorkingClaude
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_retleg_repin_20260927
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
