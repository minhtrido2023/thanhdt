# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái 2026-09-30 11:20 ICT — Tất cả việc user giao đã XONG
- 4 việc gốc (question_commit_hint, PNJ exclude, headless-merge escalation, VNM exright) — xong,
  xem lịch sử trước.
- 2 câu hỏi phụ Taylor (is_stable_payer, park insider/anomaly gate) — user đã trả lời trực tiếp:
  is_stable_payer: phải có trả cổ tức mỗi năm (dù ít), thiếu 1 năm tự rớt.
  park: phải đọc insider_flags để quyết mua.
  → Dispatch Taylor_20260930_030814: Fix A (custom30_history.py re-evaluate is_stable_payer tại
  asof=hôm nay cho kỳ mở, không đụng lịch sử đã đóng) + Fix B (compute_park_add.py đọc
  anomaly_gate.py: anomaly=HARD EXCLUDE, insider=WATCH cảnh báo). Cả 2 qua 2 vòng quant-skeptic
  (vòng 1 REFUTED bắt bug thật mỗi lần, vòng 2 CONFIRMED/high). 1 câu hỏi thiết kế phát sinh
  (hard-block hay chỉ cảnh báo insider) — user chốt (b) cảnh báo, đã đóng bus question
  Taylor/park-insider-hard-block-hay-canh-bao. Cả 2 fix ĐÃ COMMIT: Fix A = WorkingClaude 91eb663d,
  Fix B = mike 95fe407e (job Taylor_20260930_041900). CHƯA wire vào plan thật/cron — cần thêm
  arch-review nếu muốn đưa production chính thức.

## Không còn việc gì đang mở cần theo dõi ngay
- Việc 3 (headless merge production) — escalation vẫn PENDING chờ user trả lời 2 câu hỏi follow-up
  (runbook hoá direct-commit? soạn feedback Anthropic?) — không khẩn, chờ user rảnh.

## Bẫy đã ghi lại (đừng cắn lần nữa)
- Selfcheck neo bản cũ bằng `HEAD`/`main` ⇒ sau merge FAIL vĩnh viễn. Luôn neo `<commit-vá>^`.
- Selfcheck hardcode gốc canonical ⇒ chạy từ worktree test MASTER thay vì code đang sửa.
- Append text phụ vào $logfile của job LÀ THAY ĐỔI VĂN BẢN user-facing nếu có consumer chụp cửa sổ.
- notify_thread.sh inline double-quote với backtick trong nội dung → command substitution ăn mất
  chữ (đúng bug đã biết, dispatch-prompt-heredoc skill) — LUÔN build message qua heredoc biến MSG
  trước khi gọi notify_thread.sh nếu nội dung có backtick/code identifier, kể cả lệnh đơn giản
  tưởng như vô hại. Cắn thật 2026-09-30 11:19 ICT ngay trong phiên này.

