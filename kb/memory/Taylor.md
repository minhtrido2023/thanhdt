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

- [2026-11-17T03:41:33Z] ĐANG DỞ: job Taylor_20261117_034120 ORB vong3 R1,R2,N-a,N-b,N-c,N-e | NEXT: sua orb_futures.py + selfcheck o wt-orb-futures-20261116
- [2026-11-17T03:46:42Z] [orb-futures vong3 17/11] XONG job Taylor_20261117_034120: outer addddabf9, mike 3e41ae02a, KHONG merge/cron, co TAT — CHO Mike arch-review diff-only; watchdog cron = dieu kien truoc LIVE
- [2026-11-17T03:53:52Z] ĐANG DỞ: job Taylor_20261117_035339 DD QTP | NEXT: tai BCTC Q3/2026 -> agents/Taylor/research/dd_QTP_20261117/src, viet REPORT.md
- [2026-11-17T04:05:43Z] [dd-qtp 17/11] XONG job Taylor_20261117_035339: REPORT.md dd_QTP_20261117, tam sau CK 13.050 (vung 9.550-16.030) — CHO Mike fundamental-skeptic + dd_price_zones
- [2026-11-17T04:15:20Z] ĐANG DỞ: job Taylor_20261117_041500 ORB vong4 R2 re-read + loop_err | NEXT: sua orb_futures.py + selfcheck wt-orb-futures-20261116
- [2026-11-17T04:18:56Z] [orb-futures vong4 17/11] XONG job Taylor_20261117_041500: outer 1cb1ce075, mike ca6c73061, KHONG merge, co TAT — CHO Mike arch-review diff-only
- [2026-11-17T04:21:55Z] [dd-qtp r2 17/11] XONG job Taylor_20261117_041718: tam sau CK 13.140 (vung 10.390-16.490), gia/tam 0,78; QD768 goc CHUA KIEM — CHO Mike chay lai skeptic/quyet dd_price_zones
- [2026-11-17T04:23:55Z] ĐANG DỞ: job Taylor_20261117_042339 QTP investor report | NEXT: build_report.py o research/dd_QTP_20261117/investor_report
- [2026-11-17T04:34:44Z] [dd-qtp investor report 17/11] XONG job Taylor_20261117_042339: PDF md5 5facf0a700b689d234322b4e5a3368ac, CHUA gui email — CHO user 'gui email' + Mike ghi dd_price_zones
- [2026-11-17T09:30:01Z] ĐANG DỞ: job Taylor_20261117_092943 NAV ky quy phai sinh SpaceX | NEXT: doc spec muc 7 + daily_nav_snapshot/compute_active_nav/reconcile/nav_period_returns
- [2026-11-17T10:01:21Z] [nav-deriv 17/11] XONG job Taylor_20261117_092943: mike 760525131 nhanh feat/nav-deriv-margin-20261117 KHONG merge — CHO Mike arch-review+merge TRUOC 19:10 ICT + ghi flow cap SpaceX+5tr/ZaloPay-5tr (can gio that)
- [2026-11-17T10:22:26Z] ĐANG DỞ: job Taylor_20261117_102211 refactor New deals (brief newdeals_refresh_20261117) | NEXT: đọc brief, tạo worktree
- [2026-11-17T10:31:59Z] [newdeals-season 17/11] XONG job Taylor_20261117_102211: nhanh feat/newdeals-season-20261117 d97339d1a, KHONG merge/cron — CHO Mike arch-review + cai cron 19:45 ICT; DD queue Q3 = VCB
- [2026-11-17T10:44:36Z] [newdeals-season vong2 17/11] XONG job Taylor_20261117_103907: outer 530263674 (pushed), mike 3a0f92f0f gate + 0023d9367 registry, KHONG merge/cron — CHO Mike arch-review + merge cung dot + backup converge_portfolio_paper.json truoc cron 19:45 ICT
- [2026-11-17T11:02:54Z] ĐANG DỞ: job Taylor_20261117_110239 DD VCB | NEXT: đọc brief + skill due-diligence, viết REPORT.md dd_VCB_20261117
- [2026-11-17T11:11:26Z] [dd-vcb 17/11] XONG job Taylor_20261117_110239: REPORT dd_VCB_20261117, tam 42.035 (vung 36.431-49.678, r13,5%; Ke beta-that 12% => 54.646), assumptions_md5 acba98b2 — CHO Mike fundamental-skeptic + dd_price_zones
- [2026-11-17T11:22:22Z] [dd-vcb r2 17/11] XONG job Taylor_20261117_111929: 5/6 muc ap, muc 6 (doc BCTC KT 2025) bi chan do thieu cong cu PDF — CHO Mike skeptic vong 2; tam 42.035 khong doi
- [2026-11-17T15:57:51Z] [dd-vcb r3 17/11] XONG job Taylor_20261117_155604: tam 35.497 (ROE 14,6%), D3/D4 chua ap (brief mo ho) — CHO Mike skeptic R3 + lam ro D3/D4
