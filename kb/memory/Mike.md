# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-12 (cuối ngày, sau daily retro bước 3/3)

## Daily retro 08-12 — XONG
9 sự cố, 3 pattern. Wags verify GAPS FOUND → đã sửa (bổ sung sự cố #9
`DollarBill/zalopay-tv1-ceiling-vs-t1-band`, account ZaloPay, hoàn toàn vắng mặt trong draft gốc;
sửa số đếm bus sweep 34→36). File: `kb/incidents/retro/retro-2026-08-12.md`, commit `687a1a0b`.

**Pattern 1 (mới đặt tên hôm nay, tái diễn 6 lần trong ngày)** — gate/mechanism mới build ĐÚNG
nhưng caller tự động hiện có (`consolidate.sh`, `fleet_backup.sh`, `kb_nightly.sh` ×2,
`cron_health_check_daily.sh`, `backup.sh`) nuốt exit code rồi báo "done" vô điều kiện. Đã cạn
site (scan pattern-lệnh toàn 1473 file `.sh`), arch-reviewer CONFIRMED. Lesson: khi build gate
mới cho hành động có N caller sẵn, quét toàn repo theo PATTERN LỆNH ngay từ round 1, không đợi
tới round 5.

**Pattern 2 (Pattern-B, lần đặt tên thứ 3, sinh 3 instance MỚI trong ngày)** — checker/verify so
sánh SAI BIỂU DIỄN của cùng 1 sự thật (chuỗi mô tả vs giá trị, bus vs dispatch-prompt, prefix
có/không hậu tố) → báo động giả. Đề xuất PREVENTION MẠNH HƠN: thêm mục mới vào
`coding_guidelines.md` ("mọi so sánh 2-nguồn phải chuẩn hoá giá trị trước khi so") — CHƯA duyệt,
chờ user OK hướng đi (Mike có thể tự soạn `.proposed` theo §13).

**Pattern 3 (KHÔNG MỚI, vẫn TREO — nay 2 câu hỏi cùng họ)** — backlog ghi file `kb/incidents/`
không giảm (7/9 sự cố hôm nay chưa có file trước khi retro chạy). 2 quyết định CẦN USER CHỌN
đang chờ:
1. `Mike/retro-pattern-recurring-2-days` (mở 08-09, khuyến nghị (b) từ Wags 08-10) — treo >3 ngày.
2. `DollarBill/zalopay-tv1-ceiling-vs-t1-band` (mở 08-11, tái khẳng định 08-12) — giữ ceiling
   20.000 (chấp nhận rủi ro trượt) hay nới lên 20.200 khớp băng T1 mới (chốt 08-10)? Giá EOD
   08-12=20.300 đã vượt cả 2 mốc, ZaloPay vẫn 0cp TV1, mức nghiêm trọng ĐANG TĂNG mỗi ngày.

## Việc treo sang 08-13 (ưu tiên)
1. Đưa user quyết dứt điểm 3 việc CÙNG LÚC (Pattern 2 prevention + 2 câu hỏi Pattern 3 ở trên).
2. Ghi file `kb/incidents/2026-08/` cho 6 sự cố còn thiếu (retro liệt kê đủ #1,#2,#3,#5,#6,#9).
3. TV1 ZaloPay: KHÔNG đặt lệnh mới 08-13 cho tới khi có quyết định ceiling (đã dừng theo đúng
   khuyến nghị Wags, tránh churn vô ích).

- [2026-08-13T00:06:58Z] 2026-08-13 07:xx: TV1 XONG cho hôm nay. Phát hiện+sửa thêm 1 bug TZ thật trong compute_active_nav.py (date.today() trần thay vì today_ict(), khiến computed_at sai trước ~07:00 ICT — đúng họ lỗi §16). Xoá lệnh TV1 cũ (trần 20.000 cứng) khỏi plan SpaceX 08-13 (chưa duyệt), chạy injector thật cho cả 2 account: SpaceX 1.800cp + ZaloPay 1.200cp, cả 2 @ trần động 20.497đ. Cả 2 plan sẵn sàng chờ user duyệt bình thường. Việc thêm cron compute_active_nav.py trước 20:30 ICT (câu hỏi cũ) VẪN CHƯA LÀM — cần quyết riêng, không chặn hôm nay vì đã chạy tay xong.
- [2026-08-13T00:41:17Z] 2026-08-13 08:xx: Cron compute_active_nav_all.sh XONG (crontab 20:15 ICT T2-T6, commit mike@470d9f5b, kb/cron_registry.md cập nhật đúng §11). Permission Edit/Write data/trade_plans/** XONG (commit mike@ab794cf3, settings.json project — Edit/Write tool only, KHÔNG mở Bash blanket theo đúng ý user). Lưu ý: quyền mới có hiệu lực từ phiên/lượt tiếp theo, không retroactive cho phiên đang chạy. TV1 hôm nay đã xong hoàn toàn (P1 reconcile + plan đã sẵn sàng chờ duyệt) — mạch việc TV1 tạm đóng.
- [2026-08-13T04:03:55Z] 2026-08-13 08:xx: Nghiên cứu xong bảng BQ mới tav2_bq.corporate_action theo yêu cầu user — DIV/ISS/AIS event-level, đúng 'raw per-event' mà ticker_close_vs_price_dividend_adj.md từng nói thiếu. Đã ghi kb/data_registry/price-volume/corporate_action_bq.md (status TRAP: 1-lần-nạp, chưa có writer/cron, AIS lag ~7 tuần so exright_date). CHƯA wire vào pipeline nào — cần xác nhận refresh cadence + Taylor/quant-skeptic review trước khi đổi report §21 gate hoặc Oshares live.
- [2026-08-13T08:47:25Z] 2026-08-13: Chuỗi corporate_action/paper-report XONG (6 vòng, kb/projects/corporate-action-bq-integration-0813.md). Việc còn mở: Việc B (oshares_live.py) chờ user chọn consumer đầu tiên trước khi wire; vòng 6 (rc=1+KeyError) user quyết bỏ qua. Freshness corporate_action cần verify lại 08-14.
- [2026-08-13T12:47:17Z] 2026-08-13: Đã cài crontab corp_action_daily.py (07:30 ICT T2-T6), user duyệt sau 4 vòng quant-skeptic CONFIRMED. Chạy alert-only 5-10 phiên đầu, verify MAX(ingested_at) mỗi phiên trước khi tin tầng freshness/backfill. Chuỗi corporate_action/paper-report (Việc A-E) khép lại — chỉ còn Việc B (Oshares) chờ chọn consumer máy.
