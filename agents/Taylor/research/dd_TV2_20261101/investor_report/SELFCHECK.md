# Tự kiểm — TV2_DD_investor_report_20261101 (job Taylor_20261101_043110, 01/11/2026)

Lệnh: `bash scripts/make_maps.sh` → ghép `figs/fig_11_maps.png` (PIL, map_south + map_north) → `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all`;
banner: `python3 make_title_banner.py` với tiêu đề = dòng 1 của .md, logo `figs/logo.png` (render từ pecc2.com/vnt_upload/weblink/logo.svg);
HTML: `send_dd_report_email.py ... --dry-run --html-out` (KHÔNG gửi — Mike gửi).

1. Lộ nội bộ: `grep -i -E "SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros|giá vốn"` trên .md = 0 hit; .html (bỏ base64) = 0.
2. Trung tính: `grep -i -E "QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ cổ phiếu"` trên .md = 0 hit.
3. Số khớp ../REPORT_v3.md (grep chuỗi cả 2 file): kỳ vọng 20.700; vùng 17.100–25.300; tâm tích cực 29.600 / tiêu cực 11.000; độ nhạy 19.700 / 21.600 / 19.600 / 22.400 / 22.100 / 25.200; LN ngầm định 245 / 203; P/E pha đỉnh 7,45; CFO −574…−225; CMC 666,4, 64%.
   Số v2 đã bị đính chính (18.300–28.100, 22.600, P/E 11,0x) chỉ còn ở cột "Trước" Phụ lục E.
4. Luật 16: 10 trang A4 (thân 1–8, phụ lục 9–10); số từ thân không tính bảng/hình = 1.066 (gồm bảng 2.429).
5. Luật 9/13: tiêu đề 1 câu hai vế, không nháy kép thẳng; banner có logo PECC2; Be Vietnam Pro; email subject theo tiêu đề.
6. Luật 15: bản đồ khu vực Nam (TP.HCM–Cần Thơ–Cà Mau) + Bắc (Yên Bái/Tuyên Quang cũ), KHÔNG toàn quốc. Toạ độ OSM Nominatim 01/11/2026 cấp phường/xã/huyện
   (Phước Thới–Ô Môn; xã Tân Thuận; Mậu A = trung tâm huyện Văn Yên thay cho CCN Bắc Văn Yên; xã Xuân Vân; Thác Bà; Phường Thủ Đức), ghi "gần đúng" trên hình.
   Địa điểm dự án: CCN Bắc Văn Yên (nongnghiepmoitruong), CCN Xuân Vân (Nhân Dân). Khung 4 ảnh + ảnh hero: BCTN 2025 PDF tr.9/29/35 (extract_image), ghi "PECC2 công bố".
7. HTML dry-run: 13 `<img`, 0 thiếu alt; to = địa chỉ trong secrets; tổng 8,4 MB (kèm PDF + md).
8. Xem bằng mắt (render 0,9x toàn bộ + 1,25x trang 1/4/7): dấu tiếng Việt đúng, bảng không tràn. Đã sửa: nhãn pha chồng nhau (hình 01), nhãn trục bị cắt (03, 05),
   chú giải đè đường VCSH (04), mũi tên → thiếu glyph (06), nhãn số đè đường giá (07), chú thích ảnh bị cắt (10), bản đồ Nam chiếm 1 trang → ghép ngang 2 bản đồ.
   Còn: bản đồ ghép nhỏ khi in (nhãn đọc được khi phóng to PDF); trang 3 chỉ đầy ≈55%.
9. Giá: DNSE latest_trade 27.000 lúc 14:45:07 30/10/2026 (thứ Sáu; 31/10–01/11 không có phiên). Tham chiếu 02/11 = 27.000 ⇒ kết luận giống nhau ở cả hai mốc;
   giá phải xuống ≤25.300 mới vào vùng cơ sở, ≤20.700 mới về kỳ vọng.
