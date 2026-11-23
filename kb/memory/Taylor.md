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

- [2026-11-22T23:44:35Z] ĐANG DỞ: job Taylor_20261122_234422 DD DCM rebuild (job 234402 bị cancel) | NEXT: đọc skeptic r1 + report, viết REPORT_rev7.md
- [2026-11-22T23:44:43Z] ĐANG DỞ: job Taylor_20261122_234426 DD PNJ rebuild rev2 | NEXT: đọc skeptic r1 + REPORT.md dd_PNJ_20261114
- [2026-11-22T23:44:43Z] ĐANG DỞ: job Taylor_20261122_234428 DD VCB rebuild rev2 | NEXT: đọc skeptic r1 + REPORT.md
- [2026-11-22T23:44:47Z] ĐANG DỞ: job Taylor_20261122_234430 DD MSB rebuild rev2 | NEXT: đọc skeptic r1 + REPORT.md
- [2026-11-22T23:53:17Z] ĐANG DỞ: job Taylor_20261122_234428 VCB rev2 viết xong REPORT_rev2.md | NEXT: skeptic r2 → LEDGER_PROPOSAL_VCB.json → bus+notify
- [2026-11-22T23:55:37Z] ĐANG DỞ: job Taylor_20261122_234422 DCM rev7 (REPORT_rev7.md tâm 24.822 TRÊN vùng) | NEXT: skeptic r2 → LEDGER_PROPOSAL_DCM.json → bus+notify
- [2026-11-22T23:56:35Z] [dd-TTA r4 23/11] XONG job Taylor_20261122_234424: tâm sau TK 8.548 (r3 6.159), skeptic r2 INCONCLUSIVE — CHỜ Mike áp LEDGER_PROPOSAL_TTA.json (REFUTED_OPEN)
- [2026-11-22T23:59:08Z] ĐANG DỞ: job Taylor_20261122_234428 VCB REPORT_rev3 (tâm 36.000) skeptic r3 | NEXT: LEDGER_PROPOSAL_VCB.json → bus+notify
- [2026-11-23T00:01:20Z] [dd-pnj rebuild 23/11] XONG job Taylor_20261122_234426: REPORT_rev4 tam 4.205 (vung 2.212-6.198), skeptic r3 REFUTED (O2 phat kep) — CHO Mike ap LEDGER_PROPOSAL (REFUTED_OPEN) / user quyet vong 3
- [2026-11-23T00:01:59Z] [VCB rebuild 23/11] XONG job Taylor_20261122_234428: REPORT_rev3 tâm 36.000 vùng 31.200–42.500, skeptic r3 INCONCLUSIVE — CHỜ Mike áp LEDGER_PROPOSAL_VCB.json
- [2026-11-23T00:04:04Z] [dd-MSB rebuild 23/11] XONG job Taylor_20261122_234430: REPORT_r4 tam 13.042 (skeptic r3 CONFIRMED, md5 b3ec7a51) — CHO Mike ap LEDGER_PROPOSAL_MSB.json (can entry buoc1 truoc tool)
- [2026-11-23T00:08:16Z] [DD DCM rebuild 23/11] XONG job Taylor_20261122_234422: REPORT_rev8 tâm 26.780, skeptic r3 REFUTED — CHỜ Mike áp LEDGER_PROPOSAL_DCM.json (REFUTED_OPEN) / user quyết vòng 3
