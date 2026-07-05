#!/bin/bash
source /home/trido/thanhdt/WorkingClaude/wc_env.sh >/dev/null 2>&1
cd /home/trido/thanhdt/WorkingClaude
LOGD=data/volmanage_h3_logs
COMMON='BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7 AUDIT_END=2026-06-19'

run() { # name  extra_env
  echo "[$(date +%H:%M:%S)] START $1" >> $LOGD/progress.txt
  env $COMMON $2 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge > $LOGD/$1.log 2>&1
  echo "[$(date +%H:%M:%S)] DONE $1 exit=$? -> $(grep -m1 'Final NAV' $LOGD/$1.log)" >> $LOGD/progress.txt
}

: > $LOGD/progress.txt
run baseline    ""
run vm_mult1.0  "VOLMANAGE_BAL=1 VOLMANAGE_TGT_MULT=1.0"
run vm_mult0.8  "VOLMANAGE_BAL=1 VOLMANAGE_TGT_MULT=0.8"
run vm_mult1.2  "VOLMANAGE_BAL=1 VOLMANAGE_TGT_MULT=1.2"
echo "[$(date +%H:%M:%S)] ALL COMPLETE" >> $LOGD/progress.txt
