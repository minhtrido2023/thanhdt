#!/bin/bash
# H3 A/B — job Taylor_20260926_164113. Lenh pin R3 NGUYEN VAN, chi them OSHARES_PIT.
#   ctrl : OSHARES_PIT khong set -> phai tai lap 28,8627% / NAV 1.178,0099B / md5 7d053e6201c9d107685ff4d1dd9d2d2a
#   pit  : OSHARES_PIT=1         -> OShares lay tu fiinprox_oshares_pit_20260926.csv (as-of ngay doi so)
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; shift
OUT=mike/agents/Taylor/research/fiinprox_h3_h1_h2_20260927
env "$@" PYTHONPATH=/home/trido/thanhdt/WorkingClaude \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE $OUT/engine_oshpit.py v23a none postbull 0 edge > "$OUT/eng_$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/eng_$TAG.log"
