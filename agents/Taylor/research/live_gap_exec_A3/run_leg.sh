#!/bin/bash
# Luồng A3 (job Taylor_20261113_021435). Usage: run_leg.sh <TAG> <m|r> <vint|adj> KEY=VAL...
# Env cố định = run_leg.sh Luồng A2 (cache asof20260729_postrestate, NAV 50B, ETF_LIQ custompitg, AUDIT_END 06-19,
# threads=1, TZ ICT, CA snapshot 0927, park 0, namecap/yieldcombo). m ⇒ code A3 6bbb4a443 (pin0%, IDLE off);
# r ⇒ code 770393ce2 (pin1M, IDLE_CARRY_TIER=dep1m). LIQ_ZERO_BLOCK/LAG_ADV_SRC/LAG_ADV_MINP truyền TƯỜNG MINH qua args
# (trừ chân D_* cố ý không truyền để đo mặc định mới).
set -u
A3=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_exec_A3
TAG="$1"; FAM="$2"; LD="$3"; shift 3
case "$FAM" in m) CODE=/home/trido/thanhdt/wt-livegapA3-1113/WorkingClaude; IDLE=off;;
  r) CODE=/home/trido/thanhdt/wt-livegapA3-1113-r/WorkingClaude; IDLE=dep1m;; *) exit 8;; esac
SB=$A3/sb/${FAM}_$LD
[ "$(readlink -f "$SB/pt_v23_audit_2014.py")" = "$CODE/pt_v23_audit_2014.py" ] || { echo "sandbox lệch" >&2; exit 9; }
cd "$SB" || exit 9
export WORKDIR_8L=/home/trido/thanhdt/WorkingClaude PT_WORKDIR="$SB"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin" CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python TZ=Asia/Ho_Chi_Minh
unset LIQ_ZERO_BLOCK LAG_ADV_SRC LAG_ADV_MINP
START=$(date +%s)
env BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=$IDLE "$@" \
  BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
  /usr/bin/time -v $DNA_PYEXE "$SB/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$A3/logs/$TAG.log" 2>&1
RC=$?
OUTCSV=$(ls -t "$SB"/data/v23_golive_audit_2014_now_*_exp_${TAG}_univpit*.csv 2>/dev/null | head -1)
[ -n "$OUTCSV" ] && mv "$OUTCSV" "$A3/ledgers/" && OUTCSV="$A3/ledgers/$(basename "$OUTCSV")" && MD5=$(md5sum "$OUTCSV" | cut -c1-32) || MD5=NONE
echo "EXIT=$RC WALL=$(( $(date +%s)-START ))s MD5=$MD5 CSV=$(basename "${OUTCSV:-none}") CODE=$CODE@$(git -C "$CODE" rev-parse --short HEAD) SB=$SB ARGS=$*" >> "$A3/logs/$TAG.log"
