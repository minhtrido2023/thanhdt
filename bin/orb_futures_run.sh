#!/usr/bin/env bash
# orb_futures_run.sh — chạy executor ORB VN30F (trading_bot/orb_futures.py) cho 1 account.
#   bin/orb_futures_run.sh [run|funding-alert|plan-block] [--account SpaceX]
# run           : vòng lặp 09:31→14:45 (flock trong Python: gọi lại khi đang chạy ⇒ thoát ngay,
#                 nên cron watchdog mỗi 10' an toàn — resume từ state, KHÔNG đặt lại lệnh).
# funding-alert : nhắc nộp ký quỹ phái sinh khi cờ BẬT và thiếu (đi kèm nhịp egg_transfer_alert).
# plan-block    : in khối plan report.
# Cờ `orb_futures.enabled` (secrets/trading_bot_accounts.json, cấp profile) mặc định TẮT ⇒ DRY-RUN.
# CHƯA cài cron (job Taylor_20261116_162132) — đề xuất dòng cron ở kb/projects/orb-futures-sleeve-20261116.md.
set -euo pipefail
WC=/home/trido/thanhdt/WorkingClaude
MODE="${1:-run}"; shift || true
ACCOUNT=SpaceX
while [ $# -gt 0 ]; do
  case "$1" in
    --account) ACCOUNT="$2"; shift 2 ;;
    *) echo "tham số lạ: $1" >&2; exit 2 ;;
  esac
done
cd "$WC"
export TZ=Asia/Ho_Chi_Minh
case "$MODE" in
  run)           exec timeout 20000 python3 -m trading_bot.orb_futures --account "$ACCOUNT" ;;
  funding-alert) exec timeout 120 python3 -m trading_bot.orb_futures --account "$ACCOUNT" --funding-alert ;;
  plan-block)    exec timeout 60 python3 -m trading_bot.orb_futures --account "$ACCOUNT" --plan-block ;;
  *) echo "mode lạ: $MODE (run|funding-alert|plan-block)" >&2; exit 2 ;;
esac
