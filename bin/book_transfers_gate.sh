#!/usr/bin/env bash
# book_transfers_gate.sh — SOURCE file (không chạy trực tiếp). Hàm `book_transfers_gate ACCOUNT DATE LOG`.
#
# Một nơi duy nhất định nghĩa "áp book_transfers TRƯỚC bot_execute" cho MỌI đường khởi động bot:
# run_bot.sh (cron 09:05/13:00) và _restart_bot của bot_heartbeat.sh (autoheal gọi thẳng bot_execute,
# trước đây bỏ qua bước này). Cần biến: ROOT (mike/), WC_ROOT. Thông báo đi qua notify_thread.sh +
# append_event.sh (cả hai lỗi đều nuốt). Mọi output hiển thị đi stderr (autoheal bắt stdout bằng $(...)).
#
# Trả về:  0 = cho chạy bot  ·  khác 0 = KHÔNG chạy bot (caller thoát/không restart)
#   apply rc 0          → 0
#   apply rc 3 (PAUSE)  → 0, cảnh báo (lệnh gốc đã khôi phục, bot chạy bình thường)
#   apply rc khác       → plan còn transfer chưa APPLIED/PAUSED ⇒ trả rc (fail-closed: lệnh đã giảm mà
#                         chuyển nhãn không xong = đoán)
#                         plan KHÔNG có transfer chờ (kể cả cờ clearing TẮT) ⇒ chỉ cảnh báo + bus, trả 0

_bt_pending_count() {   # $1 = plan json; in số transfer chưa APPLIED/PAUSED (không đọc được plan ⇒ 0)
  python3 -I -c '
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    print(0); sys.exit()
xs = d.get("book_transfers") if isinstance(d, dict) else None
if not xs:
    print(0)
elif not isinstance(xs, list):
    print(1)
else:
    print(sum(1 for x in xs if not (isinstance(x, dict) and x.get("status") in ("APPLIED", "PAUSED"))))
' "$1" 2>/dev/null || echo 0
}

book_transfers_gate() {
  local acct="$1" date="$2" log="$3" rc=0 out pend plan tid="trading_daily"
  plan="$WC_ROOT/data/trade_plans/plan_${acct}_${date}.json"
  out="$(mktemp)"
  python3 "$ROOT/bin/apply_book_transfers.py" --account "$acct" --date "$date" >"$out" 2>&1 || rc=$?
  tee -a "$log" <"$out" >&2
  rm -f "$out"
  if [ "$rc" -eq 0 ]; then
    return 0
  fi
  if [ "$rc" -eq 3 ]; then
    "$ROOT/bin/notify_thread.sh" "⛔ **Chuyển nhãn sổ bị TẠM DỪNG** — account **$acct** ($date): lệnh gốc của mã đó đã được KHÔI PHỤC trong plan (không chuyển nhãn, không đoán); các lệnh khác chạy bình thường. Lý do: $log" "$tid" 2>/dev/null || true
    return 0
  fi
  pend="$(_bt_pending_count "$plan")"
  if [ "$pend" != "0" ]; then
    "$ROOT/bin/notify_thread.sh" "❌ **apply_book_transfers lỗi nặng (rc=$rc)** — account **$acct** ($date): plan còn $pend chuyển nhãn chưa xử lý ⇒ KHÔNG chạy bot cho account này (lệnh đã giảm theo chuyển nhãn mà không chuyển/khôi phục được). Log: $log" "$tid" 2>/dev/null || true
    "$ROOT/bin/append_event.sh" Mafee error "book-transfer-fatal" \
      "{\"account\":\"$acct\",\"plan_date\":\"$date\",\"rc\":$rc,\"pending_transfers\":$pend,\"log\":\"$log\"}" 2>/dev/null || true
    return "$rc"
  fi
  "$ROOT/bin/notify_thread.sh" "⚠️ apply_book_transfers rc=$rc nhưng plan $acct $date KHÔNG có chuyển nhãn chờ ⇒ bot vẫn chạy (không ảnh hưởng lệnh). Log: $log" "$tid" 2>/dev/null || true
  "$ROOT/bin/append_event.sh" Mafee error "book-transfer-apply-warn" \
    "{\"account\":\"$acct\",\"plan_date\":\"$date\",\"rc\":$rc,\"pending_transfers\":0,\"log\":\"$log\"}" 2>/dev/null || true
  return 0
}
