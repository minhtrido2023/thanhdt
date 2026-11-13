#!/bin/bash
# Luồng A9 (job Taylor_20261113_153627; copy A7 + 2 sửa theo verdict A7 (e)): (1) rev-parse code lấy LÚC BẮT ĐẦU (và
# kiểm lại lúc kết thúc — lệch = lỗi, exit 11); (2) unset cả SIG_ADV_MIN/SELL_CAP_LOG_OUT ngoài các chân cần.
# Usage: run_leg.sh <TAG> <adj> KEY=VAL...  Env cố định = A5/A7 (cache asof0729_postrestate, NAV 50B mặc định,
# ETF_LIQ custompitg, AUDIT_END 06-19, threads=1, TZ ICT, CA snapshot 0927, park 0, namecap/yieldcombo, IDLE_CARRY_TIER=off).
set -u
A9=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_exec_A9
CODE=/home/trido/thanhdt/wt-livegapA7-1113/WorkingClaude
TAG="$1"; LD="$2"; shift 2
SB=$A9/sb/c_$LD; [ -z "$(git -C "$CODE" status --porcelain)" ] || { echo "worktree bẩn" >&2; exit 7; }
[ "$(readlink -f "$SB/pt_v23_audit_2014.py")" = "$CODE/pt_v23_audit_2014.py" ] || { echo "sandbox lệch" >&2; exit 9; }
REV0=$(git -C "$CODE" rev-parse HEAD); BR0=$(git -C "$CODE" rev-parse --abbrev-ref HEAD)
cd "$SB" || exit 9
export WORKDIR_8L=/home/trido/thanhdt/WorkingClaude PT_WORKDIR="$SB"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin" CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python TZ=Asia/Ho_Chi_Minh
unset LIQ_ZERO_BLOCK LAG_ADV_SRC LAG_ADV_MINP IDLE_CARRY_TIER NAV_TOTAL_B SELL_ADV_CAP SELL_ADV_MAXCARRY SIG_ADV_MIN SELL_CAP_LOG_OUT
START=$(date +%s)
env BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=off NAV_TOTAL_B=50 \
  BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" SELL_CAP_LOG_OUT="$A9/ledgers/sellcap_$TAG.csv" "$@" \
  /usr/bin/time -v $DNA_PYEXE "$SB/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$A9/logs/$TAG.log" 2>&1
RC=$?
REV1=$(git -C "$CODE" rev-parse HEAD); [ "$REV0" = "$REV1" ] || { echo "CODE ĐỔI GIỮA CHỪNG $REV0 -> $REV1" >> "$A9/logs/$TAG.log"; RC=11; }
OUTCSV=$(ls -t "$SB"/data/v23_golive_audit_2014_now_*_exp_${TAG}_univpit*.csv 2>/dev/null | head -1)
[ -n "$OUTCSV" ] && mv "$OUTCSV" "$A9/ledgers/" && OUTCSV="$A9/ledgers/$(basename "$OUTCSV")" && MD5=$(md5sum "$OUTCSV" | cut -c1-32) || MD5=NONE
echo "EXIT=$RC WALL=$(( $(date +%s)-START ))s MD5=$MD5 CSV=$(basename "${OUTCSV:-none}") CODE=$CODE@${REV0:0:9}($BR0) SB=$SB ARGS=$*" >> "$A9/logs/$TAG.log"
