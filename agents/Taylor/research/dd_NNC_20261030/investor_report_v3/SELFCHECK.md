# Tự kiểm — NNC_DD_investor_report_20261103 (r5, job Taylor_20261103_134709, 03/11/2026)
md5 md f45eaf012f010f73d8880030680a60ca · pdf 97315bdd71dabe05e575a9f469c16642 · html 5eff692c699f344feef4542dd2426e9a · PDF 11 trang.
Dựng: `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all` (hình định giá 00/12/13/14/23 đọc ../r5/calc/nnc_model_r5_out.json + extras_r5_out.json +
compare_r5_out.json; khoá ../r5/calc/LOCK_md5_r5.txt 20:49:47 ICT). Hình 01–10, 18–22 giữ nguyên. Banner dựng lại (make_title_banner.py; tiêu đề = dòng 1 md).
## Kiểm
- grep luật 18 + luật 4/12 (SpaceX|ZaloPay|Taylor|Bobby|Mike|skeptic|QUALIFY|§2.5|fear|đính chính|thay bản|trước đây|đã sửa|vòng N|rN|bản trước|phiên bản) trên md + EMAIL_SUBJECT: rỗng.
- Dry-run email --html-out: to=dtienthanh@gmail.com, 16 ảnh, 9,5 MB, 16/16 <img> alt. KHÔNG gửi thật.
- Nhìn bằng mắt: hình 13 (football field, Gordon 2 chiều dưới giá).
- Số trên md khớp nnc_model_r5_out.txt / compare_r5_out.txt / extras_r5_out.json (làm tròn trăm). Giá 46.100 = DNSE close G1 03/11.
## Giới hạn
- Thời hạn thuê Núi Nhỏ (giả định 2043) và bản chất trả trước 59,2 tỷ: CHƯA XÁC MINH (BCTC scan) — nêu ở mục 5 + Phụ lục D.
- fundamental-skeptic CHƯA chạy trên r5.
