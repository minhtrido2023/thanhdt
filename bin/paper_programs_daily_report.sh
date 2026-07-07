#!/usr/bin/env bash
# paper_programs_daily_report.sh [--post] [--date YYYY-MM-DD]
# Báo cáo paper-trading hợp nhất hàng ngày (registry-driven, xem paper_programs_daily_report.py).
# Mặc định in ra stdout. --post = gửi vào Discord topic "Trading report" (1522576692638388364)
# qua notify_thread.sh (tự chunk <2000 chars).
# Luôn exit 0 khi render được report (kể cả có sleeve lỗi) — chỉ exit ≠0 khi python chết hẳn.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export TZ="Asia/Ho_Chi_Minh"

TRADING_REPORT_TOPIC="1522576692638388364"
POST=0
ARGS=()
for a in "$@"; do
  if [ "$a" = "--post" ]; then POST=1; else ARGS+=("$a"); fi
done

report="$(python3 "$ROOT/bin/paper_programs_daily_report.py" ${ARGS[@]+"${ARGS[@]}"} 2>&1)" || {
  # python chết hẳn (syntax/env) — vẫn báo trung thực thay vì rơi im lặng
  report="📋 Paper Programs Daily Report — LỖI RENDER
❌ paper_programs_daily_report.py không chạy được:
${report:0:800}
→ kiểm tra mike/bin/paper_programs_daily_report.py + registry."
}

echo "$report"
if [ "$POST" = "1" ]; then
  "$ROOT/bin/notify_thread.sh" "$report" "$TRADING_REPORT_TOPIC"
fi
