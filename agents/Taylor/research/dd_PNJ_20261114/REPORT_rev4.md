# DD — PNJ · REV 4 (sau fundamental-skeptic r1 REFUTED + r2 INCONCLUSIVE) · 2026-11-23 · job `Taylor_20261122_234426`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị, không đặt lệnh, không sửa `excluded_tickers`.
> Kế thừa `REPORT.md` (r2 14/11) cho §1–§5, §7, §9; `REPORT_rev3.md` (md5 19e23aa4…, skeptic r2 đã đọc) giữ nguyên, không ghi đè.
> Nguồn: **[HN]** BCTC HN Q3/2026 · **[SX]** soát xét HN bán niên 2026 (PwC HCM18793) · **[KT25]** BCTC HN 2025 kiểm toán (PwC HCM17725) ·
> **[TTr40]** cổ phiếu thưởng · **[TTrPH]** phát hành riêng lẻ · **[TTr607]** điều chỉnh cổ tức 2025 · **[NQ]** ĐHĐCĐ bất thường 21/10 ·
> **[GP]** GP 293/GP-NHNN · **[IRQ3]** "Cập nhật tình hình hoạt động & tài chính Q3-2026" (tài liệu ĐHĐCĐ). Tất cả tải lại từ cdn.pnj.io ngày 23/11/2026 → `src/`
> (14 PDF, md5 `src_md5.txt`). **Ảnh các trang được trích dẫn: `src/pages/*.png`** (đọc được, không cần công cụ PDF). **[BQ]** `tav2_bq`.
> Đơn vị tỷ đồng, đ/cp. Số tự đặt gắn **(ước lượng)**. Khoá: `calc/assumptions_r4.json` (lint 0 vi phạm).

## 0. Kết luận
- **Nhận định GIỮ: NON — tiếp tục loại PNJ.** Sizing V8: **0%** (không đề xuất; chuẩn 2–4% NAV không áp vì không có biên an toàn).
- **Tâm = 4.205 đ/cp** = giá trị kỳ vọng của cổ đông HIỆN HỮU trên **cây kết cục phát hành** (§6). **Vùng 2.212–6.198** = tâm tại xác suất phát hành thành công 0,25/0,75.
  Tâm r2 ~7.005 ⇒ rev3 4.780 ⇒ **rev4 4.205** (−12% so rev3; −40% so r2).
- Kết quả có **hai đỉnh**: phát hành được ở sàn pháp lý (NĐT mới trả ≥ BVPS ⇒ chuyển giao giá trị cho cổ đông hiện hữu: 8.191 trọng số) hoặc
  không phát hành được (8.000 tỷ phải tài trợ bằng nợ/tồn kho + kinh tế hạ một bậc vì KH 2027–29 của DN chỉ áp "nếu huy động vốn thành công" [IRQ3 p9]: 219 trọng số).
  Tâm phụ thuộc chủ yếu vào xác suất thành công p — **không có cơ sở độc lập**; p=0,5 là trung tính, không phải phán đoán.
- Pha sau khoá: giá đóng cửa 20/11 = 13.500 [BQ] ⇒ **giá/tâm = 3,2**; giá trên cả cận trên vùng (6.198) và trên nhánh "phát hành thành công" (8.191) ⇒ nhãn **ĐẮT**.

## Đính chính rev4 so với rev3 — hạng mục skeptic r2 (INCONCLUSIVE)

| # | Hạng mục skeptic r2 | Xử lý rev4 | Loại |
|---|---|---|---|
| 1 | **Chí mạng**: tâm lấy trung bình trên kịch bản "phát hành đúng giá trị", nhưng P* < sàn BVPS ở các kịch bản chiếm 80% trọng số nên kịch bản đó không khả thi; kết quả thực có hai đỉnh | Bỏ đồng nhất thức. Thay bằng **cây kết cục**: O1 phát hành 550tr cp ở sàn (thu 6.923, thiếu 1.077 vay bù) ⇒ (F0 − 1.077×1,08)/1.061,72; O2 không phát hành ⇒ kinh tế hạ một bậc (cơ sở→trễ, tốt→cơ sở) và (F0' − 8.000×1,08)/511,72, sàn 0. Có p, giá trị từng nhánh (§6.2) | (b) p không có cơ sở ⇒ báo dải |
| 2 | t=0,6 làm tâm cao thêm ~22%, không tính chi phí cầu nối | t=0. Chi phí cầu nối = 8% sau thuế/năm × 1 năm (lãi vay Chủ tịch 10% [HN TM16] × (1−20%)), áp cho phần thiếu (O1) và cho toàn bộ 8.000 (O2) | (a) nguồn HN TM16 |
| 3 | Đầu vào chịu lực nhất (N 2029 = 1.600, 8.000 tỷ chia 60/20/20) không truy được | **Đã tải lại** [IRQ3] (`src/Cap-nhat-tinh-hinh-hoat-dong-tinh-hinh-tai-chinh-Q3-2026.pdf`, md5 trong `src_md5.txt`): p9 "KẾT QUẢ KINH DOANH 2027–2029 – **Nếu Huy Động Vốn thành công**": LNST 0,1/1,2/1,6 nghìn tỷ; DT 43,4/50,6/57,7; p7: 21.000 ⇒ 80% = 16.500, dự phòng 7.100, nhu cầu 8.000 năm 2027 (60/20/20). Ảnh `src/pages/IRQ3_p7.png`, `IRQ3_p9.png`. Điều kiện "nếu huy động thành công" ⇒ dùng cho cách xử lý nhánh O2 | (a) |
| 4 | Soát xét PwC H1 có đoạn nhấn mạnh TM39, báo cáo chưa bàn | [SX p6] PwC HCM18793 03/09/2026: kết luận **không ngoại trừ**, **nhấn mạnh TM39** (vụ kim cương P-Lab). [SX TM39, p53]: tới 30/6 dự phòng giảm giá tồn kho 1.416,8, dự phòng thu đổi 2.267,3; Tập đoàn "**chưa ghi nhận bất cứ khiếu nại, yêu cầu bồi thường hoặc… kiện tụng nào liên quan đến nguồn gốc xuất xứ kim cương**"; biện pháp thanh khoản ở TM2.1 (giãn thanh toán thu đổi/nhà cung cấp, đàm phán NH, phát hành). Không phải ý kiến về hoạt động liên tục. Không thêm điều chỉnh: ảnh hưởng tài chính đã nằm trong dự phòng 7.071 của KH | (a) |
| 5 | Sửa LNST Q2 −282,9 → −738,9 không giải thích | Nguồn: LNST H1 soát xét 728,5 [SX] − Q1 1.467,4 = −738,9 ⇒ soát xét cắt ~456 tỷ so với Q2 tự lập (thêm dự phòng sau soát xét; r2 §2/§9). BQ dòng Q3 đã dùng số soát xét (NP_P1). Không ảnh hưởng mô hình (F0 dựa KH 2027–29) | (a) |
| 6 | Tờ trình điều chỉnh cổ tức 2025 có trong src nhưng báo cáo không nhắc | [TTr607 p1]: cổ tức tiền 2025 giảm từ 20% (852,9) xuống **10% (341,1)**, "Công ty **đã hoàn thành việc chi trả**". ⇒ **không còn nghĩa vụ cổ tức chưa trả** | (a) |
| 7 | Kịch bản phát hành thất bại chưa định lượng | Định lượng ở O2. Sàn 0 là **cận dưới**: giá trị thanh lý (tồn kho ròng 16.626 > lỗ 7.071) **không định lượng được**. Nếu thanh lý trả > 0 thì O2 bị đánh giá thấp | (b)/(c) |
| 8 | Host không đọc được PDF | Ảnh các trang trích dẫn đã render vào `src/pages/` (14 PNG) | quy trình |
| 9 | Pháp lý còn mở (NĐ 390, kiện tụng thanh toán chậm, vốn khác 500, quỹ thưởng 50,7, liên kết em trai TV HĐQT) | Kiện tụng nguồn gốc kim cương: không có tới 30/6 [SX TM39]. Còn lại **không kiểm chứng được** trong phiên (WARNING, không vào base, theo luật vụ án chỉ WARNING) | (c) |

### Đính chính rev3 so với r2 (skeptic r1 REFUTED) — giữ nguyên, rút từ REPORT_rev3.md
| # | Hạng mục skeptic r1 | Xử lý rev3 | Loại |
|---|---|---|---|
| 1 | **Lỗi chí mạng**: chia F cho 511,72+550tr cp ⇒ NĐT mới phải trả ≥14.545 cho thứ đáng 6.366 | Giá trị cổ đông hiện hữu = (F0 − PV(8.000))/n0 = P* (giá phát hành công bằng). PV dùng t=0,6 năm (ước lượng, phát hành sau kiểm toán FY2026). Trường hợp "550tr cp đã phát hành" chỉ hiển thị là kịch bản CHUYỂN GIAO, không vào tâm (§6.3) | (a) base, nguồn: [TTrPH 1.8] + đồng nhất thức |
| 2 | g 5% với ROE 10% vô hạn (r2 RONIC < Ke = phạt ngầm, trái D4) | Terminal **RONIC = Ke** (D4, NARROW): giá trị dòng ổn định = N/r, g không tạo/huỷ giá trị ⇒ bỏ biến thể g0/g5 | (a) luật D4 |
| 3 | Chệch THẤP: vốn hoá năm KH 2029 (biên ròng 2,8%) mãi mãi | Giữ KH DN làm base (luật NARROW: không thưởng, không trừ). Biên hồi phục 6,4–7,9% ⇒ chỉ **độ nhạy** (N 3.693–4.558 ⇒ 27.005–36.731 đ/cp), không có cơ sở độc lập để vào base. Kịch bản tốt N=2.500 (p 0,2) đã đại diện chiều hồi phục | (b) |
| 4 | Chệch THẤP: tiền giải phóng từ tồn kho dư | Không vào base: KH chính DN cần THÊM 1.600 vốn lưu động (20% × 8.000). Độ nhạy: mỗi 1.000 tỷ tồn kho bán được theo giá sổ ⇒ **+1.954 đ/cp** | (b) |
| 5 | Thiếu: thêm 1.768 lỗ nếu 100% khách thu đổi | Đưa vào thành kịch bản `stress_100pct` (p 0,10): 445 đ/cp | (b) có xác suất |
| 6 | BCTC kiểm toán FY2025 chưa đọc | **Đã đọc** [KT25 p4]: PwC, báo cáo HCM17725 ngày 18/03/2026, **chấp nhận toàn phần, không có đoạn nhấn mạnh** | (a) |
| 7 | Giấy phép vàng miếng NĐ 232/390 chưa kiểm | GP kinh doanh mua bán vàng miếng 293/GP-NHNN (28/12/2012) còn đăng trên trang IR. NĐ 232/2025 (hiệu lực 10/10/2025) đặt "có GP mua bán vàng miếng" làm điều kiện để xin GP **sản xuất** vàng miếng, nên không thu hồi GP mua bán. Chưa thấy PNJ được cấp GP sản xuất. **NĐ 390/2026: không kiểm chứng được** trong phiên này. Ảnh hưởng ước lượng: mảng 24K ≈17% DT Q3, vàng miếng là tập con biên mỏng ⇒ tác động lên F0 nhỏ (ước lượng <5%) | (c) |
| 8 | Số cp nhảy 341→511,7tr Q1/2026 không giải thích | [TTr40]: **thưởng 2:1 từ VCSH**, 341,149 → 511,724tr lưu hành (169.559 cp quỹ). Không có tiền vào; thặng dư vốn giảm 1.982,7 → 277,0 khớp 1.705,7 [HN BS]. ESOP 2025/2026: chưa phát hành tới 30/9 (VĐL 5.118,9 tỷ khớp đúng) | (a) |
| 9 | Quỹ phúc lợi, bảo lãnh, kiện tụng khách hàng, tài sản thuế hoãn lại 773 | Quỹ KT-PL **473,2** là nợ phải trả, không trừ thêm [HN BS 323]. **WARNING**: quỹ thưởng HĐQT & BĐH **50,7** (đầu năm 0,7) [HN TM15a] được dựng trong năm khủng hoảng; nguồn trích chưa đối chiếu. "Vốn khác của CSH" **500,0** (đầu năm 0) [HN BS 414]: cần kiểm chứng, đã nằm trong VCSH nên không đổi F0. Tài sản thuế hoãn lại 773,3: KH LNST 2027–29 cộng 2.900 ⇒ thu hồi được ở base, không điều chỉnh. **Bảo lãnh/kiện tụng khách hàng: không kiểm chứng được**; không thấy trong các trang đã đọc (BS, TM14–17, TM27), chưa đọc hết thuyết minh | (c) phần kiện tụng |
| 10 | `src/` không có trên đĩa ⇒ không truy được số | Tải lại 12 PDF gốc (md5 `src_md5.txt`). Đối chiếu lại trên ảnh trang: **21.057,9** / dư dự phòng **821,4** / câu chữ 6.104,3 & 6.783,3 [HN TM17]; vay NH **3.616,9** vs 4.223,4 + vay cá nhân **703,7** [HN TM16]; VCSH mẹ **13.182,3** [HN BS]; **7.071,1** + 550tr cp + hoàn nhập quỹ ĐTPT 4.602,8 [HN TM27]; nguyên tắc giá chào bán [TTrPH 1.8]. **KH 2027–29 + 8.000 tỷ (60/20/20)**: bản IR "Cập nhật tình hình Q3" **không tải lại được** từ pnj.com.vn ngày 23/11 ⇒ số kế thừa r2 (đã đọc p9 ở r2), **chưa truy lại** | (a)/(c) |
| 11 | Trọng số r1/r2 đặt sau khoá | Rev3 khoá trọng số trong `assumptions_r3.json` **trước** khi đọc giá/ADV (md5 bên dưới) | quy trình |
| 12 | Chưa có lượt mù giá thật | Mô hình rev3 **không có biến giá**. Khoá md5 xong rồi mới truy vấn giá/ADV BQ. ⚠️ Minh bạch: phiên này đã đọc r2 §3 có một con số giá cũ trước khi khoá (không dùng làm đầu vào) | quy trình |
| — | Phát hiện mới (TM17) | Bảng TM17 ghi **tỷ lệ khách thực hiện bán lại thực tế 28,8% (hàng 2020–26) / 7,0% (trước 2020)**, tổn thất 638,2/183,2 ⇒ lỗ/giá trị thu đổi **20,3% / 25,8%**. Áp mức lỗ đó ở 80% ⇒ ~3.867 vs KH 7.071. DN nói rõ cơ cấu hàng thu hồi sẽ dịch sang mặt hàng lỗ cao ⇒ **giữ 7.071 trong base**; chênh 3.205 tỷ (+5.878 đ/cp) chỉ là **độ nhạy chiều tăng** | (b) |

*(Hạng mục 1 rev3, "giá trị = (F0 − PV vốn mới)/n0", **bị thay ở rev4** bằng cây kết cục; hạng mục 12: tham số p của rev4 đặt SAU khi đã thấy giá — xem §6.2.)*

## 6. Định giá rev4

### 6.1 Khung
- F0 = VCSH vận hành sau phát hành tại 31/12/2026 = N/r chiết khấu từ năm đạt N (D4: NARROW ⇒ RONIC = Ke ⇒ g không tạo/huỷ giá trị). LNST 2027–28 coi như giữ lại và đã nằm trong N 2029, nên không đếm hai lần (chệch ước lượng ±260 tỷ).
- **r = 13,5%**: `deposit_rate_vn('2026-11-23')` = 7,40% (CCTG 12M 02/11; Big-4 6,80%) = neo 03/11 ⇒ Δ=0, β=1. Dải Ke 12,3–13,4% báo kèm.
- Sàn giá phát hành = max(TB 30 phiên, BVPS kiểm toán/soát xét gần nhất) [TTrPH 1.8]. BVPS FY2026 ước lượng 12.586 = (13.182,3 − 6.741,7)/511,72 (KH 2026 −6.270).
- Giá trị cp hiện hữu ở kịch bản cơ sở nếu phát hành đúng giá trị = 2.345 < 12.586 ⇒ không hợp lệ về pháp lý ⇒ cây kết cục:
  - **O1** phát hành 550tr cp ở sàn: thu 6.923; phần thiếu 1.077 vay với chi phí cầu nối 8% ⇒ (F0 − 1.164)/1.061,72.
  - **O2** không phát hành: 8.000 tài trợ bằng nợ/tồn kho với chi phí 8% ⇒ (F0' − 8.640)/511,72, sàn 0; F0' = kinh tế hạ một bậc vì KH DN chỉ áp khi huy động thành công [IRQ3 p9].

### 6.2 Kịch bản × kết cục (trọng số vận hành khoá ở r3 TRƯỚC khi đọc giá; p thành công = 0,5 trung tính, đặt SAU khi thấy giá ⇒ chỉ báo dải)

| Kịch bản vận hành | w | Cơ sở | F0 | O1 (phát hành ở sàn) | O2 (không phát hành) | 0,5·O1+0,5·O2 |
|---|---|---|---|---|---|---|
| Cơ sở | 0,50 | KH LNST 2029 = 1.600 [IRQ3 p9] | 9.200 | 7.569 | 0 | 3.785 |
| Tốt | 0,20 | (ước lượng) N=2.500 ≈ kinh tế 2023–25 [BQ 1.971/2.113/2.828] | 14.375 | 12.444 | 1.095 | 6.769 |
| KH trễ 1 năm | 0,20 | 1.600 đạt 2030 (ước lượng) | 8.106 | 6.539 | 0 | 3.269 |
| 100% thu đổi | 0,10 | cơ sở − 1.768 lỗ thêm 2027 (7.071×0,2/0,8) | 7.643 | 6.102 | 0 | 3.051 |
| **Trọng số** | | | | **8.191** | **219** | **TÂM 4.205** |

p = 0,25 ⇒ 2.212; p = 0,75 ⇒ 6.198 (**vùng**). Mỗi +0,1 của p ⇒ +797 đ/cp.

### 6.3 Độ nhạy (V1, D4) — tâm tại p=0,5
r −100bp 5.098 · −50bp 4.519 · +50bp 3.915 · +100bp 3.688 · Ke 12,3% 5.385 · Ke 13,4% 4.266.
Chiều tăng, không vào base (không có cơ sở độc lập):
- biên ròng hồi phục 6,4–7,9% ⇒ N 3.693–4.558;
- lỗ thu đổi theo tỷ lệ thực tế TM17 (lỗ 20,3%/25,8% giá trị thực hiện; 28,8%/7,0% khách thực hiện [HN TM17]) ⇒ ~3.867 thay 7.071 (−3.205 tỷ lỗ);
- mỗi 1.000 tỷ tồn kho giải phóng ⇒ +1.954 đ/cp ở nhánh O2;
- giá trị thanh lý ở nhánh O2 (không định lượng được).

### 6.4 V3 thanh khoản (sau khoá)
ADV trung vị 20 phiên **101,9 tỷ**, 60 phiên **146,2 tỷ** [BQ `ticker` Price×Volume tới 20/11]. Với vị thế 50 tỷ (ước lượng) ở tỷ lệ tham gia 10–20%, thoát trong 2,5–4,9 phiên ⇒ chiết khấu thanh khoản **0%** ⇒ trước = sau = 4.205.

### 6.5 V6 hai nền (chỉ hiển thị)
FCFE ≤ 0 (CFO TTM −2.579,5 [BQ]) ⇒ chỉ tính V_ngắn = trung vị LNST 2023–25 2.112,9 / r = 15.651 tỷ (30.585 đ/cp trên 511,72tr; 14.741 trên 1.061,72tr). V_ngắn dựa trên kinh tế trước khủng hoảng, trước nghĩa vụ thu đổi 21.058 và trước pha loãng ⇒ không làm neo, không tính D.

### 6.6 V5 — 5F
Tái dùng r2 14/11 (<12 tháng): **NARROW (đang suy giảm), BRAND/SCALE**, rủi ro số 1 = niềm tin khách hàng. Kiểm nhanh 23/11: TM17 (khách thực hiện 28,8%) và TM39 (chưa có kiện tụng nguồn gốc) không đổi phân loại.

## 8. Vùng giá & điều kiện đổi nhận định (HAI chiều)
- Tâm **4.205**, vùng **2.212–6.198**. Giá 13.500 ⇒ 3,2× tâm ⇒ **giữ NON**.
- **Đổi lên**: (i) đợt riêng lẻ hoàn tất ≥ sàn với NĐT độc lập ⇒ p→1, tâm ≈ 8.191 (vẫn dưới giá 20/11); (ii) kiểm toán FY2026 chốt lỗ thu đổi < 7.071; (iii) LNST 2 quý liền ≥ nhịp KH 2028.
- **Đổi xuống**: phát hành thất bại/thu nhỏ trước 31/12/2027; tỷ lệ thực hiện > 80%; ý kiến ngoại trừ FY2026, hoặc mâu thuẫn TM17 (6.104 vs 821) ngả về hướng Q3 thiếu dự phòng; NH tiếp tục rút hạn mức.
- Mốc: BCTC Q4/2026 (~cuối 01/2027), kiểm toán FY2026 (~03/2027), hồ sơ chào bán.

## 10. Nguồn & khoá rev4
- `calc/assumptions_r4.json` md5 **bdc370b2ee515b23043c1580c4f543ac** · `calc/model_r4.py` 85263e5645d0c994ce8517b9906ed2f0 · `calc/model_r4_out.json` cfff0097ddab0c4f0cc9505e6563dd82 (`calc/LOCK_r4_md5.txt`). Rev3: `calc/LOCK_r3_md5.txt`.
- Minh bạch mù giá: trọng số vận hành + N + r khoá ở r3 trước khi truy vấn giá. Phiên này đã thấy một con số giá cũ trong r2 §3 trước khi khoá; p của rev4 đặt sau khi thấy giá ⇒ chỉ báo dải. Mô hình không có biến giá.
- Còn mở, không kiểm chứng được: NĐ 390/2026; kiện tụng do thanh toán chậm sau 30/6; nguồn "vốn khác" 500 tỷ [HN BS 414]; nguồn quỹ thưởng HĐQT&BĐH 50,7 [HN TM15a]; CBTT về liên kết em trai TV HĐQT; giá trị thanh lý nhánh O2.
