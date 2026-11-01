# FPT — Lãi 9T +13,3% và tiền ròng 12.233 tỷ là thật, nhưng xuất khẩu Q3 chậm hẳn (ký mới +3,6%) và 9T/2026 chưa chuyển lãi thành tiền; giá 52.700 nằm DƯỚI vùng cơ sở 55–67k, phần rẻ chỉ thành hiện thực nếu Q4 thu được tiền

DD v2 · 01/11/2026 · job Taylor_20261101_101423 (v1: job Taylor_20261101_042936, lưu ở `REPORT_v1.md`) · CHỈ NGHIÊN CỨU, không đặt lệnh, không wire.
v2 áp đính chính của phản biện `SKEPTIC_20261101.md` (REFUTED ở mức văn bản; số liệu chép từ BCTC đúng). Bảng đã áp/không áp ở cuối báo cáo.
Nhãn nguồn: **[Q3HN pNN]** = BCTC hợp nhất Q3/2026 gốc (fpt.com 28/10/2026, ảnh `calc/png_q3/pNN.png`, chép số ở `calc/notes_q3_bctc.md`) ·
**[6THN]** = BCTC hợp nhất Q2/2026 · **[TCBC9T]/[TCBC6T]** = thông cáo KQKD 9T (21/10) / 6T (16/07) · **[KQKD9T pN]** = slide KQKD tháng 9 ·
**[BCTN25 pNNN]** = Báo cáo thường niên 2025 (số trang in; ảnh `calc/bctn25_p169.png` = KQKD tr.168, `calc/bctn25_p171.png` = LCTT tr.170) ·
**[CBTT]** = `calc/notes_disclosures.md` · **[BQ]**, **[DNSE]** = `calc/bq_*.csv`, `calc/dnse_latest_raw.json` ·
**[calc]** = `calc/valuation.py` → `calc/valuation_out.txt` (v1: `calc/valuation_v1.py` → `calc/valuation_out_v1.txt`). Số tự đặt ghi **(ước lượng)**.

⚠️ **Phạm vi hợp nhất đã đổi.** Từ 01/01/2026 FPT ghi nhận FPT Telecom (FTEL, mã FOX, sở hữu 45,66%) theo phương pháp vốn chủ sở hữu, không hợp nhất toàn bộ nữa, theo Công văn 1906 ngày 18/03/2026 của Cục Kế hoạch và Tài chính, Bộ Công an [Q3HN p14]. Cột 2025 in trên BCĐ, KQKD và LCTT vẫn là số cũ còn FTEL. So sánh cùng kỳ dùng số 2025 đã điều chỉnh mà FPT tự công bố [Q3HN p08] hoặc % tăng trưởng trong thông cáo.

## 0. Tóm tắt
- **Tăng trưởng là thật nhưng chậm dần.** Q3: doanh thu 13.754 tỷ (+12,1%), LNTT 3.056 tỷ (+15,0%), LNST cổ đông mẹ 2.723 tỷ (+11,8%). 9T: LNST mẹ 7.778 tỷ (+13,3%). Doanh thu CNTT nước ngoài +13,4% ở 6T, còn +8,2% ở riêng Q3. Ký mới nước ngoài +32,3% ở 6T, còn **+3,6%** ở riêng Q3 (9.799 tỷ); Q3 chỉ thắng 2 hợp đồng trên 10 triệu USD, cùng kỳ khoảng 8 (ước lượng từ số lũy kế) [calc].
- **Vẫn có chiều tích cực.** Hợp đồng >1 triệu USD 9T: 163 (+29,4%); 500 nghìn–1 triệu USD: 211 (+22,7%); khách hàng >500 nghìn USD: 367 (+9,6%) [KQKD9T p6]. Phải thu thu về khoảng 473 tỷ ngay trong Q3 (LCTT mã 09: H1 −2.007, 9T −1.534) [6THN p10; Q3HN p10]. Nhật theo JPY 9T +25,2%.
- **Và chiều tiêu cực trong chính số Nhật/Mỹ.** Doanh thu thu bằng JPY: H1 +22,6%, riêng Q3 khoảng **+15,3%** (25,35 so với 21,98 tỷ JPY, ước lượng từ lũy kế) — sát ngưỡng "hạ nhận định" của chính báo cáo này (Nhật theo JPY dưới +15%). Doanh thu thu bằng USD Q3 +5,8%. Doanh thu hàng hoá (bán chuyển tiếp) 4.000 tỷ (+19,9%), biên gộp chỉ 12,4% [KQKD9T].
- **Phần lớn mức tăng lãi đến từ công ty liên kết.** Lãi liên kết 9T +663 tỷ (+42,6%), bằng **52%** mức tăng LNTT. Bỏ lãi liên kết ra thì LNST 9T chỉ +5,2%, vì thuế suất hiệu dụng tăng từ 11,1% lên 15,2% [calc]. LN lõi 9T còn có hoàn nhập dự phòng khoảng 133 tỷ (LCTT mã 03) [Q3HN p10].
- **Tiền chưa về.** Theo định nghĩa duy nhất dùng trong báo cáo này — *tỷ lệ chuyển lãi thành tiền = (CFO + lãi vay đã trả sau thuế − capex) / LN lõi vận hành* (§4c) — 9T/2026 là **−0,12**; cùng định nghĩa: 9T/2025 0,34, cả năm 2025 0,60, cả năm 2024 1,07 (hai năm cũ còn FTEL). Các số tham khảo khác gốc cho 9T/2026: CFO/(LNTT − lãi hoạt động đầu tư − thuế) = 0,22; (CFO + tiền lãi và cổ tức thu về)/LNST = 0,28. Con số "0,12 = CFO/LNST" của v1 so lệch gốc nên đã bỏ.
- **Bảng cân đối vững.** Tiền ròng 12.233 tỷ (6.487 đ/cp), chưa trừ cổ tức tiền 1.000 đ/cp chốt 30/11. Cổ phần ở hai công ty niêm yết theo thị giá 30/10: FTEL 9.910 đ/cp, FRT 6.562 đ/cp.
- **Định giá.** PE TTM 9,7, thấp nhất khoảng 8 năm (lần gần nhất ≤9,8 là khoảng 11/2018–2019; p10 của 10 năm là 10,5). Phần lõi vận hành đang được trả khoảng **8,0 lần lợi nhuận** (ước lượng). Vùng cơ sở DCF FCFE = **55,0–66,7k** (g dài hạn 3–5% × Ke 12,3–13,4%, tỷ lệ chuyển lãi thành tiền 0,75, cùng gốc giá có quyền cổ tức). **Giá 52.700 nằm DƯỚI vùng cơ sở khoảng 4%.** Ba kịch bản 34,1k / 59,8k / 79,6k với xác suất 0,35 / 0,45 / 0,20 (ước lượng) cho kỳ vọng **54,8k (+4%)** — gần giá, vì kịch bản xấu nay dùng đúng tỷ lệ chuyển tiền đã quan sát.
- **Tiêu chí khai trước 21/10: 2/4 đạt.** LNST mẹ ≥ +12% đạt. Phải thu không tăng đạt. Ký mới chậm lại. CFO Q3 ≥ ~2.600 tỷ **không đạt** (2.097). Nhánh "MUA" của khung 21/10 chưa kích hoạt; chưa rơi xuống ngưỡng xấu 1.500 tỷ.
- **Pháp lý và quản trị: chỉ WARNING, mức THẤP–TRUNG BÌNH.** PwC soát xét 6T chấp nhận toàn phần. Phạt thuế 0,244 tỷ, không trọng yếu. Rủi ro cấu trúc: FTEL do phía Nhà nước (Bộ Công an) kiểm soát, Nhà nước nắm khoảng 50,16% FTEL [BCTN25] ⇒ free float FOX tối đa khoảng 4,2%, có tin FOX gặp khó về tiêu chí công ty đại chúng do free float thấp. Một khoản "chi phí phát triển khách hàng" 618,8 tỷ chưa được thuyết minh (§6, hiện chỉ là câu hỏi).

## 1. Kết luận và vùng giá
| | Giá trị | Ghi chú |
|---|---|---|
| Giá tham chiếu | **52.700 đ** | DNSE latest_trade khớp 30/10/2026 14:45:03, phiên gần nhất (01/11 là Chủ Nhật). Khớp BQ 30/10. Giá **còn quyền** cổ tức 1.000 đ (chốt 30/11) |
| Đỉnh / đáy 1 năm | 95.140 / 52.700 | [BQ]. −45% từ đỉnh. Cả nhóm cùng giảm: CMG 38,1k → 18,5k, ELC 25,0k → 11,0k, FOX 102,5k → 55,4k |
| **Vùng hợp lý cơ sở** | **55,0–66,7k** | DCF FCFE lõi, **một trục**: g dài hạn 3–5% × Ke 12,3–13,4%, cố định tỷ lệ chuyển tiền 0,75, tăng trưởng 5 năm 9% [calc bảng độ nhạy]. Tâm (g 4%, Ke 12,85%) 59,8k. Cùng gốc với giá có quyền cổ tức (trừ cổ tức thì 54,0–65,7k) |
| Vị trí giá | **DƯỚI vùng** | 52.700 thấp hơn cận dưới 55,0k khoảng 4% |
| Trục thứ hai (tham khảo) | 52,2–67,5k | Tỷ lệ chuyển tiền 0,60–0,90 tại g 4%, Ke 12,85%. Ở 0,40 (gần mức đã quan sát) chỉ còn 41,9k |
| Ba kịch bản | 34,1k / 59,8k / 79,6k | Xác suất 0,35 / 0,45 / 0,20 (ước lượng). Kỳ vọng có trọng số **54,8k (+4%)** |
| Mốc Ke nước ngoài | 48,5–51,8k | Ke 15,8% (Damodaran) — góc nhìn nhà đầu tư nước ngoài, không phải khung chính |
| SOTP chéo | PE lõi 8–12 lần: 48–66k | Lõi × PE + FTEL chiết khấu 0–30% + FRT chiết khấu 20% + tiền ròng [calc] |
| PE chéo | PE 9–13 × EPS 2026E 5.615 (ước lượng): 50,5–73,0k | |
| Bất định SOTP chưa đưa vào số tâm | khoảng −1,3k đến +2,4k đ/cp | Liên kết khác theo PE 6–10 thay vì giá sổ: +1,1 đến +2,4k; tiền khách ứng trước nếu coi là nợ: −1,26k; TPBank/FPTS theo giá gốc chỉ có thể tăng [calc] |

**Nhận định trung dung:** ở 52.700, thị trường đang định giá FPT gần với kỳ vọng có trọng số (54,8k) chứ không gần kịch bản cơ sở. Giá nằm dưới vùng cơ sở vì vùng đó giả định FPT trở lại chuyển 75% lãi lõi thành tiền — mức FPT đã làm được năm 2024 (1,07) và gần làm được năm 2025 (0,60), nhưng 9T/2026 đang âm. Tiền ròng và cổ phần liên kết theo thị giá đã chiếm khoảng 23k đ/cp. Hai điều chưa cho phép gọi là "rẻ chắc chắn": (1) xuất khẩu Q3 giảm tốc, khớp kịch bản "AI làm giảm số người-tháng" mà người đọc ngành độc lập đã nêu; (2) dòng tiền 9T. Không nghiêng hơn về phía xấu, vì Q4 lịch sử là quý thu tiền chính (tử số Q4/2025 khoảng 3.329 tỷ) và chiều tích cực (§0) có thật.

## 2. Kiểm lại số đầu vào
| Số | Nguồn cũ / báo chí | Số gốc | Kết quả |
|---|---|---|---|
| LNST mẹ 9T | 7.778 [CHƯA XM 21/10] | 7.778.081.180.761 đ [Q3HN p07] | Đúng |
| LNST mẹ Q3 | báo chí 2.273 | **2.723** tỷ [Q3HN p07] | Báo chí đảo chữ số |
| CFO H1/2026 | −1.146 (DD 14/10 tự tách) | −1.144,6 [6THN p10] | Đúng |
| EPS 9T | 4.142 | 4.142 trên 1.877,96 triệu cp bình quân [Q3HN p46] | Đúng |
| Số cổ phiếu | 1.714,3 triệu (DD 14/10) | **1.885,73 triệu** sau thưởng 10:1, ngày **21/09/2026** theo BCTC [Q3HN p46] (v1 ghi 22/09 — sửa) | Đã gồm 10,82 triệu ESOP phát hành 26/06 |
| Cash_P0 BQ | 7.377 | Chỉ là tiền mặt, thiếu 21.450 tỷ HTM | Không dùng làm tiền ròng |
| Tỷ lệ chuyển tiền (phản biện) | 0,22 / 0,28 | Tính lại: 952/(8.770,2 − 3.541,0 − 993,7) = 0,22; (952 + 1.246)/7.776,4 = 0,28 [calc] | Khớp |
| DSO (phản biện) | 86,5 | 13.064/55.098 × 365 = 86,5 [calc] | Khớp |

## 3. Chất lượng lợi nhuận

### 3a. Theo mảng (Q3 = 9T − 6T; cùng kỳ suy từ % FPT công bố) [calc; TCBC9T; TCBC6T; Q3HN p29–30]
| Mảng | Q3/26 | Q3/25 | YoY Q3 | 9T/26 | YoY 9T | YoY 6T |
|---|---|---|---|---|---|---|
| DT CNTT nước ngoài | 9.636 | 8.906 | **+8,2%** | 28.538 | +11,6% | +13,4% |
| LNTT CNTT nước ngoài | 1.504 | 1.391 | +8,1% | 4.510 | +10,7% | – |
| DT CNTT trong nước | 2.741 | 1.918 | +42,9% | 6.977 | +29,8% | +22,5% |
| LNTT CNTT trong nước | 234 | 106 | +120% | 542 | +108,5% | +100,5% |
| LNTT khối Công nghệ | 1.738 | 1.498 | +16,0% | 5.052 | +16,6% | +16,9% |
| DT khối GD, ĐT & khác | – | – | – | 4.508 | −3,1% | – |
| LNTT khối GD, ĐT & khác | – | – | – | 3.719 | +17,6% | – |
| — trong đó lãi liên kết | 797 | 546 | +46,0% | 2.220 | +42,6% | – |
| — phần còn lại (GD + lãi tiền gửi ròng + khác) | – | – | – | 1.499 | **−6,7%** | – |

Thị trường nước ngoài 9T [KQKD9T p5]: Nhật 13.197 tỷ (46%, +17,2% theo VND, +25,2% theo JPY; riêng Q3 theo JPY khoảng +15,3%) · Mỹ 6.485 (+6,5%; USD Q3 +5,8%) · EU 3.422 (+35,3%) · APAC 5.434 (**−4,6%**). Chuyển đổi số nước ngoài 14.411 tỷ (+16,3%), riêng Q3 4.801 tỷ (+3,8%). AI/Data Analytics 2.915 tỷ (+55%) [TCBC9T]. Hợp đồng lớn theo quy mô: >1 triệu USD 163 (+29,4%) [KQKD9T p6].
**Đọc:** Nhật vẫn là động lực nhưng đang chậm lại cả theo JPY; Mỹ gần nhóm peer lớn; APAC giảm. Mảng Mỹ nghiêng cấu trúc, Nhật nghiêng chu kỳ (khớp người đọc ngành độc lập). Số lượng hợp đồng >1 triệu USD tăng mạnh cho thấy cầu chưa gãy — cái chậm là hợp đồng siêu lớn.

### 3b. Liên kết, thuế, khoản tài chính [calc; Q3HN p08, p45]
- LNTT trừ lãi liên kết: 6.550 tỷ, +10,3%. LNST trừ lãi liên kết: 5.556 tỷ, **+5,2%**. Thuế trên LNTT-trừ-liên-kết 11,1% → **15,2%**. BCTC mô tả chính sách thuế tối thiểu toàn cầu 15% [Q3HN p27] nhưng không có dòng số liệu riêng ⇒ chưa xác nhận là nguyên nhân (GAPS G11).
- Lãi liên kết 9T 2.220 tỷ, không tách theo công ty [Q3HN p32]. Ước tách: FTEL 45,66% × LNST FOX 9T 2.884 ≈ 1.317; FRT 46,54% × (H1 629 + Q3 giả định bằng Q2) ≈ 451 (ước lượng); còn lại ≈ 452/9T, khoảng 600 tỷ/năm cho Synnex, FPT Online và các khoản khác (ước lượng) [BQ; calc].
- Lãi tiền gửi 9T 1.283 tỷ, lãi vay 612 tỷ, chênh lệch tỷ giá ròng −111 tỷ [Q3HN p45]. Hoàn nhập dự phòng khoảng 133 tỷ (mã 03), dự phòng phải thu giảm 584 → 347 tỷ phần lớn do FTEL ra khỏi hợp nhất.
- Chuyển đổi kế toán FTEL ghi thẳng +3.103 tỷ vào lợi nhuận chưa phân phối, không qua KQKD [Q3HN p43] ⇒ không phồng EPS, có phồng vốn chủ khi đọc P/B.

## 4. Bảng cân đối và dòng tiền

### 4a. Tiền ròng [Q3HN p03, p05, p32, p41–42; 6THN p3/p5]
| | 31/12/25 (còn FTEL) | 30/6/26 | 30/9/26 |
|---|---|---|---|
| Tiền + HTM | 40.547 | 28.972 | 28.830 |
| Vay ngắn + dài hạn | 21.073 | 18.448 | 16.596 |
| **Tiền ròng** | 19.474 | 10.523 | **12.233** |
Vay theo nguyên tệ: JPY 36,85 tỷ JPY (6.004 tỷ VND), GBP 17,5 triệu (619 tỷ), VND 9.974 tỷ; tiền gửi JPY 7 tỷ JPY (1.160 tỷ) [Q3HN p32, p42]. Vay JPY là phòng ngừa tự nhiên cho doanh thu JPY. Lưu ý: giá trị VND của mọi khoản vay ngoại tệ tại 30/9 trùng từng đồng với 30/6 (JPY 6.003.607.117.212 đ) ⇒ có vẻ chưa đánh giá lại theo tỷ giá cuối kỳ ở báo cáo quý; ảnh hưởng nhỏ so với tiền ròng. Tiền khách ứng trước (học phí 1.609 + người mua trả trước 761 = 2.370 tỷ, 1.257 đ/cp) là nguồn vốn trôi nổi thường trực theo mùa vụ; không trừ khỏi tiền ròng ở số tâm, đưa vào khoảng bất định §1.

### 4b. Vốn lưu động — tiền "kẹt" ở đâu [calc; Q3HN p03, p34]
| | 30/6/26 | 30/9/26 | Δ Q3 |
|---|---|---|---|
| Phải thu khách hàng (mã 131) | 10.851 | 10.847 | −4 |
| Hàng tồn kho, chủ yếu chi phí SXKD dở dang (1.811 tỷ tại 30/9) | 1.252 | 2.035 | **+782** |
| Phải thu theo tiến độ hợp đồng xây dựng (mã 134) | 302 | 280 | −21 |
| Trả trước người bán | 1.867 | 1.462 | −405 |
**DSO theo đúng định nghĩa khai trong PREREG** (tổng phải thu ngắn hạn mã 130 / doanh thu lõi TTM) = **86,5 ngày** (Q2 khoảng 91,9) — dưới ngưỡng 90 nhưng chỉ đệm 3,5 ngày (v1 dùng riêng mã 131 ra 72 ngày, khác định nghĩa — đã sửa).
**Chi phí SXKD dở dang** 686 (31/12/25) → 1.021 (30/6) → **1.811** (30/9). Đây là **chi phí đã bỏ ra nhưng hoãn ghi nhận** cho đến khi dự án được nghiệm thu — không làm phồng lợi nhuận, nhưng là **tiền bị kẹt và mang rủi ro nghiệm thu**; nếu nghiệm thu đúng hạn, nó có thể trở thành doanh thu Q4. (v1 gọi sai là "doanh thu chưa lập hoá đơn".) Khoản đúng nghĩa "doanh thu đã ghi nhận chưa thu" là mã 134 (302 → 280) và phải thu theo tiến độ bảo trì ở thuyết minh 8 (182 → 196) — gần như đi ngang [Q3HN p34]. Phải thu khu vực công theo tuổi nợ: không công bố (GAPS G9).

### 4c. Dòng tiền và tỷ lệ chuyển lãi thành tiền [Q3HN p10; 6THN p10; BCTN25 tr.168, tr.170; calc]
**Định nghĩa duy nhất:** conv = (CFO + lãi vay đã trả × (1 − t) − capex mã 21) / LN lõi vận hành; LN lõi vận hành = (LNTT − mã 05 "lãi hoạt động đầu tư" + mã 06 chi phí lãi vay) × (1 − t); t = thuế TNDN / (LNTT − lãi liên kết). Tử và mẫu cùng loại trừ lãi liên kết, lãi tiền gửi, cổ tức; cùng là trước chi phí lãi vay. Đây cũng là đại lượng nhân với LN lõi vận hành trong DCF (§7).
| Kỳ | Phạm vi | Tử số | LN lõi vận hành | t | **conv** |
|---|---|---|---|---|---|
| Cả năm 2024 | cũ (gồm FTEL) | 8.942 | 8.374 | 15,4% | **1,07** |
| Cả năm 2025 | cũ (gồm FTEL) | 5.732 | 9.628 | 14,6% | **0,60** |
| 9T/2025 | cũ (gồm FTEL) | 2.402 | 7.133 | 14,2% | **0,34** |
| 9T/2026 | mới (FTEL là liên kết) | −596 | 4.955 | 15,2% | **−0,12** |
| 2021–2023 | – | – | – | – | **chưa đo** (cần LCTT gốc BCTN 2022–2023; BQ không có mã 05/06/14 — GAPS G13) |
Tham khảo hình dạng 2021–2025 theo định nghĩa CŨ của DD 14/10 ((CFO − capex)/LNST mẹ, phạm vi lõi bỏ FTEL — định nghĩa KHÁC, không so trực tiếp): 0,55 · 0,44 · 0,80 · 0,86 · 0,39 [fpt_dcf_deconsol_20261014].
**Đọc:** mùa vụ rất mạnh (9T/2025 0,34 → cả năm 0,60; tử số Q4/2025 khoảng 3.329 tỷ), nên 9T thấp chưa đủ kết luận lãi giả. Nhưng 9T/2026 thấp hơn hẳn 9T/2025 kể cả khi tính đến việc FTEL (mảng nhiều tiền) đã ra khỏi phạm vi. Dòng tiền cả năm 2026 nhiều khả năng ở khoảng 0,3–0,45 (ước lượng) — đó là lý do kịch bản xấu dùng 0,40.
| | H1/26 | Q3/26 | 9T/26 |
|---|---|---|---|
| CFO | −1.145 | **2.097** | 952 |
| Capex (mã 21) | 1.337 | 692 | 2.029 |
| CFO − capex | −2.481 | 1.404 | **−1.077** |
CFO riêng Q3 dương nhưng thấp hơn mọi quý 3 từ 2023 (2.596 / 2.585 / 3.279, phạm vi lõi) [fpt_dcf_deconsol_20261014]. Capex 9T theo bộ phận: CNTT nước ngoài 439 · trong nước 684 · **GD-ĐT-khác 1.426 (56%)**, chủ yếu khuôn viên giáo dục: Bình Dương 415, Hoà Lạc 247, Quy Nhơn 61, Long An 37 tỷ dở dang [Q3HN p29, p37].

### 4d. TTDL và viễn thông
FTEL nằm ngoài hợp nhất từ 2026; FPT không công bố MW hay capex TTDL (GAPS G5). FOX theo BQ: LNST Q3/26 1.007 tỷ (+13,8%), PE 10,9, ADV 1 tháng khoảng 3,5 tỷ/phiên.

## 5. Giáo dục
- Học phí nhận trước: 1.992 (31/12/25) → **966 (30/6/26)** [6THN tm21, số do người phản biện đọc; phiên này chưa render lại trang] → 1.609 (30/9/26) [Q3HN p39] ⇒ Q3 tăng 643 tỷ theo mùa tuyển sinh. Chưa có số 30/9/2025 để so cùng kỳ (GAPS G3).
- Phần LNTT "GD + lãi ròng + khác" (trừ liên kết) 9T −6,7%; doanh thu khối −3,1%. BCTN 2025 viết giáo dục cần "tạo tiền đề để quay lại quỹ đạo tăng trưởng" [BCTN25].
- Khối này hút 56% capex 9T; tỷ lệ lấp đầy chỉ tiêu: chưa có nguồn (GAPS G3). Khớp nhận định của người đọc ngành độc lập về rủi ro chính sách (siết tuyển sinh học bạ, trần học phí).

## 6. Cổ đông, pha loãng, thanh khoản, pháp lý — ⚠️ WARNING THẤP–TRUNG BÌNH
- **Cổ đông lớn** [BCTN25]: Trương Gia Bình 6,89% · SCIC 5,67% · PYN Elite 3,67% · Bùi Quang Ngọc 1,76% · Trương Thị Thanh Thanh 1,48%. **Sở hữu nước ngoài 28,74% tại 18/05/2026, dự kiến 28,60% sau phát hành ESOP** [CBTT esopnq_p04], trần 49% (v1 ghi "chưa đo" — sửa).
- **Pha loãng:** thưởng 10:1 (171,4 triệu cp, ngày 21/09/2026 [Q3HN p46]) không pha loãng kinh tế. ESOP 2026 10,82 triệu cp giá 10.000 đ, hạn chế 3 năm, **đã phát hành 26/06/2026** và đã nằm trong 1.885,73 triệu cp [CBTT] — không phải pha loãng sắp tới. Vốn điều lệ 18.857 tỷ (GCN lần 62 ngày 20/10/2026).
- **Cổ tức:** đã trả 1.703 tỷ (1.000 đ/cp) trong 9T. Tạm ứng đợt 1/2026 1.000 đ/cp, chốt 30/11, trả 10/12/2026 [CBTT] — giá 52.700 hiện gồm quyền này.
- **Thanh khoản:** ADV 1 tháng khoảng 396 tỷ/phiên, 6 tháng 548 tỷ [BQ].
- **Kiểm toán:** PwC soát xét bán niên 2026 chấp nhận toàn phần, không nhấn mạnh [CBTT]. BCTC Q3 tự lập.
- **Thuế:** QĐ 1053/QĐ-DNL ngày 24/06/2026, tổng 243.977.316 đ, đã nộp 01/07 [CBTT]. Không trọng yếu.
- **WARNING 1 — FTEL:** đại diện vốn Nhà nước tại FTEL chuyển từ SCIC sang Bộ Công an năm 2025; Nhà nước nắm khoảng 50,16% [BCTN25] ⇒ free float FOX tối đa khoảng 4,2% (100% − 45,66% − 50,16%), giải thích thanh khoản 3,5 tỷ/phiên. Báo chí ghi FOX khó đáp ứng tiêu chí công ty đại chúng do free float thấp (index.vn) — chưa có quyết định cụ thể. Theo CV 1906, FPT thôi kiểm soát FTEL từ 01/01/2026 [Q3HN p14]. Phần FTEL khoảng 9,9k đ/cp theo thị giá (19% giá FPT); cổ tức, tăng vốn, pha loãng FTEL nay do bên kiểm soát khác quyết. Chiết khấu 0–30% trong định giá.
- **WARNING 2 — câu hỏi mở, chưa phải phát hiện:** "Chi phí phát triển khách hàng" ngắn hạn **618.772.175.000 đ** [Q3HN p37]. Khoản này **đã có từ 30/6/2026** với đúng số đó (Q2 tm14), và khoản vay 17,5 triệu GBP cũng có từ 30/6; dòng LCTT "tăng chi phí chờ phân bổ" H1 −958,3 và 9T −947,0 ⇒ Q3 khoảng +11 ⇒ **không phải nguyên nhân CFO Q3 yếu** (v1 suy diễn sai). Việc hai số trùng từng đồng nhiều khả năng chỉ do cùng tỷ giá lịch sử (vay ngoại tệ chưa đánh giá lại, §4a), không chứng minh đây là khoản trả trước cho khách hàng ở Anh. **Giả thuyết**, cần IR trả lời: (1) bản chất khoản này và đối tác; (2) lịch phân bổ vào chi phí (GAPS G2).
- **Giao dịch bên liên quan** 9T [Q3HN p47–48]: mua từ Synnex FPT 663 tỷ (cùng kỳ 308), bán cho FRT 386 tỷ, bán/mua với FTEL 115/211 tỷ. Dưới 2% doanh thu, quan hệ thương mại thường. BC quản trị 6T/2026 (89 trang scan) **chưa đọc trong phiên này** (GAPS G7).
- **Quét tin 01/11/2026** (WebSearch): không thấy quyết định xử phạt hay kết luận thanh tra mới với FPT/FTEL trong 10/2026; có kết luận cũ của Thanh tra Sở TT&TT Bình Dương về FTEL chi nhánh Bình Dương (giai đoạn 2022–2024, kênh IPTV/OTT ngoài danh mục, hạ tầng cáp) — quy mô chi nhánh, không trọng yếu với FPT.

## 7. Định giá [calc]
**Cấu trúc:** giá trị = lõi vận hành (DCF FCFE) + FTEL theo thị giá trừ chiết khấu + FRT theo thị giá trừ 20% + liên kết khác theo sổ khoảng 1.500 tỷ (ước lượng) + TPBank và FPTS theo giá gốc 945 tỷ + tiền ròng 12.233 tỷ (chưa trừ cổ tức, vì giá còn quyền).
**Lõi vận hành:** LNST trừ liên kết TTM khoảng 7.466 tỷ (ước lượng; Q4/25 giả định lãi liên kết khoảng 600 tỷ, GAPS G10); trừ thu nhập lãi ròng sau thuế ⇒ **6.705 tỷ** (ước lượng). Thị trường đang trả **8,0 lần**.
**Ke nội địa** (khung 30/10, β khoảng 1,1): 12,3–13,4%, dải rộng 10,5–14,0%. Mốc 15,8% (Damodaran) chỉ là góc nhìn nhà đầu tư nước ngoài. Tỷ trọng giá trị cuối kỳ 62–72%.
| Kịch bản | P (ước lượng) | Tăng LN lõi 5 năm | conv | g dài hạn | Ke | Chiết khấu FTEL | RONIC ngầm định | FV |
|---|---|---|---|---|---|---|---|---|
| Xấu: AI giảm phát giá, Mỹ/APAC co, tiền không về | 0,35 | 3%/năm | **0,40** | 3,0% | 13,4% | 30% | 5,0% (< Ke: giả định cắt giảm vĩnh viễn) | **34.100** |
| Cơ sở: Nhật giữ, Mỹ đi ngang, tiền về theo mùa vụ | 0,45 | 9%/năm | 0,75 | 4,0% | 12,85% | 15% | 16,0% | **59.800** |
| Tốt: Nhật + AI cộng thêm | 0,20 | 14%/năm | 0,85 | **4,0%** | 12,3% | 0% | 26,7% (gần ROE lịch sử) | **79.600** |
Kỳ vọng có trọng số **54.800 (+4%)**. Độ nhạy cơ sở g × Ke: g 3–5% × Ke 12,3–13,4% cho **55,0–66,7k**. Theo conv: 0,40 → 41,9k · 0,60 → 52,2k · 0,90 → 67,5k. Kịch bản tốt không còn vừa hạ Ke vừa nâng g (v1 84,6k với g 5%).
**Cầu nối FV:** 14/10 49,6k → 21/10 49,8k (mô hình cũ, Ke 14–16%, FRT theo sổ) → v1 01/11 58,8k → v2 59,8k. Cùng cấu trúc mới nhưng Ke 15% cho 52,1k ⇒ khoảng **+7,7k** là do đổi khung Ke (theo chuẩn khung 30/10), phần còn lại do SOTP theo thị giá và tách tiền ròng — **đổi phương pháp, không do tin Q3**; +1,0k từ v1 → v2 là cộng lại cổ tức còn quyền. Lưu ý: tiêu chí PREREG "FV > giá" nay được chấm trên mô hình dựng sau PREREG; trên mô hình cũ (49,8k) tiêu chí này không đạt. Kết luận "chưa MUA" không đổi vì CFO không đạt.
**Comp:** CMG PE 10,9, ELC 9,3, FOX 10,9 [BQ 30/10]. PE FPT 10 năm p10/p50/p90 = 10,5 / 15,4 / 23,7 [BQ weekly]. Peer khu vực: chưa đo (GAPS G8).

## 8. Chấm lại PREREG 21/10 (`fpt_q3_eval_20261021/PREREG.md`)
| Tiêu chí khai trước | Số gốc | Kết quả |
|---|---|---|
| LNST mẹ 9T ≥ +12% | +13,3% | **ĐẠT** |
| Ký mới NN 9T so với +32,3% (H1) | +23,1% 9T; Q3 **+3,6%** | **Chậm lại** |
| CFO Q3 ≥ ~2.600 tỷ | **2.097** | **KHÔNG ĐẠT** (trên ngưỡng xấu 1.500) |
| Phải thu không tăng | 10.851 → 10.847 | **ĐẠT** (dở dang +782 tỷ, §4b) |
| DSO < 90 (định nghĩa PREREG) | **86,5** | Đạt, đệm mỏng 3,5 ngày |
| Kết luận khung 21/10 | MUA cần CFO ≥ 2.600 **và** phải thu **và** FV > giá | **Chưa thoả**; không thuộc nhánh "không mua" |

## 9. So với nhận định của người đọc ngành độc lập (đọc mù 01/11)
- Xuất khẩu, cấu trúc 0,45 / chu kỳ 0,45: Q3 nghiêng nhẹ về cấu trúc — book-to-bill Q3 1,02 so với 1,39 ở 6T; hợp đồng siêu lớn giảm; Mỹ +6,5%. Nhưng số hợp đồng >1 triệu USD +29,4% là chiều ngược lại.
- Ký mới là TCV hay ACV: FPT không định nghĩa (GAPS G1). Nhân sự CNTT 37.618 (+5,6% so với 31/12/2025) [Q3HN p12].
- Trong nước +43% doanh thu Q3: cầu từ chính sách (NQ 57); nếu giải ngân KHCN-ĐMST-CĐS 2026 dưới 80%, dở dang và phải thu khu vực công là chỗ phải theo dõi.
- Theo dõi cùng: Infosys FY27, Accenture đáy guidance, Tankan, USD/JPY.

## 10. Mốc kiểm chứng — điều kiện đổi nhận định THEO CẢ HAI CHIỀU
Ngưỡng CFO dưới đây quy đổi từ mô hình: CFO cả năm ≈ conv × LN lõi vận hành 2026 (≈ 6.607) − lãi vay trả sau thuế (≈ 641) + capex (≈ 2.705) (ước lượng) [calc]: conv 0,2 ⇔ CFO ~3.400; 0,4 ⇔ ~4.700; 0,6 ⇔ ~6.000; **0,75 ⇔ ~7.000**; CFO 4.000 ⇔ conv 0,29; CFO 2.000 ⇔ conv ~0.
| Mốc (ngày dự kiến) | Nâng nhận định nếu | Hạ nhận định nếu |
|---|---|---|
| KQKD tháng 10–11/2026 (giữa 11 và 12/2026) | Ký mới NN lũy kế giữ ≥ +20% và thêm ≥ 2 hợp đồng >10 triệu USD | Lũy kế ký mới dưới +15% |
| BCTC hợp nhất Q4/2026 (cuối 01/2027) | CFO cả năm ≥ **6.000 tỷ** (conv ≥ 0,6) và dở dang về dưới 1.200 tỷ ⇒ kịch bản cơ sở có cơ sở, chuyển xác suất từ xấu sang cơ sở | CFO cả năm < **3.400 tỷ** (conv < 0,2) hoặc dở dang + phải thu tiếp tục tăng ⇒ kịch bản xấu thành trung tâm (~34–42k) |
| Vùng giữa | CFO 3.400–6.000 (conv 0,2–0,6): giữ nguyên xác suất | |
| Ký mới Q4/2026 so với Q4/25 (11.273 tỷ) | ≥ +10% | Âm |
| DT CNTT NN theo JPY và USD (KQKD 2026) | Mỹ ≥ +10%, APAC hết âm | Nhật theo JPY dưới +15% cả năm (Q3 đã khoảng +15,3%) |
| Kế hoạch 2027 (ĐHCĐ khoảng 04/2027) | LNTT ≥ +15% kèm mục tiêu dòng tiền | Dưới +10% |
| FTEL | Cổ tức FTEL 2026 ≥ 2.000 đ/cp | Tăng vốn/pha loãng FTEL, FOX mất tư cách đại chúng, hoặc FPT phải thoái vốn dưới thị giá |
| Khoản 618,8 tỷ | IR giải thích có doanh thu đối ứng, lịch phân bổ ngắn | Phải phân bổ lớn vào chi phí |

## 11. Hạn chế
Q3/2026 từ BCTC chưa soát xét. Doanh thu theo khu vực chỉ có trong slide IR. Lãi liên kết không tách theo công ty. Q4/25 lõi và lãi liên kết Q4/25 là ước lượng. Chuỗi conv 2021–2023 chưa đo trên định nghĩa thống nhất. Mọi tham số DCF là (ước lượng). Chi tiết: `GAPS.md`.

## 12. Bảng áp đính chính của phản biện
| # | Đính chính | Trạng thái | Cách áp / lý do |
|---|---|---|---|
| C1 | Vùng cơ sở 51–62k không tái lập | **Đã áp** | Vùng = lưới 1 trục g 3–5% × Ke 12,3–13,4%, conv 0,75: 55,0–66,7k (cùng gốc có quyền cổ tức; 54,0–65,7k nếu trừ). Giá DƯỚI vùng. Sửa tiêu đề, §0, §1; trục conv báo riêng |
| C2 | "0,12 đồng/đồng lãi" lệch gốc | **Đã áp** | Bỏ khỏi tiêu đề và §0; 0,22 và 0,28 tự tính lại khớp, ghi kèm định nghĩa |
| C3 | Ba định nghĩa conv; ngưỡng §10; kịch bản xấu | **Đã áp** | Một định nghĩa (CFO + lãi vay trả sau thuế − capex)/LN lõi vận hành; chuỗi 2024, 2025, 9T/25, 9T/26 đo từ BCTN25 và BCTC Q3. 2021–2023 **chưa đo** (thiếu LCTT gốc — GAPS G13), chỉ hiện định nghĩa cũ để thấy hình dạng. Kịch bản xấu conv 0,40 (FV 34,1k), P 0,30 → 0,35. Ngưỡng §10 quy đổi từ mô hình |
| T1 | Cổ tức 1.000đ còn quyền | **Đã áp** | Không trừ cổ tức khỏi tiền ròng; mọi FV +1.000 |
| T2 | Dở dang ≠ doanh thu chưa lập hoá đơn | **Đã áp** | §4b viết lại; mã 134 và tm8 đi ngang |
| T3 | 618,8 tỷ suy diễn quá mức | **Đã áp** | Có từ 30/6, Q3 ~+11, vay ngoại tệ chưa đánh giá lại; chuyển thành giả thuyết + 2 câu hỏi IR |
| T4 | DSO sai định nghĩa | **Đã áp** | 86,5 ngày theo PREREG (tự tính lại) |
| T5 | Kịch bản tốt vừa hạ Ke vừa nâng g | **Đã áp** | g 4% ⇒ 79,6k (cùng gốc có quyền; 78,6k nếu trừ, khớp phản biện); thêm cột RONIC |
| T6 | SOTP đếm thiếu | **Áp một phần** | Đưa vào khoảng bất định −1,3k…+2,4k đ/cp (§1); không đổi số tâm vì lãi liên kết khác chỉ ước lượng (FRT Q3 chưa có trong BQ) và TPB/FPTS chưa đo thị giá |
| T7 | Cầu nối FV | **Đã áp** | §7: +7,7k do đổi khung Ke, phần còn lại đổi phương pháp SOTP; không do tin Q3 |
| T8 | Thiếu dữ kiện cân bằng | **Đã áp** | §0, §3a: hợp đồng >1 triệu USD +29,4%, phải thu thu về ~473, JPY Q3 ~+15,3%, USD +5,8%, hàng hoá biên 12,4% (số lấy từ phản biện đối chiếu KQKD9T; JPY/USD Q3 là ước lượng từ lũy kế, chưa render lại slide trong phiên này) |
| Thấp | Sở hữu NN 28,74%; ESOP đã phát hành; ngày 21/9; FTEL 50,16% ⇒ free float ≤4,2%; học phí 966; hoàn nhập 133; PE thấp nhất ~8 năm | **Đã áp** | §0, §2, §3b, §5, §6 |
| G7 | Đọc BC quản trị 6T/2026 | **Không áp** | Ngoài ngân sách phiên (89 trang scan); giữ GAPS G7 |
