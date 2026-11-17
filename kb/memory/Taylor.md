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

- [2026-11-16T01:37:18Z] [q9-waiver 16/11] XONG job Taylor_20261116_013249: nhanh feat/q9-waiver-20261116 (17db40c3c) KHONG merge — CHO Mike arch-review + merge + chay gate that 2 weekly 09-13/11; waiver het han 2026-11-20
- [2026-11-16T01:58:14Z] [cq vong2 16/11] XONG job Taylor_20261116_014210: A 960c17f97, B 145b9cf92 KHONG merge — CHO Mike arch-review diff-only + merge
- [2026-11-16T03:16:01Z] ĐANG DỞ: job Taylor_20261116_031549 LAG early-exit Bayes | NEXT: buoc 0 -> research/lag_early_exit_bayes_20261116/
- [2026-11-16T03:28:43Z] [lag-early-exit 16/11] XONG job Taylor_20261116_031549: NO-GO thoat som LAG, nhanh research/lag-early-exit-20261116 (f037ad41f) KHONG merge — CHO user chot A (giu T+25) / B (canh bao display-only)
- [2026-11-16T16:21:43Z] ĐANG DỞ: job Taylor_20261116_162132 ORB futures live path (A probe..F spec) | NEXT: khao sat + worktree feat/orb-futures-live-20261116
- [2026-11-16T16:41:16Z] [orb-futures 16/11] XONG job Taylor_20261116_162132: nhanh feat/orb-futures-live-20261116 (outer e9aad9819, mike d91e49d32) KHONG merge/cron, co TAT — CHO Mike arch-review+quant-skeptic; sau do DRY>=10 phien, sua NAV phai sinh truoc khi user nop ky quy
- [2026-11-16T16:50:16Z] ĐANG DỞ: job Taylor_20261116_165006 ORB vong2 sua B1-B4,M1-3,m1-2,N1,spec | NEXT: sua orb_futures.py + selfcheck
- [2026-11-16T17:01:23Z] [orb-futures vong2 17/11] XONG job Taylor_20261116_165006: outer 6e4b80c22, mike 2a6ddf10c(prereg)+9f3da28cb, KHONG merge/cron, co TAT — CHO Mike arch-review diff-only (round-cap: loi moi => user); NAV fix blocker truoc nop ky quy
- [2026-11-17T03:41:33Z] ĐANG DỞ: job Taylor_20261117_034120 ORB vong3 R1,R2,N-a,N-b,N-c,N-e | NEXT: sua orb_futures.py + selfcheck o wt-orb-futures-20261116
- [2026-11-17T03:46:42Z] [orb-futures vong3 17/11] XONG job Taylor_20261117_034120: outer addddabf9, mike 3e41ae02a, KHONG merge/cron, co TAT — CHO Mike arch-review diff-only; watchdog cron = dieu kien truoc LIVE
- [2026-11-17T03:53:52Z] ĐANG DỞ: job Taylor_20261117_035339 DD QTP | NEXT: tai BCTC Q3/2026 -> agents/Taylor/research/dd_QTP_20261117/src, viet REPORT.md
- [2026-11-17T04:05:43Z] [dd-qtp 17/11] XONG job Taylor_20261117_035339: REPORT.md dd_QTP_20261117, tam sau CK 13.050 (vung 9.550-16.030) — CHO Mike fundamental-skeptic + dd_price_zones
