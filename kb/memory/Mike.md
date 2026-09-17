# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal_hold ĐÃ GỠ 2026-09-16 — logic bình thường, không còn escalate riêng.

## Việc đang mở / cần theo dõi
1. **`coord-2026-09-17` (Wags wags-fix-not-confirmed round 2, mở 09-17 05:48:17Z) CÒN HỞ ~19h,
   chưa có answer.** required_changes round 2 chưa xác nhận đã làm: urgency câu hỏi
   `zalopay-active-nav-excluded-ticker-dividend-receivable-option-c` (normal→cần nâng),
   suppress_days=8 (cần rút ngắn), 2 câu hỏi tồn đọng coord-2026-09-14. Rủi ro thật: mọi plan
   ZaloPay 18-25/09 có lệnh mua có thể vẫn bị phồng size ~15% nếu option-c chưa xử lý.
2. **Pattern "arch-review NEEDS_CHANGES vòng 2 ⇒ auto-escalate" (đề xuất từ retro-09-14) vẫn CHƯA
   wire thành code** — tái diễn y hệt ở coord-2026-09-17. Cần Mike/user quyết có build gate thật
   trong `wags_autofix.sh` không (retro-2026-09-17.md có đề xuất cụ thể).
3. **FiinPro/OShares harvest**: dừng 09-15 ở 4/59 lô oshares, 0/15 fx — 2 bug vá (tool_use_id
   filter, cooldown hourly/daily) CHƯA có selfcheck/commit xác nhận, chỉ sống trong logic phiên
   headless cũ — cần port thành code thật hoặc coi là mất.
4. Treasury buyback/corp_action mở rộng (dispatch Taylor_20260917_150848, job đã xong 2 nhánh):
   ĐANG CHỜ USER QUYẾT 5 việc — (1) bảng riêng hay trộn corp_action; (2) one-time hay recurring;
   (3) sự kiện thiếu size giữ+cờ hay trả rỗng; (4) xoá hay giữ 2 dòng MANUAL_FILL VRE/SRF; (5) mở
   sprint cổ tức mô tả không. Quyết định KHÔNG WIRE 09-08 (relative-delta absorption) vẫn đứng —
   design mới của Taylor (persistent quarterly-snapshot adjust, bảng riêng) khác hẳn đề xuất ban
   đầu của Mike (đã bị bác vì sai bản chất treasury buyback).
5. Code-quality Tầng 3 auto-dispatch ĐÃ WIRE vào `code_quality_weekly.sh` bước 7 hôm nay
   (arch-reviewer CONFIRMED sau 5 vòng) — chạy lần đầu tự động Chủ Nhật 2026-09-20 03:00 UTC.
   Backlog quan sát (manifest T0 107 file) — CHƯA quyết có cần thu hẹp gate.

## Retro 09-17 đã đóng (`6fcb489d`) — 2 sự cố, Wags CONFIRMED
- Funding-gate double-count biến thể 4 (HOÀN CHỈNH, d6568e13). Wags NEEDS_CHANGES round 2 CÒN HỞ
  (mục 1 ở trên). Tin tốt: TV1 (retro-09-16) đã đóng đúng <15h — prevention hoạt động.
- Đã đóng bù `Winston/ops-autofix-unresolved: run-bot-fail-ZaloPay-2026-09-17` (root cause đã fix,
  chỉ sót không đóng theo).

## Còn mở không khẩn
- `job_cancel_guard` nhánh systemd luôn đỏ dưới cron (theo dõi, không escalate).
- `append_event.sh` JSON cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (theo dõi qua retro).

