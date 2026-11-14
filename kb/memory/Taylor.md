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

- [2026-11-13T10:23:05Z] ĐANG DỞ: annualization_basis_selfcheck 68 file chặn (danh sách agents/Wags/research/ann_remaining_20261113.txt) | NEXT: sau khi Wags merge ec771492b vào master -> chạy $DNA_PYEXE bin/annualization_basis_selfcheck.py --update-baseline --accept-new-debt (scan ~2+ phút, chạy nền), ghi lý do frozen/PREREG/paper-only, rc=0 + đóng bus 'Wags/selfcheck-red: mike/bin/annualization_basis_selfcheck.py'
- [2026-11-13T14:30:34Z] [live-gap-exec-A7 13/11] XONG job Taylor_20261113_134219: nhanh research/live-gap-A7-sellcap-20261113 (414468bcb) KHONG merge; tran ban khong doi DD5; thieu san ADV 2ty la nguon lech; DD5 NAV live (1-2B) ~-33% vs 50B -26 — CHO quant-skeptic + user chot neo; chua do pin1M/park0.3 o NAV nho
- [2026-11-13T15:36:37Z] ĐANG DỞ: A9 (job Taylor_20261113_153627) sua tran ban A7 -> nhanh research/live-gap-A9-sellcap-fix-20261114 tu 414468bcb | NEXT: doc REPORT A7 + verdict, sua code
- [2026-11-13T16:27:25Z] [live-gap-exec-A9 13/11] XONG job Taylor_20261113_153627: nhanh research/live-gap-A9-sellcap-fix-20261114 (8b5f7fd0d, worktree wt-livegapA7-1113 doi nhanh tai cho) KHONG merge; neo DD5 NAV live khong doi -33,2, 50B -26,22 — CHO arch-reviewer vong 2 + quant-skeptic, Mike merge
- [2026-11-14T02:02:14Z] [dd-pnj 14/11] XONG REPORT job Taylor_20261114_014836: de xuat GIU LOAI, tam 6.440 vs gia 14.950; md5 REPORT caf25da7, assumptions 4e3fce77 — CHO Mike chay fundamental-skeptic + trinh user; KHONG sua excluded_tickers
- [2026-11-14T02:21:01Z] [dd-pnj r2 14/11] XONG job Taylor_20261114_021336: 10 muc skeptic ap (muc 1 chi mot phan: CHUA MU, tam 6.440 dinh chi lam neo luat 4); NON giu; REPORT md5 0ecbc539 — CHO luot dinh gia mu that (phien moi) neu user muon neo luat 4
- [2026-11-14T02:21:04Z] ĐANG DỞ: weekly 09-13/11 đã promote nhưng delivery gate BLOCK G5 (VN-Index có cổ tức) | NEXT: điều tra G5 11-11 sau backfill Winston (VNH dup, mã V-Y), chạy vnindex_total_return --update, rồi report_delivery_gate x2 (không dựng lại build)
- [2026-11-14T02:34:48Z] [dd-pnj report 14/11] XONG job Taylor_20261114_022155: investor_report/ PDF 10tr md5 fea39145, chua gui email — CHO Mike doc kiem + user bao 'gui email'; dd_price_zones.json chua ghi
- [2026-11-14T06:57:01Z] [livermore-p0p1 14/11] XONG job Taylor_20261114_063556: 0/48 phan ky dat (G1 kich hoat), H2 R2 0.2-0.29 khong kich hoat; REPORT agents/Taylor/research/livermore_divergence_20261114/REPORT.md md5 850f0bec — CHO Mike quant-skeptic + chay kappa (tuy chon) + user chot thu hep vai/NO-GO
- [2026-11-14T07:37:53Z] [sweep 14/11] universe_pit_p3_selfcheck OPEN: cho universe_pit 13/11 dung bu (dispatch Winston bi chan quyen ghi BQ) — tu dong khi xanh; 3 cau khac CLOSED
- [2026-11-14T12:15:19Z] [dd-pat 14/11] XONG REPORT job Taylor_20261114_120425: tam 75.100 (sau CK thanh khoan 10%), gia 72.700 trong vung hop ly; REPORT md5 303958a8, assumptions d8783c94 — CHO Mike chay fundamental-skeptic; chua ghi dd_price_zones
