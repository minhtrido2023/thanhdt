#!/bin/bash
# GĐ1 live-gap leg runner (job Taylor_20261112_104204). Env cố định copy từ lệnh pin R3 (registry
# "2026-10-08", repin_park0_dep1m_20261008/run_leg.sh). Usage:
#   run_leg.sh <TAG> <CODE_DIR> <WORKDIR(sandbox|WC)> KEY=VAL...   (KEY=VAL ghi đè mặc định bên dưới)
TAG="$1"; CODE="$2"; WD="$3"; shift 3
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_phase1_20261112/logs
cd "$WD" || exit 9
export WORKDIR_8L=/home/trido/thanhdt/WorkingClaude PT_WORKDIR="$WD"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin" CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python TZ=Asia/Ho_Chi_Minh
START=$(date +%s)
env BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" "$@" \
  $DNA_PYEXE "$CODE/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? WALL=$(( $(date +%s)-START ))s ($TAG code=$CODE wd=$WD $*)" >> "$OUT/$TAG.log"
