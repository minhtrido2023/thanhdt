# CYCLE_BLOCK — NNC (CTCP Đá Núi Nhỏ) · job `Taylor_20261026_045700` · as-of dữ liệu tài chính 2026Q2

> Bước 1 theo `dd_template_20261026/TEMPLATE.md`. Dữ liệu tài chính chỉ đến **2026Q2** (Q−1; Q = 2026Q3, công bố
> 20–22/10/2026). Không mở BCTC 2026Q3 hay tin bình luận KQKD Q3.
> ⚠️ **Đã nhiễm (khai trước khi viết):** (i) working memory của Taylor bơm vào đầu phiên có dòng verdict cũ của
> NNC ("NON, không fear-state, đỉnh chu kỳ, PB 1,59; weighted 62,8k vs 47,6k"); (ii) `README.md` của thư mục
> template (file được giao đọc) có biên gộp Q3 57,9%, "đá +50% so 2023–24", "giấy phép 2043", "PE 4,88x" và phụ lục
> "khẳng định NON". ⇒ **blind: no**. Khối dưới vẫn được viết chỉ từ nguồn ≤ Q−1 ghi ở từng dòng; con số 57,9% và
> verdict cũ không dùng ở đâu cả.

**Loại ngành:** chu kỳ cầu đầu tư (đá xây dựng, thị trường cục bộ bán kính ~60 km, cầu do hạ tầng công).

**A. Biên hiện tại so với lịch sử chính mã** (dữ liệu đến 2026Q2)
- Cửa sổ: 2010Q1–2026Q2, 66 quý, số chu kỳ thấy được k = 2 (đỉnh 2016–18 → đáy 2021–24 → lên 2025–26).
  **Đổi mô hình 2021Q3–2022:** dừng khai thác mỏ Núi Nhỏ (Bình Dương, 2 tr m³/năm), Mũi Tàu (Bình Phước) thành mỏ
  chính [FPTS 07/01/2026 tr.7; BQ doanh thu quý từ ~60 tỷ xuống 17 tỷ ở 2021Q3]. Tính cả hai cửa sổ.
- **Biên LNST TTM 2026Q2 = 38,8%** [BQ, ΣNP_P0/ΣRevenue_P0 4 quý = 187,2/482,0 tỷ; khớp `NPM_P0`=0,388].
  Sau khi bỏ khoản một lần 2022Q4 (NP 28,4 tỷ > doanh thu 23,5 tỷ, thay bằng trung vị 2022Q1–Q3): **phân vị 100**
  trong cả 63 quý TTM (trung vị 27,8%, max cũ 34,4%) và **phân vị 100** trong 17 quý chế độ Mũi Tàu (2022Q2+,
  trung vị 22,4%). Trung vị 5 năm (2021Q3–2026Q2, thô) = 25,9%.
- **Biên gộp:** `GPM_P0` 2026Q2 = 0,513, phân vị 100 (cả hai cửa sổ). `GPM_P0` có vẻ là TTM (`NPM_P0` là TTM), nhưng
  **chưa kiểm được với BCTC kiểm toán** (không có bản BCTC 2025 trong phiên này; FPTS chỉ có 9T2025 = 49,0%,
  không cùng cửa sổ) ⇒ dùng biên LNST làm chỉ số chính.
- k = 2 ⇒ phân vị là **mô tả**.

**B. Giá đầu ra / đầu vào**
| Biến | Vai trò | Gần nhất | Trung vị ~5 năm | Phân vị | Nguồn |
|---|---|---|---|---|---|
| Giá bán đá bình quân Mũi Tàu | đầu ra | 280,4 nghìn đ/m³ (9T2025); NNC chung 298,0 (+48,3% YoY) | ~170–200 (2020–2024: 170,0→154,1→…→202,6) | cao nhất trong chuỗi năm 2020–9T25 (6 điểm) | [CTCK] FPTS 07/01/2026 tr.13–14 |
| Giá đá 1x2 TP.HCM (Sở XD) | đầu ra vùng | 750 nghìn–<1 tr đ/m³ (08/2026) vs 350–500 nghìn đầu 2026 | — | — | [WEB] nhadautu.vn 20/08/2026 |
| Vật liệu nổ/m³ | đầu vào, 18% giá vốn 2024 | 25 nghìn đ/m³ (2024) vs 13 (2022); ANFO 42–45 nghìn/kg ổn định | — | — | [CTCK] FPTS tr.9 |
| Dịch vụ mua ngoài/m³ | đầu vào | 64 nghìn đ/m³ (2022, −24%), giảm tiếp nhờ máy nghiền | — | — | [CTCK] FPTS tr.10 |
- **CHUỖI THIẾU (một phần):** không có feed giá đá trong `data/`; chuỗi giá bán là số năm thứ cấp của 1 CTCK, 6 điểm
  (≥ 5 năm nhưng < 10). Dùng có điều kiện cho C, ghi rõ.

**C. Pha chu kỳ: ĐỈNH** (sớm ở đỉnh / cao nguyên, không phải đi xuống)
- Mặc định cơ học: A = phân vị 100, B (giá đầu ra) = cao nhất chuỗi ⇒ ≥ 80 cả hai ⇒ **ĐỈNH**. Không lệch.
- Ủng hộ 1: biên LNST TTM 38,8% vượt mọi quý kể cả đỉnh Núi Nhỏ 2016–18 (max 34,4%) [BQ].
- Ủng hộ 2: cung mới — Tam Lập 3 (KSB) và Tam Lập 2 Khu B (Fico) vào hoạt động 2025, mỗi mỏ 1 tr m³/năm, bằng
  Mũi Tàu, cùng cụm Đồng Phú–Phú Giáo [FPTS tr.15]; NNC đã chạm trần chế biến 1,4 tr m³ năm 2026F [FPTS tr.1] ⇒ sản
  lượng không tăng tiếp, chỉ còn biến giá.
- **Chống:** cầu cụm vẫn đang tăng — FPTS ước cầu cụm 34,7%/năm tới 2027 (4,9 tr m³ 2027F), các cao tốc Gia
  Nghĩa–Chơn Thành, TP.HCM–Thủ Dầu Một–Chơn Thành, Bắc Tân Uyên–Phú Giáo–Bàu Bàng thi công 2025–27 [FPTS tr.1, 6];
  giá đá vùng còn tăng mạnh tới 08/2026 [WEB]. Đỉnh có thể kéo dài 4–6 quý trước khi gãy.
- Cơ chế cú sốc dự kiến: **cầu** (hạ tầng hoàn thành, FPTS ước cầu cụm 2028F ~3,0 tr m³, −39%) **cộng cung** (Tam
  Lập). Đáy cũ 2021–24 là loại khác: **cấu trúc/sản lượng** (đóng mỏ Núi Nhỏ) + cầu yếu quanh Mũi Tàu ⇒ PB đáy
  2022–24 (0,97–1,30, BQ `PB`) chỉ so được một phần.

**D. Neo chính sách / rủi ro cấu trúc**
| Neo/rủi ro | Loại | Ngày | Chu kỳ / cấu trúc | Nguồn |
|---|---|---|---|---|
| GP Mũi Tàu: trữ lượng 22,5 tr m³, 1 tr m³ nguyên khối/năm | giấy phép | cấp 2019, **hết 2043** (còn ~17 năm) | cấu trúc — dòng tiền CÓ THỜI HẠN | FPTS tr.2, tr.9 |
| Tam Lập 3 + Tam Lập 2 Khu B, 2×1 tr m³/năm | cung đối thủ | vào hoạt động 2025 | chu kỳ (giá) | FPTS tr.15 |
| Cụm dự án hạ tầng quanh mỏ | phân bổ đầu tư công | thi công 2025–2027; cầu giảm từ 2028F | chu kỳ | FPTS tr.1, 6 |
| QĐ 1581/QĐ-UBND Bình Dương: truy thu tiền cấp quyền khai thác mỏ Núi Nhỏ (đã khai thác) | thuế-phí | trước 01/2026 (ngày QĐ chưa thấy) | một lần — rủi ro chi phí | FPTS tr.9 |
| Giới hạn công suất: chế biến 1,4 tr m³ thành phẩm/năm | giấy phép/thiết bị | 2026F | cấu trúc — trần doanh thu | FPTS tr.1, 10 |
- Dòng tiền lõi có thời hạn (2043) ⇒ E không dùng PE vĩnh viễn làm neo duy nhất.

**E. PE/PB trên LN chuẩn hoá** (giá tham chiếu 47.600 đ, đóng cửa 23/10/2026, BQ `ticker`; OShares 21,92 tr [BQ])
- Vốn hoá = 47.600 × 21,92 tr = **1.043 tỷ** [UL].
- Net cash [BQ 2026Q2]: `Cash_P0` 72,1 tỷ − nợ vay (`StDebt_P0` 6,7 + `LtDebt_P0` 18,9) = **46,5 tỷ**. `LtInvest_P0`
  119,3 tỷ không biết có phải tiền gửi có kỳ hạn ⇒ KHÔNG cộng (bẫy `Cash_P0`; cần BCTC). Lãi tiền gửi sau thuế
  trên 72 tỷ × ~5% × 0,8 ≈ **2,9 tỷ (ước lượng)**.
- LN chuẩn hoá — hai cách, chọn **E1 làm chính** vì không có LN giữa chu kỳ trong chế độ Mũi Tàu ngoài 2023–25:
  - **E1** = trung vị LNST năm chế độ Mũi Tàu 2023–2025 {36,6; 62,6; 147,8} = **62,6 tỷ** [BQ, tổng NP_P0 theo năm].
    PE_cn ex-cash = (1.043 − 46,5)/(62,6 − 2,9) = **16,7x**.
  - **E2** = biên LNST giữa chu kỳ 30% (≈ trung vị TTM toàn lịch sử ex-one-off 27,8% làm tròn lên) × doanh thu 2025
    391 tỷ = 117 tỷ [UL] ⇒ PE_cn = **8,7x**.
  - Đối chiếu: PE TTM thô 1.043/187,2 = 5,6x — đúng bẫy "PE thấp ở đỉnh".
- PB = 47.600 / BVPS 28.070 (2026Q2) = **1,70x** [BQ]; PB tại đáy 2022–24: 0,97–1,30x [BQ `PB`] (đáy khác loại, xem C).
- Dòng tiền có thời hạn: 17 năm × 62,6 tỷ chiết khấu 12% ≈ 62,6 × 7,1 = **~445 tỷ (ước lượng)**; × 117 tỷ ≈ 830 tỷ
  (ước lượng), cả hai < 1.043 tỷ vốn hoá trước khi cộng tiền.

**F. DỰ BÁO CÓ THỂ BÁC BỎ**
```
FORECAST
  indicator   : biên LNST TTM NNC = Σ LNST 4 quý / Σ doanh thu thuần 4 quý, theo BCTC quý NNC
  source      : BCTC quý NNC (CBTT HOSE) 2026Q2..2027Q1; đối chiếu tav2_bq.ticker_financial NP_P0/Revenue_P0
  baseline    : 38,8% (TTM 2026Q2)
  call        : biên LNST TTM tại 2027Q1 <= 40,0% (đỉnh biên đã đạt trong khoảng ±1,2pp; không mở rộng thêm)
  horizon     : quý 2027Q1
  due_date    : 2027-05-01 (BCTC Q1 thường 18–21/04 + 10 ngày)
  p           : 0,55
  persistence : 38,8% → cũng thoả call; mean-revert về trung vị 5 năm 25,9% → thoả call. Call chỉ SAI nếu
                biên tiếp tục mở rộng > 40% (quan điểm GIỮA-LÊN), nên đây là phép thử ĐỈNH vs GIỮA-LÊN
  void_if     : M&A/hợp nhất mỏ mới, đổi giấy phép công suất, đình chỉ khai thác, khoản bất thường > 20% LNST TTM
```
