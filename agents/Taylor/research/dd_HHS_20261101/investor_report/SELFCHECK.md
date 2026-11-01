# Tự kiểm — HHS_DD_investor_report_20261101 (job Taylor_20261101_041414, 01/11/2026)

Lệnh: `bash scripts/make_maps.sh` → `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all` (hình + PDF);
banner: `make_title_banner.py` (python3 thường) với tiêu đề = dòng 1 của .md, logo `../src/logo.png`;
HTML: `send_dd_report_email.py ... --dry-run --html-out` (KHÔNG gửi — Mike gửi).

1. Lộ thông tin nội bộ: `grep -i -E "SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros"` trên .md = **0 hit**; trên .html (bỏ base64) = 0.
   ("NAV dự án" đã đổi thành "giá trị tài sản ròng theo dự án" ở .md và nhãn hình.)
2. Ngôn ngữ trung tính: `grep -i -E "QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ"` trên .md = **0 hit**.
3. Số khớp `../REPORT.md` v2 + `../calc/valuation_v2_out.txt`: kịch bản 7.583 / 10.160 / 13.021 (figs_part.py tính lại cùng công thức, in ra khớp);
   tâm 9.959 (30/50/20) / 10.231 (25/50/25); giá 9.450 thấp hơn tâm 5–8%; cơ sở PPA tham chiếu 11.693 (−19%); thặng dư PPA 4.134 tỷ ≈ 9.570 đ/cp;
   soát xét 6T LNST mẹ 65,51 → 43,32 (−34%), tự kiểm trên ảnh Q2HN tr.8–9 và 6THN tr.9; P/B 0,98x × 11.617 = 11.385; BĐSĐT +≈650 đ (không vào tâm).
   Số v1 đã bị đính chính (tâm ≈11.900, "thấp hơn 20%", WARNING trung bình–cao, xe 40×8x) chỉ còn ở cột "Trước" của Phụ lục E.
4. Luật 16: **10 trang A4** (thân 1–8, phụ lục 9–10); số từ thân không tính bảng/hình = **1.012** (gồm bảng: 2.427).
5. Luật 9/13: tiêu đề 1 câu hai vế (điều đúng: không vay + bàn giao NC-II; điều giá/rủi ro: thặng dư chưa thực hiện, Q3 chưa soát xét, giá chỉ dưới tâm 5–8%),
   không nháy kép thẳng; banner có logo hoanghuyhhs.vn (`/images/general/logo2025111523546.png`); font Be Vietnam Pro.
   Glyph thiếu trong font (→, ⇒, ⚠️) đã thay; "~" thay bằng "≈".
6. Luật 15: bản đồ vùng (geoBoundaries ADM1, bbox Hà Nội–Hải Phòng, KHÔNG toàn quốc; ghi Hải Dương cũ nay thuộc Hải Phòng) + bản đồ Hải Phòng tự vẽ
   (toạ độ OSM Nominatim 31/10 (DD TCH) và 01/11/2026: Pruksa Town ≈ An Đồng, H1 Commerce, CRV 183 Bà Triệu HN, 275 Nguyễn Trãi HN; lô 17B Bà Triệu
   chưa xác định thành phố ⇒ không vẽ, ghi Giới hạn). Khung 5 ảnh: 4 ảnh xe trích BCTN 2025 HHS tr.4, 18, 20, 24 bằng pymupdf extract_image (≥500×300),
   ảnh New City-II từ BCTN 2025 TCH (phối cảnh). Ảnh đầu kéo International chú thích đúng: chủ yếu ở TCH, HHS dự kiến mua lại (BCTN tr.21).
   Ảnh tòa nhà ở trang chương của BCTN là ảnh trang trí, không gán dự án ⇒ không dùng.
7. HTML: 14 `<img`, 0 thẻ thiếu alt; dry-run: to=địa chỉ trong secrets, 14 ảnh, 12,4 MB (lớn; Mike cân nhắc nén nếu email bị chặn).
8. Xem bằng mắt (render 1,1x): trang 1 (banner, hero, KPI, dấu tiếng Việt đúng), trang 3 (ngành, cấu trúc, bản đồ), trang 6 (định giá + ma trận), trang 8 (pháp lý, mốc).
   Đã sửa sau lần xem: nhãn KPI bị cắt; nhãn ma trận rủi ro chồng nhau (R4/R5/R6); nhãn bản đồ Hải Phòng tràn mép và chồng chữ địa danh;
   chú thích biểu đồ giá chồng nhau; nhãn football field đè đường giá; ngắt trang để bỏ 2 trang gần trống (11 → 10 trang).
   Còn: tiêu đề 5b nằm cuối trang 4, hình sang trang 5; bản đồ ghép bị co ở trang 3 (vẫn đọc được ở bản PNG gốc).
9. Giá: DNSE latest_trade lấy 01/11/2026 10:40 ICT, khớp cuối 30/10/2026 14:45:04 = 9.450 (Chủ nhật, không có phiên). ±5% quanh giá (8.980–9.920): kết luận không đổi.
10. Mỗi hình có CSV trong `figs/` (bản đồ vùng: `scripts/pts_region.csv`; ảnh: `fig_07_products.csv` ghi trang nguồn).
