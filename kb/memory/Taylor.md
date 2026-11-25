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

- [2026-11-24T13:27:19Z] [dd-recheck w2 job B 24/11] XONG Taylor_20261124_131354: MBB adj 20.587 (REFUTED_OPEN, mở KTPL NQ ĐHĐCĐ 2026) · DBC adj 16.439 (giữ REFUTED_OPEN, không vòng 5); wt-…b commits 345e9c815/21f9e7af7 — CHỜ Mike áp LEDGER_PROPOSAL + center_adj
- [2026-11-24T13:34:27Z] [dd-recheck w2 job A 24/11] XONG Taylor_20261124_131351: PVP adj 22.988 (MECH, 01fc032ad) · MVC adj 15.684 −3,43% skeptic REFUTED trích quỹ 11% ⇒ FULL (91bccb404); wt-…a — CHỜ Mike áp LEDGER_PROPOSAL + center_adj

- [2026-11-24T16:38:52Z] [dcf-vn-redesign V2 25/11] XONG job Taylor_20261124_160038: nhánh session/Taylor_20261124_160038 (wt-dcf-vn-redesign-20261124b) 5ae76594d chưa merge; cảnh báo đắt đạt, 'tâm giao giá' không vượt null, lens chưa phải alpha — CHỜ Mike quant-skeptic + user quyết 4 việc (bản hiển thị v3, L2 hay REL, cổng mềm cảnh báo đắt, đổi tiêu chí)
- [2026-11-25T00:41:01Z] [dcf-vn-redesign V3 25/11] XONG job Taylor_20261125_001435: nhánh session/Taylor_20261124_170355 commit 152e83c11 (wt-dcf-v3-20261125) — CHỜ Mike quant-skeptic V3 + user quyết (E/P hay mô hình cho cổng mềm; chọn ENS2 vs ENS1w)
- [2026-11-25T01:10:24Z] ĐANG DỞ: job Taylor_20261125_011012 dcf-earnings-forecast (phase1 kiểm kê+PRELOCK) | NEXT: worktree wt-dcf-earnfc-20261125d
- [2026-11-25T01:21:33Z] [dcf-earnings-forecast 25/11] XONG job Taylor_20261125_011012: nhánh session/Taylor_20261125_011012 cec37fa11 (wt-dcf-earnfc-20261125d) — D0imp tệ hơn naive, gap≈sai số earnings của D0, C2 không vượt E/P — CHỜ Mike quant-skeptic + chạy lại C sau V3.1
- [2026-11-25T01:30:05Z] [dcf-vn-redesign V3.1 25/11] XONG job Taylor_20261125_011009: commit 1a279d12f nhánh session/Taylor_20261124_170355 (wt-dcf-v3-20261125) — CHỜ Mike merge; luật §5 mong manh ENS2 vs ENS1 (KD 90/120 đổi chọn); nên GDKHQ đối chiếu mã vắng BQ còn mở
- [2026-11-25T01:47:52Z] ĐANG DỞ: job Taylor_20261125_014736 J3 earnings+chu kỳ (wt-dcf-earnfc-20261125d) | NEXT: vá J2 → PRELOCK addendum → chu kỳ
- [2026-11-25T02:01:39Z] [dcf-earnfc J3 25/11] XONG job Taylor_20261125_014736: nhánh session/Taylor_20261125_011012 1d74c6474 (wt-dcf-earnfc-20261125d) — B'/C' NO-GO, A' thiên lệch D0 đổi dấu theo pha; ứng viên PREREG 'neo theo độ chu kỳ' — CHỜ Mike quant-skeptic 1 vòng + user
- [2026-11-25T02:16:37Z] ĐANG DỞ: job Taylor_20261125_021625 J4 chu kỳ hướng C (wt-dcf-earnfc-20261125d, dir dcf_earnings_forecast_20261125e) | NEXT: đọc J3 → vá mc ảo → PRELOCK_J4 commit → chạy
- [2026-11-25T02:27:33Z] [dcf-earnfc J4 25/11] XONG job Taylor_20261125_021625: 8e467efab (wt-dcf-earnfc-20261125d, dir …20261125e) — NO-GO; M4 capex +0,0019 IC36 vs P1 3/4 năm (tiêu chí dừng không kích hoạt kỹ thuật, độ lớn ~0); panel V3.2 vá mc — CHỜ Mike skeptic + quyết A→B
- [2026-11-25T02:36:21Z] [dcf-earnfc J3.1 25/11] XONG job Taylor_20261125_022916: c82a9971b (wt-dcf-earnfc-20261125d, dir …20261125f) — REPORT kết luận cuối J1→J4; KL6 rút PREREG; C trên V3.2 không đổi kết luận — CHỜ Mike skeptic J3.1/J4 + ghi KB, rồi hướng B
