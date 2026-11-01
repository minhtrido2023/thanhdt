# Tự kiểm — SIP_DD_investor_report_20261101 (job Taylor_20261101_100247, 01/11/2026)

Lệnh: `bash scripts/make_maps.sh` → `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all` (hình + PDF);
banner: `make_title_banner.py` (python3 thường) với tiêu đề = dòng 1 của .md, logo `../src/logo.png`;
HTML: `send_dd_report_email.py ... --dry-run --html-out` (KHÔNG gửi — Mike gửi).

1. Lộ thông tin nội bộ: `grep -i -E "SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros"` trên .md = **0 hit**; trên .html (bỏ base64) = 0.
2. Ngôn ngữ trung tính: `grep -i -E "QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ"` trên .md = **0 hit**.
3. Số khớp `../REPORT.md` v2 (đã áp 11 đính chính, §11) — figs_part.py exec chính `../calc/valuation.py`, in ra:
   kịch bản 77.517 / 49.235 / 25.357; tâm 47.728 (20/50/30) / 50.336 (25/50/25); hộp sai số 34.637–57.459 — khớp `../calc/valuation_out.txt` từng đồng.
   EPS TTM 5.184, P/E 9,33; P/E 8–10x → 41.472–51.840; ròng tài chính 4.412,3; tín dụng phi NH 6.015,8 = 116% VCSH mẹ.
   Ma trận tín dụng × đất (fig_09) và bảng Ke dùng `base_with()` của valuation.py; Ke 12,3/13,0/13,4% → 51.721/49.471/48.295 (P/E ≈1/(Ke−2%)).
   "Đổi ý": tích cực = base_with(lỗ 0, 16 tỷ/ha, thu hồi 90%[, CK 5%]) 55.634–58.724 (ghi ≈54.000–58.700 gồm cả 54.058 chỉ đổi lỗ+đất); tiêu cực 41.185 (lỗ 30%, 8 tỷ/ha) – 45.202 (lỗ 30%).
   Số bị phản biện sửa (EPS 5.778, tâm 51.500, "thấp hơn 6–10%", "tạm ứng nhân viên 643,7") chỉ còn ở cột "Trước" của Phụ lục E.
4. Luật 16: **10 trang A4** (thân 1–8, phụ lục 9–10); số từ thân không tính bảng/hình = **1.015** (gồm bảng: 2.323).
5. Luật 9/13: tiêu đề 1 câu hai vế (điều đúng: dòng lãi bền ≈1,25 nghìn tỷ/năm = EPS 5.184 × 242,11 tr cp; điều giá/rủi ro: 6.016 tỷ tín dụng + 635,6 tỷ tạm ứng, giá ngang tâm), không nháy kép thẳng;
   banner có logo saigonvrg.com.vn (`upload/hinhanh/logo-sgvrg-1341.png`, cắt lề trắng); font Be Vietnam Pro.
6. Luật 15: bản đồ vùng Đông Nam Bộ (bbox 105,95–107,35 / 10,45–11,45; KHÔNG toàn quốc), 4 KCN + trung tâm TP.HCM + sân bay Long Thành;
   toạ độ OSM Nominatim 01/11/2026 theo tên KCN (Phước Đông, Đông Nam, Lộc An–Bình Sơn); LMX3 không có điểm riêng trên OSM ⇒ dùng trung tâm xã Bình Lợi (địa chỉ BCTN). Ghi tỉnh cũ (Bình Dương nay thuộc TP.HCM).
   Khung 4 ảnh + ảnh hero trích BCTN 2025 SIP bằng pymupdf extract_image (≥600×350): trang PDF 4 (hero), 20 (cổng Phước Đông), 31 (mục dự án Phước Đông–Bời Lời), 30 (mục dự án KCN Đông Nam), 22 (nhà xưởng). Ảnh minh hoạ trang trí (icon, bàn họp) không dùng.
7. HTML: 12 `<img`, 0 thẻ thiếu alt; dry-run không gửi.
8. Xem bằng mắt (render 80 và 110 dpi): trang 1 (banner+logo, hero, KPI, dấu tiếng Việt đúng), trang 7 (Ke + rủi ro + pháp lý), trang 4 (bản đồ, ảnh, quỹ đất), tổng 10 trang.
   Đã sửa sau lần xem: nhãn bản đồ lệch điểm (đổi dx/dy, bỏ điểm NTC dễ gây hiểu nhầm); nhãn trục waterfall chồng nhau; nhãn ngoài khung ở hình bảng cân đối; chú thích sự kiện biểu đồ giá chồng nhau; nhãn R3/R6 ma trận rủi ro chồng nhau; tiêu đề 5c mồ côi cuối trang 5 (ngắt trang).
   Còn: trang 8 khá trống (mục 10 + ngắt trước Phụ lục); bản đồ hơi nhỏ trong PDF (đọc được, PNG gốc rõ).
9. Giá: DNSE latest_trade lấy 01/11/2026 17:07 ICT (Chủ nhật), khớp cuối 30/10/2026 14:45:06 = 48.350, marketId STO (HOSE). ±5% quanh giá (45.930–50.770): vẫn trong vùng 42–55k, kết luận không đổi.
   Chuỗi giá 12T: DNSE ohlc (đã điều chỉnh cổ tức) lưu `../calc/dnse_ohlc_SIP.json`.
10. Mỗi hình có CSV trong `figs/` (bản đồ: `fig_04_map.csv` = `scripts/pts_region.csv`; ảnh: `fig_05_photos.csv` ghi trang nguồn; bảng Ke: `tab_ke_sensitivity.csv`).
11. Ngành: từ báo cáo người đọc ngành độc lập 01/11/2026 (C&W Q2/26, CBRE 9T/26, TT 99/2025, thuế Mỹ) — không thêm số mới.
