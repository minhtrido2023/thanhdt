# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal_hold ĐÃ GỠ 2026-09-16 — logic bình thường, không còn escalate riêng.

## Việc đang mở / cần theo dõi
1. **`coord-2026-09-17` (Wags round 2, mở 09-17 05:48Z) VẪN CÒN HỞ ~43h (đến retro 09-18).**
   ESCALATED bus question `retro-pattern-recurring-coord-09-17-arch-review-round2-2days`
   (urgency high) — lần thứ 2 liên tiếp qua 2 retro. Chờ Mike/user quyết build gate thật trong
   `wags_autofix.sh` (auto-escalate khi NEEDS_CHANGES vòng 2 liên tiếp cùng topic). Rủi ro cụ thể:
   `zalopay-active-nav-excluded-ticker-dividend-receivable-option-c` chưa xử lý, plan ZaloPay có
   lệnh mua 18-25/09 có thể phồng size ~15%.
2. **FiinPro/OShares harvest**: dừng 09-15 ở 4/59 lô oshares, 0/15 fx — 2 bug vá (tool_use_id
   filter, cooldown hourly/daily) CHƯA có selfcheck/commit xác nhận — cần port thành code thật
   hoặc coi là mất.
3. **Treasury buyback/corp_action mở rộng** (Taylor branch feat/treasury-share-events-table,
   commit 4e7f51d4, 4 file `.proposed` ở kb/data_registry/price-volume/): CHỜ Mike/user duyệt
   chính thức. UNSIZED (413/577) đã chốt GIỮ trong bảng làm bằng chứng, KHÔNG phải input tính
   toán — terminal, không treo. Bảng BQ thật CHƯA tạo (chờ thiết kế consumer/oshares_live hook
   trước, theo khuyến nghị arch-reviewer).
4. Code-quality Tầng 3 auto-dispatch ĐÃ WIRE vào `code_quality_weekly.sh` bước 7 (18/09, sau 2
   vòng arch-review thu hẹp gate, commit chuỗi 90f93d5b→db0c46ea→6fd028a0, cuối 72 file). Chạy
   lần đầu tự động Chủ Nhật 2026-09-20 03:00 UTC — theo dõi kết quả lần chạy đầu.

## Retro 09-18 đã đóng (`f2ad59ec`) — 1 sự cố mới (fixed), 1 carry-over escalated
- ops_health_check 5b heartbeat-shadow (biến thể thứ 5 §28/§29): HOÀN CHỈNH `e5825e11`, không
  escalate thêm (prevention quy trình đủ).
- coord-2026-09-17 round 2: xem mục 1 trên.
- Wags verify: GAPS FOUND minor (đếm finding treasury sai 4→5), đã sửa, không đổi kết luận.

## Còn mở không khẩn
- `job_cancel_guard` nhánh systemd luôn đỏ dưới cron (theo dõi, không escalate).
- `append_event.sh` JSON cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (theo dõi qua retro).

