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

- [2026-11-13T02:31:17Z] [live-gap-exec-C2 13/11] XONG job Taylor_20261113_021438: nhanh feat/lag-cache-c2-20261113 (b1b91a5e6) KHONG merge; validate phu Price/V3 80/80 x3TZ, mut 39/39; runbook rollback + dinh chinh blast (0 lenh live) o mike 7a01e5d94 — CHO arch-reviewer + Mike merge
- [2026-11-13T02:55:36Z] [live-gap-exec-B3 13/11] XONG: nhanh feat/savings-row-b3-20261113 (04fc4ce7f) KHONG merge; e2e gate tuan 06/11 COMPLETE (stub gui); v2 selfcheck chua ket luan (timeout); cau 5% co tuc phu thuoc cashDividendReceiving=0 — CHO Mike/user
- [2026-11-13T03:07:35Z] [live-gap-exec-A3 13/11] XONG job Taylor_20261113_021435: nhanh feat/live-gap-exec-A3-20261113 (6bbb4a443) KHONG merge; L3P pin0 22,91/pin1M 26,61, DD5 -27,89/-24,96; MINP tro (live=60); pin ladderA3-L3P-* (command thieu env, da annotate) — CHO quant-skeptic + user

- [2026-11-13T03:59:56Z] ĐANG DỞ: A4 (job Taylor_20261113_034625) research/live_gap_exec_A4: Việc2 XONG (trùng byte). Chờ seed TB s3-10 (logs/tb.done) + L3F -> viết REPORT.md, registry, pin, bus topic live-gap-exec-A4-20261113 | NEXT: boot sd seed, REPORT
- [2026-11-13T04:30:54Z] [live-gap-exec-A4 13/11] XONG: Δ -0,48pp bq->pit THAT (ghep cap sd 0,014, 10/10 seed); cua so ADV BQ gom ngay fill; pin merged trung byte 80f509ec/e2de0ac4; registry them, KHONG merge/pin moi — CHO quant-skeptic + user
- [2026-11-13T07:32:55Z] [live-gap-exec-A5 13/11] XONG job Taylor_20261113_071030: pin trung byte tren ma commit (80f509ec main sach / e2de0ac4 e9a9aed1a); neo -25,2 (4707bcbe) chua fill ao, bo fill ao -3,96pp => DD5 san trung thuc -29,09 (park0.3)/-27,89 (park0); ADV live=pit 29/32 — CHO quant-skeptic + user quyet neo
- [2026-11-13T08:01:28Z] [decision-inbox 13/11] XONG job Taylor_20261113_075639: DESIGN.md o research/decision_inbox_design_20261113 (cog CUSTOM_COGS_DIR + bin/decision_inbox.py, chua code) — CHO user duyet + allow-list user tu them
- [2026-11-13T08:18:48Z] [decision-inbox impl 13/11] XONG job Taylor_20261113_080329: nhanh feat/decision-inbox-20261113 (head 2b17704de) KHONG merge, cog chua bat; selfcheck 221 ca x2 TZ 0 fail; CHO Mike chay arch-reviewer toan diff roi merge; user bat shadow (2 dong .env) sau merge; buoc 7 doi soat chua lam
- [2026-11-13T08:26:07Z] [live-gap-exec-A6 13/11] XONG job Taylor_20261113_075112: nhanh research/live-gap-A6-carry-20261113 (262c117c3) 1 cay, pin0 80f509ec + pin1M e2de0ac4 trung byte, KHONG merge; DD5 dai L3P p0.3 -28,54 [-29,09;-27,99] (s12345 = canh duoi); small-NAV 1B DD5 -32,75 (chenh L1 chi -1,6pp) => neo cho NAV live chua chot — CHO quant-skeptic + arch-review + user
- [2026-11-13T08:40:19Z] [decision-inbox vong2 13/11] XONG job Taylor_20261113_083010: nhanh feat/decision-inbox-20261113 (03187c254) KHONG merge; 7 muc + 2 muc thap, selfcheck r2 17/77->77/77; CHO arch-reviewer vong 3 (chi neu NEEDS_CHANGES lan nua -> circuit-breaker) roi Mike merge; retention state jsonl chua lam
- [2026-11-13T10:23:05Z] ĐANG DỞ: annualization_basis_selfcheck 68 file chặn (danh sách agents/Wags/research/ann_remaining_20261113.txt) | NEXT: sau khi Wags merge ec771492b vào master -> chạy $DNA_PYEXE bin/annualization_basis_selfcheck.py --update-baseline --accept-new-debt (scan ~2+ phút, chạy nền), ghi lý do frozen/PREREG/paper-only, rc=0 + đóng bus 'Wags/selfcheck-red: mike/bin/annualization_basis_selfcheck.py'
- [2026-11-13T14:30:34Z] [live-gap-exec-A7 13/11] XONG job Taylor_20261113_134219: nhanh research/live-gap-A7-sellcap-20261113 (414468bcb) KHONG merge; tran ban khong doi DD5; thieu san ADV 2ty la nguon lech; DD5 NAV live (1-2B) ~-33% vs 50B -26 — CHO quant-skeptic + user chot neo; chua do pin1M/park0.3 o NAV nho
- [2026-11-13T15:36:37Z] ĐANG DỞ: A9 (job Taylor_20261113_153627) sua tran ban A7 -> nhanh research/live-gap-A9-sellcap-fix-20261114 tu 414468bcb | NEXT: doc REPORT A7 + verdict, sua code
- [2026-11-13T16:27:25Z] [live-gap-exec-A9 13/11] XONG job Taylor_20261113_153627: nhanh research/live-gap-A9-sellcap-fix-20261114 (8b5f7fd0d, worktree wt-livegapA7-1113 doi nhanh tai cho) KHONG merge; neo DD5 NAV live khong doi -33,2, 50B -26,22 — CHO arch-reviewer vong 2 + quant-skeptic, Mike merge
