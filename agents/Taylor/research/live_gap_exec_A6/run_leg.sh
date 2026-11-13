#!/bin/bash
# Luồng A6 (job Taylor_20261113_075112). Usage: run_leg.sh <TAG> <adj|vint> KEY=VAL...
# MỘT cây code: wt-livegapA6-1113 (nhánh research/live-gap-A6-carry-20261113). Env cố định = run_leg.sh A5
# (cache asof0729_postrestate, NAV 50B mặc định, ETF_LIQ custompitg, AUDIT_END 06-19, threads=1, TZ ICT,
# CA snapshot 0927, park 0, namecap/yieldcombo, IDLE_CARRY_TIER=off). Mọi ghi đè (IDLE_CARRY_TIER, NAV_TOTAL_B,
# PARK_STATES, LIQ_ZERO_BLOCK, LAG_ADV_SRC) truyền qua args — args đặt SAU mặc định nên thắng.
set -u
A6=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_exec_A6
CODE=/home/trido/thanhdt/wt-livegapA6-1113/WorkingClaude
TAG="$1"; LD="$2"; shift 2
SB=$A6/sb/c_$LD; [ -z "$(git -C "$CODE" status --porcelain)" ] || { echo "worktree bẩn" >&2; exit 7; }
[ "$(readlink -f "$SB/pt_v23_audit_2014.py")" = "$CODE/pt_v23_audit_2014.py" ] || { echo "sandbox lệch" >&2; exit 9; }
cd "$SB" || exit 9
export WORKDIR_8L=/home/trido/thanhdt/WorkingClaude PT_WORKDIR="$SB"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin" CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python TZ=Asia/Ho_Chi_Minh
unset LIQ_ZERO_BLOCK LAG_ADV_SRC LAG_ADV_MINP IDLE_CARRY_TIER NAV_TOTAL_B
START=$(date +%s)
env BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=off NAV_TOTAL_B=50 \
  BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" "$@" \
  /usr/bin/time -v $DNA_PYEXE "$SB/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$A6/logs/$TAG.log" 2>&1
RC=$?
OUTCSV=$(ls -t "$SB"/data/v23_golive_audit_2014_now_*_exp_${TAG}_univpit*.csv 2>/dev/null | head -1)
[ -n "$OUTCSV" ] && mv "$OUTCSV" "$A6/ledgers/" && OUTCSV="$A6/ledgers/$(basename "$OUTCSV")" && MD5=$(md5sum "$OUTCSV" | cut -c1-32) || MD5=NONE
echo "EXIT=$RC WALL=$(( $(date +%s)-START ))s MD5=$MD5 CSV=$(basename "${OUTCSV:-none}") CODE=$CODE@$(git -C "$CODE" rev-parse --short HEAD) SB=$SB ARGS=$*" >> "$A6/logs/$TAG.log"
