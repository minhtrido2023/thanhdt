# Tự kiểm — NNC_DD_investor_report_20261103 (job Taylor_20261103_132045, 03/11/2026)
md5 md c4a8946405f68fcb4fc5857ea505d552 · pdf d7a83986b1346368703ee172be3c3f9a · html 9d1dda20dc5473c71b6a2e88d2beb6f0 · PDF 11 trang.
Dựng: `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all` (hình định giá 00/12/13/14/23 đọc ../r4/calc/model_r4_out.json + extras_r4_out.json +
compare_r4_out.json; khoá ../r4/calc/LOCK_md5_r4.txt 20:24:58 ICT). Hình 01–10, 18–22 giữ nguyên. Banner: make_title_banner.py (tiêu đề = dòng 1 md).
## Kiểm
- Thân ~1.286 từ (bỏ bảng/tiêu đề/ảnh/phụ lục) ≤ 1.800.
- grep luật 18 + luật 4/12 (đính chính|thay bản|trước đây|đã sửa|vòng N|rN|sai sót|bobby|skeptic|QUALIFY|fear|bản trước|phiên bản) trên md + EMAIL_SUBJECT: rỗng.
- Dry-run email --html-out: 16 ảnh, 9,5 MB, 16/16 <img> alt đóng. KHÔNG gửi thật.
- Nhìn bằng mắt: 11 trang (50 dpi), trang 1 (80 dpi), hình 00/13/14 (200 dpi).
- Số trên md khớp model_r4_out.txt / compare_r4_out.txt / extras_r4_out.json (làm tròn trăm). Giá 46.100 = DNSE close G1 03/11.
## Giới hạn
- Gordon trong hình 13 là bản bổ sung SAU khoá (cộng LN tài chính sau thuế) — không đổi tâm/thang.
- fundamental-skeptic CHƯA chạy trên r4.
