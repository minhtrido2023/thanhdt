#!/bin/bash
# Luồng A pin ladder (job Taylor_20261112_151832). Usage: run_leg.sh <TAG> KEY=VAL...
# Env cố định = lệnh pin R3 park0 2026-10-08 (registry "2026-10-08"): BQ cache asof20260729_postrestate,
# NAV 50B, ETF_LIQ custompitg, AUDIT_END 2026-06-19, BQ_CACHE_THREADS=1, TZ ICT, DNA_PYEXE, CA snapshot 0927.
# Token TRỤC GIẢ (wrapper dịch, có mặc định = pin-era, để lệnh ghi lại khai được đúng trục bị đổi):
#   ENGINE_SORT  quicksort(mặc định, code TRƯỚC vá A1) | mergesort (code SAU vá A1)
#   LAG_DATA     vintage20261029 (mặc định; 3 file LAG vintage 10-29 = data pin-era, tái lập byte 4707bcbe)
#                | adjv2_20261110 (4 file cache LAG điều chỉnh v2 của chuỗi 11-10) | frozen20261112 (5 file LAG canonical chụp 12/11)
#   LIQ_ZERO_BLOCK  wrapper đặt `off` khi không khai (= hành vi mọi pin trước 12/11); khai `lag` để bật.
#   TIEBREAK_SEED   chỉ để đo nhiễu tie-break (code research có hook, KHÔNG thuộc nhánh merge).
# Họ code chọn theo IDLE_CARRY_TIER: off ⇒ nhánh merge feat/live-gap-exec-A-20261112 (main không có knob
# IDLE_CARRY ⇒ token inert); dep1m ⇒ bản research 33f005209 + đúng 2 commit A2/A1 (có knob IDLE_CARRY).
set -u
A=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_exec_A
TAG="$1"; shift
SORT=quicksort; LAGD=vintage20261029; LIQ=off; IDLE=off; SEED=""
for a in "$@"; do case "$a" in
  ENGINE_SORT=*) SORT="${a#*=}";; LAG_DATA=*) LAGD="${a#*=}";; LIQ_ZERO_BLOCK=*) LIQ="${a#*=}";;
  IDLE_CARRY_TIER=*) IDLE="${a#*=}";; TIEBREAK_SEED=*) SEED="${a#*=}";; esac; done
case "$IDLE" in off) FAM="";; dep1m) FAM="r";; *) echo "IDLE_CARRY_TIER lạ: $IDLE" >&2; exit 8;; esac
case "$SORT" in quicksort) S=q;; mergesort) S=m;; *) echo "ENGINE_SORT lạ: $SORT" >&2; exit 8;; esac
if [ -n "$SEED" ]; then [ "$S" = m ] || { echo "TIEBREAK_SEED cần mergesort" >&2; exit 8; }; S=tb; fi
[ "$FAM$S" = m ] && CODE=/home/trido/thanhdt/wt-livegapA-1112/WorkingClaude || CODE=/home/trido/thanhdt/wt-livegapA-1112-$FAM$S/WorkingClaude
SB="$A/sb/${FAM:-b}${S}_$LAGD"
[ -d "$SB" ] || { echo "thiếu sandbox $SB — chạy make_sandboxes.sh" >&2; exit 9; }
[ "$(readlink -f "$SB/pt_v23_audit_2014.py")" = "$CODE/pt_v23_audit_2014.py" ] || { echo "sandbox $SB không trỏ $CODE" >&2; exit 9; }
cd "$SB" || exit 9
export WORKDIR_8L=/home/trido/thanhdt/WorkingClaude PT_WORKDIR="$SB"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin" CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python TZ=Asia/Ho_Chi_Minh
START=$(date +%s)
env "$@" LIQ_ZERO_BLOCK="$LIQ" \
  BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
  /usr/bin/time -v $DNA_PYEXE "$SB/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$A/logs/$TAG.log" 2>&1
RC=$?
OUTCSV=$(ls -t "$SB"/data/v23_golive_audit_2014_now_*_exp_${TAG}_univpit*.csv 2>/dev/null | head -1)
[ -n "$OUTCSV" ] && cp -p "$OUTCSV" "$A/ledgers/" && MD5=$(md5sum "$OUTCSV" | cut -c1-32) || MD5=NONE
echo "EXIT=$RC WALL=$(( $(date +%s)-START ))s MD5=$MD5 CSV=$(basename "${OUTCSV:-none}") CODE=$CODE@$(git -C "$CODE" rev-parse --short HEAD) SB=$SB ARGS=$*" >> "$A/logs/$TAG.log"
