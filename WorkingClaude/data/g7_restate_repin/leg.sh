#!/usr/bin/env bash
# G7 re-pin R3 sau DT5G restate 2026-07-29. $1=cache_path $2=exp_tag
set -uo pipefail
cd /home/trido/thanhdt/WorkingClaude
source ./wc_env.sh
BQ_LOCAL_CACHE="$1" BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap \
BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
EXP_TAG="$2" \
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
echo "EXIT=$? ($2 cache=$1)"
