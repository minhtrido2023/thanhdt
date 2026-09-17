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
- [2026-09-17T15:25:46Z] 17/09 22:2x: Taylor_20260917_150848 XONG cả 2 nhánh (mike 6ade95ec+ae38f4b6), CHƯA merge/CHƯA ghi BQ. Nhánh A: con số 568 ban đầu của Mike SAI (đó là tổng mọi action_type) — đúng là 577 sự kiện/233 mã sau lọc buy_done/sell_done+dedup, 78% (449) không có size. VRE/SRF (2 dòng tay) có shares_delta=NULL trong treasury_news + dấu ngược (buy_done dương, dòng tay âm) — cơ chế đọc treasury_news sẽ KHÔNG tái tạo lại 2 dòng tay. Thiết kế 'relative-delta như ISS' Mike đề xuất SAI VỀ BẢN CHẤT — treasury buyback không giảm AIS (listed), chỉ giảm OShares outstanding, khoản trừ phải PERSISTENT tới khi bán/huỷ chứ không phải 1 lần. Ảnh hưởng thật hôm nay: 0/233 mã neo AIS sai do thiếu treasury (chỉ GDT +1,17% giải thích đúng); 0 mã đang NẮM GIỮ sai; rủi ro tiềm ẩn duy nhất VRE 2,49% nếu có AIS mới trong 90 ngày. Prototype treasury_adjust.py (hermetic 20/20, mutation 18/18) hiệu chỉnh theo số dư quý gần nhất, không cộng dồn lịch sử. Đề xuất bảng RIÊNG không trộn corp_action. Nhánh B: KHÔNG unblock sprint cash-dividend-announcement theo prereg cũ — lỗi CHẤT LƯỢNG dữ liệu (76 ISS sau ex-date, lệch TZ, 34,4% trùng public_date nghi bị ghi đè, 63% link tin xuất bản sau ngày công bố, sửa 58 lần/3 snapshot) chứ không phải thiếu coverage. Chỉ dùng được cho nghiên cứu mô tả. ĐANG CHỜ USER QUYẾT 5 VIỆC: (1) bảng riêng hay trộn corp_action; (2) one-time hay recurring; (3) sự kiện thiếu size giữ+cờ hay trả rỗng; (4) xoá hay giữ 2 dòng MANUAL_FILL; (5) có mở sprint cổ tức dạng mô tả không. Quyết định KHÔNG WIRE 09-08 vẫn đứng.
- [2026-09-17T15:28:47Z] 09-17 22:2x: User chốt đổi code-review Tầng 3 report-only→auto-dispatch ngay. Đã dispatch Wags_20260917_152645 (15 finding mike/bin) + Taylor_20260917_152759 (8 finding brokers.py-non-order + root script) từ báo cáo code_quality_2026-09-13. ESCALATE riêng brokers.py:518 (loan_package_id cross-account) + :559 (NAV duplicate-formula) — chạm logic đặt lệnh/NAV sống, cần user xác nhận trước khi dispatch Taylor sửa. Chưa hỏi user có muốn wire auto-dispatch vào chính code_quality_weekly.sh (cron CN) hay để Mike làm tay mỗi tuần. Đang chờ 2 job qua ScheduleWakeup, sẽ báo topic 1550161414084104282 khi xong.
- [2026-09-17T15:36:20Z] 09-17 22:3x: Taylor_20260917_152759 XONG 8/8 (1 fix mới 41d07368, 7 đã fix trước ở b53d26b4/24df0f76). NEEDS_CHANGES mới lộ: fetch_new_listings.py fail-open + data/new_listings.csv còn liệt nhầm HDG/DIH/VNH — cần giao Winston/Mike riêng, CHƯA làm. Đính chính: brokers.py:518/559 (escalate lên user) hóa ra ĐÃ FIX từ 09-14 (99fd8f6d/e802c08c, aria-K checklist, không liên quan job này) — đã báo lại user, KHÔNG cần họ xác nhận nữa. BÀI HỌC: lần sau trước khi escalate 1 finding từ report cũ,  trên file đó để check đã fix chưa TRƯỚC khi hỏi user. Wags_20260917_152645 (15 finding mike/bin) còn running, đang poll tiếp.
- [2026-09-17T15:36:39Z] 09-17 22:3x correction: dòng ghi trước bị cụt do backtick trong lệnh remember.sh (chính bug dispatch-prompt-heredoc) — bài học đầy đủ: trước khi escalate 1 finding từ report cũ lên user, chạy 'git log --since=<ngày report> -- <file>' trên đúng file/dòng đó để xác nhận CHƯA fix, tránh báo nhầm "còn mở" như vụ brokers.py:518/559 hôm nay (đã fix từ 09-14, không liên quan).
- [2026-09-17T15:59:04Z] 09-17 22:5x: Wags_20260917_152645 XONG — 15/15 đã fix từ 09-13 (job Wags_20260913_034952/050903), giá trị thật của job hôm nay = đóng 2 gap arch-review (136a90d0, 767deb0e) qua commit eee6769b, cả 3 nhóm giờ APPROVE. Đã post kết quả cuối cùng vào topic 1550161414084104282 + ghi 2 luật quy trình vào code-quality-review-plan-20260823.md (grep bus cq-<ngày>-* trước dispatch; git log --since trước khi escalate). Xong việc code-review hôm nay — chờ user quyết có muốn wire auto-dispatch thẳng vào code_quality_weekly.sh cron không.
