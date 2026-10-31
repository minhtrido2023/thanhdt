# Tự kiểm — NNC_DD_investor_report_20261031 (job Taylor_20261031_014511, 31/10/2026)

md5: .md `6414434a47f03d6acbdee7234e0e8318` · .pdf `4cc4fd1cfe0d925805c85e378943e514` (14 trang A4) · .html `da2ab46c7adb45c74f1e14915552e5ca`
(dry-run: 20 ảnh nhúng, 5,3 MB, người nhận = to_email trong secrets) · build_report.py `3593c3c239d4af0e09f1864e15642b41`.
Nguồn số định giá: `../calc/valuation_v2.py` → `../calc/valuation_v2_out.txt` (md5 `3cff411d89327849e6e70a2f0ca67954`); đính chính: `../REPORT.md` §13.

## (i) Lệnh grep luật 4 / luật 12 (chạy trên .md + EMAIL_SUBJECT.txt + figs/*.csv; và trên text PDF)
- `grep -n -i -E "SpaceX|ZaloPay|giá vốn|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros"` → **0 hit ngoài "giá vốn"**; "giá vốn" 8 lần, tất cả nghĩa COGS (giá vốn đá thành phẩm / giá vốn hàng bán, mục 5a, 5e, Phụ lục A, E).
- `grep -n -i -E "QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ cổ phiếu"` → **rỗng (0 hit)**.
- Text PDF (pymupdf get_text): cả hai mẫu → [] (0 hit).
- Tên nguồn bên ngoài được nêu: FPTS chỉ ở Phụ lục C (danh mục nguồn); thân bài gọi "một công ty chứng khoán". Không tên agent nội bộ.

## (ii) Xem bằng mắt (render pymupdf 75–160 dpi, Read ảnh)
Trang 1 (banner logo + hero + bảng dữ liệu chính; dấu tiếng Việt tiêu đề/kicker/phụ đề đúng, "~" hiển thị nhỏ nhưng đọc được),
trang 4 (ngành + lịch sử), 8 (định giá: chi phí vốn + hình đường giá + bảng), 9 (3 kịch bản + độ nhạy + comp), 11 (ma trận rủi ro + pháp lý), 12 (xúc tác + Phụ lục A).
Bảng không tràn lề. Đã sửa trong lúc kiểm: chồng chữ ở hình lịch sử (trục đổi sang thứ tự mốc), football field, ma trận rủi ro, xúc tác (bỏ mốc không ngày khỏi hình,
giữ ở bảng), nhãn giá ở hình kịch bản, chú thích hình comp; tiêu đề mục 10 mồ côi cuối trang (đổi thứ tự bảng/hình).

## (iii) Số khớp bản đính chính
Mọi số định giá trong .md đọc từ valuation_v2_out.txt: vùng 59.307–79.498 (→ 59.300–79.500 / "~59–79 nghìn"), điểm giữa 69.402, lưới 50.685/57.617/70.318/84.812/94.442,
3 kịch bản phẳng 99.099/56.657/24.815, thực 131.053/77.418/32.102, 4 đường giá 59.980/69.106/76.633/80.171, chi phí ±10% 54.594–65.605 / 74.180–86.298,
r 11/15% (+3.652/−3.095 phẳng; +7.367/−6.078 thực), MVC 30% −1.346, xấu hồi phục 2035 +1.312/+2.982, P(tiêu cực) hàm ý 41–80% ở 45.000–52.000.
Số BCTC = REPORT.md §2–§5 + §13 (đã đối chiếu ảnh trang KT25 tr.39–40, Q3 tr.3/tr.28, FPTS tr.1/9/17 trong phiên này).
Đo mới trong phiên: PE TTM nhóm (BQ 30/10: NNC 4,83 · DHA 5,43 · KSB 7,13 · VLB 3,65; VLB bỏ Q2/26 ⇒ 6,25 ước lượng); NHC DT 28,97–30,39 tỷ/quý, LNST Q2/26 −0,27 tỷ (BQ);
MVC Volume_1M 41.280 cp × 14.100 ≈ 0,58 tỷ/phiên; GPM_P0 BQ = biên 4 quý (Phụ lục B).
Đính chính E1–E12 không tái xuất hiện: không còn "không thấy phạt", "FPTS gần kỳ vọng", ngưỡng 42k/58k; xác suất 25/50/20/5.

## (iv) Luật 9–14
- 9: tiêu đề = 1 câu (lợi nhuận đỉnh nhờ giá đá / giá đã chiết khấu vách 2028 / giá trị treo vào giá đá sau khi mỏ mới vào cuộc). Subject: EMAIL_SUBJECT.txt.
- 10: hero trang 1 (ngành–tăng trưởng–định giá), 19 hình + banner, mỗi hình có CSV (21 CSV gồm fin_quarterly_bq + price_raw). Mục 3–4 kiểu BCTN (lịch sử 1975→2025, sản phẩm, thị trường, cổ đông, định hướng 2026–2030/2050).
- 11: Phụ lục F chỉ miễn trừ. 12: kết luận = DƯỚI vùng hợp lý + 3 kịch bản xác suất; 3 tích cực/3 rủi ro; "đổi ý" hai chiều; giả định giá đá cho cả hai đầu vào vùng.
- 13: Be Vietnam Pro (PDF + biểu đồ); logo từ http://nuinho.vn/upload/hinhanh/logo-3594.png (185×66, lưu ../src/logo.png, nguồn ghi Phụ lục C); banner make_title_banner.py.
- 14: DCF hữu hạn 2027–2043, không terminal; r 13% (11–15%) kèm lý do + độ nhạy.

## Giới hạn / CHƯA XÁC MINH
Giá: thứ Bảy, không gọi DNSE latest_trade (thị trường đóng cửa); neo đóng cửa 30/10 từ tav2_bq.ticker. Sản lượng m³, nội dung phạt hành chính, nghị quyết chuyển ~80 tỷ LN 2026
vào quỹ, tỷ lệ cổ tức 61,37%, OShares MVC, GP Tam Lập 1 khu II, cơ cấu sản phẩm/khách hàng: CHƯA XÁC MINH (ghi ở Phụ lục D). Không gửi email (Mike đọc kiểm rồi gửi).
Tái lập: `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all`; HTML: `python3 -I ~/.claude/skills/dd-investor-report/scripts/send_dd_report_email.py NNC_DD_investor_report_20261031.md --pdf NNC_DD_investor_report_20261031.pdf --banner figs/title_banner.png --subject "$(cat EMAIL_SUBJECT.txt)" --dry-run --html-out NNC_DD_investor_report_20261031.html`.
