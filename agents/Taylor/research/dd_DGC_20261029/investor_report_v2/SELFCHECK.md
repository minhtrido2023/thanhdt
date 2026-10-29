# SELFCHECK — DGC_DD_investor_report_20261029_v2 (job Taylor_20261029_134234, 29/10/2026)

## 1. Rò rỉ nội bộ — RỖNG
`grep -n -i -E "SpaceX|ZaloPay|\bNAV\b|Taylor|Bobby|Mike|skeptic|Wendy|Spyros|Winston|Mafee|DollarBill|HARD ABANDON|time-stop|\bP1\b|giá vốn mua|vị thế|tài khoản|10\.000 ?cp|35,8" <md> <html> figs/*.csv` → 0 hit.
Nhãn (luật 1/11/12): `grep -i -E "QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ"` → 0 hit.
Ghi chú: dispatch nói "nhãn P1 (AMBIGUOUS nghiêng tích cực) giữ" — giữ ở hồ sơ định giá nội bộ (r12); báo cáo nhà đầu tư theo SKILL luật 1/12 (user chốt 19:20) dùng ngôn ngữ trung tính "giá nằm TRONG vùng giá trị, sát cận dưới". Phụ lục F chỉ miễn trừ.

## 2. Kiểm theo dispatch (a)–(g)
- (a) "không có tiền lệ": 0 hit (md + html).
- (b) "6,6%": 1 hit, Phụ lục E mục 7, kèm "đó là số gộp … ròng −447".
- (c) mọi "gia quyền" có w = 0,2/0,5/0,3 cùng dòng (grep lọc → 0 dòng thiếu); w công bố ở tear sheet, mục 3, mục 8, Phụ lục D.
- (d) không câu nào nối khoản 200 với vụ án như sự thật; hộp mục 9 dòng "Không nối được với vụ án" (thuyết minh 36 H1).
- (e) "không thấy không có nghĩa là không có" + cửa sổ 16/08–30/09 chưa quét: mục 10 (2 chỗ).
- (f) không trích ngày gỡ hạn chế HOSE ("Không có nguồn nào nêu ngày gỡ").
- (g) không có `*…*` đơn trong ô bảng (grep PCRE → 0).
- Glyph: Be Vietnam Pro thiếu → ⇒ Δ ↔ ⚠ — md không chứa (grep → 0); biểu đồ dùng fallback DejaVu.

## 3. Số khớp nguồn
Script đối chiếu: 288 số có dấu chấm/phẩy trong md; 283 tìm thấy nguyên dạng trong `dgc_valuation_20261029_r12/` (REPORT, out_r12_*, out_r11_*, out_r10_*), `inputs/ERRATA_*`, v1 md. 5 số còn lại (3.600 soda; 44.000 t Cl2; 46.000/50.000/75.000 công suất NQ 34) có trong `dgc_valuation_20261029_r11/REPORT.md` và ERRATA r11 (dạng "46k/50k/75k").
Số then chốt: A7/B7 32.182/37.060 (r10, tái lập assert); NS=0 30.019/34.896; biến thể 32.690/37.569; ròng −447 (+1.586/−406/−1.870); cầu nối −306/420/518/2.524/2.215/2.848; NPV −3.245/2.524/6.781; điện 1.811/1.146/3.266, EBITDA thấp −22→+11; TKV 1.160/138.813 = 0,84%, DGC 4,28%/75%/22%; cổ tức 4.213/3.038/1,99×; ô thấp nhất 26.117–26.558; lưới dự phòng = out_r10_final_grid.csv.

## 4. Errata vòng 5 đã áp
1. Phần C: bỏ câu tuyệt đối; TKV mở nguồn gốc nhandan.vn 21/08/2022 (cand.vn người phản biện dẫn: nhóm không mở được, không trích); quy mô tương đối có số; đối xứng hữu hạn/lặp; "hàng triệu tấn" = cáo buộc CQĐT; bỏ câu "phương án xử lý toàn bộ chất thải rắn"; BH+QLDN quy năm 530; ký quỹ: không tìm được số của doanh nghiệp, không trích "~3 tỷ"; phép kiểm vật lý: không làm được (nói rõ).
2. Nghi Sơn một cơ sở ròng (6c) + cầu nối P/E↔DCF + VLĐ 15% + duy tu + thuế legal (chưa xác minh) + điện 110kV có QĐ/ngày + Ca(OCl)2 vs clorua vôi + vốn 2.400/2.900 có nguồn từng số + "chưa xác minh" thay "KB sai".
3. Bảng động lực: không thứ hạng, Δ so với A7, định nghĩa 2 đầu mút, công bố w.
4. Cổ tức 4.213 (LCTT) / 8.000 đ/cp 25/09 / không dự báo mới.
Dự phòng: hộp phụ mục 9 + một hàng ô thấp nhất trong lưới mục 8 (đủ số).
Thêm: rủi ro không còn cột xác suất; bỏ xác suất chủ quan của bản đọc ngành (70/30, P=0,65) khỏi mục 4.

## 5. Kiểm mắt PDF
23 trang A4, font Be Vietnam Pro + banner logo (logo tải từ ducgiangchem.vn/wp-content/uploads/2023/08/logo-dgc.jpg → src/logo.png). Render (pymupdf Matrix 1.4) trang 1, 6, 9, 10, 16: dấu tiếng Việt đủ, bảng không tràn. Đã sửa: hộp Nghi Sơn bị cắt ở hero, tiêu đề hình 11 bị cắt, trục NPV hình 13. Trang 1 còn khoảng trống dưới đoạn tóm tắt (tear sheet sang trang 2 vì bảng không tách trang).
Mỗi mục có ≥1 hình: hero, 2 (giá), 3 (động lực), 4 (ngành), 5 (cơ sở), 6 (Nghi Sơn), 7a–7d, 8 (football + lưới), 9 (dự phòng ×2), 10 (dòng thời gian). 15 hình + banner, mỗi hình có CSV.

## Giới hạn
Các sửa vòng 5 chưa được người phản biện rà lại (ghi trong Phụ lục E). Doanh thu TKV qua kết quả tìm kiếm (2 báo), chưa mở bài gốc. Giá DNSE 33.300 lấy lại từ lần đọc 19:12 của bản 1, không đọc lại. Không gửi email (Mike gửi; subject gợi ý ở EMAIL_SUBJECT.txt).
