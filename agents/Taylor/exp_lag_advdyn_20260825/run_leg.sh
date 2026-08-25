#!/bin/bash
# San ADV DONG cho book LAG — job Taylor_20260825_094721.
# Engine = BAN SAO nghien cuu pt_v23_advdyn.py (dan xuat tu ban 08-04 da CONFIRMED, them dung 1 knob
# LAG_ADV_MIN_MODE). Lenh pin R3 nguyen van + snapshot asof20260729_postrestate + threads=1 + $DNA_PYEXE.
#   $1=TAG  $2=LAG_ADV_MIN_VND  $3=MODE(static|inflate|pctile)  $4=PCTILE_CSV(optional)
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; MIN="$2"; MODE="${3:-static}"; CSV="${4:-}"
OUT=mike/agents/Taylor/exp_lag_advdyn_20260825
PYTHONPATH=/home/trido/thanhdt/WorkingClaude \
LAG_ADV_MIN_VND="$MIN" LAG_ADV_MIN_MODE="$MODE" LAG_ADV_PCTILE_CSV="$CSV" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$OUT/pt_v23_advdyn.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG min=$MIN mode=$MODE csv=$CSV)" >> "$OUT/$TAG.log"
