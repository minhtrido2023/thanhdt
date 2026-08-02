#!/bin/bash
# A/B legs for the custom30V price-basis role split (job Taylor_20260802_141725, step 4/8).
#
# legA = BASKET_PRICE_BASIS=legacy -> pre-fix behaviour. MUST reproduce the pinned R3
#        (CAGR 27,60% / Sharpe 1,84 / MaxDD -17,5% / Calmar 1,58) exactly; if it does not,
#        the A/B is invalid and nothing may be concluded from legB.
# legB = BASKET_PRICE_BASIS=split  -> the fix (production default since commit ebeacad).
#
# Single variable between the legs. Frozen snapshot asof20260729_postrestate = the exact vintage
# the pinned number was measured on (live BQ cannot reproduce it: ticker/ticker_prune are
# TRUNCATE+rebuilt daily and BQ time-travel is off). threads=1 + $DNA_PYEXE per registry pin.
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
BASIS="$1"; TAG="$2"
OUT=data/basis_ab_20260802
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
BASKET_PRICE_BASIS="$BASIS" EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge \
  > $OUT/$TAG.log 2>&1
echo "EXIT=$? ($TAG basis=$BASIS)" >> $OUT/$TAG.log
