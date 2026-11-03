# SELFCHECK — báo cáo DD MVC 03/11/2026 (dựng lại trong phiên Taylor_20261103_093502)
- r4 (job Taylor_20261103_095718): PDF 11 trang, md5 dc70b3e338e1121ceea0f47534fadcad; md md5 691a82984309acc3478182704fbe330f. Dựng: venv python build_report.py pdf; banner qua make_title_banner.py (tiêu đề = dòng 1 md). Thang ngưỡng mới: biên an toàn ≤13.000 / có điều kiện 13.000–17.500 / hợp lý 17.500–22.900 / đắt ≥25.400 (số: ../r4/ext_r4_out.txt).
- Số khớp REPORT.md nội bộ (r3): tâm 20.181 (hiển thị ≈20.200); ngưỡng P10/P25/P75/P90 = 15.261/17.471/22.946/25.383 (hiển thị 15.300/17.500/22.900/25.400); kịch bản (phẳng·g2031·thực) 29.658·36.212·44.664 / 9.772·14.605·20.248 / 7.707·8.447·10.083; dải kịch bản P10–P90 8.291–39.975. Hình đọc trực tiếp ../r3/calc/model_r3_out.json. Khoá md5 ../r3/calc/LOCK_md5_r3.txt: `md5sum -c` 11 file trước khoá OK.
- grep luật 18 (đính chính|thay bản|trước đây|đã sửa|vòng N|\brN\b|sai sót|bản trước) trên md / html (bỏ base64) / subject: 0 dòng. Chú thích hình không còn đường dẫn phiên bản nội bộ.
- grep tên nội bộ (SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros|fleet) và nhãn fear-buy (QUALIFY|AMBIGUOUS|NON|§2.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ): 0 dòng.
- Email dry-run (--html-out): to=dtienthanh@gmail.com, 16 ảnh, 8,4MB, mọi <img có alt; KHÔNG gửi thật.
- Đọc mắt PDF trang 1, 7, 8, 10 (render PNG 70 dpi): dấu tiếng Việt đúng, bảng không tràn; đã sửa 2 tiêu đề hình bị cắt (fig_11, fig_12).
- Luật 15: 2 bản đồ + 2 khung ảnh sản phẩm giữ nguyên. Luật 17: r* 15,1% + TPCP 10Y 4,58% giữ nguyên (nguồn ghi "chưa đối chiếu độc lập").
- Sổ mức giá: kb/dd_price_zones.json MVC rev 2 (zone 17.500–22.900, tâm 20.200, center_alt cơ sở 14.600); rev 1 chỉ đổi con trỏ nguồn sang archive_internal/ (bản gốc git 3f0e3dc2f); dd_price_zones_selfcheck.py: lỗi 0.

- Thân (không bảng/hình/phụ lục): 1.811 từ (cũ 2.211; mục tiêu ≈1.800). grep luật 18 + tên nội bộ + 'rẻ rõ' trên md/html/subject: 0 dòng. Email dry-run --html-out: 16 ảnh, mọi <img có alt; KHÔNG gửi thật. Đọc mắt trang 1 và trang 10 (ngưỡng) OK.
## r5 (job Taylor_20261103_100718) — đổi nguyên tắc: dự án mới = giá vốn ở base
- PDF 10 trang md5 30e9b5e3a83f00f9995408a4bef4bbb3; md md5 dc28037bb8651d5a94cbe7248093b255. Dựng: venv python -I build_report.py all; banner make_title_banner.py (tiêu đề = dòng 1 md). Hình đọc ../r5/calc/model_r5_out.json (khoá ../r5/calc/LOCK_md5_r5.txt 17:15:01, md5sum -c 6/6 OK).
- Số khớp REPORT.md r5: tâm 25.725 (≈25.700); lưới P10/25/75/90 21.824/23.622/28.829/31.565 (hiển thị 21.800/23.600/28.800/31.600); cơ sở 24.199; stress 20.316; kịch bản (g2031·thực) 37.155·45.916 / 22.484·25.914 / 12.112·13.822.
- Thân (không bảng/hình/phụ lục) 1.814 từ. grep luật 18 + tên nội bộ + 'rẻ rõ' trên md / html (bỏ base64) / subject: 0·0·0. Không còn câu "đầu tư mới ⇒ giảm giá trị" (luật 20); mua NNC 51% bỏ con số dựa giá thị trường.
- Email dry-run --html-out: to=dtienthanh@gmail.com, 16 ảnh, 8,6MB, mọi <img có alt; KHÔNG gửi thật.
- Đọc mắt PDF trang 1, 6, 9 (70 dpi): dấu tiếng Việt đúng; bảng không tràn. Hình 00/10/11/12/13/14 dựng lại; 09 bỏ cột mua NNC (chưa có giá).
- Sổ mức giá kb/dd_price_zones.json MVC rev 4 (zone 23.600–28.800, tâm 25.700, center_alt cơ sở 24.200, giá 13.300 03/11); rev 3 chỉ đổi con trỏ sang archive_internal/..._rev3.md; dd_price_zones_selfcheck.py lỗi 0.
## r6 (job Taylor_20261103_103341) — sửa đối xứng sau SKEPTIC4
- PDF 11 trang md5 f69eef686484512d051f526fd70ea6a5; md md5 e69a9f0824e0fc49d9e401ae6945a706. Dựng: venv python -I build_report.py all/pdf; banner make_title_banner.py (tiêu đề = dòng 1 md). Hình đọc ../r6/calc/model_r6_out.json (khoá ../r6/calc/LOCK_md5_r6.txt 17:37:37, md5sum -c 6/6 OK).
- Số khớp REPORT.md r6: tâm 23.093 (≈23.100); P50 19.755 (≈19.800); lưới P10/25/75/90 15.586/17.345/22.540/25.132 (hiển thị 15.600/17.300/22.500/25.100); cơ sở 22.942; stress biên 16.622; phẳng 19.010; hai phía mỏ mới 22.170; kịch bản (g2031·thực) 32.358·37.200 / 21.227·24.657 / 10.854·12.565.
- Thân trước Phụ lục bỏ bảng/hình (cách đếm python split): 1.966 từ; bản r5 cùng cách đếm 1.969 (r5 báo 1.814 theo cách đếm khác) ⇒ tương đương ≈1.810.
- grep luật 18 + tên nội bộ trên md / html (bỏ base64) / subject: 0·0·0. Không còn: chi phí vốn hỗn hợp 5,98%/4,6%, "thị trường chưa tính 23,5 ha", ngưỡng nợ ròng 600 tỷ tuyệt đối, "biên an toàn" trơn.
- Email dry-run --html-out: to=dtienthanh@gmail.com, 16 ảnh, 8,6MB, mọi <img có alt; KHÔNG gửi thật.
- Đọc mắt PDF trang 1, 7, 9 (70 dpi): sửa nhãn hero "rẻ, biên an toàn có điều kiện"; tornado mở trục −10.500; nhãn stress hình 11 bị đẩy ra ngoài khung (đường vẫn hiện) — tồn.
- Sổ mức giá kb/dd_price_zones.json MVC rev 5 (zone 17.300–22.500, tâm 23.100, center_alt trung vị 19.800); rev 4 chỉ đổi con trỏ sang archive_internal/..._rev4_r5.md; selfcheck lỗi 0.
## r7 (job Taylor_20261103_132045, 03/11/2026)
- PDF 12 trang md5 c7a09871092a84b166a06ed2b287d402; md md5 10973bc6819173e0018ae335f4db3bef; html 24a134f209a17a044ec195f16cbe2246.
  Dựng: venv python -I build_report.py all + make_title_banner.py (tiêu đề = dòng 1 md). Hình đọc ../r7/calc/model_r7_out.json + compare_r7_out.json (khoá LOCK_md5_r7.txt 20:33:44).
- Thân (trước Phụ lục, bỏ bảng/tiêu đề/ảnh) 1.796 từ. grep luật 18/4/12 trên md + subject: rỗng. Dry-run email --html-out: 16 ảnh, 8,6 MB, 16/16 <img> alt. KHÔNG gửi.
- Nhìn bằng mắt: 12 trang (50 dpi), trang 1 (80 dpi), hình 00/10/11/12/13. Số khớp model_r7_out.txt / compare_r7_out.txt (làm tròn trăm).
- fundamental-skeptic CHƯA chạy trên r7.
- r8 (job Taylor_20261103_134709): PDF 12 trang md5 bc4e3897bd42e2ca753cd2e290c025b7; md md5 55896917d139f2585fea5bddc5e237fb; html b7c8c280d6565d14c1bbd46a0ccca271. Dựng: venv python -I build_report.py figs/pdf; banner make_title_banner.py (tiêu đề = dòng 1 md, logo src_img/logo.jpg). Hình đọc ../r8/calc/model_r8_out.json + compare_r8_out.json (khoá ../r8/calc/LOCK_md5_r8.txt 20:58:31). Thân trước Phụ lục 1.807 từ. grep luật 18/4/12 + QUALIFY/§2.5/rẻ rõ trên md + subject: rỗng. Email dry-run --html-out: to=dtienthanh@gmail.com, 16 ảnh, 8,6 MB, 16/16 <img> alt; KHÔNG gửi thật. Nhìn mắt hình 12 (tornado, sửa tiêu đề tràn). fundamental-skeptic CHƯA chạy trên r8.

- r9 (job Taylor_20261103_152936): PDF 12 trang md5 1652bb6cc9bce2da5a40b991860f7451; md 118ff7edfa3c1338d9683f0d95aa672d; html 5c8734d82ffefc38afdbd9913543f479. Hình đọc ../r9/calc/model_r9_out.json + compare_r9_out.json
  (khoá ../r9/calc/LOCK_md5_r9.txt 22:38:41); hero + football field vẽ thang SAU chiết khấu thanh khoản 8,4% (vị thế 5 tỷ). Thân trước Phụ lục 1.803 từ (cùng cách đếm r8 1.807).
  grep luật 18/4/12 + QUALIFY/§2.5/rẻ rõ/rN trên md + subject: rỗng ('quỹ' chỉ = quỹ khen thưởng). Email dry-run --html-out: 16 ảnh, 8,7 MB, 16/16 <img> alt; KHÔNG gửi.
  KHÔNG render được PDF ra ảnh trong phiên (thiếu pdftoppm/PyMuPDF/pypdfium2) — Mike mở PDF kiểm bảng lãi suất/thanh khoản mục 5. fundamental-skeptic CHƯA chạy trên r9.
