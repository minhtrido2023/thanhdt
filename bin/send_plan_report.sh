#!/usr/bin/env bash
# send_plan_report.sh — đọc plan T+1 → gửi summary qua Telegram + Discord
# Schedule: 19:30 ICT trading days (cron: 30 12 * * 1-5)
#
# Nếu không tìm thấy plan (do BQ stale → DollarBill bị block): gửi cảnh báo thay thế.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "$ROOT/../wc_env.sh" ] && source "$ROOT/../wc_env.sh" 2>/dev/null || true

WORKDIR="${WORKDIR_8L:-/home/trido/thanhdt/WorkingClaude}"
TODAY="$(date +%Y-%m-%d)"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT')"

# Discord: mike fleet plan channel — topic 1521183164364754974 (server 1519342571812421753)
DISCORD_PLAN_CHANNEL="1521183164364754974"

# Tìm plan file mới nhất (Bill ghi vào data/plan_SpaceX_<date>.json)
PLAN_FILE="$(ls -t "$WORKDIR"/data/plan_SpaceX_*.json 2>/dev/null | head -1)"

if [ -z "$PLAN_FILE" ] || [ ! -f "$PLAN_FILE" ]; then
  MSG="⚠️ [$TODAY $NOW_ICT] Plan T+1 KHÔNG TÌM THẤY — BQ có thể stale hoặc DollarBill chưa chạy. Kiểm tra: mike/logs/bq_freshness.log"
  echo "$MSG"
  "$ROOT/bin/notify.sh" "$MSG" 2>/dev/null || true
  "$ROOT/bin/notify_thread.sh" "$MSG" "$DISCORD_PLAN_CHANNEL" 2>/dev/null || true
  exit 0
fi

SUMMARY=$(python3 - "$PLAN_FILE" "$TODAY" "$NOW_ICT" << 'PY'
import sys, json

try:
    plan_file, today, now_ict = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(plan_file) as f:
        plan = json.load(f)

    acct   = plan.get("account", "SpaceX")
    date   = plan.get("date", "?")
    state  = plan.get("market_state", plan.get("state", "?"))
    nav    = plan.get("nav_estimate", plan.get("nav", None))
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
            price  = o.get("price","ATO/ATC")
            lines.append(f"  {side} {ticker} x{qty} @ {price}")
        if len(orders) > 10:
            lines.append(f"  ... +{len(orders)-10} lệnh khác")
    else:
        lines.append("Không có lệnh (giữ nguyên danh mục).")

    print("\n".join(lines))

except Exception as e:
    print(f"[parse error: {e}]")
    try:
        with open(sys.argv[1]) as f:
            print(f.read(600))
    except Exception:
        pass
PY
)

echo "$SUMMARY"
"$ROOT/bin/notify.sh" "$SUMMARY" 2>/dev/null || true
"$ROOT/bin/notify_thread.sh" "$SUMMARY" "$DISCORD_PLAN_CHANNEL" 2>/dev/null || true
echo "[send_plan_report] Done — $NOW_ICT"
