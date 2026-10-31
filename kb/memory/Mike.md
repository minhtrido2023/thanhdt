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
- [2026-10-31T02:03:25Z] 31/10 09:1x: NNC báo cáo nhà đầu tư ĐÃ GỬI email (dtienthanh@gmail.com) + PDF vào Discord. Vùng 59,3–79,5k (giữa 69,4k), giá 47.100 dưới vùng. Chưa skeptic vòng 2 (user hỏi 1 vòng). Pointer kb/projects/nnc-dd-20261030.md.
- [2026-10-31T02:09:09Z] 31/10 09:1x: MERGED oshares R2-R7 (outer c2c817139 + sua import mo coi 27deff762; mike 153d7ec24). Selfcheck main OK 2 TZ + 5 DCF selfcheck + ops_health selfcheck. Knob van fin. Bat live = vong rieng: vá khoa ex-date==asof/price_date, method=ERROR im lang, probe C4, caller khai price_date, doi chieu PHR/HTN/AIG; can user duyet rieng.
- [2026-10-31T02:54:30Z] 31/10 10:0x: user góp ý báo cáo NNC → skill dd-investor-report luật 15 (bản đồ + ảnh sản phẩm; make_map.py) + vá alt banner email. Chưa gửi lại NNC bản thêm hình (chờ user).
- [2026-10-31T02:54:36Z] 31/10 09:5x: user 'lam tiep cac buoc de bat live' -> Taylor_20261031_025427 (opus/medium --bg, 5400s): H1 khoa ex-date, H2 ERROR shout, H3 probe C4, H4 caller khai price_date (duong tien), H5 doi chieu PHR/HTN/AIG, H6 quet launcher. Xong: Mike kiem -> arch-review(opus high, duong tien) + quant-skeptic -> bao user; LAT CONG live (OSHARES_SOURCE_DEFAULT) chi sau CONFIRMED+APPROVED va hoi user lan cuoi, ngoai 19:00-23:10, ghi cutover-marker + dcf_lens_history cung commit.
- [2026-10-31T03:05:57Z] 31/10 10:0x: user duyệt Taylor làm lại NNC v2 (bản đồ + ảnh sản phẩm BCTN, luật 15): Taylor_20261031_030545 (sonnet/medium --bg) → dd_NNC_20261030/investor_report_v2/. Xong: Mike kiểm (grep luật 4/12, diff số vs bản gốc, render trang bản đồ/ảnh, alt <img>) → gửi email send_dd_report_email.py --banner + PDF vào .ccdb-attachments.
