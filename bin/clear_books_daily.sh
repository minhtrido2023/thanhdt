#!/usr/bin/env bash
# clear_books_daily.sh — chạy clear_books.py (SHADOW, chỉ báo cáo) cho plan T+1 của mọi account live.
# Cron 20:45 ICT T2-T6: SAU auto_exit_inject 20:40, TRƯỚC plan_position_drift 20:50 / send_plan_report 21:00.
# KHÔNG đổi plan/journal; chỉ ghi state/clear_books_shadow/<acct>_<plan_date>.json + log. Thiết kế:
# kb/projects/book-clearing-plan-20261029.md. rc≠0 chỉ log (shadow, không báo động) — lý do thật nằm trong log (§29).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true
PY="${DNA_PYEXE:-/home/trido/thanhdt/wc_venv/bin/python}"
NOW="$(TZ='Asia/Ho_Chi_Minh' date +'%Y-%m-%d %H:%M ICT')"
PLAN_DATE="$(cd "$WC_ROOT" && python3 -c "
import datetime as dt
from zoneinfo import ZoneInfo
from trading_bot.vn_market import next_trading_day
print(next_trading_day(dt.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()))" 2>&1)" || {
  echo "=== [clear_books_daily] $NOW — KHÔNG tính được ngày plan T+1: $PLAN_DATE"; exit 1; }
echo "=== [clear_books_daily] $NOW — plan_date=$PLAN_DATE ==="
cd "$ROOT" || exit 1
"$PY" bin/clear_books.py --plan-date "$PLAN_DATE"
rc=$?
echo "=== [clear_books_daily] rc=$rc ==="
exit "$rc"
