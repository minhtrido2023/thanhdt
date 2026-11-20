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

- [2026-11-20T04:19:46Z] ĐANG DỞ: job Taylor_20261120_041933 DD TTA | NEXT: tải BCTC Q3/2026 vào agents/Taylor/research/dd_TTA_20261120/src
- [2026-11-20T04:19:47Z] ĐANG DỞ: job Taylor_20261120_041936 QTP r3 envcapex | NEXT: đọc dd_QTP_20261117/model/qtp_model.py + REPORT, dựng qtp_model_r3.py ở research/qtp_r3_envcapex_20261120
- [2026-11-20T04:27:42Z] [qtp-r3 20/11] XONG job Taylor_20261120_041936: tam QTP r3 sau CK ~7053 (DAT, gia/tam 1,45) do opex 572 ty/nam + von du an khi thai — CHO Mike skeptic + Wendy soat TT57 D20.3 tuong duong trong TT12/2025; Mike sua REPORT/investor/dd_price_zones
- [2026-11-20T04:29:34Z] [dd-tta 20/11] XONG job Taylor_20261120_041933: REPORT dd_TTA_20261120, tam 8.040 (sau TK 7.240), KHONG RE — CHO Mike goi fundamental-skeptic + ghi dd_price_zones
- [2026-11-20T04:40:15Z] [qtp-r3b 20/11] XONG job Taylor_20261120_043725: tam 7.701 sau CK (P0 0,4), DAT; CHO Mike sua REPORT r2/investor/dd_price_zones
- [2026-11-20T04:49:53Z] [qtp-r3c 20/11] XONG job Taylor_20261120_044905: REPORT_r3c, tam 7.701 giu nguyen, opex2032=8.458, thuan loi=9.240 — CHO Mike ap vao REPORT r2/investor; con thieu GPMT 517 PL2 (can xin ban)
- [2026-11-20T04:52:47Z] [dd-tta-r2 20/11] XONG job Taylor_20261120_044902: tam 6.342 / sau TK 5.708 (B' trung tam), NON §2/§2.5, KHONG RE giu — CHO Mike goi fundamental-skeptic r2 + ghi dd_price_zones (chua ghi, khong email)
- [2026-11-20T05:00:49Z] ĐANG DỞ: job Taylor_20261120_050035 TTA r3 + investor report | NEXT: REPORT_r3.md + model/dcf_tta_r3.py rồi investor_report/
- [2026-11-20T05:11:53Z] [dd-tta-r3+NDT 20/11] XONG job Taylor_20261120_050035: REPORT_r3 tam 6.159 sau CK 2,89% (md5 model 5ff89722…), investor_report 7 trang dry-run — CHO Mike ghi dd_price_zones + user bao gui email
- [2026-11-20T09:29:45Z] ĐANG DỞ: job Taylor_20261120_092932 QTP investor report 20/11 | NEXT: dựng investor_report_20261120 từ REPORT_r3c + investor_report r2
- [2026-11-20T09:35:54Z] [qtp-investor 20/11] XONG job Taylor_20261120_092932: investor_report_20261120 11 trang dry-run, chưa gửi email — CHỜ Mike kiểm + user lệnh gửi; dd_price_zones QTP Mike ghi
- [2026-11-20T09:37:01Z] ĐANG DỞ: job Taylor_20261120_093005 selfcheck sweep — 3 CLOSED (981a0a3c7); restore research 37952c0bb (branch fix/restore-dcf-research-20261120) chờ arch-reviewer | NEXT: merge pathspec vào mike master, chạy dcf_rate_frame + dcf_rstar_refresh selfcheck, đóng, ghi finding
- [2026-11-20T09:42:24Z] [sweep 20/11] XONG job Taylor_20261120_093005: 5/6 selfcheck-red CLOSED; phs_flash OPEN (de xuat manual_only cho Wags) — sweep sau: neu van OPEN => CAN USER + post Architecture
- [2026-11-20T14:45:50Z] [ddz-perf 20/11] XONG job Taylor_20261120_143220: nhánh perf/ddzone-watch-20261120 commit 108f7b220 (wt-ddzone-perf-20261120) — CHỜ Mike review+merge
- [2026-11-20T16:05:56Z] [dd-bqclient 20/11] XONG job Taylor_20261120_154910: commit 57c554c2c nhanh fix/dd-bqclient-failcache-20261120 (outer repo) — CHO Mike review+cherry-pick
