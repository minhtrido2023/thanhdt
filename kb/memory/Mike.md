# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
1. **RCA plan pipeline 08-20 + retro 08-20 — CẢ HAI ĐÃ XONG (2026-08-20 cuối ngày).**
   3 lỗi RCA đã đóng (xem dưới). Retro 08-20 đã ghi `kb/incidents/retro/retro-2026-08-20.md`,
   verified by Wags (2 gap tìm thấy, cả 2 đã sửa). 5 sự cố, Pattern C mới (xem dưới) là bài học
   quan trọng nhất trong ngày.
2. **LUẬT TỰ ĐẶT (Pattern C, 2026-08-20):** trước khi thiết kế cơ chế điều phối liên-agent mới,
   hỏi "lưới an toàn hiện có đã phủ ca xấu nhất chưa?" — nếu rồi thì chỉ chốt đơn giản nhất ở
   cửa hẹp nhất, KHÔNG dựng giao thức song song. **>2 vòng arch-review liên tiếp cho 1 fix =
   tín hiệu thiết kế sai**, dừng lại thay vì tiếp tục vá. (Vụ batch-id 728 dòng/6 vòng review/
   >3h bị revert, đúng lẽ ra chỉ cần debounce 30 dòng.)
3. **plan-dd-check-string fix** (commit 9a9dbb1) — cần ngày có LAG/BAL entry để verify.
4. **Order-book Pha 0 telemetry** (commit d6346efd) — N=39 obs/3 phiên, tích lũy bình thường.

## Trạng thái 3 lỗi RCA 08-20 (commit 1cf275ca + cd2f66f5 + 7cb65314 + WC 3955e59b)
- Lỗi #1 (2 phiên song song): debounce per-thread trong wake_thread.sh, WAKE_DEBOUNCE_S=180s,
  fail-open, reconciler là lưới (bỏ wake ⇒ trễ ≤5' chứ không mất). selfcheck 10/10 PASS.
  Batch-id đã REVERT sạch (-1453 dòng). **CHƯA có entry kb/incidents/ riêng cho vụ batch-id —
  cần tạo `kb/incidents/2026-08/2026-08-20-batch-id-overengineer-reverted.md`.**
  VERIFY THẬT còn treo: 19:00 ICT 08-21 khi bq_freshness_check fan-out 2 account — kỳ vọng log
  wake_thread.log có 1 SUCCESS + 1 DEBOUNCED, chỉ 1 phiên Mike.
- Lỗi #2 (egg bất đối xứng): EGG_NOTE phát vô điều kiện mọi account trong bq_freshness_check.sh.
- Lỗi #3 (mua VPI dù đã chốt): signal_holds 2 tầng (prompt + gate send_plan_report + bot_execute).
  holds LIVE: book=BAL buy + ticker=VPI buy, cả 2 until 2026-09-16. selfcheck 23/23 PASS.
- plan_ZaloPay_2026-08-21: 0 orders, VPI trong deferred, approved_by=None.

## Việc còn treo (từ retro 08-20)
- Tạo entry kb/incidents/ cho batch-id revert (xem trên).
- compute_park_trim.py: thêm retry/guard cho cửa sổ EOD-closure DNSE (~19:06 ICT) — hiện đọc
  broker 1 lần, không phân biệt "tạm ngừng" vs "0 thật" (case thật 08-20, tự phục hồi sau chạy
  lại tay, chưa có guard code).
- 6 file selfcheck có cleanup gap glob (orderbook_shadow rác đĩa) — rủi ro thấp, chưa vá.
- Theo dõi Pattern C ngày mai — có tái diễn "vòng arch-review lặp không dừng" không.
- 3 selfcheck đỏ từ retro 08-19 (nav_cum_dividend, corp_action_daily, lag_forensic_filter) —
  ĐÃ ĐÓNG trong ngày 08-20 (commit 129b063a + af1451d4), không còn treo.

## Bối cảnh còn hiệu lực
- GDKHQ D1-D3 LIVE từ 08-17. yield_floor Option C WIRED, review 2027-02-10.
- TV1 Rule A LIVE từ 08-15. CASH_VENDOR gate: ĐÓNG.
- P2 expvol_pacing: shadow log-only trên LIVE từ 08-17, review 2026-09-15.
- BAL signal shadow-track (case VPI): review 2026-09-16.
- OKF split mandate: file vượt 40KB → tự split.
- CHƯA LÀM (mức thấp, không gấp): F2.3 thêm dòng prompt-sinh-plan vào bảng §25
  coding_guidelines; F3.3 checker cảnh báo khi signal_hold hết hạn 09-16.
- P3 ccdb session-dedupe: KHÔNG CẦN NỮA — debounce đã giải quyết ở tầng gửi.

- [2026-08-21T02:06:38Z] 2026-08-21 09:xx: user yêu cầu đơn giản hoá lớp wake-up. Root cause 'No conversation found' = session CODEX (UUIDv7) kẹt trong thread Trading Daily sau đổi backend global→claude 08-20; scheduler._run_task ccdb không có guard session_is_resumable. Đề xuất 'kết quả là dữ liệu, không phải wake': agents/Mike/research/wakeup_simplification_proposal_20260821.md — CHỜ USER QUYẾT, chưa sửa gì. Việc ngay: user gõ /backend claude ở Trading Daily.
