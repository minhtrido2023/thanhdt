# DD — TTA r3 · 2026-11-20 · job `Taylor_20261120_050035` (đính chính cơ học vòng 2 lên REPORT_r2.md)

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua. Không đặt lệnh, không wire, **không ghi `dd_price_zones.json` (Mike làm), không email**.
> REPORT.md/REPORT_r2.md + model r1/r2 giữ nguyên. Mô hình r3: `model/dcf_tta_r3.py` → `model/out_r3.json` (mọi số dưới đây đọc từ file này
> trừ khi ghi nguồn PDF). Dữ liệu giá: `model/data/px_tta.csv` = `tav2_bq.ticker` TTA 2025-09-01→2026-11-19 (304 phiên).
> Kiểm tái lập: r3 chạy lại r2 ra đúng V1 {A 12.651, B 8.821, B′ 5.559, C 1.175} / V2 {12.651, 8.945, 5.776, 1.513} — khớp `dcf_tta_r2.py`.

## 0. Kết luận r3

**Hướng giữ: KHÔNG RẺ ở 10.250 đ (đóng cửa 19/11/2026, BQ).** Đổi so với r2 chỉ ở mức số do thay chiết khấu thanh khoản 10% phẳng bằng quy ước fleet.

| Mục (V1, trọng số A/B/B′/C = 0,15/0,25/0,35/0,25) | đ/cp |
|---|---|
| Tâm có trọng số **trước** chiết khấu thanh khoản | **6.342** |
| Chiết khấu thanh khoản d(5 tỷ) = nửa spread 0,44% + σ·√(Q/ADV) 2,45% | **2,89%** (ADV 250 phiên); 3,87% (ADV 68 phiên) |
| **Tâm có trọng số SAU thanh khoản (expected_weighted)** | **6.159** (ADV 68 phiên: 6.097; 10% phẳng — chỉ độ nhạy: 5.708) |
| Giá 19/11 / tâm | **1,66×** sau TK · 1,62× trước TK |

**Vùng giá — CÙNG NỀN sau thanh khoản (tâm 6.159):**
| Vùng | Ngưỡng (đ/cp) |
|---|---|
| Dưới vùng hợp lý (≤ 0,85 × tâm) | **≤ 5.235** |
| Hợp lý (0,85× … 1,15× tâm) | **5.235 – 7.083** |
| Trên vùng hợp lý (> 1,15× tâm) | **> 7.083** — giá 10.250 nằm ở đây |

Mọi ô lưới P(A) 0–0,35 × P(C) 0,10–0,40 sau TK: **≤ 8.110 < 10.250** ⇒ kết luận bền với trọng số (r2 ghi ≤7.516 với 10% phẳng; thay quy ước ⇒ trần lưới tăng, hướng không đổi).
Biến thể bù trừ lai (H): tâm **6.444** trước / **6.257** sau TK (+102 so với V1). V2: 6.534 / 6.345. Pháp lý: WARNING. Quản trị: **WARNING (nâng, §6)**.

**assumptions_md5** (`model/dcf_tta_r3.py`) = `5ff89722e26d04ad7f808cd170285a19`.

## 1. Chiết khấu thanh khoản — quy ước fleet (đính chính 1)

Phương pháp như SCL r3 (`dd_SCL_20261029/r3/calc/compare_r3.py`): d(Q) = nửa spread Corwin-Schultz (120 phiên, High/Low) + Y·σ_ngày·√(Q/ADV_trung vị), Y = 1,0 (đăng ký trước), tham chiếu Q = 5 tỷ.
Đo trên `model/data/px_tta.csv`: σ_ngày (log, 250 phiên 18/11/2025→19/11/2026) **1,626%** · ADV trung vị (Price×Volume) **2,20 tỷ** (250 phiên) / **1,13 tỷ** (68 phiên) · spread CS **0,88%**.

| Q | d (ADV 250) | d (ADV 68) | Y=0,5 (ADV 250) | Số phiên thoát @20% ADV (250 / 68) |
|---|---|---|---|---|
| 1 tỷ | 1,54% | 1,97% | 0,99% | 2,3 / 4,4 |
| **5 tỷ (tham chiếu)** | **2,89%** | 3,87% | 1,67% | 11,3 / 22,2 |
| 10 tỷ | 3,91% | 5,29% | 2,17% | 22,7 / 44,4 |

Chọn ADV 250 phiên làm chính (cửa sổ khớp σ); ADV 68 phiên là cận dưới (thanh khoản 3 tháng gần đây giảm một nửa). 10% phẳng của r2 chỉ còn là độ nhạy (tâm 5.708).
Ghi chú: ADV 68 phiên r2 ghi 1,07 tỷ (trung vị KL 102.100 cp × giá) — r3 đo bằng trung vị Price×Volume từng phiên ra 1,13 tỷ; khác do cách lấy trung vị (tích vs thành phần).

## 2. Tỷ lệ EPTC trả — so cùng kỳ 9T/9T (đính chính 2)

| Kỳ | DT khu vực Ninh Thuận (mặt trời) | Hoá đơn ×1,08 VAT (ước lượng thuế suất) | Δ phải thu EPTC | Tiền EPTC trả | Tỷ lệ |
|---|---|---|---|---|---|
| 9T/2025 | 280,12 [Q3/25 tr.36 bộ phận] | 302,5 | 77,11 → 211,94 = **+134,8** | 167,7 | **55,4%** |
| Q4/2025 | — | — | 211,94 → 237,66 = **+25,7** | — | — |
| 9T/2026 | 295,5 [Q3/26 bộ phận] | 319,1 | 237,66 → 399,63 = **+162,0** | 157,2 | **49,2%** |

Nguồn số dư: 77,11 tỷ (31/12/2024) **[KT25 tr.24 V.2 — đã đối chiếu PDF, bỏ nhãn "chưa kiểm"]**; 211,94 [Q3/2025 tr.19]; 237,66 / 399,63 [Q3/2026 tr.18 mục 3].
**Bỏ** phép tính "2025 ~62%" của r2 (`sens_w_r2.py:26` lấy ngược hoá đơn từ chính giả định 62% — vòng tròn).
Đọc: EPTC trả **~55% → ~49%** cùng kỳ — thấp hơn tỷ lệ ngụ ý của B′ (72%) và sát C (55%), đang xấu đi nhẹ. Vẫn N nhỏ (2 kỳ, 1 người mua) ⇒ không phải xác suất.
Giả định ngầm: toàn bộ Δ phải thu EPTC đến từ mặt trời — xem §8 (Ngòi Hút 2).

## 3. Trọng số — khai đường thử + độ nghiêng (đính chính 3)

**Đường thử thật (r2, `dcf_tta_r2.py:83–86` rồi chốt), V1 trước TK:** 0,20/0,25/0,35/0,20 → **6.916** · 0,15/0,25/0,40/0,20 → **6.562** · **chốt 0,15/0,25/0,35/0,25 → 6.342**.
Bộ chốt là bộ **thấp nhất** trong ba bộ đã thử. Cùng lúc r2 chọn **V1** (bù trừ ngay — biến thể thấp nhất) và chiết khấu 10% (cao hơn quy ước fleet).
⇒ Tổng thể r2 **nghiêng thận trọng**. Các yếu tố CÓ LỢI cho TTA mà mô hình bỏ sót (nêu cạnh nhau, không bù vào base):
| Yếu tố bỏ sót | Hướng | Đo |
|---|---|---|
| Dòng tiền Q4/2026 (mô hình bắt đầu 2027, bảng cân đối 30/9/2026) | + | chưa đo |
| Hoàn/giảm thuế TNDN trên doanh thu bị hồi tố (thuế suất ưu đãi thấp) | + nhỏ | chưa đo |
| Loại tỷ giá dùng tính hồi tố: QĐ 13/2020 quy đổi theo tỷ giá nào (ngày hoá đơn / ngày ký / trung tâm) | ± | **chưa kiểm**; r3 dùng TB năm `data/macro_usdvnd.csv` (ước lượng) |
| Bù trừ lai (bù trừ tới mức phải thu vượt, phần dư trả góp 5 năm lãi 8,4%) | + | tâm **+102** (6.342 → 6.444) |

**Biến thể bù trừ (đ/cp, trước TK):**
| | A | B | B′ | C | Tâm chốt | Sau TK 2,89% |
|---|---|---|---|---|---|---|
| V1 bù trừ ngay | 12.651 | 8.821 | 5.559 | 1.175 | **6.342** | **6.159** |
| H lai | 12.651 | 8.839 | 5.670 | 1.407 | 6.444 | 6.257 |
| V2 trả góp | 12.651 | 8.945 | 5.776 | 1.513 | 6.534 | 6.345 |
B (hồi tố 385) gần như không đổi giữa V1/H vì hồi tố < phải thu vượt 330 chỉ ~55 tỷ.

**Độ nhạy trọng số (V1, sau TK 2,89%):** lạc quan 0,25/0,30/0,30/0,15 **7.432** · r1-style **7.640** · A/B′/C 0,25/0/0,50/0,25 **6.056** · đều 0,25×4 **6.848** · bi quan 0,10/0,15/0,35/0,40 **4.859** · 0/0/0,5/0,5 **3.270**.
Lưới sau TK (P(A) hàng × P(C) 0,10/0,20/0,25/0,30/0,40; B:B′ = 1:1,4): P(A)=0: 6.162…4.488 · 0,15: 6.997…5.323 · 0,25: 7.553…5.879 · 0,35: **8.110**…6.436.

**Độ nhạy r (tâm sau TK):** −100bp **6.612** · −50bp **6.380** · 0 **6.159** · +50bp **5.950** · +100bp **5.751**. Phước Hoà (tâm sau TK): =0 **5.666** · sổ sách 90,7 **6.159** · 95,7 **6.186**.

## 4. DSCR 2027 trừ thuế + chia LN HTKD (đính chính 4)

DSCR = (EBITDA − capex − thuế − chia LN HTKD tiền mặt) / (lãi + gốc 280). HTKD 2027 = 30,0 tỷ (12% EBITDA thuỷ điện; [KT25 tr.30] phải trả phân chia LN HTKD cuối 2025 = 31,37 tỷ).
| | EBITDA | Thuế | HTKD | Lãi | DSCR trước thuế/HTKD (r2) | **DSCR r3** |
|---|---|---|---|---|---|---|
| A | 588,2 | 15,2 | 30,0 | 130,6 | 1,36 | **1,25** |
| B | 531,5 | 11,8 | 30,0 | 130,6 | 1,22 | **1,12** |
| B′ | 477,3 | 8,5 | 30,0 | 130,6 | 1,09 | **1,00** |
| C | 365,3 | 0,8 | 24,1 | 146,1 | 0,79 | **0,73** |
Khớp ước của phản biện (A ~1,26 / B′ ~1,00 / C ~0,73). Tất cả **trước** dòng tiền hồi tố. **HARD ABANDON #3 neo DSCR ~1,00**: B′ — kịch bản trung tâm — không còn dư địa trả nợ.

## 5. Phước Hoà (đính chính 5)

[KT25 tr.30 mục 15a(*)]: 5 tỷ là **khoản phải trả bà Nguyễn Thị Thanh** theo Biên bản thoả thuận 16/4/2025 về chuyển tiền chi phí triển khai dự án thuỷ điện tích năng Phước Hoà;
khoản này **sẽ được đối trừ vào phần góp vốn của bà Thanh** ngay sau khi công ty dự án được thành lập và có tài khoản ngân hàng.
⇒ Sửa câu r2 "BCTC không nói đó là nợ hay góp vốn": BCTC nói rõ — **hiện là nợ phải trả, sẽ thành vốn góp**. Xử lý mô hình giữ nguyên (90,7 = 95,7 − 5): sau khi chuyển thành vốn góp, 5 tỷ là phần của bên ngoài trong công ty dự án ⇒ trừ đúng.
Base = sổ sách (NPV = 0), không giảm giá trị vì là dự án mới.

## 6. Quản trị — nâng WARNING (đính chính 6; chỉ WARNING có nguồn, KHÔNG đưa vào base)

| Sự kiện | Nguồn |
|---|---|
| Phải thu ngắn hạn khác đầu 2025: **bà Nguyễn Thị Ngọc (Chủ tịch HĐQT) 96,64 tỷ** = khoản "tạm chi trả nợ vay ông Trần Huy Đức" theo BB HĐQT số 10.05/2023/BB-HĐQT ngày 10/5/2023; đến 31/12/2025 công ty "đã hoàn tất thủ tục chuyển giao quyền và nghĩa vụ về khoản nợ phải trả đối với ông Trần Huy Đức cho các cá nhân liên quan" (số cuối năm = 0) | KT25 tr.26 mục 5(*) |
| Vay dài hạn thành viên Ban lãnh đạo **139,25 tỷ → 0** cuối 2025 | KT25 tr.34 mục b |
| Phải thu Cty TNHH XD Trường Thành (cổ đông lớn, bên liên quan) 23,5 tỷ đầu 2025 → 0; cho vay ngắn/dài hạn Cty TNHH XD Trường Thành 12,5 + 2,5 tỷ tại 30/9/2026 | KT25 tr.26; Q3/26 tr.18 mục 2 |
| Sở hữu 30/9/2025: Trần Huy Đức **23,26%**, Cty TNHH XD Trường Thành **23,63%**, Nguyễn Thị Ngọc **11,63%**, Trần Huy Thiệu **4,34%**, Đinh Quang Chiến 6,03%, cổ đông khác 31,11% | BCTC Q3/2025 tr.31 |
| Nhóm Đinh Quang Chiến lên **20,04%** (25/08/2026) | [TX] |
**Free float ước ~17–20%** (= cổ đông khác 31,11% trừ phần nhóm Chiến gom thêm sau 30/9/2025 ~14pp; ước lượng — chưa có danh sách cổ đông 2026), **không phải ~30%** như đọc thô.
Đọc: tiền công ty từng đi qua Chủ tịch để trả nợ vay cá nhân cựu Chủ tịch; khoản vay BLĐ và phải thu này cùng biến mất bằng "chuyển giao cho cá nhân liên quan" không nêu tên/giá —
**chưa có bằng chứng thất thoát** (số dư về 0, kiểm toán không ngoại trừ) nhưng là dòng tiền bên liên quan không minh bạch. Free float thấp ⇒ củng cố việc dùng ADV 68 phiên làm cận dưới thanh khoản.

## 7. Vùng giá cùng nền + khai md5 (đính chính 7)

Đã ở §0. Mọi ngưỡng tính trên **tâm sau TK 6.159**: dưới ≤ **5.235** · hợp lý **5.235–7.083** · trên **> 7.083**. (r2 trộn: 4.850 sau TK 10% với 6.340 trước TK — bỏ.)
Ở cả hai nền: giá 10.250 = **1,62× tâm trước TK (6.342)** và **1,66× tâm sau TK (6.159)** ⇒ **TRÊN vùng hợp lý ở cả hai mức** — kết luận không đổi.
Nếu chỉ cân A/B (loại hẳn B′/C): 10.250 cần tâm trước TK = 10.250/0,9711 = **10.555** ⇒ P(A) = (10.555 − 8.821)/(12.651 − 8.821) = **0,45** (r2 ghi ~67% vì dùng 10% phẳng — thay bằng số này).
HARD ABANDON (giữ 5 điều kiện r2 §4), sửa #3: **DSCR 2027 sau thuế + HTKD < 1,00, hoặc vi phạm covenant/giãn-hoãn nợ/tái cấp vốn** ⇒ bỏ phân tích mua.

## 8. Phải thu EPTC có gồm thuỷ điện Ngòi Hút 2 (48 MW) không? (đính chính 8)

**Chưa kiểm được từ BCTC.** Thuyết minh phải thu [Q3/26 tr.18 mục 3; KT25 tr.24] chỉ tách theo **người mua** (Tổng công ty Điện lực Miền Bắc 43,98; Công ty Mua bán điện 399,63), không theo nhà máy;
không có hợp đồng mua bán điện từng nhà máy trong BCTC. Chỉ báo gián tiếp (suy luận, không phải bằng chứng): DT khu vực Yên Bái 9T/2026 279,8 tỷ ≈ 31 tỷ/tháng, phải thu EVNNPC 43,98 ≈ 1,4 tháng
doanh thu thuỷ điện — khớp kịch bản EVNNPC mua **toàn bộ** thuỷ điện (kể cả Ngòi Hút 2). Nếu ngược lại Ngòi Hút 2 bán cho EPTC (nhà máy >30 MW thường ký với EPTC), một phần Δ phải thu EPTC là thuỷ điện ⇒
tỷ lệ trả tiền mặt trời ở §2 còn **thấp hơn**. Cần: hợp đồng PPA Ngòi Hút 2 hoặc hỏi IR. Không đổi mô hình.

## Phụ lục — Giới hạn
- Chưa qua phản biện vòng 3 (không yêu cầu). Không ghi dd_price_zones, không email.
- Tỷ giá local dừng 29/4/2026; loại tỷ giá hồi tố theo QĐ 13/2020: chưa kiểm. VAT 8% trên hoá đơn điện: ước lượng.
- §2 Phụ lục A (r2) giữ nguyên phán quyết nội bộ.

## Khai md5
assumptions_file = `agents/Taylor/research/dd_TTA_20261120/model/dcf_tta_r3.py` · **assumptions_md5 = `5ff89722e26d04ad7f808cd170285a19`** (đo `md5sum`) · output `model/out_r3.json` md5 `246318d2b1897783bda00ef2bfbfa15d`.
