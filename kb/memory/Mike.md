# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái 2026-09-30 12:05 ICT — Tất cả việc đã XONG, chờ 1 quyết định nhỏ
- Chuỗi is_stable_payer + park insider/anomaly gate + label_asof column đã đóng hoàn toàn.
  3 commit: WorkingClaude 91eb663d (Fix A), mike 95fe407e (Fix B), WorkingClaude 038a4805
  (label_asof). Tất cả CONFIRMED quant-skeptic, đã commit sạch.

## CHỜ USER: cột label_asof chưa vào schema BQ production
- custom30v_8l CSV/code đã có cột label_asof nhưng bảng BQ thật (tav2_bq.custom30v_8l) CHƯA thêm
  field label_asof:DATE — cố ý chưa tự ý bq load. Lần chạy production kế (papertrade_daily.sh
  [6b], 15:30 ICT hôm nay 2026-09-30) sẽ chạy với schema CŨ cho tới khi user duyệt thêm field.
  Không khẩn, không phải bug.

## Tồn đọng rất nhỏ, không chặn
- selfcheck [E] có thể siết thêm (assert open-period label_asof >= rebal_date) — quant-skeptic đề
  xuất, chưa làm, không ảnh hưởng kết quả hiện tại.
- corp_action feed max_ingested gần ngưỡng stale — Winston nên biết trước 2026-10-01.

## Bài học mới: job record có thể "kẹt" dù việc đã xong (wrapper quên update)
- Gặp job status=running/OVERDUE nhưng bus đã có event kết quả khớp topic + thời gian → PID chết
  (ps rỗng) + logfile không tồn tại = đủ bằng chứng dùng `mike_json.py job-set ... status=done
  ended_at=<epoch> result_summary='...' --force` để dọn bảng theo dõi. Tool tự chặn nếu thiếu
  ended_at/result_summary hoặc thiếu bằng chứng — đúng thiết kế, không phải bug.

## Không còn việc gì đang mở cần theo dõi ngay
- Việc 3 (headless merge production) — escalation vẫn PENDING chờ user trả lời 2 câu hỏi follow-up
  (runbook hoá direct-commit? soạn feedback Anthropic?) — không khẩn, chờ user rảnh.

## Bẫy đã ghi lại (đừng cắn lần nữa)
- Selfcheck neo bản cũ bằng `HEAD`/`main` ⇒ sau merge FAIL vĩnh viễn. Luôn neo `<commit-vá>^`.
- notify_thread.sh inline double-quote với backtick → LUÔN build message qua heredoc biến MSG.

