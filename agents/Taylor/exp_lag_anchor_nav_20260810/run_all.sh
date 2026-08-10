#!/bin/bash
# A/B NAV-level trần anchor book LAG — job Taylor_20260810_101717.
# Lệnh pin R3 NGUYÊN VĂN (mike/agents/Taylor/research/lag_repin_20260803/run_repin.sh),
# chỉ khác: chạy qua run_leg.py để tiêm trần anchor vào engine (§8: EXP_TAG mọi chân).
#   $1 = cap ("none" | 0.00 | 0.01 | ...)   $2 = tag
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
CAP="$1"; TAG="$2"
OUT=mike/agents/Taylor/exp_lag_anchor_nav_20260810
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
$DNA_PYEXE "$OUT/run_leg.py" "$CAP" "$TAG" > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG cap=$CAP)" >> "$OUT/$TAG.log"
