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

- [2026-11-12T13:28:37Z] [live-gap-p2b 12/11] XONG job Taylor_20261112_125912: 0 dac trung ben IS->OOS tren tap giao dich duoc (placebo 0/1 vs that 0), log_adv20/H1-IS mat; H5 theo episode PIT dep1m -1,18pp tho/-0,37 khu nam, 7 episode => khong ket luan; lực thấp rho<0,25 — CHO quant-skeptic + Mike
- [2026-11-12T13:40:44Z] [live-gap-p3 12/11] XONG job Taylor_20261112_132954: 0/6 bien thoi diem qua PREREG (MDE 14-110pp, ~5 cua so/era); baseline P0 thang tiet kiem 12T 77,6% (3T 62%), thua 2019/2022; ref DT5G CRISIS/BEAR->tiet kiem CAGR ~= engine, DD -12,6 vs -17,1 (bao hiem, khong ung vien); sizing w 0,4/0,6/0,8 cho DD p5 -10/-15/-20 — CHO quant-skeptic + Mike
- [2026-11-12T16:26:49Z] [live-gap-exec-D 12/11] XONG job Taylor_20261112_162001: P(thang 12T) 77,6-84,6% (pin0/pin1M; -1,5pp: 74-82%), CI N_eff 45-98%; chinh sach DT5G->tiet kiem 1T ton 0,9-2,7pp CAGR, DD +2,4-4,5pp (bao hiem); D2 0 dac trung qua, MDE80 BAL 0,5/LAG 0,3 — CHO quant-skeptic + Mike
- [2026-11-12T16:32:39Z] [live-gap-E 12/11] XONG job Taylor_20261112_151839/162006: waterfall dong, du +1,4..2,2pp (T9, gia thuyet ro park live/CAPIT size chua do); W3 fills_booked thieu lenh ban DISC (dung so); pin 23,37 trong phan phoi tie-break — CHO quant-skeptic + Mike
- [2026-11-12T17:17:00Z] [live-gap-exec-A 13/11] XONG job Taylor_20261112_162004: nhanh feat/live-gap-exec-A-20261112 (efdb282bd) KHONG merge; dai moi 23,39/26,77 (seed mean 26,30), DD5 -27,6/-25,0 vs neo -25,2 — CHO quant-skeptic + user; registry+6 pin chua commit
- [2026-11-12T17:49:03Z] [live-gap-exec-B 13/11] XONG job Taylor_20261112_172358: nhanh feat/savings-row-20261112 (9246cd93e) KHONG merge; savings selfcheck 56 PASS; report_return_gate_selfcheck FAIL co san tren master; report_v2_selfcheck timeout chua ket luan; template/gate chua sua — CHO user duyet + Wendy ve cach dien dat
- [2026-11-12T18:43:29Z] [live-gap-exec-A2 13/11] XONG job Taylor_20261112_181209: lo NULL khong phai nguyen nhan (L2 sach pit 23,32/26,85, DD5 -27,7/-25,3); chenh L1->L2 = fill ao ma ADV<=0; de xuat LAG_ADV_SRC=pit mac dinh — CHO quant-skeptic + user; nhanh 4f7609c34/770393ce2 KHONG merge
- [2026-11-12T19:03:34Z] [live-gap-exec-B2 13/11] XONG job Taylor_20261112_181211: nhanh feat/savings-row-20261112 (418667a32) KHONG merge; v2 selfcheck PASS 177 x3; anchor_warning siet, gate crosscheck cot tiet kiem — CHO user/Wendy duyet cau chu+thue+ten cot template
- [2026-11-13T02:31:17Z] [live-gap-exec-C2 13/11] XONG job Taylor_20261113_021438: nhanh feat/lag-cache-c2-20261113 (b1b91a5e6) KHONG merge; validate phu Price/V3 80/80 x3TZ, mut 39/39; runbook rollback + dinh chinh blast (0 lenh live) o mike 7a01e5d94 — CHO arch-reviewer + Mike merge
- [2026-11-13T02:55:36Z] [live-gap-exec-B3 13/11] XONG: nhanh feat/savings-row-b3-20261113 (04fc4ce7f) KHONG merge; e2e gate tuan 06/11 COMPLETE (stub gui); v2 selfcheck chua ket luan (timeout); cau 5% co tuc phu thuoc cashDividendReceiving=0 — CHO Mike/user
- [2026-11-13T03:07:35Z] [live-gap-exec-A3 13/11] XONG job Taylor_20261113_021435: nhanh feat/live-gap-exec-A3-20261113 (6bbb4a443) KHONG merge; L3P pin0 22,91/pin1M 26,61, DD5 -27,89/-24,96; MINP tro (live=60); pin ladderA3-L3P-* (command thieu env, da annotate) — CHO quant-skeptic + user

- [2026-11-13T03:59:56Z] ĐANG DỞ: A4 (job Taylor_20261113_034625) research/live_gap_exec_A4: Việc2 XONG (trùng byte). Chờ seed TB s3-10 (logs/tb.done) + L3F -> viết REPORT.md, registry, pin, bus topic live-gap-exec-A4-20261113 | NEXT: boot sd seed, REPORT
