#!/usr/bin/env bash
# send_plan_report.sh — đọc plan T+1 → gửi summary qua Telegram + Discord
# Schedule: 19:30 ICT trading days (cron: 30 12 * * 1-5)
#
# Verify ARTIFACT thật (file plan có đúng ngày T+1, đúng schema) — KHÔNG tin vào job
# status của dispatch.sh (job có thể báo "timeout" dù plan đã ghi xong, xem sự cố
# 2026-07-01: DollarBill_20260701_103128 timeout nhưng plan_SpaceX_2026-07-02.json
# hợp lệ). Nếu KHÔNG tìm thấy artifact hợp lệ → ESCALATE thật (bus question event,
# Mike tự đọc ở phiên sau) thay vì chỉ gửi 1 tin Telegram rồi im lặng chờ người phát hiện.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true

WORKDIR="${WORKDIR_8L:-/home/trido/thanhdt/WorkingClaude}"
TODAY="$(date +%Y-%m-%d)"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT')"
ACCOUNT="SpaceX"

# Discord: DollarBill trading-plan channel — tách riêng khỏi Trading Daily (2026-07-01,
# user chỉ đạo) để tránh spam các topic khác khi Mike dispatch DollarBill từ bất kỳ đâu.
DISCORD_PLAN_CHANNEL="1521183164364754974"

EXPECTED_DATE="$(cd "$WORKDIR" && python3 -c "
import datetime as dt
from trading_bot.vn_market import next_trading_day
print(next_trading_day(dt.date.today()))
" 2>/dev/null)"

# Plan file mới nhất theo mtime (Bill ghi vào data/trade_plans/plan_<account>_<date>.json)
PLAN_FILE="$(ls -t "$WORKDIR"/data/trade_plans/plan_${ACCOUNT}_*.json 2>/dev/null | head -1)"

RESULT=$(cd "$WORKDIR" && python3 - "$PLAN_FILE" "$EXPECTED_DATE" "$TODAY" "$NOW_ICT" "$ACCOUNT" << 'PY'
import sys, json

plan_file, expected_date, today, now_ict, acct = sys.argv[1:6]

def escalate(reason, detail=""):
    print("ESCALATE")
    print(reason)
    print(detail)

if not plan_file:
    escalate("no_plan_file", f"Không có file plan_{acct}_*.json nào trong data/trade_plans/.")
    sys.exit(0)

try:
    with open(plan_file) as f:
        plan = json.load(f)
except Exception as e:
    escalate("plan_unparseable", f"{plan_file}: {e}")
    sys.exit(0)

plan_date = plan.get("plan_date", plan.get("date"))
if expected_date and plan_date != expected_date:
    escalate("plan_date_stale",
              f"File mới nhất ({plan_file}) có plan_date={plan_date!r}, kỳ vọng {expected_date!r} "
              f"(T+1 từ hôm nay {today}). DollarBill có thể chưa chạy hoặc bị lỗi chiều nay.")
    sys.exit(0)

if "orders" not in plan:
    escalate("plan_missing_orders", f"{plan_file}: thiếu field 'orders' — schema không hợp lệ.")
    sys.exit(0)

# --- Valid plan found: build normal summary ---
date   = plan_date or "?"
state  = plan.get("state_name", plan.get("market_state", plan.get("state", "?")))
nav    = plan.get("nav_basis", {}).get("account_nav") if isinstance(plan.get("nav_basis"), dict) \
         else plan.get("nav_estimate", plan.get("nav", None))
orders = plan.get("orders", [])

lines = [f"📋 PLAN T+1 — {acct} ({date}) | {today} {now_ict}"]

nav_str = f"{nav:,.0f}đ" if isinstance(nav, (int, float)) else str(nav) if nav else "N/A"
lines.append(f"Regime: {state} | NAV ước: {nav_str}")

if orders:
    buys  = [o for o in orders if str(o.get("side","")).upper() in ("BUY","MUA","B")]
    sells = [o for o in orders if str(o.get("side","")).upper() in ("SELL","BAN","S")]
    lines.append(f"Lệnh: {len(buys)} mua, {len(sells)} bán ({len(orders)} tổng)")
    for o in orders[:10]:
        side   = o.get("side","?")
        ticker = o.get("ticker","?")
        qty    = o.get("quantity", o.get("qty","?"))
        price  = o.get("ref_price", o.get("price","ATO/ATC"))
        price_str = f"{price:,.0f}" if isinstance(price, (int, float)) else price
        lines.append(f"  {side} {ticker} x{qty} @ {price_str}")
    if len(orders) > 10:
        lines.append(f"  ... +{len(orders)-10} lệnh khác")
else:
    lines.append("Không có lệnh (giữ nguyên danh mục).")

print("OK")
print("\n".join(lines))
PY
)

STATUS="$(echo "$RESULT" | head -1)"

if [ "$STATUS" = "ESCALATE" ]; then
  REASON="$(echo "$RESULT" | sed -n '2p')"
  DETAIL="$(echo "$RESULT" | tail -n +3)"
  MSG="🔴 [$TODAY $NOW_ICT] Plan T+1 CHƯA SẴN SÀNG ($REASON) — $DETAIL Cần Mike hoặc user kiểm tra thủ công, KHÔNG tự phục hồi."
  echo "$MSG"
  "$ROOT/bin/notify.sh" "$MSG" 2>/dev/null || true
  "$ROOT/bin/notify_thread.sh" "$MSG" "$DISCORD_PLAN_CHANNEL" 2>/dev/null || true
  "$ROOT/bin/append_event.sh" Mike question "plan-t1-not-ready" \
    "{\"reason\":\"$REASON\",\"detail\":$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$DETAIL"),\"expected_date\":\"$EXPECTED_DATE\",\"account\":\"$ACCOUNT\",\"checked_at\":\"$TODAY $NOW_ICT\"}" \
    2>/dev/null || true
  exit 0
fi

SUMMARY="$(echo "$RESULT" | tail -n +2)"
echo "$SUMMARY"
"$ROOT/bin/notify.sh" "$SUMMARY" 2>/dev/null || true
"$ROOT/bin/notify_thread.sh" "$SUMMARY" "$DISCORD_PLAN_CHANNEL" 2>/dev/null || true
echo "[send_plan_report] Done — $NOW_ICT"
