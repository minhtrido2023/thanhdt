#!/usr/bin/env bash
# paper_main_early_check.sh — phát hiện SỚM khi paper-main (probe harness cho EXTREME-regime
# gate + vol-scale chase-cap) không sinh evidence thật, thay vì chỉ biết qua báo cáo EOD 15:20
# hay khi user hỏi. Chạy ~30' sau mỗi cron executor (09:10 sáng / 13:05 chiều ICT).
#
# Gốc sự cố 2026-07-08/09: ghost-guard/TZ bug khiến journal tồn tại nhưng 0 lệnh thật cả 2
# ngày liền — không ai biết cho tới khi user hỏi trực tiếp 07-09 chiều. Script này đóng đúng
# gap đó cho tương lai: kiểm tra journal hôm nay CÓ PLACE/FILL/DONE thật chưa, báo Discord
# ngay nếu KHÔNG — đủ sớm trong ngày để còn kịp chẩn đoán + sửa trước khi hết phiên.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"

TRADING_DAILY_THREAD="1521470705563340910"
TODAY="$(TZ=Asia/Ho_Chi_Minh date +%Y-%m-%d)"
NOW_ICT="$(TZ=Asia/Ho_Chi_Minh date +'%H:%M ICT')"
SESSION="${1:-morning}"   # morning | afternoon — chỉ để hiển thị trong message

PLAN_FILE="$WC_ROOT/data/trade_plans/plan_main_${TODAY}.json"
JOURNAL="$WC_ROOT/data/execution_logs/exec_main_${TODAY}_journal.csv"

_notify() {
  "$ROOT/bin/notify_thread.sh" "$1" "$TRADING_DAILY_THREAD" 2>/dev/null || true
}

# Không có probe plan hôm nay (vd lỗi paper_main_probe_plan.py) → tự nó đã là bất thường,
# vì cron này chạy T2-T6 nên LUÔN phải có plan.
if [ ! -f "$PLAN_FILE" ]; then
  _notify "🔴 **paper-main early-check ($SESSION, $NOW_ICT)** — KHÔNG có plan hôm nay ($PLAN_FILE thiếu). paper_main_probe_plan.py (cron 08:52 ICT) có thể đã lỗi — kiểm tra mike/logs/paper_main_probe_plan.log."
  exit 1
fi

if [ ! -f "$JOURNAL" ]; then
  _notify "🔴 **paper-main early-check ($SESSION, $NOW_ICT)** — có plan nhưng KHÔNG có journal ($JOURNAL thiếu). Executor có thể chưa chạy/chết ngay khi khởi động — kiểm tra mike/logs/run_bot_main_${TODAY}*.log."
  exit 1
fi

HAS_REAL="$(python3 -c "
import csv
try:
    with open('$JOURNAL', encoding='utf-8') as f:
        print('yes' if any(r.get('event') in ('PLACE','FILL','DONE') for r in csv.DictReader(f)) else 'no')
except OSError:
    print('no')
" 2>/dev/null || echo no)"

if [ "$HAS_REAL" != "yes" ]; then
  GHOST_COUNT="$(grep -c ',GHOST_ORDER,' "$JOURNAL" 2>/dev/null || echo 0)"
  _notify "🔴 **paper-main early-check ($SESSION, $NOW_ICT)** — journal tồn tại nhưng 0 lệnh PLACE/FILL/DONE thật (GHOST_ORDER: $GHOST_COUNT dòng). Đây đúng dấu hiệu sự cố 07-08/09 (ghost-guard/TZ) — evidence cho EXTREME-regime gate + vol-scale chase-cap hôm nay = 0, không tính vào tiến độ. Cần kiểm tra ngay, đừng đợi báo cáo EOD 15:20."
  exit 1
fi

# Healthy — im lặng (không cần báo mỗi lần OK, theo quiet-heartbeat convention).
exit 0
