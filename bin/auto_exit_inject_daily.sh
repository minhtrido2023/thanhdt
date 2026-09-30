#!/usr/bin/env bash
# auto_exit_inject_daily.sh — chèn tự động đề xuất SELL vào plan T+1 của MỌI account live khi
# sleeve LAG/BAL/CAPIT tới mốc exit cố định (auto_exit_rules.py), chạy SAU khi DollarBill ghi
# plan (~19:0x) và SAU inject_discretionary_orders.sh 20:30, TRƯỚC send_plan_report 21:00
# (cron 20:40 ICT — xem mike/kb/cron_registry.md mục auto-exit-inject). Lặp account qua
# live_dnse_labels() — thêm account mới tự có, giống inject_discretionary_orders.sh.
#
# KÍCH HOẠT LIVE 2026-09-30, user duyệt Option 2 (bus question
# duyet-merge-auto-exit-lag-bal-capit, job Taylor_20260930_080814/100845). Chỉ CHÈN đề xuất vào
# plan nháp — Mafee chỉ thực thi plan-bound SAU khi user duyệt (human-in-the-loop giữ nguyên).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true
WORKDIR="${WORKDIR_8L:-$WC_ROOT}"
PY="${DNA_PYEXE:-python3}"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%F %H:%M ICT')"

EXTRA_ARGS="${1:-}"   # cho phép truyền --dry-run khi test

LIVE_LABELS="$(cd "$WORKDIR" && python3 -c "from trading_bot.config import live_dnse_labels; print(' '.join(live_dnse_labels()))" 2>/dev/null)"
if [ -z "$LIVE_LABELS" ]; then
  echo "[auto_exit_inject] $NOW_ICT — không lấy được live labels, dừng." >&2
  exit 1
fi

rc=0
for ACCT in $LIVE_LABELS; do
  echo "=== [auto_exit_inject] $ACCT — $NOW_ICT ==="
  (cd "$WORKDIR" && "$PY" mike/bin/auto_exit_inject.py --account "$ACCT" $EXTRA_ARGS) || rc=1
done
exit $rc
