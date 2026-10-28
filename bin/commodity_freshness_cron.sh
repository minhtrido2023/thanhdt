#!/usr/bin/env bash
# commodity_freshness_cron.sh — chạy bin/commodity_freshness_monitor.py, chỉ post Discord (topic
# feeds_data) khi stdout KHÔNG rỗng (monitor chỉ in khi trạng thái đổi). Cron 07:30 ICT hằng ngày,
# sau lượt nạp 23:00 ICT của bq_admin. Lỗi monitor (rc≠0) cũng post — im lặng là bẫy (§29).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export TZ=Asia/Ho_Chi_Minh
out="$(/usr/bin/python3 "$ROOT/bin/commodity_freshness_monitor.py" 2>&1)"
rc=$?
if [ "$rc" -ne 0 ]; then
  "$ROOT/bin/notify_thread.sh" "⚠️ commodity_freshness_monitor LỖI rc=$rc:
${out:0:1500}" feeds_data
  exit "$rc"
fi
if [ -n "$out" ]; then
  "$ROOT/bin/notify_thread.sh" "📡 Độ tươi commodity_prices (thay đổi so với lần trước):
${out:0:1800}" feeds_data
fi
