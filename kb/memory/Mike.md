# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 16/11 → 17/11
- Plan T+1 T3 17/11 user duyệt 23:3x ICT 16/11.
- Retro 16/11 ghi (kb/incidents/retro/retro-2026-11-16.md). Pattern 1 (BQ raw thủng) lặp retro thứ 3; ĐÃ escalate `retro-pattern-recurring-bq-raw-gap-wire-0b-unmerged` (khuyến nghị A: merge wire [0b] ticker_integrity_precheck vào bq_freshness_check.sh qua arch-review) — chờ user quyết. Waiver Q9 ĐÃ merge (23f286b50).
## Đang chờ / mở
- User: quyết escalation wire [0b].
- Verify NAV 16/11 đã ghi vào nav_history_SpaceX.csv (report_v2_fallback 12:12Z).
- Taylor: orb-futures vòng 2 (feat/orb-futures-live-20261116) chờ arch-review diff; chưa merge.
- Mốc: 18/11 chấm LVR-2026-10-21; 26/11 Bobby review quý; 15/12 checkpoint LAG ADV + corp-action shadow.

- [2026-11-17T03:41:22Z] [17/11 10:4x] User duyệt (a): Taylor vòng 3 nhỏ ORB (R1 test BOT_STOP+EXIT_PLACED, R2 watch_broker khi chuyển trạng thái kết thúc, N-a/b/c/e) → arch-review CHỈ DIFF → merge (cờ TẮT, không cron).
- [2026-11-17T03:52:55Z] [17/11 11:0x] ORB R3 (outer addddabf9, mike 3e41ae02a): arch-review diff = 6 mục R1/R2/N-a/b/c/e ĐÓNG THẬT (7/7 mutant bắt) nhưng 1 lỗi MỚI do R2: báo ĐỎ giả 'USER ĐÓNG TAY' ngay sau CLOSED nếu positions trễ hơn order_detail (orb_futures.py:835-838+463-467) — chặn LIVE, KHÔNG chặn DRY/merge. Cầu chì ⇒ dừng, chưa merge, hỏi user: (1) merge DRY ngay + sửa trong lúc chạy DRY [khuyến nghị] (2) Taylor vòng 4 trước merge (3) dừng. Còn chờ 4 câu: BOT_STOP đóng?, 10 phiên DRY, nộp thử 5tr, tin [DRY].
- [2026-11-17T03:53:46Z] [17/11 10:5x] DD QTP: Bobby sector read xong (sector_read_nhiet_dien_than_20261117.md); Taylor job Taylor_20261117_035339 đang chạy (brief agents/Taylor/research/dd_QTP_20261117/brief.md). Bước sau: fundamental-skeptic trên REPORT.md → dd-investor-report PDF (KHÔNG email) → ghi dd_price_zones.json + kb/projects/qtp-dd-20261117.md. moat tái dùng NARROW 06/2026.
- [2026-11-17T04:15:03Z] [17/11 11:1x] User chọn (2): Taylor vòng 4 siêu nhỏ (đọc lại positions xác nhận trước báo ĐỎ ở R2 + test; loop_err reset) → arch-review CHỈ DIFF → merge (cờ TẮT, không cron). Còn chờ 4 câu user.
- [2026-11-17T04:17:25Z] [17/11 11:2x] DD QTP: Taylor R1 xong, skeptic INCONCLUSIVE (số khớp, nhưng cần: đọc QĐ768 gốc+COD, hạ trọng số kịch bản tốt, sửa bội số, viết lại mốc#1). R2 Taylor_20261117_041718 (sonnet) đang áp. Sau R2: dựng PDF dd-investor-report (KHÔNG email), kb/projects/qtp-dd-20261117.md, dd_price_zones.json, post user.
