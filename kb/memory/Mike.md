# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary.

## Chờ user quyết — 2 câu hỏi mới (từ Wags 01:51 08-28)
1. **BAF BQ retro-update** (bus: Wags/baf-universe-pit-quality-retro-update-needs-user-approval): UPDATE 1119 dòng lịch sử BAF → BANNED trong tav2_mike.universe_pit_quality. Urgency=THẤP (BAF không có trong trade plan, bị chặn bởi FLOOR_FAIL+rating_8l=4 độc lập). Options A=chạy DML / B=ghi nhận known caveat / C=khác.
2. **capit-lever selfcheck 2 FAIL còn lại** (bus: Wags/capit-lever-selfcheck-2-remaining-fail-permission-blocked): L2/L3 bị chặn permission classifier; Taylor đề xuất patch cụ thể. Urgency=THẤP-TRUNG BÌNH.

## KHẨN — security leak CHƯA đóng hẳn (>3 ngày, treo)
- Số tài khoản DNSE THẬT lộ public GitHub minhtrido2023/thanhdt. Fix code đã push (commit c1303a96, 3d358b14) — bus question `security-leak-2026-08-24-remaining-repo-visibility-and-sudo` vẫn CHƯA có answer.
- 2 hạng mục cần user quyết: (1) repo private/rewrite-history, (2) thu hồi sudo hainguyen/hungle/namiq.
- Đừng mở question thứ 2 trùng — nhắc lại đúng topic cũ.

## Selfcheck status (sau batch fix đêm 08-28 01:51)
- dc_book_waterfall: ✅ FIXED (67 PASS / 0 FAIL)
- lag_forensic_filter: ✅ FIXED (33 PASS / 0 FAIL) — BAF added to BANNED code
- universe_pit_quality: ✅ FIXED (PASS, gap 08-24 backfilled)
- phs_flash_api: ✅ PASS (verified 09:00)
- capit_lever: ⚠️ PARTIAL — 2 FAIL còn lại (L2/L3, permission blocked)
- now_injection_selfcheck: ⚠️ FAIL — checking new sessions, likely false-positive (sessions fresh, no [now:] yet)

## wakeup_audit.py buffer-race
- time_claim_audit.py buffer-race CHƯA SỬA (bug gốc còn trong code, sẽ tái diễn lần tới có mismatch thật)

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

