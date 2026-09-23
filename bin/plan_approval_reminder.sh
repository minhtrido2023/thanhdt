#!/usr/bin/env bash
# plan_approval_reminder.sh — nhắc duyệt plan SÁT giờ bot chạy (08:50 ICT, 15' trước 09:05)
# qua Telegram, CHỈ khi plan hôm nay THẬT SỰ đang bị approval-gate chặn.
#
# Escalate: kb/incidents/retro/retro-2026-09-22.md, pattern
# retro-pattern-recurring-plan-approval-gate-3days (tái diễn 09-14/09-21/09-22 — prevention
# hiện có, 21:00 + second-chance 23:00 + preflight 08:45, ĐỀU đã gửi Telegram nhưng lẫn trong
# nhiều dòng check khác nên không đủ nổi bật để user hành động kịp). User duyệt option A
# 2026-09-23 08:48 ICT, kèm chỉ đạo: "nếu plan không đổi thì không cần báo" — tức plan không
# cần duyệt / đã duyệt rồi thì IM LẶNG, không gửi gì (khác preflight_check.sh gửi mỗi ngày
# bất kể GREEN/RED).
#
# Tái dùng NGUYÊN VĂN trading_bot.plan.approval_block_reason() — hàm bot_execute.py dùng để
# chặn THẬT (dòng ~2042) — không viết lại công thức riêng (coding_guidelines §28: 2 nơi tự
# tính cùng 1 điều kiện sẽ lệch nhau theo thời gian).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
TODAY="$(TZ=Asia/Ho_Chi_Minh date +%Y-%m-%d)"

if ! LABELS="$(cd "$WC_ROOT" && python3 -c "from trading_bot.config import live_dnse_labels; print(' '.join(live_dnse_labels()))")"; then
  echo "[plan_approval_reminder] KHÔNG đọc được danh sách account (trading_bot.config lỗi) — bỏ qua." >&2
  exit 1
fi
if [ -z "$LABELS" ]; then
  echo "[plan_approval_reminder] không có account nào enabled=true/mode=live/broker=dnse — không chạy gì."
  exit 0
fi

for acc in $LABELS; do
  reason="$(cd "$WC_ROOT" && python3 -c "
from trading_bot.plan import load_plan, approval_block_reason
p = load_plan('$TODAY', account='$acc')
r = approval_block_reason(p) if p is not None else None
print(r or '', end='')
")"
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "[plan_approval_reminder] $acc: lỗi Python khi đọc plan (rc=$rc) — không kết luận được, xem log phía trên." >&2
    continue
  fi
  if [ -n "$reason" ]; then
    "$ROOT/bin/notify.sh" "⏰ NHẮC DUYỆT PLAN — còn ~15 phút trước giờ bot chạy (09:05 ICT). $reason" 2>/dev/null || true
    echo "[plan_approval_reminder] $acc: đã nhắc qua Telegram — $reason"
  else
    echo "[plan_approval_reminder] $acc: không cần nhắc (đã duyệt / không yêu cầu duyệt / không có lệnh / không có plan hôm nay)"
  fi
done
