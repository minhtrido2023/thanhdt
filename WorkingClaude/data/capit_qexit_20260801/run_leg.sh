#!/bin/bash
# CAPIT quality-exit A/B legs (job Taylor_20260801_073610).
# Same pinned config as the 07-31 sizing study => the ctrl leg must reproduce the R3 pin exactly.
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
QX="$1"; TAG="$2"
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
CAPIT_QEXIT="$QX" EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge \
  > data/capit_qexit_20260801/$TAG.log 2>&1
echo "EXIT=$? ($TAG qexit=$QX)" >> data/capit_qexit_20260801/$TAG.log
