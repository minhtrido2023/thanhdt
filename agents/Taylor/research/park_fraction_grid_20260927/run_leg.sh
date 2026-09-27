#!/bin/bash
# Park-fraction grid leg. Copy of c30v_hau_kiem_20260927/run_main2.sh with the corp-action
# snapshot PINNED, so the vintage is reproducible (run_main2.sh read LIVE BQ).
# "$@" is LAST on purpose: run_main.sh put PARK_STATES after `env "$@"`, which made every
# caller override a SILENT no-op (`env` keeps the last assignment). Verify the log line
# "parking policy (cash_etf_states)" on every leg.
# $1 = EXP_TAG ; rest = extra env assignments (must include PARK_STATES=3:x)
WT=/home/trido/thanhdt/WorkingClaude
OUT=$WT/mike/agents/Taylor/research/park_fraction_grid_20260927
TAG="$1"; shift
cd "$WT" || exit 9
export WORKDIR_8L="$WT"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
AUDIT_END=2026-06-19 \
BASKET_CA_SNAPSHOT=data/snapshots/corp_action_share_20260927.parquet \
EXP_TAG="$TAG" "$@" \
$DNA_PYEXE "$WT/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
