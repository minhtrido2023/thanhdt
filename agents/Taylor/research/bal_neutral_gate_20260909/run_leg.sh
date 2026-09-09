#!/bin/bash
# VONG 3 BAL — one leg. Command = pinned R3 command verbatim, same frozen snapshot, threads=1.
# Only difference between legs: NGATE (truc A) or BRULE (truc B).
#   $1 = leg tag (also AUDIT_EXP_TAG suffix)   $2 = NGATE   $3 = BRULE
# gate_engine.py re-inserts THIS directory at sys.path[0] after the production insert, so
# `import simulate_holistic_nav` picks up the RESEARCH COPY here (production file untouched).
# The control leg proves the copy is faithful: it must reproduce the pinned R3 CSV byte-for-byte.
set -u
LEG="$1"; NG="${2:-off}"; BR="${3:-off}"
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
D=mike/agents/Taylor/research/bal_neutral_gate_20260909
PYTHONPATH=/home/trido/thanhdt/WorkingClaude \
NGATE="$NG" BRULE="$BR" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 AUDIT_EXP_TAG="balgate$LEG" \
$DNA_PYEXE $D/gate_engine.py v23a none postbull 0 edge > "$D/run_$LEG.log" 2>&1
echo "EXIT=$?" >> "$D/run_$LEG.log"
