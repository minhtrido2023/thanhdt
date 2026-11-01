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

- [2026-11-01T03:32:32Z] ĐANG DỞ: DD HHS job Taylor_20261101_033221 — research/dd_HHS_20261101/ | NEXT: đọc src scan, tìm BCTC hợp nhất, viết REPORT
- [2026-11-01T03:42:48Z] ĐANG DỞ: DD HHS job Taylor_20261101_033221 — số đọc xong calc/notes_read.md + valuation_out.txt | NEXT: viết REPORT.md, GAPS.md, bus finding
- [2026-11-01T03:45:42Z] [dd-HHS 01/11] XONG job Taylor_20261101_033221: research/dd_HHS_20261101/REPORT.md + GAPS.md (chua commit) — vung 8.800-15.900 tam ~11.900 vs 9.450, nua duoi; WARNING trung binh-cao (uy quyen, HHS Capital 1.302 ty); TCH-DD ghi sai International (thuc te Dongfeng) — CHO Mike doc/quyet investor report
- [2026-11-01T04:09:54Z] ĐANG DỞ: DD TV2 v2 job Taylor_20261101_040936 — research/dd_TV2_20261101/ | NEXT: đọc REPORT 28/10, gaps, REPORT_v2
- [2026-11-01T04:11:31Z] [dd-HHS-gaps 01/11] XONG job Taylor_20261101_040247: GAPS_FILL.md (chua commit) — vung giu 8,8-15,9k; WARNING moi: KL 08/KL-TTTP (Pruksa gia NOXH) + TB 2124 (N01 CRV); HHS Capital khong ten nguoi ban — CHO Mike gop voi skeptic
- [2026-11-01T04:14:32Z] ĐANG DỞ: DD HHS v2+investor job Taylor_20261101_041414 — research/dd_HHS_20261101/ | NEXT: đọc SKEPTIC+GAPS_FILL, sửa REPORT, rồi investor_report
- [2026-11-01T04:16:33Z] ĐANG DỞ: DD SIP job Taylor_20261101_041613 — research/dd_SIP_20261101/ | NEXT: tải src BCTC, đọc Bobby KCN, viết REPORT
- [2026-11-01T04:16:53Z] ĐANG DỞ: DD HHS job Taylor_20261101_041414 — calc/valuation_v2_out.txt xong (tam TCH-basis ~9.960, vung 7.600-13.000) | NEXT: viết REPORT v2, GAPS, bus; rồi investor_report
- [2026-11-01T04:17:37Z] ĐANG DỞ: DD TV2 v2 job Taylor_20261101_040936 — gaps+du lieu xong (src/gaps, calc/hist_out.txt) | NEXT: calc/valuation.py, REPORT_v2.md, GAPS.md, bus finding dd-TV2-v2-20261101
- [2026-11-01T04:19:24Z] ĐANG DỞ: DD HHS job Taylor_20261101_041414 — VIỆC 1 XONG (REPORT v2, bus dd-hhs-v2); VIỆC 2 investor_report đang làm | NEXT: copy khuôn TCH investor_report, sửa
- [2026-11-01T04:22:08Z] [dd-TV2-v2 01/11] XONG job Taylor_20261101_040936: research/dd_TV2_20261101/REPORT_v2.md + GAPS.md (chua commit) — vung 18,3-28,1k tam ~23k vs 27.000 (trong vung nua tren); room ngoai 0%; 4 HD EPC — CHO skeptic roi investor report
- [2026-11-01T04:27:02Z] ĐANG DỞ: DD SIP job Taylor_20261101_041613 — số đọc xong calc/notes_read.md, cbtt_facts.md, comps_bq.csv | NEXT: valuation.py, đọc Bobby KCN, REPORT/GAPS, bus
- [2026-11-01T04:29:57Z] ĐANG DỞ: DD FPT job Taylor_20261101_042936 — research/dd_FPT_20261101/ | NEXT: đọc skill, src, PREREG cũ, tìm BCTC Q3
- [2026-11-01T04:30:03Z] [dd-HHS-v2+investor 01/11] XONG job Taylor_20261101_041414: REPORT v2 (co so TCH, tam ≈9.960-10.230, gia -5..-8%) + investor_report/ (10tr, chua commit, chua gui) — CHO Mike doc kiem + gui email
- [2026-11-01T04:31:30Z] ĐANG DỞ: DD TV2 v3+investor job Taylor_20261101_043110 — research/dd_TV2_20261101/ | NEXT: đọc SKEPTIC, sửa REPORT_v3, rồi investor_report
- [2026-11-01T04:35:22Z] ĐANG DỞ: DD TV2 job Taylor_20261101_043110 — A xong REPORT_v3 (kỳ vọng 20.700, vùng 17,1-25,3k, giá +31%) | NEXT: investor_report theo khuôn TCH
- [2026-11-01T04:35:59Z] ĐANG DỞ: DD FPT job Taylor_20261101_042936 — calc/notes_q3_bctc.md + notes_disclosures.md xong | NEXT: spot-check CF p10, BQ/DNSE, valuation, REPORT
- [2026-11-01T04:36:04Z] [dd-SIP 01/11] XONG job Taylor_20261101_041613: research/dd_SIP_20261101/REPORT.md + GAPS.md (chua commit) — vung hop ly 44-58k tam ~51,5k vs 48.350 nua duoi; WARNING trung binh (cho vay CTCK 4.223 khong TSDB 69%, TP T&T 1.000,7); VRG khong phai CD lon — CHO Mike skeptic/investor report
- [2026-11-01T04:40:18Z] ĐANG DỞ: DD FPT job Taylor_20261101_042936 — calc/valuation_out.txt xong (co so 58,8k, khoang 40-85k, gia 52,7k) | NEXT: REPORT.md, GAPS.md, bus
- [2026-11-01T04:43:10Z] [dd-FPT 01/11] XONG job Taylor_20261101_042936: research/dd_FPT_20261101/REPORT.md + GAPS.md (chua commit) — vung co so 51-62k tam ~58,8k vs 52,7k; CFO 9T 952; ky moi Q3 +3,6%; WARNING thap-TB (FTEL/Bo CA, khoan 618,8 ty GBP) — CHO skeptic + Mike investor report
- [2026-11-01T04:45:51Z] ĐANG DỞ: DD SIP v2+investor job Taylor_20261101_044530 — research/dd_SIP_20261101/ | NEXT: đọc SKEPTIC, sửa REPORT+valuation.py, rồi investor_report
- [2026-11-01T04:46:28Z] [dd-TV2-investor 01/11] XONG job Taylor_20261101_043110: REPORT_v3 + investor_report/ (10tr, chua commit, CHUA gui) — ky vong 20.700, vung co so 17,1-25,3k, gia 27.000 +31% TREN vung; CHO Mike doc kiem + gui email
- [2026-11-01T04:48:03Z] ĐANG DỞ: DD SIP job Taylor_20261101_044530 — valuation v2 xong (tam trong so 47.728, co so 49.235) | NEXT: sửa REPORT.md v2, GAPS, quét pháp lý, bus; rồi investor_report
