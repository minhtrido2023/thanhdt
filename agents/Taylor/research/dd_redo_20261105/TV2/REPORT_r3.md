# TV2 (PECC2) — DD redo VÒNG 3 · giá đóng cửa 06/11/2026 · job `Taylor_20261108_142016`

> Chỉ nghiên cứu, trung dung. Pháp lý/quản trị = WARNING, ngoài tâm. Không đặt lệnh, không sửa `kb/dd_price_zones.json`.
> - Áp đính chính fundamental-skeptic 08/11 (`../TOP5_CORRECTIONS_20261108.md` mục TV2). Mỗi điểm được kiểm lại bằng calc, không chép.
> - Số: `calc_r3/model_tv2_r3_out.txt|json`. Chạy lại: `$DNA_PYEXE -I calc_r3/model_tv2_r3.py`. Chạy 2 lần, md5 trùng byte: json `ad2f217e…`, txt `c4346951…`, LOCK `94e22037…`.
> - `SUMMARY.json` sinh bằng `calc_r3/make_summary_r3.py` (2 lần trùng byte, md5 `d5c91d04…`). Bản cũ lưu ở `SUMMARY_r2.json`.
> - Khoá upstream: `calc_r3/LOCK_r3_md5.txt` (17 file: engine, giá BQ 04/11 + 06/11 cùng SQL, lịch sử BQ cùng SQL, lãi huy động, PDF BCTC Q3, script).
> - Control: chạy hàm r2 trên giá 04/11 ra đúng tâm 15.832, P10 2.726 (assert trong script).
> - REPORT_r2 vẫn hiệu lực cho §8 (và các phần không nêu lại ở đây). **§2–§4 của r3 THAY THẾ §2–§4 của r2** (không đọc song song).

## 0. Kết luận

| Sau CK 2,52% @5 tỷ | r3 (headline B) | r2 |
|---|---|---|
| **Tâm** (kỳ vọng lưới) | **17.491** | 15.832 |
| P50 kết cục | 16.019 | 15.843 |
| Giá trị tại tham số trung tâm (177,5 · g4 · CMC 0% · bền) | 18.981 | 18.883 |
| **P10 / P90 kết cục** | **7.702 / 30.677** | 2.726 / 30.675 |
| min / max kết cục (n = 324) | 2.769 / 44.940 | 0 / 44.938 |

**Giá và nhãn**
- Giá **27.400** (đóng cửa 06/11, BQ) cao hơn tâm **56,7%**. Tâm thấp hơn giá 36,2%.
- **84,1% trọng số kết cục nằm dưới giá.**
- Nhãn **TRONG vùng**: giá thấp hơn P90 10,7%.

**Vì sao nhãn mong manh**
- P90 do nhánh tích cực quyết định: nhánh này chiếm 84% trọng số quanh P90, với xác suất chỉ 0,25.
- Hai biến thể song song ra **TRÊN vùng**:
  - C (P/E 1/r cho mọi nhánh): P90 26.734.
  - Trần P/E 7,45x: P90 26.888.
- Điều 7: nếu theo định nghĩa vùng v3 01/11 (17.100–25.300), giá nằm TRÊN vùng.

**Thay đổi so với r2: tâm +10,5%.** Toàn bộ đến từ hai đính chính có cơ sở dữ liệu (§1). Hướng kết luận không đổi: giá cao hơn tâm 47–74% ở mọi biến thể (§3).

## 1. Kiểm từng đính chính

| # | Đính chính skeptic | Kiểm bằng dữ liệu (đo trong phiên này) | Kết quả |
|---|---|---|---|
| 1 | Bỏ sàn P/E 0 khi ROE < g; dùng 1/r khi ROE < r | Tỷ lệ chi trả DY/EY các quý 2022Q4–2025Q3 = **0,88–1,27** (BQ `ticker_financial`). Phải trả cổ tức 67,97 tỷ tại 30/09/2026 (TM14, BCTC HN Q3 tr.24/38) ≈ 1.006 đ/cp. Giá thấp nhất từ 2022 = **18.300** (2022). P/B trung vị 2023/24/25 = 1,54/1,82/1,86 (BQ `ticker`) | **ĐÚNG, áp.** P10 2.726 là artifact của sàn 0. Khi ROE thấp, TV2 thực tế trả hết LN chứ không tái đầu tư ở ROE < g. Tâm +1.436, P10 → 6.319 (biến thể A; skeptic ra 17.268, tôi ra 17.269) |
| 2 | Neo nhánh sập ở MỨC đáy quan sát, không áp tỷ lệ ×0,30 | LNST TTM 2023Q1–2025Q3: TB **64,3**, min 53,0, max 74,6 tỷ (BQ). ×0,30 × 110 = 33 tỷ, thấp hơn min quan sát | **ĐÚNG, áp.** Neo 64,3 tỷ (TB đáy). Tâm +221, P10 → **7.702**. Độ nhạy: neo 53,0 ⇒ 17.256; neo 74,6 ⇒ 17.704 |
| 2b | (tự rà, điều 2 đối xứng) Có cần neo trần cho nhánh +30% không? | Nhánh +30% cao nhất 357,5 tỷ. Đỉnh TTM 2017–21 là 317,8 tỷ danh nghĩa; tăng theo g 4% tới 2029 (×1,04⁸) thành 435 | Nằm trong dải ⇒ **không neo trần**. Ghi lại để chứng minh lưới không bị neo một chiều. **So sánh lệch chuẩn:** đỉnh được nhân 1,04⁸ ra 435 còn đáy 64,3 giữ danh nghĩa. Thử chặn nhánh +30% ở đỉnh danh nghĩa 317,8 thì P90 30.682, tâm 17.375 ⇒ không trọng yếu |
| 3 | Nhánh cao P/E 8,3–8,8x vượt P/E thị trường pha đỉnh (7,45x) | P/E thị trường 2017Q3–2021Q4 (BQ, theo quý): trung vị **7,09**, TB 6,99. Số 7,45 do REPORT_v3 dùng (khác cửa sổ) | **Báo song song, KHÔNG vào base.** P/E thị trường ở pha đỉnh đã chiết khấu kỳ vọng LN sập. Mô hình đã có trục độ bền riêng, áp thêm trần là đếm hai lần. Trần 7,45x ⇒ tâm 16.523 / P90 26.888 (TRÊN). Trần 7,09x ⇒ 15.791 / 25.578 (TRÊN) |
| 3b | Biến thể C (P/E 1/r mọi nhánh) | C ⇔ RONIC = r (không thưởng/không phạt tái đầu tư) = bản "chặt-3c". User đã chốt 08/11 10:50 chỉ dùng bản này làm độ nhạy | **Song song.** Tâm 16.470, P10 7.702, P90 26.734 ⇒ **TRÊN vùng** (skeptic 16.463/7.677/26.733) |
| 4 | Bridge 21.000 → 18.784 → 15.832 | §2 | Có từng bước; mỗi bước nêu nguyên nhân là đổi PHƯƠNG PHÁP, không có thông tin mới |
| 5 | CMC 666,4/188,6 chỉ có trong PDF scan | Render PyMuPDF BCTC HN Q3. **TM32.c (tr.36/38): phải thu CMC 666.374.010.268.** TM3 (tr.18/38): 657.327.141.975, cột dự phòng **trống**. **TM2a (tr.16/38): đầu tư LK CMC ghi sổ 188.637.915.014** (gốc 228,885 tỷ, lỗ lũy kế −40,247 tỷ) | **ĐÃ KIỂM.** Phơi nhiễm 855,012 tỷ (r2 dùng 854,97; ảnh hưởng ~0). Lệch TM3/TM32.c 9,0 tỷ vẫn chưa giải. WARNING "13 pháp nhân" giữ nguyên |
| 6 | Giá ngụ ý | §4 | LNST vĩnh viễn ~234–256 tỷ |

## 2. Bridge — tâm trượt qua các vòng (không có thông tin mới; chỉ đổi phương pháp)

| Vòng | Tâm | Nguyên nhân |
|---|---|---|
| v3 01/11 | 20.700 (tâm vùng cơ sở 21.000) | P/E gán tay 7–9x, neo P/E thị trường pha đỉnh (7,45x); chưa có CK |
| r1 05/11 | 18.784 | P/E nội tại từ r 13,5% và ROE: nhánh tiêu cực 5,43x thay 7–8x (11.000 → 7.665); CK 2,52% (−486) |
| r2 05/11 | 15.832 | CMC tách thành trục độc lập cho mọi kịch bản (kỳ vọng ≈ −1.418); trục độ bền "sập 70%" theo tỷ lệ; sàn P/E 0 khi ROE < g |
| **r3 08/11** | **17.491** | xem bảng r2 → r3 |

**r2 → r3 từng bước (sau CK)**

| Bước | Tâm | P10 | P90 |
|---|---|---|---|
| r2 control (giá 04/11) | 15.832 | 2.726 | 30.675 |
| Giá/CK cửa sổ tới 06/11 | 15.833 | 2.726 | 30.677 |
| CMC đầu tư 188,6 → 188,638 | 15.833 | 2.726 | 30.677 |
| Đ1: P/E 1/r khi ROE < r (= A) | 17.269 | 6.319 | 30.677 |
| **Đ2: sập neo mức đáy 64,3 (= B, headline)** | **17.491** | **7.702** | **30.677** |

Nhận xét: hai vòng r1 và r2 kéo tâm xuống bằng các giả định một chiều ở phía dưới (P/E tiêu cực nội tại, sập theo tỷ lệ, sàn 0). r3 gỡ đúng hai giả định trái dữ liệu. Phía trên (P90) không đổi qua r1–r3 vì nhánh tích cực không bị đụng.

## 3. Headline và các biến thể song song

| Biến thể | Tâm | P10 | P50 | P90 | % trọng số dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| **B — headline** | **17.491** | **7.702** | 16.019 | **30.677** | 84,1% | TRONG |
| A (chỉ Đ1) | 17.269 | 6.319 | 16.019 | 30.677 | 84,1% | TRONG |
| C (P/E 1/r mọi nhánh) | 16.470 | 7.702 | 15.981 | 26.734 | 91,1% | **TRÊN** |
| B + trần P/E 7,45x | 16.523 | 7.702 | 16.019 | 26.888 | 91,1% | **TRÊN** |
| B + trần P/E 7,09x (trung vị đo) | 15.791 | 7.448 | 15.198 | 25.578 | 93,2% | **TRÊN** |
| B, đáy 53,0 | 17.256 | 6.822 | 16.019 | 30.677 | 84,1% | TRONG |
| B, đáy 74,6 | 17.704 | 8.533 | 16.019 | 30.677 | 84,1% | TRONG |
| B, trọng số 30/50/20 | 18.284 | 7.758 | 17.083 | 32.146 | 81,4% | TRONG |
| B, trọng số 20/50/30 | 16.697 | 7.678 | 15.602 | 29.180 | 86,8% | TRONG |
| B, bỏ trục độ bền | 18.664 | 10.282 | 17.500 | 29.738 | 85,3% | TRONG |

**Vì sao chọn B làm headline**
- Đ1 và Đ2 đều có dòng cơ sở dữ liệu.
- C không vào base vì giả định RONIC = r cho cả nhánh ROE cao. Đó là bản chặt-3c, mà user đã chốt 08/11 chỉ dùng làm độ nhạy (moat NONE ⇒ không thưởng, không trừ, giữ mô hình cơ sở).
- Trần P/E không vào base vì sẽ đếm hai lần với trục độ bền (§1 mục 3).

**Đọc nhanh bảng**
- Tâm dao động **15.791–18.664** giữa các biến thể. Giá cao hơn tâm **47–74%**.
- Nhãn chỉ giữ được TRONG khi P/E nhánh tích cực được phép vượt 7,45x.

**Độ nhạy r (tâm sau CK, β = 1)**

| −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|
| 19.440 (+11,1%) | 18.410 | 17.491 | 16.673 | 15.927 (−8,9%) |

**Rủi ro chưa mô hình hoá (kế thừa r2):** mô hình tính khoản mất CMC sau lá chắn thuế 20% (model:85), nhưng chưa có cơ sở khấu trừ; lá chắn này đẩy giá trị lên ~350 đ/cp.

**P10 sau đính chính.** P10 7.702 ứng P/B 0,39. Mức này vẫn dưới P/B thấp nhất quan sát (0,92, năm 2022; dữ liệu `calc_r3/pxhist_tv2.csv` chỉ từ 2017) và dưới giá thấp nhất từ 2022 (18.300). Nguyên nhân: đuôi CMC mất 30–50% cộng LN sập về đáy cùng xảy ra. Đây là kết cục có xác suất của lưới, không phải artifact công thức như P10 2.726 cũ.

## 4. Giá ngụ ý (g 4%, CMC 0%, LN bền mãi, P/E nội tại)

| Giả định | LNST vĩnh viễn cần để ra giá 27.400 (trước CK 28.107) |
|---|---|
| P/E nội tại | **233,5 tỷ**: ROE 17,5%, P/E 8,13x, trong đó ~102,8 tỷ (44%) là lãi float trên tiền khách ứng |
| Như trên, kèm mất CMC kỳ vọng (14%) | 242,6 tỷ |
| P/E 1/r | 256,2 tỷ (ROE 19,3%) |

Đối chiếu:
- LNST TTM 2026Q3: 211,1.
- Đỉnh TTM 2017–21: 317,8.
- TB đáy 2023–25: 64,3.

Giá hiện tại cần đồng thời ba điều: LN ở mức cao hơn TTM hiện tại, giữ mãi, và lãi float không giảm khi giải ngân thiết bị EPC.

**Gordon g 4% (LNST 2026E 229,5, ước lượng, trước CK)**
- Có lãi tiền gửi: 27.478.
- Không lãi tiền gửi, công thức r2: 11.736.
- Không lãi tiền gửi, áp Đ1 (1/r): **14.098**.

## 5. Thanh khoản (cửa sổ tới 06/11)

| Cỡ | ADV trung vị | CK |
|---|---|---|
| **5 tỷ** (tham chiếu) | 120 phiên 3,22 tỷ (Q/ADV 155%, ngoài vùng √) | **2,52%** |
| 5 tỷ | 250 phiên 6,38 tỷ | 1,86% |
| 5 tỷ | 60 phiên 2,61 tỷ | 2,76% |
| **Sleeve 10/20/40 triệu** | 120 phiên | 0,37% / 0,41% / 0,47% |

- Tâm ở cỡ sleeve 40 triệu = **17.857**. Nhãn không đổi.
- Nhãn đặt theo cỡ 5 tỷ.

## 6. Pháp lý / quản trị — ⚠️ WARNING (giữ nguyên REPORT_r2 §6, không có cờ nào đóng)

1. Vụ án EVNNPT/PC1: cựu Chủ tịch và KTT bị khởi tố (CBTT 21/05/2026). Pháp nhân chưa bị khởi tố.
2. **13 pháp nhân "tư vấn xây dựng điện"** (họp báo Bộ Công an 02/07/2026) không nêu tên. Chưa xác định TV2 có trong danh sách hay không.
3. CMC (liên kết): phơi nhiễm 855,0 tỷ ≈ 64% VCSH mẹ; không dự phòng; số dư TM3 và TM32.c lệch 9,0 tỷ.
   - 9T/2026 phát sinh giao dịch với CMC 478,7 tỷ, kèm dòng âm −58,1 tỷ (TM32.b tr.36/38).
4. HĐ tổng thầu với bên liên quan được loại khỏi ngưỡng 35% (NQ HĐQT 29/10).
5. Room ngoại 0% từ 14/09/2026.
6. Phiên này không tra tin mới. Lần tra gần nhất là 05/11 (REPORT_r2 §6.7); **chưa tra lại sau 05/11, cần tra lại trước khi dùng nhãn**.

## 7. Giả định khoá (đủ trong `SUMMARY.json` › `assumptions`)

- r = 13,5% + 1,0 × (CCTG 12T 7,40% − 7,40%) = **13,5%**.
- VCSH mẹ 1.330,8 tỷ; N = 67,526 triệu cp.
- CMC 855,012 tỷ.
- P/E 1/r khi ROE < r.
- Nhánh sập neo 64,3 tỷ.
- Các tham số [UL]: kịch bản 250/177,5/110 (25/50/25), xác suất CMC, xác suất độ bền, g 3/4/5%.
- Không thưởng moat (5F: NONE).

## 8. Mốc đổi nhận định + HARD ABANDON

Giữ REPORT_r2 §8. Cập nhật ngưỡng nhãn theo r3:
- **TRÊN vùng** khi giá > 30.677. Ở các biến thể C hoặc trần P/E, mốc này là 26.734–26.888, tức giá hiện tại đã vượt.
- **DƯỚI vùng** khi giá < 7.702.

HARD ABANDON khi xảy ra một trong các việc:
- khởi tố pháp nhân;
- TV2 có tên trong 13 pháp nhân;
- CMC trích lập > 30%;
- kiểm toán FY2026 ngoại trừ.

**Không đủ điều kiện sleeve fear-buy §2.5**: giá cao hơn tâm 57%, không phải trạng thái sợ hãi, vụ án chưa kết luận.
