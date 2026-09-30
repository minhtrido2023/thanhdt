# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái 2026-09-30 09:50 ICT — 4 việc user giao đã XONG
- Việc 1 (question_commit_hint bắt buộc-hoá): CONFIRMED arch-review vòng 3 + wire bắt buộc vào
  dispatch.sh (cả --bg/foreground), commit ff340ea8→7d3f4991. Bus question retro-pattern-recurring-
  bus-question-closure-gap-real-fix-no-answer-event đã đóng (resolver tự nhận qua decision event).
- Việc 2 (PNJ exclude): xong, cả 2 account, review trigger = PNJ BCTC Q3/2026 (event-based).
- Việc 3 (headless merge production): KHÔNG thể cấp qua config — classifier tầng platform, ngoài
  tầm dispatch.sh. Đã đề xuất workaround (ưu tiên direct-commit thay vì feature-branch+merge).
  Bus question retro-pattern-recurring-classifier-blocks-headless-agent-production-write còn PENDING
  (age 1 ngày) — chờ user trả lời 2 câu hỏi follow-up (runbook hoá direct-commit? soạn feedback
  Anthropic xin exception thật?).
- Việc nhỏ (VNM exright_date): Winston đã xác nhận lệch 1 phiên, đã báo, không cần làm thêm.

## Còn mở, không cần user quyết ngay
- 2 câu hỏi thiết kế phụ của Taylor (calculated_fear_state_backstop.md 2026-09-28): is_stable_payer
  tự rớt khi DN không chia cổ tức? đường park có nên đọc insider_flags.json/anomaly_flags.json?
- Escalation classifier-block (Việc 3) chờ user trả lời.

## Bẫy đã ghi lại (đừng cắn lần nữa)
- Selfcheck neo bản cũ bằng `HEAD`/`main` ⇒ sau merge FAIL vĩnh viễn. Luôn neo `<commit-vá>^`.
- Selfcheck hardcode gốc canonical ⇒ chạy từ worktree test MASTER thay vì code đang sửa.
- Đóng 1 `question` do AGENT KHÁC đăng lên bus vẫn cần 1 `answer`/`decision` ngắn TRÊN BUS.
- `git show <rev>:<path>` tính path từ GỐC REPO, `git diff … -- <pathspec>` tính từ CWD.
- Append text phụ vào $logfile của job LÀ THAY ĐỔI VĂN BẢN user-facing nếu có consumer chụp cửa sổ
  (tail -c N) — luật: trước khi ghi thêm vào artifact người khác, grep xem ai chụp cửa sổ nó.

