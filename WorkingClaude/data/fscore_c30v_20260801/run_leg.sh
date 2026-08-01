#!/bin/bash
# FSCORE-enhancer A/B legs for custom30V (job Taylor_20260801_131833).
# Config = the PINNED R3 command (data/results_registry.md "2026-07-29 RE-PIN R3"), unchanged,
# except (a) the frozen snapshot is named explicitly and (b) EXP_TAG/AUDIT_EXP_TAG force a
# non-canonical output path (coding_guidelines §8). The ctrl leg must reproduce 27,60/1,84/-17,5/1,58.
# usage: run_leg.sh <TAG> [EXTRA_ENV_ASSIGNMENTS...]
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; shift
env "$@" \
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
  NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
  PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
  EXP_TAG="$TAG" AUDIT_EXP_TAG="$TAG" \
  "$DNA_PYEXE" data/fscore_c30v_20260801/engine_fsx.py v23a none postbull 0 edge \
  > "data/fscore_c30v_20260801/eng_$TAG.log" 2>&1
echo "EXIT=$? (leg=$TAG env=$*)" >> "data/fscore_c30v_20260801/eng_$TAG.log"
