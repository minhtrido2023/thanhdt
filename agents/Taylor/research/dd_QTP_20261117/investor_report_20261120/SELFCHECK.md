# SELFCHECK — QTP investor report 20/11/2026 (job Taylor_20261120_092932)
- Nguồn số: qtp_r3_envcapex_20261120/REPORT_r3c.md + qtp_model_r3c.py (md5 6d80cb978eb340fec7c9c26eaf0ec2a5); trích bằng extract_model_numbers.py -> figs/model_numbers.json; build_report.py assert tâm 7.701/8.557 khớp mô hình.
- Số mới tính bằng mô hình (không có trong REPORT_r3c): ±50bp 8.787/7.908 và 8.338/7.504; lưới 3x3 kịch bản vận hành × bù giá (trước CK); tiền ròng P50/P100 cổ tức 900.
- Lãi huy động 12T hiệu dụng 19/11/2026 = 7,40% (deposit_rate_vn, CCTG 12M 02/11). Dòng r*/TPCP: dcf_rate_display('2026-11-19').
- PDF 11 trang (thân ~8,5, phụ lục ~2,5); md5 PDF cdedcf1fd7c99baad596294d993b3b02; md5 md 1aba777144e1d0534c6e47b7a422b22a.
- Grep luật 1/4/11/12/18 trên md + subject: rỗng. HTML: 13 hit chỉ nằm trong dữ liệu base64 ảnh; bỏ base64 thì rỗng. Mã rủi ro đổi R1..R7 -> #1..#7 để không chạm mẫu \br[0-9] (-i).
- Font: Be Vietnam Pro thiếu glyph → ⇒ nên md/hình không dùng hai ký tự này.
- Kiểm bằng mắt: trang 1 (banner+hero+KPI), 5 (mục 6 dự án), 7 (định giá) — dấu tiếng Việt đúng, bảng không tràn.
- send_dd_report_email.py --dry-run: to=địa chỉ user trong secrets, 13 ảnh, 6,1MB, KHÔNG gửi.
- Giới hạn còn mở: GPMT 517 phụ lục; lãi suất NQ 105; 115 tỷ/năm FS chưa thuyết minh.
