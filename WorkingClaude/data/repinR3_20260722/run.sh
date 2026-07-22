#!/usr/bin/env bash
# G6 re-pin R3 A/B — control (ticker_prune DISTINCT-ever) vs pit (universe_pit_q per-day).
# Pinned R3 command verbatim + $DNA_PYEXE (coding_guidelines.md §8); EXP_TAG keeps BOTH legs off the
# canonical CSV. Cache is verified:false today -> both legs run live BQ, contemporaneous.
set -u
cd /home/trido/thanhdt/WorkingClaude
source ./wc_env.sh
OUT=data/repinR3_20260722
COMMON='BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7 AUDIT_END=2026-06-19'
env BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
    PARK_STATES="3:0.7" AUDIT_END=2026-06-19 UNIVERSE_SRC=prune EXP_TAG=repinR3control \
    "$DNA_PYEXE" pt_v23_audit_2014.py v23a none postbull 0 edge > $OUT/control.log 2>&1
echo "CONTROL_EXIT=$?" >> $OUT/control.log
env BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
    PARK_STATES="3:0.7" AUDIT_END=2026-06-19 UNIVERSE_SRC=pit EXP_TAG=repinR3pit \
    "$DNA_PYEXE" pt_v23_audit_2014.py v23a none postbull 0 edge > $OUT/pit.log 2>&1
echo "PIT_EXIT=$?" >> $OUT/pit.log
touch $OUT/DONE
