#!/bin/bash
# A/B FAIL-C: MOT BIEN = NHAN cot index cua chuoi edge-health.
#   CONTROL: EDGE_HEALTH_CSV -> data/lag_edge_health.csv.bak_20260927_prefailc (header entry,ret,mean12,win12,n12)
#            => engine fallback _eh_key="entry"  (= dung file MA PIN ae81bd47 da doc that)
#   NEW    : mac dinh data/lag_edge_health.csv (co known_date) => _eh_key="known_date"
# 5 cot so hoc cua 2 file da verify BYTE-IDENTICAL (md5 d6ac4be1294cc26650af9b61ea20dd1e)
# => khac biet duy nhat co the xay ra la NHAN index. Moi env khac copy nguyen van tu run_pin.sh (park 0,30).
WC=/home/trido/thanhdt/WorkingClaude
OUT=$WC/mike/agents/Taylor/research/failc_ab_20260927
TAG="$1"; shift
cd "$WC" || exit 9
export WORKDIR_8L="$WC"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env "$@" \
BASKET_CA_SNAPSHOT=$WC/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.3" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$WC/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
