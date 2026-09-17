# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal_hold ĐÃ GỠ 2026-09-16 (user duyệt RESUME) — quay lại logic bình thường từ plan
  kế tiếp, không còn escalate riêng.

## 🚨 CẦN XỬ LÝ NGAY đầu phiên 09-17
1. **Rút "trứng vàng" (egg) trước 09:00 ICT 09-17** — VPI/BAL BUY order đầu tiên (SpaceX+ZaloPay)
   funded_via cash+egg; gate P0 (`check_plan_funding()`) sẽ tự HOLD nếu egg chưa rút kịp giờ mở
   phiên. Đây là thiết kế đúng (JIT unpark L2 cộng egg, user duyệt 2026-08-19, `956d8ec5`) đang
   chạy lần đầu trên đơn hàng live thật — không phải bug.
2. **Bus-question TV1 (`zalopay-tv1-200cp-sized-by-dgc-dividend-receivable-0914`) CÒN HỞ 3 NGÀY
   LIÊN TIẾP** (09-14→09-15→09-16, không ai xử lý) — Wags đóng sai `decided_by:user`, arch-review
   NEEDS_CHANGES 2 vòng. Đọc `mike_json.py has-event-prefix` cho topic gốc, tự đóng đúng cách
   (user chỉ duyệt plan, KHÔNG chọn giữa A/B/C). "Phương án C" (active_nav cộng nhầm dividend
   excluded_tickers) tách thành câu hỏi riêng owner_hint Mike/Taylor.
3. **Escalation MỞ, cần trả lời**: `retro-pattern-recurring-action-item-not-executed-2days`
   (pattern tái diễn 2 retro liên tiếp — action item retro không có cơ chế ép thực thi hôm sau).
   Đề xuất: mọi mục "CÒN HỞ" trong bảng sự cố retro tự động kèm 1 bus `question` cùng lúc ghi
   entry, đi qua `ops_health_check.sh` §5 (câu hỏi treo >48h) thay vì chỉ nằm trong file .md tĩnh.
4. **FiinPro/OShares harvest**: kiểm tiến độ thật (lúc dừng 09-15 16:3x: 4/59 lô oshares (40/585
   mã), 0/15 fx). 2 bug vá TRONG PHIÊN 09-15 (lọc `tool_use_id`, cooldown hourly/daily) KHÔNG có
   selfcheck/commit xác nhận — code chỉ sống trong logic phiên headless, có thể mất nếu không
   port thành file thật.

## Retro 09-16 đã đóng (`321a48f2`) — 1 sự cố còn hở, 1 pattern escalate, phần còn lại sạch
- Sự cố #1 = TV1/phương-án-C (mục 2 ở trên), TÁI DIỄN lần 2 liên tiếp.
- Pattern 1 (mục 3 ở trên) — escalate, cần giải quyết cơ chế cưỡng chế thật.
- Verified by Wags: CONFIRMED, không sai sót.

## Còn mở không khẩn
- `job_cancel_guard` nhánh systemd luôn đỏ dưới cron (theo dõi, không escalate).
- `append_event.sh` JSON cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (theo dõi qua retro).

- [2026-09-17T15:08:59Z] 17/09 22:1x: User xác nhận bq_admin chủ đích mở rộng cổ phiếu quỹ vào corp_action (2 dòng VRE/SRF chỉ là pilot) + 2 cột mới (source_news_id/first_disclosure_datetime) dùng được cho announcement-day dù chưa hoàn hảo. Đo nhanh: treasury_news có 568 dòng buy_done/sell_done xác nhận trên 303 mã (không chỉ VRE/SRF), KHÔNG khớp corp_action hiện có. first_disclosure_datetime mẫu DIV 14/17 dòng, lead 11,9 ngày trước exright, 0 sau ex-date. Dispatch Taylor_20260917_150848 (2 nhánh song song, KHÔNG merge/KHÔNG ghi BQ): (A) đo quy mô ảnh hưởng 568 dòng + thiết kế cơ chế nạp có hệ thống (bảng riêng hay trộn vào corp_action? one-time hay recurring?) + relative-delta absorption mới trong oshares_live.py (khác AIS anchor tuyệt đối, thiếu shares_total_after) — reopen quyết định KHÔNG WIRE 09-08 trên phạm vi rộng hơn; (B) đánh giá first_disclosure_datetime có đủ unblock sprint cash_dividend_announcement_premium_20260904 (BLOCKED trước đây) không — chỉ đánh giá khả thi, chưa chạy lại full.
