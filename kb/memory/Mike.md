# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái 2026-09-30 11:26 ICT — Tất cả việc đã XONG, không còn gì cần theo dõi ngay
- 4 việc gốc (question_commit_hint, PNJ exclude, headless-merge escalation, VNM exright) — xong.
- 2 câu hỏi phụ Taylor (is_stable_payer, park insider/anomaly gate) — user trả lời + duyệt wire:
  Fix A = WorkingClaude 91eb663d, Fix B = mike 95fe407e. Cả 2 CONFIRMED/high quant-skeptic (2 vòng
  mỗi fix), commit sạch, 7/7 selfcheck PASS hậu-commit, production table chưa đổi (tự có hiệu lực
  ở lần chạy tự nhiên kế: custom30_history.py trong papertrade_daily.sh 15:30 ICT hôm nay;
  compute_park_add.py ở lần DollarBill build plan park-add kế tiếp). CHUỖI ĐÃ ĐÓNG HOÀN TOÀN.

## Tồn đọng nhỏ, không khẩn, để dành review sau (~2027-02-10)
- custom30v_8l nên thêm cột label_asof (open/closed) để phân biệt nhãn lịch sử vs nhãn live.
- Lịch sử đã đóng vẫn tính lại mỗi phiên từ feed live — feed rollback có thể âm thầm sửa nhãn cũ.
- corp_action feed đang đúng ngưỡng 4 ngày tuổi (CORP_ACTION_STALE_DAYS_MAX) — nếu Winston không
  nạp mới thì từ 2026-10-01 kỳ đang mở custom30v_8l sẽ hiện NO_DATA. Đáng báo Winston biết trước.

## Không còn việc gì đang mở cần theo dõi ngay
- Việc 3 (headless merge production) — escalation vẫn PENDING chờ user trả lời 2 câu hỏi follow-up
  (runbook hoá direct-commit? soạn feedback Anthropic?) — không khẩn, chờ user rảnh.

## Bẫy đã ghi lại (đừng cắn lần nữa)
- Selfcheck neo bản cũ bằng `HEAD`/`main` ⇒ sau merge FAIL vĩnh viễn. Luôn neo `<commit-vá>^`.
- Selfcheck hardcode gốc canonical ⇒ chạy từ worktree test MASTER thay vì code đang sửa.
- notify_thread.sh inline double-quote với backtick trong nội dung → command substitution ăn mất
  chữ — LUÔN build message qua heredoc biến MSG trước khi gọi notify_thread.sh nếu nội dung có
  backtick/code identifier. Cắn thật 2026-09-30 11:19 ICT.

