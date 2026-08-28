# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary.

## Đang chờ / mở nhỏ
1. **capit-lever selfcheck 2 FAIL còn lại** (bus: Wags/capit-lever-selfcheck-2-remaining-fail-permission-blocked): L2/L3 bị chặn permission classifier; Taylor đề xuất patch cụ thể. Urgency=THẤP-TRUNG BÌNH. User chưa cho ý kiến.
2. **Security leak VM**: user báo tạo máy ảo riêng trong server thay cho repo private/sudo revoke. Bus đóng DEFERRED. Theo dõi tiến độ VM khi có cập nhật.

## Selfcheck status (sau batch fix đêm 08-28 01:51)
- dc_book_waterfall, lag_forensic_filter, universe_pit_quality, phs_flash_api: ✅ PASS
- capit_lever: ⚠️ 2 FAIL còn lại (L2/L3, permission blocked)
- now_injection_selfcheck: ⚠️ likely false-positive (new sessions fresh)

## wakeup_audit / buffer-race
- time_claim_audit.py buffer-race CHƯA SỬA (bug gốc còn trong code)

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

## Quyết định đã chốt hôm nay (08-28)
- BAF BQ retro-update: Option B — ghi nhận known caveat, không sửa lịch sử (decided_by: user)
- Security leak: tạo VM riêng thay vì repo private/sudo revoke (decided_by: user)

