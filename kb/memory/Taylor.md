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

- [2026-10-25T13:11:09Z] ĐANG DỞ job Taylor_20261025_131052: BAL EVEB phase2 (V0-V4 replay R3) → agents/Taylor/research/bal_eveb_phase2_20261025/ | NEXT: đọc REPORT lag_bal + skeptic, registry 2026-10-08, worktree, PREREG
- [2026-10-25T13:15:14Z] ĐANG DỞ job Taylor_20261025_131052: batch 10 run nền (wt-bal-eveb-phase2-20261025, logs/run_batch.log), PREREG 604786eb3 | NEXT: verify ctl md5 537e349b/a6ba34d8, evaluate.py, bootstrap, REPORT
- [2026-10-25T13:18:08Z] [trend-basics-filter 10-25] XONG job Taylor_20261025_131054 (413f67e26): 1/39 đạt (LAG×up60) = hiệu ứng mã đứng giá, không phải xu hướng; value×xu hướng không thêm — chờ quant-skeptic nếu Mike muốn
- [2026-10-25T13:49:05Z] ĐANG DỞ job Taylor_20261025_131052: 10 run PREREG xong (0/4 đạt), đang chạy 8 run amendment A1 wv1-4 (logs/run_batch3.log, commit 04ec38d61) | NEXT: evaluate.py → REPORT.md → bus finding
- [2026-10-25T14:05:27Z] ĐANG DỞ job Taylor_20261025_140517: lag-capacity-floor R1(KL T-1/trung vị N)/R2(bỏ ABANDONED_REFUND)/R3(noise floor park=0) trên wt-lag-capacity-floor-20261025 | NEXT: PREREG_R.md
- [2026-10-25T14:09:30Z] ĐANG DỞ job Taylor_20261025_140517: 54 run R nền (wt-lag-capacity-floor, logs/run_batch_R.log), PREREG_R ddcc86747 | NEXT: analyze_R.py, verify ctl md5, REPORT_R, 3 bus finding R1/R2/R3
- [2026-10-25T14:13:07Z] [bal-eveb-phase2 10-25] XONG job Taylor_20261025_131052: 0/8 dat, NO-GO (885b2c944, nhanh research/bal-eveb-phase2-20261025, chua merge); BAL xep theo ta, khong co yieldcombo — CHO Mike/user: dong nhanh BAL x dong tien, co ghi registry no_ledger khong
- [2026-10-25T16:00:13Z] [lag-capacity-floor R 10-25] XONG job Taylor_20261025_140517 @ce26d14e3 (chua merge): dai thuc thi 50 ty san 11,86..22,61/tran 14,74..25,40; san nhieu park0 1,57pp — CHO Mike/user
- [2026-10-25T17:25:49Z] ĐANG DỞ job Taylor_20261025_172538: lag-capacity S1(ΔIS/ΔOOS)/S2(đọc code live defer vs bỏ)/S3(trần KL mở cửa + slippage) trên wt-lag-capacity-floor-20261025 | NEXT: đọc REPORT_R/PREREG_R/out_R_metrics.csv
- [2026-10-25T17:34:56Z] ĐANG DỞ job Taylor_20261025_172538: S1 3cdefe417 + S2 fe910d1e5 xong (bus); S3 batch 24 run nền từ 00:33 (wt-lag-capacity-floor, logs/run_batch_S.log), PREREG_S 1e909f719 | NEXT: analyze_S.py → REPORT_S §S3 → bus S3 + 'S ket luan'
- [2026-10-25T18:23:10Z] [lag-capacity-floor S 10-26] XONG job Taylor_20261025_172538 @148b84685 (chua merge): band 50 ty ~11,7-20,7/14,6-23,8, trung tam 18,5-20,7/21,2-23,8, chi phi IS -4,2..-4,4pp — CHO Mike/user: co chay bien the doi 3 phien + cong gia anchor khong
- [2026-10-26T01:34:42Z] [dd-NNC 10-26] XONG job Taylor_20261026_012529: NON (khong fear-state, dinh chu ky, PB1,59); weighted 62,8k vs 47,6k. REPORT research/dd_NNC_20261026/. Meo: BCTC scan -> pip --target /tmp/pdflib pypdf, trich anh trang roi Read anh
