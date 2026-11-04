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

- [2026-11-04T01:30:15Z] ĐANG DỞ: crisis-DD HT1 ngày6 job Taylor_20261104_013004 | NEXT: đọc dossier, tin mới, dd-note
- [2026-11-04T01:30:15Z] ĐANG DỞ: crisis-DD DRI ngày3 job Taylor_20261104_013001 | NEXT: đọc DOSSIER, tìm tin mới, dd-note
- [2026-11-04T01:33:14Z] [crisis-dd DRI 04/11] XONG ngày3 (không cờ, GIỮ) — mới: NQ 22/10 nâng ngưỡng duyệt GD bên liên quan 10→30% (theo dõi R6); chờ SXKD T10 ~10/11
- [2026-11-04T01:33:20Z] [crisis-dd HT1 04/11] XONG ngay6 (khong co, GIU) — con: BCTC goc, ngay 7 tong ket
- [2026-11-04T15:54:57Z] ĐANG DỞ: DD DCM job Taylor_20261104_155446 — research/dd_DCM_20261104/ | NEXT: đọc skill+template, render BCTC Q3/26
- [2026-11-04T16:16:14Z] [dd-DCM 04/11] XONG job Taylor_20261104_155446: tam 28.072 (sau CK TK 28.072), gia 33.000 DAT (>P90 31.901); CHUA skeptic, CHUA commit, CHUA investor report/price_zones
- [2026-11-04T16:32:57Z] [dd-DCM r2 04/11] XONG job Taylor_20261104_162755: tam 27.021 (r1 28.072), gia 33.000 DAT (co dieu kien bien: 220 NGHIENG DAT, >=233 HOP LY); REPORT_r2.md; CHUA skeptic r2, CHUA commit, CHUA email
- [2026-11-04T16:48:51Z] [dd-DCM investor 04/11] XONG job Taylor_20261104_164310: PDF 9tr ở research/dd_DCM_20261104/investor_report/; dry-run email OK, CHƯA gửi; CHƯA ghi dd_price_zones.json (cần skeptic xác nhận)
- [2026-11-04T17:01:34Z] ĐANG DỞ: DD DCM r4 (hợp đồng khí PM3 CAA) job Taylor_20261104_170125 — research/dd_DCM_20261104/ | NEXT: đọc egm2025 txt KEY CONTENTS, model_r2.py, REPORT_r3.md
- [2026-11-04T17:09:05Z] [C1 te-crosscheck 05/11] XONG job Taylor_20261104_170501: branch feat/te-crosscheck-20261105 (worktree wt-te-crosscheck-20261105), CHỜ arch-review rồi merge; đề xuất TE làm tầng CPI chờ user duyệt
- [2026-11-04T17:11:29Z] [dd-DCM r4 05/11] XONG job Taylor_20261104_170125: giả thuyết user NỬA ĐÚNG (giá đổi qua SĐBS12 Nam Du 10,39 cố định, không qua PM3); tâm 27.021->23.644, giá 33.000 ĐẮT mọi lưới; CHƯA skeptic, CHƯA commit, investor PDF lỗi thời
- [2026-11-04T17:32:21Z] [dd-DCM r5+investor 05/11] XONG job Taylor_20261104_172238: tam 24.326 (A 24.192, B 24.459), gia 33.000 tren vung gia tri moi luoi; nguong dao 243 (ND30+V1); REPORT_r5.md + investor_report/DCM_DD_investor_report_20261105.pdf 9tr; CHUA skeptic r5, CHUA commit, CHUA email, CHUA dd_price_zones; NQ 23/9 chinh thuc khong tim thay
- [2026-11-04T18:22:08Z] ĐANG DỞ: D2 liquidity-spread→deposit lead job Taylor_20261104_182158 — agents/Taylor/research/liquidity_spread_deposit_lead_20261105/ | NEXT: PREREG khoá md5 rồi chạy
- [2026-11-04T18:24:03Z] ĐANG DỞ: E1 macro_snapshot_asof job Taylor_20261104_182156 — worktree wt-macro-snapshot-asof-20261105 | NEXT: selfcheck 3 asof + DD_SKILL_PROPOSAL.md + bus finding
- [2026-11-04T18:25:39Z] [D1+freshness 05/11] XONG job Taylor_20261104_182153: 2 nhánh feat/liq-spread-d1-20261105 (outer 246e38553, mike d83ae9762) CHỜ arch-review rồi merge; D2 (nghiên cứu spread dẫn lãi huy động) chưa làm
- [2026-11-04T18:27:22Z] [D2 liq-spread 05/11] XONG job Taylor_20261104_182158: ỦNG HỘ biên N=3 (LOO→không KL), nhánh research/liquidity-spread-deposit-lead-20261105 CHƯA merge, chờ quant-skeptic (Mike)
- [2026-11-04T18:29:19Z] [E1 macro_snapshot 05/11] XONG job Taylor_20261104_182156: commit 1447c2a90 nhánh feat/macro-snapshot-asof-20261105, CHỜ arch-review nhẹ, chưa merge
- [2026-11-04T18:36:45Z] [D2 r2 05/11] XONG job Taylor_20261104_183446: nhãn KHÔNG KẾT LUẬN, commit 18748ac7c nhánh research/liquidity-spread-deposit-lead-20261105, CHƯA merge
- [2026-11-04T18:37:18Z] [CPI-TE 05/11] XONG job Taylor_20261104_182151: nhanh feat/cpi-te-tier-20261105 (wt-cpi-te-20261105) commit 1cdd76581, CHO arch-review+merge; golive CAPIT PIT CPI 4.69->5.09 can Mike xac nhan; chua quet results_registry theo DCF mode
