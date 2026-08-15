# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-15T05:48Z (GDKHQ D1-D3 đang code hoá)

## GDKHQ D1-D3 — ĐANG CODE HOÁ (job Taylor_20260815_054822, opus/high, timeout 3600s)
- User duyệt code hoá ngay cuối tuần này (2026-08-15). Thiết kế đã chốt ở
  agents/Taylor/research/exdate_order_pipeline_20260815/README.md §8 — job này HIỆN THỰC HOÁ,
  không thiết kế lại.
- Yêu cầu: G4 (bất biến đồng-hệ, mọi lô cùng mã 1 lần đọc phải cùng marketPrice) + G5 (đối soát
  chéo corporate_action) trong price_frame.py; cổng D2 ở tầng sinh plan (ref_price/qty/trần bắt
  buộc từ resolve_reference() khi mã GDKHQ, không thì bỏ mã khỏi plan); D3 đóng 3 chỗ
  (strategies.py fallback, merge_park_orders.py 345-354, paper_main_probe_plan.py).
- BẮT BUỘC 2 ca chứng minh ngược THẬT: dựng lại bản đọc BID 19:10:23 (2 lô khác hệ) → G4 phải
  chặn; dựng lại plan_main_2026-08-11 (ref 24.250 sai) → gate phải bắt.
- Ranh giới: KHÔNG dời cron, KHÔNG đụng backtest, KHÔNG mở rộng corp_actions.json.
- Code+selfcheck xong DỪNG — KHÔNG tự áp cho plan thật (kể cả 08-17). Chờ quant-skeptic +
  user duyệt lần cuối.
- Bus: gdkhq-D1-D3-code-approved (decided_by=user).
- ĐANG CHỜ job này.

## TV1 — Rule A (bản fix UPCOM) đang LIVE, an toàn
- Verify sống OK, selfcheck PASS (từ ~04:5x). Theo dõi phiên tiếp theo.

## Việc còn hở từ trước (chưa xử lý, không khẩn)
1. ops_health_check.sh::_rollup_resolved() substring-match — NEEDS_CHANGES 08-14, CHƯA vá.
2. Selfcheck-masking E5 capit_lever — chưa xác nhận đã vá hay chỉ mới ĐO.
3. plan-dd-check-string fix (commit 9a9dbb1) — chờ xác nhận phiên LIVE 08-17.
4. MIKE.md 44,2KB vượt 40KB — cần tách OKF.
5. EOD daily report chưa bao giờ gửi email — hỏi user có wire không.

## Bối cảnh còn hiệu lực
- dispatch-prompt-heredoc skill — dùng cho MỌI prompt dispatch có backtick/code snippet.

