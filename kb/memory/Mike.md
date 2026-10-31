# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái cuối ngày 30/10 (sang 31/10)
- SCL thoái xong (fill 13:10 30/10). DRI giảm 50% + bán tay đã xử. Luật cảnh báo tăng vốn đã merge.
- DCF mặc định domestic_v2 (rollback: RATE_FRAME_DEFAULT→legacy); theo dõi ops_health CHECKDCFRF.
- drift checker CANNOT_CHECK ĐÃ VÁ (0027dac67); theo dõi 31/10-04/11 xem còn xuất hiện trong retro không. Hai chẩn đoán trigger (Taylor vs arch-review) chưa đối chiếu.
- oshares_live: knob TẮT đã merge; R2-R7 Taylor xong (outer a3c2c0600 nhánh session/oshares-r2r7-20261030, mike 0298dd9b1 nhánh session/oshares-r2r7-ops-20261030) — CHỜ USER: chạy quant-skeptic+arch-review rồi merge mike trước, outer sau; KHÔNG bật live.
- DD NNC xong (kb/projects/nnc-dd-20261030.md): chờ user có gửi email (dd-investor-report) không.
- Chờ user: DGC vòng 6, TV2 watchlist, nguồn Tampa/CFR NH3 vào BQ?
- cron clear_books_daily đã cài (lần đầu T2 02/11 20:45).
- Mốc: nav-loss-brake 11-09; DT CRISIS ~11/10; Livermore ~19/11; BĐS 11-26; commodity 11-25; LAG 12-15; measurement audit ~12-27.

- [2026-10-30T21:34:29Z] 31/10 weekly ops audit xong: sửa đỏ giả harness (0a1bb517b) + manifest (8bdf3f6e6) + index (efc8f5248). Theo dõi: livermore REPORT_BLOCK ở weekly 09:00 31/10 (chưa verify); deposit_fallback known_red phải tự đóng ở lần daily 04:30 01/11; newdeals T2 02/11 phải PASS (TCB).
- [2026-10-31T01:45:26Z] 31/10 08:5x: NNC: skeptic REFUTED (medium; 12 đính chính, file dd_NNC_20261030/SKEPTIC_20261031.md: phạt hành chính KT25 TM7.8, gán nguồn Bobby/FPTS, giá thực -3%/năm, cho thuê Núi Nhỏ...). Taylor_20261031_014511 (opus/medium) áp đính chính + viết báo cáo nhà đầu tư dd_NNC_20261030/investor_report/. Xong: Mike grep luật 4/12, render PDF xem mắt, gửi email send_dd_report_email.py (--banner), đính PDF vào .ccdb-attachments, thả claim topic:dd-NNC-email-20261031.
- [2026-10-31T01:47:48Z] 31/10 08:5x: oshares R2-R7: arch-review APPROVED (non-blocking: import mo coi TABLE,bq oshares_dcf.py:28; merge WC truoc mike) + quant-skeptic CONFIRMED high (merge knob tat an toan; ho con lai: ex-date==asof voi gia pre-ex khai price_date=asof lot khoa R5 — dong truoc khi bat live). CHO USER duyet merge (WC truoc, mike sau, ngoai 19:00-23:10). KHONG bat live.
