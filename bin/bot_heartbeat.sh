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
THREAD_ID="${3:-1521470705563340910}"

JOURNAL="$WC_ROOT/data/execution_logs/exec_${ACCOUNT}_${PLAN_DATE}_journal.csv"
PLAN_FILE="$WC_ROOT/data/trade_plans/plan_${ACCOUNT}_${PLAN_DATE}.json"
EXEC_STATE_FILE="$WC_ROOT/data/execution_logs/exec_${ACCOUNT}_${PLAN_DATE}_state.json"
STATE_DIR="$ROOT/state/bot_heartbeat"
mkdir -p "$STATE_DIR"
LASTLINE_FILE="$STATE_DIR/${ACCOUNT}_${PLAN_DATE}.lastline"
DEADFLAG_FILE="$STATE_DIR/${ACCOUNT}_${PLAN_DATE}.dead_notified"

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

# ── 0a. Ngày không có plan/lệnh → im lặng hoàn toàn ──────────────────────────
if [ ! -f "$PLAN_FILE" ]; then
  exit 0
fi
N_ORDERS="$(python3 -c "import json; print(len(json.load(open('$PLAN_FILE')).get('orders', [])))" 2>/dev/null || echo 0)"
if [ "${N_ORDERS:-0}" -eq 0 ] 2>/dev/null; then
  exit 0
fi

# ── 0b. Plan hôm nay đã khớp xong toàn bộ → tự coi như ngày không có plan ────
if [ -f "$EXEC_STATE_FILE" ]; then
  ALL_DONE="$(python3 -c "
import json
d = json.load(open('$EXEC_STATE_FILE'))
parents = d.get('parents', {})
print('yes' if parents and all(p.get('done') for p in parents.values()) else 'no')
" 2>/dev/null || echo no)"
  if [ "$ALL_DONE" = "yes" ]; then
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

# ── 1. Process liveness (chỉ tới đây khi: có plan thật + chưa xong + trong giờ) ──
PID="$(pgrep -f "bot_execute.py --account $ACCOUNT --date $PLAN_DATE" | head -1 || true)"

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

# ── 3. Digest = SỔ LỆNH giống app DNSE (user yêu cầu 2026-07-07: message bot phải đối
#    chiếu 1-1 được với sổ lệnh trong app — mỗi dòng 1 lệnh con: giờ đặt, Mua/Bán, mã,
#    KL khớp/KL đặt, giá, trạng thái — thay vì thống kê event nội bộ PID/parent/delta
#    "chẳng liên quan gì" với cái user nhìn thấy trong app).
MSG="$(python3 - "$JOURNAL" "$ACCOUNT" "$NOW_ICT" "$N_ORDERS" << 'PYEOF'
import csv, sys
from collections import OrderedDict, defaultdict

journal, account, now_ict, n_orders = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])

children = OrderedDict()   # child_oid -> {ts,ticker,side,qty,limit_px,filled,fill_px,cancelled}
parent_done = {}           # parent_id -> note
parent_wait = {}           # parent_id -> (ticker, side, latest wait/fail note)
parent_of_child = {}

with open(journal, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        ev, pid = row["event"], row["parent_id"]
        oid = row.get("child_oid") or ""
        if ev == "PLACE":
            children[oid] = {"ts": row["ts"][11:16], "ticker": row["ticker"],
                             "side": row["side"], "qty": float(row["qty"] or 0),
                             "limit_px": float(row["price"] or 0), "filled": 0.0,
                             "fill_px": None, "cancelled": False}
            parent_of_child[oid] = pid
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

lines = [f"🟢 **Bot {account} — sổ lệnh {now_ict}**"]
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
)"

echo "$MSG"
_notify "$MSG"
