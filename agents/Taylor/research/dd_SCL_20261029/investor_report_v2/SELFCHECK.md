# SELFCHECK — SCL_DD_investor_report_20261103 (03/11/2026)
- Số định giá đọc từ ../r3/calc/{model_r3_out.json, compare_r3_out.json, reverse_r3_out.json}; khoá md5 ../r3/calc/LOCK_md5_r3.txt (23:11:00 ICT) trước khi đọc giá/ADV; md5 model_r3_out.* không đổi sau khi chạy compare/reverse.
- grep luật 1/4/11/12/18 (tên nội bộ, tav2_bq, đính chính, bản cũ, 25.500…): rỗng ở md + EMAIL_SUBJECT.txt + PDF.
- PDF 9 trang; thân ≈1.290 từ không tiêu đề (wc_body.py).
- Thanh khoản tham chiếu 5 tỷ (quy ước fleet), bảng 1/5/10 tỷ; nhãn theo giá trị sau CK 5 tỷ.
- Email: send_dd_report_email.py --dry-run --html-out → to=user, 11 ảnh, 5,6MB; 0 thẻ <img thiếu alt. KHÔNG gửi thật.
