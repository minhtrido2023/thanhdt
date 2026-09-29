#!/bin/bash
# Moi truong PIN R3 y nguyen (repin_park030_20260927/run_pin.sh, PARK_STATES=3:0.3 = production
# park 0,30 user chot 2026-09-27 15:48 ICT) — doi DUNG MOT bien: chan park.
WC=/home/trido/thanhdt/WorkingClaude
OUT=$WC/mike/agents/Taylor/research/c30v_position_replay_20260927
LEG="$1"
cd "$WC" || exit 9
export WORKDIR_8L="$WC"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env \
BASKET_CA_SNAPSHOT=$WC/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.3" AUDIT_END=2026-06-19 EXP_TAG="ab_park_${LEG}" \
$DNA_PYEXE "$OUT/run_ab.py" "$LEG" v23a none postbull 0 edge > "$OUT/ab_${LEG}.log" 2>&1
echo "EXIT=$?" >> "$OUT/ab_${LEG}.log"
