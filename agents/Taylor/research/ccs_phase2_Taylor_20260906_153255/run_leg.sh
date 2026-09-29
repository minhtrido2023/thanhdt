#!/bin/bash
# CCS Phase 2 — one leg of the A/B. Command = pinned R3 command verbatim (run_repin.sh 2026-08-03),
# same frozen snapshot, threads=1. Only difference between legs: CCS_TRIM_FRAC.
#   $1 = leg tag (ctrl|trim50)   $2 = CCS_TRIM_FRAC (1 = control, 0.5 = treatment)
# EXP_TAG keeps output off every canonical/pinned path (coding_guidelines §8).
set -u
LEG="$1"; FRAC="$2"
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
D=mike/agents/Taylor/research/ccs_phase2_Taylor_20260906_153255
PYTHONPATH=/home/trido/thanhdt/WorkingClaude \
CCS_TRIM_FRAC="$FRAC" CCS_LEG="$LEG" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG=ccsp2$LEG \
$DNA_PYEXE $D/ccs_p2_engine.py v23a none postbull 0 edge > "$D/run_$LEG.log" 2>&1
echo "EXIT=$?" >> "$D/run_$LEG.log"
