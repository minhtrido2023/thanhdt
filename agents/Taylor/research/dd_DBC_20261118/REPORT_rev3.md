# DD — DBC (CTCP Tập đoàn Dabaco Việt Nam, HOSE) · REV 3 · 23/11/2026 · job `Taylor_20261123_050005`

> **Khoá giả định:** `rev3/assumptions_DBC_rev3.json`, **assumptions_md5 = `66d9fbc6e099246b4c386080340c26cd`**. Lint `bin/dd_assumptions_lint.py`: 0 vi phạm. File khoá không chứa giá thị trường.
> **Mô hình:** `rev3/calc_rev3.py` (md5 `9c0c167e…`), đầu ra `rev3/calc_rev3_output.txt` (md5 `41369f17…`). Mốc theo dõi: `rev3/calc_rev3_milestones.py`, đầu ra `calc_rev3_milestones_output.txt`. Mọi số trong báo cáo lấy từ các file đầu ra này, trừ chỗ ghi nguồn khác.
> **Bản trước:**
> - rev1: `REPORT.md`, tâm 19.491. Phản biện `skeptic/r1.json` INCONCLUSIVE.
> - rev2: `REPORT_rev2.md`, tâm 17.317, khoá `25d2e305…`. Phản biện `skeptic/r2.json` INCONCLUSIVE.
>
> Rev3 sửa các hạng mục r2 còn sửa được (bảng Đính chính B).
> **Mù giá:** giả định được khoá trước khi đọc giá. Giá DNSE đọc sau bước khoá, ghi ở §6d. Hạn chế: người dựng đã thấy giá trong rev1/rev2 (§10).

## 0. Kết luận

- **Tâm = 14.696 đ/cp.** Đây là kỳ vọng trọng số 25/50/25 sau chiết khấu thanh khoản 2%.
  - **Vùng giá trị: [7.284; 21.857].**
  - Tâm trước chiết khấu thanh khoản: 14.996. Kịch bản cơ sở sau chiết khấu: 14.821.
- **So với rev2 (17.317): −15,1%. So với rev1 (19.491): −24,6%.**
  - Thay đổi duy nhất của rev3 lên tâm: **loại lợi nhuận chuyển nhượng BĐS lịch sử** ra khỏi ROE chuẩn hoá.
  - Lý do: theo BCTC kiểm toán, lợi nhuận gộp BĐS giảm từ 373,9 tỷ (2021) và 308,5 tỷ (2023) xuống 4,6 tỷ (2025) và 7,6 tỷ (9T/26). Mảng này không còn là nguồn lãi định kỳ.
  - Rev3 thay phần BĐS lịch sử bằng mức chạy hiện tại.
- **Giá 16.200 (DNSE, 23/11/2026 11:29) = 1,10× tâm ⇒ quanh/trên giá trị hợp lý, KHÔNG rẻ.**
  - Cổng 0,85×tâm = 12.492, còn cách xa.
- **Độ bất định rất lớn và hai chiều.** Tâm là trung bình của các cách nhìn chu kỳ khác nhau, không phải một con số chắc chắn.
  - Theo cửa sổ: chỉ 12 quý cho 22.630 (+54%); chỉ 20 quý cho 7.596 (−48%).
  - Nếu XDCB được tài trợ 50% bằng nợ: 12.210 (−16,9%).
  - Nếu giữ lãi BĐS lịch sử: 17.317 (+17,8%).
  - Cửa sổ dài 2016–2026, chưa tách XDCB/BĐS, chỉ là độ nhạy: 17.834 nếu gộp cả vốn; khoảng 23.640 nếu quy đổi sang ROE_op (ước lượng).
- **Kiểm toán:** BCTC 2025 do EY kiểm toán, ý kiến chấp nhận toàn phần.
- **Pháp lý: chỉ WARNING.** Phải thu người lao động 237,1 tỷ; nếu mất trắng thì −539 đ/cp. Không đưa vào base.
- **Sizing (V8):** chuẩn 2–4% NAV/mã. Ở giá hiện tại **không đề xuất mua**.

## Đính chính so với rev trước

### A. Hạng mục skeptic r1 (đã xử lý ở rev2, giữ nguyên trong rev3)

| # | Hạng mục | Xử lý | Nguồn |
|---|---|---|---|
| A1 | Quỹ khen thưởng phúc lợi (KTPL) chưa trừ | Đưa vào base: k = 11,06% LNST, gộp 2021–2025 = 346,85/3.135,61 (KTPL + thù lao HĐQT/BKS) | KT23 TM20 · KT25 TM23 · H1/26 TM25.1 · NQ ĐHĐCĐ 01/2026 |
| A2 | Chưa có BCTC kiểm toán 2025 | Đã tải BCTC kiểm toán 2022–2025. Q4/22 sửa theo số kiểm toán: −224,0 tỷ (BQ ghi −79,1) | `src/kt22…kt25_hopnhat_vi.pdf` |
| A3 | Lịch sử XDCB/vốn chủ chưa đo | Đo theo từng quý (mã 242 BCTC kiểm toán; quý giữa nội suy, là ước lượng). Trung bình 15 quý 17,4%, cao hơn ngưỡng 15% | BCĐKT kiểm toán + Q3/26 |
| A4 | Cửa sổ chuẩn hoá chọn sau khi thấy giá | Luật khai trước: tâm = trung bình đều của 3 cửa sổ 12/15/20 quý | file khoá `windows_predeclared` |
| A5 | Dùng ROE3Y của BQ làm "xác nhận độc lập" | Bỏ | — |
| A6 | Lỗ tính thuế 647 tỷ chưa ghi tài sản thuế hoãn lại | Chỉ tính vào kịch bản tốt: 647 × 20% = 129,4 tỷ | TM 31.4 H1/26 |
| A7 | Chi tuân thủ môi trường | Không kiểm chứng được. Chỉ làm độ nhạy 50–150 tỷ (ước lượng): −0,8% đến −2,3% | — |
| A8 | Phát hành ESOP 2026 | Không kiểm chứng đầy đủ. Độ nhạy pha loãng 1–3%: tâm 14.647 đến 14.553 | TM25.1 H1/26 |

### B. Hạng mục skeptic r2 → xử lý trong rev3

| # | Hạng mục r2 | Bằng chứng mới | Xử lý | Ảnh hưởng |
|---|---|---|---|---|
| B1 | Lãi 326,8 tỷ quý Q2/23 có phải khoản một lần? | Lợi nhuận gộp BĐS & xây lắp (doanh thu − giá vốn, tỷ đồng): 2021 = 887,66 − 513,76 = 373,9 (KT22); 2022 = 247,27 − 93,35 = 153,9; 2023 = 769,28 − 460,81 = 308,5 (KT23 TM22.1/23); 2024 = 267,59 − 242,86 = 24,7; 2025 = 21,41 − 16,78 = 4,6 (KT25 TM25.1/26); 9T/26 = 98,61 − 90,98 = 7,6 (Q3/26 mục VI). Năm 2023 cả năm chỉ lãi 25 tỷ nên Q2/23 gần như chắc chắn chứa lãi BĐS. Phân bổ theo quý không công bố | **(a) Vào base.** Trừ lợi nhuận gộp BĐS × (1 − 20%) khỏi LNST lịch sử (chia đều các quý trong năm, ước lượng), rồi cộng lại mức chạy = trung bình 2024/2025/2026 quy năm × 0,8 = **2,64 tỷ/quý**. Tổng lãi BĐS sau thuế bị loại trong 20 quý: 474,3 tỷ. Cơ sở độc lập: doanh thu BĐS kiểm toán giảm 769 → 21 tỷ. Không công bố quỹ đất/dự án mới; nếu có dự án mới thì đó là kịch bản, không đưa vào base | −15,1%. Độ nhạy: giữ BĐS lịch sử cho 17.317. Chưa trừ chi phí bán hàng/quản lý riêng của BĐS, nên mức loại có thể hơi cao |
| B2 | XDCB coi như 100% vốn chủ tài trợ, không có độ nhạy | Nợ vay gộp lớn (r2 dẫn 7.622 tỷ); lãi vay trong thời gian xây dựng được vốn hoá | **(b) Độ nhạy.** Tính lại ROE lịch sử với cùng tỷ lệ tài trợ. Base giữ 100%, vì lãi vay của phần vay đã vốn hoá vào XDCB, không đi qua LNST lịch sử | Vốn chủ tài trợ 50%: 12.210 (−16,9%). 25%: 10.965 (−25,4%) |
| B3 | Cửa sổ dài 2016+ | BQ `ticker_financial` 2016Q1–2021Q3 (chưa đối chiếu kiểm toán; không có XDCB/BĐS) | **(b) Độ nhạy, không vào base.** Lý do: (1) 2016–2021 có lãi BĐS lớn chưa tách (riêng 2021 là 373,9 tỷ); (2) đỉnh ASF 2020 (ROE quý tới ~40%); (3) chưa có XDCB lịch sử | ROE gộp cả vốn 14,22% → base 17.834. Bỏ 2020: 11,86% → 12.943. Quy đổi ROE_op (/(1 − 18%), ước lượng): 23.640 và 18.565 |
| B4 | Lợi ích cổ đông không kiểm soát (mã 61 so với mã 60) | KT23 TM31: LNST phân bổ cho cổ đông 2023 = 25,007 tỷ = mã 60; 2022 = 5,195 = mã 60. NCI trong vốn Q3/26 = 1,05 tỷ | Không đáng kể; không chỉnh | 0 |
| B5 | Thời hạn ưu đãi thuế TNDN | Không kiểm chứng được trong phiên này. Thuế hiệu dụng 9T/26 là 10,8%; ROE lịch sử đã sau thuế | **(c)** Độ nhạy ước lượng: nếu thuế hiệu dụng lên 20% thì LNST giảm khoảng (1 − 0,8/0,892) ≈ −10% ⇒ tâm giảm khoảng 13% (ước lượng, chưa chạy trong calc) | ước lượng |
| B6 | Phần capex trại heo còn lại | Không công bố (TM 8 Q3/26) | XDCB được ghi NPV = 0 (V4a). Phần chi còn lại là dự án tăng trưởng nên không trừ | — |
| B7 | Ý kiến kiểm toán không đọc được trực tiếp (PDF dạng quét) | OCR trang báo cáo kiểm toán KT23/KT22: "Chúng tôi đã kiểm toán…"; KT25: EY | Ghi nhận; chưa thấy đoạn ngoại trừ trên các trang đã OCR | — |

## 1. Nguồn và đối chiếu

- **LNST theo quý:** BQ `NP_P0`.
  - Tổng năm 2021, 2023, 2024, 2025 khớp dòng 60 của BCTC kiểm toán: 829,56 / 25,01 / 769,08 / 1.506,77 tỷ.
  - Năm 2022: BQ cộng lại 150,1 tỷ; kiểm toán là 5,19 tỷ ⇒ sửa Q4/22.
- **Vốn chủ mẹ:** lấy từ BQ (BVPS × số cổ phiếu, có 2 điểm đã sửa). Riêng 2021Q4 và 2022Q4 lấy từ BCTC kiểm toán.
- **XDCB:** mốc cuối năm lấy từ BCĐKT kiểm toán. Các quý giữa là nội suy (ước lượng).
- **LNST chuẩn hoá (sau khi loại BĐS):** 915,5 tỷ/năm. EPS chuẩn hoá 2.124 đ; sau trích KTPL 1.889 đ.

## 2. Chuẩn hoá ROE (luật khai trước; LNST đã loại BĐS)

Công thức: ROE_op = 4 × LNST quý / (vốn chủ mẹ − XDCB). XDCB ghi theo sổ sách với NPV = 0.

| Cửa sổ | ROE toàn vốn | ROE_op nội suy | ROE_op bậc thang |
|---|---|---|---|
| W12 (Q4/23–Q3/26) | 13,88% | 16,84% | 16,35% |
| W15 (Q1/23–Q3/26) | 10,03% | 11,87% | 11,43% |
| W20 (Q4/21–Q3/26) | 7,19% | 8,32% | 7,85% |
| **Tâm = trung bình đều** | | **12,34%** | 11,88% (tâm 13.875, −5,6%) |

- Sau trích KTPL: ROE cho cổ đông = 12,34% × (1 − 11,06%) = **10,98%**.
- Biến thể gộp cả vốn (XDCB cũng sinh ROE lịch sử): tâm 9.845 (−33,0%).

## 3. Quỹ khen thưởng phúc lợi

- k = 11,06%, gộp 5 năm lợi nhuận 2021–2025.
- Tỷ lệ từng năm: 5,7% / 0% / 0% / 26,5% / 6,3%. Thù lao HĐQT/BKS trích từ lợi nhuận 2021–2023 chưa đọc ⇒ k có thể hơi thấp.
- Độ nhạy theo k:

| k | Tâm |
|---|---|
| 0% | 17.405 |
| 6,3% | 15.862 |
| 13,0% | 14.221 |
| 26,5% | 10.915 |

## 4. XDCB và BĐS

- **XDCB 30/9/2026: 1.302,6 tỷ**, trong đó trại heo 873,4 tỷ.
  - Base: NPV = 0 theo sổ sách.
  - Kịch bản xấu: haircut 40% phần trại heo. Cơ sở: Bobby — làn sóng mở trại 2025–26.
  - Độ nhạy theo tỷ lệ tài trợ: xem B2.
- **BĐS:** giữ mức chạy 2,64 tỷ/quý sau thuế. Dự án BĐS mới, nếu xuất hiện, là kịch bản tăng — không đưa vào base.

## 5. Dòng tiền, V6 (chỉ hiển thị)

- CFO trung bình 1.133,3 tỷ/năm; capex (gồm thuê tài chính) 1.178,7 tỷ/năm ⇒ **FCFE ≈ −45,5 tỷ/năm ⇒ V_dài không xác định.**
- **V_ngắn = 10.324 đ/cp.** Tỷ lệ tái đầu tư 0,535; ROE toàn vốn sau KTPL 9,34%.
- FCFE âm do capex tăng trưởng (trại heo, ép đậu), không phải tín hiệu đắt.
- Không tính được D ⇒ không có cờ D. Tâm không trộn với V_ngắn.

## 6. Định giá

### 6a. Khung và V1

- **Mô hình thu nhập thặng dư:**
  V = (vốn chủ − XDCB) × (ROE_op × (1 − k) − g) / (r − g) + XDCB − haircut (chỉ kịch bản xấu) + lá chắn thuế (chỉ kịch bản tốt).
- **Tham số:**
  - Vốn chủ mẹ 8.720,4 tỷ; 431,05 triệu cổ phiếu.
  - g = 5%.
  - Biên kịch bản ±3,25 điểm % ROE toàn vốn (= ±3,82 điểm % ROE_op).
- **r = 13,5%** (V1): neo lãi huy động 12 tháng hiệu dụng 7,4% (`deposit_rate_vn`, CCTG 12T 02/11; kiểm lại 18/11 và 23/11 vẫn 7,4%). Δ = 0, β = 1.
- **Độ nhạy r:**

| Lãi huy động | Tâm β = 1 | Tâm β = 0,5 |
|---|---|---|
| −100bp | 16.277 (+10,8%) | 15.437 (+5,0%) |
| −50bp | 15.437 (+5,0%) | 15.055 (+2,4%) |
| +50bp | 14.037 (−4,5%) | 14.357 (−2,3%) |
| +100bp | 13.447 (−8,5%) | 14.037 (−4,5%) |

- **Dải Ke D4:** Ke 12,3% → tâm 16.645; Ke 13,4% → tâm 14.837.
- **g:** 4% → 15.223; 6% → 14.028.

### 6b. Kịch bản

| Kịch bản | Xác suất | ROE_op | Giá trị trước chiết khấu thanh khoản |
|---|---|---|---|
| Xấu (haircut 40% XDCB trại heo) | 25% | 8,52% | 7.433 |
| Cơ sở | 50% | 12,34% | 15.123 |
| Tốt (+ lá chắn thuế 129,4 tỷ) | 25% | 16,16% | 22.303 |
| **Kỳ vọng sau chiết khấu 2%** | | | **14.696**, vùng [7.284; 21.857] |

Đổi trọng số kịch bản: 35/50/15 → 13.238 (−9,9%); 15/50/35 → 16.153 (+9,9%).

### 6c. V3 — thanh khoản

- Chiết khấu 2% là ước lượng, dựa trên ADV đo sau bước khoá ở rev1 (18/11): vị thế ≤20 tỷ thoát hết trong ≤10 phiên ở mức tham gia 10%.
- Giá trị trước chiết khấu 14.996; sau chiết khấu 14.696. Ở mức chiết khấu 0%: 14.996; 5%: 14.246.
- Nhãn rẻ/đắt dùng giá trị **sau** chiết khấu.

### 6d. So giá (bước cuối, sau khoá)

- **Giá DNSE `latest_trade` (G1) 16.200 đ, 23/11/2026 11:29.**
  - Giá/tâm = 1,10; giá/kịch bản cơ sở = 1,09.
  - P/B hàm ý tại tâm 0,73; P/E chuẩn hoá hàm ý 6,9.
- **Dải giá/tâm qua các phán đoán chính:**
  - Cửa sổ: 0,72–2,13.
  - BĐS giữ/loại: 0,94–1,10.
  - Tỷ lệ XDCB do vốn chủ tài trợ 50–100%: 1,10–1,33.
- **⇒ Nhãn: quanh/trên giá trị hợp lý, không rẻ.** Cổng 0,85×tâm = 12.492, không đạt.

## 7. Pháp lý / quản trị — chỉ WARNING

- **Kiểm toán và soát xét:**
  - EY soát xét bán niên 2026: sạch.
  - Kiểm toán 2025: chấp nhận toàn phần.
  - Kiểm toán 2022: điều chỉnh giảm LNST Q4 144,9 tỷ ⇒ cần theo dõi chất lượng số liệu quý chưa kiểm toán.
- **Phải thu người lao động 237,1 tỷ** (TM 4a Q3/26): WARNING; mất trắng = −539 đ/cp.
- **Bên liên quan nhỏ:** Transeco 20 tỷ.
- **Vốn tăng năm 2024:** dùng 100% đúng phương án.
- **Không kiểm chứng được:** giấy phép môi trường từng trại; toàn văn NQ ĐHĐCĐ 2026 về ESOP; thời hạn ưu đãi thuế.

## 8. 5F (V5)

- Tái dùng 5F đầy đủ của rev1 §8, lập ngày 18/11/2026 (chưa quá 12 tháng).
  - **moat_tier = NARROW (mỏng; NONE cũng đứng được)**, COST/INTEGRATION.
  - Rủi ro số 1: chu kỳ giá heo + ASF.
- Kiểm nhanh rev3: ROE_op lõi dao động 8,3% (W20) – 16,8% (W12), chưa qua tiêu chí lợi nhuận siêu ngạch bền ⇒ không thưởng tham số moat.
- BĐS cạn: lợi thế quỹ đất Bắc Ninh không còn đóng góp vào lợi nhuận.

## 9. Mốc khoá trước — cả hai chiều

**Hiệu ứng trượt cửa sổ (cơ học, không phải cơ bản).** Khi có BCTC Q4/26, Q1/23 (lỗ −320,7 tỷ) rơi khỏi W15 và Q4/21 rơi khỏi W20. Vì vậy tâm sẽ tăng ngay cả khi quý mới lỗ:

| LNST Q4/26 | Tâm |
|---|---|
| −50 tỷ | 16.401 (+11,6%) |
| +35 tỷ | 16.942 (+15,3%) |
| +120 tỷ | 17.470 (+18,9%) |

⚠️ Đổi nhận định phải dựa vào bảng dưới, **không** dựa vào mức tăng cơ học này. Luật dự kiến cho rev sau (ghi rõ trước): báo kèm tâm "neo khung" giữ nguyên các quý đầu cửa sổ của rev3.

| Mốc | Thời điểm | Chiều tăng | Chiều giảm |
|---|---|---|---|
| BCTC Q4/26 | ≤ 30/01/2027 | LNST ≥ 120 tỷ, không trích lập tài sản sinh học ⇒ trọng số kịch bản tốt 35% | LNST < −50 tỷ hoặc trích lập > 100 tỷ ⇒ trọng số kịch bản xấu 35% |
| Trích KTPL từ lợi nhuận 2026 | ~04/2027 | ≤ 6% LNST | ≥ 15% LNST |
| Doanh thu BĐS | mỗi BCTC | Dự án BĐS mới được công bố, có số liệu ⇒ kịch bản tăng | — |
| Giá heo T1/27 (Bobby F1/F2) | 05/02/2027 | ≥ 65k/kg | < 50k/kg |
| BCTC Q1/27 | ≤ 30/04/2027 | LNST ≥ 300 tỷ và biên gộp ≥ 8,5% | LNST < 150 tỷ |
| Đàn heo T3/27 (Bobby F8) | 15/04/2027 | ≤ +3% YoY | ≥ +4% YoY |
| Lãi huy động 12T | liên tục | −50bp ⇒ +5,0% | +50bp ⇒ −4,5% |
| XDCB và ROE_op | mỗi BCTC | ROE_op quý ≥ 12,3% khi trại vào vận hành | XDCB > 20% vốn chủ và ROE_op quý < 10% |
| Phải thu người lao động | BCTC Q4/26 | ≤ 150 tỷ ⇒ gỡ WARNING | > 300 tỷ hoặc trích lập |

## 10. Điểm yếu của chính báo cáo

1. **Tâm phụ thuộc mạnh vào phán đoán cửa sổ** (−48%/+54%), vào giả định tài trợ XDCB (tới −25%) và vào cách xử lý BĐS (+18%). Nên đọc vùng giá trị, không đọc tâm như một con số chắc.
2. **Phân bổ lãi BĐS theo quý là ước lượng** (chia đều trong năm). Việc trừ lợi nhuận gộp chưa tính chi phí bán hàng/quản lý riêng của BĐS ⇒ phần loại có thể hơi cao, tâm có thể hơi thấp.
3. **Cửa sổ dài (2016+) cho giá trị cao hơn nhiều nhưng chứa lãi BĐS và ASF 2020 chưa tách.** Tôi không đưa vào base. Đây là phán đoán và nghiêng về phía thận trọng.
4. **Chiều lệch tâm lý:** người dựng đã thấy giá rev1/rev2. Rev3 kéo tâm xuống, ra khỏi vùng "rẻ" — ngược chiều với thiên lệch mua — nhưng vẫn không loại trừ được hoàn toàn.
5. **Chưa kiểm chứng:** thời hạn ưu đãi thuế, chi tuân thủ môi trường, ESOP 2026, thời hạn hoàn ứng của khoản phải thu người lao động.

## 11. Nguồn

- **BCTC hợp nhất kiểm toán:**
  - `src/kt22_hopnhat_vi.pdf` (dabaco.vn wp-content)
  - `src/kt23_hopnhat_vi.pdf` (drive 18XK0rqA…, tải từ trang CBTT dabaco.vn)
  - `src/kt24_hopnhat_vi.pdf`
  - `src/kt25_hopnhat_vi.pdf` (EY)
- **BCTC giữa niên độ:** `src/h1_d.pdf` (soát xét H1/26); `src/q3_hopnhat.pdf` (mục VI: doanh thu/giá vốn BĐS 9T/26).
- **Ảnh minh chứng:** `png/kt25_41_tm23.png`; `png/h1d_52_equity.png`.
- **BQ:** `tav2_bq.ticker_financial` DBC 2016Q1–2026Q3 (truy vấn 23/11/2026).
- **Lãi suất:** `deposit_rate_vn`. **Giá:** DNSE (đọc sau bước khoá).
- **Ngành:** Bobby sector read 18/11. **5F:** `REPORT.md` §8.

## 12. Sổ giá

- **KHÔNG ghi `kb/dd_price_zones.json`.** Đề xuất ghi sổ: `LEDGER_PROPOSAL_DBC.json`.
- Tâm 14.696; vùng [7.284; 21.857]; center_alt (kịch bản cơ sở sau chiết khấu thanh khoản) 14.821.
- Giá tham chiếu 16.200 (23/11/2026).
- **assumptions_md5 = `66d9fbc6e099246b4c386080340c26cd`.**
