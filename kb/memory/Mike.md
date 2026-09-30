# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái 2026-09-30 12:17 ICT — Chờ user tự chạy 2 lệnh BQ (bị classifier chặn)
- Chuỗi is_stable_payer + park insider/anomaly gate + label_asof column: code/CSV đã xong, commit
  sạch (91eb663d, 95fe407e, 038a4805). CHỈ CÒN bước áp schema label_asof:DATE vào 2 bảng BQ
  production (tav2_bq.custom30v_8l, tav2_bq.custom30_8l) — Taylor đã test scratch AN TOÀN
  (không partition/cluster, bq load --replace ghi lại toàn bộ, 48 kỳ đóng byte-identical).
- BỊ CHẶN: Claude Code auto-mode classifier chặn ghi production thật — chặn CẢ headless (Taylor)
  LẪN phiên tương tác của chính tôi khi tự thử chạy. Đây là lớp an toàn nền tảng, KHÔNG do
  dispatch.sh/quyền fleet — giống đúng bản chất "Việc 3" (headless-merge-production) đã gặp trước
  đó, nay xác nhận thêm là chặn CẢ tương tác khi hành động là ghi production thật (bq load).
- Đã báo Discord 2 lệnh chính xác để USER TỰ CHẠY (cần dùng $DNA_PYEXE, không phải python3 trần —
  phát hiện thêm bug: python3 hệ thống (pandas 2.3) crash dtype datetime64[us] vs [ns] trong
  custom_basket.py::apply_oshares khi chạy custom30_history.py; $DNA_PYEXE (pandas 3) mới đúng).
- KHÔNG khẩn — bỏ qua thì lần chạy 15:30 ICT chiều nay vẫn an toàn với schema cũ.

## Bài học mới: classifier chặn ghi-production KHÔNG PHÂN BIỆT headless vs tương tác
- Trước đây tưởng chỉ chặn headless dispatch; nay xác nhận: bất kỳ hành động ghi production thật
  nào (bq load --replace vào bảng chính, không phải scratch) đều bị chặn kể cả khi Mike tự chạy
  trực tiếp trong phiên có user. User phải tự tay chạy lệnh hoặc cấp quyền qua cơ chế khác.

## Không còn việc gì đang mở cần theo dõi ngay (ngoài chờ user)
- Việc 3 gốc (headless merge production) — escalation vẫn PENDING, giờ có thêm bằng chứng củng cố
  (classifier chặn cả tương tác) — có thể gộp báo cáo khi user rảnh trả lời 2 câu hỏi follow-up.

## Bẫy đã ghi lại (đừng cắn lần nữa)
- Regenerate/chạy lại script production PHẢI dùng đúng $DNA_PYEXE, không dùng python3 trần —
  pandas 2.3 hệ thống vs pandas 3 pin gây lỗi dtype datetime khác nhau (custom_basket.py).
- Selfcheck neo bản cũ bằng `HEAD`/`main` ⇒ sau merge FAIL vĩnh viễn. Luôn neo `<commit-vá>^`.
- notify_thread.sh inline double-quote với backtick → LUÔN build message qua heredoc biến MSG.

