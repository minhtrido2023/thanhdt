# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
1. **RCA plan pipeline 2026-08-20 — XONG cả 3 lỗi.** Bài học quan trọng nhất: tôi đã over-engineer
   lỗi #1 (giao thức batch-id 728 dòng/10 call site/6 vòng arch-review/>3h, KHÔNG xong) trong khi
   lời giải đúng là debounce 30 dòng ở wake_thread.sh. User phải dừng tôi lại. Nguyên nhân: tôi
   xây tầng bảo đảm THỨ BA cho thứ reconciler (cron */5, dựng sáng cùng ngày) đã bảo đảm rồi.
   ⇒ LUẬT TỰ ĐẶT: trước khi thiết kế cơ chế điều phối mới, hỏi "lưới an toàn hiện có đã phủ ca
   xấu nhất chưa?" Nếu rồi thì chỉ cần chốt đơn giản nhất ở cửa hẹp nhất, KHÔNG dựng giao thức.
   Dấu hiệu cảnh báo sớm: >2 vòng arch-review cho 1 fix = thiết kế sai, không phải fix chưa đủ.
2. **plan-dd-check-string fix** (commit 9a9dbb1) — cần ngày có LAG/BAL entry để verify.
3. **Order-book Pha 0 telemetry** (commit d6346efd) — N=39 obs/3 phiên, tích lũy bình thường.

## Trạng thái 3 lỗi RCA (commit 1cf275ca + cd2f66f5 + 7cb65314 + WC 3955e59b)
- Lỗi #1 (2 phiên song song): debounce per-thread trong wake_thread.sh, WAKE_DEBOUNCE_S=180s,
  fail-open, reconciler là lưới (bỏ wake ⇒ trễ ≤5' chứ không mất). selfcheck 10/10 PASS.
  Batch-id đã REVERT sạch (-1453 dòng). VERIFY THẬT: 19:00 ICT 08-21 khi bq_freshness_check
  fan-out 2 account — kỳ vọng log wake_thread.log có 1 SUCCESS + 1 DEBOUNCED, chỉ 1 phiên Mike.
- Lỗi #2 (egg bất đối xứng): EGG_NOTE phát vô điều kiện mọi account trong bq_freshness_check.sh.
- Lỗi #3 (mua VPI dù đã chốt): signal_holds 2 tầng (prompt + gate send_plan_report + bot_execute).
  holds LIVE: book=BAL buy + ticker=VPI buy, cả 2 until 2026-09-16. selfcheck 23/23 PASS.
- plan_ZaloPay_2026-08-21: 0 orders, VPI trong deferred, approved_by=None.

## Bối cảnh còn hiệu lực
- GDKHQ D1-D3 LIVE từ 08-17. yield_floor Option C WIRED, review 2027-02-10.
- TV1 Rule A LIVE từ 08-15. CASH_VENDOR gate: ĐÓNG.
- P2 expvol_pacing: shadow log-only trên LIVE từ 08-17, review 2026-09-15.
- BAL signal shadow-track (case VPI): review 2026-09-16.
- OKF split mandate: file vượt 40KB → tự split.
- CHƯA LÀM (mức thấp, không gấp): F2.3 thêm dòng prompt-sinh-plan vào bảng §25
  coding_guidelines; F3.3 checker cảnh báo khi signal_hold hết hạn 09-16.
- P3 ccdb session-dedupe: KHÔNG CẦN NỮA — debounce đã giải quyết ở tầng gửi, khỏi restart ccdb.

## Việc còn treo từ retro 08-19
- 3 selfcheck đỏ (nav_cum_dividend, corp_action_daily, lag_forensic_filter) — cần chủ sở hữu xác nhận
- bot_prepare_plan.py bug2 (plan phantom) — cần Taylor điều tra hoặc xác nhận dead/unused

