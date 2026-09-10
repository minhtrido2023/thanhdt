#!/usr/bin/env bash
# hit_details_daily.sh — cron wrapper cho hit_details.py (công cụ audit thuần, kb/coding_guidelines.md
# §29): chạy hit_details.py cho hôm nay, rồi báo 1 dòng vào topic NỘI BỘ kèm đường dẫn file.
#
# KHÔNG đổi logic lọc/đặt lệnh — chỉ tạo thêm 1 file quan sát + 1 dòng thông báo. User duyệt wire
# 2026-09-10 22:54 ICT (Discord, xem kb/discord_channels.json): chỉ wire hit_details.py, KHÔNG wire
# indicator_monitor.py (data-quality đã thuộc trách nhiệm Winston/data-ops, không quản lý thêm).
#
# ⚠️ Post vào `trading_daily` (nội bộ), KHÔNG post vào `trading_report` (kênh DUY NHẤT cho báo cáo
# tổng hợp — user chỉ đạo 2026-09-11 00:00 ICT: chi tiết công thức/factor là nội bộ, báo cáo cho
# outsider giữ nguyên như cũ, không lẫn audit detail vào).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MIKE_BIN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATE="$(TZ=Asia/Ho_Chi_Minh date +%Y-%m-%d)"

[ -f "$ROOT/wc_env.sh" ] && source "$ROOT/wc_env.sh" 2>/dev/null || true

cd "$ROOT"
_out="$(python3 hit_details.py "$DATE" 2>&1)" || {
  echo "$_out" >&2
  echo "❌ hit_details_daily.sh: hit_details.py lỗi cho $DATE — xem log." >&2
  exit 1
}
echo "$_out"

_f="data/hit_details_${DATE}.md"
if [ -f "$_f" ]; then
  "$MIKE_BIN/notify_thread.sh" "📋 Hit Details ${DATE} (nội bộ): ${_out} — \`${_f}\`" trading_daily
else
  echo "⚠️ hit_details_daily.sh: $_f không tồn tại sau khi chạy — không gửi Discord." >&2
  exit 1
fi
