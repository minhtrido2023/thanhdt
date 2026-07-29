#!/usr/bin/env bash
# bq_monthly_pin.sh — cron wrapper for bq_monthly_pin.py (ngày 1 hàng tháng, 22:00 ICT).
#
# Vì sao 22:00 ICT ngày 1 (cron `0 15 1 * *` — máy chạy giờ UTC):
#   - SAU toàn bộ chuỗi ghi trong ngày (ingest tav2 ~17:2x, daily_refresh 18:30,
#     pipeline 19:00 universe_pit, fa_ratings earnings-window 20:00, inject 20:30) => pin chụp
#     một trạng thái ĐÃ ỔN ĐỊNH, không phải nửa chừng một lần ghi.
#   - TRƯỚC sync_bq_cache_daily.sh 23:45 (~105' đệm, runtime đo thật ~7' baseline).
#   - TRÁNH XA cửa sổ rebuild ngoài của bq_admin buổi sáng (`ticker_prune` bị TRUNCATE+rebuild
#     lúc 07:27 ICT ngày 2026-07-29). Snapshot là atomic, nhưng pin đúng vào GIỮA một
#     TRUNCATE...INSERT sẽ chụp được bảng rỗng và bắn CRITICAL giả — nên không đặt buổi sáng.
#   - Không đụng phút với job nào đang có (21:00 send_plan, 23:00 second-chance, 23:45 sync).
# Chỉ chạy ngày 1 => giờ trong ngày không phụ thuộc T2-T6; ngày 1 rơi vào cuối tuần vẫn đúng
# (bảng đứng yên, pin vẫn hợp lệ — không có gì để chờ).
#
# An toàn: job này CHỈ đọc bảng production và ghi vào dataset RIÊNG `tav2_pin` + log. Không
# chạm tiền thật, không chạm bảng canonical nào.
set -uo pipefail
ROOT="/home/trido/thanhdt/WorkingClaude"
export PATH="/home/trido/google-cloud-sdk/bin:$PATH"
export TZ="Asia/Ho_Chi_Minh"
LOG="$ROOT/mike/logs/bq_monthly_pin.log"
mkdir -p "$(dirname "$LOG")"

echo "=== bq_monthly_pin $(date +%FT%T%z) ===" >> "$LOG"
# timeout 4500 (75') — worst case vẫn xong trước 23:15, còn 30' đệm trước sync 23:45.
timeout 4500 /usr/bin/python3 "$ROOT/mike/bin/bq_monthly_pin.py" "$@" >> "$LOG" 2>&1
rc=$?
echo "--- exit=$rc $(date +%FT%T%z) ---" >> "$LOG"

# rc: 0=OK 1=CRITICAL 2=WARN 3=lỗi vận hành 124=timeout. Script tự gửi Discord cho 0/1/2/3;
# timeout/crash thì nó chưa kịp gửi gì -> wrapper phải tự báo, nếu không cron chết = im lặng.
if [ "$rc" -ge 3 ]; then
  "$ROOT/mike/bin/notify.sh" "BQ monthly pin FAIL (exit=$rc$([ "$rc" = 124 ] && echo ' TIMEOUT')) — xem $LOG" 2>/dev/null || true
  "$ROOT/mike/bin/notify_thread.sh" "BQ monthly pin FAIL (exit=$rc$([ "$rc" = 124 ] && echo ' TIMEOUT')) — xem $LOG" "1521470705563340910" 2>/dev/null || true
fi
exit "$rc"
