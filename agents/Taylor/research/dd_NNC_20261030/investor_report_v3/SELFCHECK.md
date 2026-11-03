# Tự kiểm — NNC_DD_investor_report_20261103 (r6, job Taylor_20261103_152936, 03/11/2026)
md5 md efa9d87c9408ad3d704b3a4d7bdd2564 · pdf 0137f629a9f90feba4db765e43a741ac · html ac0257d9ff15b3381bec44b52e0416e9 · PDF 11 trang.
Dựng: `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all` (hình 00/12/13/14/23 đọc ../r6/calc/nnc_model_r6_out.json + extras_r6_out.json + compare_r6_out.json;
khoá ../r6/calc/LOCK_md5_r6.txt 22:31:57 ICT). Hình 01–10, 18–22 giữ nguyên. Banner dựng lại (tiêu đề = dòng 1 md).
## Kiểm
- grep luật 18 + bước 4 (SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros|QUALIFY|AMBIGUOUS|NON|§2.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đính chính|thay bản|trước đây|đã sửa|bản trước|phiên bản|rN) trên md + EMAIL_SUBJECT: rỗng. ("quỹ" chỉ xuất hiện như quỹ khen thưởng/đầu tư phát triển.)
- Thân (không bảng, không ảnh) ≈1.800 từ (cách đếm split trước Phụ lục A).
- Dry-run email --html-out: to=dtienthanh@gmail.com, 16 ảnh, 9,6 MB, 16/16 <img> có alt. KHÔNG gửi thật.
- Số trên md khớp nnc_model_r6_out.txt / compare_r6_out.txt / liquidity_r6_out.txt / extras_r6_out.json / report_nums_r6.txt (làm tròn trăm).
## Giới hạn
- KHÔNG render được PDF ra ảnh để nhìn bằng mắt trong phiên (máy thiếu pdftoppm/PyMuPDF/pypdfium2) — Mike nên mở PDF kiểm bảng thanh khoản/lãi suất trang định giá.
- Thời hạn thuê Núi Nhỏ (2043) và bản chất trả trước 59,2 tỷ: CHƯA XÁC MINH. Hệ số tác động thanh khoản Y=1 là giả định từ nghiên cứu, không hiệu chỉnh bằng lệnh thực tế cho NNC.
- fundamental-skeptic CHƯA chạy trên r6.
