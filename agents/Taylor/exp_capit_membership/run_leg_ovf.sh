#!/bin/bash
# POSITIVE CONTROL for the CAPIT-membership question: same pinned-R3 leg but with
# CAPIT_BEAR_OVERFLOW=1, the ONLY switch that makes pt_v23_audit_2014.py:124 (_c30v_asof) read
# tav2_bq.custom30v_8l at all. Proves the harness is not blind to that table.
#   run_leg_ovf.sh <tag> <cache_dir>
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; CACHE="$2"
OUT=mike/agents/Taylor/exp_capit_membership
BQ_LOCAL_CACHE="$CACHE" BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
CAPIT_BEAR_OVERFLOW=1 \
BASKET_PRICE_BASIS=split EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge \
  > $OUT/$TAG.log 2>&1
echo "EXIT=$? ($TAG overflow=1 cache=$CACHE)" >> $OUT/$TAG.log
