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

- [2026-10-30T02:54:30Z] [drift-silent-exit 30/10] XONG 0027dac67 nhanh session/drift-silent-exit-20261030 (wt-drift-silent-exit-20261030, chua merge) — CHO Mike arch-review + merge; dong crontab 00:xx khong ton tai (goi tay/agent)
- [2026-10-30T03:25:06Z] [dri-investor-report-v3 30/10] XONG job Taylor_20261030_031031: research/dd_DRI_20261027/investor_report_v3/ (19tr, chua commit) — CHO Mike doc kiem/gui email
- [2026-10-30T03:58:01Z] [erp-domestic 30/10] XONG job Taylor_20261030_034654: research/erp_domestic_20261030/ (commit 5fec4fc14) ERP noi dia 5,0 (3,4-6,5), Ke b1,1 12,3 — CHO quant-skeptic + user duyet; doi dcf_valuation phai doi ca g_T cap
- [2026-10-30T04:42:45Z] [erp-domestic-v2 30/10] XONG job Taylor_20261030_041731: research/erp_domestic_v2_20261030/ (37eb90ef5) ERP 5,42 khong ben (5,22-6,15); patch f3f756256 nhanh session/erp-domestic-dcf-20261030 (wt-erp-domestic-dcf-20261030, chua merge) — CHO quant-skeptic + user; truoc khi bat sua 2 selfcheck CCTG + dcf_earning_power.py:53
- [2026-10-30T05:37:36Z] [erp-domestic-dcf-enable 30/10] XONG job Taylor_20261030_050926: aba7502d1 (session/erp-domestic-dcf-20261030) + c8d4f77d4 mike (session/erp-domestic-dcf-ops-20261030), chua merge — CHO Mike arch-review+skeptic, merge 2 nhanh cung luot; rollback = RATE_FRAME_DEFAULT -> legacy
- [2026-10-30T07:45:57Z] [dcf-followups 30/10] XONG nhanh session/dcf-followups-20261030 (outer 35826c455, mike cfff46935, chua merge) — CHO Mike arch-review + merge 2 repo cung luot
- [2026-10-30T10:04:14Z] [oshares-live-dcf 30/10] XONG outer 0a1a16675 (session/oshares-live-20261030, wt /home/trido/wt-oshares-live-20261030) + mike 898b4fd17 (session/oshares-live-ops-20261030), chua merge — CHO arch-review+skeptic+user; bat live = quyet dinh rieng
- [2026-10-30T10:08:17Z] [dgc-dd-v2.2 30/10] XONG job Taylor_20261030_094438: dd_DGC_20261029/investor_report_v2_2/ (24tr, CHANGELOG+SELFCHECK, chua commit, chua gui) — CHO Mike chay fundamental-skeptic + quyet gui email
- [2026-10-30T10:28:44Z] [dgc-dd-v2.2-rev2 30/10] XONG job Taylor_20261030_102330 tai investor_report_v2_2 (25tr, chua commit/gui) — CHO Mike quyet gui email / rà lai
- [2026-10-30T16:08:02Z] [oshares-r2r7 30/10] XONG outer a3c2c0600 (session/oshares-r2r7-20261030) + mike 0298dd9b1 (session/oshares-r2r7-ops-20261030), chua merge — CHO arch-review+skeptic+user; bat live can caller khai price_date truoc
- [2026-10-30T16:15:40Z] [dd-NNC-20261030 30/10] XONG job Taylor_20261030_160612: research/dd_NNC_20261030/REPORT.md (chua commit) ky vong 50.300 (+7%), xap xi hop ly — CHO Mike doc/quyet investor report
- [2026-10-31T02:00:49Z] [dd-NNC-investor-31/10] XONG job Taylor_20261031_014511: REPORT.md §13 (KV 59-79k, duoi vung) + investor_report/ (14tr, chua commit, chua gui) — CHO Mike doc kiem + gui email
