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

- [2026-10-25T17:25:49Z] ĐANG DỞ job Taylor_20261025_172538: lag-capacity S1(ΔIS/ΔOOS)/S2(đọc code live defer vs bỏ)/S3(trần KL mở cửa + slippage) trên wt-lag-capacity-floor-20261025 | NEXT: đọc REPORT_R/PREREG_R/out_R_metrics.csv
- [2026-10-25T17:34:56Z] ĐANG DỞ job Taylor_20261025_172538: S1 3cdefe417 + S2 fe910d1e5 xong (bus); S3 batch 24 run nền từ 00:33 (wt-lag-capacity-floor, logs/run_batch_S.log), PREREG_S 1e909f719 | NEXT: analyze_S.py → REPORT_S §S3 → bus S3 + 'S ket luan'
- [2026-10-25T18:23:10Z] [lag-capacity-floor S 10-26] XONG job Taylor_20261025_172538 @148b84685 (chua merge): band 50 ty ~11,7-20,7/14,6-23,8, trung tam 18,5-20,7/21,2-23,8, chi phi IS -4,2..-4,4pp — CHO Mike/user: co chay bien the doi 3 phien + cong gia anchor khong
- [2026-10-26T01:34:42Z] [dd-NNC 10-26] XONG job Taylor_20261026_012529: NON (khong fear-state, dinh chu ky, PB1,59); weighted 62,8k vs 47,6k. REPORT research/dd_NNC_20261026/. Meo: BCTC scan -> pip --target /tmp/pdflib pypdf, trich anh trang roi Read anh
- [2026-10-26T04:55:12Z] [dd-template 10-26] XONG job Taylor_20261026_045054: mau DD + khoi chu ky mu o research/dd_template_20261026/ (chua commit) — CHO Mike/user duyet so dd_cycle_reads.md + cong; chay lai mu 5 ma = job khac
- [2026-10-26T04:59:04Z] [sector-frames 10-26] XONG job Taylor_20261026_045056: khung bank/BDS/hoa chat o research/sector_frames_20261026/; CHAM du bao F-CHEM-2 <=2027-02-28, F-BANK/RE/CHEM-1 ngay 2027-05-20
- [2026-10-26T05:03:01Z] [dd-blind-DDV 10-26] XONG job Taylor_20261026_045654: NON khong doi, blind=no (mau tu lo verdict DDV) — de xuat lam sach README/TEMPLATE truoc khi chay mu lai
- [2026-10-26T05:04:08Z] [dd-blind-SAS 10-26] XONG job Taylor_20261026_045658: NON=NON, blind no (README §4 lo verdict); research/dd_blind_SAS_20261026/
- [2026-10-26T05:04:47Z] [dd-blind-NNC 10-26] XONG job Taylor_20261026_045700: NON=NON, blind:no (WM+README lo verdict cu); khoi mu sot HTM/Tam Lap/MVC -> mau buoc 1 can doc CDKT BCTC Q-1 goc. research/dd_blind_NNC_20261026/
- [2026-10-26T05:10:44Z] [dd-blind-SZL 10-26] XONG job Taylor_20261026_045656: NON=NON, blind:no (WebSearch lo so Q3). Meo: chay mu phai cam WebSearch tu do o buoc 1 (tom tat tu chen so quy Q); mau E 'trung vi LN' lech xuong voi annuity — de xuat sua mau, CHO Mike
- [2026-10-26T05:46:41Z] [dd-blind2-FPT 10-26] XONG buoc 1 job Taylor_20261026_054003: md5 3c30d4ba, du bao NP me Q3/26 >=2680 ty p0,75 cham 2026-11-07; blind:no (WebSearch lo khuyen nghi CTCK Q2). Buoc 2 = job khac
- [2026-10-26T05:47:27Z] [dd-blind2-DRI 10-26] XONG buoc 1 job Taylor_20261026_054006: CYCLE_BLOCK md5 15bd430e khoa 12:47 ICT, blind yes; du bao bien LNST Q3/26 >=27% p0,70 cham 2026-11-09 — buoc 2 la job khac
