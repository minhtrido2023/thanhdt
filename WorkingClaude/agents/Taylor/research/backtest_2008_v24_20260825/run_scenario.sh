#!/bin/bash
# job Taylor_20260825_055651 -- Step 2 backtest 2008-2026. RESEARCH-ONLY (production KHONG bi sua).
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
OUT=/home/trido/thanhdt/WorkingClaude/agents/Taylor/research/backtest_2008_v24_20260825
P5=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/p5_engine
TAG="$1"; shift
unset BQ_LOCAL_CACHE
env "$@" \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_START=2008-01-01 AUDIT_END=2026-08-21 EXP_TAG="$TAG" \
STATE_TABLE_OVERRIDE=tav2_bq.taylor_exp_dt5g_recompute_2008_2026_20260825 \
PYTHONPATH="$P5" \
$DNA_PYEXE "$OUT/engine_2008.py" v23a none postbull 0 edge > "$OUT/logs/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/logs/$TAG.log"
