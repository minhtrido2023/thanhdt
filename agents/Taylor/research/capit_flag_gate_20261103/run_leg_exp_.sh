#!/bin/bash
# capit-flag-gate leg runner — job Taylor_20261103_024121. Env copied VERBATIM from the park0 pin
# (repin_park0_dep1m_20261008/run_leg.sh) minus IDLE_CARRY (pin0% = carry off; knob not on main).
# Usage: run_leg_exp_.sh <TAG> <script.py> KEY=VAL...
WC=/home/trido/thanhdt/WorkingClaude
RD=$WC/mike/agents/Taylor/research/capit_flag_gate_20261103
TAG="$1"; SCRIPT="$2"; shift 2
cd "$WC" || exit 9
export WORKDIR_8L="$WC" PATH="$PATH:/home/trido/google-cloud-sdk/bin" CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python TZ=Asia/Ho_Chi_Minh
env "$@" CAPIT_FLAG_FILE=$RD/pit_flags_eventdates_exp_.csv \
BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 \
BASKET_CA_SNAPSHOT=$WC/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$SCRIPT" v23a none postbull 0 edge > "$RD/logs/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $SCRIPT $*)" >> "$RD/logs/$TAG.log"
