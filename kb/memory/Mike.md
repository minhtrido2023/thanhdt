# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-15T06:40Z (chờ verify GDKHQ + dispatch Winston data trap)

## GDKHQ D1-D3 — CODE XONG, TỰ VERIFY OK, ĐANG CHỜ quant-skeptic
- Job Taylor_20260815_054822 XONG. Commit e39aafb + a3dc7aff. Tự verify: selfcheck PASS thật
  (2 ca chứng minh ngược từ artifact gốc), 0 plan thật bị chạm.
- **ĐANG CHỜ**: verify_finding.sh (topic "GDKHQ code hoa D1-D3 XONG"), pid 3290499, chạy từ
  06:33. Khi CONFIRMED → hỏi user duyệt lần cuối trước khi DollarBill dùng cho plan thật.

## Winston data trap ticker.Price GDKHQ — ĐÃ DISPATCH
- Job Winston_20260815_064023 (opus/medium, timeout 1800s): xác nhận lại ca VHM 08-06 (lệch hệ
  số 2,0) bằng BQ thật, quét rộng tần suất bất thường, xác định nguyên nhân, bổ sung
  kb/data_registry/price-volume/.
- ĐANG CHỜ job này.

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

