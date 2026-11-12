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

- [2026-11-11T10:11:57Z] [dd-cfo-anchor 11/11] XONG job Taylor_20261111_095819: 0/9 nen trung dung dat prelock (D2 capex chuan nganh gan nhat, truot BH); thi truong KHONG thuong CFO/LN; giu V_dai — CHO Mike skeptic + user
- [2026-11-11T13:48:37Z] ĐANG DỞ job Taylor_20261111_133358 DD CST: model xong (calc/model_out.json, tâm 13.084/sau CK 12.681, giá 14.900 TRÊN tâm) | NEXT: viết REPORT.md + md5 assumptions + bus finding
- [2026-11-11T13:52:00Z] [dd-CST 11/11] XONG job Taylor_20261111_133358: tam 13.084 (sau CK 0,3ty 12.681; P10 6.316/P90 20.799), gia 14.900 TREN tam, moat NONE; assumptions_md5 74c9efbd — CHO Mike skeptic + ghi so
- [2026-11-11T14:11:30Z] [dd-cst-report 11/11] XONG job Taylor_20261111_140332: PDF 7tr + HTML tại research/dd_CST_20261111/report/, CHƯA gửi email (dry-run OK) — CHỜ user nói 'gửi email'; vùng giá ghi dd_price_zones là việc Mike
- [2026-11-12T05:26:18Z] ĐANG DỞ job Taylor_20261112_051752 DD VCP: model xong calc/model_out.json | NEXT: viết REPORT.md + bus finding
- [2026-11-12T05:29:46Z] [dd-vcp 12/11] XONG job Taylor_20261112_051752: tam 41.810 (sau CK 40.515), vung 22.502-67.385, gia BQ 11/11 37.900 sat tam; flag cho vay ca nhan 823 ty + LCTT lech + bien phe lieu Q3 — CHO Mike skeptic + ghi so
- [2026-11-12T05:54:03Z] [dd-vcp-report 12/11] XONG job Taylor_20261112_054520: PDF 7tr + HTML tại research/dd_VCP_20261112/investor_report/, CHƯA gửi email — CHỜ user nói 'gửi email'; vùng giá ghi dd_price_zones là việc Mike
- [2026-11-12T10:47:12Z] [live-gap GD0 12/11] XONG job Taylor_20261112_104201: hurdle PIT 01/07-11/11 = 2,548% (Mike 2,70% la phang 7,4%); SpaceX -6,41pp, ZaloPay -9,97 (sleeve bot -5,06) vs tiet kiem; fill-vs-open POST (09-14..11-11) -11,4bps khong cham +22; proposal .proposed CHO user duyet; GD1 la job khac
- [2026-11-12T11:17:12Z] [live-gap-p1 12/11] XONG job Taylor_20261112_104204: W0 cold −0,50%/warm +2,96% @50B (tiết kiệm +2,70%), live thua engine 2,6–6,8pp không ở W1–W2a, W2b–W5 CHƯA ĐO; control KHÔNG tái hiện 4707bcbe (drift DATA LAG phái sinh), vá sort (a) INERT — CHỜ quant-skeptic + Mike
- [2026-11-12T12:15:10Z] [live-gap-p1b 12/11] XONG job Taylor_20261112_112708: vá mergesort chữa lệch AUDIT_END (không look-ahead), pin dưới vá 23,60% vs 23,37% (CHƯA re-pin, cần duyệt); drift control = data LAG restate (events_classified), không PIT; gap live-engine SX 3,0-3,9pp / ZaloPay 2,1-2,6pp chủ yếu β T7 — CHỜ quant-skeptic + Mike; W2b-W5 chưa đo
- [2026-11-12T12:46:18Z] [live-gap-p2a 12/11] XONG job Taylor_20261112_122858: 0/90 dac trung qua FDR IS&OOS; value LAG chet OOS; OOS hits = muc placebo (hieu ung nam); H5 hurdle-tang OOS -11,6pp nhung ~3 episode; ~45% deal LAG engine vuot ADV — CHO quant-skeptic + Mike
