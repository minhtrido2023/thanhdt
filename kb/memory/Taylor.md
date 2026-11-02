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

- [2026-11-01T15:52:06Z] ĐANG DỞ: DCF VN calibration job Taylor_20261101_155145 — agents/Taylor/research/dcf_vn_calibration_20261101/ | NEXT: đọc docs, PREREG
- [2026-11-01T15:54:53Z] [dd-price-zone 01/11] XONG job Taylor_20261101_154045: nhánh feat/dd-price-zone-20261101 (ecd94e5e4, chưa merge) — chờ Mike arch-review/merge; ngưỡng 15% chờ Mike tư vấn user
- [2026-11-01T16:10:40Z] [dd-price-zone vòng2 01/11] XONG job Taylor_20261101_160440: 634f9da84 (chưa merge) — chờ Mike merge; hỏi user DD_ALERT_BASIS + xác nhận center_kind HHS/SIP/TCH
- [2026-11-01T16:20:09Z] [dd-price-zone vòng3 01/11] XONG job Taylor_20261101_161715: ad5a89c2d (chưa merge) — chờ Mike merge; HPG tâm 19.221 chỉ chân RI, hỏi user nếu muốn giữ 20.200
- [2026-11-01T16:42:33Z] [dcf-vn-calib 01/11] XONG job Taylor_20261101_155145: REPORT commit 91336200c (s=0, g_T 4,5% level fix; beta khong vao xep hang; lich 15/2-5-8-11) — CHO quant-skeptic + user quyet; chua code knob vn_v3
- [2026-11-01T16:59:53Z] ĐANG DỞ: dcf_expectation_lens job Taylor_20261101_165940 — agents/Taylor/research/dcf_expectation_lens_20261101/ | NEXT: đọc REPORT dcf_vn_calibration, viết PREREG
- [2026-11-01T17:29:15Z] [dcf-expectation-lens 02/11] XONG job Taylor_20261101_165940: REPORT commit 29ac97b3b — khong xay DCF nhe; ung vien R&D rieng accS (so voi d_NPR LAG) CHO user quyet
- [2026-11-02T01:28:21Z] ĐANG DỞ: job Taylor_20261102_012810 dcf_rate_proxy — research/dcf_rate_proxy_20261102/ | NEXT: đọc docs, PREREG
- [2026-11-02T01:40:11Z] [dcf-rate-proxy 02/11] XONG job Taylor_20261102_012810 (commit 16b3cbddf): giu r hang; de xuat hien thi them r* thi truong (15,1%) + TPCP10Y, chua wire; TPCP10Y/macro_indicator can entry data_registry truoc khi dung
- [2026-11-02T01:54:22Z] [quarterly-report-schedule 02/11] XONG job Taylor_20261102_013823: 33eaaa4e7 nhanh feat/quarterly-report-schedule-20261102 (chua merge) — cho Mike arch-review + cai cron (de xuat kb/cron_registry_quarterly.proposed)
- [2026-11-02T02:17:42Z] [quarterly-report vong2 02/11] XONG job Taylor_20261102_020151: 7bc9aa38e nhanh feat/quarterly-report-schedule-20261102 (chua merge) — cho Mike arch-review r2 + merge + cai cron
- [2026-11-02T02:31:46Z] [dcf-rate-display 02/11] XONG job Taylor_20261102_015334: code 283b0dcd6 (wt-dcf-rate-display-20261102), kb 3f0626e6b — chua merge, cho Mike arch-review; r* cache can build lai hang thang
