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

- [2026-10-29T04:05:48Z] [dd-PVT 10-29] XONG job Taylor_20261029_035644: NON @21.300 san, FV ky vong ~18,0k, rerun DD <=15,3k; research/dd_PVT_20261029/ (chua commit) — CHO Mike goi fundamental-skeptic; cau hoi #1: do lon tac dong TT99 dry-dock
- [2026-10-29T05:33:20Z] [dd-SCL 10-29] XONG job Taylor_20261029_052549: NON @31.100 cum (TERP 28.612), FV ~25,5k; research/dd_SCL_20261029/ (chua commit) — CHO Mike goi skeptic; user can chon xu ly quyen mua truoc 06/11
- [2026-10-29T05:37:11Z] [dgc-val r6 29/10] XONG job Taylor_20261029_053128: dai A 29.817 / B 34.695 (C 36.663 chi do nhay, D r5 40.302); cau noi KHONG dung duoc, bien r4; CHO Mike goi fundamental-skeptic; mo: du phong 200 (R1/R2), 48,23 LCTT = thanh ly TSCD
- [2026-10-29T06:15:19Z] [scl-investor-report 29/10] XONG job Taylor_20261029_055834: research/dd_SCL_20261029/investor_report/ (md+pdf 14tr+html+figs, chua commit) — CHO Mike gui email/duyet
- [2026-10-29T07:42:07Z] [capraise 29/10] XONG @251ebcdaf nhanh session/capraise-20261029 (wt-capraise-20261029, chua merge) — CHO Mike arch-review + user duyet merge; kb/cron_registry dong 109 can sua mo ta
- [2026-10-29T07:50:37Z] [pvp-investor-report 29/10] XONG job Taylor_20261029_074021: research/dd_PVP_20261029/investor_report/ (md+pdf 14tr+html+10 figs, chua commit); REPORT.md v2.1 7 sua skeptic — CHO Mike doc kiem/gui email
- [2026-10-29T09:42:45Z] [dri-investor-report 29/10] XONG job Taylor_20261029_093106: research/dd_DRI_20261027/investor_report/ (md+pdf 17tr+html+10 figs, chua commit) — CHO Mike doc kiem/gui email
- [2026-10-29T10:50:01Z] [dgc-val r7 29/10] XONG job Taylor_20261029_104456: NON (discriminator), A7 32.182/B7 37.060, gia 32.900 trong dai; de xuat HARD ABANDON 10.000cp ZaloPay (35,8% NAV) — CHO Mike goi skeptic vong 2 + user xac nhan doi nhan
- [2026-10-29T10:55:25Z] [dri-investor-report-v2 29/10] XONG job Taylor_20261029_104401: research/dd_DRI_20261027/investor_report_v2/ (md+pdf 20tr+html+21 figs, subject o EMAIL_SUBJECT.txt, chua commit) — CHO Mike doc kiem/gui email
- [2026-10-29T11:04:03Z] [dgc-val r8 29/10] XONG job Taylor_20261029_105958: agents/Taylor/research/dgc_valuation_20261029_r8/ (chua commit) — CHO user chon nhan P1/P2 + phuong an giam tap trung ZaloPay (a-d)
- [2026-10-29T11:47:21Z] [dgc-val r9 29/10] XONG job Taylor_20261029_113514: R2-R1 6.065 = 100% bien vinh vien (0 tu khoan 200); r8 263d/cp SAI (1.516 neu lap mai); bang N; khong base case — CHO Mike/skeptic + hoi DGC ban chat du phong
- [2026-10-29T12:01:48Z] [dgc-val r10 29/10] XONG job Taylor_20261029_115813: research/dgc_valuation_20261029_r10/ (chua commit); 100ty/quy vinh vien=-6065; Q4 tach 217 (R2 N=0 36880, r4 32399); khong base case — CHO Mike/skeptic vong 3; mo: T7 cong ty con, khau tru thue (legal-vn)
- [2026-10-29T12:23:18Z] [dgc-investor-report 29/10] XONG job Taylor_20261029_121056: research/dd_DGC_20261029/investor_report/ (md+pdf 19tr+html+13 figs, chua commit) — CHO Mike doc kiem/gui email
- [2026-10-29T13:27:35Z] [dgc-val r11 29/10] XONG job Taylor_20261029_131656: research/dgc_valuation_20261029_r11/ (chua commit); NS trong A7 +2.163d/cp, bottom-up NPAT2030 -182/217/479, khong doi gia dinh chinh; 100ty/quy vinh vien = khong tien le — CHO Mike/skeptic; mo: von 2.400 vs 2.900, gia dan xuat clo/H3PO3 [UL]
- [2026-10-29T13:37:30Z] [manual-deviation 29/10] XONG e11fab9bd nhanh session/manual-deviation-20261029 (wt-manual-deviation-20261029, chua merge) — CHO Mike arch-review + user; sau merge seed so that (add --verify 2 lenh SCL) + chay lai NAV 29/10
- [2026-10-29T13:45:40Z] [dgc-ke 29/10] XONG job Taylor_20261029_133456: Ke 14,9% giua vung 12,2-16,7% (PREREG tam 15,8%, thi truong 13,1%); rf trung tam 6,75 building-block — CHO Mike/user; mo: dcf_valuation g_T=rf 7,4% can nghien cuu rieng
- [2026-10-29T13:54:56Z] [manual-deviation vòng 2 29/10] XONG @83da1791f nhanh session/manual-deviation-20261029 (chưa merge) — CHO Mike arch-review vòng 3 + user; pageIndex=1-based là giả định chưa kiểm DNSE thật
