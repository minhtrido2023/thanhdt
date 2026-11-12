#!/bin/bash
# GĐ1 vòng 3 (job Taylor_20261112_122855). Usage: run_leg.sh <TAG> KEY=VAL...  (chạy trong sandbox đóng băng sb/,
# trần RAM 5G/chân qua systemd-run scope — §32). TRACE=1 => open_trace (ghi mọi file mở).
TAG="$1"; shift
R=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_phase1c_20261112; S=$R/sb; OUT=$R/logs
cd "$S" || exit 9
export WORKDIR_8L=/home/trido/thanhdt/WorkingClaude PT_WORKDIR="$S"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin" CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python TZ=Asia/Ho_Chi_Minh
PRE=(); [ "${TRACE:-0}" = 1 ] && { rm -f "$OUT/$TAG.opened"; PRE=("$R/../live_gap_phase1b_20261112/open_trace.py" "$OUT/$TAG.opened"); }
START=$(date +%s)
systemd-run --user --scope -q -p MemoryMax=5G env BASKET_CA_SNAPSHOT=$S/data/snapshots/corp_action_share_20260927.parquet \
  BQ_LOCAL_CACHE=$S/data/bq_cache_asof20261111 BQ_CACHE_THREADS=1 BASKET_WT=namecap BASKET_SELECT=yieldcombo \
  PARK_STATES=3:0.0 NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-11-12 EXP_TAG="$TAG" "$@" \
  /usr/bin/time -v $DNA_PYEXE "${PRE[@]}" "$S/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? WALL=$(( $(date +%s)-START ))s ($TAG sb=$S code=$(readlink -f $S/pt_v23_audit_2014.py) $*)" >> "$OUT/$TAG.log"
