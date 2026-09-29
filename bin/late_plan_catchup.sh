#!/usr/bin/env bash
# late_plan_catchup.sh — cứu plan T+1 được publish sau chuỗi PARK cố định 19:30→20:30.
# Chỉ xử lý plan hợp lệ, chưa duyệt và còn thiếu dấu vết của chuỗi; không đặt lệnh.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true
PLAN_DIR="${PARK_CHAIN_PLAN_DIR:-$WC_ROOT/data/trade_plans}"
LOCK_DIR="${LATE_PLAN_LOCK_DIR:-$ROOT/state/locks}"
NOW_ICT="$(TZ=Asia/Ho_Chi_Minh date +'%F %H:%M ICT')"
mkdir -p "$LOCK_DIR"

PLAN_DATE="$(cd "$WC_ROOT" && python3 -c '
from trading_bot.vn_market import now_ict,today_ict,is_holiday,next_trading_day
n=now_ict()
if n.weekday() >= 5 or is_holiday(n.date()): raise SystemExit("NOT_TRADING_DAY")
if n.hour < 21: raise SystemExit("BEFORE_WINDOW")
print(next_trading_day(today_ict()))
' 2>&1)"
case "$PLAN_DATE" in
  NOT_TRADING_DAY|BEFORE_WINDOW) echo "[late_plan] $NOW_ICT — $PLAN_DATE, no-op."; exit 0 ;;
esac
[[ "$PLAN_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || { echo "[late_plan] bad date: $PLAN_DATE" >&2; exit 1; }

labels="$(cd "$WC_ROOT" && python3 -c 'from trading_bot.config import live_dnse_labels;print(" ".join(live_dnse_labels()))')" || exit 1
rc=0

# JSON is the authority, not mtime: reject wrong date, malformed or already-approved plans.
check_status() {
  python3 - "$1" "$2" <<'PY'
import json,sys
try:
 p=json.load(open(sys.argv[1]))
 assert p.get('plan_date',p.get('date')) == sys.argv[2]
 assert isinstance(p.get('orders'),list)
 if p.get('approved_by'): print('APPROVED')
 elif (p.get('park_trim_proposal') or {}).get('_merged_into_orders','').startswith('✅ ĐÃ MERGE'): print('READY')
 else: print('NEEDS_CHAIN')
except FileNotFoundError: print('MISSING')
except Exception: print('INVALID')
PY
}

# Pass 1: chấm trạng thái từng account, quyết định có cần chạy chuỗi hay không.
# park_trim_daily.sh/jit_unpark_daily.sh/merge_park_daily.sh xử lý TẤT CẢ account cùng lúc
# (không nhận --account riêng) — nên chỉ cần MỘT account NEEDS_CHAIN là đủ để chạy 1 lần,
# chạy xong nó sửa luôn account khác đang NEEDS_CHAIN.
needs_chain=0
declare -A status_of
for acct in $labels; do
  plan="$PLAN_DIR/plan_${acct}_${PLAN_DATE}.json"
  status="$(check_status "$plan" "$PLAN_DATE")"
  status_of["$acct"]="$status"
  case "$status" in
    APPROVED|INVALID) echo "[late_plan] $acct $PLAN_DATE — $status, REFUSE." >&2; rc=1 ;;
    MISSING) echo "[late_plan] $acct $PLAN_DATE — $status, no-op." ;;
    NEEDS_CHAIN) needs_chain=1 ;;
  esac
done

if [ "$needs_chain" = 1 ]; then
  lock="$LOCK_DIR/late_plan_chain_${PLAN_DATE}.lock"
  if mkdir "$lock" 2>/dev/null; then
    (
      trap 'rmdir "$lock"' EXIT
      echo "[late_plan] $PLAN_DATE — catch-up L1→L2→merge→inject (1 lần cho mọi account cần)."
      PARK_CHAIN_PLAN_DIR="$PLAN_DIR" "$ROOT/bin/park_trim_daily.sh" || exit 1
      PARK_CHAIN_PLAN_DIR="$PLAN_DIR" "$ROOT/bin/jit_unpark_daily.sh" || exit 1
      PARK_CHAIN_PLAN_DIR="$PLAN_DIR" "$ROOT/bin/merge_park_daily.sh" --write || exit 1
      "$ROOT/bin/inject_discretionary_orders.sh" || exit 1
    ) || rc=1
  else
    echo "[late_plan] chain — lock held, no-op."
  fi
fi

# Pass 2: gửi second-chance cho MỌI account NEEDS_CHAIN hoặc READY — không chỉ account tự
# kích hoạt chain. Bug cũ: account #2 (SpaceX) có thể đã được chain của account #1 (ZaloPay)
# sửa xong TRƯỚC KHI tới lượt nó trong vòng lặp, nên status đọc được là READY và bị bỏ qua
# hoàn toàn (kể cả bước gửi lại) dù plan trên đĩa đã đổi thật từ sau lần gửi 21:00 — Discord
# vẫn hiển thị bản BLOCKED_RECONCILE cũ. second-chance tự idempotent (so md5), gọi thêm cho
# account đã READY từ trước là an toàn (in NO-OP nếu không đổi gì).
for acct in $labels; do
  status="${status_of[$acct]:-}"
  case "$status" in
    NEEDS_CHAIN|READY) ;;
    *) continue ;;
  esac
  lock="$LOCK_DIR/late_plan_send_${acct}_${PLAN_DATE}.lock"
  if ! mkdir "$lock" 2>/dev/null; then echo "[late_plan] $acct — send-lock held, no-op."; continue; fi
  (
    trap 'rmdir "$lock"' EXIT
    "$ROOT/bin/send_plan_report.sh" --account "$acct" --second-chance || exit 1
  ) || rc=1
done
exit "$rc"
