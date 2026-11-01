# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái cuối ngày 31/10 (sang 01/11)
- oshares_live: CUTOVER LIVE xong 31/10 15:3x (OSHARES_SOURCE_DEFAULT=live; rollback đổi 1 từ về fin). R11 (áp dụng thống nhất plan echo/EOD/paper) arch-review NEEDS_CHANGES → R12 (Taylor, nhánh session/oshares-r12-20261031 / -ops-): quant-skeptic từng REFUTED (SIGALRM bị nuốt) → vá R12b/R12c; kiểm trạng thái merge R11/R12 trước khi nói "xong". Theo dõi: shout caller thiếu price_date, ops_health mục 17, DCF_RICH LAG.
- report-v2 đã merge master (be54861d6 + r3 5fe318820 + vá 6d9e6cffd). Cron báo cáo THÁNG 10 chạy 09:00 ICT 01/11 bằng pipeline v2 — MỐC KIỂM (PDF 4 trang, TWR MTD −1,885%, SpaceX không chứa ZaloPay). Tuần 26-30/10 v2 đã gửi cả 2 TK.
- Còn mở report-v2: flaky md5 monthly SpaceX ~1/3 lượt (chưa rõ gốc, diag 57aac317f); builder thiếu env BQ ⇒ attribution Unavailable vẫn COMPLETE (giao Taylor: fail-loud); giữ/bỏ số TK DNSE trong .md SpaceX; reports/v2/draft chưa dọn.
- DD: NNC xong (v2 đã email). HPG: Taylor_20261031_093839 DD đang/đã chạy → kb/projects/hpg-dd-20261031.md; TCH/MBB investor report có sẵn. Hỏi user gửi email nếu chưa.
- Wakeup MISS 31/10 = 3/20 (15%): theo dõi 01-04/11; nếu ≥10% lặp lại → cổng hậu kiểm transcript.
- drift CANNOT_CHECK đã vá (0027dac67): theo dõi tới 04/11.
- Chờ user: DGC vòng 6, TV2 watchlist, nguồn Tampa/CFR NH3 vào BQ?
- Mốc: nav-loss-brake 11-09; DT CRISIS ~11/10; Livermore ~19/11; BĐS 11-26; commodity 11-25; LAG 12-15; measurement audit ~12-27; clear_books_daily lần đầu T2 02/11 20:45.

- [2026-11-01T03:32:30Z] 01/11 DD HHS: Bobby xong (sector_read_xe_tai_thuong_mai_vn_20261101.md); Taylor_20261101_033221 đang DD → agents/Taylor/research/dd_HHS_20261101/REPORT.md; sau đó kiểm số + skeptic/investor report + email nếu user yêu cầu. Hợp nhất HHS chưa có — Taylor tìm.
- [2026-11-01T03:46:51Z] 01/11 DD HHS: Taylor XONG (REPORT.md, pointer kb/projects/hhs-dd-20261101.md). Chờ user: chạy fundamental-skeptic? / gửi email (skill dd-investor-report)?
- [2026-11-01T04:09:55Z] 01/11 11:1x DD TV2: Taylor_20261101_040936 (v2 khách quan+GAPS → dd_TV2_20261101/REPORT_v2.md). Kế: fundamental-skeptic → Taylor investor report → Mike kiểm grep → email. LUẬT MỚI: mọi DD tự chạy skeptic+report+email (skill đã cập nhật). HHS (dd_HHS_20261101) CHƯA skeptic/email → làm sau TV2 theo luật mới, hoặc hỏi user.
- [2026-11-01T04:14:24Z] 01/11 HHS: user duyệt bước tiếp. Skeptic REFUTED medium (SKEPTIC_20261101.md), GAPS_FILL.md xong. Taylor_20261101_041414 đang làm REPORT v2 + investor_report/ → Mike đọc kiểm (grep luật, render PDF) rồi gửi email send_dd_report_email.py (+ .ccdb-attachments PDF). Đóng claim: đã nhả topic:dd-hhs; kb pointer hhs-dd-20261101.md cần cập nhật sau v2.
