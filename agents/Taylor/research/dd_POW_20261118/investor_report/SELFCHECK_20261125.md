# SELFCHECK — POW investor report 25/11/2026 (bổ sung từ REPORT_rev5 Phụ lục F)
- PDF 10 trang (build_report.pdf), md5 76bdc8ca5e521f1738e55a2d46ec3075; HTML cùng tên (dry-run, KHÔNG gửi).
- Lint send_dd_report_email.py --dry-run: **2 vi phạm MD_LEDGER_MISMATCH** (md giữ tâm 9.792/vùng 7.166–12.419 của REV2; sổ giá hiện hành rev 2 = 9.387/6.966–11.808). **CHƯA đủ điều kiện gửi** — phải dựng lại phần định giá theo REPORT_rev4 trước. Đây là lệch có từ trước 25/11, không do vòng này tạo ra.
- Nội dung thêm: hình công suất, hình lãi vay, hộp độ nhạy nợ, bảng ba lớp, biên upside, dòng QHĐ8. Không còn dấu vết nguồn nhà môi giới (grep môi giới/vikki/đính chính/vòng N: rỗng). Hình cơ cấu điện hệ thống nằm riêng ở png/ (nội bộ), không vào bản NĐT.
- Số: model/calc_20261125_output.txt (chạy lại được bằng tools/calc_20261125.py). Lãi vay 9T/26: OCR TM21 gây nhập nhằng chữ số (1.509,1 đọc từ chuỗi "1.509.i29.13i.110"); tổng 1.535,7 ≈ 1.536 khớp con số đã dùng ở REPORT cũ.
