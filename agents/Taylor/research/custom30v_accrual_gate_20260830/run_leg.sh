#!/bin/bash
# custom30V accrual-quality gate A/B legs (job Taylor_20260830_014429).
# Config = PINNED R3 command (results_registry.md "2026-08-03 RE-PIN R3"), unchanged, on the
# forked engine_ag.py/custom_basket_ag.py (BASKET_SELECT=yieldcombo_agate adds the pre-registered
# accrual gate; BASKET_SELECT=yieldcombo control leg must reproduce 28.86/1.90/-17.8/1.62 exactly).
# usage: run_leg.sh <TAG> [EXTRA_ENV_ASSIGNMENTS...]
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; shift
env "$@" \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap PARK_STATES="3:0.7" \
  AUDIT_END=2026-06-19 LAG_ADV_BASIS=price \
  EXP_TAG="$TAG" AUDIT_EXP_TAG="$TAG" \
  "$DNA_PYEXE" mike/agents/Taylor/research/custom30v_accrual_gate_20260830/engine_ag.py v23a none postbull 0 edge \
  > "mike/agents/Taylor/research/custom30v_accrual_gate_20260830/eng_$TAG.log" 2>&1
echo "EXIT=$? (leg=$TAG env=$*)" >> "mike/agents/Taylor/research/custom30v_accrual_gate_20260830/eng_$TAG.log"
