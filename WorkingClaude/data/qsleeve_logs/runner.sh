#!/bin/bash
# Q-SLEEVE family runs (plan_quality_sleeve_20260712.md, N=5) — job Taylor_20260712_080114
# Control = R3 pin contemporaneous; trials 1-3 = Q8-NEU / Q12-NEU / QF8-NEU. Trial 4 runs later
# (needs winner). All outputs EXP_TAG'd _exp_qsleeve* — never touch canonical (§8).
cd /home/trido/thanhdt/WorkingClaude
PY=/home/trido/thanhdt/wc_venv/bin/python
BASE="BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_SELECT=yieldcombo PARK_STATES=3:0.7 AUDIT_END=2026-06-19"
run() {  # $1=tag  $2=extra env
  echo "[runner] START $1 $(date -u +%H:%M:%S)"
  env $BASE $2 EXP_TAG="qsleeve_$1" $PY pt_v23_audit_2014.py v23a none postbull 0 edge \
      > data/qsleeve_logs/$1.log 2>&1
  echo "[runner] DONE $1 rc=$? $(date -u +%H:%M:%S)"
}
run ctrl   "BASKET_WT=namecap"                                                              &
run q8neu  "BASKET_WT=ew BASKET_TOPN=8 BASKET_GATE_RATING=2 BASKET_LIQ_FLOOR_B=5"           &
wait
run q12neu "BASKET_WT=ew BASKET_TOPN=12 BASKET_GATE_RATING=2 BASKET_LIQ_FLOOR_B=5"          &
run qf8neu "BASKET_WT=ew BASKET_TOPN=8 BASKET_GATE_RATING=none BASKET_QFLOOR=1 BASKET_LIQ_FLOOR_B=5" &
wait
touch data/qsleeve_logs/WAVE1_DONE
echo "[runner] WAVE1 ALL DONE $(date -u +%H:%M:%S)"
