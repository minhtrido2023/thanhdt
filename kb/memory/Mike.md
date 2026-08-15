# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-15T05:04Z (TV1 relit + GDKHQ investigation dispatched)

## TV1 — ĐÃ lật lại Rule A (bản fix), an toàn (2026-08-15)
- User duyệt lật lại sau khi cả 2 finding UPCOM-fix CONFIRMED (high). Đã sửa 2 state file
  (SpaceX+ZaloPay), verify SỐNG bằng resolve_price_band() thật với anchor_basis=
  official_reference_price + anchor_exchange=UPCOM: mode=rule_a, anchor lấy đúng giá tham
  chiếu (khác giá đóng cửa). Selfcheck 37/37 + 33/33 PASS. Bus event
  tv1-rule-a-relit-post-upcom-fix (decided_by=user).
- THEO DÕI phiên tiếp theo: lệnh Rule A đầu tiên chạy thật với anchor đã fix — kiểm journal +
  log injector có in [anchor] đúng sàn/marketId không.

## GDKHQ tổng quát — ĐANG ĐIỀU TRA (job Taylor_20260815_050425, opus/high, ~50 phút)
- User duyệt mở rộng phạm vi: không chỉ Rule A, mà TOÀN BỘ vận hành đặt lệnh khi chạm mã GDKHQ.
- 3 phần: (1) vẽ bản đồ điểm rủi ro + kiểm BQ/DNSE có tự điều chỉnh quyền không, (2) thiết kế
  fix (KHÔNG code ngay, chỉ thiết kế + đo độ lớn), (3) quét lịch sử lệnh thật từ 07-01 xem đã
  từng dính GDKHQ chưa.
- Đã kiểm trước dispatch: KHÔNG có lệnh SSI nào trong plan 08-17 hiện tại → không khẩn cấp tiền
  thật ngay, nhưng cần điều tra kỹ.
- ĐANG CHỜ job này.

## Việc còn hở từ trước (chưa xử lý)
1. ops_health_check.sh::_rollup_resolved() substring-match — NEEDS_CHANGES 08-14, CHƯA vá.
2. Selfcheck-masking E5 capit_lever — chưa xác nhận đã vá hay chỉ mới ĐO.
3. plan-dd-check-string fix (commit 9a9dbb1) — chờ xác nhận phiên LIVE 08-17.
4. MIKE.md 44,2KB vượt 40KB — cần tách OKF.
5. EOD daily report chưa bao giờ gửi email — hỏi user có wire không.

## Bối cảnh còn hiệu lực
- TV1: đừng tự nhắc lại status tĩnh cũ — chỉ nêu khi có thay đổi thật.
- dispatch-prompt-heredoc skill (~/.claude/skills/dispatch-prompt-heredoc/) — dùng heredoc-vào-
  biến cho MỌI prompt dispatch có backtick/code snippet.

