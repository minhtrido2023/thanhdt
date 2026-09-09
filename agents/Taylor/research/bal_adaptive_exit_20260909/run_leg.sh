#!/bin/bash
# VONG 2 BAL adaptive exit — one leg. Command = pinned R3 command verbatim, same frozen snapshot,
# threads=1. Only difference between legs: ADAPT_MODE.
#   $1 = leg tag (also AUDIT_EXP_TAG suffix)   $2 = ADAPT_MODE (off|A|B|C|D)
# sys.path[0] is this script's own directory, so `import simulate_holistic_nav` picks up the
# RESEARCH COPY here (production file untouched). The control leg proves the copy is faithful:
# it must reproduce the pinned R3 CSV byte-for-byte.
set -u
LEG="$1"; MODE="$2"
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
D=mike/agents/Taylor/research/bal_adaptive_exit_20260909
PYTHONPATH=/home/trido/thanhdt/WorkingClaude \
ADAPT_MODE="$MODE" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 AUDIT_EXP_TAG="baladapt$LEG" \
$DNA_PYEXE $D/adaptive_engine.py v23a none postbull 0 edge > "$D/run_$LEG.log" 2>&1
echo "EXIT=$?" >> "$D/run_$LEG.log"
