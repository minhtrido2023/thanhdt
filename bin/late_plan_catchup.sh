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
ran_chain=0
for acct in $labels; do
  plan="$PLAN_DIR/plan_${acct}_${PLAN_DATE}.json"
  # JSON is the authority, not mtime: reject wrong date, malformed or already-approved plans.
  status="$(python3 - "$plan" "$PLAN_DATE" <<'PY'
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
)"
  case "$status" in
    READY|MISSING) echo "[late_plan] $acct $PLAN_DATE — $status, no-op."; continue ;;
    APPROVED|INVALID) echo "[late_plan] $acct $PLAN_DATE — $status, REFUSE." >&2; rc=1; continue ;;
  esac
  lock="$LOCK_DIR/late_plan_${acct}_${PLAN_DATE}.lock"
  if ! mkdir "$lock" 2>/dev/null; then echo "[late_plan] $acct — lock held, no-op."; continue; fi
  (
    trap 'rmdir "$lock"' EXIT
    if [ "$ran_chain" = 0 ]; then
      echo "[late_plan] $acct $PLAN_DATE — catch-up L1→L2→merge→inject."
      PARK_CHAIN_PLAN_DIR="$PLAN_DIR" "$ROOT/bin/park_trim_daily.sh" || exit 1
      PARK_CHAIN_PLAN_DIR="$PLAN_DIR" "$ROOT/bin/jit_unpark_daily.sh" || exit 1
      PARK_CHAIN_PLAN_DIR="$PLAN_DIR" "$ROOT/bin/merge_park_daily.sh" --write || exit 1
      "$ROOT/bin/inject_discretionary_orders.sh" || exit 1
      ran_chain=1
    fi
    "$ROOT/bin/send_plan_report.sh" --account "$acct" --second-chance || exit 1
  ) || rc=1
done
exit "$rc"
