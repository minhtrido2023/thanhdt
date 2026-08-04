#!/bin/bash
# Duong cong CAPACITY theo NAV — job Taylor_20260804_102015.
# Lenh pin R3 NGUYEN VAN (ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo
# PARK_STATES="3:0.7" AUDIT_END=2026-06-19 v23a none postbull 0 edge), chi doi 2 bien:
#   $1 = NAV_TOTAL_B  (1|5|10|20|30|50|75|100)
#   $2 = LIQ_UNCAP    (0 = chan THAT/production, 1 = chan LY TUONG fill hoan hao)
#   $3 = LIQ_PCT      (TUY CHON, mac dinh 0.20 = production). Bo trong => TAG va hanh vi GIU
#        NGUYEN y het 16 chan goc, nen cach tai lap o §7 bao cao van dung nguyen van.
#        Dat 0.04 => tran fill neo theo fill THAT DNSE (~3,86% ADV/phien), tra loi killer
#        objection cua quant-skeptic (recommended_reruns, 2026-08-04).
# Snapshot BQ cache asof20260729_postrestate + BQ_CACHE_THREADS=1 + $DNA_PYEXE (pandas 3).
# EXP_TAG LUON duoc set => KHONG BAO GIO ghi de CSV canonical (coding_guidelines §8).
set -u
cd /home/trido/thanhdt/WorkingClaude || exit 1
# shellcheck disable=SC1091
source ./wc_env.sh
NAVB="$1"; UNCAP="$2"; PCT="${3:-0.20}"
SUF=$([ "$UNCAP" = "1" ] && echo "ideal" || echo "real")
TAG="cap${NAVB}b_${SUF}"
# Chi them hau to khi PCT khac mac dinh => 16 chan goc giu nguyen ten file.
[ "$PCT" = "0.20" ] || TAG="${TAG}_liqpct${PCT//./p}"
OUT=mike/agents/Taylor/exp_capacity_20260804
env LIQ_UNCAP="$UNCAP" LIQ_PCT="$PCT" \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B="$NAVB" ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
  PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
  "$DNA_PYEXE" "$OUT/pt_v23_capacity.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG NAV=${NAVB}B LIQ_UNCAP=$UNCAP LIQ_PCT=$PCT)" >> "$OUT/$TAG.log"
