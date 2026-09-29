#!/bin/bash
# PART 3 — one leg of the BAL ey-tilt A/B. Command = pinned R3 command verbatim, same frozen
# snapshot, threads=1. Only difference between legs: BAL_CFO_BLEND (lambda).
#   $1 = leg tag   $2 = BAL_CFO_BLEND (0 = control)
# AUDIT_EXP_TAG keeps output off every canonical/pinned path (coding_guidelines §8) — REQUIRED here
# because BAL_CFO_BLEND has NO filename suffix of its own.
set -u
LEG="$1"; LAM="$2"
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
D=mike/agents/Taylor/research/bal_2025_diagnosis_20260909/p3
PYTHONPATH=/home/trido/thanhdt/WorkingClaude \
BAL_CFO_BLEND="$LAM" BAL_YIELD_METRIC=pe \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 AUDIT_EXP_TAG="baley$LEG" \
$DNA_PYEXE $D/bal_ey_engine.py v23a none postbull 0 edge > "$D/run_$LEG.log" 2>&1
echo "EXIT=$?" >> "$D/run_$LEG.log"
