# Tự kiểm — TV1_DD_investor_report_20261102 (job Taylor_20261102_042930, 02/11/2026)

Lệnh tái lập (chạy từ `investor_report/`): `bash scripts/make_maps.sh` → `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all`;
banner: `python3 ~/.claude/skills/dd-investor-report/scripts/make_title_banner.py --title "<dòng 1 .md bỏ '# '>" --ticker TV1 --kicker "Báo cáo due diligence · UPCOM: TV1" --sub "Nhóm nghiên cứu · 02/11/2026" --logo figs/logo.png --out figs/title_banner.png`;
HTML: `python3 -I .../send_dd_report_email.py <md> --pdf <pdf> --banner figs/title_banner.png --dry-run --html-out TV1_DD_investor_report_20261102.html` (KHÔNG gửi — Mike gửi).
Giá 12T: `scripts/tv1_px_bq.csv` (bq `tav2_bq.ticker` alias t, 27/10/2025–30/10/2026; đóng cửa 30/10 = 19.800 khớp DNSE `../calc/dnse_raw.json`).

(a) Lộ nội bộ / trung tính — grep trên .md: `SpaceX|ZaloPay|giá vốn|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros` = 0 hit;
    `QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ cổ phiếu` = 0 hit. figs/*.csv = 0 hit. HTML (bỏ base64) = 0 hit.
(b) Độ dài: PDF 11 trang (thân 1–9, phụ lục 10–11). Số từ thân không tính bảng/hình = 1.214 (gồm bảng 2.433) ≤ ~1.800.
(c) Xem bằng mắt (render 1,4x): trang 1 (banner + hero + tear sheet), trang 7 (định giá: 2 bảng kịch bản/PV + bối cảnh lãi suất), trang 4 (bản đồ + ảnh) và toàn bộ 11 trang ở 0,6x:
    dấu tiếng Việt đúng, bảng không tràn. Đã sửa: tiêu đề hero bị cắt; nhãn chú thích đè cột (hình 01, 03); nhãn trục bị cắt (06, 08, 09); glyph mũi tên thiếu (03);
    ảnh hero mây che → đổi ảnh lưới điện; dấu * hiển thị thô; tiêu đề “Ba điều cần biết” mồ côi cuối trang 1 → sang trang 2.
    Còn: nhãn bản đồ ghép nhỏ khi in (đọc được khi phóng to); trang 9 (mục 10) chỉ đầy ≈1/3; trang 7 bảng kịch bản tách khỏi tiêu đề mục 7 (bảng giữ nguyên khối).
(d) Số khớp ../REPORT.md (vòng 2) + ../calc/valuation_out.txt + ../calc/rate_lines.txt: quét tự động 171 chuỗi số trong thân (trước Phụ lục E) — 4 không có nguyên văn trong nguồn,
    đều có nguồn khác: 20.000 (tham chiếu 02/11 = "20,0" trong REPORT §1), 46% và 18.000–20.500 (tính từ giá 12T: đỉnh 36.550 ngày 25/03/2026; min/max từ 15/07),
    57,76 (Q1+Q2/26 dữ liệu tổng hợp = 32,23 + 25,53, khớp H1 soát xét 57,759). "≈3/4 mức giảm trước khởi tố" = (36.550 − 24.400 đóng cửa 06/05) / (36.550 − 19.800) = 72,5%.
    Kiểm thủ công: PV 19.200–20.600, giá −4%…+3%; EV chưa CK 21.600; cơ sở 13.500–29.000 (tâm 20.100); tốt 28.500–38.700; xấu 10.800–15.100; SOTP 23.900/44.200;
    lõi Q3 16–45; CFO Q3 69,8; dự phòng −24,9 (KH 90,81→68,36); P/E 2,8 / 3,2–3,8; P/B 0,92 / 1,04; Ke 12,3–13,4%; r* 15,1% / TPCP 4,58% (+0,64).
    Ở giá tham chiếu 20.000: 20.000/20.600 − 1 = −2,9%, 20.000/19.200 − 1 = +4,2% ⇒ "−3%…+4%", kết luận không đổi.
(e) Số cũ bị đính chính (62,5; 27,5 dự phòng; "tăng 63,2→68,4"; 36–44; +7%; 3,24x; 125–155; 16.400–26.100; "thấp hơn ~10%"; 24.300/44.700) chỉ còn ở cột "Trước" Phụ lục E.
    Hai trùng hợp hợp lệ: 27,5 = QLDN 9T/25 (Phụ lục A); 16.400 = ô 125 tỷ × 3,5x trong lưới độ nhạy.
(f) HTML dry-run: 13 `<img`, 0 thiếu/vỡ alt; người nhận = địa chỉ trong secrets; 8,7 MB. Tiêu đề không có nháy kép thẳng (dùng “ ” trong thân).

Luật 15: bản đồ khu vực miền Trung (Quảng Nam cũ/Đà Nẵng) + Hà Nội, KHÔNG toàn quốc. Toạ độ: Sông Bung 5 = Global Energy Monitor wiki (15,8077; 107,7472; xã Mà Cooih–Thạnh Mỹ theo thông báo đấu giá — báo Đấu thầu);
  trụ sở 66 Lương Ngọc Quyến, phường Thanh Liệt (địa chỉ: footer pecc1.com.vn, WebFetch 02/11) → OSM Nominatim (20,9841; 105,7950); Đà Nẵng (MTV3, cấp thành phố) → OSM (16,0685; 108,2240).
  Ảnh: 3 banner trang chủ pecc1.com.vn (`../src/web/`, cắt phần không có khung chữ), ghi "minh hoạ lĩnh vực, không xác định công trình". BCTC đều là bản scan, không có ảnh sản phẩm trích được; chưa có BCTN 2025.
  Logo: pecc1.com.vn/images/logo.png → `../src/logo.png`, `figs/logo.png`.
Chưa làm (ngoài phạm vi dispatch): ghi `kb/dd_price_zones.json` — để Mike làm khi gửi email.
