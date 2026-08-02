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
# GUARDRAILS (nhúng thẳng vào prompt — fixer KHÔNG được vượt). NGUỒN CHUẨN TẮC =
# kb/ops_runbook.md § Nguyên tắc phân quyền tự sửa — bản chép NÀY (comment + prompt dòng
# ~165 dưới) phải khớp bảng đó, sửa 1 chỗ phải sửa cả 2 (khảo sát vận hành 2026-08-01):
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
TRADING_DAILY_THREAD="trading_daily"
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
STARTED_ISO_FILE="$STATE_DIR/$SLUG.started_iso"
CONFIRM_FILE="$STATE_DIR/$SLUG.confirmed"
NOW=$(date +%s)

# Post-condition check của LẦN DISPATCH TRƯỚC (Wags audit 2026-07-30, P2): cooldown stamp bị
# ghi TRƯỚC khi fixer chạy, và user đã được báo "đã cử agent sửa" ngay lúc đó — nếu fixer lạc
# đề/chết im, KHÔNG GÌ phản bác câu đó trong suốt cooldown (đúng lớp lỗi vừa vá ở daily_retro
# hôm nay: rc=0/exit-code không nói lên nội dung có đúng việc không). Kiểm 1 lần duy nhất mỗi
# dispatch (cache ở CONFIRM_FILE, không hỏi bus lặp lại mỗi lần gọi) — nếu có STAMP từ lần
# trước mà CHƯA từng xác nhận xong: tra bus Winston tìm finding 'ops-autofix-done: <label>'
# hoặc question 'ops-autofix-unresolved: <label>' xuất hiện SAU thời điểm dispatch đó (hợp
# đồng đầu ra bắt buộc ở prompt bên dưới). Không thấy ⇒ notify thật, không im lặng chờ hết
# cooldown rồi mới lộ ra.
#
# ⚠️ Giới hạn THẬT (arch-reviewer 2026-07-30, khác với refresh_deposit_rate_vn.sh — script đó
# dispatch ĐỒNG BỘ nên tự check ngay trong CÙNG lần chạy; ops_autofix.sh này dispatch --bg nên
# CHỈ tự check được ở LẦN GỌI SAU cho ĐÚNG label đó): những label gắn ngày vào tên (vd
# `run-bot-fail-SpaceX-2026-07-28`, dùng đúng 1 lần rồi không lặp lại) sẽ KHÔNG BAO GIỜ được
# check bởi cơ chế này — không có "lần gọi sau" nào cho 1 label chỉ xảy ra 1 lần. Cơ chế này
# chỉ thật sự hiệu quả cho label LẶP LẠI theo tên (ops-health-*, bq-cache-sync-verify, ...).
# Muốn phủ cả nhóm label-1-lần cần thêm 1 sweep định kỳ (từ ops_health_check.sh/daily_retro.sh)
# quét state/autofix/*.started_iso thiếu .confirmed quá N giờ — CHƯA làm, ghi nhận là nợ.
if [ -f "$STAMP_FILE" ] && [ ! -f "$CONFIRM_FILE" ] && [ -s "$STARTED_ISO_FILE" ]; then
  LAST_ISO="$(cat "$STARTED_ISO_FILE" 2>/dev/null || true)"
  if [ -n "$LAST_ISO" ]; then
    CONFIRMED="$(python3 - "$LAST_ISO" "$LABEL" "$ROOT/bus/inbox/Winston.jsonl" <<'PYEOF' 2>/dev/null || echo no
import json, sys
from datetime import datetime
start_iso, label, path = sys.argv[1:4]
start = datetime.strptime(start_iso, "%Y-%m-%dT%H:%M:%SZ")
allowed = {f"ops-autofix-done: {label}": "finding",
           f"ops-autofix-unresolved: {label}": "question"}
found = False
try:
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            topic = rec.get("topic")
            if topic not in allowed or rec.get("event_type") != allowed[topic]:
                continue
            try:
                rts = datetime.strptime(rec.get("ts", ""), "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue
            if rts >= start:
                found = True
    print("yes" if found else "no")
except FileNotFoundError:
    print("no")
PYEOF
)"
    if [ "$CONFIRMED" = "yes" ]; then
      touch "$CONFIRM_FILE"
    else
      echo "[ops_autofix] '$LABEL' — lần autofix TRƯỚC (dispatch lúc $LAST_ISO) KHÔNG có kết quả xác nhận được trên bus."
      "$ROOT/bin/notify_thread.sh" "⚠️ [ops-autofix] Lần tự sửa TRƯỚC cho '$LABEL' (lúc $LAST_ISO) KHÔNG có kết quả xác nhận được (không có finding/question khớp trên bus) — fixer có thể đã lạc đề/chết im. Cần người kiểm tra trực tiếp, đừng tin thông báo 'đã sửa' trước đó." "$TRADING_DAILY_THREAD" 2>/dev/null || true
    fi
  fi
fi

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
date -u +%Y-%m-%dT%H:%M:%SZ > "$STARTED_ISO_FILE"
rm -f "$CONFIRM_FILE"  # dispatch mới — chưa xác nhận, lần gọi sau phải tự tra lại bus

"$ROOT/bin/notify_thread.sh" "🔧 [ops-autofix] Phát hiện vấn đề '$LABEL' — đã tự động cử agent chẩn đoán + sửa (Winston/fable). Sẽ báo kết quả vào đây khi xong." "$TRADING_DAILY_THREAD" 2>/dev/null || true

# Known-issue lookup (cost-opt #2, 2026-07-30): grep kb/incidents/ by keyword BEFORE
# dispatch, inline the top matches into the prompt — saves the fixer its own search round-trips
# for a pattern that already happened (checked: data-registry-accuracy alone has recurred ≥5
# times per the retro log). Only shortcuts the SEARCH step; prompt below still requires the
# fixer to verify the match actually applies before reusing an old fix (each occurrence so far
# has had a genuinely different specific root cause even within the same family).
KNOWN_ISSUE="$(python3 "$ROOT/bin/incident_lookup.py" "$LABEL" "$DETAILS" 2>/dev/null || true)"

# Prompt dưới (việc 2/3) chép NGUYÊN VĂN ranh giới tự-sửa từ kb/ops_runbook.md § Nguyên tắc
# phân quyền tự sửa — bắt buộc nhúng trực tiếp vào prompt (LLM headless cần thấy ranh giới
# ngay trong context, không thể chỉ "đọc file" đáng tin cậy bằng). Sửa ranh giới ở
# ops_runbook.md thì PHẢI sửa lại việc 2/3 dưới cho khớp (khảo sát vận hành 2026-08-01).

"$ROOT/bin/dispatch.sh" Winston "NHIỆM VỤ OPS-AUTOFIX (mandate user 2026-07-07: tự phát hiện tự sửa, báo cáo sau): checker định kỳ vừa phát hiện vấn đề vận hành.

CONTEXT: $LABEL
CHI TIẾT TỪ CHECKER:
$DETAILS
${KNOWN_ISSUE:+
$KNOWN_ISSUE
}
QUY TRÌNH BẮT BUỘC:
1. CHẨN ĐOÁN từ bằng chứng thật (log/file/API), không đoán. Đọc kb/ops_runbook.md trước. Nếu có mục 'khớp từ khoá' ở trên, đọc kỹ và tự xác nhận có thực sự CÙNG root cause không (đừng áp mù) — nếu khác, vẫn phải grep -rn kb/incidents/ tự tìm thêm như trước giờ.
2. SỬA trong giới hạn: ĐƯỢC sửa bug code script report/check/pipeline/cache, resync cache, resend report, dọn lock/flag kẹt, restart daemon phụ trợ; commit fix với message rõ ràng.
3. CẤM TUYỆT ĐỐI (dù thấy 'cần thiết'): sửa trade plan, trading_rules.json, logic đặt lệnh executor/brokers, crontab dòng thực thi (run_bot/heartbeat/pkill), xoá dữ liệu, tạo/xoá BOT_STOP. Nếu root cause nằm ở đó → append_event.sh Winston question '<topic>' với mô tả + đề xuất, notify Telegram, rồi DỪNG.
4. VERIFY artifact sau khi sửa (chạy lại checker/script bị lỗi, xác nhận hết lỗi thật) — không tin self-report.
5. BÁO CÁO: notify_thread.sh vào thread $TRADING_DAILY_THREAD — ngắn gọn: hỏng gì, nguyên nhân, đã sửa gì, verify thế nào. Nếu ảnh hưởng workflow sống → thêm 1 FILE entry mới kb/incidents/<YYYY-MM>/<YYYY-MM-DD>-<topic>.md + 1 dòng trong kb/incidents/index.md (KHÔNG append vào kb/INCIDENTS.md — file đó nay chỉ là STUB REDIRECT).
6. BẮT BUỘC (khác việc 5, đây là hợp đồng đầu ra máy đọc được — dispatch này chạy nền, không ai chờ trực tiếp, nên đây là tín hiệu DUY NHẤT phân biệt \"đã xong thật\" với \"lạc đề/chết im\"): kết thúc bằng ĐÚNG MỘT trong hai lệnh sau — (a) nếu đã chẩn đoán+sửa+verify xong (hoặc xác nhận không có gì để sửa): append_event.sh Winston finding \"ops-autofix-done: $LABEL\" \"<JSON: root_cause, fix, verify>\"; (b) nếu gặp ranh giới cấm ở việc 3 hoặc không chẩn đoán được: append_event.sh Winston question \"ops-autofix-unresolved: $LABEL\" \"<JSON: ly_do>\". Thiếu bước này = lần chạy này coi như KHÔNG xác nhận được, dù các việc 1-5 có làm đúng đến đâu." \
  --bg --thread "$TRADING_DAILY_THREAD" --timeout "$AUTOFIX_TIMEOUT" --model opus 2>&1 | tail -3

echo "[ops_autofix] dispatched fixer for '$LABEL'"
