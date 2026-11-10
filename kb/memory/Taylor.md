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

- [2026-11-09T07:47:24Z] [dd-lagcand GAS 09/11] XONG job Taylor_20261109_073604: tam 46.488 (P10 39.010/P90 55.150) TREN vung @74.100 (r ngu y 6,2%); WARNING free float 4,24%; CHO Mike skeptic + ghi so
- [2026-11-09T07:47:55Z] [dd-lagcand CSV 09/11] XONG job Taylor_20261109_073602: TREN vung @22.600 (tam 17.273 P10 12.739 P90 21.885); surprise = gia axit tam thoi; CHO Mike skeptic + ghi so
- [2026-11-09T08:33:26Z] [dd-lagcand MSB r2 09/11] XONG job Taylor_20261109_083128: tam 12.739->13.018 (P10 9.675/P90 16.373) TRONG bien tren @16.350, luat4 khong dat; CHO Mike ghi so
- [2026-11-09T08:34:06Z] [dd-lagcand CSV r2 09/11] XONG job Taylor_20261109_083124: tam 17.273->20.717 (P10 15.825/P90 25.470) TRONG @22.600, luat4 khong dat; CHO Mike ghi so
- [2026-11-09T08:35:39Z] [dd-lagcand GAS r2 09/11] XONG job Taylor_20261109_083126: tam 46.488->50.146 (P10 43.327/P90 57.840) TREN vung @74.100; chua kiem: TM du phong 343, ly do mien nhiem; CHO Mike ghi so
- [2026-11-10T03:54:07Z] [dd-dilution r4 10/11] XONG job Taylor_20261110_034232: HHS quyen 60%@10.000+co tuc CP 7% CHUA thuc hien, nhan DUOI khong doi (ex du 11.615/P10 10.711, TERP 9.346); SCL ex 28.000 > P90 ex 25.681 (5ty) TREN khong doi; ledger de xuat trong research/dd_dilution_update_20261110/SUMMARY.md; CHO Mike skeptic + ghi so
- [2026-11-10T05:48:44Z] ĐANG DỞ job Taylor_20261110_053022 BAL edge gate: worktree wt-bal-edge-gate-20261110 (+mike wt agents/Taylor/wt-mike-bal-edge-20261110), selfcheck 65/0; NEXT: kiểm cắt cụt run e0930, bootstrap state, doc kb/projects/bal-edge-monthly-gate-20261110.md, commit, bus finding
- [2026-11-10T06:02:44Z] CHỜ Mike arch-review BAL edge gate: code d0e01e21e (wt-bal-edge-gate-20261110) + mike c5c1e5374; khi merge phải chạy --bootstrap + cài cron (cần duyệt)
- [2026-11-10T06:16:34Z] CHỜ Mike duyệt BAL edge gate VÒNG 2: code f103ae0fa (wt-bal-edge-gate-20261110) + mike 8f9250363; merge xong phải --bootstrap + cài cron (cần duyệt)
- [2026-11-10T06:26:28Z] [bal-edge-monthly-gate 10/11] XONG job Taylor_20261110_053025: cong thang BAL HAI CAGR -2,62/-2,76pp (P>0 0,01), Calmar khong phan biet, DD tot hon = giam exposure (placebo); CHO quant-skeptic + user quyet; worktree wt-balgate-1110 giu de skeptic tai lap
- [2026-11-10T08:30:26Z] [book-regime-fit 10/11] XONG job Taylor_20261110_082023: BAL binh thuong (beta), LAG lech duoi trai chua du goi gay, 0/32 bien timing; CHO quant-skeptic; next de xuat: per-event LAG
- [2026-11-10T09:36:02Z] [2026-11-10] [book-regime-fit sua theo skeptic] XONG job Taylor_20261110_091634: gap gia pkl that, LAG -12,36% (A+codtuc), duoi trai con R3park0, yeu park70; CHO skeptic lan 2; khuyen owner pipeline them check so ma/phien
