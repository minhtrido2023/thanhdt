# DD — PNJ · REV 3 (dựng lại sau fundamental-skeptic r1 REFUTED) · 2026-11-23 · job `Taylor_20261122_234426`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị, không đặt lệnh, không sửa `excluded_tickers`.
> Kế thừa `REPORT.md` (r2, 14/11; md5 0ecbc539…) cho §1–§5, §7, §9 — **không làm lại**, chỉ sửa phần skeptic r1 bác + bổ sung hạng mục thiếu.
> Nguồn: **[HN]** BCTC hợp nhất Q3/2026 · **[SX]** soát xét bán niên 2026 PwC · **[KT25]** BCTC hợp nhất 2025 kiểm toán PwC ·
> **[TTr40]** tờ trình 40/2026 cổ phiếu thưởng · **[TTrPH]** tờ trình phát hành riêng lẻ · **[NQ]** NQ/biên bản ĐHĐCĐ bất thường 21/10 ·
> **[GP]** GP 293/GP-NHNN. Tất cả **tải lại từ cdn.pnj.io ngày 23/11/2026** vào `src/` (12 file, md5 ở `src_md5.txt`). **[BQ]** `tav2_bq`.
> Đơn vị tỷ đồng, đ/cp. Số tự đặt gắn **(ước lượng)**. Khoá: `calc/assumptions_r3.json` (lint `dd_assumptions_lint.py`: 0 vi phạm).

## 0. Kết luận

- **Nhận định GIỮ NGUYÊN: NON — tiếp tục loại PNJ** (skeptic r1 xác nhận phần này). Sizing V8: **0%** — không đề xuất mua.
- **Định giá viết lại**: dùng **giá phát hành nhất quán**: giá trị/cp của cổ đông HIỆN HỮU = (F0 − PV 8.000 tỷ vốn mới)/511,72tr.
  r2 lấy F chia 1.061,72tr cp, tức ngầm giả định NĐT mới trả ≥14.545 đ/cp cho thứ mô hình định giá 6.366. Lỗi này skeptic đã bắt đúng.
- **Tâm (giá trị kỳ vọng có trọng số kịch bản) = 4.780 đ/cp**; kịch bản cơ sở 3.489; **vùng đọc 3.270–6.670** (tâm trọng số tại r ±100bp).
  Dải kịch bản 1.351 (KH trễ 1 năm) … 13.602 (thương hiệu hồi phục). Tâm r2 ~7.005 (giữa vùng 6.370–7.640) ⇒ **giảm ~32%**.
- **Pha sau khoá** (đọc giá sau khi khoá md5): giá đóng cửa 20/11 = 13.500 ⇒ **giá/tâm = 2,82**. Giá thị trường ngang kịch bản TỐT (13.602), hoặc ngang
  trường hợp NĐT mới trả cao hơn giá trị (chuyển giao giá trị, 8.665 ở kịch bản cơ sở). Không có biên an toàn ⇒ nhãn **ĐẮT** so với giá trị nội tại.
- Ở kịch bản cơ sở, giá phát hành công bằng P* = 3.489 < **sàn pháp lý BVPS ~12.586** (ước lượng BVPS kiểm toán FY2026) [TTrPH 1.8].
  ⇒ Đợt 8.000 tỷ chỉ thành công nếu NĐT mới định giá PNJ cao hơn mô hình (cần F0 ≥ 13.855 tỷ, tức gần kịch bản tốt), nếu không đợt phát hành sẽ thất bại hoặc bị thu nhỏ. Đây là rủi ro lớn nhất và **không kiểm chứng được** trước khi có kết quả chào bán.

## Đính chính so với rev trước (r2) — từng hạng mục skeptic r1

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

## 6. Định giá rev3 (thay §6 r2)

### 6.1 Khung
- F0 = giá trị VCSH **sau phát hành** tại 31/12/2026 = N/r chiết về từ năm đạt N (RONIC = Ke). LNST 2027–28 (100; 1.200) coi như giữ lại và đã nằm trong N 2029, nên không đếm hai lần. Chệch do giả định này: ước lượng ±260 tỷ.
- Giá trị cp hiện hữu = max(0, F0 − 8.000/(1+r)^0,6)/511,72. Đây cũng là giá phát hành công bằng P*.
- **r = 13,5%**: lãi huy động 12T hiệu dụng `deposit_rate_vn('2026-11-23')` = **7,40%** (CCTG 12M 02/11; Big-4 6,80%) = neo 03/11 ⇒ Δ=0, β=1.

### 6.2 Kịch bản (khoá trước giá; trọng số ước lượng chủ quan, lệch xuống có lý do trong file khoá)

| Kịch bản | p | Cơ sở | F0 (tỷ) | đ/cp hiện hữu | P* ≥ sàn BVPS 12.586? |
|---|---|---|---|---|---|
| Cơ sở | 0,50 | KH LNST 2029 của DN = 1.600 | 9.200 | **3.489** | Không |
| Tốt | 0,20 | (ước lượng) N=2.500 ≈ kinh tế 2023–25 (BQ 1.971/2.113/2.828) | 14.375 | 13.602 | Có |
| KH trễ 1 năm | 0,20 | 1.600 đạt năm 2030 (ước lượng) | 8.106 | 1.351 | Không |
| 100% thu đổi | 0,10 | cơ sở − 1.768 lỗ thêm 2027 (7.071×0,2/0,8) | 7.643 | 445 | Không |
| **Kỳ vọng trọng số (TÂM)** | | | | **4.780** | |

### 6.3 Kịch bản CHUYỂN GIAO (chỉ hiển thị, không vào tâm)
Trong trường hợp 550tr cp được phát hành ở sàn pháp lý dù P* < sàn, NĐT mới trả cao hơn giá trị và phần chênh chuyển sang cổ đông hiện hữu. Khi đó F0/1.061,72 = 8.665 (cơ sở), 7.635 (trễ), 13.540 (tốt).
Ở sàn BVPS 12.586, 550tr cp chỉ thu **6.923 < 8.000**. Muốn phát hành công bằng ở sàn thì cần F0 ≥ **13.855**. Kịch bản thất bại phát hành (giá trị có thể <445): **không định lượng được**.

### 6.4 Độ nhạy (V1, D4)
| | −100bp | −50bp | +50bp | +100bp | Ke 12,3% | Ke 13,4% |
|---|---|---|---|---|---|---|
| Cơ sở | 5.197 | 4.308 | 2.733 | 2.034 | 5.574 | 3.648 |
| Tâm trọng số | 6.674 | 5.688 | 3.971 | 3.274 | 7.093 | 4.955 |

Thời điểm phát hành t=0 / 1,0 năm: cơ sở 2.345 / 4.205; tâm 3.706 / 5.495. Độ nhạy chiều tăng không vào base: biên ròng hồi phục 6,4/7,9% ⇒ 27.005/36.731; lỗ thu đổi theo tỷ lệ thực tế TM17 ⇒ +5.878; mỗi 1.000 tỷ tồn kho giải phóng ⇒ +1.954.

### 6.5 V3 thanh khoản (sau khoá)
ADV trung vị 20 phiên **101,9 tỷ**, 60 phiên **146,2 tỷ** (BQ `ticker` Price×Volume tới 20/11/2026). Giả sử vị thế 50 tỷ (ước lượng, ~2–4% NAV một account lớn): ở tỷ lệ tham gia 10–20% thì thoát trong 2,5–4,9 phiên ⇒ **chiết khấu thanh khoản 0%**; giá trị trước = sau chiết khấu = 4.780.

### 6.6 V6 hai nền (chỉ hiển thị)
FCFE ≤ 0 (CFO TTM −2.579,5 [BQ]) và trượt cổng CFO ⇒ chỉ tính **V_ngắn**: trung vị LNST 2023–25 = 2.112,9; N/r = 15.651 tỷ, tức 30.585 đ/cp trên 511,72tr hoặc 14.741 trên 1.061,72tr. V_ngắn dựa trên kinh tế **trước khủng hoảng**, trước nghĩa vụ thu đổi 21.058 và trước pha loãng, nên không dùng làm neo. Không tính D.

### 6.7 V5 — 5F
Đã làm ở r2 14/11 (<12 tháng, tái dùng): NARROW (đang suy giảm), BRAND/SCALE; rủi ro số 1 = niềm tin khách hàng. Kiểm nhanh 23/11: số liệu mới (TM17: khách thực hiện 28,8% hàng 2020–26) **không đổi** phân loại.

## 8. Vùng giá & điều kiện đổi nhận định (HAI chiều)
- Vùng đọc **3.270–6.670**, tâm **4.780**; giá 13.500 ⇒ 2,82× tâm ⇒ giữ NON.
- **Đổi lên** (tái định giá, có thể bỏ loại): (i) đợt riêng lẻ hoàn tất ≥ sàn với NĐT độc lập, vì đó là bằng chứng thị trường cho F0 ≥ 13,9k; (ii) BCTC kiểm toán FY2026 chốt lỗ thu đổi < 7.071 (gần mức lỗ thực tế 20–26%); (iii) LNST 2 quý liền ≥ nhịp KH 2028.
- **Đổi xuống**: đợt phát hành thất bại/thu nhỏ trước 31/12/2027; tỷ lệ thực hiện > 80%; kiểm toán FY2026 có ý kiến ngoại trừ, hoặc làm rõ mâu thuẫn TM17 (6.104 vs 821) theo hướng Q3 thiếu dự phòng; vay NH tiếp tục co hẹp.
- Mốc: BCTC Q4/2026 (~cuối 01/2027), kiểm toán FY2026 (~03/2027), hồ sơ chào bán UBCKNN.

## 10. Nguồn & khoá rev3
- `calc/assumptions_r3.json` md5 **921e9fae404cdc213bb5b80ade66a656** · `calc/model_r3.py` md5 c7edf4b2bdaee5e4e3468ec088abd63d · `calc/model_r3_out.json` md5 188186371d119b4f7d2364a48b60a1e8 (`calc/LOCK_r3_md5.txt`).
- `src/` 12 PDF tải lại 23/11 (`src_md5.txt`); trang đã đọc: [KT25] p3–6; [HN] p3, p5, p26, p28, p34; [TTr40] p1; [TTrPH] p2; [GP] p1; [NQ biên bản] p4 (348,4tr phiếu dự họp).
- Giá/ADV đọc **sau** khoá: BQ `tav2_bq.ticker` tới 2026-11-20.
- Còn mở (không kiểm chứng được): bản IR có KH 2027–29 (chưa tải lại được), NĐ 390/2026, kiện tụng/bảo lãnh, nguồn vốn khác 500 tỷ, nguồn quỹ thưởng HĐQT 50,7 tỷ, đối chiếu CBTT về "em trai thành viên HĐQT".
