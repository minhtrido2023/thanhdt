#!/bin/bash
# VONG 4 custom30V selector — one leg. Lenh = pin R3 nguyen van, cung snapshot dong cung, threads=1.
# Khac biet DUY NHAT giua cac chan: BASKET_CFO_POOL (L1a/L1b) | BASKET_SELECT=eycfq (L2) |
# BASKET_BANKSWAP=1 (L3). sel_engine.py re-insert thu muc nay len sys.path[0] sau lenh insert cua
# production => `custom_basket` lay BAN COPY o day (file production khong bi dung).
# Chan control chung minh ban copy trung thuc: phai tai lap CSV pin R3 byte-for-byte.
set -u
EXTRA=()
LEG="$1"
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
D=mike/agents/Taylor/research/custom30v_selector_20260909
POOL=""; SEL="yieldcombo"; SWAP=""
case "$LEG" in
  ctrl) ;;
  L1a)  POOL=90 ;;
  L1b)  POOL=120 ;;
  L2)   SEL="eycfq" ;;
  L3)   SWAP=1 ;;
  *) echo "unknown leg $LEG"; exit 2 ;;
esac
EXTRA=()
[ -n "$POOL" ] && EXTRA+=("BASKET_CFO_POOL=$POOL")
[ -n "$SWAP" ] && EXTRA+=("BASKET_BANKSWAP=$SWAP")
env PYTHONPATH=/home/trido/thanhdt/WorkingClaude \
    "${EXTRA[@]}" \
    BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 LAG_ADV_BASIS=price \
    NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT="$SEL" \
    PARK_STATES="3:0.7" AUDIT_END=2026-06-19 AUDIT_EXP_TAG="c30vsel$LEG" \
    $DNA_PYEXE $D/sel_engine.py v23a none postbull 0 edge > "$D/run_$LEG.log" 2>&1
echo "EXIT=$?" >> "$D/run_$LEG.log"
