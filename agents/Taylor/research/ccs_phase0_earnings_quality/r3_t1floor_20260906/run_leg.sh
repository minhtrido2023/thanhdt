#!/bin/bash
# T1-accruals floor R3 legs (job Taylor_20260906_022452). Config = PINNED R3 command verbatim
# (results_registry.md "2026-08-03 RE-PIN R3 THEO ĐÚNG MẶC ĐỊNH PRODUCTION LAG_ADV_BASIS=price"),
# on forked engine_t1.py/custom_basket_t1.py (BASKET_T1FLOOR=abs|demean adds the floor; ctrl leg
# with BASKET_T1FLOOR unset must reproduce 28.86/1.90/-17.8/1.62 exactly).
# usage: run_leg.sh <TAG> [EXTRA_ENV_ASSIGNMENTS...]
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
HERE="mike/agents/Taylor/research/ccs_phase0_earnings_quality/r3_t1floor_20260906"
TAG="$1"; shift
env "$@" \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap PARK_STATES="3:0.7" \
  AUDIT_END=2026-06-19 LAG_ADV_BASIS=price BASKET_SELECT=yieldcombo \
  EXP_TAG="$TAG" AUDIT_EXP_TAG="$TAG" \
  "$DNA_PYEXE" "$HERE/engine_t1.py" v23a none postbull 0 edge \
  > "$HERE/eng_$TAG.log" 2>&1
echo "EXIT=$? (leg=$TAG env=$*)" >> "$HERE/eng_$TAG.log"
