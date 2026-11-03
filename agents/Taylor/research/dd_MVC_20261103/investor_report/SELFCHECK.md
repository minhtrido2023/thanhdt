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
