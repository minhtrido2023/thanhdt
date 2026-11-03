# Tự kiểm — NNC_DD_investor_report_20261103 (job Taylor_20261103_130007, 03/11/2026)
md5 md 9cbf5ca9dd8f5308ad8ba7f43c843e73 · pdf 3e266097ac7f3a41f3923a4395a1c667 · html 93529f0b32b22f3b3ff6abe535307094 · PDF 10 trang.
Dựng: `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all` (hình định giá 00/11/12/13/14/23 đọc ../r3/calc/model_r3_out.json; khoá ../r3/calc/LOCK_md5_r3.txt
20:04:30 ICT, md5sum -c 8/8 OK). Hình 01–10, 18–22 dựng lại bằng _base_v2.py (bản sao khuôn 31/10, chỉ sửa ô KPI P/E·P/B theo giá 03/11 và ngày ở đầu trang).
Banner: make_title_banner.py (tiêu đề = dòng 1 md; logo ../src/logo.png).
## Kiểm
- Thân ~1.087 từ (bỏ bảng/tiêu đề/ảnh/phụ lục) ≤ 1.800.
- grep luật 18 + luật 4/12 (đính chính|thay bản|trước đây|đã sửa|vòng N|rN|sai sót|tên nội bộ|QUALIFY|fear|kiểm định|xung đột lợi ích…) trên md + EMAIL_SUBJECT: rỗng.
  Trên HTML có 13 hit — đều là chuỗi base64 ảnh nhúng (đã xem), không phải chữ.
- Dry-run email --html-out: tới địa chỉ user trong secrets, 16 ảnh, 9,4 MB, 16/16 <img> alt đóng đúng. KHÔNG gửi thật.
- Nhìn bằng mắt: cả 10 trang (60 dpi) + hình 00/11/12/13/14/23 (200 dpi): dấu đúng, nhãn không chồng sau khi chỉnh, bảng không tràn.
- Số trên md khớp model_r3_out.txt / compare_r3_out.txt (làm tròn trăm). Giá 46.100 = DNSE close 03/11, khớp BQ ticker.Price 03/11.
## Giới hạn
- Hình 10 (mỏ cụm), 19–22 (bản đồ, ảnh) giữ nguyên bộ 31/10 (nguồn ghi trong CSV đi kèm). Bỏ hình cơ cấu cổ đông (tiêu đề cũ bị cắt) — thay bằng 1 câu.
- fundamental-skeptic CHƯA chạy trên r3.
