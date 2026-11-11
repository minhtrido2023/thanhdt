# DD — CST (CTCP Than Cao Sơn – TKV, HNX) · 2026-11-11 · job `Taylor_20261111_133358`

> NGHIÊN CỨU READ-ONLY, không phải khuyến nghị mua; người quyết là user. **Đã qua fundamental-skeptic 11/11 (REFUTED mức văn bản, nhãn định giá đứng; 14 đính chính đã áp — Phụ lục E).**
>
> **Nguồn** (mỗi số trong báo cáo đều ghi nguồn; ảnh trang lưu ở `img_q3/`):
> - **[Q3]** BCTC riêng Q3/2026, bản gốc lấy từ HNX CBTT, đăng 22/10/2026 lúc 10:52. Chưa soát xét. Ký ngày 20/10/2026 (TT99/2025). File `src_q3/000000016954303_VI_BaoCaoTaiChinh_Q3_2026.pdf`; `p` = số trang PDF.
> - **[GT3]** Công văn giải trình LN số 8364/TCS-KT ngày 20/10/2026 (`src_q3/…GiaiTrinh…Q3_2026.pdf`).
> - **[6T]** BCTC 6T/2026 đã soát xét, `src/VI_BaoCaoTaiChinh_SauSoatXet_6T_2026.pdf`. PKF-TTG soát xét, kết luận chấp nhận toàn phần.
> - **[KT25]** BCTC 2025 đã kiểm toán, `src/VI_BaoCaoTaiChinh_KiemToan_2025.pdf`. AASC kiểm toán, ý kiến chấp nhận toàn phần.
> - **[BQ]** `tav2_bq.ticker_financial` (NP_P0/Revenue_P0 là số quý) và `tav2_bq.ticker` (giá, khối lượng thật).
> - **[Bobby]** `kb/data_registry/market-state/sector_read_than_20261111.md`, đọc ngành mù.
> - Phép tính: `calc/model.py` → `calc/model_out.json`. Giả định khoá ở `calc/assumptions.json`.
>
> Số nào không đo được đều gắn nhãn **(ước lượng)**.

## 0. Kết luận

**Ở giá 14.900, giá đang CAO HƠN tâm giá trị khoảng 17% ⇒ không có biên an toàn.**
- **Tâm giá trị:** **13.084 đ/cp** trước chiết khấu thanh khoản, **12.681** sau chiết khấu ở cỡ 0,3 tỷ.
- **Vùng giá trị:** bi quan 6.316, lạc quan 20.799 (sau chiết khấu thanh khoản).
- **Nhãn:** TRONG vùng nhưng TRÊN tâm. Ngưỡng luật 0,85×tâm = **10.779**, giá hiện tại chưa chạm.

Lý do ngắn gọn: CST là **đơn vị gia công khai thác cho TKV theo giá vốn cộng lãi định mức**.
- 97% doanh thu bán cho các đơn vị TKV.
- Biên gộp chỉ 2–5%.
- ROE 2025 là 7,9%, thấp hơn chi phí vốn 13,5%.
- Định giá dựa vào sổ sách và vòng đời mỏ tới 08/2045. Không có lợi thế cạnh tranh (moat) để thưởng thêm.

**Giá vừa tăng +21% so với mức 12.300 (02–04/11) lên 14.900 (+18,3% so với đóng cửa 06/11 là 12.600)**; riêng ngày 11/11 khớp 327.200 cp, khoảng 26 lần khối lượng trung vị 60 phiên. Khối lượng tăng TRƯỚC nghị quyết (03/11: 65.800 cp ≈ 5 lần; 05/11: 41.300), ngay sau công văn TKV ngày 04/11. Thời điểm trùng với Nghị quyết HĐQT ngày 06/11 về việc **ĐHĐCĐ bất thường để thông qua phương án phân phối lợi nhuận và chi trả cổ tức theo chỉ đạo của TKV**.
- Lợi nhuận các năm trước chưa phân phối còn **130,7 tỷ**, trần khoảng **3.050 đ/cp** (§6).
- Cổ tức chỉ làm **hiện thực hoá** giá trị cho cổ đông, không làm **tăng** giá trị nội tại.

**Pháp lý/quản trị:** chỉ WARNING nhẹ (§7). Không có vụ việc. Đổi công ty kiểm toán từ AASC sang PKF-TTG, nhưng cả hai đều cho ý kiến sạch.

## 1. Kiểm chứng giả thuyết

### 1a. Số Mike đã đọc, đối chiếu với bản gốc

| Số Mike đưa | Bản gốc | Kết quả |
|---|---|---|
| LNST Q3/26 −4,365 tỷ; Q3/25 −4,9 | −4,365 / −4,907 [Q3 p5] | ✅ |
| DT thuần Q3/26 1.039,2, −47,7% (Q3/25 1.987,5) | 1.039,179 / 1.987,459 [Q3 p5] | ✅ |
| LNST 9T/26 ~15,9 | 15,884 [Q3 p5] | ✅ |
| Q1 10,59; Q2 9,65 | 6T = 20,249 [6T tr.9] ⇒ Q2 = 9,66 khi Q1 = 10,59 [BQ] | ✅ |
| Dự phòng phải trả NH 333,5, trong đó 260,8 do đất bóc | 333,523; trong đó 260,811 "đất bóc không đạt hệ số kế hoạch" [Q3 p17] | ✅ (diễn giải: §2b) |
| VĐL 428,47 | 428,468 [Q3 p4] | ✅ |
| KH LNST 2026 ~36 tỷ (−28% so 2025) | Chỉ có báo chí (Thời báo Tài chính); không có NQ gốc trong `src` | ⚠️ **Lệch**: LNST 2025 kiểm toán là **82,75** [KT25 tr.8], nên 36 tương đương **−56%**, không phải −28%. Con số −28% có thể so với kế hoạch 2025 hoặc dùng LNTT (chưa kiểm) |

### 1b. Ba giả thuyết

| Giả thuyết | Bằng chứng | Kết luận |
|---|---|---|
| Doanh thu giảm gần một nửa là do sản lượng chứ không phải giá/chuyển giao | Sản lượng tiêu thụ Q3 **412.867 t so với 927.728 t (−55,5%)** [GT3]. DT/tấn **2,517 tr so với 2,142 tr (+17,5%)** (tự tính) | **ĐÚNG.** Do sản lượng; GT3 ghi "ảnh hưởng bởi điều kiện khai thác". Giá/tấn tăng chứ không giảm |
| Lãi mỏng và biến động là do dự phòng/chi phí bóc đất | Số dư dự phòng: 0 (31/12/25) → **705,8** (30/6) → **333,5** (30/9) [6T tr.10; Q3 p17]. Năm 2025 cũng tương tự: 9T/25 cộng lại 283,3 rồi về 0 cuối năm [Q3 p6; KT25 tr.7] | **NỬA ĐÚNG.** Dự phòng là bút toán dồn tích trong năm theo kế hoạch rồi quyết toán với TKV cuối năm, **không phải lỗ ẩn**. Lãi mỏng đến từ (i) sản lượng thấp, (ii) nhiên liệu +26%, (iii) xu hướng lãi định mức do TKV phân bổ giảm từ 2023 (§2) |
| Giá chuyển giao nội bộ kiểu giá vốn cộng lãi nên LN ít nhạy giá than thế giới | 97% DT bán cho đơn vị TKV [Q3 p21–22]. Hợp đồng phối hợp kinh doanh, "doanh thu, chi phí quyết toán với Tập đoàn vào cuối năm" [Q3 p8]. Biên gộp năm 5,0% (2024), 4,3% (2025), 2,2% (9T/26). Newcastle +25% so cùng kỳ [Bobby] trong khi LN CST giảm | **NỬA ĐÚNG.** Hiện tại LN tách khỏi giá than thế giới. Nhưng 2022–23 (TKV lãi lớn) LNST CST đạt **339,9 / 293,1** [BQ cộng quý], tức có độ nhạy **gián tiếp, có độ trễ, qua cách TKV phân bổ** |

## 2. Chất lượng lợi nhuận

### 2a. Kết quả kinh doanh (tỷ đồng) [Q3 p5]

| Khoản mục | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|
| DT thuần | 1.039,2 | 1.987,5 | 5.566,7 | 6.668,3 |
| LN gộp (biên) | 28,0 (2,70%) | 37,9 (1,91%) | 123,4 (2,22%) | 260,4 (3,91%) |
| DT tài chính | 2,7 | 1,5 | 8,4 | 4,6 |
| Chi phí lãi vay | 2,8 | 8,0 | 16,8 | 22,6 |
| Chi phí QLDN | 32,3 | 37,1 | 102,9 | 210,4 |
| LN thuần HĐKD | −5,0 | −6,5 | 9,6 | 29,2 |
| LN khác | −0,2 | 0,9 | 10,9 | 0,8 |
| LNST | **−4,37** | **−4,91** | **15,88** | **23,40** |

**Tách theo mảng (9T/26)** [Q3 p19]:
- Than: 5.402,2 (9T/25: 6.508,3).
- Dịch vụ: 164,5 (9T/25: 160,0).
- Thuyết minh không tách giá vốn theo mảng.

**Doanh thu tài chính 8,4** [Q3 p20]:
- Lãi tiền gửi 3,8.
- **Lãi ký quỹ môi trường 4,6**: lãi trên ký quỹ 165,6 tỷ, khoản này không rút ra được.

**Khoản một lần 9T/26:**
- Thu nhập khác 13,57 (LN khác ròng 10,93 [Q3 p5]), gồm thanh lý tài sản 6,3 và **đánh giá lại tài sản thuê hoạt động 7,0** [Q3 p20].
- Loại phần này ra, **LNTT lõi 9T ≈ 7,3 tỷ** (tự tính).
- **Chuẩn hoá một lần (đính chính skeptic):** LN khác 2024 là 38,78 tỷ trước thuế [KT25 tr.8] (khoảng 31 tỷ sau thuế) nằm trong LNST 2024 = 130,0 ⇒ LN lõi 2024 ≈ 99. LN lõi TTM ≈ 66 (75,2 gồm LN khác 9T/26 10,93).

**QLDN giảm 107 tỷ, phần lớn KHÔNG phải tiết kiệm thật:**
- Thuế, phí, lệ phí trong QLDN: 2,6 tỷ (9T/26) so với **99,5 tỷ** (9T/25) [Q3 p20–21].
- Tiền cấp quyền khai thác phân bổ đường thẳng 20 năm: chi phí 2025 là **83,6 tỷ** [KT25 tr.22]; 9T/26 vẫn phân bổ 62,7 tỷ (Q3: 20,9), số dư trả trước **260,7 tỷ** [Q3 p38] — cùng nhịp khoảng 84 tỷ/năm. Vậy QLDN giảm là do **phân loại lại khoản mục chi phí** (thuế, phí, lệ phí 99,5 → 2,6), không phải lệch thời điểm ghi nhận; LNST 2025 không bị dồn chi phí một lần. Kết luận "không phải tiết kiệm thật" vẫn đúng. *(Đã sửa theo skeptic.)*

**Nhiên liệu:**
- Chi phí nhiên liệu 9T/26 **1.350,2 tỷ so với 1.071,4 tỷ (+26,0%)**, trong khi DT giảm 16,5% [Q3 p21].
- Nhiên liệu chiếm 24,8% giá vốn 9T/26.
- GT3 quy lỗ Q3 cho "giá nhiên liệu tăng cao do tình hình Trung Đông".

### 2b. Dự phòng "đất bóc không đạt hệ số kế hoạch"

**Chính sách kế toán:**
- §16 [Q3 p13] là chính sách dự phòng chung: trích thêm vào chi phí, hoặc hoàn nhập giảm chi phí.
- **Không có** khoản mục "chi phí bóc đất đá vốn hoá" trên trả trước dài hạn. Trả trước DH 421,8 gồm tiền cấp quyền 260,7, sửa chữa lớn 57,0, tài liệu địa chất 59,5, công cụ 27,6, khác 17,0 [Q3 p38].
- Nghĩa là **không có dấu hiệu "LN hiện tại mượn của tương lai"** theo kiểu vốn hoá chi phí bóc vượt hệ số (mục #1 của Bobby).

**Cấu phần 333,5** [Q3 p17]:
- Đất bóc không đạt hệ số kế hoạch: 260,8.
- Cung độ vận tải không đạt kế hoạch: 39,5.
- Chi phí sản xuất theo kế hoạch: 33,2.

**Cơ chế** (suy luận từ dữ kiện, chưa có văn bản TKV):
- Doanh thu do TKV trả theo định mức kế hoạch, đã gồm khối lượng bóc theo hệ số kế hoạch.
- Phần bóc chưa làm được ghi trước vào chi phí dưới dạng nghĩa vụ phải trả, để chi phí khớp với doanh thu.
- Cuối năm quyết toán với TKV. Bằng chứng: số dư 0 ở cả 31/12/2024 và 31/12/2025, trong khi giữa năm lên tới 705,8.

⇒ Số dư về 0 cuối năm chỉ chứng minh quyết toán theo mùa vụ, **không chứng minh trung tính với LN**: phần quyết toán đã nằm trong LN năm lịch sử, nên không trừ riêng trong định giá (đúng), nhưng quyết toán Q4 có thể lệch **hai chiều**:
- Nếu TKV giảm trừ doanh thu nhiều hơn số đã trích, Q4 lỗ thêm.
- Nếu hoàn nhập lớn hơn phần bị giảm trừ, Q4 có lãi.
- Số dư giảm 705,8 → 333,5 (−372 tỷ trong Q3) **chưa phân tích được là sử dụng hay hoàn nhập** (việc còn mở).

**Hệ số bóc thực tế so với kế hoạch: KHÔNG CÓ SỐ trong BCTC/GT3.** Chỉ biết là "không đạt".

**Q4 quyết định cả năm** — tỷ trọng LNST Q4 trong LNST năm [BQ]:

| Năm | LNST Q4 | Tỷ trọng cả năm |
|---|---|---|
| 2023 | 179,9 | 61% |
| 2024 | 6,7 | 5% |
| 2025 | 59,4 | 72% |

### 2c. Xu hướng nhiều năm (LNST, tỷ đồng)

| Năm | LNST | Nguồn | Ghi chú |
|---|---|---|---|
| 2021 | 106,6 | BQ | |
| 2022 | 339,9 | BQ | |
| 2023 | 293,1 | BQ | |
| 2024 | **130,0** | KT25 | BQ cộng 4 quý ra 139,7, lệch 9,7 tỷ (có thể do điều chỉnh quyết toán); dùng KT25 |
| 2025 | **82,7** | KT25 | |
| TTM Q3/26 | 75,2 | Q4/25 59,35 + 9T/26 15,88 | |

- ROE 2025 = 82,7 / VCSH bình quân 1.049 = **7,9%** (tự tính).
- ROE_Min5Y = 7,8% [BQ].

### 2d. Độ nhạy (mục #11 của Bobby)

- **Nhiên liệu ±10%** ⇒ ±135 tỷ trên nền 9T (theo năm khoảng ±180 tỷ, ước lượng), tức khoảng **2,4 lần LNST TTM**.
  - LN chưa sụp dù nhiên liệu +26% ⇒ phần lớn chi phí **được TKV chuyển giá qua đơn giá/quyết toán** (gián tiếp).
  - Biên 9T giảm 1,7 điểm %, tương đương phần chuyển giá còn thiếu khoảng 95 tỷ trên nền 9T (ước lượng).
- **Hệ số bóc ±0,5 m³/t:** không có số.
- **Sản lượng ±10%:** LN gần như không theo tỷ lệ, vì là lãi định mức. Không có công thức đơn giá để lượng hoá.

## 3. Bảng cân đối và dòng tiền (tỷ đồng) [Q3 p3–4, p6; KT25 tr.6–9]

| Khoản mục | 30/09/26 | 31/12/25 |
|---|---|---|
| Tiền và tương đương | 195,9 | 1,9 |
| Vay (30/9: toàn bộ dài hạn; 31/12/25: ngắn hạn 79,2 + dài hạn 405,9) | 129,5 | 485,1 |
| **Tiền ròng (net cash)** | **+66,4** | **−483,2** |
| Phải thu khách hàng | 360,4 | 327,0 |
| – trong đó các đơn vị TKV | 337,9 (Tuyển than Cửa Ông 233,0; Kho vận & Cảng Cẩm Phả 104,8) | 309,1 |
| Tồn kho | 296,7 | 692,7 |
| – thành phẩm | 11,7 | 304,5 |
| – sản phẩm dở dang | 220,8 | 337,5 |
| Dự phòng phải trả NH | 333,5 | 0 |
| Chi phí phải trả | 104,9 (thuê băng tải đất đá 85,4; phí thương hiệu TKV 19,1) | 0,5 |
| VCSH | 961,3 | 1.028,2 |
| – LNST chưa phân phối | 146,5 | 213,4 |

- **Tiền ròng mang tính mùa vụ.** Nó đảo từ −483 lên +66 nhờ xả tồn kho 396 và dự phòng 333,5. Cả hai khoản sẽ đảo chiều khi quyết toán Q4.
  - **Không đủ cơ sở để ước "tiền ròng thật" cuối năm**: hai điểm cuối năm có sẵn là −483 (2025) và +545 (2024: tiền 800,4 − vay 255,4), biến động rất lớn theo chu kỳ đầu tư và quyết toán. *(Đã bỏ ước −200..−400 theo skeptic.)*
- **Ký quỹ môi trường:** gốc 165,6 + lãi 46,6 = **212,2 tỷ**, phải thu dài hạn từ Quỹ BVMT Quảng Ninh, cho 2 dự án Khe Chàm II và mở rộng Cao Sơn [Q3 p25; KT25 tr.18]. Đây là tài sản bị phong toả cho phục hồi môi trường, không phải tiền tự do.
- **Thuê ngoài bảng:** tài sản đi thuê 131,8 tỷ, kỳ hạn 1–5 năm [Q3 p19].

**CFO 4 quý gần nhất:**

| Quý | CFO | Nguồn |
|---|---|---|
| Q4/25 | 56,3 | KT25 169,9 − 9T/25 113,6 |
| Q1/26 | 101,0 | BQ (PDF Q1 chưa render) |
| Q2/26 | 284,9 | 6T 385,9 − Q1 |
| Q3/26 | 197,4 | 9T 583,3 − 6T |
| **Cộng** | **639,6** | |

- Con số này bị thổi phồng bởi dự phòng 333,5 (sẽ đảo chiều) và xả tồn kho 396.
- CFO năm: **289,6 (2024), 169,9 (2025)** [KT25 tr.9].

**Capex:**
- 276,1 (2024), **359,2** (2025), **chỉ 13,9 trong 9T/26** so với 320,3 cùng kỳ.
- Đầu tư gần như dừng trong 2026. Chưa rõ là hoãn hay dự án đã qua giai đoạn mua sắm chính.

**Dự án mở rộng mỏ Cao Sơn:**
- Tổng mức đầu tư **1.829,5 tỷ** (vay 70%), triển khai từ 09/2023 [KT25 tr.19].
- XDCBDD còn 104,0 [Q3 p4].
- Phần còn phải chi **không có số**.
- Theo luật NPV = 0, phần còn phải chi được đối ứng bằng giá trị tương đương, không trừ vào base.

## 4. Giá chuyển giao và mức phụ thuộc TKV

- **Hợp đồng phối hợp kinh doanh với TKV:** "cùng phối hợp khai thác, chế biến và tiêu thụ than; doanh thu, chi phí quyết toán với Tập đoàn cuối năm" [Q3 p8].
- **Bán hàng:** bán cho các đơn vị TKV **5.410,8 / 5.566,7 = 97,2%** DT 9T/26. Gồm Tuyển than Cửa Ông 4.078,8 và Kho vận & Cảng Cẩm Phả 1.323,4 [Q3 p21–22].
- **Mua hàng:** từ tập đoàn 1.872,5, gồm Vật tư TKV 1.413,7 và Hoá chất mỏ Cẩm Phả 296,6.
- **Phí thương hiệu TKV:** 19,1 phải trả.
- Công thức đơn giá, tỷ lệ lãi định mức và độ trễ điều chỉnh: **KHÔNG công bố**.
- Năm 2025 có thêm giao dịch vận chuyển đất đá bằng băng tải với CTCP Tân Phú Xuân (40,87% tổng tài sản) [KT25 tr.2].
- **Kết luận:** CST là đơn vị gia công phụ thuộc gần như hoàn toàn. Không có quyền định giá, không có khách hàng ngoài tập đoàn đáng kể (DT ngoài TKV khoảng 2,8%).

## 5. Quyền khai thác, trữ lượng, đồng hồ cắt hào, thuế phí

- **Giấy phép khai thác số 280/GP-BTNMT ngày 07/08/2023**, công suất thiết kế **4,5 triệu t/năm**, trữ lượng nguyên khai dự kiến khai thác **65,99 triệu t**, hoạt động **tới 08/2045** [KT25 tr.19].
  - 65,99 triệu t là trữ lượng tại thời điểm cấp phép (2023); phần đã khai thác 2023–2026 chưa trừ, nên "đủ ~18 năm ở 3,7 triệu t/năm" chỉ là thứ tự độ lớn (ước lượng), không phải trữ lượng còn lại.
  - Q3/26 tiêu thụ 0,41 triệu t (quy năm 1,65 triệu t/năm) — **chỉ là MỘT quý mùa mưa, quý thấp theo mùa** (DT Q3 cũng thấp cả 2024 lẫn 2025 [BQ]); DT 9T/26 chỉ giảm −16,5%. Sản lượng giảm vì "điều kiện khai thác" [GT3], không phải thiếu cầu: TKV đang cần than (Bobby: tiêu thụ 10T +20%, NQ28 cho khai thác vượt công suất).
- **Tiền cấp quyền khai thác:** thông báo 2025 **226,3 tỷ**, gồm cả phần bổ sung do điều chỉnh đơn giá. Phân bổ đều 20 năm; chi phí 2025 là 83,6 tỷ [KT25 tr.22]. Số dư trả trước 30/9/26 là 260,7 [Q3 p38].
- **Chi phí thăm dò hoàn trả Nhà nước:** 69,3 tỷ, phân bổ tới 2045 [KT25 tr.22].
- **Lực thứ 6 (đồng hồ cắt hào):**
  - (i) Quy hoạch Quảng Ninh đóng dần mỏ lộ thiên tới 2030 [Bobby]. Nhưng Cao Sơn vừa được cấp giấy phép tới 2045 cho dự án mở rộng, nên **base dùng 2045**. Rủi ro đóng sớm đưa vào độ nhạy (đóng 2030 ⇒ tâm 12.033, −8%; vì ROE < r nên đóng sớm và thu hồi sổ sách gần như không làm mất giá trị).
  - (ii) Đề án tái cơ cấu TKV phải xong trước 27/11/2026: có thể hợp nhất hoặc hoán đổi công ty con [Bobby F9 P = 0,20].
  - (iii) Moong càng sâu thì hệ số bóc càng tăng (cấu trúc).
- **Thuế tài nguyên/phí BVMT:** chi tiết thuế ở trang 43–46 bản Q3, chưa đọc kỹ. **Chưa có số thuế suất.** Không thấy kết luận thanh tra hay truy thu trong BCTC.

## 6. Cổ đông, ĐHĐCĐ bất thường, nhân sự, cổ tức, thanh khoản

**Cổ đông:**
- TKV nắm **27.909.807 cp = 65,14%**, người đại diện vốn là ông Vũ Văn Khẩn (Chủ tịch HĐQT). Đây là cổ đông lớn duy nhất (chốt 27/05/2026) [src/Danh-sach-co-dong…].
- Free float tối đa 34,86%.
- Room ngoại: **chưa kiểm**.

**ĐHĐCĐ bất thường 2026** (NQ HĐQT 40/NQ-TCS-HĐQT và TB 8923, cùng ngày 06/11/2026) [src/vi-nghiquyet…; tb-ve-ngay-dkcc…]:
- Ngày 06/11 là ngày **ra nghị quyết triệu tập**, chưa phải ngày họp.
- Ngày chốt danh sách: **30/11/2026**. Ngày họp: **20–30/12/2026**.
- Nội dung: **"Thông qua phương án phân phối lợi nhuận và chi trả cổ tức"**, kế toán trưởng hoàn thiện **"theo chỉ đạo của TKV tại công văn 7788/TKV-KSNB ngày 04/11/2026"**. Tỷ lệ chưa công bố.
- **Quỹ có thể chia:**
  - LNST chưa phân phối cuối 2025 = 213,4, gồm 130,7 các năm trước và 82,7 năm 2025 [KT25 tr.7].
  - Sau ĐHĐCĐ 2026, số đã phân phối là 213,4 + 15,9 − 146,5 = **82,8**, đúng bằng LN 2025, trong đó cổ tức 700 đ/cp tương đương 29,9 tỷ [Q3 p6].
  - ⇒ **130,7 tỷ của các năm trước vẫn chưa phân phối, trần khoảng 3.050 đ/cp** (tự tính; nếu chia cả LN 9T/26 thì trần 3.420). Cổ tức tiền thực tế thấp hơn trần vì còn trích quỹ khen thưởng phúc lợi. Mô hình không double-count: B₀ đã chứa khoản này và cổ tức trung tính với giá trị nội tại.
  - Ràng buộc tiền: tiền 195,9 tại 30/9, nhưng cuối năm theo mùa vụ thường thấp (1,9 tại 31/12/25). Chia hết 130,7 có thể cần vay.
  - Khả năng TKV yêu cầu chia tối đa (chính sách thu hồi vốn nhà nước): **không có số**, chỉ có tiêu đề nội dung.
- **Tác động định giá:** cổ tức đặc biệt trung tính với giá trị nội tại (VCSH giảm đúng bằng tiền nhận), chỉ hiện thực hoá giá trị. Giá đã tăng 21% từ 06/11 ⇒ **thị trường đang định giá kỳ vọng cổ tức**.

**Nhân sự:**
- 22/06/2026: **bổ nhiệm lại** bà Đào Thị My làm Người phụ trách kiểm toán nội bộ, 5 năm, từ 01/07/2026 (QĐ 4711) [src/VI_thongbaothaydoinhansu.pdf]. Đây là việc thường lệ.
- **Thay đổi ngày 25/09: không có file gốc trong `src`, CHƯA KIỂM.** Bằng chứng gián tiếp trong BCTC Q3 [p22]: Kế toán trưởng Lương Xuân Quang mới bổ nhiệm (thù lao năm trước 7,0 tr so với 287,6 tr), PGĐ Vũ Quang Dũng mới trong 2026, TV HĐQT độc lập Phạm Hồng Lương 17,5 → 162,9 tr.
- Từ 6T/2026, người ký BCTC thay Giám đốc là Phó GĐ Nguyễn Ngọc Dũng; Q3 do Giám đốc Phạm Quốc Việt ký.

**Đổi GCN ĐKDN:**
- 10/09/2026: chỉ đổi địa chỉ theo sắp xếp hành chính (NQ 36/2026/QH16 thành lập TP Quảng Ninh) [src/VI_thongbaothaydoigiaychungnhan.pdf].
- Lần đổi 16/07: không có trong `src`.

**Kiểm toán:** HĐ kiểm toán/soát xét 2026 ký với **PKF-TTG** ngày 14/07/2026, thay AASC (kiểm toán 2025) [src/VI_CBTTkhac.pdf].

**Lịch sử cổ tức tiền** [BQ Dividend_1Y, theo năm chi]: 1.200 (2021), 1.500 (2022–23), 2.000 (2024), 1.000 (2025), 700 (2026).
- Tỷ lệ chi trả trên LN 2025 là 36% (29,9/82,7).

**Thanh khoản** (khối lượng thật [BQ], `calc/px_cst.csv`):

| Chỉ tiêu | Giá trị |
|---|---|
| KL trung vị 60 phiên | **12.600 cp/phiên** |
| ADV60 (giá trị trung vị) | **0,132 tỷ** |
| ADV250 | 0,199 tỷ |
| σ ngày | 2,04% |
| Phiên KL = 0 kể từ 06/2025 | 1 |

| Cỡ vị thế | Chiết khấu thanh khoản (ADV60) | Số phiên thoát @10–20% ADV60 |
|---|---|---|
| 1,0 tỷ | 5,6% | **38–76** |
| 0,3 tỷ | 3,1% | **11–23** |
| 0,1 tỷ | 1,8% | 4–8 |

- Chiết khấu tính theo σ√(Q/ADV), cùng phương pháp dd_VGS r2.
- **Sizing: tối đa khoảng 0,1–0,3 tỷ.** Cỡ 1 tỷ không thoát được trong vòng một tháng.
- Đợt tăng khối lượng tháng 11 (trung vị tháng 64.300) là bất thường, không nên dùng làm nền thanh khoản.

## 7. Pháp lý và quản trị — chỉ WARNING

- ⚠️ **Tái cơ cấu TKV 2026–2030** (dự thảo trước 27/11/2026): khả năng sáp nhập hoặc hoán đổi; tỷ lệ hoán đổi là rủi ro hoặc lợi ích cho cổ đông thiểu số [Bobby].
- ⚠️ **Giao dịch bên liên quan chiếm phần lớn** DT/chi phí; công thức giá không công bố (§4).
- ⚠️ **Đổi kiểm toán** AASC → PKF-TTG giữa chu kỳ. Ý kiến cả hai sạch: KT25 chấp nhận toàn phần (tr.5), 6T kết luận chấp nhận toàn phần (tr.6).
- ⚠️ Dòng 17 LCTT 9T in **+45,07** ("tiền chi khác cho HĐKD") — dấu bất thường [Q3 p6], cần hỏi.
- ⚠️ Môi trường/bãi thải: ký quỹ 212 tỷ. Chưa thấy xử phạt trong tài liệu đã đọc. **Chưa tra** UBCKNN/HNX/báo chí về vụ việc.
- Không có vụ án, khởi tố hay xử phạt nào trong tài liệu đã đọc.

## 8. Định giá — mù giá thị trường; tâm do mô hình quyết, không theo giá

**Khung:** thu nhập thặng dư (residual income) hữu hạn tới 2045, theo đề xuất của Bobby về vòng đời mỏ hữu hạn, không dùng g vĩnh viễn.
- V = B₀ + Σ(N − r·B₀)/(1+r)^t + phần thu hồi sổ sách cuối kỳ.
- B₀ = **961,3** (VCSH 30/9/26).
- T = 19 năm (GP 280).
- Thu hồi 50% sổ sách khi đóng mỏ (ước lượng).
- g = 0.

**Chi phí vốn:**
- **r = 13,5%** = điểm neo, vì lãi huy động 12 tháng `effective_deposit_rate('2026-11-11')` = **7,40%** (cctg_12m ngày 02/11; Big-4 6,8%), đúng bằng mức neo. β = 1.
- r = 13,5% có thể quá cao cho một đơn vị kiểu giá vốn cộng lãi có β thấp. Với r = 12%, tâm là 14.497.

**Kịch bản** (trọng số chủ quan, ước lượng):

| Kịch bản | Trọng số | LN chuẩn hoá N (tỷ/năm) | Cơ sở dữ liệu | Giá trị/cp | Sau CK 0,3 tỷ |
|---|---|---|---|---|---|
| Bi quan | 30% | 35 | KH 2026 ~36 (báo chí) | 6.517 | 6.316 |
| Cơ sở | 45% | 75 | LNST TTM 75,2 [Q3 + KT25] | 12.808 | 12.414 |
| Lạc quan | 25% | 130 | LNST 2024 kiểm toán 130,0 = trung vị năm 2023–25 | 21.460 | 20.799 |
| **Tâm** | | | | **13.084** | **12.681** |

**Chuẩn hoá một lần và điểm yếu nhất của định giá (skeptic 11/11, Mike tái tính):**
- N cơ sở 75,2 gồm LN khác 9T/26 10,93; N lạc quan 130 = LNST 2024 gồm khoảng 31 tỷ sau thuế là một lần. Tính trên LN lõi (35 / 66,5 / 99) thì **tâm ≈ 11.263** (nhãn "trên tâm" mạnh hơn).
- **Giá 14.900 tương đương N chuẩn hoá ≈ 88 tỷ/năm trong 19 năm** (≈ 91 sau chiết khấu thanh khoản).
- **GIẢ ĐỊNH QUYẾT ĐỊNH:** base lấy TTM gần đáy (75) và coi "suy giảm cấu trúc" (hệ số bóc tăng, TKV nén lãi định mức, đóng lộ thiên QN 2030 — Bobby STRUCTURAL 0,55 tầm 3–5 năm). Nếu N theo chu kỳ trừ đỉnh 2022–23 (trung bình 2021/24/25 ≈ 106) thì tâm ≈ **15.300–17.700, giá nằm DƯỚI tâm — nhãn đảo chiều**. Chưa có số đơn giá/định mức TKV để kiểm luận điểm này.
- N bi quan (30% trọng số) dựa trên kế hoạch ~36 tỷ chỉ có từ báo chí (chưa có NQ ĐHĐCĐ thường niên gốc).

**Các khoản trừ/không trừ trong base:**
- Không có khoản giảm trừ nào ngoài thu hồi sổ sách 50% (ước lượng; cơ sở: TSCĐ nguyên giá 4.657, hao mòn 4.044, tức đã khấu hao 87% [Q3 p4]).
- Dự án mở rộng: NPV = 0, không trừ.
- Dự phòng 333,5: trung tính (§2b), không trừ.

**Độ nhạy theo lãi huy động** (tâm trước CK, so với 13.084):

| Δ lãi huy động | β = 1 | β = 0,5 |
|---|---|---|
| −100bp | 13.998 (+7,0%) | 13.528 (+3,4%) |
| −50bp | 13.528 (+3,4%) | 13.303 (+1,7%) |
| +50bp | 12.664 (−3,2%) | 12.871 (−1,6%) |
| +100bp | 12.267 (−6,2%) | 12.664 (−3,2%) |

**Độ nhạy khác (tâm trước CK):**
- Thu hồi sổ sách 100% ⇒ 14.095; 0% ⇒ 12.072.
- Đóng mỏ 2030 ⇒ 12.033.

**Đối chiếu bội số:**
- Tại giá 14.900: **P/B 0,66**, PE TTM 8,5.
- Tâm tương đương P/B 0,58 và PE TTM khoảng 7,5.

**Comp TKV** [BQ, giá 11/11; BVPS và LN TTM mới nhất]:

| Mã | Loại mỏ | P/B | PE TTM | ROE5Y |
|---|---|---|---|---|
| THT (Hà Tu) | Lộ thiên | 0,53 | 2,5 | 13,0% |
| NBC | | 0,61 | 5,2 | 11,1% |
| MDC | | 0,65 | 9,5 | 18,4% |
| TVD | | 0,67 | 5,7 | 18,5% |
| HLC | | 0,69 | 18,3 | 20,1% |
| CST | Lộ thiên | 0,66 | 8,5 | 19,3% |

- Bổ sung (skeptic): **MVB (Mỏ Việt Bắc)** P/B 0,68, PE 14,9 [BQ]. Thêm MVB: trung vị PE 5,7 → 7,6; P/B trung vị nhóm ≈ 0,66.
- CST tại giá hiện tại ngang P/B nhóm; PE (8,5) chỉ **nhỉnh hơn nhẹ trung vị 7,6** (không còn "cao hơn rõ") dù LN đang giảm.
- TC6 và TDN (lộ thiên) không có trong BQ, nên không dùng.

**Hai nền giá trị** (chỉ hiển thị, không đổi tâm):

| Nền | Cách tính | Giá trị/cp |
|---|---|---|
| V_ngắn | LN chuẩn hoá 75,2 (trung vị TTM 3 năm: 312,9 / 30,1 / 75,2) × (1 − g/ROE; g = 0) / r | **13.001** |
| V_dài | FCFE trung bình 2024–25 (84,8; 43,6 = CFO − capex + thanh lý + vay ròng [KT25]) / r | **11.098** |
| D | \|ln(V_ngắn/V_dài)\| = 0,16 < ln2 | Không có cờ phân kỳ |

- FCFE > 0; cổng CFO đạt (CFO 3 năm 712,4 [2023 = 252,9 lấy từ BQ; 2024–25 từ KT25] > LNST 3 năm 505,8).
- Lưu ý: V_dài dùng công thức vĩnh viễn g = 0, không phải vòng đời hữu hạn — chỉ để hiển thị theo skill.
- **Dòng C4** (CFO3 − min(capex, khấu hao) = 237,5 − 256,7 = **−19 tỷ/năm**): âm ⇒ không ra giá trị. Lưu ý: trộn cửa sổ thời gian (CFO 3 năm, khấu hao 2 năm, capex 2023 lấy CFI từ BQ) và khấu hao đang giảm (9T/26 chỉ 113,5) nên dấu C4 dễ đổi. Nhãn "chưa qua tiêu chí khoá trước, chỉ theo dõi".
- **Dòng D2** (CFO3 − ~4,8% × DT; tỷ lệ capex/DT trung vị peer HLC/MDC/NBC/THT/TVD 2023–25 từ `calc/peer_capex.csv`: skeptic tái lập ra 4,43% / 4,87% / 4,94% tuỳ cách gộp, không đúng 4,83%; cột dùng là CFI ròng chứ không phải capex thuần; dấu kết quả không đổi) ≈ 237,5 − 415,6 = **−178 tỷ/năm**: âm ⇒ không ra giá trị. D2 không hợp với mô hình giá vốn cộng lãi, nơi DT rất lớn so với biên. Nhãn "chưa qua tiêu chí khoá trước, chỉ theo dõi".

**Vùng giá** (sau chiết khấu thanh khoản 0,3 tỷ):

| Mốc | Giá |
|---|---|
| P10 ≈ bi quan | 6.316 |
| Tâm | **12.681** |
| P90 ≈ lạc quan | 20.799 |
| Ngưỡng luật 0,85×tâm | **10.779** |

**Giá 14.900: TRONG vùng, trên tâm 17,5% ⇒ không có biên an toàn.**

## 9. Vị thế và lợi thế cạnh tranh (5F tầng b) — lần đầu, chưa có trong `data/moat_tags.csv`

**Loại hình doanh nghiệp:** đơn vị khai thác gia công cho công ty mẹ độc quyền hành chính (TKV), bán theo giá vốn cộng lãi định mức.

| Lực | Đánh giá | Bằng chứng |
|---|---|---|
| Người mua | **Rất mạnh** | 97,2% DT từ đơn vị TKV, giá do TKV quyết toán (§4) |
| Nhà cung cấp | Mạnh | 1.413,7 vật tư mua từ Vật tư TKV; nhiên liệu 24,8% giá vốn, giá thị trường |
| Đối thủ / gia nhập | Thấp | Giấy phép antraxit nằm trong tay TKV [Bobby]. Nhưng rào cản thuộc về **tập đoàn**, không thuộc CST |
| Sản phẩm thay thế | Trung bình | Than nhập pha trộn >60 triệu t/năm [Bobby]; điện than giữ vai trò tới 2030+ |
| Lực thứ 6 | Có đồng hồ | Giấy phép 2045, quy hoạch đóng lộ thiên Quảng Ninh, tái cơ cấu TKV |

- **moat_tier = NONE**; moat_type = ADMIN/LICENSE (thuộc TKV, không thuộc CST).
- Bằng chứng định lượng:
  - Biên gộp 2,2–5,0% (2024–9T/26).
  - ROE 2025 7,9%, ROE_Min5Y 7,8% < Ke 13,5%.
  - ROE5Y 19,3% / ROIC5Y 17,9% [BQ] chỉ cao nhờ đỉnh 2022–23 (LNST 340/293), không qua điều kiện (i) "nhiều chu kỳ".
- **Rủi ro số 1:** lãi định mức do TKV phân bổ có thể tiếp tục bị nén (sản lượng giảm vì điều kiện khai thác, hệ số bóc tăng), kèm tái cơ cấu TKV quyết định số phận pháp nhân.
- **Tham số moat trong mô hình:** KHÔNG thêm (NONE). KHÔNG trừ: không ép N về Ke; kịch bản lạc quan vẫn giữ N = 130.
- **Độ nhạy theo moat:**
  - NONE và NARROW cho cùng giá trị (không thưởng).
  - WIDE giả định (RONIC > Ke, N giữ 130) ⇒ khoảng 21.460 = kịch bản lạc quan. Không có cơ sở để dùng.
- **ĐỀ XUẤT dòng `data/moat_tags.csv`** (human-curated, KHÔNG tự sửa file):
  `CST,NONE,ADMIN/CONTRACT-MINER,—,"Cost-plus contract miner for TKV (97% rev intra-group, GPM 2-5%, ROE 2025 7.9%<Ke); licence 280/GP to 2045 but barrier belongs to TKV; risks: TKV-allocated margin compression + TKV 2026-30 restructuring (merger/swap) + QN open-pit closure policy",2026-11-11,dd_CST_20261111,N`

## 10. Mốc khoá trước và điều kiện đổi nhận định (cả hai chiều)

**Các mốc:**

| # | Mốc | Ngày | Tốt hơn (nâng) | Xấu hơn (hạ) |
|---|---|---|---|---|
| M1 | BCTC Q4/2026: LNST cả năm 2026 | ~20/01/2027 | ≥ 100 tỷ (Q4 ≥ 84) và dự phòng 31/12 = 0 ⇒ dời trọng số sang lạc quan; 55–100 ⇒ base xác nhận | **≤ 55 tỷ (trung điểm bi quan 35 / cơ sở 75)** hoặc dự phòng không về 0 / TKV giảm trừ DT ⇒ dời trọng số sang bi quan; < 15 (Q4 lỗ) ⇒ bi quan mạnh |
| M2 | ĐHĐCĐ bất thường: cổ tức | 20–30/12/2026 | Chia ≥ 2.000 đ/cp tiền mặt mà không vay thêm ⇒ hiện thực hoá giá trị, xác nhận TKV thu hồi vốn đều | ≤ 700 đ/cp hoặc trả bằng cổ phiếu ⇒ kỳ vọng hiện tại sai (tác động giá, không đổi giá trị nội tại) |
| M3 | Đề án tái cơ cấu TKV | dự thảo trước 27/11/2026, công bố trong 12 tháng | Giá trị quy đổi/cp của phương án hoán đổi > **1,15×tâm (≈15.050 trước CK)** | Giá trị quy đổi/cp < **0,85×tâm (≈11.120 trước CK)** hoặc giải thể/đóng mỏ trước 2035 *(neo lại theo tâm, đối xứng; đính chính skeptic — bản trước dùng 0,6×BVPS = 13.462 > tâm, tự mâu thuẫn)* |
| M4 | Sản lượng tiêu thụ | Q4/26, Q1/27 | Về ≥ 0,9 triệu t/quý | Tiếp tục < 0,5 triệu t/quý |

**Điều kiện đổi nhận định:**
- **Chiều lên (đáng quan tâm):** giá ≤ **10.779** (0,85×tâm sau CK), HOẶC LNST 2026 ≥ 100 tỷ với CFO ≥ LNST và dự phòng về 0. Khi đó dời trọng số kịch bản và tính lại tâm.
- **Chiều xuống:** LNST 2026 < 15 tỷ, HOẶC có lịch đóng mỏ Cao Sơn trước 2035, HOẶC TKV giảm trừ DT cuối năm lớn hơn số đã trích dự phòng.

## 11. Bối cảnh vĩ mô — chỉ hiển thị, không đổi giá trị

Snapshot `macro_snapshot_20261111.md`, chỉ trích các dòng có cờ ok:
- SX công nghiệp +15,0% so cùng kỳ (T10).
- GDP Q3 +9,95%.
- CPI 5,09%.
- LNH 3M 7,00% (+0,68 điểm % trong 12 tháng).
- USD/VND −2,72% trong 12 tháng.

Ngành theo đọc mù của Bobby:
- Cầu than mạnh: TKV tiêu thụ 10T 44,06 triệu t (+20%); El Niño 2026–27; NQ28 cho phép khai thác vượt ≤ 15% công suất tới 2027.
- Diesel 28.696 đ/l (đã giảm 2 kỳ đầu T11).

**Điều thị trường có thể chưa tính** (chỉ là quan sát, không đưa vào giá trị):
- Nếu Hormuz bình thường hoá, nhiên liệu (24,8% giá vốn) giảm trong 2–3 quý tới, nới biên.
- CST lại đang hụt sản lượng vì "điều kiện khai thác" trong lúc TKV thiếu than. Đây là vấn đề riêng của mỏ, không phải của cầu.

## Phụ lục A — Nguồn từng số

**Q3** (`src_q3/000000016954303…pdf`; ảnh `img_q3/vi_pNN.png`):
- p3–4: bảng cân đối.
- p5: kết quả kinh doanh.
- p6: lưu chuyển tiền tệ 9T.
- p8: §I.5 hợp đồng phối hợp kinh doanh.
- p13: chính sách dự phòng.
- p16–17: tiền, tồn kho, vay, chi phí phải trả, dự phòng 25a.
- p19–21: doanh thu, chi phí theo yếu tố, nhiên liệu, thuế phí.
- p21–24: bên liên quan và phải thu TKV.
- p25: ký quỹ môi trường.
- p38: trả trước dài hạn.

**GT3:** `img_q3/gt_p01.png`, `gt_p02.png` — sản lượng 412.867 t so với 927.728 t.

**6T:** tr.6 (kết luận soát xét), tr.9 (KQKD 6T), tr.10 (LCTT 6T: dự phòng 705,8; CFO 385,9).

**KT25:**
- tr.2: giao dịch ≥ 35% tổng tài sản.
- tr.5: ý kiến AASC.
- tr.6–7: bảng cân đối.
- tr.8: KQKD (2025: 82,75; 2024: 130,02).
- tr.9: LCTT.
- tr.11: số lao động 3.188.
- tr.18: ký quỹ môi trường.
- tr.19: dự án mở rộng, giấy phép 280/GP, 2045, trữ lượng 65,99 triệu t.
- tr.22: tiền cấp quyền 226,3; phân bổ 83,6.

**CBTT** (`src/`): NQ 40/NQ-TCS-HĐQT; TB 8923 (ĐHĐCĐ bất thường); TB 4712/QĐ 4711 (nhân sự 22/06); CBTT 5440 (PKF-TTG); TB 7098 (GCN 10/09); danh sách cổ đông lớn 04/09.

**BQ:**
- `ticker_financial` CST 2020Q4–2026Q3 (LNST quý; ROE5Y/ROE_Min5Y/ROIC5Y; Dividend_1Y).
- Peer P/B, PE (truy vấn trong phiên).
- `calc/peer_capex.csv`, `calc/px_cst.csv`.

**Báo chí:**
- KH 2026 ~36 tỷ: https://thoibaotaichinhvietnam.vn/than-cao-son-tkv-dat-muc-tieu-loi-nhuan-2026-chi-hon-36-ty-dong-188807.html (chưa có NQ gốc).
- Đối chiếu: https://vnbusiness.vn/lai-chua-day-16-ty-dong-than-cao-son-xuat-hien-khoan-du-phong-hon-333-ty-dong.html

**Lãi huy động:** `deposit_rate_vn.effective_deposit_rate('2026-11-11')` = 7,40%.

## Phụ lục B — Chưa làm / giới hạn

- **Chưa kiểm:**
  - Room ngoại.
  - Thay đổi nhân sự 25/09 và GCN 16/07 (không có file gốc).
  - Thuế suất tài nguyên (trang 43–46 bản Q3).
  - Hệ số bóc thực tế so với kế hoạch (không công bố).
  - Công thức đơn giá TKV.
  - PDF Q1/2026 (CFO Q1 lấy từ BQ).
- Kịch bản bi quan dùng KH 36 tỷ từ báo chí; tỷ lệ "−28%" mâu thuẫn với số kiểm toán (§1a).
- Trọng số kịch bản 30/45/25 là chủ quan (ước lượng).
- Skeptic đã chạy (xem Phụ lục E). Sổ vùng giá ghi với `assumptions_md5` = md5 của `calc/assumptions.json`.

## Phụ lục E — Phản biện fundamental-skeptic 11/11/2026 và đính chính đã áp

**Kết quả: REFUTED mức văn bản (medium); nhãn định giá "giá 14.900 trên tâm, không biên an toàn" ĐỨNG.** Skeptic tái lập mô hình ra đúng 6.517 / 12.808 / 21.460, tâm 13.084, sau CK 12.681; >20 số khớp ảnh gốc BCTC/GT3/NQ/KT25.

Đã sửa: (1) §10 M1 và M3 đối xứng; (2) chuẩn hoá một lần + dòng "giá ⇔ N≈88" + độ nhạy N chu kỳ (nhãn đảo nếu N≈106); (3) cơ chế tiền cấp quyền (phân bổ ~84/năm cả hai năm); (4) dự phòng "trung tính" → "đã nằm trong LN năm, quyết toán lệch hai chiều" + việc mở −372 tỷ Q3; (5) LN khác 13,57 thu nhập khác / 10,93 ròng; (6) vay 31/12/25 gồm ngắn hạn 79,2; (7) bỏ ước "tiền ròng thật −200..−400"; (8) mốc giá +21%/+18,3% và khối lượng tăng trước NQ; (9) sản lượng quy năm Q3 mùa vụ + trữ lượng 65,99 là tại 2023; (10) trần cổ tức 3.050 (3.420 nếu gồm 9T) và quỹ phúc lợi; (11) D2 tỷ lệ không tái lập; (12) C4 trộn cửa sổ; (13) thêm MVB vào comp; (14) nhân sự có bằng chứng gián tiếp trong Q3 p22.

**Còn mở (không chặn kết luận):** NQ ĐHĐCĐ thường niên 2026 gốc (kế hoạch 36 tỷ chỉ từ báo chí; mâu thuẫn −28%/−56%); phân tích −372 tỷ dự phòng Q3; nhân sự 25/09; room ngoại; thuế tài nguyên; tra pháp lý bên ngoài; tiền lệ hợp nhất mỏ lộ thiên TKV cho M3 (không khẳng định).
