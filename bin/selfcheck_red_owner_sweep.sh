#!/usr/bin/env bash
# selfcheck_red_owner_sweep.sh — Thứ Sáu hàng tuần: giao backlog câu hỏi `selfcheck-red: *` cho
# CHỦ SỞ HỮU CỐ ĐỊNH rà + đóng (user duyệt 2026-10-08, bus question
# `Mike/retro-pattern-recurring-selfcheck-red-backlog-not-closed`, phương án A của Wags 24b6dfee).
#
# Vấn đề gốc: selfcheck_baseline_diff.py mở question khi 1 selfcheck đỏ, ack `triaged-needs-human`
# suppress 14 ngày — nhưng KHÔNG có ai được giao sửa ⇒ 17 câu tồn 10 ngày, 0 đóng.
# Phân công (theo VỊ TRÍ file, không theo nội dung):
#   - `mike/bin/*`           → Wags   (hạ tầng fleet)
#   - file gốc WorkingClaude → Taylor (code nghiên cứu/production repo ngoài)
# Câu nào xanh lại thì selfcheck_baseline_diff.py (04:30 ICT hằng ngày) TỰ đóng; script này chỉ
# đảm bảo có người làm cho nó xanh, hoặc đóng có bằng chứng nếu là false-positive/selfcheck lỗi thời.
#
# Lịch: 16:30 ICT Thứ Sáu (`30 9 * * 5` UTC) — sau papertrade_daily 15:30 (worst DONE 15:42) và custom30v watch 16:05.
# Idempotent: stamp state/selfcheck_red_sweep/<ngày>_<chủ>.done chứa JOB_ID. Lần chạy sau cùng ngày
# hỏi jobs.sh: job done/running/overdue/pending-resume ⇒ bỏ qua; failed/timeout/cancelled/không tìm thấy
# ⇒ giao lại (sửa 2026-10-09, user duyệt: trước đây stamp ghi ngay khi 'sent' nên job hỏng vì OAuth
# 16:30 bị coi là đã làm cả tuần). Lượt bù: cron 18:52 Thứ Sáu chạy lại chính script này.
# Stamp rỗng (bản cũ) ⇒ không biết job nào ⇒ bỏ qua như trước (không dispatch chồng).
# Chạy tay: bin/selfcheck_red_owner_sweep.sh [--dry-run]
set -uo pipefail
ROOT="/home/trido/thanhdt/WorkingClaude/mike"
STATE_DIR="$ROOT/state/selfcheck_red_sweep"
ARCH_THREAD="$("$ROOT/bin/discord_channel.sh" architecture)"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
log() { echo "[$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%dT%H:%M:%S%z)] $*"; }
mkdir -p "$STATE_DIR"

log "=== selfcheck_red_owner_sweep START (dry=$DRY) ==="

# Danh sách câu đang mở, tách theo chủ. Lỗi đọc audit ⇒ DỪNG có tiếng (không coi là "0 câu").
# rc của bus_question_audit.py = SỐ câu pending (không phải mã lỗi) ⇒ không xét rc, xét JSON parse được.
_audit_err="$(mktemp)"
AUDIT_JSON="$(python3 "$ROOT/bin/bus_question_audit.py" --json 2>"$_audit_err")"
if ! LISTS="$(printf '%s' "$AUDIT_JSON" | python3 -c '
import json, sys
d = json.load(sys.stdin)
P = "selfcheck-red: "
for q in d.get("pending", []):
    t = q.get("topic", "")
    if q.get("agent") != "Wags" or not t.startswith(P):
        continue
    f = t[len(P):]
    owner = "Wags" if f.startswith("mike/") else "Taylor"
    print("%s\t%s\t%s" % (owner, (q.get("ts") or "")[:10], f))
' 2>>"$_audit_err")"; then
  log "ERROR: không đọc được bus_question_audit — lỗi thật: $(head -c 500 "$_audit_err")"
  "$ROOT/bin/notify_thread.sh" "🔴 selfcheck_red_owner_sweep: không đọc được danh sách câu hỏi (bus_question_audit lỗi) — tuần này CHƯA giao việc. Xem logs/selfcheck_red_owner_sweep.log." "$ARCH_THREAD" >/dev/null 2>&1 || true
  rm -f "$_audit_err"; exit 1
fi
rm -f "$_audit_err"

for OWNER in Wags Taylor; do
  ITEMS="$(printf '%s\n' "$LISTS" | awk -F'\t' -v o="$OWNER" '$1==o {print "- `selfcheck-red: " $3 "` (mở từ " $2 ")"}')"
  N="$(printf '%s' "$ITEMS" | grep -c '^- ' || true)"
  if [ "$N" -eq 0 ]; then log "$OWNER: 0 câu mở — bỏ qua"; continue; fi
  STAMP="$STATE_DIR/${TODAY}_${OWNER}.done"
  if [ -e "$STAMP" ]; then
    PREV_JOB="$(head -n1 "$STAMP" 2>/dev/null | tr -d '[:space:]')"
    if [ -z "$PREV_JOB" ]; then log "$OWNER: đã dispatch hôm nay ($STAMP, stamp cũ không có job_id) — bỏ qua"; continue; fi
    "$ROOT/bin/jobs.sh" status "$PREV_JOB" >/dev/null 2>&1; PREV_RC=$?
    case "$PREV_RC" in
      0|2|3|5) log "$OWNER: job hôm nay $PREV_JOB còn sống/đã xong (jobs.sh rc=$PREV_RC) — bỏ qua"; continue ;;
      *) log "$OWNER: job hôm nay $PREV_JOB KHÔNG thành công (jobs.sh rc=$PREV_RC: 1=failed/timeout/cancelled, 4=không tìm thấy) ⇒ giao lại" ;;
    esac
  fi
  if [ "$OWNER" = "Wags" ]; then
    LOC='nằm trong repo mike (/home/trido/thanhdt/WorkingClaude/mike/bin/...)'
  else
    LOC='nằm ở GỐC repo WorkingClaude (/home/trido/thanhdt/WorkingClaude/<file>)'
  fi
  PROMPT="$(cat <<'PROMPT_EOF'
SELFCHECK-RED OWNER SWEEP (tự động, Thứ Sáu hằng tuần). Headless mode.
Bạn là CHỦ SỞ HỮU CỐ ĐỊNH của nhóm câu hỏi bus `selfcheck-red: *` bên dưới (user duyệt 2026-10-08,
question Mike/retro-pattern-recurring-selfcheck-red-backlog-not-closed). Suppress 14 ngày KHÔNG phải
"đã xử lý" — việc của bạn là làm cho từng câu ĐÓNG có bằng chứng, hoặc nói rõ vì sao chưa đóng được.

Với MỖI file trong danh sách:
1. Chạy lại selfcheck trên HEAD canonical bằng đúng interpreter runner dùng: `$DNA_PYEXE` cho .py
   (source /home/trido/thanhdt/WorkingClaude/wc_env.sh), `bash` cho .sh. Lấy output thật.
2. Phân loại bằng bằng chứng vừa đọc (§29 — không đoán):
   (a) ĐÃ XANH ⇒ đóng ngay: `python3 bin/close_bus_question.py "Wags/selfcheck-red: <file>" --resolution "..." --evidence "<rc=0 + dòng tổng kết>" --actor <bạn>`
   (b) selfcheck LỖI THỜI (assertion cứng số đếm/vị trí, fixture cũ, hardcode đường dẫn canonical) ⇒ sửa
       selfcheck trong worktree riêng, chạy lại xanh (+ dưới `env -u TZ`), merge, đóng kèm commit.
   (c) BUG THẬT trong code production ⇒ sửa trong worktree, arch-reviewer (Agent subagent_type
       arch-reviewer) phải APPROVED trước khi merge; chạy selfcheck theo phạm vi (§23). Đóng kèm commit.
   (d) phụ thuộc môi trường (TZ, cache, credential, file sống) ⇒ sửa phụ thuộc, không nới assertion.
   (e) tính năng đã gỡ/selfcheck không còn ý nghĩa ⇒ KHÔNG tự xoá; ghi đề xuất retire kèm bằng chứng.
3. RANH GIỚI CỨNG — KHÔNG tự sửa: trade plan, trading_rules.json, logic đặt lệnh
   (trading_bot/executor.py, bot_execute.py, đường giá/khối lượng lệnh), crontab, xoá dữ liệu,
   BOT_STOP, file data sống. Gặp ⇒ chỉ chẩn đoán, gom vào MỘT bus question cho user.
4. Không xong hết trong lượt này là bình thường — ưu tiên câu CŨ NHẤT, đừng vội vàng sửa ẩu.

Kết thúc: ghi ĐÚNG 1 bus finding topic `selfcheck-red-owner-sweep-<YYYY-MM-DD>-<bạn>` với bảng
file → phân loại → hành động → trạng thái (CLOSED+commit / OPEN+lý do). Đọc finding sweep các tuần
trước: câu nào OPEN qua ≥2 sweep liên tiếp ⇒ đánh dấu "CẦN USER" trong finding và post 1 dòng vào
topic Architecture. Không mở question riêng cho từng file.

Danh sách câu đang mở (file
PROMPT_EOF
)"
  PROMPT="$PROMPT $LOC):
$ITEMS"
  log "$OWNER: $N câu mở → dispatch"
  if [ "$DRY" -eq 1 ]; then printf '%s\n----\n' "$PROMPT"; continue; fi
  if OUT="$("$ROOT/bin/dispatch.sh" "$OWNER" "$PROMPT" --bg --model opus --effort high --timeout 5400 --thread "$ARCH_THREAD" 2>&1)"; then
    JOB="$(printf '%s' "$OUT" | grep -oE 'job=[A-Za-z]+_[0-9]{8}_[0-9]{6}' | head -n1 | cut -d= -f2)"
    if [ -n "$JOB" ]; then
      printf '%s\n' "$JOB" >"$STAMP.tmp" && mv "$STAMP.tmp" "$STAMP"
    else
      # Không bóc được job_id ⇒ stamp rỗng = bỏ qua lượt bù (an toàn: không dispatch chồng).
      log "WARNING: không bóc được job_id từ output dispatch — stamp rỗng, lượt bù sẽ không kiểm được job"
      : >"$STAMP"
    fi
    log "$OWNER: dispatched job=${JOB:-?} — $(printf '%s' "$OUT" | tail -1)"
  else
    log "ERROR: dispatch $OWNER thất bại — lỗi thật: $(printf '%s' "$OUT" | tail -3)"
    "$ROOT/bin/notify_thread.sh" "🔴 selfcheck_red_owner_sweep: dispatch $OWNER thất bại ($N câu chưa được giao). Lỗi: $(printf '%s' "$OUT" | tail -1)" "$ARCH_THREAD" >/dev/null 2>&1 || true
  fi
done
log "=== selfcheck_red_owner_sweep END ==="
