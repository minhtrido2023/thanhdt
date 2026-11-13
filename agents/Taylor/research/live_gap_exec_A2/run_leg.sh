#!/bin/bash
# Luồng A2 (job Taylor_20261112_181209). Usage: run_leg.sh <TAG> <off|1m> KEY=VAL...
# Env cố định = run_leg2.sh Luồng A (pin R3 park0 10-08): cache asof20260729_postrestate, NAV 50B, ETF_LIQ custompitg,
# AUDIT_END 06-19, threads=1, TZ ICT, CA snapshot 0927, LAG data vintage 10-29, park 0, namecap/yieldcombo.
# off ⇒ code main f210c726b(+mergesort) + 4f7609c34 (LAG_ADV_SRC); 1m ⇒ research 49cd913ae + 770393ce2, IDLE_CARRY_TIER=dep1m.
set -u
A2=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_exec_A2
TAG="$1"; END="$2"; shift 2
case "$END" in off) CODE=/home/trido/thanhdt/wt-livegapA2-1113/WorkingClaude; SB=$A2/sb/m; IDLE=off;;
  1m) CODE=/home/trido/thanhdt/wt-livegapA2-1113-r/WorkingClaude; SB=$A2/sb/r; IDLE=dep1m;; *) exit 8;; esac
[ "$(readlink -f "$SB/pt_v23_audit_2014.py")" = "$CODE/pt_v23_audit_2014.py" ] || { echo "sandbox lệch" >&2; exit 9; }
cd "$SB" || exit 9
export WORKDIR_8L=/home/trido/thanhdt/WorkingClaude PT_WORKDIR="$SB"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin" CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python TZ=Asia/Ho_Chi_Minh
START=$(date +%s)
env BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=$IDLE "$@" \
  BASKET_CA_SNAPSHOT=/home/trido/thanhdt/WorkingClaude/data/snapshots/corp_action_share_20260927.parquet \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
  /usr/bin/time -v $DNA_PYEXE "$SB/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$A2/logs/$TAG.log" 2>&1
RC=$?
OUTCSV=$(ls -t "$SB"/data/v23_golive_audit_2014_now_*_exp_${TAG}_univpit*.csv 2>/dev/null | head -1)
[ -n "$OUTCSV" ] && mv "$OUTCSV" "$A2/ledgers/" && OUTCSV="$A2/ledgers/$(basename "$OUTCSV")" && MD5=$(md5sum "$OUTCSV" | cut -c1-32) || MD5=NONE
echo "EXIT=$RC WALL=$(( $(date +%s)-START ))s MD5=$MD5 CSV=$(basename "${OUTCSV:-none}") CODE=$CODE@$(git -C "$CODE" rev-parse --short HEAD) SB=$SB END=$END ARGS=$*" >> "$A2/logs/$TAG.log"
