#!/bin/bash
# RE-PIN R3 — job Taylor_20260803_035250.
# Engine = PRODUCTION pt_v23_audit_2014.py (khong sua gi, git status sach).
# Lenh pin R3 nguyen van + snapshot dong cung asof20260729_postrestate + threads=1 + $DNA_PYEXE.
#   leg "price" = mac dinh production hom nay (LAG_ADV_BASIS khong set -> "price")  -> ky vong 28,86%
#   leg "close" = chan doi chung, tai lap so pin cu                                  -> ky vong 27,24%
# EXP_TAG dung de KHONG de canonical ..._wtnamecap.csv (coding_guidelines §8).
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; shift
OUT=mike/agents/Taylor/research/lag_repin_20260803
env "$@" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
