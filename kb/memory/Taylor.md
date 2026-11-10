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

- [2026-11-10T03:54:07Z] [dd-dilution r4 10/11] XONG job Taylor_20261110_034232: HHS quyen 60%@10.000+co tuc CP 7% CHUA thuc hien, nhan DUOI khong doi (ex du 11.615/P10 10.711, TERP 9.346); SCL ex 28.000 > P90 ex 25.681 (5ty) TREN khong doi; ledger de xuat trong research/dd_dilution_update_20261110/SUMMARY.md; CHO Mike skeptic + ghi so
- [2026-11-10T05:48:44Z] ĐANG DỞ job Taylor_20261110_053022 BAL edge gate: worktree wt-bal-edge-gate-20261110 (+mike wt agents/Taylor/wt-mike-bal-edge-20261110), selfcheck 65/0; NEXT: kiểm cắt cụt run e0930, bootstrap state, doc kb/projects/bal-edge-monthly-gate-20261110.md, commit, bus finding
- [2026-11-10T06:02:44Z] CHỜ Mike arch-review BAL edge gate: code d0e01e21e (wt-bal-edge-gate-20261110) + mike c5c1e5374; khi merge phải chạy --bootstrap + cài cron (cần duyệt)
- [2026-11-10T06:16:34Z] CHỜ Mike duyệt BAL edge gate VÒNG 2: code f103ae0fa (wt-bal-edge-gate-20261110) + mike 8f9250363; merge xong phải --bootstrap + cài cron (cần duyệt)
- [2026-11-10T06:26:28Z] [bal-edge-monthly-gate 10/11] XONG job Taylor_20261110_053025: cong thang BAL HAI CAGR -2,62/-2,76pp (P>0 0,01), Calmar khong phan biet, DD tot hon = giam exposure (placebo); CHO quant-skeptic + user quyet; worktree wt-balgate-1110 giu de skeptic tai lap
- [2026-11-10T08:30:26Z] [book-regime-fit 10/11] XONG job Taylor_20261110_082023: BAL binh thuong (beta), LAG lech duoi trai chua du goi gay, 0/32 bien timing; CHO quant-skeptic; next de xuat: per-event LAG
- [2026-11-10T09:36:02Z] [2026-11-10] [book-regime-fit sua theo skeptic] XONG job Taylor_20261110_091634: gap gia pkl that, LAG -12,36% (A+codtuc), duoi trai con R3park0, yeu park70; CHO skeptic lan 2; khuyen owner pipeline them check so ma/phien
- [2026-11-10T11:02:22Z] CHỜ arch-review vòng 2 lagcache: nhánh session/lagcache-1110 49e70d6df; bf13v2 (research/book_regime_fit_20261110/backfill13_v2, px md5 4974943…) --apply CHỈ sau duyệt; khi merge sửa mike/bin/asof_label_selfcheck.py:46 777→780
- [2026-11-10T13:04:35Z] ĐANG DỞ job Taylor_20261110_125453 DD VGS: model khoa md5 191bb785, SUMMARY.json xong; NEXT: viet REPORT.md + bus finding
- [2026-11-10T13:07:37Z] [dd-VGS 10/11] XONG job Taylor_20261110_125453: tam 26.520 sau CK5ty (P10 19.165/P90 34.314), gia 19.300 TRONG sat P10, luat4 dat; nua gia tri la lien ket+Legend City; CHO Mike skeptic + ghi so
- [2026-11-10T13:08:02Z] CHỜ Mike skeptic+arch-review lag-cache-adjusted: code b16d7487d (wt-lagadj-1110) + mike 91a911827; R3 +0,92/+0,78pp vượt sàn nhiễu ⇒ user quyết re-pin; apply pkl + chạy refresh tay chỉ sau duyệt
- [2026-11-10T13:20:38Z] [2026-11-10] dd-VGS r2 XONG job Taylor_20261110_131720: tam 26.778 (sau CK 1ty 26.526, P10 19.393/P90 34.722), gia 19.300 DUOI mong manh, luat4 dat; CHO Mike skeptic lan 2 + ghi so
- [2026-11-10T13:41:29Z] ĐANG DỞ job Taylor_20261110_132044 lagadj r2: A1 4 chân r3z xong (Δ pin0 -0,04/pin1M -0,37 ⇒ KHÔNG re-pin), pkl v2+pt v2 xong; code wt-lagadj-1110 sửa B uncommitted; NEXT: selfcheck, B5/B9/B10, doc, tách commit, bus
- [2026-11-10T13:53:11Z] CHỜ Mike duyệt lag-cache-adjusted r2: code fd29f496a (wt-lagadj-1110) + mike edb3ffba0; KHÔNG re-pin R3; user quyết 4 mục trong doc §6; không merge/apply/cron trước duyệt
- [2026-11-10T15:28:07Z] CHỜ Mike: lagadj r3 code cf21463b9 + mike eecd82ae7 + repin branch feat/repin-mirror-live-20261110 @307593815; chờ quant-skeptic, user quyết re-pin + neo DD -28,0 + TTL delist
