#!/bin/bash
# LAG quality-gate A/B legs — job Taylor_20260803_015850.
# Engine = pt_v23_lagqual_research.py (research copy of pt_v23_audit_2014.py + 2 opt-in knobs,
# default OFF = byte-identical). Production pt_v23_audit_2014.py is NEVER edited (skill §14).
# Frozen snapshot asof20260729_postrestate + threads=1 + $DNA_PYEXE + the verbatim R3 pin command.
# L0 (both knobs off) MUST reproduce CAGR 27.24 / Sharpe 1.81 / MaxDD -18.4 / Calmar 1.48,
# else the A/B is invalid and nothing may be concluded from any treatment leg.
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; shift
OUT=mike/agents/Taylor/research/lag_quality_20260803
env "$@" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_lagqual_research.py v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
