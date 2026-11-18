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

- [2026-11-18T03:57:58Z] ĐANG DỞ: job Taylor_20261118_035743 DD DBC | NEXT: doc skill due-diligence, render BCTC scan src/, viet REPORT.md dd_DBC_20261118
- [2026-11-18T04:04:48Z] ĐANG DỞ: job Taylor_20261118_035743 DD DBC — calc xong model/calc_output.txt | NEXT: viet REPORT.md dd_DBC_20261118 + bus finding
- [2026-11-18T04:08:14Z] [dd-dbc 18/11] XONG job Taylor_20261118_035743: REPORT dd_DBC_20261118, tam 21.815 (vung 14.034-29.195), gia/tam 0,78, phan ky manh D=1,44; md5 511073ce — CHO Mike fundamental-skeptic + dd_price_zones
- [2026-11-18T04:14:25Z] ĐANG DỞ: job Taylor_20261118_041402 DD POW | NEXT: doc skill, render BCTC scan, viet REPORT dd_POW_20261118
- [2026-11-18T04:21:06Z] ĐANG DỞ: job Taylor_20261118_041402 DD POW — calc xong model/calc_output.txt (tam 8.806) | NEXT: viet REPORT.md dd_POW_20261118 + bus finding
- [2026-11-18T04:24:03Z] [dd-pow 18/11] XONG job Taylor_20261118_041402: REPORT dd_POW_20261118, tam 8.806 (vung 5.551-12.060), gia/tam 1,50; md5 c1054c74 — CHO Mike fundamental-skeptic + dd_price_zones
- [2026-11-18T04:25:49Z] [dd-dbc r2 18/11] XONG job Taylor_20261118_041902: tam 18.414 (v1 21.815), gia/tam 0,92 (dai 0,78-0,97), FCFE<=0 bo V_dai/D, md5 708441c3 — CHO Mike skeptic vong 2 + quyet dinh tap kich ban (xau/tot dat lai => 1,15)
- [2026-11-18T04:35:34Z] [dd-pow r2 18/11] XONG job Taylor_20261118_043309: tam 9.792 (vung 7.166-12.419), gia/tam 1,35 DAT, md5 721c5f28 — CHO Mike skeptic vong 2 + dd_price_zones
- [2026-11-18T04:35:46Z] [dd-dbc r3 18/11] XONG job Taylor_20261118_043114: tam 19.491 (vung 11.314-27.270), gia/tam 0,87 (dai hai truc 0,83-1,10), ROE 15q 11,42%, md5 207da8c9 — CHO Mike ghi dd_price_zones; khong con skeptic r4
- [2026-11-18T04:37:21Z] ĐANG DỞ: job Taylor_20261118_043658 investor report DBC | NEXT: doc skill dd-investor-report, copy build tu POW investor_report neu co
- [2026-11-18T04:42:21Z] ĐANG DỞ: job Taylor_20261118_043658 investor report DBC — anh/logo/ban do/BQ/DNSE xong (investor_report/) | NEXT: build_report.py figs + md + pdf + selfcheck
- [2026-11-18T04:47:56Z] [dd-dbc investor 18/11] XONG job Taylor_20261118_043658: PDF/HTML/md o dd_DBC_20261118/investor_report (10 trang, md5 d5a8515f) — CHO user bao 'gui email' + Mike ghi dd_price_zones
- [2026-11-18T12:24:10Z] ĐANG DỞ: job Taylor_20261118_122349 DD LLM | NEXT: doc skill, render BCTC src/, viet REPORT dd_LLM_20261118
- [2026-11-18T12:28:41Z] ĐANG DỞ: job Taylor_20261118_122819 lead-signal run-up TV1/VCP (paper) | NEXT: kb recall, PREREG, BQ pull, engine
- [2026-11-18T12:35:01Z] ĐANG DỞ: job Taylor_20261118_122349 DD LLM — calc xong model/calc_output.txt (tam 31.589, vung 4.497-51.769) | NEXT: viet REPORT.md dd_LLM_20261118 + bus finding
- [2026-11-18T12:38:40Z] [dd-llm 18/11] XONG vong1 job Taylor_20261118_122349: REPORT dd_LLM_20261118 tam 31.589 (vung 4.497-51.769) gia/tam 1,05, D=1,69 phan ky manh, RI tien mac ket 13.560; md5 assumptions dea9f474 — CHO Mike fundamental-skeptic
- [2026-11-18T12:42:11Z] [lead-signal-runup 18/11] XONG job Taylor_20261118_122819: NO-GO 0/48 GO (15 informative nhung deu tre, net am); REPORT md5 14c49853 — CHO Mike quant-skeptic + ghi NO-GO vao ta-schools-vn
- [2026-11-18T12:47:15Z] ĐANG DỞ: job Taylor_20261118_124655 DD LLM vong2 (ap skeptic_r1) | NEXT: doc skeptic_r1.md, render PDF, tai giai trinh, sua calc.py
- [2026-11-18T12:55:42Z] [dd-llm r2 18/11] XONG job Taylor_20261118_124655: NHAN DOI 'quanh hop ly 1,05' -> 'DAT 1,35x', tam 24.599 (vung 3.630-39.728), bien co so 4,5% trung vi; ngoai tru KT 3 nam + canh bao HNX; md5 assumptions aaaeec21 — CHO Mike skeptic r2 + dung PDF
