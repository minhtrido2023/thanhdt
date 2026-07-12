#!/bin/bash
# V2.5 lever LOO/DSR verification runs — job Taylor_20260712_054553 (non-canonical outputs, EXP_TAG'd)
cd /home/trido/thanhdt/WorkingClaude
PY=/home/trido/thanhdt/wc_venv/bin/python
BASE="BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7 AUDIT_END=2026-06-19 RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5 RECOVERY_CAPIT_ONLY=1 RECOVERY_CAPIT_VOL=1.7 RECOVERY_CAPIT_BASE=63 RECOVERY_SIG_C=1 RECOVERY_C_CONFIRM=1 RECOVERY_C_ARM_K=30 RECOVERY_STATE_BLIND=1 RECOVERY_PE_PCT_MAX=0.20"
LEV="RECOVERY_LEVER_PARK=1 RECOVERY_LEVER_FRAC=0.50 MGE=1.5 MGE_CAPIT_ONLY=1 MARGIN_CALL=1 MGE_HARD=1.65 LEVER_NAV_CAP_B=100 BORROW_ANNUAL=0.125"
run() {  # $1=tag  $2=extra env
  echo "[runner] START $1 $(date -u +%H:%M:%S)"
  env $BASE $2 EXP_TAG="_$1" $PY pt_v25_loo_tmp_20260712.py v23a none postbull 0 edge \
      > data/v25chk_logs/$1.log 2>&1
  echo "[runner] DONE $1 rc=$? $(date -u +%H:%M:%S)"
}
run v25chk_LF        ""                                        &
run v25chk_LEV       "$LEV"                                    &
wait
run v25chk_LOO2020   "$LEV LEVER_SKIP=2020-01-01:2020-12-31"   &
run v25chk_LOO2022   "$LEV LEVER_SKIP=2022-10-01:2023-02-28"   &
wait
run v25chk_LOO2023   "$LEV LEVER_SKIP=2023-03-01:2023-12-31"   &
run v25chk_LEVnocap  "$LEV LEVER_NAV_CAP_B=100000"             &
wait
touch data/v25chk_logs/ALL_DONE
echo "[runner] ALL DONE $(date -u +%H:%M:%S)"
