#!/usr/bin/env bash
# §5.3 item: re-measure the LAG-liquidity delta ON THE NEW UNIVERSE.
# Delta_pit = (pit + LIQ_ZERO_BLOCK=lag) - (pit alone, from run.sh). Compare against the delta
# measured on `prune` on 2026-07-21 (+4.11pp) to see whether universe_pit's B3/B4 liquidity rule
# makes the LAG liquidity layer redundant.
set -u
cd /home/trido/thanhdt/WorkingClaude
source ./wc_env.sh
OUT=data/repinR3_20260722
env BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
    PARK_STATES="3:0.7" AUDIT_END=2026-06-19 UNIVERSE_SRC=pit LIQ_ZERO_BLOCK=lag EXP_TAG=repinR3pitliqzb \
    "$DNA_PYEXE" pt_v23_audit_2014.py v23a none postbull 0 edge > $OUT/pit_liqzb.log 2>&1
echo "PITLIQZB_EXIT=$?" >> $OUT/pit_liqzb.log
touch $OUT/DONE_LAGLIQ
