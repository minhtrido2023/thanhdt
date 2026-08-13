#!/usr/bin/env bash
# compute_active_nav_all.sh — refresh data/execution_logs/active_nav_<account>.json cho MỌI
# account live (SpaceX, ZaloPay, ...), chạy TRƯỚC inject_discretionary_orders.sh (20:30 ICT) —
# injector fail-closed nếu computed_at không phải HÔM NAY, nên bản refresh này phải mới hơn.
#
# Thêm 2026-08-13 sau khi phát hiện compute_active_nav.py trước đó KHÔNG có cron nào gọi —
# injector chỉ chạy được nhờ ai đó chạy tay compute_active_nav.py trước. Cùng lúc phát hiện +
# sửa bug TZ thật trong compute_active_nav.py (date.today() trần thay vì today_ict(), §16).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true
PY="${DNA_PYEXE:-python3}"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%F %H:%M ICT')"

LIVE_LABELS="$(cd "$WC_ROOT" && python3 -c "from trading_bot.config import live_dnse_labels; print(' '.join(live_dnse_labels()))" 2>/dev/null)"
if [ -z "$LIVE_LABELS" ]; then
  echo "[compute_active_nav_all] $NOW_ICT — không lấy được live labels, dừng." >&2
  exit 1
fi

rc=0
for ACCT in $LIVE_LABELS; do
  echo "=== [compute_active_nav_all] $ACCT — $NOW_ICT ==="
  (cd "$WC_ROOT" && "$PY" mike/bin/compute_active_nav.py --account "$ACCT") || rc=1
done
exit $rc
