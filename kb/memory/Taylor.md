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

- [2026-11-18T12:24:10Z] ĐANG DỞ: job Taylor_20261118_122349 DD LLM | NEXT: doc skill, render BCTC src/, viet REPORT dd_LLM_20261118
- [2026-11-18T12:28:41Z] ĐANG DỞ: job Taylor_20261118_122819 lead-signal run-up TV1/VCP (paper) | NEXT: kb recall, PREREG, BQ pull, engine
- [2026-11-18T12:35:01Z] ĐANG DỞ: job Taylor_20261118_122349 DD LLM — calc xong model/calc_output.txt (tam 31.589, vung 4.497-51.769) | NEXT: viet REPORT.md dd_LLM_20261118 + bus finding
- [2026-11-18T12:38:40Z] [dd-llm 18/11] XONG vong1 job Taylor_20261118_122349: REPORT dd_LLM_20261118 tam 31.589 (vung 4.497-51.769) gia/tam 1,05, D=1,69 phan ky manh, RI tien mac ket 13.560; md5 assumptions dea9f474 — CHO Mike fundamental-skeptic
- [2026-11-18T12:42:11Z] [lead-signal-runup 18/11] XONG job Taylor_20261118_122819: NO-GO 0/48 GO (15 informative nhung deu tre, net am); REPORT md5 14c49853 — CHO Mike quant-skeptic + ghi NO-GO vao ta-schools-vn
- [2026-11-18T12:47:15Z] ĐANG DỞ: job Taylor_20261118_124655 DD LLM vong2 (ap skeptic_r1) | NEXT: doc skeptic_r1.md, render PDF, tai giai trinh, sua calc.py
- [2026-11-18T12:55:42Z] [dd-llm r2 18/11] XONG job Taylor_20261118_124655: NHAN DOI 'quanh hop ly 1,05' -> 'DAT 1,35x', tam 24.599 (vung 3.630-39.728), bien co so 4,5% trung vi; ngoai tru KT 3 nam + canh bao HNX; md5 assumptions aaaeec21 — CHO Mike skeptic r2 + dung PDF
- [2026-11-18T12:57:50Z] ĐANG DỞ: job Taylor_20261118_125730 investor report LLM | NEXT: doc skill dd-investor-report, copy build tu dd_DBC investor_report
- [2026-11-18T13:02:16Z] ĐANG DỞ: job Taylor_20261118_125730 investor report LLM — assets xong (investor_report/src, figs/map) | NEXT: build_report.py figs + md + pdf + selfcheck
- [2026-11-18T13:08:00Z] [dd-llm investor 18/11] XONG job Taylor_20261118_125730: PDF/HTML/md o dd_LLM_20261118/investor_report (10 trang, md5 cf86360a) — CHO user bao 'gui email' + Mike ghi dd_price_zones
- [2026-11-19T03:46:01Z] ĐANG DỞ: job Taylor_20261119_034548 vnindex-tr-g5-drift (read-only) | NEXT: doc vnindex_total_return.py, tr_build.py, phan tich lech synth vs official
- [2026-11-19T03:54:12Z] [g5-drift 19/11] XONG job Taylor_20261119_034548: G5 lech = ro thieu LPS/DMX/GEL/CRV (OShares NULL/khong co dong) — CHO Winston lap OShares DMX + GEL/CRV, user duyet restate 18/08 + va G8
