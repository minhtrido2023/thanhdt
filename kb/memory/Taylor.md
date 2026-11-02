# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Taylor.

> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Taylor ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Taylor/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Taylor_history.md` — không mất, không auto-load.

- [2026-11-02T01:28:21Z] ĐANG DỞ: job Taylor_20261102_012810 dcf_rate_proxy — research/dcf_rate_proxy_20261102/ | NEXT: đọc docs, PREREG
- [2026-11-02T01:40:11Z] [dcf-rate-proxy 02/11] XONG job Taylor_20261102_012810 (commit 16b3cbddf): giu r hang; de xuat hien thi them r* thi truong (15,1%) + TPCP10Y, chua wire; TPCP10Y/macro_indicator can entry data_registry truoc khi dung
- [2026-11-02T01:54:22Z] [quarterly-report-schedule 02/11] XONG job Taylor_20261102_013823: 33eaaa4e7 nhanh feat/quarterly-report-schedule-20261102 (chua merge) — cho Mike arch-review + cai cron (de xuat kb/cron_registry_quarterly.proposed)
- [2026-11-02T02:17:42Z] [quarterly-report vong2 02/11] XONG job Taylor_20261102_020151: 7bc9aa38e nhanh feat/quarterly-report-schedule-20261102 (chua merge) — cho Mike arch-review r2 + merge + cai cron
- [2026-11-02T02:31:46Z] [dcf-rate-display 02/11] XONG job Taylor_20261102_015334: code 283b0dcd6 (wt-dcf-rate-display-20261102), kb 3f0626e6b — chua merge, cho Mike arch-review; r* cache can build lai hang thang
- [2026-11-02T04:00:17Z] ĐANG DỞ: crisis-DD DRI ngày1 job Taylor_20261102_040003 | NEXT: legal-vn + tin DN, viết quick note dd-note
- [2026-11-02T04:02:33Z] [crisis-dd DRI 02/11] XONG ngày1 quick (không cờ, GIỮ) — mở: SXKD T10 ~10/11, Quỹ TDND/Dakruco BCTC Q3 chi tiết
- [2026-11-02T04:04:02Z] [tv1-dd 02/11] XONG job Taylor_20261102_035322: REPORT commit 8fcce1711 — cho Mike chay fundamental-skeptic + investor report; mo: khoan thu nhap khac 33,8 ty chua giai
- [2026-11-02T04:28:22Z] [tv1-dd r2 02/11] XONG job Taylor_20261102_042353 — cho Mike chay fundamental-skeptic vong 2 + investor report; ket luan moi: gia ~ngang EV da chiet khau; TV1 co ten trong 13 don vi BCA
- [2026-11-02T04:29:49Z] ĐANG DỞ: job Taylor_20261102_042930 TV1 investor report — research/dd_TV1_20261102/investor_report/ | NEXT: đọc skill dd-investor-report, TV2 build_report
- [2026-11-02T04:40:45Z] [tv1-investor 02/11] XONG job Taylor_20261102_042930 commit 958175a36 — cho Mike gui email + ghi dd_price_zones.json
- [2026-11-02T07:53:55Z] ĐANG DỞ: job Taylor_20261102_075340 TV1 DD r3 (sửa B1-B4,N1-N10) — research/dd_TV1_20261102/ | NEXT: đọc SKEPTIC2, sửa valuation.py→REPORT→investor_report
- [2026-11-02T08:03:59Z] [tv1-dd r3 02/11] XONG job Taylor_20261102_075340 commit 465fedbc1 — ban dinh chinh NDT cho Mike gui email + sua dd_price_zones TV1 (17.800-20.600)
