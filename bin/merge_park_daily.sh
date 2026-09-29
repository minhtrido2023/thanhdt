#!/usr/bin/env bash
# merge_park_daily.sh — gộp đề xuất bán PARK của L1 (park_trim) + L2 (jit_unpark) vào orders[]
# của plan T+1, cho MỌI account live. Đây là WRITER DUY NHẤT của vùng lệnh bán PARK trong plan
# (đường merge cũ trong approve_plan_with_jit.sh đã gỡ HẲN 2026-08-11 — hai writer trên cùng
# một vùng chính là cấu hình sinh ra sự cố bán trùng 1.600cp ngày 08-07).
#
# Vị trí trong chuỗi (20:20 ICT): DollarBill ghi plan ~19:0x → park_trim_daily.sh 19:30 →
# jit_unpark_daily.sh 19:40 → [MERGE ĐÂY 20:20] → inject_discretionary_orders.sh 20:30 →
# send_plan_report.sh 21:00. Chọn 20:20 vì: sau compute_active_nav_all.sh 20:15 (không đụng
# nhau — merge thuần file I/O, không gọi DNSE) và trước inject 20:30.
#
# `--write` KHÔNG nằm trong script mà nằm ở DÒNG CRON: merge_park_orders.py mặc định dry-run,
# nên chạy tay `merge_park_daily.sh` (không tham số) là một phiên shadow an toàn, in đúng báo
# cáo sẽ ghi mà không ghi gì.
#
# Cổng duyệt KHÔNG bị chạm: merge_park_orders.py luôn đặt requires_user_approval=True và TỪ
# CHỐI plan đã có chữ ký (rc=1) trừ khi --force-clear-approval, mà cờ đó lại XOÁ chữ ký. Plan
# vẫn phải qua user duyệt như mọi ngày.
#
# Mã thoát của merge_park_orders.py: 0 = OK (đã ghi khi có --write) · 1 = REFUSED/fail-closed,
# KHÔNG ghi gì · 2 = không có plan T+1. Wrapper gộp thành rc≠0 để cron_health_check thấy.
#
# Cài 2026-08-14 (job Taylor_20260814_142151) theo §6 mà user duyệt trong
# mike/agents/Taylor/research/park_merge_wire_20260811.md. Xem mike/kb/cron_registry.md.
#
# Test không đụng production: PARK_CHAIN_PLAN_DIR=<thư mục sandbox> ./merge_park_daily.sh --write
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
# shellcheck source=/dev/null
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true
PY="${DNA_PYEXE:-python3}"
PLAN_DIR="${PARK_CHAIN_PLAN_DIR:-$WC_ROOT/data/trade_plans}"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%F %H:%M ICT')"

EXTRA_ARGS="${1:-}"   # dòng cron truyền --write; bỏ trống = shadow (dry-run)

PLAN_DATE="$(cd "$WC_ROOT" && python3 -c "
import sys
from trading_bot.vn_market import now_ict, today_ict, is_holiday, next_trading_day
n = now_ict()
if n.weekday() >= 5 or is_holiday(n.date()):
    sys.exit('NOT_TRADING_DAY')
print(next_trading_day(today_ict()))
" 2>&1)"
case "$PLAN_DATE" in
  NOT_TRADING_DAY) echo "[merge_park] $NOW_ICT — hôm nay không phải ngày giao dịch, bỏ qua."; exit 0 ;;
esac
if [[ ! "$PLAN_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "[merge_park] $NOW_ICT — không tính được ngày plan T+1: $PLAN_DATE" >&2
  exit 1
fi

LIVE_LABELS="$(cd "$WC_ROOT" && python3 -c "from trading_bot.config import live_dnse_labels; print(' '.join(live_dnse_labels()))" 2>/dev/null)"
if [ -z "$LIVE_LABELS" ]; then
  echo "[merge_park] $NOW_ICT — không lấy được live labels, dừng." >&2
  exit 1
fi

rc=0
for ACCT in $LIVE_LABELS; do
  echo "=== [merge_park] $ACCT plan_date=$PLAN_DATE — $NOW_ICT ==="
  # shellcheck disable=SC2086  # EXTRA_ARGS cố ý tách từ (cùng khuôn inject_discretionary_orders.sh)
  (cd "$WC_ROOT" && "$PY" mike/bin/merge_park_orders.py --account "$ACCT" \
      --plan-date "$PLAN_DATE" --plan-dir "$PLAN_DIR" $EXTRA_ARGS) || rc=1
done
exit $rc
