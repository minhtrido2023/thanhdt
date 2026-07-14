#!/bin/bash
# Pha-3 DCF selector backtest — job Taylor_20260714_070221
# Pinned R3 command (registry 2026-07-12) + EXP_TAG/BASKET_DCF_MODE so nothing writes canonical (§8).
# NOTE: registry prints "BQ_LOCAL_CACHE=1" but "1" resolves to WORKDIR/1 -> no manifest -> SILENT
# fallback to live BQ (wrong vintage). Correct value is data/bq_cache.
cd /home/trido/thanhdt/WorkingClaude
P=/home/trido/thanhdt/wc_venv/bin/python
BASE='BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7 AUDIT_END=2026-06-19'
L=data/dcf_exp_logs

run() {  # $1=label  $2=extra env
  ( eval "env $BASE $2 $P pt_v23_audit_2014.py v23a none postbull 0 edge" ) > $L/$1.log 2>&1
  echo "$1 exit=$?" >> $L/DONE_MARKS
}

run ctrl   "EXP_TAG=dcfctrl20260714" &
run varA   "BASKET_DCF_MODE=exclude_rich" &
run varB   "BASKET_DCF_MODE=tiebreak BASKET_DCF_W=0.25" &
wait
touch $L/ALL_DONE
