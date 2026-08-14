#!/usr/bin/env bash
# park_trim_daily.sh — L1 park-target compliance cho MỌI account live. Ghi artifact
# data/trade_plans/park_trim_<account>_<plan_date>.json (plan_date = T+1), là nguồn bằng chứng
# mà merge_park_orders.py VÀ cổng approve_plan_with_jit.sh cùng đọc.
#
# Vị trí trong chuỗi (19:30 ICT): DollarBill ghi plan ~19:0x → [L1 ĐÂY 19:30] →
# jit_unpark_daily.sh 19:40 → merge_park_daily.sh 20:20 → inject_discretionary_orders.sh 20:30
# → send_plan_report.sh 21:00. Script CHỈ ĐỌC broker; không đặt lệnh, không ghi plan.
#
# RÀNG BUỘC CỨNG — chỉ chạy SAU 15:00 ICT của một NGÀY GIAO DỊCH: compute_park_trim.py lấy giá
# qua DNSE close_price(), trả 0 khi phiên chưa đóng (đúng cái đã xảy ra 2026-08-07). Guard bên
# dưới là bản cưỡng chế BẰNG CODE của ràng buộc đó — giờ cron một mình không đủ (chạy tay,
# cron bị sửa giờ, hay đổi TZ đều vượt qua được một dòng comment).
#
# Cài 2026-08-14 (job Taylor_20260814_142151) theo §6 mà user duyệt trong
# mike/agents/Taylor/research/park_merge_wire_20260811.md. Xem mike/kb/cron_registry.md.
#
# Test không đụng production: PARK_CHAIN_PLAN_DIR=<thư mục sandbox> ./park_trim_daily.sh
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
# shellcheck source=/dev/null
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true
PY="${DNA_PYEXE:-python3}"
PLAN_DIR="${PARK_CHAIN_PLAN_DIR:-$WC_ROOT/data/trade_plans}"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%F %H:%M ICT')"

EXTRA_ARGS="${1:-}"   # cho phép truyền --json khi test

# Ngày plan T+1 + 2 guard. now_ict()/today_ict() của trading_bot.vn_market tự neo ICT, KHÔNG
# phụ thuộc TZ của process gọi vào (coding_guidelines §16).
PLAN_DATE="$(cd "$WC_ROOT" && python3 -c "
import sys
from trading_bot.vn_market import now_ict, today_ict, is_holiday, next_trading_day
n = now_ict()
if n.weekday() >= 5 or is_holiday(n.date()):
    sys.exit('NOT_TRADING_DAY')
if n.hour < 15:
    sys.exit('BEFORE_1500_ICT')
print(next_trading_day(today_ict()))
" 2>&1)"
case "$PLAN_DATE" in
  NOT_TRADING_DAY) echo "[park_trim] $NOW_ICT — hôm nay không phải ngày giao dịch, bỏ qua."; exit 0 ;;
  BEFORE_1500_ICT) echo "[park_trim] $NOW_ICT — CHƯA tới 15:00 ICT, TỪ CHỐI chạy (giá đóng cửa chưa có; xem header)." >&2; exit 1 ;;
esac
if [[ ! "$PLAN_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "[park_trim] $NOW_ICT — không tính được ngày plan T+1: $PLAN_DATE" >&2
  exit 1
fi

LIVE_LABELS="$(cd "$WC_ROOT" && python3 -c "from trading_bot.config import live_dnse_labels; print(' '.join(live_dnse_labels()))" 2>/dev/null)"
if [ -z "$LIVE_LABELS" ]; then
  echo "[park_trim] $NOW_ICT — không lấy được live labels, dừng." >&2
  exit 1
fi

rc=0
for ACCT in $LIVE_LABELS; do
  echo "=== [park_trim] $ACCT plan_date=$PLAN_DATE — $NOW_ICT ==="
  # shellcheck disable=SC2086  # EXTRA_ARGS cố ý tách từ (cùng khuôn inject_discretionary_orders.sh)
  (cd "$WC_ROOT" && "$PY" mike/bin/compute_park_trim.py --account "$ACCT" \
      --out "$PLAN_DIR/park_trim_${ACCT}_${PLAN_DATE}.json" $EXTRA_ARGS) || rc=1
done
exit $rc
