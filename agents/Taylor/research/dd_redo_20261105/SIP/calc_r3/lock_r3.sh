#!/usr/bin/env bash
# Khoá md5 upstream SIP r3 TRƯỚC khi chạy model (model không tự ghi LOCK). Chạy: bash lock_r3.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
WC=/home/trido/thanhdt/WorkingClaude
{
  echo "# LOCK md5 SIP r3 — job Taylor_20261108_180132 — ghi lúc $(TZ=Asia/Ho_Chi_Minh date '+%Y-%m-%dT%H:%M:%S%z') TRƯỚC khi chạy model_r3.py"
  md5sum SIP/calc_r3/assumptions_r3.json SIP/calc_r3/model_r3.py SIP/calc_r3/px_sip_r3.sql SIP/calc_r3/px_sip_r3_20261106.csv \
    SIP/calc/model_sip_r2.py SIP/calc/model_sip_r2_out.json SIP/SUMMARY_r2.json SIP/SUMMARY_r1_stale.json \
    _common_g2r2/ddr2.py _common_g2r2/px_g2r2_20261104.csv _common_g2/ddg2.py _shared/wpct.py \
    TOP5D_CORRECTIONS_20261108.md STANDARD_r2.md ../dd_SIP_20261101/calc/notes_read.md \
    $WC/deposit_rate_vn.py $WC/data/deposit_rate_vn_events.csv $WC/cctg_rate_vn.py $WC/data/cctg_rate_vn_events.csv
} > SIP/calc_r3/LOCK_md5.txt
cat SIP/calc_r3/LOCK_md5.txt
