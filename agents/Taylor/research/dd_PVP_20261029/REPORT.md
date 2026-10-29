# DD — PVP (CTCP Vận tải Dầu khí Thái Bình Dương / PVTrans Pacific, HOSE) · 2026-10-29 · v2 BẢN SẠCH · job `Taylor_20261029_072547`

**Verdict: NON / không-phải-case-§2.5 @18.750** · **v2.1** (7 sửa nhỏ của phản biện vòng 2, §14) (giá sàn, DNSE `latest_trade` 14:29:04 29/10; đóng cửa BQ 28/10 là 20.150).
PVP đang ở **ĐỈNH** chu kỳ lợi nhuận, không phải đáy. Vì vậy điều kiện "đáy chưa tới" của §2.5 bị ❌, và một ❌ là loại. **Không** có ca fear-buy ở đây.
Phần định giá dưới đây là **quan điểm định giá ngoài khung §2.5**. Nó không phải căn cứ để mua theo §2.5. Dải tham khảo **15,5–22,4k (ước lượng)**.
Sàn tài sản là dải **13,6–14,9k trước capex**. Nếu công ty mua cả hai dự án tàu, sàn chỉ còn **4,7–6,1k** (cận dưới = 177 tỷ cam kết FSO năm 1 chưa hoà giải không thành tiền).
**Chạy lại §2.5 chỉ khi có tín hiệu chu kỳ chạm đáy** (§11). Giá giảm một mình thì không đủ.

> Chỉ NGHIÊN CỨU. Không phải khuyến nghị mua, không lệnh, không wire. Người quyết định là user. v1 (nhãn AMBIGUOUS) giữ ở `REPORT_v1_ambiguous.md`.
> **Nguồn.** **[Q3 pN]** = `src/bctc_q3_2026.pdf`, trang PDF N (scan, chưa soát xét). **[H1 pN]** = `src/bctc_banien_2026_kiemtoan.pdf`: bán niên 2026
> **soát xét** bởi Deloitte, số 0152/VN1A-HC-BC ngày 14/08/2026, kết luận chấp nhận toàn phần [H1 p6]. **[Q2 pN]** = `src/bctc_q2_2026.pdf`.
> **[AGM pN]** = `src/agm2026_nq_bienban.pdf`: NQ 01-2026/NQ-TBD-ĐHĐCĐ + biên bản ĐHĐCĐ thường niên 23/06/2026, tải từ pacificshipping.vn/dai-hoi-co-dong, 72 trang scan.
> **[CB]** = CBTT gốc (`src/cb_*.pdf`). **[BQ]** = `tav2_bq`. **[DNSE]** = `dnse_api` lúc 14:29 29/10. **[web]** = báo chí, nguồn thứ cấp (§13).
> Mọi phép tính nằm trong `calc.py` → `out.txt` (**0 FAIL / 29 self-check**, v2.1). Nền ngành lấy từ Bobby (`kb/data_registry/market-state/sector_read_oil_gas_shipping_20261029.md`).
> PVP lập **BCTC riêng**: không có công ty con, không có công ty liên kết [Q3 p8].

## 0. Tóm tắt

| Câu hỏi | Trả lời ngắn (số đo) |
|---|---|
| Giá | Sàn **18.750** [DNSE 14:29, KL 291.740 cp]. BQ 28/10 **20.150**. Brief ghi 22.900 là giá đóng cửa ngày **20/10**. So với đỉnh 25.000 (08/10) giá đã giảm **−25%** |
| LN 9T đến từ đâu | LN gộp vận tải **292,9 tỷ**, gấp **2,08 lần** 9T/25 (140,7) và bằng **111%** mức tăng LN gộp toàn công ty. Mảng FSO đi ngang; thương mại LPG và ủy thác lãi ≈0 |
| Tăng trưởng thật | Báo cáo **+79,5%** LNTT 9T. Cùng cơ sở (bỏ khác biệt trích sửa chữa TT99 + khấu hao Apollo) chỉ còn **+23% … +34%**. Q3: LN gộp vận tải báo cáo +12,6% YoY, nhưng cùng cơ sở là **−12%** (suy luận) |
| Vì sao Q3 giảm 50% so với Q2 | **DT vận tải quốc tế −39%** (365,5 → 224,4), LN gộp vận tải **−52%**. Nhiên liệu đi ngang, tỷ giá không trọng yếu. BCTC không nêu nguyên nhân gốc |
| 9T so với kế hoạch | KH **xác nhận từ NQ ĐHĐCĐ** [AGM p21]: DT 2.700 / LNTT 270 / LNST 216, cổ tức 10%. 9T đạt **81,7% / 129,2% / 128,7%** |
| Bảng cân đối | Tiền ròng **1.125,6 tỷ** (30/9). Sau trừ phải trả cổ tức 109,5 (cổ tức 2025 103,7, lịch thanh toán 20/10 theo NQ 17 — chưa có chứng từ sau 20/10; + ~5,8 tồn cũ) còn **1.016 tỷ ≈ 9.797 đ/cp** |
| Rủi ro lớn nhất | ĐHĐCĐ đã duyệt mua tàu **116 tr USD ≈ 3.021 tỷ = 1,55 lần vốn hoá**, đúng vùng giá tàu cũ ở đỉnh. Phần VCSH chi ra là **916 tỷ ≈ 90% tiền ròng** sau cổ tức. Mua cả hai dự án ⇒ nợ ròng ~2.005 tỷ, ND/VCSH 0,95 |
| FSO | Lịch cam kết cho thuê [H1 p34] hàm ý **dòng tiền FSO giảm**: hiện ~239/năm → **~136/năm** từ 7/2027 → **~37/năm** từ 7/2031 |
| Định giá (ngoài khung §2.5) | PE TTM **6,04**, PB **0,93**. PB trung vị lịch sử ra **15,5k**. SOTP kỳ vọng ra **22,4k**, hoặc **20,8k** nếu chắc chắn mua cả hai dự án. PE lịch sử × LN 2027 ra **8,1k**: đây là "giá thị trường quen trả", không phải giá trị (đều ước lượng) |

## 1. Kiểm chứng điều Mike chưa kiểm

| Mike/báo chí ghi | Kiểm từ gốc | Kết quả |
|---|---|---|
| Giá đóng cửa 28/10 = 22.900 (BQ) | BQ 28/10 = **20.150**; 20/10 = 22.900. DNSE 29/10 14:29 = **18.750** (sàn; tham chiếu 20.150) | ❌ Brief lệch 1 tuần. Mọi định giá trong file dùng 18.750 |
| BQ: Q3 DT ~838, LNST ~67,5 | [Q3 p6] **838,414 / 67,514** | ✅ |
| Q2 134,2, Q1 ~75,5, 6T 209,7 | Tổng các quý 75,54 + 134,19 = **209,73**; số 6T soát xét [H1 p9] **210,51** | ✅ Chênh **+0,78** là **điều chỉnh khi soát xét**. Q1 suy ngược ra 76,32 là do điều chỉnh này, không phải lỗi BQ |
| KH 2026: 2.700 / 270 / 216 | [AGM p21] Phụ lục 04, NQ 01-2026/NQ-TBD-ĐHĐCĐ 23/06/2026. Cổ tức KH 10%. HĐQT được tự điều chỉnh chỉ tiêu | ✅ **gốc**. Con số "77,6%" trên báo chí gần nhất với phép chia LNST 6T cho KH **LNTT**: 209,73/270 = 77,7%. Tôi không tái lập được đúng 77,6% |
| "9T ~277 vượt KH" | 9T LNST **278,03** [Q3 p6] = 128,7% KH LNST | ✅ |
| Cổ tức tiền 10% | [CB NQ 17/NQ-TBD-HĐQT 28/08/2026] cổ tức **năm 2025** 10%, 1.000 đ/cp: ĐKCC **18/09**, **thanh toán 20/10/2026**, tổng **103,70 tỷ**. Tại 30/9 phải trả cổ tức là 109,5 tỷ [Q3 p4] | ✅ Lịch thanh toán 20/10 theo NQ 17 (**sau** ngày BCTC; chưa có chứng từ sau 20/10). Trừ toàn bộ phải trả 109,5 (gồm ~5,8 tồn cũ) ⇒ tiền ròng ≈ 1.016. Ngoài ra **KH tạm ứng cổ tức 2026 10%** (~103,7 tỷ nữa, chưa có ngày) [AGM p22] |
| ĐHĐCĐ bất thường gia hạn | [CB] NQ **22**/NQ-TBD-HĐQT **02/10**: hạn **≤15/11/2026**. NQ **23**/NQ-TBD-HĐQT **23/10**: hạn **≤30/11/2026**. Lý do cả hai lần: "hoàn thiện các văn kiện" | ✅ gia hạn 2 lần, văn kiện **chưa công bố** |
| Mua Aframax thứ 3 | [AGM p21, H1 p34] ĐHĐCĐ 23/06 duyệt (1) **Aframax số 2** 56,5 tr USD (VCSH 17,08 / vay 39,42) và (2) **Aframax số 3 HOẶC 2 tàu MR1/MR2** 59,5 tr USD (VCSH 18,11 / vay 41,39). Aframax #2 có báo cáo khả thi riêng (dự án DT-07/26/TBD, Phụ lục 11 [AGM p37–45]). Đến 14/08, **chưa ký thoả thuận nào** [H1 p34] | ⚠️ Chưa mua tàu nào. ĐHĐCĐ bất thường dự kiến bàn tàu #3 [web 12/09] |
| Tin dự kiến tăng vốn | Không thấy trong BCTC, NQ ĐHĐCĐ 2026 hay 8 CBTT đã đọc. Cơ cấu vốn = 30% VCSH + 70% vay | ❌ Không xác nhận. Nếu văn kiện ĐHĐCĐ bất thường có phát hành ⇒ xem §11 |
| GĐ mới Phan Công từ 23/6 | [H1 p4] Hoàng Đức Chính miễn nhiệm 23/06; Phan Công bổ nhiệm GĐ + TV HĐQT 23/06, đại diện pháp luật từ 10/07. PGĐ Vũ Ngọc Khôi miễn nhiệm 12/08. [CB QĐ 20/QĐ-TBD-HĐQT 03/09/2026] bổ nhiệm có thời hạn **ông Vũ Thanh Tùng** làm PGĐ (GĐ đề nghị, tờ trình 43/TTr-GĐ 13/08; NQ chi bộ 15-NQ/CB-TBD 27/08) | ✅ Quy trình bổ nhiệm nội bộ bình thường. Vẫn là WARNING quản trị (§10) |
| GD với người có liên quan | [CB] NQ 16/NQ-TBD-HĐQT 18/08/2026: 6 đối tác trong hệ thống PVTrans, giá trị **"theo thực tế phát sinh"** | ⚠️ Giao dịch vận hành; không có trần giá trị |
| Cổ đông lớn; VIS Rating A | [H1 p28] PVTrans **64,92%**, Lê Ngọc Anh 6,66%. VIS **A, ổn định** [web cafef] | ✅ (VIS từ nguồn thứ cấp). **Room ngoại: chưa kiểm** (không có nguồn trong BQ/DNSE đã dùng) |

## 2. (A) Lợi nhuận đến từ đâu — theo mảng [Q3 p13-14, Q2 p13-14, H1 p29-30]

| Mảng | Q1/26 | Q2/26 | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|---|---|
| **Vận tải** DT | 232,6 | 365,5 | 224,4 | 172,9 | 822,5 | 501,1 |
| Vận tải LN gộp (biên) | 76,0 | **146,5 (40,1%)** | **70,4 (31,4%)** | 62,5 (36,2%) | **292,9** | 140,7 |
| **FSO** DT / LN gộp | — | 59,3 / — | 59,7 / 22,6 | 60,0 / 21,9 | 177,4 / 66,3 | 182,9 / 68,5 |
| Thương mại LPG DT / LN gộp | — | 51,6 / ~0 | 272,2 / 0,06 | 451,8 / ~0 | — | — |
| Ủy thác khai thác tàu cho PVTrans DT / LN gộp | — | 244,4 / 0,8 | 280,0 / 0,66 | 147,3 / 0,9 | — | — |
| **Tổng LN gộp** | | | **93,9** | 85,3 | **362,4** | 225,9 |

- **Vận tải 100% quốc tế** từ 2025 [H1 p30]. PVP vì vậy nhạy cước quốc tế hơn hẳn PVT (Bobby §3.5).
- **Đội tàu sở hữu: 3 tàu dầu + 1 FSO** [Q3 p10]. Apollo (Aframax, **hết khấu hao**, NBV 0). Pacific Era (MR, NBV 342,5, thế chấp Woori). Pacific Pride (MR, NBV 495,7, thế chấp VCB).
  FSO Đại Hùng Queen (NBV 389,1, còn ~2,6 năm khấu hao). Có thuê tàu ngoài (Signal Maritime Aframax Pool, Sokana) [H1 p22]. BCTC không ghi tuổi tàu; theo [web], Apollo ~21 tuổi năm 2026.
- [web elibook 25/05/2026, dẫn CTCK]: Apollo tái ký thuê **70.000 USD/ngày**. Thời hạn và bên thuê không nêu. **Chưa kiểm**.
- **Q3 so với Q2:** DT vận tải −39%, LN gộp −52%. Nhiên liệu Q3 77,1 ≈ Q2 80,7 ⇒ nguyên nhân là **doanh thu giảm**, không phải chi phí tăng. Nguyên nhân gốc (off-hire, thời điểm chuyến, tàu thuê ngoài) **chưa kiểm**.
- **Q3 so với cùng kỳ, cùng cơ sở:** Q3/25 còn trích dự phòng sửa chữa (≈ 53,1/3 = **17,7 tỷ/quý**, giả định chia đều và hạch toán vào giá vốn vận tải — **suy luận**).
  LN gộp vận tải Q3/25 cùng cơ sở là 80,2 ⇒ Q3/26 70,4 là **−12,3%**, không phải +12,6%. Khấu hao Apollo không ảnh hưởng so sánh Q3: Apollo hết khấu hao khoảng giữa 2025, xem §3.

## 3. (B) Chất lượng lợi nhuận

| Khoản | 9T/26 | 9T/25 | Ghi chú |
|---|---|---|---|
| Lãi thanh lý tàu | **0** | 0 | Thu nhập khác 9T là 0,006 tỷ [Q3 p6] |
| Lãi tiền gửi (LCTT mã 05) | 57,4 | 38,6 | **16,5% LNTT**. Phần này **giảm** khi chi ~916 tỷ VCSH mua tàu |
| Dòng LCTT mã 03 "Các khoản dự phòng" (chung; gán cho trích sửa chữa định kỳ là **suy luận**) | **0** | **53,1** | TT99: ngừng trích trước [H1 p15]. Số dư 232,9 chuyển hết sang ngắn hạn ⇒ dự kiến lên đà trong 12 tháng (suy luận) |
| Khấu hao TSCĐ (LCTT mã 02) | 239,5 | 275,2 | Chênh **35,7**. Q2: 79,8 so với 98,5 (chênh 18,7) [Q2 p14, TM 8a]. Q1+Q3 chênh 16,9 ⇒ Apollo hết khấu hao khoảng **giữa 2025**. Era/Pride đã khấu hao đủ năm 2025 (suy luận: gán phần chênh cho Apollo) |
| Tỷ giá Q3 | ròng khoảng −4,5 | | Không trọng yếu. Vay **toàn VND** |

**LNTT 9T cùng cơ sở** [out.txt §3]:

| Cơ sở | 9T/26 | 9T/25 | Tăng trưởng |
|---|---|---|---|
| Báo cáo | 348,9 | 194,3 | +79,5% |
| A: cả hai kỳ ĐỀU trích sửa chữa và ĐỀU khấu hao Apollo | 260,2 | 194,3 | **+33,9%** |
| B: cả hai kỳ KHÔNG trích sửa chữa và KHÔNG khấu hao Apollo | 348,9 | 283,1 | **+23,2%** |

Hai cơ sở khác nhau chỉ vì mẫu số khác nhau. Tăng trưởng thật nằm trong **+23% … +34%**. v1 ghi +52% vì chỉ bỏ trích sửa chữa mà quên khấu hao Apollo.
**Đọc:** LN 9T/26 là **thật về tiền**: CFO 9T 473,0 tỷ = 1,70 lần LNST, capex chỉ 0,18. Nhưng phần tăng thật nhỏ hơn nhiều so với con số báo cáo,
và phần cước quốc tế đỉnh Q2 là phần kém bền nhất.

## 4. (C) Bảng cân đối & dòng tiền 30/9/2026 [Q3 p3-5, p9, p11]

| | 30/9/2026 | 01/01/2026 |
|---|---|---|
| Tiền + tương đương / Tiền gửi HTM | 718,2 / 1.015,9 | 503,9 / 818,8 |
| Vay NH / DH (VND) | 134,9 / 473,5 | 157,6 / 574,7 |
| **Tiền ròng** | **1.125,6** | 590,4 |
| Phải trả cổ tức (103,7 cổ tức 2025, lịch thanh toán 20/10 theo NQ 17, chưa có chứng từ sau 20/10; + ~5,8 tồn cũ) | 109,5 | 6,3 |
| Dự phòng sửa chữa định kỳ | 232,9 | 232,9 |
| Phải thu KH | 534,8 (PVTrans 299,8) | 254,2 |
| VCSH / BVPS | 2.099,6 / **20.246** | 1.931,3 |

- Lịch trả nợ 134,9 tỷ/năm, khoản cuối đáo hạn 2030 [H1 p25].
- **Capex đã duyệt** [AGM p21]: 116 tr USD ≈ **3.021 tỷ** (VCB 26.040), gồm VCSH 916 và vay 2.104.
  Báo cáo khả thi Aframax #2 của chính công ty [AGM p40, p44]: giá tàu **56,318 tr USD**, tàu ≤15 tuổi, cờ nước ngoài.
  Giả định TC bình quân đời dự án **30.240 USD/ngày**, 346 ngày khai thác/năm. Kết quả: **NPV dự án 43.719 USD (≈ 0)**, **IRR 7,67% (cấp dự án)**, ROE 10,03%; **NPV vốn CSH +2.237.928 USD** [AGM p44]; ngưỡng IRRmin = 10% + 1% rủi ro [AGM p43].
  Dự báo TC 1 năm (bình quân 3 broker) cho tàu non-eco: 53.800 (2026) → 43.800 (2027) → 39.400 (2028).
  ⇒ **IRR cấp dự án 7,67% thấp hơn chính ngưỡng IRRmin 11% công ty tự đặt**; NPV vốn CSH dương (+2,24 tr USD) là nhờ đòn bẩy vay 70%.
  Giả định "mua đắt −10%" ở kịch bản cơ sở vì vậy **thận trọng hơn** mô hình của công ty (đó là nhận định của nhóm, không phải kết luận của báo cáo khả thi).
- **Kịch bản mua (ước lượng, gắn xác suất)**:

| Kịch bản | P (ước lượng) | Giá trị tàu | VCSH chi | Lý do gán P |
|---|---|---|---|---|
| Mua cả hai dự án | 0,50 | 116,0 tr USD | 916 tỷ | ĐHĐCĐ đã duyệt cả hai; ĐHĐCĐ bất thường được triệu tập riêng cho tàu #3 [web 12/09] (v2.1: bỏ lý do "hạn VAT 31/12/26" — AGM p40: tàu cờ nước ngoài, không nhập khẩu, không phát sinh thuế NK/VAT) |
| Chỉ Aframax #2 | 0,35 | 56,5 | 445 | #2 đã có báo cáo khả thi; #3 có thể hoãn khi giá tàu cao hoặc ĐHĐCĐ bất thường tiếp tục bị lùi |
| Không mua | 0,15 | 0 | 0 | Đã 4 tháng chưa ký; ĐHĐCĐ bất thường đã gia hạn 2 lần |
| **Kỳ vọng** | | **77,8 tr USD ≈ 2.025 tỷ** | **614 tỷ** | |

## 5. (D) Khách hàng, hợp đồng, bên liên quan — và FSO

- **Bên liên quan chiếm 63,3% DT 6T** (865,4/1.367,3) [H1 p38]: PVTrans 555,7 (FSO + ủy thác), BSR (Dung Quất) 199,5, LPG Việt Nam 94,5.
  Q2 riêng: doanh thu từ PVTrans 554,7 [Q2 p15]. Bảng Q3 ghi PVTrans 951,5, lớn hơn tổng DT Q3 ⇒ nhiều khả năng là số lũy kế 9T (suy luận).
- **Hợp đồng FSO Đại Hùng Queen** [H1 p34], đọc lại nguyên văn: khoản cam kết cho thuê không hủy ngang **1.163,7 tỷ** *"thể hiện khoản tiền Công ty sẽ
  thu từ Tổng Công ty ... từ việc cho thuê kho nổi FSO Đại Hùng Queen"*. Biên bản 03/06/2025 thống nhất *"điều chỉnh giá cước và gia hạn hợp đồng đến
  ngày 31 tháng 12 năm 2036"*. Cam kết *"đang được tính theo thời hạn và đơn giá mới này"*. Phụ lục hợp đồng đang hoàn tất thủ tục ký.
  ⇒ Con số này **chỉ gồm FSO** (không có tàu khác) và **đã phản ánh giá mới** (không nhân thêm hệ số giảm giá). v1 hiểu sai cả hai điểm.

| Lịch cam kết [H1 p34] | 30/6/2026 | /năm | 01/01/2026 | /năm |
|---|---|---|---|---|
| ≤ 1 năm | 415,8 | 415,8 (7/26–6/27) | 234,6 | 234,6 |
| Năm 2–5 | 542,9 | **135,7** (7/27–6/31) | 652,9 | 163,2 |
| Sau 5 năm | 205,0 | **37,3** (7/31–12/36, 5,5 năm) | 238,1 | 39,7 |
| Tổng | 1.163,7 | | 1.125,6 | |

- **Hàm ý:** doanh thu FSO đang chạy khoảng **239/năm** (Q3 × 4). Theo lịch cam kết, nó giảm còn khoảng **136/năm** từ 7/2027, rồi **~37/năm** từ 7/2031.
  Giá vốn FSO ≈ toàn bộ là khấu hao (148/năm, hết khoảng 2029). Vì vậy LN gộp FSO 2027–29 sẽ về **gần 0 hoặc âm**, và **dòng tiền FSO giảm khoảng 100 tỷ/năm** từ H2/2027.
  **Rủi ro FSO nằm ở dòng tiền theo lịch, không phải ở chuyện "phụ lục chưa ký".** v1 viết "+148 tỷ/năm khi FSO hết khấu hao" là **sai**; đã bỏ.
- **Không hoà giải được mục "≤1 năm 415,8":** tại 01/01/2026 mục này là 234,6, khớp với mức doanh thu hiện tại. Trong H1 công ty đã thu 117,8,
  nhưng tổng cam kết vẫn **tăng** +38,0 ⇒ có khoảng **155,8 tỷ cam kết mới**, dồn hết vào năm đầu (+181,2).
  Doanh thu FSO Q3 (59,7) vẫn ở mức giá cũ.
  Giả thuyết: đây là phần **chênh lệch giá hồi tố** theo biên bản 6/2025, chưa ghi nhận doanh thu vì phụ lục chưa ký. **Chưa kiểm được.**
  Tôi tính FSO theo đúng lịch cam kết, và nêu độ nhạy: nếu phần vượt mức hiện tại (177 tỷ) không thành tiền ⇒ **−1.319 đ/cp**.
- Tỷ trọng TC/chuyến/pool và ngày đáo hạn từng hợp đồng tàu dầu: **BCTC không có** (Bobby 6.A1–2, chưa kiểm được).

## 6. (E) Cổ phiếu, thanh khoản, sizing — **chỉ dùng nội bộ, KHÔNG đưa vào báo cáo nhà đầu tư**

- 103.702.452 cp, không đổi [Q3 p13]. Tự do chuyển nhượng khoảng 28%. ADV20 **33,1 tỷ**, ADV60 22,8 tỷ [BQ tới 28/10]. Cuối 2025 chỉ 1,3–2,2 tỷ/ngày.
- NAV thật 28/10 [`data/execution_logs/nav_history_*.csv`]: **SpaceX 0,967 tỷ**, **ZaloPay 0,920 tỷ**.
  Vị thế 2–4% NAV = **18–39 triệu** ≈ 1.000–2.100 cp, tức **≤0,12% ADV20**. Thanh khoản **không phải vấn đề**, kể cả khi ADV về mức 2025.
  (Verdict NON ⇒ không có sizing đề xuất; số trên chỉ để ghi nhận capacity.)

## 7. (F) Định giá — quan điểm NGOÀI khung §2.5 [out.txt §6]

| Giá | Vốn hoá | PE TTM (LNST 321,9) | PB | EV | EV/EBITDA 9T năm hoá | DY (1.000đ) |
|---|---|---|---|---|---|---|
| **18.750** (DNSE 14:29, sàn) | 1.944 | **6,04** | **0,93** | 928 | 1,24 | 5,3% |
| 20.150 (BQ 28/10) | 2.090 | 6,49 | 1,00 | 1.074 | 1,43 | 5,0% |

Lịch sử PVP từ 2018 [BQ]: PE p25/50/75 = 4,90 / 6,33 / 8,00; PB = 0,53 / 0,77 / 0,91. LNST bình quân 2023–25 = 196,5 tỷ; TTM = 1,64 lần mức nền.

| Phương pháp | xấu / cơ sở / tốt | Kỳ vọng (0,40/0,45/0,15) | Đọc |
|---|---|---|---|
| **PP-A** PE lịch sử × LNST 2027 + NPV mua đắt | 1.229 / 10.255 / 20.057 | **8.115** | Mức thị trường quen trả. Đánh giá thấp vì PE thấp áp lên cả phần LN từ lãi tiền gửi. **Không** dùng làm cận dải |
| **PB trung vị** 0,77 × BVPS | — | **15.545** | Neo trung tính |
| **PP-B SOTP** (kỳ vọng theo xác suất mua) | 15.701 / 24.428 / 34.095 | **22.387** | Cộng tài sản; nhạy với bội số đội tàu tự đặt |
| PP-B nếu **chắc chắn mua cả hai** | 12.821 / 23.468 / 34.095 | **20.803** | Khớp ước lượng của skeptic (~20.870) |

Thành phần PP-B (tỷ): tiền ròng sau cổ tức **1.016** + FSO PV **761** + đội tàu cũ (EBITDA 300/400/550 × 3,0/3,5/4,0) − dự phòng sửa chữa **233** − chi phí công ty **208**
− NPV mua đắt (kỳ vọng) **608 / 203 / 0**.
- **FSO PV 761 tỷ** = lịch cam kết (trừ Q3 đã thu), tính sau thuế (DT × 0,8 + lá chắn khấu hao), chiết khấu 10%/năm (ước lượng). **Giống nhau ở cả 3 kịch bản**; đã bỏ hệ số giá.
- **NPV mua đắt** = −30% / −10% / 0 áp cho **mỗi** dự án được mua, nhân xác suất mua ở bảng §4. Nếu mua cả hai: −906 / −302 / 0.
- **LNST 2027 (PP-A)** = 150 / 200 / 260 (ước lượng). Đã trừ khoảng 40 tỷ so với v1 cho phần doanh thu FSO giảm từ 7/2027.
- **Trọng số 0,40 / 0,45 / 0,15:** nhánh tốt = **K3 Bobby 0,15**. Phần 0,05 bớt ra chuyển sang nhánh xấu, vì Bobby cho CYCLICAL 0,55 và P(BDTI ≤3.500 ngày 30/09/27) = 0,58.

| Độ nhạy trọng số | PP-A | PP-B |
|---|---|---|
| v1 0,35/0,45/0,20 | 9.056 | 23.307 |
| **v2 0,40/0,45/0,15** | **8.115** | **22.387** |
| Nghiêm 0,45/0,40/0,15 | 7.664 | 21.951 |

**Sàn tài sản** (đội tàu cũ = 0; dải: cận dưới = 177 tỷ cam kết FSO năm 1 không thành tiền):

| | đ/cp |
|---|---|
| Trước capex: tiền ròng sau cổ tức + FSO PV − dự phòng sửa chữa | **13.568–14.887** |
| Tiền ròng sau cổ tức − VCSH dự định chi 916 tỷ (= 99,7 tỷ) | 961 |
| **Sau capex mua cả hai** (tàu mới chỉ đáng bằng nợ vay, VCSH bỏ vào coi = 0) + FSO PV − dự phòng | **4.731–6.050** |
| … trừ thêm tạm ứng cổ tức 2026 10% (KH, chưa chốt) | 5.050 |

Ở giá 18.750, thị trường đang định giá đội tàu cũ khoảng **609 tỷ**, thấp hơn sổ sách 838. Nếu cộng lại NPV mua đắt kỳ vọng cơ sở, con số là **~811 tỷ**.
Như vậy giá đã chiết khấu một phần rủi ro cước 2027, nhưng **sàn sau capex chỉ 4,7–6,1k**: nếu tiền bị tiêu vào tàu, phần bảo vệ bằng tiền mặt gần như biến mất.

**Kết luận định giá (ngoài §2.5):** dải tham khảo **15,5–22,4k (ước lượng)**, từ PB trung vị tới PP-B kỳ vọng. Giá 18.750 nằm trong dải và **không có biên an toàn**
so với cận dưới. Biên an toàn 15% dưới cận dưới 15.545 là **~13.200** (v1 viết ≤15.500 là sai số học).

**Phản ứng giá (không khẳng định nhân quả):** 25/09 tăng trần, đúng ngày GDKHQ dự ĐHĐCĐ bất thường. 08/10 đỉnh 25.000. 21/10 (sau CBTT Q3) giảm sàn 21.300
trong khi VNINDEX +2,8%. 23/10 CBTT gia hạn ĐHĐCĐ. 29/10 sàn 18.750, cùng phiên PVT giảm sàn. Giá đầu năm 13.240–14.660 [BQ].

## 8. Đối chiếu 20 mục DD của Bobby (§6)

| # | Trạng thái | Kết quả |
|---|---|---|
| 1 TC/chuyến/pool | ❌ | Không có trong BCTC. Biên vận tải dao động 24–40% theo quý ⇒ nhạy cước cao; có phải trả Aframax Pool |
| 2 Lịch đáo hạn TC | ❌ | Không có. Apollo 70k USD/ngày chỉ từ [web] |
| 3 Khách cùng hệ thống | ✅ | 63,3% DT 6T là bên liên quan; vận tải có BSR 199,5 tỷ 6T |
| 4 Nội địa vs quốc tế | ✅ | Vận tải 100% quốc tế [H1 p30] |
| 5 Bảng đội tàu / tuổi | ⚠️ | 4 tài sản có NBV [Q3 p10]; tuổi chỉ từ [web] |
| 6 Lịch dry-dock | ⚠️ | TT99 ngừng trích; dự phòng 232,9 chuyển hết sang ngắn hạn |
| 7 Mua tàu ở đỉnh | ⚠️ **rủi ro chính** | 116 tr USD đã duyệt; mô hình công ty NPV ≈ 0 ở TC 30.240; chưa ký; ĐHĐCĐ bất thường ≤30/11 |
| 8 Lãi thanh lý | ✅ | 0. Apollo hết khấu hao ⇒ quyền chọn lãi bán (chưa có tin) |
| 9 Khấu hao | ⚠️ | Apollo hết khấu hao giữa 2025 (−35,7 KH 9T); Era/Pride còn khoảng 4,7–5,0 năm |
| 10 Tàu già | ❌ | Apollo ~21 tuổi [web] |
| 11 Nợ theo đồng tiền | ✅ | Toàn VND |
| 12 Tỷ giá | ✅ | Ròng Q3 khoảng −4,5 tỷ |
| 13 Lãi vay/EBITDA | ✅ | 5,6% |
| 14 Dùng LN đỉnh | ⚠️ | Cổ tức 10% + KH tạm ứng 10%; **định tiêu 916 tỷ VCSH cho tàu** |
| 15 Nhiên liệu | ⚠️ | Q3 77,1 (gấp 2,7 lần Q3/25) ⇒ có chạy chuyến (suy luận) |
| 16–17 Off-hire / trừng phạt | ❌ | Không nêu |
| 18 Cabotage | — | Không áp dụng |
| 19 FSO | ⚠️ | Cam kết đến 2036 theo giá mới: **dòng tiền giảm** từ 7/2027 (§5) |
| 20 TA lọc dầu 2027 | ❌ | Gián tiếp qua BSR |

## 9. §2 / §2.5 — áp dụng cái nào ⇒ **NON**

- **§2 (scandal cá nhân): không áp dụng.** Không có khởi tố hay điều tra.
- **§2.5 (chu kỳ ngành):** #1 chu kỳ ✅. #2 sống sót ✅ (kể cả sau capex ND/VCSH ~0,95, vay VND dài). #3 dẫn đầu chi phí ⚠️ (không kiểm được).
  #4 sàn tài sản ⚠️: trước capex PB 0,93 với ~48% là tiền ròng; nhưng **sau capex sàn chỉ còn 4,7–6,1k** = 0,25–0,32 lần giá.
  **"Đáy chưa tới" ❌:** đây là **ĐỈNH** LN (Bobby: cuối đỉnh; F1/F2 dự báo BDTI giảm 41–61% tới 2027). Giá giảm −25% từ đỉnh, chưa tới ngưỡng T1 >35%.
- ⇒ **NON / không-phải-case-§2.5.** Một ❌ là loại; v1 gán AMBIGUOUS là sai nhãn (skeptic REFUTED).

## 10. Pháp lý / quản trị — WARNING (luật 27/09: phân tích bình thường, chỉ cảnh báo)

- ⚠️ **Thay GĐ 23/06/2026**, cùng ngày ĐHĐCĐ duyệt dự án tàu: Hoàng Đức Chính → **Phan Công**. PGĐ Vũ Ngọc Khôi miễn nhiệm 12/08.
  **Vũ Thanh Tùng** được bổ nhiệm PGĐ 03/09 [CB]. Không thấy liên quan khởi tố. Rủi ro: ban điều hành mới quyết capex 1,55 lần vốn hoá đúng đỉnh.
- ⚠️ **ĐHĐCĐ bất thường gia hạn 2 lần** (02/10 → ≤15/11; 23/10 → ≤30/11), đều "hoàn thiện văn kiện". Đây là mốc then chốt.
- Phải thu khó đòi cũ Huỳnh Thị Huyền Như 73,07 tỷ đã dự phòng 100% [Q3 p9]. Soát xét H1 chấp nhận toàn phần ✅. BCTC năm 2025 kiểm toán: không có trong tay.
- Giao dịch bên liên quan không có trần giá trị ⇒ không kiểm được giá chuyển nhượng.

## 11. Trigger đổi verdict / chạy lại DD — mỗi dòng gắn verdict đích

| Mốc | Cần thấy | Verdict đích |
|---|---|---|
| **ĐHĐCĐ bất thường (≤30/11/2026)** | Văn kiện: giá/tuổi tàu #2/#3, có phát hành cổ phiếu không | **Hoãn/huỷ cả hai dự án** ⇒ sàn quay về 13,6–14,9k: **NON giữ**, cập nhật định giá. **Mua ≥56,5 tr USD tàu 10–15 tuổi** ⇒ **NON giữ**, NPV −30% thành kịch bản chính. **Có phát hành pha loãng** ⇒ **NON giữ**, hạ định giá |
| Phụ lục FSO ký | Giá + lịch thu, giải thích được mục 415,8 | **NON giữ**. Nếu 177 tỷ hồi tố không thành tiền ⇒ −1,3k/cp |
| BCTC Q4/2026 + năm 2026 kiểm toán (~20/01–03/2027) | LN gộp vận tải Q4 so với 70,4; chi phí lên đà dùng dự phòng 232,9 | **NON giữ**. Q4 < 50 tỷ ⇒ ghi nhận chu kỳ đang xuống (chưa phải đáy) |
| **CHU KỲ ĐÁY — điều kiện chạy lại §2.5** | **≥1 tín hiệu đáy**: (a) LNST 4 quý ≤ ~200 tỷ (về mức nền 2023–25), (b) Bobby F2: **BDTI ≤3.500 ngày 30/09/2027**, (c) PB ≲ 0,75 **chỉ tính khi đi kèm (a) hoặc (b)** | **Chạy lại DD §2.5** (có thể ra QUALIFY/AMBIGUOUS/NON). Kèm điều kiện: biết rõ tiền đã/không bị tiêu vào tàu |
| Bobby F1 31/03/2027 | Aframax TCE < 150k nhưng LN gộp vận tải ≥ 60 tỷ/quý | **NON giữ**; dấu hiệu có TC khoá giá ⇒ nâng nhánh cơ sở khi chạy lại |
| **Chỉ có giá** ≤ ~13.200 (15% dưới cận 15,5k) mà **không** có tín hiệu đáy | | **Xem lại định giá ngoài §2.5** (không chạy §2.5 ⇒ không gán AMBIGUOUS) |
| Giá > 22.400 không có tin mới | | NON giữ; đắt so với SOTP kỳ vọng |

## 12. Phần tôi CHƯA CHẮC (cho fundamental-skeptic tấn công)

1. **Mục FSO "≤1 năm 415,8":** không hoà giải được với doanh thu ~239/năm. Giả thuyết hồi tố chưa kiểm. Độ nhạy −1.319 đ/cp. Tôi cũng chưa rõ năm 1 có tính lũy kế các kỳ đã đến hạn mà chưa thu hay không.
2. **Xác suất mua 0,50 / 0,35 / 0,15** là tự đặt, chỉ neo vào việc đã duyệt và việc đã gia hạn (v2.1 bỏ hạn VAT). Văn kiện ĐHĐCĐ bất thường sẽ thay các số này.
3. **Giá trị FSO** dùng suất chiết khấu 10% tự đặt; khấu hao FSO giả định đều 148/năm. v2.1 độ nhạy: r=8% **792,5** / 10% **760,7** / 12% **731,8** tỷ (+307 / −278 đ/cp).
4. **Gán phần chênh khấu hao 35,7 cho Apollo** và **17,7/quý trích sửa chữa vào giá vốn vận tải Q3/25** đều là suy luận (BCTC không tách).
5. PP-B vẫn nhạy với bội số × EBITDA đội tàu: ±0,5 lần × 400 = ±1.930 đ/cp. Bội số và EBITDA chuẩn hoá đều là ước lượng tự đặt.
6. Không có dữ liệu hợp đồng thuê tàu dầu. Tuổi tàu và Apollo 70k USD/ngày chỉ từ [web].
7. Room ngoại: **chưa kiểm**.
8. Lãi bán Apollo ở đỉnh (quyền chọn có lợi) chưa định giá; thuế khi bán chưa tính.
9. Q3 doanh thu từ PVTrans 951,5: giả định là lũy kế 9T.

## 13. Nguồn

- **NQ + biên bản ĐHĐCĐ thường niên 2026 (gốc)**: https://pacificshipping.vn/assets/tenant/uploads/media-uploader/pacific/nghi-quyet-va-bien-ban-hop-dhdcd-thuong-nien-nam-20261782396900.pdf → `src/agm2026_nq_bienban.pdf`
  (Phụ lục 04 KH p21, Phụ lục 05 cổ tức p22, Phụ lục 11 + báo cáo khả thi Aframax p37–45)
- CBTT gốc pacificshipping.vn/tin-co-dong: NQ 17 (28/08, cổ tức), QĐ 20 (03/09, PGĐ), NQ 22 (02/10, gia hạn), NQ 16 (18/08, GD bên liên quan), NQ 23 (23/10, gia hạn)
- [web] ĐHĐCĐ bất thường, Aframax #3: https://doanhnhan.baophapluat.vn/van-tai-dau-khi-thai-binh-duong-pvp-trieu-tap-dhdcd-bat-thuong-muon-mua-them-tau-aframax-thu-3.html (12/09/2026)
- [web] Apollo 70k USD/ngày: https://elibook.vn/2026/05/25/pvt-gia-cuoc-thue-tau-dau-tho-aframax-van-neo-cao-trong-quy-2-tau-apollo-tai-ky-hop-dong-70000-dola-ngay-gap-doi-gia-thue-cu/
- [web] VIS Rating A: https://cafef.vn/pvtrans-pacific-lan-dau-duoc-xep-hang-a-trien-vong-on-dinh-boi-vis-rating-18826061617063305.chn
- [web] Đội tàu: https://tapchicongthuong.vn/pv-trans-pacific--pvp--du-chi-112-trieu-usd-de--tre-hoa--doi-tau-139280.htm

## 14. Lịch sử phiên bản: v1 AMBIGUOUS → v2 NON

v1 (`REPORT_v1_ambiguous.md`, `calc_v1.py`, `out_v1.txt`, job `Taylor_20261029_065413`) bị fundamental-skeptic **REFUTED phần nhãn**.
Số nền của v1 khớp trang BCTC. v2 sửa như sau:

| Hạng mục | v1 | v2 | Sửa vì |
|---|---|---|---|
| **Verdict** | AMBIGUOUS | **NON / không-phải-case-§2.5** | §9 có ❌ "đáy chưa tới" ⇒ loại |
| FV kỳ vọng SOTP (PP-B) | 23.107 | **22.387** (xác suất mua) / 20.803 (chắc mua cả hai) | Thêm NPV mua đắt cho dự án #2 (59,5 tr USD); FSO theo lịch; trọng số tốt 0,15 |
| PP-A kỳ vọng | 12.235 | 8.115 | Dự án #2 + LNST 2027 trừ phần FSO giảm + trọng số |
| Dải định giá | 15,5–23k | 15,5–22,4k (ngoài §2.5) | |
| Sàn tài sản | 12.768 (tiền còn nguyên) | **14.887 trước capex / 6.050 sau capex** | FSO PV mới cao hơn; thêm sàn sau khi chi 916 tỷ VCSH |
| FSO | ×0,70 PV × hệ số giá 0,70/0,90/1,0; "có thể gồm tàu khác"; "+148 tỷ/năm từ 2029" | Lịch cam kết RIÊNG FSO, giá mới; PV 761; dòng tiền giảm ~239 → 136 → 37/năm | Đọc lại H1 p34: trùng đếm + đọc sai |
| Tăng trưởng LNTT cùng cơ sở | +52% | **+23% … +34%** | Thêm khấu hao Apollo |
| Q3 LN gộp vận tải YoY | +12,6% | **−12% cùng cơ sở** (suy luận) | Trừ trích sửa chữa Q3/25 |
| KH 2026 | báo chí, "chưa có gốc" | **NQ ĐHĐCĐ gốc** 2.700/270/216, cổ tức 10% | Tìm được NQ |
| "Báo chí chia nhầm 77,6%" | khẳng định | Gần nhất với LNST/KH LNTT (77,7%), không tái lập đúng | |
| Trigger chạy lại | Giá ≤ ~15.500 | Tín hiệu **chu kỳ đáy** (LN ≤200 / BDTI ≤3.500 @30/09/27 / PB ≲0,75); giá ≤13.200 một mình ⇒ chỉ AMBIGUOUS | Số học sai; thiếu điều kiện chu kỳ |
| Sizing | NAV 50–100 tỷ | NAV thật 0,967 / 0,920 tỷ, chỉ dùng nội bộ | |
| Điểm yếu Q1 lệch 0,78 | chưa giải | Đóng: điều chỉnh soát xét 209,73 → 210,51 | |
| Mục chưa đọc | NQ 02/10, PGĐ 04/09, cổ tức 28/08 | Đã đọc: hạn ≤15/11; PGĐ Vũ Thanh Tùng; cổ tức chi 20/10 = 103,70 tỷ | |
| Giá | DNSE 13:58 | DNSE 14:29:04 = 18.750 (sàn) | |
| **v2.1** (phản biện vòng 2 CONFIRMED + 7 sửa nhỏ) | — | (a) trigger PB≲0,75 chỉ kèm (a)/(b); dòng 'chỉ giá ≤13.200' → xem lại định giá ngoài §2.5 · (b) sàn dải 13,6–14,9k / 4,7–6,1k · (c) bỏ lý do VAT · (d) NPV CSH +2.237.928 USD, IRRmin 11%, IRR 7,67% cấp dự án · (e) LCTT 03 chung, gán sửa chữa = suy luận · (f) cổ tức: lịch 20/10 theo NQ 17, 109,5 gồm ~5,8 tồn cũ · (g) FSO PV r=8/10/12% 792,5/760,7/731,8 | calc.py 0 FAIL / 29 |
