#!/bin/bash
# A/B gate cung ADV cho book LAG — job Taylor_20260804_080547.
# Engine = BAN SAO nghien cuu pt_v23_advgate.py (khac production dung 3 khoi da ghi chu, no-op khi
# LAG_ADV_MIN_VND=0). Lenh pin R3 nguyen van + snapshot asof20260729_postrestate + threads=1 + $DNA_PYEXE.
#   $1 = TAG, $2 = nguong VND (0 = chan doi chung, ky vong tai lap 28,86%)
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; MIN="$2"
OUT=mike/agents/Taylor/exp_lag_advgate_20260804
PYTHONPATH=/home/trido/thanhdt/WorkingClaude \
LAG_ADV_MIN_VND="$MIN" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$OUT/pt_v23_advgate.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG min=$MIN)" >> "$OUT/$TAG.log"
