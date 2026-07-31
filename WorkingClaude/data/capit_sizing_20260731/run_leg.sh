#!/bin/bash
# A/B legs cho cau hoi CAPIT sizing base (job Taylor_20260731_085810).
# Chay tren snapshot dong cung asof20260729_postrestate => contemporaneous, khong troi vintage.
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
BASE="$1"; TAG="$2"
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
CAPIT_SIZE_BASE="$BASE" CAPIT_SIZE_DIAG=1 EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge \
  > data/capit_sizing_20260731/$TAG.log 2>&1
echo "EXIT=$? ($TAG base=$BASE)" >> data/capit_sizing_20260731/$TAG.log
