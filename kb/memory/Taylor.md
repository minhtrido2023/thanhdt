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

- [2026-10-26T01:34:42Z] [dd-NNC 10-26] XONG job Taylor_20261026_012529: NON (khong fear-state, dinh chu ky, PB1,59); weighted 62,8k vs 47,6k. REPORT research/dd_NNC_20261026/. Meo: BCTC scan -> pip --target /tmp/pdflib pypdf, trich anh trang roi Read anh
- [2026-10-26T04:55:12Z] [dd-template 10-26] XONG job Taylor_20261026_045054: mau DD + khoi chu ky mu o research/dd_template_20261026/ (chua commit) — CHO Mike/user duyet so dd_cycle_reads.md + cong; chay lai mu 5 ma = job khac
- [2026-10-26T04:59:04Z] [sector-frames 10-26] XONG job Taylor_20261026_045056: khung bank/BDS/hoa chat o research/sector_frames_20261026/; CHAM du bao F-CHEM-2 <=2027-02-28, F-BANK/RE/CHEM-1 ngay 2027-05-20
- [2026-10-26T05:03:01Z] [dd-blind-DDV 10-26] XONG job Taylor_20261026_045654: NON khong doi, blind=no (mau tu lo verdict DDV) — de xuat lam sach README/TEMPLATE truoc khi chay mu lai
- [2026-10-26T05:04:08Z] [dd-blind-SAS 10-26] XONG job Taylor_20261026_045658: NON=NON, blind no (README §4 lo verdict); research/dd_blind_SAS_20261026/
- [2026-10-26T05:04:47Z] [dd-blind-NNC 10-26] XONG job Taylor_20261026_045700: NON=NON, blind:no (WM+README lo verdict cu); khoi mu sot HTM/Tam Lap/MVC -> mau buoc 1 can doc CDKT BCTC Q-1 goc. research/dd_blind_NNC_20261026/
- [2026-10-26T05:10:44Z] [dd-blind-SZL 10-26] XONG job Taylor_20261026_045656: NON=NON, blind:no (WebSearch lo so Q3). Meo: chay mu phai cam WebSearch tu do o buoc 1 (tom tat tu chen so quy Q); mau E 'trung vi LN' lech xuong voi annuity — de xuat sua mau, CHO Mike
- [2026-10-26T05:46:41Z] [dd-blind2-FPT 10-26] XONG buoc 1 job Taylor_20261026_054003: md5 3c30d4ba, du bao NP me Q3/26 >=2680 ty p0,75 cham 2026-11-07; blind:no (WebSearch lo khuyen nghi CTCK Q2). Buoc 2 = job khac
- [2026-10-26T05:47:27Z] [dd-blind2-DRI 10-26] XONG buoc 1 job Taylor_20261026_054006: CYCLE_BLOCK md5 15bd430e khoa 12:47 ICT, blind yes; du bao bien LNST Q3/26 >=27% p0,70 cham 2026-11-09 — buoc 2 la job khac
- [2026-10-26T05:48:22Z] [dd-blind2-TV1 10-26] buoc 1 KHOA md5 4409305f (research/dd_blind2_TV1_20261026/); F: bien gop Q3/26 <33,0% p0.65, cham 2026-11-09 — buoc 2 la job khac
- [2026-10-26T06:44:41Z] [dgc-q3-forecast 10-26] KHOA md5 d6ea39f4 (research/dgc_q3_forecast_20261026/): LNST me Q3/26 320 ty, 50% [270,370], 80% [215,425]; cham khi DGC cong bo (du kien 27/10-14/11)
- [2026-10-26T08:18:08Z] [commodity-te 10-26] XONG job Taylor_20261026_075337 @cff2bc5c3: TE nowcast KQKD IC 0,45 (thi truong da dinh gia), B3 13 trial khong qua cong, khong chinh model — CHO Mike/user: PREREG forward LAG surprise-decomp + xin bq_admin feed APT/xut/P4/BDTI
- [2026-10-26T09:47:02Z] [lag-capacity-floor D 10-26] XONG job Taylor_20261026_074918 @456b07baf (chua merge): band 50 ty ~11,7-18,1/14,6-20,8, CHINH D3AK10 18,08/20,82; lo ro slot LAG (inflight vo hinh tran 12) ~3pp, pin cung huong -2,2/-2,6 — CHO verify live slot + ca partial SCL/VPB plan 27/10
- [2026-10-26T10:05:01Z] [commodity-nowcast-block 10-26] XONG job Taylor_20261026_095926 @920bb4219 (wt-commodity-nowcast, chua merge) — CHO arch-reviewer + Mike merge
- [2026-10-26T10:22:53Z] [commodity-sue-decomp 10-26] XONG job Taylor_20261026_095928 @a1547392c (chua merge, wt-commodity-sue-decomp-20261026): PREREG-4 md5 6c5642c1; CHO Mike goi quant-skeptic + duyet cron (CRON_PROPOSAL.md) + merge. Luu y: S2 (SUE live) dIC lich su -0,012
- [2026-10-26T16:13:28Z] [p4-sulfur 10-26] XONG job Taylor_20261026_160657: research/commodity_p4_sulfur_20261026/ (chua commit) — P4 nowcast DGC gay tu 2024, 17 trial GD khong ung vien; CHO Winston sua registry key phosphorus->phosphate_rock_cny
- [2026-10-26T16:41:53Z] [nowcast-p4 10-26] XONG job Taylor_20261026_163838 @c0ae8de0a nhánh feat/nowcast-p4-20261026 (chưa merge) — CHO Mike arch-review+merge; Winston thêm yellow_phosphorus vào freshness monitor
- [2026-10-26T16:49:40Z] [nowcast-p4 vòng 2 10-26] XONG @ac2077912 nhánh feat/nowcast-p4-20261026 (chưa merge) — CHỜ arch-review vòng 2 + Mike merge
