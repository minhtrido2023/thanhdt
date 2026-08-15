# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-15T08:33Z (bq_admin mạch ĐÃ ĐÓNG HẲN, chỉ còn chờ GDKHQ D1-D3)

## GDKHQ D1-D3 — CONFIRMED (high), VẪN ĐANG CHỜ user chọn hướng — VIỆC MỞ DUY NHẤT còn lại
- (a) duyệt dùng thật ngay, (b) dry-run trace 08-17 (BID/MBS/SSI/VIX) trước. Đã hỏi nhiều lần,
  KHÔNG nhắc thêm — chờ tự nhiên.

## bq-admin ticker.Price self-heal — ĐÃ ĐÓNG HẲN (2026-08-15T08:33Z)
- Registry `kb/data_registry/price-volume/ticker_price_stale_on_exdate.md` final (commit
  28c098fb): H2 (gate dòng 209 chặn self-heal) + H4a (fill-forward T-1 không log) = CONFIRMED
  bởi bq_admin bằng code cụ thể. "Cửa sổ tự sửa 15 phiên" đánh dấu CHỈ TRÊN GIẤY.
- Cả 2 bus question `bq-admin-*` đã đóng qua close_bus_question.py, tự verify audit = 0 pending.
  Q3 (backfill) hạ xuống ghi chú "nice to have" — lý do hợp lý: backfill không giải quyết gốc
  vì cơ chế sinh lỗi + self-heal-không-fire vẫn còn nguyên.
- Việc treo (không khẩn, 0đ, thuộc Taylor/DollarBill): lag_entry_anchor.py:105 đọc thẳng
  ticker.Price làm trần ràng buộc — chưa vá.

## TV1 — Rule A (bản fix UPCOM) đang LIVE, an toàn
- Verify sống OK, selfcheck PASS. Theo dõi phiên tiếp theo.

## Việc còn hở từ trước (chưa xử lý, không khẩn)
1. ops_health_check.sh::_rollup_resolved() substring-match — NEEDS_CHANGES 08-14, CHƯA vá.
2. Selfcheck-masking E5 capit_lever — chưa xác nhận đã vá hay chỉ mới ĐO.
3. plan-dd-check-string fix (commit 9a9dbb1) — chờ xác nhận phiên LIVE 08-17.
4. MIKE.md 44,2KB vượt 40KB — cần tách OKF.
5. EOD daily report chưa bao giờ gửi email — hỏi user có wire không.

## Bối cảnh còn hiệu lực
- dispatch-prompt-heredoc skill — dùng cho MỌI prompt dispatch có backtick/code snippet.
- CASH_VENDOR gate: giữ ĐÓNG (user duyệt 08-15), mở lại chỉ khi >=1 sự kiện ISS/hỗn hợp VÀ qua
  2026-09-13. commit dce25180.

