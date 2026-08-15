# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-15T07:30Z (bq_admin trả lời + mâu thuẫn phát hiện, chờ Winston + user)

## GDKHQ D1-D3 — CONFIRMED (high), VẪN ĐANG CHỜ user chọn hướng
- Đã hỏi 2 lần (06:50, nhắc lại 07:30): (a) duyệt dùng thật ngay, (b) dry-run trace 08-17 trước.
  CHƯA có phản hồi.

## bq-admin ticker.Price mechanism — bq_admin trả lời 2/3, PHÁT HIỆN MÂU THUẪN, đang điều tra tiếp
- bq_admin giải thích: Price = reconcile cafef(unadjusted×1000) + VCI(adjusted, ghi đè phiên mới
  nhất). Cửa sổ tự sửa 15 phiên: lệch >1% (anchor_event) + cafef "settled" (SETTLE_RUN=4) →
  ghi đè lại. Ngoài cửa sổ: chốt vĩnh viễn. Q3 (backfill 42 dòng) CHƯA trả lời.
- **Mike tự query BQ NGAY 07:29: VHM 08-06 Price VẪN 153.000 (sai)** — 7 phiên đã trôi qua, vẫn
  trong cửa sổ 15 phiên, lệch 98,4% vượt xa ngưỡng 1% — LẼ RA đã tự sửa theo mô tả nhưng CHƯA.
  Mâu thuẫn thật, đã ghi bus finding "bq-admin-explained-price-mechanism-self-heal-15session".
- Đã dispatch Winston (job Winston_20260815_072951, opus/medium, timeout 1500s): kiểm 41 dòng
  lỗi khác có tự sửa chưa (cô lập VHM có phải ca đặc biệt), đề xuất giả thuyết vì sao kẹt, soạn
  câu hỏi follow-up sắc để relay bq_admin (kèm hỏi lại Q3), cập nhật registry entry.
- Bus question Winston/bq-admin-ticker-price-exdate-backfill CHƯA đóng (chưa thực sự resolved —
  Q3 chưa trả lời + mâu thuẫn mới) — KHÔNG dùng close_bus_question.py cho tới khi thực sự xong.
- ĐANG CHỜ job này.

## Winston data trap round 1 — XONG (context cũ)
- Registry entry gốc: kb/data_registry/price-volume/ticker_price_stale_on_exdate.md, commit
  6a9c9dff. lag_entry_anchor.py:105 đọc thẳng ticker.Price làm trần — CHƯA vá, 0đ thiệt hại,
  gộp vào lần sửa GDKHQ tiếp theo.

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

