# SELFCHECK — POW investor report 26/11/2026 (dựng lại theo sổ rev 2 = REPORT_rev4 + rev5 Phụ lục F)
- PDF 11 trang, md5 3e91f8ff2e161eec9b29e5f634fd462d; md md5 41ec9b81f58d84f9d8323e7e4fe61d09. Số từ thân (trừ bảng/hình/phụ lục) ~1.520. KHÔNG gửi email.
- Email dry-run lint: 0 vi phạm, 1 cảnh báo SKEPTIC_NOT_CONFIRMED (sổ skeptic_final=REFUTED_OPEN). MD_LEDGER_MISMATCH: hết.
- dd_assumptions_lint --strict (assumptions rev4, md5 820f22c0...): 0 vi phạm, rc=0.
- dd_blind_lint --mode valuation (assumptions rev4 + model_rev3/rev4_inputs): rc=1, 2 vi phạm: (1) assumptions:3 TICKER (file khoá ghi tên mã), (2) model_rev3_inputs:25 chữ "vốn hoá FY25" = vốn hoá chi phí kế toán, không phải vốn hoá thị trường. Cả hai là file đã khoá 23/11, không sửa.
- Grep số REV2 (9.792/7.166/12.419/9.891) trong md và CSV hình: 0. img thiếu alt: 0. Render 11 trang xem bằng mắt.
- Giá: đóng cửa 25/11 13.300 (DNSE ohlc = BQ) ⇒ 1,42x; DNSE latest_trade 26/11 11:29:35 13.200 ⇒ 1,41x. ROE di sản hàm ý 13,66% (giải ngược calc_rev4).
- E15 in (9.861, +5,0%). E16 in (dd_history_label asof 20/11). E17 (V9) CHƯA in: sổ không có center_adj, dựng mới cần PREREG mù giá, ngoài phạm vi việc này.
- Chưa có: bảng g×Ke (REV4 không tính; g=0). ADV vẫn đo 18/11.
