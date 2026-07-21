#!/bin/bash
set -x
cd /home/trido/thanhdt/WorkingClaude
source wc_env.sh 2>/dev/null
D=data/liqzb_20260721
COMMON='BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7 AUDIT_END=2026-06-19'
env BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG=liqzbctrl \
  $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge > $D/ctrl.log 2>&1
echo "CTRL_EXIT=$?" >> $D/ctrl.log
env BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 LIQ_ZERO_BLOCK=lag \
  $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge > $D/treat.log 2>&1
echo "TREAT_EXIT=$?" >> $D/treat.log
touch $D/DONE
