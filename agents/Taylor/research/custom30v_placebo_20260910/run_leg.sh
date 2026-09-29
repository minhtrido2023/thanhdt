#!/bin/bash
# VONG 5 custom30V PLACEBO — one leg. Lenh = pin R3 nguyen van, cung snapshot dong cung, threads=1.
# Khac biet DUY NHAT giua cac chan: BASKET_CFO_POOL (60|120) + BASKET_PLACEBO_FIN/_MODE.
# sel_engine.py re-insert thu muc NAY len sys.path[0] sau lenh insert cua production => `custom_basket`
# lay BAN COPY o day (file production khong bi dung). Chan control chung minh ban copy trung thuc:
# phai tai lap CSV pin R3 byte-for-byte (md5 7d053e6201c9d107685ff4d1dd9d2d2a).
set -u
LEG="$1"
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
D=mike/agents/Taylor/research/custom30v_placebo_20260910
A=/home/trido/thanhdt/WorkingClaude/$D
POOL=""; EXTRA=()
case "$LEG" in
  ctrl)  EXTRA+=("BASKET_FINCOUNT_DUMP=$A/fincount_ctrl.csv") ;;
  L1b)   POOL=120; EXTRA+=("BASKET_FINCOUNT_DUMP=$A/fincount_L1b.csv") ;;
  # P1 = pool 60 (ctrl pool) ep so ten tai chinh = so cua L1b  -> PHA LOANG NGANH thuan
  P1d)   EXTRA+=("BASKET_PLACEBO_FIN=0:$A/fincount_L1b.csv"  "BASKET_PLACEBO_MODE=top"
                 "BASKET_FINCOUNT_DUMP=$A/fincount_P1d.csv") ;;
  P1r1)  EXTRA+=("BASKET_PLACEBO_FIN=101:$A/fincount_L1b.csv" "BASKET_PLACEBO_MODE=random"
                 "BASKET_FINCOUNT_DUMP=$A/fincount_P1r1.csv") ;;
  P1r2)  EXTRA+=("BASKET_PLACEBO_FIN=202:$A/fincount_L1b.csv" "BASKET_PLACEBO_MODE=random"
                 "BASKET_FINCOUNT_DUMP=$A/fincount_P1r2.csv") ;;
  # P2 = pool 120 (ten moi) ep so ten tai chinh = so cua ctrl -> THEM TEN RE, nganh giu nguyen
  P2d)   POOL=120; EXTRA+=("BASKET_PLACEBO_FIN=0:$A/fincount_ctrl.csv" "BASKET_PLACEBO_MODE=top"
                 "BASKET_FINCOUNT_DUMP=$A/fincount_P2d.csv") ;;
  P2r1)  POOL=120; EXTRA+=("BASKET_PLACEBO_FIN=101:$A/fincount_ctrl.csv" "BASKET_PLACEBO_MODE=random"
                 "BASKET_FINCOUNT_DUMP=$A/fincount_P2r1.csv") ;;
  P2r2)  POOL=120; EXTRA+=("BASKET_PLACEBO_FIN=202:$A/fincount_ctrl.csv" "BASKET_PLACEBO_MODE=random"
                 "BASKET_FINCOUNT_DUMP=$A/fincount_P2r2.csv") ;;
  *) echo "unknown leg $LEG"; exit 2 ;;
esac
[ -n "$POOL" ] && EXTRA+=("BASKET_CFO_POOL=$POOL")
env PYTHONPATH=/home/trido/thanhdt/WorkingClaude \
    "${EXTRA[@]}" \
    BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 LAG_ADV_BASIS=price \
    NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
    PARK_STATES="3:0.7" AUDIT_END=2026-06-19 AUDIT_EXP_TAG="c30vpb$LEG" \
    $DNA_PYEXE $D/sel_engine.py v23a none postbull 0 edge > "$D/run_$LEG.log" 2>&1
echo "EXIT=$?" >> "$D/run_$LEG.log"
