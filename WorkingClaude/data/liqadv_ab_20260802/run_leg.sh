#!/bin/bash
# A/B legs — job Taylor_20260802_163657. Hai bản sửa fidelity ĐỘC LẬP, đo tách bạch:
#   Việc 1  LIQ_ZERO_BLOCK : off  -> lag    (mã ADV<=0/không đo được = KHÔNG mua được)
#   Việc 2  LAG_ADV_BASIS  : close -> price (ADV = Volume_3M_P50 x COALESCE(Price,Close))
#
# L0 = legacy cả hai  -> PHẢI tái lập pin R3 hiện hành 27,24% / 1,81 / -18,4% / 1,48 / 1.006,33B.
#      Không tái lập được thì A/B VÔ HIỆU, không kết luận gì từ L1/L2/L3.
# L1 = chỉ Việc 1. L2 = chỉ Việc 2. L3 = cả hai (ứng viên production).
#
# Snapshot đóng cứng asof20260729_postrestate = ĐÚNG vintage của số pin (live BQ không tái lập
# được: ticker/ticker_prune TRUNCATE+rebuild mỗi ngày, BQ time-travel tắt). threads=1 + $DNA_PYEXE.
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
LZB="$1"; ADV="$2"; TAG="$3"
OUT=data/liqadv_ab_20260802
mkdir -p $OUT
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
LIQ_ZERO_BLOCK="$LZB" LAG_ADV_BASIS="$ADV" EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge \
  > $OUT/$TAG.log 2>&1
echo "EXIT=$? ($TAG lzb=$LZB adv=$ADV)" >> $OUT/$TAG.log
