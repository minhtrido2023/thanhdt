#!/usr/bin/env bash
# for_each_live_account.sh <script> [extra args]
#
# Chạy <script> --account <label> [extra args] một lần cho MỖI account thật đang bật tự
# động hàng ngày (secrets/trading_bot_accounts.json: enabled=true, mode="live",
# broker="dnse" — xem trading_bot.config.live_dnse_labels()).
#
# Đây là điểm DUY NHẤT cần biết danh sách account cho các script cron dùng-chung
# (preflight_check.sh, ops_health_check.sh, send_plan_report.sh) — thêm 1 account mới vào
# trading_bot_accounts.json là các script này TỰ ĐỘNG chạy cho account đó, KHÔNG cần sửa
# cron/code gì thêm. Xem kb/account_onboarding_runbook.md.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"

if [ $# -lt 1 ]; then
  echo "usage: for_each_live_account.sh <script> [extra args]" >&2
  exit 1
fi
SCRIPT="$1"; shift

# FAIL-CLOSED: một lỗi import (vd conflict marker trong trading_bot/config.py, sự cố
# 2026-08-14) phải KÊU, không được lặng lẽ biến thành "không có account nào" rồi exit 0 —
# hôm đó preflight/ops_health/EOD của CẢ 2 account bị bỏ qua im lặng, cron thấy rc=0.
# "python lỗi" (rc≠0) khác hẳn "chạy được nhưng danh sách rỗng" (cấu hình thật sự trống).
if ! LABELS="$(cd "$WC_ROOT" && python3 -c "from trading_bot.config import live_dnse_labels; print(' '.join(live_dnse_labels()))")"; then
  MSG="[for_each_live_account] KHÔNG đọc được danh sách account (trading_bot.config lỗi) — BỎ QUA $SCRIPT cho MỌI account. Kiểm tra ngay: cd $WC_ROOT && python3 -c 'import trading_bot.config'"
  echo "$MSG" >&2
  [ -x "$ROOT/bin/notify.sh" ] && "$ROOT/bin/notify.sh" "$MSG" >/dev/null 2>&1
  exit 1
fi
if [ -z "$LABELS" ]; then
  echo "[for_each_live_account] KHÔNG có account nào enabled=true/mode=live/broker=dnse — không chạy gì." >&2
  exit 0
fi

rc=0
for acc in $LABELS; do
  echo "=== $SCRIPT --account $acc ==="
  "$SCRIPT" --account "$acc" "$@" || rc=1
done
exit $rc
