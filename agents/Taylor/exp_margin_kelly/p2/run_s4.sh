#!/bin/bash
# VIEC 1 — S4 (margin co dieu kien dd52<=-20%) o TANG PORTFOLIO-ENGINE.
# job Taylor_20260803_073714 · RESEARCH-ONLY.
#
# Engine = BAN SAO NGHIEN CUU p2/engine_dd52.py (production pt_v23_audit_2014.py KHONG bi sua;
# diff = 2 hunk additive: MGE_GATE="dd52" + MGE_DD52, inert khi khong dung).
# Lenh pin R3 nguyen van (results_registry.md muc 2026-08-03) + snapshot dong cung
# asof20260729_postrestate + BQ_CACHE_THREADS=1 + $DNA_PYEXE (pandas 3).
#   L0 control : khong bat gi          -> PHAI tai lap 28,86% / 1,90 / -17,8% / 1,62
#   L1/L2      : MGE 1.3 / 1.5, MGE_CAPIT_ONLY=1 FORCE_REAL_LEVER=1 MGE_GATE=dd52 MGE_DD52=-20
# EXP_TAG bat buoc de KHONG de canonical CSV (coding_guidelines §8).
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; shift
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/p2
env "$@" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$OUT/engine_dd52.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
