#!/bin/bash
# Chân PATCHED: env NGUYÊN VĂN pin (sexies), cwd canonical, engine canonical byte-identical,
# chỉ `custom_basket` bị thay bằng bản VÁ trong worktree (qua inject_patched_basket.py).
WC=/home/trido/thanhdt/WorkingClaude
WT=$WC/mike/agents/Taylor/wt-forensic-failclosed-2709/WorkingClaude
OUT=$WC/mike/agents/Taylor/research/forensic_failclosed_20260927
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
$DNA_PYEXE "$OUT/inject_patched_basket.py" "$WT/custom_basket.py" "$WC/pt_v23_audit_2014.py" \
  v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
