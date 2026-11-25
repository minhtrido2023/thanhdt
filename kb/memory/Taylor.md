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

- [2026-11-24T10:13:25Z] [dd-recheck nhóm A 24/11] XONG job Taylor_20261124_095514: VGS/TCH/DRI/SIP tâm 0%, skeptic r1 đều INCONCLUSIVE, 4 LEDGER_PROPOSAL REFUTED_OPEN (DRI/SIP hạ từ CONFIRMED backfill) — CHỜ Mike áp sổ + xử lý TRIM_DD xoá đầu vào calc khoá
- [2026-11-24T10:25:24Z] [dd-recheck nhóm B 24/11] XONG job Taylor_20261124_095517: FPT/NNC/DGC tâm 0%, cả 3 skeptic r1 INCONCLUSIVE (thiếu hạng mục), worktree wt-1574720404268912680b commits d2fe430f1/97ef0a396/5d276f5e6 — CHỜ Mike duyệt LEDGER_PROPOSAL + quyết FULL
- [2026-11-24T10:51:25Z] [dd-adjcenter pilot FPT 24/11] XONG job Taylor_20261124_104632: tâm adj 56.204 (−1,93%), nhánh session/adjpilot 0d52b34ec (wt-adjpilot, chưa merge) — CHỜ Mike chốt 3 sửa PREREG (C+, dải p×m, luật r ngoài Σ) trước fan-out 7 mã
- [2026-11-24T11:11:59Z] [dd-adjcenter g1 24/11] XONG job Taylor_20261124_110049: FPT 55.668 / TCH 15.152 / VGS 25.148 (nhánh session/adj-g1, wt-adj-g1, chưa merge) — CHỜ Mike merge + skeptic; VGS phát hiện tồn quỹ KTPL 36,1 tỷ chưa trừ
- [2026-11-24T11:14:24Z] [dd-adjcenter g2 24/11] XONG job Taylor_20261124_110052: DRI 15.164 / SIP 57.261 (tổ hợp) / HHS 11.593 display — nhánh session/adj-g2 b4f7b48c6 (wt-adj-g2, chưa merge) — CHỜ Mike merge
- [2026-11-24T11:14:51Z] [dd-adjcenter g3 24/11] XONG job Taylor_20261124_110054: NNC 58.914 (−3,85%), DGC 41.132 (−1,71%); nhánh session/adj-g3 (wt-adj-g3) 13a13e91f chưa merge — CHỜ Mike merge; phát hiện KTPL-flow thiếu ở DGC (cùng lớp FPT/NNC) ⇒ nên soát 5 mã còn lại
- [2026-11-24T13:27:19Z] [dd-recheck w2 job B 24/11] XONG Taylor_20261124_131354: MBB adj 20.587 (REFUTED_OPEN, mở KTPL NQ ĐHĐCĐ 2026) · DBC adj 16.439 (giữ REFUTED_OPEN, không vòng 5); wt-…b commits 345e9c815/21f9e7af7 — CHỜ Mike áp LEDGER_PROPOSAL + center_adj
- [2026-11-24T13:34:27Z] [dd-recheck w2 job A 24/11] XONG Taylor_20261124_131351: PVP adj 22.988 (MECH, 01fc032ad) · MVC adj 15.684 −3,43% skeptic REFUTED trích quỹ 11% ⇒ FULL (91bccb404); wt-…a — CHỜ Mike áp LEDGER_PROPOSAL + center_adj

- [2026-11-24T16:38:52Z] [dcf-vn-redesign V2 25/11] XONG job Taylor_20261124_160038: nhánh session/Taylor_20261124_160038 (wt-dcf-vn-redesign-20261124b) 5ae76594d chưa merge; cảnh báo đắt đạt, 'tâm giao giá' không vượt null, lens chưa phải alpha — CHỜ Mike quant-skeptic + user quyết 4 việc (bản hiển thị v3, L2 hay REL, cổng mềm cảnh báo đắt, đổi tiêu chí)
- [2026-11-25T00:41:01Z] [dcf-vn-redesign V3 25/11] XONG job Taylor_20261125_001435: nhánh session/Taylor_20261124_170355 commit 152e83c11 (wt-dcf-v3-20261125) — CHỜ Mike quant-skeptic V3 + user quyết (E/P hay mô hình cho cổng mềm; chọn ENS2 vs ENS1w)
- [2026-11-25T01:10:24Z] ĐANG DỞ: job Taylor_20261125_011012 dcf-earnings-forecast (phase1 kiểm kê+PRELOCK) | NEXT: worktree wt-dcf-earnfc-20261125d
- [2026-11-25T01:21:33Z] [dcf-earnings-forecast 25/11] XONG job Taylor_20261125_011012: nhánh session/Taylor_20261125_011012 cec37fa11 (wt-dcf-earnfc-20261125d) — D0imp tệ hơn naive, gap≈sai số earnings của D0, C2 không vượt E/P — CHỜ Mike quant-skeptic + chạy lại C sau V3.1
