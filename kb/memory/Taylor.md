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

- [2026-10-06T03:48:16Z] [sell-split 10-06] XONG job Taylor_20261006_033324: fix/sell-split-by-loan-package-20261006@e7715cd0 (wt-sellsplit-1006), 49/49 x4, mut 20/20. CHỜ Mike arch-review + user duyệt merge; bot ZaloPay chưa có fix tới khi merge+restart.
- [2026-10-06T04:11:06Z] [2026-10-06 sell-split r2] XONG job Taylor_20261006_040234: fix/sell-split-by-loan-package-20261006@8a669a9a, 24/24 mut. CHỜ Mike arch-review + user duyệt merge + restart bot ZaloPay.
- [2026-10-06T04:25:16Z] [lane-C 10-06] XONG job Taylor_20261006_041048: feat/funnel-lane-c-20261006@9cf42868 (wt-lanec-1006), 193/193 x4TZ x2py, mut 40/40. CHỜ Mike arch-review + user duyệt merge (cron 19:37 dùng lại, không đổi).
- [2026-10-06T04:43:31Z] [lane-C r2 10-06] XONG job Taylor_20261006_043550: feat/funnel-lane-c-20261006@ce0d4aa8, 210/210 x4TZ x2py, mut 56/56 (tmpdir copy). CHỜ Mike arch-review r2 + merge trước cron 19:37.
- [2026-10-06T05:46:30Z] [lane-C season 10-06] XONG job Taylor_20261006_052500: feat/funnel-lane-c-season-20261006@05d1d7c2 (wt-season-1006), 263/263 x4TZ x2py, mut 103/103. DRI KHÔNG mùa vụ (η² 0,10) ⇒ vẫn RA; CHỜ user chọn C1S (ship) hay C1A (DRI vào, IS/OOS lệch dấu) + Mike arch-review/merge.
- [2026-10-06T15:14:23Z] [broker-primary r6] XONG job Taylor_20261006_143910: feat/broker-primary-20261003@7db42331, 705/707 x3TZ x2py, mut 472/472 (3.12 471, 1 tương đương), BƯỚC0 hiếm (≤10d 67/20.636). Thay dòng r5. CHỜ Mike arch-review r6 + user quyết merge; KHÔNG bật live.
- [2026-10-07T04:36:12Z] [broker-primary r8 10-07] XONG job Taylor_20261007_034436: feat/broker-primary-r7-20261007@58aa852d, 782/784 x3TZ x2py, mut 538/538 (3.12 537, 1 tương đương). Thay dòng r7. CHỜ Mike arch-review r8 + user duyệt merge; KHÔNG bật live.
- [2026-10-07T05:44:19Z] [broker-primary r9 10-07] XONG job Taylor_20261007_050650: feat/broker-primary-r7-20261007@5c0257a6, 785/787 x3TZ x2py, mut 539/539 (3.12 538, 1 tương đương). Thay dòng r8. CHỜ Mike arch-review r9 + merge (user đã duyệt); KHÔNG bật live.
- [2026-10-07T06:49:00Z] [broker-primary r10 10-07] XONG job Taylor_20261007_062338: feat/broker-primary-r10-20261007@6e26dbe1 test-only, 788/790 x3TZ x2py, mut 541/541 (3.12 540). Thay dòng r8/r9. CHỜ Mike merge; KHÔNG bật live.
- [2026-10-08T04:48:53Z] ĐANG DỞ job Taylor_20261008_042322 adjfactor awaiting r3: sửa 5 mục arch-review (wt-await-1008 @c2854372) | NEXT: selfcheck+mut, review lại 1 lần, merge
- [2026-10-08T05:49:34Z] [adjfactor awaiting 10-08] DUNG sau arch-review vong 2 NEEDS_CHANGES (feat/adjfactor-awaiting-trade-20261008@25cf9a22, wt-await-1008): B1 _state_write msg duong xoa khoa, B2 alert.sh:560 dung -n DRIFTS, B3 test khe 1-2 phien, B4 dry-run lai sau r3. CHO Mike/user cho phep r4 roi merge.
- [2026-10-08T06:30:28Z] ĐANG DỞ job Taylor_20261008_055312 adjfactor awaiting r4: commit 9e4a6bd1 (wt-await-1008), 570/570 x4, mut 64/64 | NEXT: arch-review 1 lần → APPROVED squash merge mike master / NEEDS_CHANGES ghi finding dừng
