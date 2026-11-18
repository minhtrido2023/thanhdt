# SELFCHECK — POW investor report 18/11/2026
- PDF: POW_DD_investor_report_20261118.pdf, 9 trang (fitz), md5 4823098cfdea170f1db1252b54fdc198. HTML: POW_DD_investor_report_20261118.html (send_dd_report_email.py --dry-run --html-out; KHÔNG gửi). Email dry-run: 11 ảnh, 12,4MB.
- Số từ thân (trừ bảng/hình/phụ lục): 1.096 (≤1.800 ✔).
- grep bước 4 (a) tên nội bộ: rỗng ✔; (b) nhãn QUALIFY/NON/fear/kiểm định…: rỗng ✔; luật 18 (đính chính/vòng N/r[0-9]…): rỗng ✔ (md + html đã bỏ base64).
- <img> thiếu alt: 0 ✔.
- Render trang 1, 5, 7 xem bằng mắt: dấu tiếng Việt đúng, bảng không tràn, banner + hero + ảnh BCTN hiển thị.
- Giá: DNSE latest_trade 13.500 (18/11/2026 11:29:50) vs đóng cửa 13.250 ⇒ giá/tâm 1,38× (1,35× tại 13.250); kết luận không đổi (trên vùng giá trị hợp lý). ROE di sản hàm ý 12,6% @13.250 / 12,9% @13.500 (model/calc_output_rev2.txt).
- Giới hạn: không có LN theo nhà máy; giao dịch bên liên quan chưa đọc; 3 con số sản lượng khác định nghĩa; PDF 5,3MB (ảnh).
- Ghi chú: pymupdf không có trong wc_venv hiện tại (build trước đó đã tạo PDF); render kiểm dùng python3 fitz.
