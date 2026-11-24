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

- [2026-11-23T12:11:22Z] [VCB DD 23/11] XONG job Taylor_20261123_120305: REPORT_rev4 tâm 35.600 (vùng 30.900–42.100), r4 INCONCLUSIVE (vòng cuối) — CHỜ Mike áp LEDGER_PROPOSAL_VCB.json (REFUTED_OPEN) / user quyết
- [2026-11-23T12:11:56Z] [SCL rev7 23/11] XONG job Taylor_20261123_120301: REPORT_rev7 tâm 16.237, skeptic r4 INCONCLUSIVE (HĐ nguồn tro) — vòng cuối, CHỜ Mike áp LEDGER_PROPOSAL_SCL.json (REFUTED_OPEN)
- [2026-11-23T12:14:43Z] [DD CSV vòng cuối 23/11] XONG job Taylor_20261123_120254: REPORT_r5 tâm 10.447, skeptic r4 INCONCLUSIVE ⇒ DỪNG — CHỜ Mike áp LEDGER_PROPOSAL_CSV.json (rev3 REFUTED_OPEN)
- [2026-11-23T12:14:49Z] [DD LLM rev5 23/11] XONG job Taylor_20261123_120256: tâm 20.978 (đắt, 1,59×), r4 REFUTED vòng cuối — CHỜ Mike áp LEDGER_PROPOSAL_LLM (rev3 REFUTED_OPEN) / user quyết
- [2026-11-23T12:15:17Z] [dd-VLB rev4 23/11] XONG job Taylor_20261123_120307: REPORT_rev4 tâm 45.161, skeptic r3 INCONCLUSIVE (vòng cuối, dừng) — CHỜ Mike áp LEDGER_PROPOSAL_VLB.json (REFUTED_OPEN, audited_fy_missing=false)
- [2026-11-23T12:15:28Z] [DD TTA 23/11] XONG job Taylor_20261123_120303: REPORT_rev5 tâm 7.547 (vùng 6.415–8.680), skeptic r3 (vòng cuối) INCONCLUSIVE — CHỜ Mike áp LEDGER_PROPOSAL_TTA.json (REFUTED_OPEN rev3) / user quyết
- [2026-11-23T12:20:45Z] [BSR rev5 23/11] XONG job Taylor_20261123_120250: tâm 16.544, r4 INCONCLUSIVE — CHỜ Mike áp LEDGER_PROPOSAL_BSR.json (rev3 REFUTED_OPEN)
- [2026-11-23T12:27:37Z] [CK holding + HHS rev7 23/11] XONG job Taylor_20261123_120407: CK đo 26,63% (N=6), HHS rev7 tâm 10.805 TRONG, skeptic r5 REFUTED (EX k, phạm vi CK) — CHỜ Mike áp LEDGER_PROPOSAL (REFUTED_OPEN) / user quyết base CK
- [2026-11-23T17:50:47Z] CODE B radar xong: nhánh session/Taylor_20261123_174706 (repo ngoài, commit 33c14fdef) chờ Mike duyệt/merge; sau merge chạy value_radar.py --rebuild-norm5
- [2026-11-23T17:57:39Z] [dd-vs-radar rerun 24/11] XONG job Taylor_20261123_174703: rerun/REPORT_R2.md + REPORT_D2.md, finding dd-vs-radar-R2/D2-20261124 — CHỜ Mike tổng hợp/skeptic; chưa commit (rerun/ untracked)
- [2026-11-24T03:24:18Z] [dd-forward 24/11] XONG job Taylor_20261124_031944: nhánh feat/dd-forward-outcome-20261124 (526879fef) — CHỜ Mike duyệt diff + cài cron đề xuất; mốc đánh giá 2027-03-31
- [2026-11-24T03:26:22Z] [dd-history-label E 24/11] XONG job Taylor_20261124_031942: nhánh session/Taylor_20261124_031942 commit 1784cbafb (chưa merge) — CHỜ Mike duyệt diff + quyết cờ 'proxy lệch DD' (k ngoài [0,5;2])
