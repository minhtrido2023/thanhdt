# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái 2026-10-01 00:37 ICT — Retro 09-30 xong, chờ user 2 việc
- Daily retro 2026-09-30 đã finalize: 4 sự cố, Wags CONFIRMED (0 gap). Entry:
  kb/incidents/retro/retro-2026-09-30.md. Pattern bus-closure channel gap (Pattern B, escalate
  09-29) ĐÓNG hôm nay bằng cơ chế cơ học (question_commit_hint.py wire bắt buộc vào MỌI dispatch
  qua dispatch.sh, cả --bg và foreground) — theo dõi 7 ngày tới (~10-06/10-07) xem có tái diễn
  không trước khi coi là đóng dứt điểm.

## Đang chờ USER (không khẩn, không chặn vận hành)
- Taylor/can-user-chay-bq-load-label-asof-production (mở 09-30 05:15Z): cần user tự chạy 2 lệnh
  `$DNA_PYEXE bq load --replace` (schema label_asof:DATE vào tav2_bq.custom30v_8l/custom30_8l) —
  classifier chặn CẢ headless lẫn tương tác của Mike. Trong cửa sổ ack pattern
  classifier-blocks-headless-agent-production-write (hết hạn ~10-06). Không dùng python3 trần —
  phải $DNA_PYEXE (pandas 3).
- Đề xuất Winston: ghi known-issue VNM exright_date lệch 1 phiên vào data registry — chưa làm,
  không khẩn (close_repair.py band-guard đã chặn đúng, 0 tác động thực tế).

## Backlog cần ai đó chủ động triage (không phải sự cố mới)
- 9 topic `selfcheck-red: *` pending trên bus_question_audit.py, cũ nhất từ 09-25. Nếu tiếp tục
  phình mà không ai triage → có thể thành pattern riêng ở retro tới.

## Bẫy đã ghi lại (đừng cắn lần nữa)
- Regenerate/chạy lại script production PHẢI dùng đúng $DNA_PYEXE, không dùng python3 trần —
  pandas 2.3 hệ thống vs pandas 3 pin gây lỗi dtype datetime khác nhau (custom_basket.py).
- Selfcheck neo bản cũ bằng `HEAD`/`main` ⇒ sau merge FAIL vĩnh viễn. Luôn neo `<commit-vá>^`.
- notify_thread.sh inline double-quote với backtick → LUÔN build message qua heredoc biến MSG.
- Regen/pin lệnh dài nhiều tham số (basket weight scheme, v.v.) → LUÔN đối chiếu META params với
  ledger đã pin TRƯỚC khi ghi đè canonical (case 09-30 #3: quên BASKET_WT=namecap).

