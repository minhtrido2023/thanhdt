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

- [2026-11-19T03:46:01Z] ĐANG DỞ: job Taylor_20261119_034548 vnindex-tr-g5-drift (read-only) | NEXT: doc vnindex_total_return.py, tr_build.py, phan tich lech synth vs official
- [2026-11-19T03:54:12Z] [g5-drift 19/11] XONG job Taylor_20261119_034548: G5 lech = ro thieu LPS/DMX/GEL/CRV (OShares NULL/khong co dong) — CHO Winston lap OShares DMX + GEL/CRV, user duyet restate 18/08 + va G8
- [2026-11-19T04:49:20Z] [intraday-cluster-audit 19/11] XONG job Taylor_20261119_044412: NO-GO #1/#4, 0/5 setup PASS (cum FZ-001 17, FZ-002 15), holdout khong du N — CHO Mike quant-skeptic + gui user
- [2026-11-19T05:05:58Z] [fill-timing recheck 19/11] XONG job Taylor_20261119_044040: BUY blocks -18bps PASS, SELL khong PASS, khoang trong du lieu sau 06-12 — CHO Mike quant-skeptic + user duyet keo intraday moi
- [2026-11-19T05:18:02Z] [basket-vs-fz 19/11] XONG job Taylor_20261119_051521: FZ ~ cuoc thoi diem hoi (rổ 53%/69% loi nhuan, excess CI90 chua 0, 17/15 cum) — CHO Mike quant-skeptic + bao user
- [2026-11-19T05:20:56Z] [fill-timing OOS 19/11] XONG job Taylor_20261119_051519: BUY -12.0bps CI[-27.4,+2.8] khong PASS/khong rollback; SELL +1.2 - CHO Mike quant-skeptic
- [2026-11-19T05:33:26Z] [2026-11-19] fz-signal-ledger XONG job Taylor_20261119_052906: commit 9b7dc051b nhanh session/fz-signal-ledger-20261119 (wt-fz-ledger-20261119) — CHO Mike duyet+merge; user phai xin nguon signal hang ngay moi cron
- [2026-11-19T06:03:59Z] [2026-11-19] fill-timing-monitor XONG job Taylor_20261119_055805: commit d524f03ca nhánh session/fill-timing-monitor-20261119 — CHO Mike review diff + cài cron (đề xuất 07:40 ICT T2-T6)
- [2026-11-19T08:01:33Z] ĐANG DỞ: job Taylor_20261119_080122 vnindex-tr G8 gap patch (worktree wt-vnindex-tr-g8-gap-20261119) | NEXT: đọc G8/VERIFY_SEALED
- [2026-11-19T08:05:18Z] ĐANG DỞ: job Taylor_20261119_080508 arch review 8L+DT5G data-leverage plan (read-only) | NEXT: đọc data_registry + kiểm kê BQ, viết agents/Taylor/research/arch_8l_dt5g_data_leverage_20261119/REPORT.md
- [2026-11-19T08:14:03Z] [g8-gap 19/11] XONG job Taylor_20261119_080122: commit 48d4a8d07 nhánh session/vnindex-tr-g8-gap-20261119 — CHO Mike duyet+arch-review; merge => o TR chua co so tu 11/12 (6 ma CRV/GEL/HPA/DSH/DVV/DMX)
- [2026-11-19T08:26:16Z] [arch-8l-dt5g 19/11] XONG job Taylor_20261119_080508: REPORT o research/arch_8l_dt5g_data_leverage_20261119 — CHO user quyet 5 cau (A1 snapshot vintage, bq_admin, 12 trial A4, C1, ky vong) roi moi dispatch Wave A
- [2026-11-19T08:57:22Z] [g8-gap r2 19/11] XONG job Taylor_20261119_084930: commit 905745fbb — CHO Mike arch-review lại + user duyệt ack đề xuất (6 mã, đến 12-27) rồi mới merge
- [2026-11-19T09:04:55Z] ĐANG DỞ: job Taylor_20261119_090443 A3 bản đồ v2 + A4 nowcast 12 họ | NEXT: đọc REPORT §0,5,6,7,8; code B2 commodity_cycle_te_20261026
- [2026-11-19T09:05:03Z] ĐANG DỞ: job Taylor_20261119_090450 sector-leaders-nowcast (việc 5) | NEXT: đọc REPORT arch_8l + commodity_cycle_te, viết PREREG, chạy
- [2026-11-19T09:10:29Z] [macro-stress C1 19/11] XONG job Taylor_20261119_090510: commit e09a591a0 nhánh session/macro-stress-ledger-20261119 — CHO Mike review diff + quyết wire dna_report
- [2026-11-19T09:17:15Z] [A4 nowcast 19/11] XONG job Taylor_20261119_090443: 5/12 họ GO (heo, môi giới, sân bay, cảng, ô tô), commit 3469ad3dc — CHO Mike gọi quant-skeptic rồi mới viết PREREG-5 (B1)
- [2026-11-19T09:22:39Z] [sector-leaders 19/11] XONG job Taylor_20261119_090450: KHONG sleeve; T2 display dat, T9 ung vien PREREG-5 paper (commit 19a9944b9) — CHO Mike goi quant-skeptic + user duyet
- [2026-11-19T09:25:32Z] [g8-gap r3 19/11] XONG job Taylor_20261119_091916: commit f7cdf9a22 (lib) + fd5c29454 (README) — CHO Mike arch-review vong 3, merge CUNG ack 6 ma; chua replay BQ that voi K=11
