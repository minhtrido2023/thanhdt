#!/bin/bash
# Phase-1 runner — job Taylor_20260823_120317. RESEARCH-ONLY (production KHONG bi sua).
# Lenh pin R3 nguyen van (results_registry.md 2026-08-03) + snapshot asof20260729_postrestate.
# EXP_TAG bat buoc (coding_guidelines §8: khong bao gio de canonical CSV).
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/margin_valuation_spread_phase1_20260823
P5=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/p5_engine
TAG="$1"; shift
env "$@" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 CAPIT_SIZE_DIAG=1 EXP_TAG="$TAG" \
PYTHONPATH="$P5" \
$DNA_PYEXE "$OUT/engine_p1.py" v23a none postbull 0 edge > "$OUT/logs/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/logs/$TAG.log"
