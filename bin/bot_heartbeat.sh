#!/usr/bin/env bash
# bot_heartbeat.sh <account> [plan_date] [thread_id]
# Giám sát bot_execute.py trong giờ giao dịch — chạy qua cron mỗi 5' 09:00-15:00 ICT T2-T6.
#
# Im lặng hoàn toàn (không báo Discord, không cố restart) trong các trường hợp KHÔNG cần
# giám sát:
#   (a) Ngày không có trading plan (file không tồn tại hoặc 0 lệnh)
#   (b) Plan hôm nay đã chạy XONG (mọi order state["parents"][*]["done"]==true) — tự động
#       coi như ngày không có trading plan từ lúc đó, dù còn trong giờ giao dịch
#   (c) Giờ nghỉ trưa 11:30-13:00 ICT (bot bị stop chủ động qua cron riêng, không phải chết)
#   (d) Ngoài giờ giao dịch (trước 09:00 hoặc sau 14:50 ICT) — process tự thoát là bình thường
#
# Chỉ khi CÓ plan thật + CHƯA xong + đang trong giờ giao dịch (trừ giờ nghỉ trưa) mới:
#   - process chết → tự restart (setsid) rồi báo kết quả (thành công/thất bại)
#   - process sống → digest lệnh mới (PLACE/FILL/DONE/PLACE_FAIL) từ journal, hoặc heartbeat
#     im lặng nếu chưa có gì mới
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true

ACCOUNT="${1:?usage: bot_heartbeat.sh <account> [plan_date] [thread_id]}"
PLAN_DATE="${2:-$(TZ=Asia/Ho_Chi_Minh date +%Y-%m-%d)}"
# Trading Daily thread — mọi giao dịch hàng ngày gộp về 1 thread cố định.
THREAD_ID="${3:-trading_daily}"   # tên trong kb/discord_channels.json

JOURNAL="$WC_ROOT/data/execution_logs/exec_${ACCOUNT}_${PLAN_DATE}_journal.csv"
PLAN_FILE="$WC_ROOT/data/trade_plans/plan_${ACCOUNT}_${PLAN_DATE}.json"
EXEC_STATE_FILE="$WC_ROOT/data/execution_logs/exec_${ACCOUNT}_${PLAN_DATE}_state.json"
STATE_DIR="$ROOT/state/bot_heartbeat"
mkdir -p "$STATE_DIR"
LASTLINE_FILE="$STATE_DIR/${ACCOUNT}_${PLAN_DATE}.lastline"
DEADFLAG_FILE="$STATE_DIR/${ACCOUNT}_${PLAN_DATE}.dead_notified"
DONEFLAG_FILE="$STATE_DIR/${ACCOUNT}_${PLAN_DATE}.plan_done_announced"

NOW_ICT="$(TZ=Asia/Ho_Chi_Minh date +'%H:%M ICT')"
NOW_HHMM="$(TZ=Asia/Ho_Chi_Minh date +'%H%M')"

_notify() {
  [ -n "$THREAD_ID" ] || { echo "$1"; return; }
  "$ROOT/bin/notify_thread.sh" "$1" "$THREAD_ID" 2>/dev/null || true
}

_restart_bot() {
  local rlog="$ROOT/logs/run_bot_${ACCOUNT}_autoheal_$(TZ=Asia/Ho_Chi_Minh date +%Y%m%d_%H%M%S).log"
  ( cd "$WC_ROOT" && setsid env TZ=Asia/Ho_Chi_Minh python3 -u bot_execute.py \
      --account "$ACCOUNT" --date "$PLAN_DATE" --auto-otp \
      > "$rlog" 2>&1 < /dev/null & )
  sleep 5
  pgrep -f "bot_execute.py --account $ACCOUNT --date $PLAN_DATE" | head -1 || true
}

# Render SỔ LỆNH giống app DNSE từ journal — dùng cho cả digest 5' lẫn message hoàn tất
# kế hoạch (xem mục 0b).
_orderbook_digest() {
  python3 - "$JOURNAL" "$ACCOUNT" "$NOW_ICT" "$N_ORDERS" << 'PYEOF'
import csv, sys
from collections import OrderedDict

journal, account, now_ict, n_orders = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])

children = OrderedDict()   # child_oid -> chi tiết lệnh con
parent_done = {}
parent_wait = {}

with open(journal, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        ev, pid = row["event"], row["parent_id"]
        oid = row.get("child_oid") or ""
        if ev == "PLACE":
            children[oid] = {"ts": row["ts"][11:16], "ticker": row["ticker"],
                             "side": row["side"], "qty": float(row["qty"] or 0),
                             "limit_px": float(row["price"] or 0), "filled": 0.0,
                             "fill_px": None, "cancelled": False}
            parent_wait.pop(pid, None)
        elif ev == "FILL" and oid in children:
            c = children[oid]
            c["filled"] = max(c["filled"], float(row["qty"] or 0))  # journal ghi lũy kế/child
            c["fill_px"] = float(row["price"] or 0) or c["fill_px"]
        elif ev in ("CANCEL", "CANCELLED") and oid in children:
            children[oid]["cancelled"] = True
        elif ev == "DONE":
            parent_done[pid] = row.get("note") or "khớp đủ"
            parent_wait.pop(pid, None)
        elif ev in ("WAIT_CASH", "WAIT_QUOTA", "WAIT_T2_SETTLEMENT", "PLACE_FAIL") and pid not in parent_done:
            reason = {"WAIT_CASH": "chờ sức mua", "WAIT_QUOTA": "chờ thanh khoản (giới hạn 10% KLGD)",
                      "WAIT_T2_SETTLEMENT": "chờ hàng T+2 về"}.get(ev, row.get("note") or ev)
            parent_wait[pid] = (row["ticker"], row["side"], reason)

def px(v):        # 32500 -> "32.50" như app
    return f"{v/1000:,.2f}" if v else "?"

lines = []
for oid, c in reversed(children.items()):   # mới nhất lên đầu, giống app
    side = "BÁN" if c["side"] == "sell" else "MUA"
    if c["cancelled"]:
        status = "Hủy"
    elif c["filled"] >= c["qty"] > 0:
        status = "Khớp ✅"
    elif c["filled"] > 0:
        status = "Khớp một phần"
    else:
        status = "Chờ khớp"
    shown_px = c["fill_px"] if c["fill_px"] else c["limit_px"]
    lines.append(f"• {c['ts']}  {side} {c['ticker']}  {c['filled']:.0f}/{c['qty']:.0f} @ {px(shown_px)}  — {status}")

for pid, (ticker, side, reason) in parent_wait.items():
    side_vn = "BÁN" if side == "sell" else "MUA"
    lines.append(f"• --:--  {side_vn} {ticker}  0/…  — chưa đặt ({reason})")

n_parent_done = len(parent_done)
lines.append(f"Kế hoạch hôm nay: hoàn tất {n_parent_done}/{n_orders} lệnh"
             + (" — còn lại đang chờ điều kiện." if n_parent_done < n_orders else " — XONG."))
print("\n".join(lines))
PYEOF
}

# ── 0a. Ngày không có plan/lệnh → im lặng hoàn toàn ──────────────────────────
if [ ! -f "$PLAN_FILE" ]; then
  exit 0
fi
N_ORDERS="$(python3 -c "import json; print(len(json.load(open('$PLAN_FILE')).get('orders', [])))" 2>/dev/null || echo 0)"
if [ "${N_ORDERS:-0}" -eq 0 ] 2>/dev/null; then
  exit 0
fi

# ── 0b. Plan hôm nay đã khớp xong toàn bộ → BÁO HOÀN TẤT 1 LẦN rồi im lặng ───
# Trước 2026-07-07 chiều: đi thẳng vào im lặng → cú khớp CUỐI CÙNG của ngày không bao
# giờ được báo chi tiết (VCB 100cp @61.10 khớp 13:00:22, bot thoát 13:01, heartbeat
# 13:05 thấy all-done → câm luôn — user chất vấn "khớp lệnh gì, bao nhiêu, giá nào?").
# Giờ: lần ĐẦU phát hiện all-done → gửi sổ lệnh đầy đủ + lời chào kết thúc, đặt cờ,
# các nhịp sau mới im lặng.
if [ -f "$EXEC_STATE_FILE" ]; then
  ALL_DONE="$(python3 -c "
import json
d = json.load(open('$EXEC_STATE_FILE'))
parents = d.get('parents', {})
print('yes' if parents and all(p.get('done') for p in parents.values()) else 'no')
" 2>/dev/null || echo no)"
  if [ "$ALL_DONE" = "yes" ]; then
    if [ ! -f "$DONEFLAG_FILE" ] && [ -f "$JOURNAL" ]; then
      _notify "✅ **Account $ACCOUNT — HOÀN TẤT toàn bộ kế hoạch hôm nay ($NOW_ICT)** — bot đã nghỉ, không còn gì để làm. Sổ lệnh cuối cùng:
$(_orderbook_digest)"
      touch "$DONEFLAG_FILE"
    fi
    rm -f "$DEADFLAG_FILE" "$LASTLINE_FILE"
    exit 0
  fi
fi

# ── 0c. Giờ nghỉ trưa (11:30-13:00 ICT) — bot bị stop chủ động, không phải chết ──
if [ "$NOW_HHMM" -ge 1130 ] && [ "$NOW_HHMM" -lt 1300 ]; then
  exit 0
fi

# ── 0d. Ngoài giờ giao dịch — process tự thoát là bình thường ────────────────
if [ "$NOW_HHMM" -ge 1450 ] || [ "$NOW_HHMM" -lt 0900 ]; then
  exit 0
fi

# ── 0e. Grace window quanh giờ cron khởi động bot (09:05 sáng, 13:00 chiều) ──
# Heartbeat chạy đúng :00/:05 RACE với cron run_bot cùng phút: pgrep chưa thấy process
# (đang spawn) → tưởng chết → spawn bot THỨ HAI + bắn "BOT DIE → AUTO-RESTART" giả
# (flock cứu khỏi double-order nhưng message gây hiểu lầm "bot bật tắt liên tục" —
# xảy ra thật 09:00 + 13:00 ngày 2026-07-07). Trong cửa sổ grace: bỏ qua dead-check,
# để cron chính thức khởi động bot; digest vẫn chạy bình thường nếu bot đã sống.
if { [ "$NOW_HHMM" -ge 0900 ] && [ "$NOW_HHMM" -lt 0910 ]; } || \
   { [ "$NOW_HHMM" -ge 1300 ] && [ "$NOW_HHMM" -lt 1310 ]; }; then
  GRACE=1
else
  GRACE=0
fi

# ── 1. Process liveness (chỉ tới đây khi: có plan thật + chưa xong + trong giờ) ──
PID="$(pgrep -f "bot_execute.py --account $ACCOUNT --date $PLAN_DATE" | head -1 || true)"

if [ -z "$PID" ] && [ "$GRACE" = "1" ]; then
  exit 0   # bot chưa được cron khởi động / đang spawn — không phải chết
fi

if [ -z "$PID" ]; then
  NEWPID="$(_restart_bot)"
  if [ -n "$NEWPID" ]; then
    _notify "🟡 **BOT DIE → AUTO-RESTART OK** — account **$ACCOUNT** ($PLAN_DATE) chết lúc $NOW_ICT, đã tự restart (PID $NEWPID, setsid). Đang resume state, theo dõi tiếp."
    rm -f "$DEADFLAG_FILE"
  else
    if [ ! -f "$DEADFLAG_FILE" ]; then
      _notify "🔴 **BOT DIE — AUTO-RESTART THẤT BẠI** — account **$ACCOUNT** ($PLAN_DATE) chết lúc $NOW_ICT, tự restart KHÔNG thành công. Cần can thiệp tay ngay."
      touch "$DEADFLAG_FILE"
    fi
  fi
  exit 0
fi
rm -f "$DEADFLAG_FILE"

# ── 2. Journal delta since last check ────────────────────────────────────────
if [ ! -f "$JOURNAL" ]; then
  _notify "⚠️ [$NOW_ICT] bot $ACCOUNT PID=$PID đang sống nhưng chưa có journal file."
  exit 0
fi

LAST="$(cat "$LASTLINE_FILE" 2>/dev/null || echo 0)"
TOTAL="$(wc -l < "$JOURNAL" | tr -d ' ')"

if [ "$TOTAL" -le "$LAST" ]; then
  # No new events — silent heartbeat every 5' (only text, no Discord spam beyond schedule)
  _notify "🟢 [$NOW_ICT] bot $ACCOUNT sống (PID $PID), không có event mới từ lần check trước."
  echo "$TOTAL" > "$LASTLINE_FILE"
  exit 0
fi

echo "$TOTAL" > "$LASTLINE_FILE"

# ── 3. Digest = SỔ LỆNH giống app DNSE (dùng chung _orderbook_digest với message
#    hoàn tất kế hoạch ở mục 0b — một nguồn render duy nhất).
MSG="🟢 **Bot $ACCOUNT — sổ lệnh $NOW_ICT**
$(_orderbook_digest)"

echo "$MSG"
_notify "$MSG"
