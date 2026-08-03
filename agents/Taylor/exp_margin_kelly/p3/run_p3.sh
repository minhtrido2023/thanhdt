#!/bin/bash
# PHAN 3 — TACH BIEN co che SIZING: "dich von parking sang CAPIT o washout sau".
# job Taylor_20260803_082141 · RESEARCH-ONLY (production pt_v23_audit_2014.py KHONG bi sua).
#
# Engine = BAN SAO NGHIEN CUU p3/engine_park.py = p2/engine_dd52.py + 1 hunk THEM (`parkdd:f`),
# inert khi CAPIT_SIZE_BASE khong bat dau bang "parkdd:".
# Lenh pin R3 nguyen van (results_registry.md muc 2026-08-03) + snapshot asof20260729_postrestate
# + BQ_CACHE_THREADS=1 + $DNA_PYEXE (pandas 3). KHONG bat MGE => KHONG vay mot dong nao.
#   P0  control : CAPIT_SIZE_BASE=cash          -> PHAI tai lap 28,86% / -17,8% / 1,62 / 1.178,01B
#   Pxx        : CAPIT_SIZE_BASE=park:f         (dich parking o MOI su kien washout)
#   PDxx       : CAPIT_SIZE_BASE=parkdd:f       (dich parking CHI o su kien dd52<=-20%)
# EXP_TAG bat buoc de KHONG de canonical CSV (coding_guidelines §8).
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; shift
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/p3
env "$@" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 CAPIT_SIZE_DIAG=1 EXP_TAG="$TAG" \
$DNA_PYEXE "$OUT/engine_park.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
