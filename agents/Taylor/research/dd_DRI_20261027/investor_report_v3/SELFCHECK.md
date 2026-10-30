# Tự kiểm — DRI_DD_investor_report_20261030_v3 (job Taylor_20261030_031031, 30/10/2026)

md5: .md `8cffa84445de25b00674594163ec39d2` · .pdf `1024d7292e82ded332cf4935758a6150` (19 trang A4) · .html `5131d0e8783efae503ddf9ef1027ba4e`
(23 ảnh nhúng = banner + 22 hình). Nền: v2 `../investor_report_v2/` (không ghi đè v1/v2).

## (i) Số khớp v2/nguồn — không đổi số định giá
Lấy mọi chuỗi số trong .md v3 (1.477 lần xuất hiện, 462 chuỗi khác nhau), so với .md v2: 16 chuỗi mới (đo lại sau sửa ngưỡng xúc tác), tất cả là giá mới / phép tính cơ học / làm tròn:
- **Giá DNSE** (gọi trong phiên này, 10:11 ICT 30/10): đóng cửa 29/10 = 14.700 (DNSE ohlc 1D, khớp `figs/price_raw.csv` tav2_bq); 30/10 latest_trade G1
  10:08:44 = 14.500, tham chiếu 14.600, cao/thấp 14.700/14.300, KL 18.610 CP (phiên sáng, chưa đóng cửa). secdef marketId = UPX.
- **Tại 14.700:** vốn hoá 1.076,0 tỷ; P/E 5,2× (1.076,0/208,4); P/B 1,47× (1.076,0/729,9); tỷ suất cổ tức 6,8%; tiền ròng/vốn hoá ~22%
  (236,7/1.076); cổ tức/LNST TTM ~35% (73,2/208,4); tiền ròng sau cổ tức = ~2,2 năm cổ tức (162,8/73,2); vượt cận trên khoảng tin 12,5k: 18% (14.500: 16%).
- **Kịch bản:** dải lấy nguyên hằng số v2 (`NOREPLANT` 13.225–15.115 · `FV_TB` 9.078–11.116 · `FV_NHANH[0]`–`FV_TB[0]` 6.920–8.058);
  xác suất 25/50/25 là NHẬN ĐỊNH chủ quan (ghi rõ trong báo cáo); bình quân theo xác suất = 10.463 → "~10.500" (in bởi `build_report.py`,
  `figs/fig_21_scenarios.csv`). % so với 14.700: −10/+3, −38/−24, −53/−45, ~−29.
- **Giá cao su ngầm định nếu hoãn tái canh:** nội suy tuyến tính dải 13.225 (@1,97) – 15.115 (@2,18): 14.700 → 2,13; 14.500 → 2,11 (ước lượng, ghi "nội suy").
  Mức ~2,55 (@14.700) đã có ở v2 (bảng định giá ngược).
- **8,74%** lãi thực = khung r4 (`dri_val_supply_adj_r3_20261027/REPORT.md`: r danh nghĩa 12%, π 3%) — luật 14, chỉ ghi chú, không đổi tính toán.
- **Tái canh thực tế ~3%** = (94,56 + 37,77)/4.081,64 = 3,2% (số v2/BCTN). Nhịp kế hoạch Q4 ~1.390 t/tháng = 4.168/3 (số v2, ghi "tính").
- **94** = số thông báo 94/TB-CT. 13,2/15,1 = làm tròn dải phản biện.
Không có số định giá mới: FV trung tâm, khoảng tin 8,0–12,5k, lưới 27 ô, đường sản lượng, dải hoãn tái canh, P/B nhóm y nguyên v2 (r4 POST-HOC + số phản biện).

## (ii) Cập nhật từ nguồn sau v2 (chỉ GHI, không đổi định giá)
- dri.com.vn quét 30/10 ~10:15 ICT: tin mới nhất 22/10 (AAFA); **không có BCTC/SXKD mới sau 29/10**.
- Thông báo 94/TB-CT ngày 08/10/2026 (đăng web 08/10): cổ tức 2025 10% tiền mặt, **chi từ 20/10/2026** — v2 ghi "ngày chi trả chưa xác minh";
  v3 ghi ở 5c, 6, Phụ lục B/C/D. Thông báo VSDC đăng web 15/09/2026 (chưa đọc nội dung ngày GDKHQ — vẫn ghi "suy luận ~22/09").
- Tài liệu lấy ý kiến cổ đông bằng văn bản 2026 có trên web — KHÔNG phân tích (ngoài phạm vi "không nghiên cứu mới"), ghi ở Giới hạn.

## (iii) Grep (lệnh trong dispatch, `-i`) trên .md + EMAIL_SUBJECT.txt + figs/*.csv + text PDF
`SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros|QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ cổ phiếu`:
**0 hit.** Grep mở rộng thêm `Winston|Mafee|DollarBill|sleeve|biên an toàn|nhãn`: 0 hit trừ `fig_12_history.csv` "Nhãn hiệu" (lịch sử thương hiệu, không phải nhãn xếp hạng).
"giá vốn" chỉ nghĩa COGS (4 dòng mục 5).

## (iv) Luật 9–14
- **Luật 12:** bỏ thang QUALIFY/AMBIGUOUS/NON (header, mục 1, 10, Phụ lục D/F, hero "Xếp hạng nhóm"), bỏ đoạn "vùng giá cần chạy lại kiểm định / biên an toàn 15%".
  Kết luận = vị trí giá (TRÊN dải cơ sở, TRONG dải hoãn tái canh) + bảng 3 kịch bản có xác suất + "thị trường đang định giá gì" (hai cách hiểu: ~2,55 $/kg có tái canh
  hoặc ~2,1 $/kg nếu hoãn). Ba luận điểm tích cực ngang ba luận điểm rủi ro ở trang 1; mục 2 "Hai cách đọc DRI" với chứng cứ cho cả hai; mục 7 thêm bằng chứng
  ủng hộ/ngược lại cho trục hoãn tái canh và **chiều lệch POST-HOC hai phía** (3 hiệu chỉnh đều nâng giá trị → có thể lệch lên; mid neo trung vị lịch sử → có thể lệch xuống).
  "Điều làm đổi ý" tách hai chiều (mục 1); bảng xúc tác mục 10 có hai cột "Tích cực hơn nếu / Tiêu cực hơn nếu". Pre-mortem mục 8 đổi câu hỏi khỏi giọng nhà đầu tư.
- **Luật 9:** tiêu đề giữ câu user đã khen + thêm vế tích cực "tiền ròng dồi dào". Subject email (`EMAIL_SUBJECT.txt`) trung dung, không nhãn.
- **Luật 11:** Phụ lục F chỉ còn miễn trừ trách nhiệm, không câu xung đột lợi ích.
- **Luật 13:** Be Vietnam Pro cho thân PDF (pymupdf Story) + toàn bộ biểu đồ (fallback DejaVu chỉ cho ký hiệu → ⇒ Σ mà Be Vietnam Pro thiếu glyph; ①②③ đổi
  thành "1 ·"). Kiểm glyph bằng fontTools: .md chỉ còn → Δ ⚠ không có trong Be Vietnam Pro — MuPDF tự fallback, đã xem bằng mắt trang 11/15 hiển thị đúng.
  Banner `figs/title_banner.png` (make_title_banner.py, logo `../src/logo.png`, nguồn ghi Phụ lục C) đặt đầu trang 1 PDF full-width (511 pt, thay h1); dấu tiếng Việt
  tiêu đề/kicker/phụ đề đã xem bằng mắt. HTML dựng bằng `send_dd_report_email.py --dry-run --banner --html-out` (không Georgia/ARIA; 23 ảnh).
- **Luật 14:** ghi chú ở mục 7 + Phụ lục D: dòng tiền có thời hạn tới 2054, mặt bằng giá 2025, chiết khấu thực 8,74% (12% danh nghĩa), không giá trị cuối kỳ;
  không áp rf chuẩn hoá cho DCF vô hạn.
- **Luật 10 / thẩm mỹ:** thêm `fig_21_scenarios` (22 hình). Trống đáy trang đo bằng script (`/tmp/v3_measure.py`, text+ảnh): 2/18/22/3/5/3/8/1/1/22/9/1/3/18/14/1/9/1/15 %
  — trang 1 = 2% (v2 ~15–20%), trang 5 = 5%, hình xúc tác mục 10 in đủ khổ (ngưỡng co ảnh hạ từ 28% xuống 15%), trang cuối đầy 85%. Ngắt trang cứng chỉ còn
  trước mục 3; bảng dài phụ lục (>12 hàng) được tách trang (không lặp nền — đã xem trang 17), có chống mồ côi tiêu đề bảng. Nhãn trục ma trận rủi ro bị dính chữ do font
  rộng hơn → xuống dòng.
- Xem bằng mắt: trang 1 (banner+hero+tear sheet), 2, 4 (ngành + giới thiệu DN), 13 (định giá: kịch bản), 14 (rủi ro), 15 (pháp lý + xúc tác), 17 (phụ lục).

## Giới hạn tự kiểm
Không đọc lại scan BCTC; xác suất kịch bản là nhận định; không gọi lại DNSE sau 10:11 ICT (giá 30/10 là giá phiên sáng). Không gửi email (Mike đọc kiểm rồi gửi).
Tái lập: `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all`; HTML:
`python3 -I ~/.claude/skills/dd-investor-report/scripts/send_dd_report_email.py <md> --pdf <pdf> --banner figs/title_banner.png --subject "$(cat EMAIL_SUBJECT.txt)" --dry-run --html-out <html>`.
