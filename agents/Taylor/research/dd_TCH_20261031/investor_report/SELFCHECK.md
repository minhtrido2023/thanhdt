# Tự kiểm — TCH_DD_investor_report_20261031 (job Taylor_20261031_151105, 31/10/2026)

Lệnh: `bash scripts/make_maps.sh` → `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all` (hình + PDF);
banner: `make_title_banner.py` (python3 thường) với tiêu đề = dòng 1 của .md; HTML: `send_dd_report_email.py ... --dry-run --html-out` (KHÔNG gửi).

1. Lộ thông tin nội bộ: `grep -i -E "SpaceX|ZaloPay|Taylor|Bobby|Mike|skeptic|Wendy|Spyros"` trên .md = 0 hit; trên .html (bỏ base64) = 0.
2. Ngôn ngữ trung tính: `grep -i -E "QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ cổ phiếu"` trên .md = 0 hit.
3. Số khớp REPORT.md v2 (grep từng chuỗi cả 2 file): vùng 10.150–15.050; tâm 12.300–12.650 (trọng số 12.650, nghiêng ngành 12.280); LN mẹ 537,7;
   NMTT 5.599,8 / −893; tiền đất 2.993; QĐ thuế 20,21 tỷ; CRV 89,35%; P/B ngành ≈9.480; SOTP 11.200–11.450; CK ngầm định 20/25/29%.
   Số v1 đã bị đính chính (8.700, 10.700, 11.950, biên ròng 36%) chỉ xuất hiện ở cột "Trước" của Phụ lục E.
4. Luật 16: 11 trang A4 (thân trang 1–9, phụ lục 10–11); số từ thân không tính bảng/hình = 1.136 (gồm bảng: 2.620).
5. Luật 9/13: tiêu đề 1 câu hai vế, không nháy kép thẳng; banner có logo (hoanghuy.vn, làm sạch nền xám → trắng, `figs/logo_clean.png`); Be Vietnam Pro.
6. Luật 15: bản đồ vùng (geoBoundaries ADM1, bbox Hà Nội–Hải Phòng, KHÔNG toàn quốc) + bản đồ Hải Phòng tự vẽ (toạ độ OSM Nominatim,
   cấp phố/KĐT; Green River ghi "vị trí xấp xỉ"; không vẽ sông/đường vì không có dữ liệu vector; 17B Bà Triệu, Pruksa Town không vẽ).
   Khung 5 ảnh dự án trích từ BCTN 2025 tr.16–18 bằng pymupdf extract_image (≥300×200), ghép nhãn "Hoàng Huy công bố (phối cảnh)".
7. HTML: 16 `<img`, 0 thẻ thiếu alt; dry-run: to=địa chỉ trong secrets, 16 ảnh, 14,8 MB (lớn — ảnh BCTN độ phân giải cao; Mike cân nhắc nén nếu email bị chặn).
8. Xem bằng mắt (render 1,1x): trang 1 (banner, hero, KPI — dấu tiếng Việt đúng), trang 3–4 (ngành, cấu trúc, bản đồ, ảnh), trang 7–9 (định giá, ma trận, rủi ro, WARNING).
   Đã sửa sau lần xem: chồng chữ ở 7 hình; "~" in như dấu trừ trong Be Vietnam Pro → đổi thành "≈"; ký tự Δ/→/↔ thiếu glyph → bỏ.
   Còn: tiêu đề "Ba điều cần biết" rơi cuối trang 1 (danh sách sang trang 2); ma trận rủi ro bị co nhỏ ở trang 8.
9. Giá: đóng cửa 30/10/2026 = 11.850 (BQ `ticker` + DNSE OHLC khớp; 31/10 thứ Bảy không có phiên). Ở ±5% quanh giá kết luận "trong vùng, nửa dưới" không đổi.
