#!/usr/bin/env bash
# paper_checkpoint_escalation.sh — phát hiện + escalate checkpoint paper-program đã tới hạn
# nhưng CHƯA có ai thực sự đánh giá (gate_criteria vẫn "pending").
#
# Root cause (2026-08-04, user hỏi "sao vẫn treo mà không có đánh giá gì"): paper_programs_daily_report.sh
# (cron 09:00 T2-T6) chỉ MÔ TẢ trạng thái mỗi ngày — với "fill_timing" (end=2026-07-31, ĐÃ QUA 4 ngày,
# 0/5 gate) và "vol_scale_chase_cap" (ngưỡng evidence 10 phiên đã qua từ ~07-20, 4/5 gate vẫn pending),
# report lặp lại NGUYÊN VĂN "đã qua, CHƯA xác nhận" mỗi ngày từ 07-31 mà không có forcing function nào
# biến "nhắc" thành "hành động" — CÙNG root cause class với báo cáo tuần/tháng bị bỏ sót đã fix
# 2026-08-01 (check_report_cadence.sh), nhưng chưa ai làm bản tương đương cho paper-program checkpoint.
#
# Detection (đơn giản, cơ học, không tái tạo logic đếm evidence-session của report chính — tránh
# duplicate fragile logic, xem coding_guidelines.md §2/§3):
#   (a) `end` (lịch, YYYY-MM-DD) đã set và đã qua hôm nay, HOẶC
#   (b) text `review_short`/`end_or_trigger` chứa cả "đã qua" VÀ "xác nhận" VÀ "chưa" (không phân biệt
#       hoa/thường) — đúng cụm mà Taylor tự tay ghi khi 1 checkpoint evidence-based đã qua ngưỡng
#       nhưng chưa xác nhận (xem vol_scale_chase_cap.review_short).
# Idempotent: state/paper_checkpoint_escalated.json, mỗi program chỉ escalate lại sau ≥7 ngày.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
TRADING_REPORT_THREAD="trading_report"
REGISTRY="$ROOT/kb/paper_programs_registry.json"
STATE="$ROOT/state/paper_checkpoint_escalated.json"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
COOLDOWN_DAYS=7

mkdir -p "$ROOT/state"
[ -f "$STATE" ] || echo '{}' > "$STATE"

PLAN="$(python3 - "$REGISTRY" "$STATE" "$TODAY" "$COOLDOWN_DAYS" <<'PYEOF'
import json, sys
from datetime import date, timedelta

reg_path, state_path, today_s, cooldown_s = sys.argv[1:5]
today = date.fromisoformat(today_s)
cooldown = int(cooldown_s)

with open(reg_path) as f:
    reg = json.load(f)
progs = reg.get("programs", reg) if isinstance(reg, dict) else reg

with open(state_path) as f:
    state = json.load(f)

actions = []
for p in progs:
    pid = p.get("id")
    end = p.get("end")
    review_short = (p.get("review_short") or "") + " " + (p.get("end_or_trigger") or "")
    low = review_short.lower()

    overdue = False
    reason = ""
    if end:
        try:
            if date.fromisoformat(end) < today:
                overdue = True
                reason = f"checkpoint lịch đã qua (end={end})"
        except ValueError:
            pass
    if not overdue and ("đã qua" in low and "xác nhận" in low and "chưa" in low):
        overdue = True
        reason = "text checkpoint tự ghi 'đã qua ... chưa xác nhận'"

    if not overdue:
        continue

    gates = p.get("gate_criteria", [])
    pending = [g["text"] for g in gates if g.get("status") == "pending"]
    if not pending:
        continue  # đã đánh giá hết, không còn gì để escalate

    last_esc = state.get(pid)
    if last_esc:
        try:
            if (today - date.fromisoformat(last_esc)).days < cooldown:
                continue
        except ValueError:
            pass

    actions.append({
        "id": pid,
        "name": p.get("name", pid),
        "owner": p.get("owner", "Taylor"),
        "reason": reason,
        "pending_count": len(pending),
        "total_count": len(gates),
        "pending_gates": pending,
        "charter": f"mike/kb/paper_programs_charter/{pid}.md",
    })

print(json.dumps(actions, ensure_ascii=False))
PYEOF
)"

N=$(echo "$PLAN" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
if [ "$N" -eq 0 ]; then
  echo "paper_checkpoint_escalation: OK — không có checkpoint paper-program nào quá hạn và bị bỏ ngỏ."
  exit 0
fi

# BATCH: cùng lý do và cùng cơ chế với check_report_cadence.sh — N checkpoint quá hạn = N job
# Taylor --bg, CÙNG $TRADING_REPORT_THREAD, from=Mike ⇒ không gộp thì N lượt wake vào một
# thread ⇒ phiên Mike song song, post trùng (RCA plan_pipeline_3loi_rca_20260820.md lỗi #1;
# arch-reviewer vòng 6, #1). $N đếm xong TRƯỚC vòng lặp nên `expected` là số thật.
# Ở file này dispatch fail được xử lý tường minh (`continue` khi DRC≠0) ⇒ member đó KHÔNG đăng
# ký ⇒ `expected` cao hơn số member thật ⇒ anh em nhường thêm tối đa BATCH_REG_GRACE_S (600s)
# rồi bắn. Trễ có trần, không nuốt lượt. CỐ Ý không hạ $N sau mỗi lần fail: $N phải cố định
# TRƯỚC vòng lặp, còn `expected` trong batch record chỉ tăng (max) chứ không giảm.
PAPER_BATCH_ID="papercheckpoint_$(TZ='Asia/Ho_Chi_Minh' date +%Y%m%d_%H%M%S)"
echo "paper_checkpoint_escalation: [batch] wake gộp cho $N job Taylor — batch_id=$PAPER_BATCH_ID"

echo "$PLAN" | python3 -c "
import json, sys
for a in json.load(sys.stdin):
    gates = ' | '.join(a['pending_gates'])
    print(f\"{a['id']}\t{a['name']}\t{a['owner']}\t{a['reason']}\t{a['pending_count']}\t{a['total_count']}\t{a['charter']}\t{gates}\")
" | while IFS=$'\t' read -r PID NAME OWNER REASON PCOUNT TCOUNT CHARTER GATES; do
  MSG="🔴 **Paper-program checkpoint quá hạn, chưa có đánh giá — ${NAME}** (\`${PID}\`, phụ trách ${OWNER}). Lý do: ${REASON}. Còn ${PCOUNT}/${TCOUNT} tiêu chí gate ở trạng thái pending: ${GATES}. Đây là auto-dispatch từ paper_checkpoint_escalation.sh (cron) — Taylor đang được giao đi kiểm tra thực tế + cập nhật registry. Chi tiết: \`${CHARTER}\`."
  echo "$MSG"
  "$ROOT/bin/notify_thread.sh" "$MSG" "$TRADING_REPORT_THREAD" 2>/dev/null || true
  "$ROOT/bin/append_event.sh" Mike question "paper-checkpoint-overdue-${PID}" \
    "{\"program\":\"${PID}\",\"reason\":\"${REASON}\",\"pending_gates\":${PCOUNT},\"question\":\"Checkpoint paper-program qua han, da auto-dispatch Taylor kiem tra. Xac nhan/theo doi.\"}" \
    2>/dev/null || true
  PROMPT="Checkpoint paper-program '${NAME}' (id=${PID}) trong mike/kb/paper_programs_registry.json đã tới hạn theo dữ liệu thật nhưng ${PCOUNT}/${TCOUNT} tiêu chí gate vẫn 'pending' — chưa ai thực sự đi kiểm tra. Đọc charter mike/kb/paper_programs_charter/${PID}.md + registry entry đầy đủ (data_sources, probe) trước khi làm. Với MỖI tiêu chí pending, kiểm tra bằng dữ liệu thật (journal paper main, execution_quality_review.py, hoặc nguồn được khai trong registry) — đừng suy đoán. Cập nhật status từng gate_criteria trong registry (pass/fail/pending kèm lý do) và review_short nếu cần. Nếu ĐỦ điều kiện chuyển bước tiếp (quant-skeptic rerun / user sign-off) thì CHUẨN BỊ đề xuất rõ ràng cho user quyết — KHÔNG tự bật live. Nếu CHƯA đủ, nói rõ còn thiếu gì + ước thời gian cần thêm. Ghi bus finding khi xong: program id, kết luận từng gate, khuyến nghị bước kế tiếp."
  # DISPATCH TRƯỚC, ack/cooldown SAU — và chỉ khi dispatch THẬT SỰ thành công.
  # Thứ tự cũ (ack ở trên, dispatch ở dưới, exit code bị `| tail -5` nuốt, cooldown ghi vô
  # điều kiện) biến 1 dispatch hỏng thành ĐIỂM MÙ 7 NGÀY: bus khẳng định "đã dispatch
  # ${OWNER}", question bị hạ xuống WARN-ONLY nên không wags_autofix nào đi triage, và
  # cooldown chặn escalate lại — đúng cái detector mà chính commit này vừa gỡ đi
  # (arch-reviewer NEEDS_CHANGES high, coord-2026-08-05; pattern monitoring-fix-creates-silence).
  DISPATCH_OUT="$("$ROOT/bin/dispatch.sh" Taylor "$PROMPT" --thread "$TRADING_REPORT_THREAD" --bg --model opus --effort high --timeout 2400 \
    --batch-id "$PAPER_BATCH_ID" --batch-size "$N" 2>&1)"
  DRC=$?
  printf '%s\n' "$DISPATCH_OUT" | tail -5

  if [ "$DRC" -ne 0 ]; then
    # FAIL-CLOSED: circuit breaker OPEN, model/provider sai, dispatch.sh lỗi… → KHÔNG ack
    # (question ở lại pending_q routable để wags_autofix đi triage), KHÔNG ghi cooldown
    # (lần chạy sau tự thử lại), và phát event `error` để có dấu vết chủ động.
    "$ROOT/bin/append_event.sh" Wags error "paper-checkpoint-dispatch-failed-${PID}" \
      "{\"program\":\"${PID}\",\"rc\":${DRC},\"owner\":\"${OWNER}\",\"note\":\"dispatch owner THAT BAI — khong ack, khong ghi cooldown, question giu nguyen routable\",\"dispatch_tail\":$(printf '%s' "$DISPATCH_OUT" | tail -3 | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')}" \
      2>/dev/null || true
    WARN="⚠️ **Dispatch ${OWNER} THẤT BẠI** cho checkpoint quá hạn \`${PID}\` (rc=${DRC}). Không ack, không đặt cooldown — sẽ escalate lại lần chạy sau; câu hỏi \`paper-checkpoint-overdue-${PID}\` vẫn ở diện Wags triage."
    echo "$WARN"
    "$ROOT/bin/notify_thread.sh" "$WARN" "$TRADING_REPORT_THREAD" 2>/dev/null || true
    continue
  fi

  # Ack `triaged-needs-human:` (ACK_PREFIX của ops_health_check.sh check #5) — CHỈ hợp lệ vì
  # dispatch owner ở trên đã thành công: câu hỏi này thật sự đã được giao, chỉ còn chờ NGƯỜI
  # xác nhận/theo dõi, không có fix tooling nào để Wags làm. Không ack thì nó nằm mãi trong
  # pending_q (script này KHÔNG BAO GIỜ phát answer/decision cùng topic) → COORD_WARN dispatch
  # wags_autofix 2 lần/ngày suốt 48h cho việc ĐÃ được giao (sự cố thật coord-2026-08-05).
  # Ack CHỈ tắt auto-dispatch — câu hỏi vẫn hiện đầy đủ ở dòng "ĐÃ TRIAGE, chờ NGƯỜI quyết"
  # cho tới khi có answer/decision thật, nên KHÔNG tạo im lặng mới.
  # agent_id = Wags (không phải Mike): tác giả thật của ack là cơ chế điều phối này, ghi Mike
  # làm audit trail nói dối là Mike đã triage. `_acked()` gom ack toàn cục nên đổi id không
  # ảnh hưởng matching — phần "Mike/" trong TOPIC là khoá trỏ tới câu hỏi, phải giữ.
  "$ROOT/bin/append_event.sh" Wags status "triaged-needs-human:Mike/paper-checkpoint-overdue-${PID}" \
    "{\"program\":\"${PID}\",\"note\":\"auto-triaged: da dispatch ${OWNER} kiem tra (dispatch rc=0), chi cho nguoi xac nhan — khong co fix tooling\"}" \
    2>/dev/null || true

  python3 -c "
import json
state = json.load(open('$STATE'))
state['$PID'] = '$TODAY'
json.dump(state, open('$STATE', 'w'), indent=2, ensure_ascii=False)
"
done
