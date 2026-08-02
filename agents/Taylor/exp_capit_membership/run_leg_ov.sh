#!/bin/bash
# Same pinned-R3 A/B leg as data/basis_ab_20260802/run_leg.sh, but with the BQ cache dir as an
# argument so the custom30v_8l overlay (CAPIT-membership branch input) can be swapped.
#   run_leg_ov.sh <basis> <tag> <cache_dir>
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
BASIS="$1"; TAG="$2"; CACHE="$3"
OUT=mike/agents/Taylor/exp_capit_membership
BQ_LOCAL_CACHE="$CACHE" BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
BASKET_PRICE_BASIS="$BASIS" EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge \
  > $OUT/$TAG.log 2>&1
echo "EXIT=$? ($TAG basis=$BASIS cache=$CACHE)" >> $OUT/$TAG.log
