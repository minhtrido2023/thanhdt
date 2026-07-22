#!/usr/bin/env bash
# ops_autofix.sh "<context-label>" "<issue-details>"
#
# Cơ chế TỰ SỬA LỖI VẬN HÀNH (user mandate 2026-07-07: "bất cứ khi nào phát sinh lỗi thì
# tự động fix bug, không thụ động chờ báo lỗi... tự fix rồi báo cáo lại").
#
# Được gọi bởi các checker định kỳ (ops_health_check.sh, sync_bq_cache_daily.sh, ...) khi
# phát hiện vấn đề — dispatch 1 headless agent (Winston, model opus) để CHẨN ĐOÁN + SỬA
# trong giới hạn an toàn (guardrails bên dưới) + báo cáo vào Trading Daily. Model hạ từ
# fable xuống opus (cost-opt model-drift fix, 2026-07-17) — mọi issue checker này gọi tới
# là "phức tạp thường" (chẩn đoán+fix 1 script) theo đúng ladder ở MIKE.md §Model routing,
# không phải "cực kỳ phức tạp" cần fable. Cần fable thật (issue khó bất thường) → dispatch
# tay lại với --model fable, đừng mặc định.
#
# GUARDRAILS (nhúng thẳng vào prompt — fixer KHÔNG được vượt):
#   ĐƯỢC tự sửa : bug code trong script report/check/pipeline/cache, resync cache, resend
#                 report, dọn lock/flag kẹt, restart daemon phụ trợ, commit fix.
#   CẤM tự sửa  : mọi thứ chạm tiền thật — trade plan, trading_rules.json, logic đặt lệnh
#                 trong executor/brokers (ngoài crash-fix rõ ràng), crontab dòng thực thi
#                 (run_bot/heartbeat/pkill), xoá dữ liệu, BOT_STOP. Gặp các thứ này →
#                 ESCALATE (bus question + Telegram) và DỪNG.
#
# Chống bão dispatch: mỗi context-label chỉ autofix tối đa 1 lần / AUTOFIX_COOLDOWN giây
# (mặc định 3600) — lần trùng trong cooldown chỉ notify, không dispatch thêm.
#
# Timeout: AUTOFIX_TIMEOUT giây/attempt (mặc định 1800). 900 cũ quá ngắn cho job chẩn-đoán-sâu
# (Winston_20260707_072729: attempt 1 bị kill đúng 900s khi heartbeat còn tươi từng phút,
# attempt 2 làm lại từ đầu mất thêm 694s — phí trọn 15' + 1 slot). Checker nào biết issue
# nhẹ có thể tự hạ: AUTOFIX_TIMEOUT=600 ops_autofix.sh "<label>" "<details>".
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
TRADING_DAILY_THREAD="1521470705563340910"
AUTOFIX_COOLDOWN="${AUTOFIX_COOLDOWN:-3600}"
AUTOFIX_TIMEOUT="${AUTOFIX_TIMEOUT:-1800}"

LABEL="${1:?usage: ops_autofix.sh \"<context-label>\" \"<issue-details>\"}"
DETAILS="${2:-"(không có chi tiết kèm theo — đọc log của checker gọi tới)"}"

STATE_DIR="$ROOT/state/autofix"
mkdir -p "$STATE_DIR"
# printf (không echo) để newline cuối không biến thành '-' — bug tìm ra khi selfcheck
# cooldown 2026-07-07: SLUG lệch tên stamp file → cooldown không khớp → dispatch lặp.
SLUG="$(printf '%s' "$LABEL" | tr -cs 'a-zA-Z0-9' '-' | cut -c1-60)"
STAMP_FILE="$STATE_DIR/$SLUG.last"
NOW=$(date +%s)
if [ -f "$STAMP_FILE" ]; then
  LAST=$(cat "$STAMP_FILE" 2>/dev/null || echo 0)
  if [ $((NOW - LAST)) -lt "$AUTOFIX_COOLDOWN" ]; then
    echo "[ops_autofix] '$LABEL' đã autofix trong $((AUTOFIX_COOLDOWN/60))' gần nhất — chỉ notify, không dispatch lặp."
    "$ROOT/bin/notify_thread.sh" "🔁 [ops-autofix] Vấn đề '$LABEL' TÁI DIỄN trong cooldown (fix trước có thể chưa ăn) — cần người xem: $DETAILS" "$TRADING_DAILY_THREAD" 2>/dev/null || true
    exit 0
  fi
fi
# Global episode guard (2026-07-15, Wags coord-2026-07-15): checker sweep per-account
# (for_each_live_account) gọi ops_autofix vài giây liên tiếp với LABEL KHÁC NHAU cho cùng
# 1 issue fleet-wide → cooldown per-label không dedupe được (sự cố 07-15: ops-health-ZaloPay
# 01:20:06Z + ops-health-SpaceX 01:20:12Z → 2 Winston fable song song, kết luận NGƯỢC nhau
# trên cùng preflight_check.sh). Trong AUTOFIX_GLOBAL_GUARD giây (mặc định 600) sau BẤT KỲ
# dispatch autofix nào: lần gọi sau chỉ notify gộp-episode, KHÔNG dispatch song song, và
# KHÔNG stamp cooldown per-label (issue thật sự riêng sẽ được checker kỳ sau re-flag và
# dispatch bình thường). Escape hatch: AUTOFIX_GLOBAL_GUARD=0 tắt guard.
AUTOFIX_GLOBAL_GUARD="${AUTOFIX_GLOBAL_GUARD:-600}"
GLOBAL_STAMP="$STATE_DIR/_global.last"
if [ "$AUTOFIX_GLOBAL_GUARD" -gt 0 ] && [ -f "$GLOBAL_STAMP" ]; then
  GLAST=$(cat "$GLOBAL_STAMP" 2>/dev/null || echo 0)
  GAGE=$((NOW - GLAST))
  if [ "$GAGE" -lt "$AUTOFIX_GLOBAL_GUARD" ]; then
    echo "[ops_autofix] global guard: autofix khác vừa dispatch ${GAGE}s trước — gộp episode, không dispatch song song cho '$LABEL'."
    "$ROOT/bin/notify_thread.sh" "⏸️ [ops-autofix] '$LABEL' phát hiện ${GAGE}s sau 1 autofix khác đang chạy — gộp chung episode, không dispatch song song (nếu là issue riêng biệt, checker kỳ sau sẽ tự re-flag): $DETAILS" "$TRADING_DAILY_THREAD" 2>/dev/null || true
    exit 0
  fi
fi
echo "$NOW" > "$STAMP_FILE"
echo "$NOW" > "$GLOBAL_STAMP"

"$ROOT/bin/notify_thread.sh" "🔧 [ops-autofix] Phát hiện vấn đề '$LABEL' — đã tự động cử agent chẩn đoán + sửa (Winston/fable). Sẽ báo kết quả vào đây khi xong." "$TRADING_DAILY_THREAD" 2>/dev/null || true

"$ROOT/bin/dispatch.sh" Winston "NHIỆM VỤ OPS-AUTOFIX (mandate user 2026-07-07: tự phát hiện tự sửa, báo cáo sau): checker định kỳ vừa phát hiện vấn đề vận hành.

CONTEXT: $LABEL
CHI TIẾT TỪ CHECKER:
$DETAILS

QUY TRÌNH BẮT BUỘC:
1. CHẨN ĐOÁN từ bằng chứng thật (log/file/API), không đoán. Đọc kb/INCIDENTS.md + kb/ops_runbook.md trước — vấn đề có thể là dạng đã biết có sẵn cách xử lý.
2. SỬA trong giới hạn: ĐƯỢC sửa bug code script report/check/pipeline/cache, resync cache, resend report, dọn lock/flag kẹt, restart daemon phụ trợ; commit fix với message rõ ràng.
3. CẤM TUYỆT ĐỐI (dù thấy 'cần thiết'): sửa trade plan, trading_rules.json, logic đặt lệnh executor/brokers, crontab dòng thực thi (run_bot/heartbeat/pkill), xoá dữ liệu, tạo/xoá BOT_STOP. Nếu root cause nằm ở đó → append_event.sh Winston question '<topic>' với mô tả + đề xuất, notify Telegram, rồi DỪNG.
4. VERIFY artifact sau khi sửa (chạy lại checker/script bị lỗi, xác nhận hết lỗi thật) — không tin self-report.
5. BÁO CÁO: notify_thread.sh vào thread $TRADING_DAILY_THREAD — ngắn gọn: hỏng gì, nguyên nhân, đã sửa gì, verify thế nào. Nếu ảnh hưởng workflow sống → thêm entry kb/INCIDENTS.md. Ghi bus event finding như thường lệ." \
  --bg --thread "$TRADING_DAILY_THREAD" --timeout "$AUTOFIX_TIMEOUT" --model opus 2>&1 | tail -3

echo "[ops_autofix] dispatched fixer for '$LABEL'"
