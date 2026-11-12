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

- [2026-11-12T05:26:18Z] ĐANG DỞ job Taylor_20261112_051752 DD VCP: model xong calc/model_out.json | NEXT: viết REPORT.md + bus finding
- [2026-11-12T05:29:46Z] [dd-vcp 12/11] XONG job Taylor_20261112_051752: tam 41.810 (sau CK 40.515), vung 22.502-67.385, gia BQ 11/11 37.900 sat tam; flag cho vay ca nhan 823 ty + LCTT lech + bien phe lieu Q3 — CHO Mike skeptic + ghi so
- [2026-11-12T05:54:03Z] [dd-vcp-report 12/11] XONG job Taylor_20261112_054520: PDF 7tr + HTML tại research/dd_VCP_20261112/investor_report/, CHƯA gửi email — CHỜ user nói 'gửi email'; vùng giá ghi dd_price_zones là việc Mike
- [2026-11-12T10:47:12Z] [live-gap GD0 12/11] XONG job Taylor_20261112_104201: hurdle PIT 01/07-11/11 = 2,548% (Mike 2,70% la phang 7,4%); SpaceX -6,41pp, ZaloPay -9,97 (sleeve bot -5,06) vs tiet kiem; fill-vs-open POST (09-14..11-11) -11,4bps khong cham +22; proposal .proposed CHO user duyet; GD1 la job khac
- [2026-11-12T11:17:12Z] [live-gap-p1 12/11] XONG job Taylor_20261112_104204: W0 cold −0,50%/warm +2,96% @50B (tiết kiệm +2,70%), live thua engine 2,6–6,8pp không ở W1–W2a, W2b–W5 CHƯA ĐO; control KHÔNG tái hiện 4707bcbe (drift DATA LAG phái sinh), vá sort (a) INERT — CHỜ quant-skeptic + Mike
- [2026-11-12T12:15:10Z] [live-gap-p1b 12/11] XONG job Taylor_20261112_112708: vá mergesort chữa lệch AUDIT_END (không look-ahead), pin dưới vá 23,60% vs 23,37% (CHƯA re-pin, cần duyệt); drift control = data LAG restate (events_classified), không PIT; gap live-engine SX 3,0-3,9pp / ZaloPay 2,1-2,6pp chủ yếu β T7 — CHỜ quant-skeptic + Mike; W2b-W5 chưa đo
- [2026-11-12T12:46:18Z] [live-gap-p2a 12/11] XONG job Taylor_20261112_122858: 0/90 dac trung qua FDR IS&OOS; value LAG chet OOS; OOS hits = muc placebo (hieu ung nam); H5 hurdle-tang OOS -11,6pp nhung ~3 episode; ~45% deal LAG engine vuot ADV — CHO quant-skeptic + Mike
- [2026-11-12T13:05:33Z] [live-gap-p1c 12/11] XONG job Taylor_20261112_122855: park khớp lịch live => DẤU GAP ĐẢO, live thắng engine +4,35..+4,65pp (engine -8,2/-7,3%); beta gần cân, gap là alpha (engine tín hiệu alpha đổi dấu theo park); live BAL+LAG ~5% NAV => không phải phép thử BAL/LAG; tie-break sd 0,35pp CAGR — CHỜ quant-skeptic + Mike; W2b-W5 chưa đo
- [2026-11-12T13:28:37Z] [live-gap-p2b 12/11] XONG job Taylor_20261112_125912: 0 dac trung ben IS->OOS tren tap giao dich duoc (placebo 0/1 vs that 0), log_adv20/H1-IS mat; H5 theo episode PIT dep1m -1,18pp tho/-0,37 khu nam, 7 episode => khong ket luan; lực thấp rho<0,25 — CHO quant-skeptic + Mike
- [2026-11-12T13:40:44Z] [live-gap-p3 12/11] XONG job Taylor_20261112_132954: 0/6 bien thoi diem qua PREREG (MDE 14-110pp, ~5 cua so/era); baseline P0 thang tiet kiem 12T 77,6% (3T 62%), thua 2019/2022; ref DT5G CRISIS/BEAR->tiet kiem CAGR ~= engine, DD -12,6 vs -17,1 (bao hiem, khong ung vien); sizing w 0,4/0,6/0,8 cho DD p5 -10/-15/-20 — CHO quant-skeptic + Mike
- [2026-11-12T16:26:49Z] [live-gap-exec-D 12/11] XONG job Taylor_20261112_162001: P(thang 12T) 77,6-84,6% (pin0/pin1M; -1,5pp: 74-82%), CI N_eff 45-98%; chinh sach DT5G->tiet kiem 1T ton 0,9-2,7pp CAGR, DD +2,4-4,5pp (bao hiem); D2 0 dac trung qua, MDE80 BAL 0,5/LAG 0,3 — CHO quant-skeptic + Mike
- [2026-11-12T16:32:39Z] [live-gap-E 12/11] XONG job Taylor_20261112_151839/162006: waterfall dong, du +1,4..2,2pp (T9, gia thuyet ro park live/CAPIT size chua do); W3 fills_booked thieu lenh ban DISC (dung so); pin 23,37 trong phan phoi tie-break — CHO quant-skeptic + Mike
- [2026-11-12T17:17:00Z] [live-gap-exec-A 13/11] XONG job Taylor_20261112_162004: nhanh feat/live-gap-exec-A-20261112 (efdb282bd) KHONG merge; dai moi 23,39/26,77 (seed mean 26,30), DD5 -27,6/-25,0 vs neo -25,2 — CHO quant-skeptic + user; registry+6 pin chua commit
- [2026-11-12T17:49:03Z] [live-gap-exec-B 13/11] XONG job Taylor_20261112_172358: nhanh feat/savings-row-20261112 (9246cd93e) KHONG merge; savings selfcheck 56 PASS; report_return_gate_selfcheck FAIL co san tren master; report_v2_selfcheck timeout chua ket luan; template/gate chua sua — CHO user duyet + Wendy ve cach dien dat
- [2026-11-12T18:43:29Z] [live-gap-exec-A2 13/11] XONG job Taylor_20261112_181209: lo NULL khong phai nguyen nhan (L2 sach pit 23,32/26,85, DD5 -27,7/-25,3); chenh L1->L2 = fill ao ma ADV<=0; de xuat LAG_ADV_SRC=pit mac dinh — CHO quant-skeptic + user; nhanh 4f7609c34/770393ce2 KHONG merge
- [2026-11-12T19:03:34Z] [live-gap-exec-B2 13/11] XONG job Taylor_20261112_181211: nhanh feat/savings-row-20261112 (418667a32) KHONG merge; v2 selfcheck PASS 177 x3; anchor_warning siet, gate crosscheck cot tiet kiem — CHO user/Wendy duyet cau chu+thue+ten cot template
