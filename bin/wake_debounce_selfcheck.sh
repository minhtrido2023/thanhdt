#!/usr/bin/env bash
# Selfcheck cho lớp debounce của wake_thread.sh (RCA 2026-08-20 lỗi #1).
#
# Bất biến kiểm tra: thread vừa được đánh thức trong WAKE_DEBOUNCE_S giây thì lượt wake kế
# tiếp KHÔNG được tạo phiên mới (đó chính là ca đẻ ra 2 phiên Mike song song, đo thật 08-18
# cách 31s và 08-20 cách 83s). Chạy THẬT script, không mô phỏng lại logic.
#
# CCDB_API_URL trỏ vào cổng chết ⇒ nhánh POST luôn fail — cố ý: ta chỉ quan tâm wake có ĐI
# TỚI POST hay bị chặn TRƯỚC đó, và tách bạch hai nhánh bằng đúng dòng log của từng nhánh.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TID=8888888888888888          # thread giả, không tồn tại
MARK="$ROOT/state/wake_debounce/$TID"
LOG="$ROOT/logs/wake_thread.log"
# Isolated temp log — fixture rows không lẫn vào production wake_thread_errors.log (§5b pattern)
ERRLOG="$(mktemp /tmp/wake_sc_XXXXXX_errors.log)"
export WAKE_THREAD_ERRLOG="$ERRLOG"
export WAKE_THREAD_API_BASE="http://127.0.0.1:9"   # discard port -> POST chắc chắn fail, KHÔNG chạm ccdb thật

n=0
ok() { n=$((n+1)); if [ "$1" = "1" ]; then echo "  ok: $2"; else echo "FAIL: $2"; exit 1; fi; }

_calls_since() { # đếm dòng mới của 1 log kể từ mốc byte
  local f="$1" off="$2" pat="$3"
  [ -f "$f" ] || { echo 0; return; }
  tail -c "+$((off+1))" "$f" 2>/dev/null | grep -c "$pat"
}

rm -f "$MARK"
mkdir -p "$ROOT/logs"; : >> "$LOG"; : >> "$ERRLOG"
LOFF=$(stat -c%s "$LOG"); EOFF=$(stat -c%s "$ERRLOG")

# CA 1 — wake đầu tiên: KHÔNG bị chặn, phải đi tới POST (POST fail => có dòng lỗi).
bin/wake_thread.sh "$TID" "selfcheck call 1" "sc-1" >/dev/null 2>&1
ok "$([ "$(_calls_since "$LOG" "$LOFF" DEBOUNCED)" = 0 ] && echo 1 || echo 0)" \
   "wake ĐẦU TIÊN không bị debounce"
ok "$([ "$(_calls_since "$ERRLOG" "$EOFF" 'wake_thread')" -ge 1 ] && echo 1 || echo 0)" \
   "wake đầu tiên có đi tới POST (POST fail như dự kiến)"
ok "$([ -f "$MARK" ] && echo 1 || echo 0)" "mốc thời gian được ghi sau lượt đầu"

# CA 2 — job thứ hai xong NGAY sau đó (ca 08-20, 83s / ca 08-18, 31s đều < cửa sổ):
# phải bị chặn TRƯỚC POST, và exit 0 (caller không được coi là lỗi).
LOFF=$(stat -c%s "$LOG"); EOFF=$(stat -c%s "$ERRLOG")
bin/wake_thread.sh "$TID" "selfcheck call 2" "sc-2" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "lượt bị chặn trả exit 0 (không phải lỗi)"
ok "$([ "$(_calls_since "$LOG" "$LOFF" DEBOUNCED)" = 1 ] && echo 1 || echo 0)" \
   "lượt thứ hai bị DEBOUNCED (không mở phiên song song)"
ok "$([ "$(_calls_since "$ERRLOG" "$EOFF" 'wake_thread')" = 0 ] && echo 1 || echo 0)" \
   "lượt bị chặn KHÔNG chạm POST"

# CA 3 — quá cửa sổ: wake lại bình thường (không kẹt vĩnh viễn).
echo $(( $(date +%s) - 10000 )) > "$MARK"
LOFF=$(stat -c%s "$LOG"); EOFF=$(stat -c%s "$ERRLOG")
bin/wake_thread.sh "$TID" "selfcheck call 3" "sc-3" >/dev/null 2>&1
ok "$([ "$(_calls_since "$LOG" "$LOFF" DEBOUNCED)" = 0 ] && echo 1 || echo 0)" \
   "quá cửa sổ ⇒ wake đi tiếp (không kẹt vĩnh viễn)"

# CA 4 — file mốc chứa giá trị RÁC: fail-open, wake vẫn đi (thà thừa còn hơn nuốt).
echo "not-a-number" > "$MARK"
LOFF=$(stat -c%s "$LOG")
bin/wake_thread.sh "$TID" "selfcheck call 4" "sc-4" >/dev/null 2>&1
ok "$([ "$(_calls_since "$LOG" "$LOFF" DEBOUNCED)" = 0 ] && echo 1 || echo 0)" \
   "mốc rác ⇒ fail-open, wake đi tiếp"

# CA 5 — thread KHÁC không bị ảnh hưởng (debounce là per-thread, không phải toàn cục).
echo "$(date +%s)" > "$MARK"
TID2=7777777777777777
rm -f "$ROOT/state/wake_debounce/$TID2"
LOFF=$(stat -c%s "$LOG")
bin/wake_thread.sh "$TID2" "selfcheck other thread" "sc-5" >/dev/null 2>&1
ok "$([ "$(_calls_since "$LOG" "$LOFF" DEBOUNCED)" = 0 ] && echo 1 || echo 0)" \
   "thread KHÁC không bị chặn lây (debounce per-thread)"

# CA 6 — tắt được bằng env (thoát hiểm khi cần ép wake).
echo "$(date +%s)" > "$MARK"
LOFF=$(stat -c%s "$LOG")
WAKE_DEBOUNCE_S=0 bin/wake_thread.sh "$TID" "selfcheck call 6" "sc-6" >/dev/null 2>&1
ok "$([ "$(_calls_since "$LOG" "$LOFF" DEBOUNCED)" = 0 ] && echo 1 || echo 0)" \
   "WAKE_DEBOUNCE_S=0 tắt được lớp debounce"

rm -f "$MARK" "$ROOT/state/wake_debounce/$TID2" "$ERRLOG"
echo
echo "wake_debounce_selfcheck: $n/$n PASS"
