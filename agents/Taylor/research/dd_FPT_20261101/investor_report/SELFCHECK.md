# Tự kiểm — FPT_DD_investor_report_20261101 (job Taylor_20261101_101423, 01/11/2026)

Lệnh: `bash scripts/make_maps.sh` → `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all` (hình + PDF);
banner: `make_title_banner.py` (python3 thường) với tiêu đề = dòng 1 của .md, logo `../src/logo.png`;
HTML: `send_dd_report_email.py ... --dry-run --html-out` (KHÔNG gửi — Mike gửi).

1. Lộ thông tin nội bộ: `grep -i -E "SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros"` trên .md = **0 hit**; trên .html (bỏ base64) = 0.
2. Ngôn ngữ trung tính: `grep -i -E "QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ"` trên .md = **0 hit**.
3. Số khớp `../REPORT.md` v2 + `../calc/valuation_out.txt`: figs_part.py tính lại cùng công thức, in ra kịch bản 34.057 / 59.833 / 79.581, kỳ vọng 54.761,
   vùng cơ sở 54.987–66.705 — trùng từng đồng với valuation.py. Giá 52.700 DƯỚI vùng ≈4%. Tỷ lệ chuyển tiền 1,07 / 0,60 / 0,34 / −0,12 (calc §3b).
   Số v1 đã bị đính chính (51–62k, 0,12 đồng/đồng lãi, 40,1k, 84,6k, DSO 72, "doanh thu chưa lập hoá đơn", 618,8 tỷ = trả trước khách Anh) chỉ còn ở cột "Trước" Phụ lục E.
4. Luật 16: **10 trang A4** (thân 1–8, phụ lục 9–10); số từ thân không tính bảng/hình = **703** (gồm bảng: 1.667).
5. Luật 9/13/14: tiêu đề 1 câu hai vế, không nháy kép thẳng; banner có logo fpt.com (`/fpt-logo.svg`, đổi class CSS sang fill để render màu đúng); font Be Vietnam Pro;
   glyph thiếu (→, ∝) đã thay. Ke 12,3–13,4% (dải bảng 12,3–15,8%), 15,8% ghi nhãn "nước ngoài (USD)".
6. Luật 15: 3 bản đồ VÙNG (Bắc / Trung / Nam, geoBoundaries ADM1, KHÔNG toàn quốc); toạ độ OSM Nominatim 01/11/2026 (Trụ sở 10 Phạm Văn Bạch, ĐH FPT Hòa Lạc,
   FPT Complex + ĐH FPT Đà Nẵng, ĐH FPT TP.HCM, ĐH FPT Cần Thơ); Quy Nhơn cấp thành phố (Wikipedia); Bình Dương/Long An không có vị trí công bố ⇒ chỉ tô tỉnh, không vẽ điểm.
   Ghi "Bình Định cũ, nay thuộc Gia Lai". Thị trường xuất khẩu = sơ đồ vector (không nền bản đồ thế giới), cỡ chấm tỷ lệ doanh thu 9T: Nhật 13.197 / Mỹ 6.485 / EU 3.422 / APAC 5.434.
   Khung 5 ảnh trích BCTN 2025 FPT (trang PDF 26, 50, 54, 74, 99) bằng pymupdf extract_image; hero = trang PDF 23. Ảnh máy chủ chú thích là mảng nay thuộc liên kết FPT Telecom.
7. HTML: 13 `<img`, 0 thiếu alt, 0 thẻ hỏng; dry-run: to=địa chỉ trong secrets, 13 ảnh, 12,2 MB (lớn; Mike cân nhắc nén nếu bị chặn).
8. Xem bằng mắt (render 85–110 dpi): trang 1 (banner + logo màu, hero KPI, football field), trang 3–4 (ngành, sơ đồ xuất khẩu, bản đồ), trang 5 (ảnh, 5a–5b),
   trang 7 (định giá + rủi ro). Đã sửa sau lần xem: nhãn Nhật/APAC chồng bong bóng; nhãn trục đè nguồn (hình 1, 10); nhãn ma trận rủi ro chồng nhau;
   tiêu đề football field sai ("dưới mọi vùng" — thực tế giá nằm trong dải SOTP và P/E); logo render đen; bản đồ 3 cột quá nhỏ ⇒ 2 hàng.
   Còn: bản đồ miền Trung nhỏ chữ (đọc được ở PNG gốc); trang 3 và 4 có khoảng trống cuối trang; Investment Summary nằm đầu trang 2 (trang 1 = banner + hero KPI + football field).
9. Giá: DNSE latest_trade khớp cuối 30/10/2026 14:45:03 = 52.700 (01/11 Chủ Nhật, không có phiên); giá còn quyền cổ tức 1.000 đ, mọi giá trị so cùng gốc.
10. Mỗi hình số liệu có CSV trong `figs/` (12 CSV; bản đồ: `fig_05_maps.csv` gộp `scripts/pts_*.csv`; ảnh: `fig_06_photos.csv` ghi trang nguồn).
