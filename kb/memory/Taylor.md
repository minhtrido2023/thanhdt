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

- [2026-10-05T18:09:34Z] [funnel8l] XONG job Taylor_20261005_180152: feat/discretionary-8l-funnel-20261006@7750213f (wt-funnel8l-1006), 53/53 x4TZ, mut 18/18. CHỜ Mike merge + cài cron 19:35 + dòng cron_registry.
- [2026-10-05T18:12:45Z] [lane-C 10-06] XONG job Taylor_20261005_180155: GARP C1 edge ro t=5.3 (median ma ~peer). CHO Mike/user quyet them lan C vao funnel; quant-skeptic truoc moi wire/size.
- [2026-10-05T18:28:55Z] [funnel8l r2] XONG job Taylor_20261005_181751: feat/discretionary-8l-funnel-20261006@5c528d5b, 117/117 x4TZ, mut 35/35. CHỜ Mike arch-review lại + merge + cron 19:35 (snapshot r1 data/rating_8l_daily/rating_8l_2026-10-05.csv còn đó).
- [2026-10-05T19:38:41Z] [intraday-watch shadow] XONG job Taylor_20261005_185546: feat/intraday-price-watch-20261006@7aefa5da (wt-ipw-1006), 171/171 x4TZ, mut 59/59. CHỜ Mike arch-review trọn bộ 1 lần + user duyệt merge/cron mỗi phút 09-14 ICT + 5 phiên shadow.
- [2026-10-05T20:23:56Z] [intraday-watch r2] XONG job Taylor_20261005_195221: feat/intraday-price-watch-20261006@42d099e8, 268/268 x4TZ x2py, mut 119/121 (2 tuong duong). CHO Mike arch-review + user chot mac dinh a-d + merge/cron (proposed: kb/cron_registry.md.proposed).
- [2026-10-06T03:48:16Z] [sell-split 10-06] XONG job Taylor_20261006_033324: fix/sell-split-by-loan-package-20261006@e7715cd0 (wt-sellsplit-1006), 49/49 x4, mut 20/20. CHỜ Mike arch-review + user duyệt merge; bot ZaloPay chưa có fix tới khi merge+restart.
- [2026-10-06T04:11:06Z] [2026-10-06 sell-split r2] XONG job Taylor_20261006_040234: fix/sell-split-by-loan-package-20261006@8a669a9a, 24/24 mut. CHỜ Mike arch-review + user duyệt merge + restart bot ZaloPay.
- [2026-10-06T04:25:16Z] [lane-C 10-06] XONG job Taylor_20261006_041048: feat/funnel-lane-c-20261006@9cf42868 (wt-lanec-1006), 193/193 x4TZ x2py, mut 40/40. CHỜ Mike arch-review + user duyệt merge (cron 19:37 dùng lại, không đổi).
- [2026-10-06T04:43:31Z] [lane-C r2 10-06] XONG job Taylor_20261006_043550: feat/funnel-lane-c-20261006@ce0d4aa8, 210/210 x4TZ x2py, mut 56/56 (tmpdir copy). CHỜ Mike arch-review r2 + merge trước cron 19:37.
- [2026-10-06T05:46:30Z] [lane-C season 10-06] XONG job Taylor_20261006_052500: feat/funnel-lane-c-season-20261006@05d1d7c2 (wt-season-1006), 263/263 x4TZ x2py, mut 103/103. DRI KHÔNG mùa vụ (η² 0,10) ⇒ vẫn RA; CHỜ user chọn C1S (ship) hay C1A (DRI vào, IS/OOS lệch dấu) + Mike arch-review/merge.
- [2026-10-06T14:15:50Z] [broker-primary r5] XONG job Taylor_20261006_133445: feat/broker-primary-20261003@26fbc30d, 666/668 x3TZ x2py, mut 449/449 (3.12 448, 1 tương đương). Thay dòng r4. CHỜ Mike arch-review r5 + user quyết merge; KHÔNG bật live.
- [2026-10-06T14:46:09Z] ĐANG DỞ r6 broker-primary (job Taylor_20261006_143910): BƯỚC0 xong (≤10d: 67 cặp/20.636 (mã,ex), 2020+ 24 cặp; cùng ngày 887) ⇒ làm thiết kế _multi_event 2 writer | NEXT: sửa code wt-brokerprimary-1003, test, mutation, commit, bus broker-primary-r6
