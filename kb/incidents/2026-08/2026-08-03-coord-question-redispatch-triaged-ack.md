---
kind: incident
date: 2026-08-03
topic: coord-question-redispatch-triaged-ack
title: >-
  2026-08-03: ops_health_check check #5 dispatch LẶP wags_autofix cho 2 câu hỏi đã triage xong
  là "chỉ NGƯỜI quyết được" — ranh giới WARN-ONLY bám TUỔI (48h) thay vì TRẠNG THÁI triage
status: fixed
category: dispatch-orchestration
origin: >-
  job Wags_20260803_054508 (wags_autofix coord-2026-08-03) nhận đúng 2 câu hỏi mà job Wags
  trước đó 4h25 (Wags_20260803_012008) đã triage và Mike weekly editorial 02:38 đã xác nhận lại
recorder: Wags (Fleet Ops Coordinator), job Wags_20260803_054508
---

# 2026-08-03 — checker dispatch LẶP Wags cho câu hỏi đã triage "chờ NGƯỜI" — thêm ACK `triaged-needs-human:`

**What happened.** `ops_health_check.sh` check #5 (08:20/12:45 + preflight) dispatch
`wags_autofix.sh coord-2026-08-03` lúc 05:45 với đúng 2 câu hỏi mà một job Wags TRƯỚC ĐÓ
(`Wags_20260803_012008`, 01:20) đã triage xong và kết luận là THẬT nhưng **chỉ NGƯỜI/thời gian
quyết được, không có fix tooling nào**:
- `Mike/retro-pattern-recurring-silent-cron-spof-2` — chờ 3–5 ngày xác nhận 3 cơ chế phòng mới
  (`cron_health_check_daily.sh`, `shellcheck_gate.sh`, forcing-function dispatch) chạy sạch;
- `Winston/ops-autofix-unresolved: run-bot-fail-ZaloPay-2026-08-03` — KHÔNG PHẢI BUG, plan
  `requires_user_approval=true` + `approved_by=null`, code-gate hoạt động ĐÚNG; chỉ user duyệt
  được, Wags bị cấm cứng đụng trade plan.

Mike weekly editorial 02:38 (mục 11 "bus question hygiene") đã xác nhận lại y hệt: "2 pending
còn lại có lý do rõ ràng". 3h07 sau, checker vẫn đốt thêm 1 job Wags (Opus) cho đúng 2 câu đó.

**Root cause.** Checker có 2 nhánh `[WARN-ONLY]` (không spawn agent) — câu hỏi TREO LÂU >48h và
`wags-fix-not-confirmed:*` — với **đúng lý do "loại câu hỏi này chỉ user quyết được, spawn Wags
lặp lại vô nghĩa"**. Nhưng ranh giới lại là TUỔI (48h), không phải TRẠNG THÁI TRIAGE: một câu
hỏi đã được kết luận "cần người" vẫn ở `pending_q` → `COORD_WARN` → dispatch 2 lần/ngày suốt
48h đầu, rồi mới rơi vào nhánh WARN-ONLY. Kết quả triage của vòng trước **không có chỗ nào để
ghi lại** nên vòng sau bắt đầu lại từ đầu — đúng lớp lỗi "suy luận lại từ trạng thái hiện tại
thay vì ghi sự thật bền ngay lúc phát sinh" (coding_guidelines mục 5).

**Fix** (commit `<xem finding bus>`): ACK có chủ đích, không phải nới matcher.
Agent triage ghi `append_event.sh <id> status "triaged-needs-human: <topic câu hỏi gốc>" '<lý do>'`.
Check #5 gom `acks` (khớp CHÍNH XÁC topic hoặc dạng `Agent/topic`, ack phải đăng SAU câu hỏi) và
đẩy câu hỏi sang dòng `[WARN-ONLY] … ĐÃ TRIAGE, chờ NGƯỜI quyết`.
Ranh giới cố ý: ack **chỉ tắt auto-dispatch** — KHÔNG đụng `resolvers`/`_resolved()`, KHÔNG đóng
câu hỏi, KHÔNG giấu khỏi báo cáo (tránh dựng lại đúng lỗi mà arch-reviewer đã bác ở vòng
auto-close "EXPIRED-30d" 07-30). Fail-closed: không ack / sai topic / ack đăng trước câu hỏi →
dispatch y như cũ. Không cần hạn dùng: quá 48h câu hỏi tự sang nhánh TREO LÂU (cũng WARN-ONLY).

**Verify.** `bash -n` OK; `ops_health_check_selfcheck.py` 39/39 PASS (30 cũ + 9 assertion mới,
ca 12–13); 2 mutation độc lập đều ĐỎ được (bỏ nhánh ack → 2 FAIL; bỏ so sánh timestamp → 1 FAIL).
Chạy thật `OPS_HEALTH_DRY_RUN=1 bin/ops_health_check.sh --account ZaloPay`: 2 câu hỏi hiện đầy
đủ trên dòng `[WARN-ONLY]`, không còn dòng routable → `COORD_WARN` rỗng → không dispatch.

**Lesson.** Khi một nhánh WARN-ONLY đã tồn tại với lý do "chỉ người quyết được", kiểm tra xem
ranh giới của nó là TRẠNG THÁI hay chỉ là một proxy dễ code (ở đây: tuổi 48h). Proxy sai làm
đúng lớp lãng phí mà nhánh đó sinh ra để chặn vẫn xảy ra, chỉ là trong cửa sổ hẹp hơn.
