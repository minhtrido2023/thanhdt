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

- [2026-11-19T09:58:47Z] [dna-macro-stress 19/11] XONG job Taylor_20261119_095526: commit 91b9a1ef1 repo ngoai nhanh session/dna-macro-stress-line-20261119 — CHO Mike review + quyet noi vao prompt ZaloPay-only (khong vao SpaceX report_v2)
- [2026-11-19T10:05:01Z] [prereg5-hog 19/11] XONG job Taylor_20261119_095518: commit 9b8ddf032 PREREG5 họ 2 DBC — CHỜ Mike thêm registry entry + quyết cron; nowcast 2026Q4 đầu tiên ghi 05-20/01/2027 TRƯỚC khi DBC công bố
- [2026-11-19T10:06:01Z] [bank-nodata 19/11] XONG job Taylor_20261119_095521: commit d0a14445e (wt-bank-nodata-20261119 sparse) — CHO Mike review + arch-reviewer; user quyết riêng có fail-closed fa_ratings_8l cho bank vắng lens không
- [2026-11-19T14:53:23Z] ĐANG DỞ: job Taylor_20261119_145312 bank-nodata phương án B (wt-bank-nodata-20261119, rating_8l_history.py max-rule + cổng chặn) | NEXT: đọc rating_8l_history.py:430-580, sửa, selfcheck
- [2026-11-19T15:07:41Z] [bank-nodata B 19/11] XONG job Taylor_20261119_145312: commit be7b01fa5 (wt-bank-nodata-20261119 sparse) — CHO quant-skeptic + arch-reviewer + user duyet; merge phai chay pre-commit + tao snapshot lens o run dau
- [2026-11-19T15:28:26Z] [bank-nodata R2 19/11] XONG job Taylor_20261119_152223: commit d2fe7a2d5 (wt-bank-nodata-20261119) — CHO arch-reviewer vong 3 + user duyet; merge can tao snapshot lens o run live dau
- [2026-11-20T04:19:46Z] ĐANG DỞ: job Taylor_20261120_041933 DD TTA | NEXT: tải BCTC Q3/2026 vào agents/Taylor/research/dd_TTA_20261120/src
- [2026-11-20T04:19:47Z] ĐANG DỞ: job Taylor_20261120_041936 QTP r3 envcapex | NEXT: đọc dd_QTP_20261117/model/qtp_model.py + REPORT, dựng qtp_model_r3.py ở research/qtp_r3_envcapex_20261120
- [2026-11-20T04:27:42Z] [qtp-r3 20/11] XONG job Taylor_20261120_041936: tam QTP r3 sau CK ~7053 (DAT, gia/tam 1,45) do opex 572 ty/nam + von du an khi thai — CHO Mike skeptic + Wendy soat TT57 D20.3 tuong duong trong TT12/2025; Mike sua REPORT/investor/dd_price_zones
- [2026-11-20T04:29:34Z] [dd-tta 20/11] XONG job Taylor_20261120_041933: REPORT dd_TTA_20261120, tam 8.040 (sau TK 7.240), KHONG RE — CHO Mike goi fundamental-skeptic + ghi dd_price_zones
- [2026-11-20T04:40:15Z] [qtp-r3b 20/11] XONG job Taylor_20261120_043725: tam 7.701 sau CK (P0 0,4), DAT; CHO Mike sua REPORT r2/investor/dd_price_zones
- [2026-11-20T04:49:53Z] [qtp-r3c 20/11] XONG job Taylor_20261120_044905: REPORT_r3c, tam 7.701 giu nguyen, opex2032=8.458, thuan loi=9.240 — CHO Mike ap vao REPORT r2/investor; con thieu GPMT 517 PL2 (can xin ban)
