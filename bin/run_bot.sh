#!/usr/bin/env bash
# run_bot.sh — deterministic execution wrapper cho bot_execute.py.
# Thay thế headless LLM dispatch cho các tác vụ trading thực tế (placement, fills).
#
# Usage:
#   bin/run_bot.sh [--account LABEL] [--date YYYY-MM-DD] [--auto-otp] [--dry-run]
#
# bot_execute.py tự publish events lên Mike fleet bus (STEP_FAIL, fill_lagging).
# Wrapper này thêm: start/end Discord notify + bus event.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
# Source wc_env.sh to get TZ=Asia/Ho_Chi_Minh (required for session_phase to use ICT)
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true

ACCOUNT="SpaceX"
PLAN_DATE="$(date +%Y-%m-%d)"
AUTO_OTP=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --account) ACCOUNT="$2"; shift 2 ;;
    --date)    PLAN_DATE="$2"; shift 2 ;;
    --auto-otp) AUTO_OTP=true; shift ;;
    --dry-run)  DRY_RUN=true; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

_tid="1521470705563340910"  # Trading Daily thread — mọi giao dịch hàng ngày gộp về đây
_discord() {
  "$ROOT/bin/notify_thread.sh" "$1" "$_tid" 2>/dev/null || true
}

LOG="$ROOT/logs/run_bot_${ACCOUNT}_${PLAN_DATE}.log"
mkdir -p "$ROOT/logs"

ts_start="$(date +%s)"
# Message thân thiện, có nghĩa với người đọc (user yêu cầu 2026-07-07 — tường minh vận
# hành): nói rõ bot vào phiên làm gì (mấy lệnh / HOLD), thay vì tên tiến trình + flag.
_n_orders="$(python3 -c "
import json
try:
    print(len(json.load(open('$WC_ROOT/data/trade_plans/plan_${ACCOUNT}_${PLAN_DATE}.json')).get('orders', [])))
except Exception:
    print('?')
" 2>/dev/null)"
_hr_ict="$(TZ='Asia/Ho_Chi_Minh' date +'%H:%M')"
if [ "$_n_orders" = "0" ]; then
  _discord "🤖 **Bot vào phiên ($_hr_ict)** — account **$ACCOUNT**: kế hoạch hôm nay là HOLD (không có lệnh) — bot trực phiên để đồng bộ trạng thái, không giao dịch gì."
else
  _discord "🤖 **Bot vào phiên ($_hr_ict)** — account **$ACCOUNT**: bắt đầu thực thi kế hoạch $PLAN_DATE (${_n_orders} lệnh). Sổ lệnh cập nhật mỗi 5 phút tại đây."
fi

"$ROOT/bin/append_event.sh" Mafee status "bot-start" \
  "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\",\"auto_otp\":$AUTO_OTP}" 2>/dev/null || true

if [ "$DRY_RUN" = true ]; then
  echo "[DRY-RUN] would run: python bot_execute.py --account $ACCOUNT $([ "$AUTO_OTP" = true ] && echo '--auto-otp')"
  _discord "🔍 DRY-RUN — không thực thi lệnh thật."
  exit 0
fi

set +e
cd "$WC_ROOT"
OTP_FLAG=""
[ "$AUTO_OTP" = true ] && OTP_FLAG="--auto-otp"
# shellcheck disable=SC2086
python3 bot_execute.py --account "$ACCOUNT" --date "$PLAN_DATE" $OTP_FLAG \
  2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}
set -e

ts_end="$(date +%s)"
elapsed=$(( ts_end - ts_start ))

_hr_end="$(TZ='Asia/Ho_Chi_Minh' date +'%H:%M')"
if [ "$rc" -eq 0 ]; then
  # Nói rõ LÝ DO rời phiên (user feedback 2026-07-07 chiều: "bot vừa bật vừa tắt" đọc
  # rất khó hiểu khi message không nói bot dừng vì XONG VIỆC hay vì lỗi).
  if grep -q "tất cả account đã khớp đủ" "$LOG" 2>/dev/null; then
    _reason="đã HOÀN TẤT toàn bộ kế hoạch hôm nay — không còn gì để làm, bot nghỉ (sổ lệnh chi tiết sẽ có trong heartbeat/EOD report)"
  elif [ "$_n_orders" = "0" ]; then
    _reason="kế hoạch hôm nay là HOLD — bot đã đồng bộ trạng thái xong và nghỉ"
  else
    _reason="kết thúc đợt làm việc bình thường; nếu đang giữa ngày bot sẽ quay lại theo lịch (13:00 sau nghỉ trưa), cuối ngày chờ báo cáo EOD 15:00"
  fi
  _discord "✅ **Bot rời phiên ($_hr_end)** — account **$ACCOUNT**: ${_reason} (chạy $((elapsed/60)) phút)."
  "$ROOT/bin/append_event.sh" Mafee status "bot-done" \
    "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\",\"elapsed_s\":$elapsed,\"rc\":0}" 2>/dev/null || true
else
  tail_preview="$(tail -c 300 "$LOG" 2>/dev/null | tr '\n' ' ')"
  _discord "❌ **Bot gặp lỗi và dừng ($_hr_end)** — account **$ACCOUNT** (rc=$rc, chạy $((elapsed/60)) phút). Hệ thống giám sát sẽ tự khởi động lại nếu còn trong giờ giao dịch; chi tiết kỹ thuật: $LOG. Preview: $tail_preview"
  "$ROOT/bin/append_event.sh" Mafee error "bot-fail" \
    "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\",\"elapsed_s\":$elapsed,\"rc\":$rc,\"log\":\"$LOG\"}" 2>/dev/null || true
  # Mandate user 2026-07-07 (tự phát hiện → tự sửa): mọi lần bot fail đều tự cử agent
  # chẩn đoán root cause qua ops_autofix.sh — cùng pattern ops_health_check.sh. Dispatch
  # --bg bên trong nên không block; tự cooldown 1h/label chống bão. Trước đây nhánh này
  # chỉ alert suông → không ai tự chẩn đoán (gap phát hiện sau sự cố OTP 2026-07-08).
  "$ROOT/bin/ops_autofix.sh" "run-bot-fail-${ACCOUNT}-${PLAN_DATE}" \
    "run_bot.sh --account $ACCOUNT (plan $PLAN_DATE) thoát rc=$rc sau $((elapsed/60)) phút. Log: $LOG. Tail: $tail_preview — Việc cần làm: (1) xác định root cause thật trong log; (2) kiểm tra bot đã tự hồi phục chưa (heartbeat autoheal, log $ROOT/logs/run_bot_${ACCOUNT}_autoheal_*.log + journal exec_${ACCOUNT}_${PLAN_DATE}_journal.csv trong data/execution_logs/); (3) nếu còn lệnh kẹt/bot chết trong giờ giao dịch → ưu tiên khôi phục an toàn trong ranh giới cho phép, còn lại escalate." 2>/dev/null || true
fi

"$ROOT/bin/consolidate.sh" >> "$ROOT/logs/consolidator.log" 2>&1 || true
exit "$rc"
