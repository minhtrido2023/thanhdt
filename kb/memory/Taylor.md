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

- [2026-11-18T12:55:42Z] [dd-llm r2 18/11] XONG job Taylor_20261118_124655: NHAN DOI 'quanh hop ly 1,05' -> 'DAT 1,35x', tam 24.599 (vung 3.630-39.728), bien co so 4,5% trung vi; ngoai tru KT 3 nam + canh bao HNX; md5 assumptions aaaeec21 — CHO Mike skeptic r2 + dung PDF
- [2026-11-18T12:57:50Z] ĐANG DỞ: job Taylor_20261118_125730 investor report LLM | NEXT: doc skill dd-investor-report, copy build tu dd_DBC investor_report
- [2026-11-18T13:02:16Z] ĐANG DỞ: job Taylor_20261118_125730 investor report LLM — assets xong (investor_report/src, figs/map) | NEXT: build_report.py figs + md + pdf + selfcheck
- [2026-11-18T13:08:00Z] [dd-llm investor 18/11] XONG job Taylor_20261118_125730: PDF/HTML/md o dd_LLM_20261118/investor_report (10 trang, md5 cf86360a) — CHO user bao 'gui email' + Mike ghi dd_price_zones
- [2026-11-19T03:46:01Z] ĐANG DỞ: job Taylor_20261119_034548 vnindex-tr-g5-drift (read-only) | NEXT: doc vnindex_total_return.py, tr_build.py, phan tich lech synth vs official
- [2026-11-19T03:54:12Z] [g5-drift 19/11] XONG job Taylor_20261119_034548: G5 lech = ro thieu LPS/DMX/GEL/CRV (OShares NULL/khong co dong) — CHO Winston lap OShares DMX + GEL/CRV, user duyet restate 18/08 + va G8
- [2026-11-19T04:49:20Z] [intraday-cluster-audit 19/11] XONG job Taylor_20261119_044412: NO-GO #1/#4, 0/5 setup PASS (cum FZ-001 17, FZ-002 15), holdout khong du N — CHO Mike quant-skeptic + gui user
- [2026-11-19T05:05:58Z] [fill-timing recheck 19/11] XONG job Taylor_20261119_044040: BUY blocks -18bps PASS, SELL khong PASS, khoang trong du lieu sau 06-12 — CHO Mike quant-skeptic + user duyet keo intraday moi
- [2026-11-19T05:18:02Z] [basket-vs-fz 19/11] XONG job Taylor_20261119_051521: FZ ~ cuoc thoi diem hoi (rổ 53%/69% loi nhuan, excess CI90 chua 0, 17/15 cum) — CHO Mike quant-skeptic + bao user
- [2026-11-19T05:20:56Z] [fill-timing OOS 19/11] XONG job Taylor_20261119_051519: BUY -12.0bps CI[-27.4,+2.8] khong PASS/khong rollback; SELL +1.2 - CHO Mike quant-skeptic
- [2026-11-19T05:33:26Z] [2026-11-19] fz-signal-ledger XONG job Taylor_20261119_052906: commit 9b7dc051b nhanh session/fz-signal-ledger-20261119 (wt-fz-ledger-20261119) — CHO Mike duyet+merge; user phai xin nguon signal hang ngay moi cron
- [2026-11-19T06:03:59Z] [2026-11-19] fill-timing-monitor XONG job Taylor_20261119_055805: commit d524f03ca nhánh session/fill-timing-monitor-20261119 — CHO Mike review diff + cài cron (đề xuất 07:40 ICT T2-T6)
