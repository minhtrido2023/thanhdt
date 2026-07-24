#!/usr/bin/env bash
# inject_discretionary_orders.sh — chèn tự động lệnh gom DISCRETIONARY_SPECIAL vào plan T+1
# của MỌI account live, chạy SAU khi DollarBill ghi plan (~19:0x) và TRƯỚC send_plan_report
# 21:00 (cron 20:30 ICT). Lặp account qua live_dnse_labels() — thêm account mới tự có.
#
# KÍCH HOẠT LIVE 2026-07-24 (quant-skeptic CONFIRMED job Taylor_20260724_024201 + 2 việc hardening
# job Taylor_20260724_030732 [dry-run đường DNSE thật phát hiện+fix bug account_id, session guard
# chặn giữa phiên] + user duyệt trực tiếp). Cron: xem mike/kb/cron_registry.md mục
# discretionary-accumulation-inject. Plan vẫn requires_user_approval → human gate giữ nguyên; chỉ
# CHÈN lệnh vào plan, không tự đặt lệnh thật.
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
  echo "[inject_discretionary] $NOW_ICT — không lấy được live labels, dừng." >&2
  exit 1
fi

rc=0
for ACCT in $LIVE_LABELS; do
  echo "=== [inject_discretionary] $ACCT — $NOW_ICT ==="
  (cd "$WORKDIR" && "$PY" mike/bin/discretionary_accumulation_inject.py --account "$ACCT" $EXTRA_ARGS) || rc=1
done
exit $rc
