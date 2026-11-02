# TV1 (EVNPECC1) — Giá trị nội tại dựng MÙ với giá thị trường (giai đoạn 1)

Job `Taylor_20261102_144349` · 02/11/2026 · tái lập: `python3 -I valuation_blind.py > valuation_blind_out.txt`
(mọi số dưới đây lấy từ `valuation_blind_out.txt`). Nhãn: [UL] = giả định tự đặt, kèm căn cứ; [nguồn] = số đọc được.
File không chứa giá cổ phiếu, vốn hoá hay P/E, P/B, lợi suất cổ tức của TV1.

## 0. Kết quả (khoá trước khi so giá)

| | đ/cp |
|---|---|
| **Tâm = kỳ vọng xác suất** (4 kịch bản giá PPA × 3 kịch bản đường ống tư vấn; Q 195 GWh; Ke 12,85%) | **27.800** |
| Ô trung vị (giá PPA 520 × tư vấn giữa) | 25.100 |
| **Dải chính, P20–P80 của lưới có trọng số** | **22.100 – 35.100** |
| Toàn lưới 12 ô | 16.200 – 50.000 |
| Giá trị tiếp cận qua cổ tức (payout 27% thực tế FY2025 / 40%) | 26.400 / 27.200 |

Cấu phần của tâm: thuỷ điện **16.400** + tư vấn **12.300** + tiền ròng điều chỉnh **−900**.
Tâm **không** chứa xác suất rủi ro vụ án; độ nhạy vụ án nằm riêng ở §D.

Phân bố lệch phải: kỳ vọng (27.800) cao hơn trung vị (25.100) vì kịch bản "giữ giá hợp đồng 949 đ/kWh" (P = 0,15) cho 35.100–50.000.

**Độ nhạy chính của tâm:**

| Biến | Giá trị thử → tâm (đ/cp) |
|---|---|
| Ke | 10%: 38.600 · 12,3%: 29.300 · 13,4%: 26.400 · 14%: 25.100 |
| Quỹ KTPL | 10%: 31.500 · 15%: 29.700 · 25%: 25.900 |
| Sản lượng | Q175: 25.500 · Q215: 30.000 · Q236,6: 32.500 |
| Giá PPA (tư vấn giữa, Q195) | 340: 18.200 · 440: 22.100 · 520: 25.100 · 600: 28.000 · 750: 33.600 · 949: 41.000 |

## 0b. Khai báo giao thức mù — trung thực, mức nhiễm

- **Không** truy vấn giá, vốn hoá hay bội số TV1 (DNSE/BQ) trước khi khoá. **Không** đọc REPORT §0/§8,
  investor_report/, SKEPTIC*, dd_price_zones.json, kb/projects/tv1-*, dgc-tv1-*, bus tv1-dd-*.
- **NHIỄM, không tránh được (phải khai):**
  1. Working memory của Taylor được bơm tự động vào đầu phiên. Nó có các dòng tóm tắt vòng r4–r8, gồm một mức giá đóng
     cửa gần đây và các vùng giá trị cũ. Tôi đã thấy các dòng này trước khi làm.
  2. `tv1_sb5_ppa_price_20261013/README.md` §4–§5 (bảng SOTP đ/cp cũ và bảng vị thế có giá vốn) lọt qua bộ lọc grep.
  3. `valuation.py` dòng 5 (hằng số giá) hiện ra khi đọc phần đầu file để lấy số cổ phiếu.
  - **Cách giảm thiểu:** mọi giả định được dựng từ BCTC, quy định, định mức và đường ống, đều có căn cứ ghi trong script.
    Không có tham số nào được hiệu chỉnh ngược về một mức giá. Kết quả cao hơn rõ các vùng cũ: bằng chứng là kết quả
    không bị kéo về giá, nhưng **không chứng minh** quy trình sạch hoàn toàn. Phản biện nên soi những giả định xác suất [UL].

## A. Thuỷ điện Sông Bung 5

**Hiệu chuẩn 2025** [FY25 tr.34; BCTN25 tr.7, 24]:
- Doanh thu 261,6 tỷ, gồm thuế tài nguyên và DVMTR **37,2** (khoản EVN trả thêm, chuyển thẳng đi).
- Giá ròng **949 đ/kWh**.
- O&M tiền mặt **21,2 tỷ** (90 đ/kWh); khấu hao 38,1.

### A1. Giá PPA sau mốc tái ký — HÀNH LANG từ kinh tế và quy định

**(i) Sự thật hợp đồng**
- Dự thảo HĐ sửa đổi 05 (2018: EVN NQ 286/NQ-HĐTV, Cục ĐTĐL 1374/ĐTĐL-GP) ghi:
  - giá cố định bình quân 569,36;
  - 2019–21 ở mức 569,36;
  - **từ 01/01/2022 ở mức 243,66** (chưa gồm O&M, thuế và phí) [PA2018 tr.13].
- **Thực tế không hạ:** giá ròng 2014–17 là 938,78–940,76; giá 2022–25 gồm thuế và phí là 1.052–1.148, ròng ≈949.
  ⇒ Phụ lục 05 hoặc không ký như dự thảo, hoặc điều kiện kích hoạt khác. **Điều kiện kích hoạt: CHƯA XÁC ĐỊNH.**
  Không tìm được thuyết minh BCTC, CBTT hay tài liệu ĐHĐCĐ 2026 nào nêu biểu giá. Bài ĐHCĐ 30/04/2026 cũng không nhắc giá điện.
- Bằng chứng một bậc giảm SẼ đến:
  - BCTN 2025 tr.38, lời chính công ty: "…khi giá điện của nhà máy TĐ Sông Bung 5 sụt giảm".
  - Lời lãnh đạo qua KBSV 17/04/2026: từ 2027, ở mức 500–600 (**chưa kiểm bản gốc**).

**(ii) Khuôn pháp lý** (LEGAL_PPA)
- IRR ≤ 12% là **trần** trên toàn đời 40 năm.
- EVN không được đơn phương hạ giá; ngược lại, bậc thấp đã ký thì chủ đầu tư phải chấp nhận.
- Đ.14 TT 12/2025 (hợp đồng hết hạn): bù giá trị còn lại + chi phí SXKD + lợi nhuận hợp lý.
- Khung giá thuỷ điện 2026 là 0–1.110 đ/kWh (không ràng buộc ở 949).

**(iii) IRR dự án dựng lại** (TMĐT 1.372 tỷ; sản lượng và giá thực 2013–2026; O&M thực; thuế 20%)
- Phát hiện chính:
  - IRR luỹ kế đến 2026 chỉ **2,8%** (chưa tính giá trị còn lại).
  - IRR **toàn đời** 2013–2052 ở giá 949 là **7,7%** (8,0% nếu 2019–20 không khô như suy ra).
  - Ở giá 600 là 6,3%; ở giá 400 là 5,2%.
  - Giá cần để IRR toàn đời chạm 12% vượt 3.000 đ/kWh.
- ⇒ **Trần IRR 12% KHÔNG phải căn cứ để hạ giá.** Nhà máy thực tế sinh lời dưới mức quy định cho phép, do sản lượng thực
  (BQ 2013–23 là 175,3) thấp hơn thiết kế (208,85–230). Nếu có hạ, nguồn duy nhất là **bậc giá đã ghi trong hợp đồng**
  (cơ chế giá từng năm dồn lên kỳ trả nợ), không phải quy định.
- Lá bài đàm phán của chủ sở hữu là thật: Luật Điện lực 61/2024 Đ.52.1(d) và Đ.14 TT 12.

**(iii-b) Giá sàn để chủ sở hữu còn vận hành**
- Công thức: O&M + sửa chữa lớn + thu hồi và lợi nhuận trên giá trị còn lại (RAB ~449 tỷ, còn 26 năm).
- Kết quả: **398 (8%) / 437 (10%) / 477 (12%) / 540 (15%) đ/kWh** ở Q195; ở Q175 là 444–602.
- Hoà vốn tiền mặt 140; hoà vốn kế toán 309.
- Đối chiếu dự thảo 2018: 243,66 + O&M 95 = **338**, thấp hơn hoà vốn kế toán. Nếu O&M theo định mức TT 12
  (2% TMĐT) thì **415**, tức sát sàn kinh tế.
- ⇒ Mức 340 không làm kịch bản, chỉ để trong độ nhạy (18.200 đ/cp).

**(iv) Tiền lệ và thị trường điện**
- Vĩnh Sơn 333 / Sông Hinh 462 đ/kWh: nhà máy cũ đã khấu hao hết. Không cùng loại (SB5 còn RAB 449 tỷ).
- BSA kế hoạch 2026 ngầm khoảng 752 đ/kWh (không giải thích).
- Sông Bung 4A bị hạ về trần khung 1.110 sau thanh tra.
- Phần Qc so với giá thị trường điện (SMP+CAN): **chưa kiểm** SB5 có tham gia trực tiếp không. Không mô hình riêng.

**Kịch bản giá ròng 2027+** (xác suất [UL]; kỳ vọng 592 đ/kWh):

| Kịch bản | Giá | P | Căn cứ |
|---|---|---|---|
| P1 giữ hợp đồng | 949 | 0,15 | Mốc 2022 đã qua mà không hạ; EVN không được hạ đơn phương; IRR thấp. Nhưng công ty tự viết "sụt giảm" |
| P2 thoả thuận | 600 | 0,30 | Đầu trên lời lãnh đạo; ≈ sàn kinh tế ở lợi nhuận 15% trên RAB |
| P3 thoả thuận | 520 | 0,35 | Giữa lời lãnh đạo; ≈ sàn kinh tế ở 12–15% |
| P4 sàn kinh tế | 440 | 0,20 | Lợi nhuận ~10% trên RAB; ≈ bậc 2018 + O&M theo TT 12 (415) |

- **Sản lượng P50 = 195 GWh** [UL]: giữa BQ 2013–23 (175, có 2 năm rất khô) và BQ 2021–25 (215). Độ nhạy 175–236,6.

### A2. DCF thuỷ điện 2027 – 08/2059

- Dòng tiền: LNST × (1 − KTPL 20%) + khấu hao − capex duy trì.
- Giả định: O&M trượt 2,5%/năm; chi phí chung phân bổ 8; khấu hao 38 đến 2039; thuế 20%; quy ước giữa năm.
- Sau 2052 (hết đời kinh tế), giá theo Đ.13 (chi phí + lợi nhuận hợp lý) ⇒ giữ mức kịch bản [UL].
- Giá trị **sau 2059 = 0**.

| Kịch bản | LNST 2028 (Q195) | Giá trị Q195 (Ke 12,85%) | Q175 | Q236,6 |
|---|---|---|---|---|
| P1 949 | 92,6 | 790 | 694 | 991 |
| P2 600 | 38,2 | 444 | 383 | 571 |
| P3 520 | 25,7 | 365 | 312 | 475 |
| P4 440 | 13,2 | 286 | 241 | 379 |

- Kỳ vọng: **437 tỷ = 16.400 đ/cp**.
- Mỗi năm hạ bậc trễ thêm cộng **1.500–1.850 đ/cp**.
- Đối chiếu tài sản:
  - AASC 2018 thẩm định 1.686 tỷ ở Ke 7%;
  - 6 lần đấu giá 2019–21 (khởi điểm 1.688 → 1.351,7 tỷ) đều không có người đăng ký.
  ⇒ Người mua đã chiết khấu bậc giá. Giá trị 286–790 tỷ ở đây nhất quán với việc không ai mua ở ≥1.352 tỷ.

### A3. Điện mặt trời nổi 46 MWp + 5 MW BESS (~800 tỷ, ~90 tỷ doanh thu/năm) — KHÔNG TÍNH

- IRR dự án ≈ **6,8%**, thấp hơn Ke ⇒ NPV ≈ **−296 tỷ** ở mức vốn đầu tư công bố.
- Dự án chưa vào quy hoạch TP Đà Nẵng mới (ĐHCĐ 30/04/2026) và chưa có cơ chế giá.
- **Điều kiện kích hoạt giá trị dương:** vốn đầu tư ≲ 504 tỷ. Giá tấm pin 7 → 3 tỷ/MWp (lời chủ tịch 06/2025) làm điều
  này khả dĩ. Hoặc có cơ chế giá cao hơn khoảng 90 tỷ/năm.

## B. Tư vấn KS-TK điện — dựng từ đường ống

**Số thật** [FY25 tr.34-35, bq_fin 4 quý, Q3]:

| Năm | Doanh thu tư vấn | Biên gộp | EBIT sau chi phí chung |
|---|---|---|---|
| 2023 | 318,7 | — | — |
| 2024 | 346,2 | 24,8% | 5,4% |
| 2025 | 447,0 | 18,1% | 10,0% |
| 9T/26 | 324,5 (**+29%**) | 28,4% (lõi) | **11–17%** (A/B, tuỳ cách đọc khoản hoàn nhập Q3) |

- **Hợp đồng ký mới 2025 là 835,1 tỷ**, cao nhất lịch sử [baodauthau post192515]. Bằng 1,87× doanh thu tư vấn 2025.
- Người mua trả trước +33% (104,4 → 138,7).
- Kế hoạch 2026 cho mảng tư vấn ≈ 454,5 tỷ (641,5 − 187), công ty tự nói "thận trọng, chỉ tính HĐ hiện có".

**Tỷ lệ phí theo định mức** [TT 38/2026 PL VIII, đọc bảng gốc]. Công trình công nghiệp (năng lượng) cấp I:
- Thiết kế kỹ thuật 1,28% / 1,09% chi phí xây dựng ở mức 1.000 / 2.000 tỷ; bản vẽ thi công = 60% thiết kế kỹ thuật
  ⇒ thiết kế 2 bước ≈ 1,7–2,0% chi phí xây dựng.
- Báo cáo khả thi (FS) 0,40–0,25%; giám sát thi công 0,82–0,64%.
- **Kiểm bằng gói thật:** 500kV Krông Buk–Tây Ninh 1 (KS+TKKT+BVTC) = 158,84 / 14.060 = **1,13% TMĐT**;
  Thốt Nốt–Đức Hòa = 1,12%.
- ⇒ Tỷ lệ phí hiệu dụng f = **1,6% TMĐT** [UL] (KS-TK-FS 1,2% + giám sát/khác 0,4%).

**Thị phần hiệu dụng**
- Capex EVN 2025 là 125.778 tỷ ⇒ bể phí ≈ 2.012 tỷ ⇒ **thị phần TV1 ≈ 22%**.
- Đây là thị trường oligopoly gốc EVN (PECC1–5). Mỗi gói 500kV có 1–2 nhà thầu, giảm giá 1–5% [BOBBY §3].

**Vai trò đặc thù**
- TV1 là đơn vị thiết kế phía Bắc của nhóm EVN (EVN 54,34%). Khách hàng chính:
  - BQLDA điện miền Bắc: 115 gói, 533 tỷ;
  - BQLDA miền Trung: 426 tỷ;
  - EVNNPT: 273 tỷ (tổng 650 gói, 4.023 tỷ kể từ 2017, vietnamfinance 11/2025).
- Hợp đồng gần đây: tư vấn Tuyên Quang mở rộng **81,7 tỷ / 62 tháng**. TV1 là bên duy nhất dự thầu và cũng là bên thiết kế
  nhà máy gốc.
- Nguồn việc nêu tại ĐHCĐ 2026: Sơn La MR 800 MW, Lai Châu MR 800 MW, Tuyên Quang MR, Sông Ba Hạ, An Vương, Quảng Trị;
  500kV AC/HVDC; **lập lại FS Ninh Thuận 1** cùng PECC2 và Viện Năng lượng; ĐGNK cùng PTSC.
  Vai trò của TV1 ở từng dự án ngoài Tuyên Quang **chưa xác nhận**.
- Thiếu điện miền Bắc 5.680 MW năm 2027 (BCT 15/09/2026) rơi đúng địa bàn của TV1.

**Đường ống EVN 2026–2030**
- Hai nguồn mâu thuẫn: ~830.000 tỷ (vietnamplus, BQ 166k/năm) và ~5 tỷ USD/năm (bản tin EVN 12/2026, ~130k).
- Kế hoạch 2026 là 123k; H1 giải ngân 36%; 500kV mới khởi công 2/28 (BOBBY).
- Bobby xếp loại: **STRUCTURAL_UPCYCLE về khối lượng, ADMIN_GATED về nhịp**.

**Kịch bản** (doanh thu 2026E 520 [UL: 9T + Q4 bằng Q4/25]; ΔVLĐ = 40% × Δdoanh thu; capex 5; g dài hạn 5% ≤ GDP danh
nghĩa; KTPL 20%; Ke 12,85%):

| Kịch bản (P) | Tăng doanh thu 27–30 | Biên EBIT | LNST 2027 / 2030 / 2032 | Giá trị | đ/cp |
|---|---|---|---|---|---|
| Thấp (0,30) | 3%/năm | 8% | 34,2 / 37,4 / 40,5 | 170 | 6.400 |
| Giữa (0,50) | 8%/năm | 11% | 49,4 / 62,2 / 70,5 | 328 | 12.300 |
| Cao (0,20) | 14%/năm | 14% | 66,3 / 98,3 / 117,8 | 569 | 21.300 |

Căn cứ từng kịch bản:
- **Thấp:** capex EVN đi ngang (Bobby F1 P=0,55); biên ≈ bình quân 2024–25.
- **Giữa:** EVN đạt ~70% kế hoạch 830k, cộng trượt giá xây dựng và dịch cơ cấu sang thuỷ điện mở rộng/500kV.
  Doanh thu năm 2027 cũng đã có backlog đỡ (book-to-bill 1,87).
- **Cao:** đạt đủ kế hoạch, cộng NT1 và HVDC, cộng đòn bẩy chi phí chung (biên 9T/26 trường hợp B).

Ghi chú mô hình:
- Kỳ vọng tư vấn **329 tỷ = 12.300 đ/cp**. Terminal chiếm 58–77% giá trị.
- RONIC sau KTPL ≫ Ke, vì mảng này ít tài sản, chỉ cần vốn lưu động.
- Ke × g (kịch bản giữa): Ke 10% → 446–725; Ke 14% → 268–305.

## C. Tiền và bảng cân đối 30/09/2026

| Khoản | tỷ đồng |
|---|---|
| Tiền + tiền gửi HTM | 198,6 |
| Vay (118,8 là cá nhân/bên liên quan) | −129,9 |
| Cổ tức phải trả (chi 29/10) | −43,2 |
| Lãi vay cá nhân phải trả | −64,3 |
| **Tiền ròng thô** | **−38,7** |
| KTPL trích từ LNST 9T/26 (rò rỉ thật, tiền đã nằm trong số dư) | −24,9 |
| LNST Q4/26 sau KTPL [UL] | +40 |
| **Tiền ròng điều chỉnh** | **−23,7 tỷ = −900 đ/cp** |

- Nợ tranh chấp Long + Ngãi 127,63 tỷ (gốc + lãi) **đã nằm trong sổ** ⇒ khấu trừ đủ theo sổ. Vụ Ngãi đã thua phúc thẩm.
  Không cộng lại phần có thể thắng.
- KTPL tính đúng ở dòng tiền cổ đông, tức × (1 − 20%) trên mọi LNST, không phải chiết khấu bội số.
- **Giới hạn:** chưa tách được số dư quỹ KTPL chưa chi. Nếu còn nguyên 30,1 thì −1.130 đ/cp.
- Các cờ chất lượng báo cáo (hoàn nhập dự phòng Q3, lệch thuyết minh so với BCTC kiểm toán) được giữ ở REPORT §3–§5.
  Không điều chỉnh vào giá trị, vì tư vấn được dựng trên biên **lõi**.

## D. Vụ án EVNNPT/PC1 — chỉ là WARNING + độ nhạy (không vào tâm)

- **Bằng chứng hiện có:**
  - Chủ tịch HĐQT và phó phòng TCKT bị khởi tố (07/05/2026);
  - TV1 có tên trong "13 công ty liên quan" (VnExpress 02/07);
  - chưa có kết luận hay cáo trạng; KQKD 9T/26 chưa cho thấy tác động (doanh thu tư vấn +29%);
  - pháp nhân không thể bị truy cứu 5 tội danh này theo Đ.76 BLHS hiện hành.
- **Bằng chứng sẽ xác nhận:** kết luận điều tra hoặc cáo trạng nêu pháp nhân; quyết định cấm thầu theo NĐ 214/2025 Đ.133;
  trích lập hoặc thuyết minh tại BCTC kiểm toán FY2026.

| Cú sốc | Δ đ/cp |
|---|---|
| Cấm thầu EVN 3 năm, doanh thu tư vấn −50% 2027–29 | −8.600 |
| Cấm 5 năm, −50% | −13.700 |
| Cấm 3 năm, −70% | −12.100 |
| Buộc nộp lợi bất chính 20 / 50 / 100 tỷ | −660 / −1.660 / −3.320 |

## E. Điều thị trường CÓ THỂ CHƯA TÍNH — và có thể ĐÃ TÍNH QUÁ TAY

**Có thể chưa tính:**

1. **Không có căn cứ quy định để cắt sâu giá PPA.** IRR toàn đời thực ≈ 7,7–8% < trần 12%. Sàn kinh tế (lợi nhuận hợp lý
   trên giá trị còn lại) là **440–540 đ/kWh**, không phải 340. Mỗi năm hạ bậc trễ là +1.500–1.850 đ/cp.
   *Kiểm:* giá ròng/kWh Q4/2026 và năm 2027; CBTT về phụ lục PPA; biên bản ĐHĐCĐ 2027.
2. **Backlog đã khoá doanh thu tư vấn 2026–27.** Hợp đồng ký mới 2025 là 835 tỷ (1,87× doanh thu), trả trước +33%,
   doanh thu 9T +29%, trong khi kế hoạch công ty 2026 chỉ 454,5 tỷ ("thận trọng").
   *Kiểm:* doanh thu tư vấn FY2026 ≥ 500 tỷ (BCTC kiểm toán ~03/2027).
3. **Đòn bẩy hoạt động:** EBIT tư vấn tăng từ 5% (2024) lên 10% (2025) và 11–17% (9T/26) nhờ chi phí chung cố định.
   *Kiểm:* biên EBIT tư vấn FY2026 ≥ 11% sau khi bỏ hoàn nhập.
4. **Vị thế "thiết kế gốc" ở các nhà máy thuỷ điện mở rộng miền Bắc** (Tuyên Quang MR đã ký 81,7 tỷ, là bên duy nhất dự thầu)
   trong bối cảnh thiếu điện miền Bắc 2027. Lợi thế ở đây là tài liệu gốc và chuyên môn hiếm, không phải giá thầu.
   *Kiểm:* gói tư vấn Sơn La/Lai Châu MR trao cho TV1 (muasamcong).
5. **Thiết kế lại là nguồn việc:** mỗi lần đổi kế hoạch (PDP8 sửa lần 2, LNG sang than, tách dự án NT1) đều sinh thêm
   việc FS/thiết kế cho đơn vị đang nắm hồ sơ (Bobby §2).

**Có thể đã tính quá tay (hoặc mình có thể sai):**

1. Bậc giá là thật: chính công ty viết "sụt giảm". Nếu hợp đồng sửa đổi đã ký đúng 243,66 thì giá trị còn 18.200
   (tư vấn giữa).
2. Điện mặt trời nổi có NPV âm ở mức vốn công bố. Ai tính nó như một động lực là tính quá tay.
3. Quỹ KTPL 20% LNST chảy ra người lao động. Payout 27% giữ tiền ở lãi tiền gửi (rò rỉ ~1.400 đ/cp).
4. Tư vấn chịu ADMIN_GATED: 500kV mới khởi công 2/28. Capex EVN 2026 đi ngang. Định mức mới (TT 38/2026) chưa so được
   với TT 12/2021 về mức tăng hay giảm.
5. Chất lượng số liệu (khoản hoàn nhập Q3 chưa soát xét, lệch thuyết minh) và tranh chấp vay cá nhân.

## F. Ghi chú phương pháp

- Ke: khoảng nội địa 12,3–13,4% (khung fleet), áp cho cả hai mảng. Thuỷ điện là dòng tiền có thời hạn, không dùng
  terminal. Tư vấn dùng terminal g 5% (RONIC ≫ Ke).
- Không áp chiết khấu thanh khoản hay thiểu số. Phần "tiếp cận qua cổ tức" chỉ trừ rò rỉ đo được (tiền bị giữ ở lãi
  tiền gửi 5,5% so với Ke).
- Xác suất kịch bản đều là [UL] có căn cứ. Đây là điểm yếu nhất, cần phản biện.

## Nguồn

- BCTC gốc `../dd_TV1_20261102/src/` (số trích ở REPORT §2–§7, `calc/valuation.py` khối dữ liệu).
- `../tv1_sb5_ppa_price_20261013/` (README §1–3, `sb5_price_series.csv`, `peer_hydro_prices.md`).
- `LEGAL_PPA_20261102.md`, `LEGAL_VN_20261102.md`.
- `kb/data_registry/market-state/sector_read_power_consulting_20261028.md` (Bobby, mù).
- TT 38/2026/TT-BXD PL VIII: https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/7/38.2026.tt-bxd-pl8dmqldavatvxd_signed1.pdf
  (Bảng 1.1, 2.3, 2.9, 2.24).
- Báo và trang web:
  - https://baodauthau.vn/pecc1-bao-lai-cao-nhat-lich-su-186-ty-dong-tuong-duong-eps-5500-dong-post192515.html
    (hợp đồng ký mới 2025);
  - https://baodauthau.vn/dhcd-pecc1-manh-tay-chia-co-tuc-tham-gia-loat-du-an-thuy-dien-mo-rong-luoi-dien-dien-hat-nhan-post198014.html
    (ĐHCĐ 30/04/2026);
  - https://vietnamfinance.vn/lien-tuc-trung-thau-nganh-dien-pecc1-co-tiem-luc-ra-sao-d135676.html (Tuyên Quang MR,
    650 gói);
  - https://baodauthau.vn/pecc1-dat-cuoc-tuong-lai-vao-du-an-dien-mat-troi-noi-post180887.html (ĐMT nổi);
  - https://www.vietnamplus.vn/tang-truong-gdp-2-con-so-nganh-dien-buoc-vao-chu-ky-phat-trien-moi-post1136875.vnp
    (EVN 830k);
  - https://evn.com.vn/userfile/User/tcdl/files/2026/3/BanTinEVN-So122026-20260331111014798.pdf (EVN ~5 tỷ USD/năm).
