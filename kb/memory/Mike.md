# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-15T08:29Z (bq_admin CONFIRMED H2+H4a, Winston chốt registry+bus, chờ user)

## GDKHQ D1-D3 — CONFIRMED (high), VẪN ĐANG CHỜ user chọn hướng (đã hỏi nhiều lần, KHÔNG nhắc thêm)
- (a) duyệt dùng thật ngay, (b) dry-run trace 08-17 trước. Chờ tự nhiên, không spam nhắc nữa.

## bq-admin ticker.Price self-heal — bq_admin CONFIRMED bằng code, Winston đang chốt lại
- bq_admin xác nhận ĐÚNG cả H2 (anchor_event chỉ xét 1 ngày, gate ở 1 dòng cụ thể, lỗi giữa
  cửa sổ bị bỏ qua vĩnh viễn) và H4a (fill-forward T-1 khi null là chủ đích, có test, nhưng
  KHÔNG log — giải thích 26/42 dòng lỗi). Q3 (backfill) vẫn chưa rõ.
- Đã dispatch Winston (job Winston_20260815_082902, opus/medium, timeout 1200s): cập nhật
  registry từ "giả thuyết" → "CONFIRMED", tự quyết đóng bus question theo skill
  bus-question-closure (không hỏi lại Mike).
- ĐANG CHỜ job này. Không khẩn, 0đ thiệt hại. Việc treo cũ: lag_entry_anchor.py:105 chưa vá.

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

