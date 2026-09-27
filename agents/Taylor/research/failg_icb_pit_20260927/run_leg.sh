#!/bin/bash
# Pinned R3 environment, verbatim from research/oshares_weight_exdate_20260927/run_leg.sh (the
# TICKET-1 pin, now merged to main), with ONE substitution: BQ_LOCAL_CACHE points at this job's
# symlink farm so only fa_ratings_8l.parquet differs between legs. Engine code = canonical tree
# (== main @f2cfb124 == the code the 24,42% pin was produced with); this branch changes only
# rating_8l_history.py, which the engine never imports -> no wrapper needed.
# $1 = leg tag (ctl_anyvalue | new_icbpit)
WC=/home/trido/thanhdt/WorkingClaude
OUT=$WC/mike/agents/Taylor/research/failg_icb_pit_20260927
TAG="$1"
cd "$WC" || exit 9
export WORKDIR_8L="$WC"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env \
BASKET_CA_SNAPSHOT=$WC/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE="$OUT/cache_$TAG" BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="failg_$TAG" \
$DNA_PYEXE "$WC/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG)" >> "$OUT/$TAG.log"
