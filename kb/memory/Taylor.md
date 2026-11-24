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

- [2026-11-24T03:24:18Z] [dd-forward 24/11] XONG job Taylor_20261124_031944: nhánh feat/dd-forward-outcome-20261124 (526879fef) — CHỜ Mike duyệt diff + cài cron đề xuất; mốc đánh giá 2027-03-31
- [2026-11-24T03:26:22Z] [dd-history-label E 24/11] XONG job Taylor_20261124_031942: nhánh session/Taylor_20261124_031942 commit 1784cbafb (chưa merge) — CHỜ Mike duyệt diff + quyết cờ 'proxy lệch DD' (k ngoài [0,5;2])
- [2026-11-24T03:46:22Z] [E2 dd-history-label v2 24/11] XONG job Taylor_20261124_034215: nhánh session/Taylor_20261124_034215 — CHỜ Mike duyệt diff + merge; SIP caveat lệch số skeptic, cần skeptic xác nhận cách đo
- [2026-11-24T04:00:55Z] [CK holding v2 24/11] XONG job Taylor_20261124_032640: N=12 trung vi 6,5% (IQR -19..38%), khong du lam base HHS -> khuyen 0% + dai 0/6.5/23/38% — CHO Mike quant-skeptic + user chot Viec 1
- [2026-11-24T04:56:41Z] [CK holding v3 24/11] XONG job Taylor_20261124_041821: N=13 trung vi 1,5% (ex-KSF 5,6%), dai trung tam -12/1,5/+23% (34,9pp, KHONG dat 20pp) — CHO Mike quant-skeptic + commit + user chot base HHS
- [2026-11-24T06:09:21Z] [CK holding v4 24/11] XONG job Taylor_20261124_053704: hull(a)u(d) -11.9/1.5/+14.4% (26.3pp, KHONG dat), de xuat HHS 0%/+6/+14/+37 khop skeptic — CHO Mike quant-skeptic vong cuoi + commit + user chot dai
- [2026-11-24T08:16:37Z] [CK holding v5 24/11] XONG job Taylor_20261124_073243: hien tai 19,7% (PAN), median -3,2% N=12, hull 36,5pp KHONG dat; +6% mat cho dua — CHO Mike skeptic phan doi + commit + user chot dai
- [2026-11-24T09:53:16Z] [dd-recheck pilot HHS 24/11] XONG job Taylor_20261124_094353: worktree wt-1574720404268912680 commit bd92fae86, tam khong doi 10.805, skeptic r1 REFUTED (CK base cu) — CHO Mike duyet quy trinh + user chot CK holding truoc rev8/fan-out 7 ma
- [2026-11-24T10:13:25Z] [dd-recheck nhóm A 24/11] XONG job Taylor_20261124_095514: VGS/TCH/DRI/SIP tâm 0%, skeptic r1 đều INCONCLUSIVE, 4 LEDGER_PROPOSAL REFUTED_OPEN (DRI/SIP hạ từ CONFIRMED backfill) — CHỜ Mike áp sổ + xử lý TRIM_DD xoá đầu vào calc khoá
- [2026-11-24T10:25:24Z] [dd-recheck nhóm B 24/11] XONG job Taylor_20261124_095517: FPT/NNC/DGC tâm 0%, cả 3 skeptic r1 INCONCLUSIVE (thiếu hạng mục), worktree wt-1574720404268912680b commits d2fe430f1/97ef0a396/5d276f5e6 — CHỜ Mike duyệt LEDGER_PROPOSAL + quyết FULL
- [2026-11-24T10:51:25Z] [dd-adjcenter pilot FPT 24/11] XONG job Taylor_20261124_104632: tâm adj 56.204 (−1,93%), nhánh session/adjpilot 0d52b34ec (wt-adjpilot, chưa merge) — CHỜ Mike chốt 3 sửa PREREG (C+, dải p×m, luật r ngoài Σ) trước fan-out 7 mã
- [2026-11-24T11:11:59Z] [dd-adjcenter g1 24/11] XONG job Taylor_20261124_110049: FPT 55.668 / TCH 15.152 / VGS 25.148 (nhánh session/adj-g1, wt-adj-g1, chưa merge) — CHỜ Mike merge + skeptic; VGS phát hiện tồn quỹ KTPL 36,1 tỷ chưa trừ
- [2026-11-24T11:14:24Z] [dd-adjcenter g2 24/11] XONG job Taylor_20261124_110052: DRI 15.164 / SIP 57.261 (tổ hợp) / HHS 11.593 display — nhánh session/adj-g2 b4f7b48c6 (wt-adj-g2, chưa merge) — CHỜ Mike merge
- [2026-11-24T11:14:51Z] [dd-adjcenter g3 24/11] XONG job Taylor_20261124_110054: NNC 58.914 (−3,85%), DGC 41.132 (−1,71%); nhánh session/adj-g3 (wt-adj-g3) 13a13e91f chưa merge — CHỜ Mike merge; phát hiện KTPL-flow thiếu ở DGC (cùng lớp FPT/NNC) ⇒ nên soát 5 mã còn lại
- [2026-11-24T13:27:19Z] [dd-recheck w2 job B 24/11] XONG Taylor_20261124_131354: MBB adj 20.587 (REFUTED_OPEN, mở KTPL NQ ĐHĐCĐ 2026) · DBC adj 16.439 (giữ REFUTED_OPEN, không vòng 5); wt-…b commits 345e9c815/21f9e7af7 — CHỜ Mike áp LEDGER_PROPOSAL + center_adj
- [2026-11-24T13:34:27Z] [dd-recheck w2 job A 24/11] XONG Taylor_20261124_131351: PVP adj 22.988 (MECH, 01fc032ad) · MVC adj 15.684 −3,43% skeptic REFUTED trích quỹ 11% ⇒ FULL (91bccb404); wt-…a — CHỜ Mike áp LEDGER_PROPOSAL + center_adj
- [2026-11-24T14:39:15Z] [dcf-vn-redesign 24/11] XONG job Taylor_20261124_140534: nhánh session/Taylor_20261124_140534 (wt-dcf-vn-redesign-20261124) 6937c5cc2 chưa merge; không mô hình mù giá nào đạt cắt-giá 36T, đề xuất RIM-VN 2 lớp — CHỜ Mike quant-skeptic + Winston kiểm mã huỷ niêm yết + user quyết tâm hiển thị có dùng giá quá khứ

- [2026-11-24T16:01:36Z] ĐANG DỞ [dcf-vn-redesign V2, job Taylor_20261124_160038]: worktree wt-dcf-vn-redesign-20261124b nhánh session/Taylor_20261124_160038, thư mục agents/Taylor/research/dcf_vn_redesign_20261124b/ | NEXT: kiểm kê dữ liệu → PRELOCK → sửa 9 lỗi skeptic → họ mô hình đa proxy → REPORT + bus (a)(b)(c)(d)
