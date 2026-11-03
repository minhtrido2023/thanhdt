# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái cuối ngày 02/11 (sang 03/11)
- Retro 02/11 ghi (retro-2026-11-02.md). Theo dõi: wakeup MISS 0/20 (chưa rõ do cổng exit 8); anomaly-flags-stale giả CN/lễ chưa fix.
- SÁNG 03/11 sau 09:05: kiểm fill bán hết DRI + TV1 về 0 cả 2 TK (user duyệt plan 23:34); TCH đã bỏ khỏi plan theo luật cờ.
- 4 quy tắc user 02/11 (kb/projects/dd-flag-rules-20261102.md). Nhánh dev: V2 DD-zone-candidates APPROVED (chờ user duyệt merge); V1 dd-flag-order-gate đang vòng 2 (Taylor) → arch-review lại → CHỜ USER xác nhận phạm vi 'cờ' (193/336 mã bị cờ; 8/30 custom30V gồm CTCK) trước merge.
- Chờ user: pnj-bctc-q3-review-trigger (chạy lại DD PNJ?); state_TV1_*.json (thesis/trần/điều kiện dừng PPA); 4 bản TV1 cũ trong hộp thư NĐT; KBSV/PPA gốc chưa kiểm; DGC vòng 6; TV2 watchlist; tunnel cố định.
- Theo dõi: dcf_refresh_gate log 03/11 08:12; dcf-rstar-refresh (nhánh feat/dcf-rstar-refresh-20261102) → arch-review → cài cron, hạn tay 2026-12-07; crontab báo cáo quý CHƯA cài (cần user, trước 31/12).
- Mốc: nav-loss-brake 11-09; DT CRISIS ~11/10; Livermore ~19/11; commodity 11-25; BĐS 11-26; LAG 12-15; measurement audit ~12-27.

- [2026-11-03T02:54:33Z] 03/11 09:5x V1 cổng cờ (PARK miễn, CAPIT áp) MERGED main 7eb1f434d; V2 ứng viên DD MERGED mike 77c6b6a86 (user duyệt). Đang chờ: CAPIT research Taylor_20261103_024121 → quant-skeptic → báo user. Kiểm fill bán DRI+TV1 sau 15:00 (SpaceX DRI 950/TV1 2300, ZaloPay DRI 450/TV1 1100 lúc 09:41). Sáng nay cổng cờ có hiệu lực từ lượt run_bot 13:00 / plan 04/11.
- [2026-11-03T05:38:09Z] 03/11 12:40 dcf-rstar-refresh MERGED (WC f3e6b9f8c, mike a7038237f) + 2 cron ĐÃ CÀI (23 18 2-7 refresh; 37 3 check-expiry; backup backups/crontab_pre_dcf_rstar_20261103_1237.txt). Theo dõi: logs/dcf_rstar_refresh.log lần đầu 04/11 01:23 ICT (đường tắt rc=0) và 03/12 (dựng thật đầu tiên). Xong chuỗi DCF 02-03/11.
- [2026-11-03T08:32:14Z] 03/11 15:3x DD MVC: Bobby xong (sector_read_gach_nung_icd_binhduong_20261103.md); Taylor_20261103_082601 đang DD; sau đó skeptic → investor report → DỪNG, KHÔNG gửi email tới khi user báo (skill đã sửa); ghi dd_price_zones.json
- [2026-11-03T08:51:43Z] 03/11 15:5x DD MVC: skeptic CONFIRMED+12 đính chính (SKEPTIC_20261103.md); Taylor_20261103_085129 áp đính chính + dựng investor report + dd_price_zones; xong → Mike đọc kiểm (grep luật 18, render PDF) → đính kèm PDF Discord → CHỜ user báo gửi email
- [2026-11-03T09:05:31Z] 03/11 16:1x DD MVC XONG: PDF investor_report đã đưa user; CHỜ user báo 'gửi email' → gửi đúng 1 lần bản chốt (send_dd_report_email.py, EMAIL_SUBJECT.txt, banner trong investor_report/figs). Pointer kb/projects/mvc-dd-20261103.md
- [2026-11-03T09:35:18Z] 03/11 16:4x DD MVC vòng 3: user yêu cầu skeptic vòng 2 (xong: SKEPTIC2_20261103.md) + dựng lại mù giá; Taylor_20261103_093502 đang làm (r3/, đè investor_report/); xong → Mike kiểm (grep L18, render) → có thể skeptic vòng 3 ngắn → post PDF; CHƯA gửi email tới khi user báo
- [2026-11-03T09:57:34Z] 03/11 17:0x DD MVC r4: skeptic vòng 3 CONFIRMED; Taylor_20261103_095718 sửa nhãn rẻ có điều kiện+thang ngưỡng+cắt từ+dd_price_zones NNC; xong → Mike grep L18 + render → post PDF; CHƯA gửi email
- [2026-11-03T10:04:13Z] 03/11 17:1x DD MVC r4 CHỐT: PDF md5 dc70b3e3 đã đưa user (thang ≤13.000/13.000-17.500/17.500-22.900/≥25.400, giá 13.700 = rẻ có điều kiện). CHỜ user báo 'gửi email' → gửi 1 lần (send_dd_report_email.py ... EMAIL_SUBJECT.txt, banner figs).
- [2026-11-03T10:07:33Z] 03/11 17:1x DD MVC r5: user đổi nguyên tắc (dự án mới base = sổ sách/NPV 0; luật 20 skill đã ghi); Taylor_20261103_100718 kiểm kê khoản giảm trừ + dựng lại mù giá + rà NNC-DD; xong → Mike grep L18/render → skeptic vòng 4 ngắn (mọi giảm trừ base có cơ sở?) → post PDF; báo user quyết có dựng lại NNC không; CHƯA gửi email
