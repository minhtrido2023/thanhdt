# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- **VPI/BAL signal HOLD hết hạn HÔM NAY 2026-09-16** — review đến hẹn, cần quyết có gỡ HOLD hay
  gia hạn. Chưa xử lý.

## 🚨 CẦN XỬ LÝ NGAY đầu phiên 09-16
1. **VPI/BAL review đến hẹn 09-16** — quyết định gỡ HOLD hay gia hạn, cập nhật `kb/current_ops.md`.
2. **Bus-question TV1 (`zalopay-tv1-200cp-sized-by-dgc-dividend-receivable-0914`) CÒN HỞ 2 NGÀY
   LIÊN TIẾP** (09-14 → 09-15, không ai xử lý) — Wags đóng sai `decided_by:user`, arch-review
   NEEDS_CHANGES 2 vòng. Đọc `mike_json.py has-event-prefix` cho topic gốc, tự đóng đúng cách
   (không giao Wags vòng 3 không gate). "Phương án C" (active_nav cộng nhầm dividend
   excluded_tickers) cũng chưa ai quyết.
3. **FiinPro/OShares harvest**: kiểm tiến độ thật (lúc dừng 09-15 16:3x: 4/59 lô oshares (40/585
   mã), 0/15 fx, cooldown daily-limit đặt tới 00:20 ICT 09-16 — nên đã hết hạn, có thể chạy lại).
   2 bug vá TRONG PHIÊN (lọc `tool_use_id`, cooldown hourly/daily) KHÔNG có selfcheck/commit xác
   nhận — code chỉ sống trong logic phiên headless, có thể mất nếu không port thành file thật.

## Retro 09-15 đã đóng (`ab6af586`) — 5 sự cố, 2 pattern:
- Sự cố #1/#2: tiếp nối ingest BQ 09-14, tự phục hồi trước giờ bot — HOÀN CHỈNH, đóng vòng.
- Sự cố #3 (Pattern 1 MỚI, theo dõi): FiinPro/OShares connector 2 bug thật (false rate-limit từ
  `tool_results()` quét nhầm Bash/Read; cooldown sai loại hourly/daily) — đã vá TRONG PHIÊN,
  KHÔNG có selfcheck/commit. Nếu tái diễn ở script khác đọc `tool_results()` → áp bài học ngay.
- Sự cố #4 (Pattern 2 MỚI): action item retro (TV1) không được thực thi hôm sau — GAP QUY TRÌNH,
  đề xuất chưa làm: mở kèm bus `question` tự động cho mọi mục "CÒN HỞ" trong retro để đi qua
  `ops_health_check.sh` §5 (câu hỏi treo >48h) thay vì chỉ nằm trong file draft tĩnh.
- Sự cố #5: Wags verify độc lập bắt draft ban đầu bỏ sót KHP double-count fix + canary feed
  (đã land 01:27-01:30Z, HOÀN CHỈNH) — đã bổ sung vào entry.

## Còn mở không khẩn
- `job_cancel_guard` nhánh systemd luôn đỏ dưới cron (theo dõi, không escalate).
- `append_event.sh` JSON cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (theo dõi qua retro).
- Canary feed corp-action: cron `5 0 * * 1-5` đã cài (mike `7296f332`/`d00d0a8d`), việc non-blocking
  còn lại: SC2 basename, canary check so toàn bộ 37 cột, notify rc=3 chỉ log, WARN không de-dup.
