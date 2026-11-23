# DD — LLM (Lilama, UPCoM) · REV 4 · 2026-11-23 · job `Taylor_20261123_001048`

> Chỉ nghiên cứu, không phải khuyến nghị mua. Không đặt lệnh. Pháp lý chỉ ghi WARNING.
>
> **Lịch sử bản:**
> - rev2 (`REPORT.md`, 18/11, tâm 24.599) → skeptic DD_GENERAL r1 **REFUTED**.
> - rev3 (`REPORT_rev3.md`, tâm 28.834) → skeptic r2 **REFUTED** (`skeptic/r2_raw.md`).
> - Rev4 = rev3 + sửa toàn bộ hạng mục của r2 (§1B).
> - Mô tả doanh nghiệp, chất lượng lợi nhuận, 5F, pháp lý ở rev2 §3–§7, §11 vẫn giữ nguyên, trừ các điểm sửa dưới đây.
>
> **Ký hiệu nguồn:**
> - **[HN]** BCTC hợp nhất Q3/26, `src/bao_cao_tai_chinh_hop_nhat_q3.2026_vie-da_nen.{pdf,txt}`.
> - **[KT25 pX]** BCTC hợp nhất kiểm toán 2025 (AASC, 310325.015/BCTC.KT2, ký 31/03/2026), `src_r2/llm_25cn_bctc_hn_da_kt_signed.pdf`, md5 `9be1160b5c2ffca6683ff765ce00ade7`. Ảnh 57 trang ở `png/kt25full/`; pX là số trang PDF.
> - **[BQ]** `tav2_bq.ticker_financial` (`model/bq_fin_LLM.csv`).
> - **[Web]** URL ở mục Nguồn.
>
> **Khoá giả định MÙ GIÁ** (không truy vấn giá LLM trước khi khoá):
> - `model/assumptions_LLM_20261123_rev4.json`, md5 **`deb5277d9d15493b6e544b5945a889e6`**. `bin/dd_assumptions_lint.py`: 0 vi phạm.
> - Đầu vào số: `model/model_rev4_inputs.json`, md5 `d84427edf31fb7b677ca866b14640f2e`.
> - Mô hình: `model/calc_rev4.py`, md5 `2d16371e59a57e16bfc40d70373abca7`. Output: `model/calc_rev4_output.txt`.
> - Pha sau khoá: `model/postlock_rev4.py` → `postlock_rev4_output.txt`.
> - Số tôi tự đặt đều gắn nhãn **(ước lượng)**.

## 0. Kết luận rev4

**Tâm giá trị 32.376 đ/cp** (sau chiết khấu thanh khoản 10%; trước chiết khấu 35.974). **Vùng [3.630; 55.828]**. Mốc 0,85×tâm = 27.520.
- So với rev2 24.599: +31,6%. So với rev3 28.834: +12,3%.
- Một phương pháp SOTP cho cả ba kịch bản. Trọng số theo **tần suất 2017–2025: 2/9 – 6/9 – 1/9**.

| Kịch bản | Trọng số | Sau chiết khấu thanh khoản |
|---|---|---|
| Xấu | 2/9 | 3.630 |
| Cơ sở | 6/9 | 38.050 |
| Tốt | 1/9 | 55.828 |

- Giá tham chiếu 33.300 đ (18/11/2026, lấy từ rev2, KHÔNG truy vấn lại) = **1,03× tâm**. Nhãn: **quanh giá trị hợp lý** (không rẻ). Muốn tâm bằng giá thì biên gộp cơ sở cần 5,0%, so với trung vị 4,5%.
- Tâm rất nhạy với ba trục đều có chiều giảm:
  - Hạng mục bị kiểm toán ngoại trừ: xoá phần ở công ty con ⇒ 28.194; xoá thêm cả công ty liên kết ⇒ 24.460.
  - Quyết toán cổ phần hoá (khung ước lượng): 26.732–31.248.
  - Bảo lãnh cho Lilama 69-1 nếu có: 26.766–30.974.
- **Sizing V8:** ở giá ≈ tâm, không đề xuất mở vị thế. Nếu giá ≤ 27.520 ⇒ tối đa **2% NAV** (đáy dải 2–4%), vì kiểm toán ngoại trừ 3 năm liền, free float ~2% và thanh khoản ~0,45 tỷ/phiên.
- **WARNING** (không vào base):
  - Kiểm toán ngoại trừ 2023–2025; soát xét 6T/26 cũng ngoại trừ.
  - Quyết toán cổ phần hoá chưa được duyệt.
  - HNX duy trì diện cảnh báo.
  - Công ty con có ~330 tỷ vay quá hạn.

## 1. Đính chính so với rev trước

### 1A. Hạng mục skeptic r1 (đối với rev2) — đã xử lý ở rev3, giữ nguyên trong rev4 trừ chỗ ghi khác

| # | Hạng mục (chiều) | Bằng chứng | Xử lý |
|---|---|---|---|
| 1 | Dự phòng bảo hành 747,1 bị coi là nợ tiền mặt 100% (↑) | Roll-forward 9T/26 [HN TM23/31/33]: 980,110 + 148,883 − 376,018 − 2,337 − 747,099 ⇒ chi bằng tiền **3,54 tỷ (0,9%)** | (a) base: chỉ 25% số dư là chi bằng tiền (**ước lượng thận trọng**, gấp ~27 lần mức đo). Xấu 100%, tốt 10%. Phần không phải tiền × 0,8. Lưới (chỉ số dư): 0,9% ⇒ 33.643 · 25% ⇒ 32.351 · 50% ⇒ 31.010 · 100% ⇒ 28.328 |
| 2 | Hamon 160,4 tính 100% là nợ (↑) | [HN TM24] [KT25 p42 TM22]: đây là tiền đã thu từ bảo lãnh thực hiện HĐ (USD 6.175.500, Sông Hậu 1), treo vì Hamon phá sản. Còn phải trả Hamon Italia 163,4 [KT25 p38] | (b) base giữ là nợ. Kịch bản tốt ghi nhận 128,3 sau thuế. Nếu base cũng ghi nhận ⇒ 33.664 |
| 3 | DT base 4.500 không có backlog (↓) | Không tìm thấy phần giá trị của LLM trong QT II (HĐ 25.202 tỷ ký với liên danh PowerChina–Lilama) [Web]. Không tìm thấy công bố backlog | (a) base **DT 4.150 = TTM 4.145,5** (Q4/25 1.719,8 [BQ] + 9T/26 2.425,7 [HN]). Độ nhạy: 3.378 (kế hoạch 2026 của mẹ) ⇒ 30.382; 5.433 (FY2025) ⇒ 35.690 |
| 4 | Bảo lãnh của mẹ cho công ty liên kết (↓) | Đọc đủ thuyết minh [KT25 p22–57]: **không có** thuyết minh bảo lãnh/nợ tiềm tàng. TM26 p46 chỉ có thuê đất + ngoại tệ. TM39 p54: không có sự kiện sau. Lilama 69-1: VCSH −102,61, nợ quá hạn 496,97; ngân hàng kiện 69-1; BIDV bán nợ 69-1 [Web] | (c) **không kiểm chứng được tuyệt đối**. Độ nhạy nếu mẹ gánh 25/50/100% nợ quá hạn 69-1 ⇒ 30.974 / 29.571 / 26.766 |
| 5 | Tăng vốn 1.500/2.500 tỷ, giá chưa rõ | Không tìm thấy phương án/giá | V4a: NPV=0 nếu phát hành bằng giá trị. Phát hành 45 triệu cp mệnh giá 10.000 ⇒ 23.942 |
| 6 | Quỹ KTPL lãi 2026 chưa trừ (↓) | **rev4 sửa tỷ lệ, xem 1B-#2** | (a) base trừ 6,28% × 695,0 = 43,6; NOPAT × (1 − 6,28%) |
| 7 | HNA còn giữ không | [KT25 p28 TM4c]: tỷ lệ 3,71% tại cả 31/12/2025 và 01/01/2025 ⇒ đấu giá 07/2025 không bán. Q3/26 giá gốc 85,696 không đổi | (a) giữ 77,2. HNA = 0 ⇒ 31.505 |
| 8 | File khoá rev2 chứa giá LLM | — | File khoá rev3/rev4 không chứa giá |

### 1B. Hạng mục skeptic r2 (đối với rev3)

| # | Hạng mục (chiều) | Bằng chứng | Xử lý rev4 | Ảnh hưởng lên tâm |
|---|---|---|---|---|
| 1 | **Bảo hành trừ kép trong NOPAT** (↑, killer) | [KT25 p12]: chi phí bán hàng = 0 cả 2024 và 2025 ⇒ trước TT 99/2025, trích bảo hành nằm trong giá vốn, nên GPM lịch sử 4,5% **đã trừ trích bảo hành**. Phần không phải tiền về sau thành hoàn nhập vào thu nhập khác (bị loại khỏi GPM): **2024 19,61 + 2025 174,27 trên DT 6.101,3 + 5.432,6 = 1,68% DT** [KT25 p48] | (a) **Bỏ dòng trừ bảo hành riêng**. **Cộng lại hoàn nhập đo được 1,68% DT × 0,8** ở cơ sở và tốt; xấu 0. Không dùng tỷ lệ trích ngầm của 2025 (≥544,5 ≈ 10% DT) vì đó là năm quyết toán bất thường | +3.616 (0% ⇒ 28.760 → 1,68% ⇒ 32.376). Lưới tỷ lệ cộng lại: 0% ⇒ 28.760 · 1% ⇒ 30.913 · 1,68% ⇒ 32.376 · 3% ⇒ 35.218 |
| 2 | Tỷ lệ quỹ KTPL 12,8% đã cũ (↑) | [HN TM25]: NQ ĐHĐCĐ 232/NQ-ĐHĐCĐ 26/06/2026 phân phối LN 2025 gồm ĐTPT 242,306 và **KTPL 30,895** trên LNST mẹ 492,04 = **6,28%** | (a) tỷ lệ 6,28% (số thực tế gần nhất) | trừ 43,6 + NOPAT; tắt hẳn ⇒ 32.760 (+1,2%) |
| 3 | Hạng mục ngoại trừ chưa chạy lại trên khung rev3 (↓) | [KT25 p07–09]: công ty con = phải thu quá hạn 92,26 + tồn kho 246,69 + lãi vốn hoá 31,56 = **370,51**; công ty liên kết mã 252 = **330,77** | (b) độ nhạy trên khung rev4: xoá phần công ty con ⇒ **28.194 (−12,9%)**; xoá thêm liên kết ⇒ **24.460 (−24,4%)**; chỉ liên kết về 50% ⇒ 30.509. Không vào base (WARNING kiểm toán, không có cơ sở độc lập về mức tổn thất) | 0 ở base |
| 4 | Quyết toán CPH chưa duyệt, không có số (↓) | Không tìm thấy số tiền phải nộp NSNN / điều chỉnh vốn nhà nước trong BCTC hay web | (c) **không kiểm chứng được**. Khung (ước lượng, không có cơ sở): −100 / −300 / −500 tỷ ⇒ 31.248 / 28.990 / 26.732 | 0 ở base |
| 5 | Trọng số 25/50/25 không có neo | [BQ] LNST mẹ 2017–25: lỗ năm 2018 (−163,1) và 2019 (−78,0) = 2/9. GPM ≥7% chỉ năm 2025 [KT25 p12; BQ GPM] = 1/9 | (a) base **2/9 – 6/9 – 1/9** (tần suất, N = 9, nhỏ). Lưới: 25/50/25 ⇒ 33.889 · 40/45/15 ⇒ 26.949 · 50/40/10 ⇒ 22.618 · 10/50/40 ⇒ 41.719 | −1.513 so với 25/50/25 |
| 6 | Thời hạn thuê đất TM26 | [KT25 p46]: 124 Minh Khai thuê 50 năm; KCN Bắc Vinh tới 18/12/2048; Cơ khí Lắp máy (Ninh Bình) tới 01/07/2046; Lilama 7 trả một lần 40 năm | Không có hợp đồng nào hết hạn trong tầm nhìn định giá ⇒ không điều chỉnh | 0 |

## 2. Khung định giá rev4

**Công thức:** SOTP = NOPAT/r + (vị thế tài chính ròng sau nợ vận hành 1.466,16 + số dư bảo hành không phải tiền × 0,8 − quỹ KTPL chưa trích 43,6) × f + đầu tư tài chính dài hạn theo sổ 553,7 + HNA 77,2 + Hamon 128,3 (chỉ tốt) − tổn thất phải thu cũ 200 (chỉ xấu, ước lượng).
- **NOPAT** = 0,8 × (DT × GPM − QLDN + 1,68% × DT) × (1 − 6,28%).
- **Đầu vào chung:**
  - Vị thế tài chính ròng sau nợ vận hành 1.466,16: tiền + tiền gửi 3.576,4 − vay 620,7 = 2.955,75; NWC vận hành −1.489,59 [HN; skeptic r1 và r2 đã khớp].
  - r = 13,5%, g = 0, moat NONE.
  - Số cổ phiếu 79,726104 triệu.

| Kịch bản | DT | GPM | QLDN | Cộng lại hoàn nhập | Số dư bảo hành chi tiền | f | NOPAT | Trước / sau chiết khấu thanh khoản |
|---|---|---|---|---|---|---|---|---|
| Xấu 2/9 | — | — | — | 0 | 100% | 0,077 | −30 | 4.033 / 3.630 |
| Cơ sở 6/9 | 4.150 | 4,5% | 100 | 1,68% | 25% | 1 | 117,3 | 42.278 / 38.050 |
| Tốt 1/9 | 6.000 | 7% | 120 | 1,68% | 10% (+ Hamon) | 1 | 300,5 | 62.032 / 55.828 |

**Độ nhạy biên gộp cơ sở:**

| GPM cơ sở | 3% | 4% | 5% | 6% | 7% |
|---|---|---|---|---|---|
| Tâm | 29.775 | 31.509 | 33.244 | 34.978 | 36.713 |

## 3. V1 — r gắn lãi huy động

**r = 13,5%:**
- Lãi huy động 12T hiệu dụng = max(Big-4 12M 6,8% [16/11], CCTG 12M 7,40% [02/11]) = 7,40%, đúng bằng điểm neo 03/11 ⇒ Δ = 0.
- β = 1.

**Độ nhạy tâm theo lãi huy động:**

| Δ lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| β = 1 | 33.078 (+2,2%) | 32.714 (+1,0%) | 32.063 (−1,0%) | 31.771 (−1,9%) |
| β = 0,5 | 32.714 | 32.542 | 32.217 | 32.063 |

- Hai đầu dải Ke nội địa (D4): 12,3% ⇒ 33.232; 13,4% ⇒ 32.442.

## 4. V3 — thanh khoản (pha sau khoá)

- Tham chiếu rev2 (18/11): ADV trung vị 90 phiên ~0,45 tỷ/phiên; Bộ Xây dựng nắm 97,88% (HN TM25b) ⇒ free float ~2%.
- Không có dữ liệu Amihud hay thực thi độc lập ⇒ chỉ độ nhạy. Tâm báo ở mức 10%.

| Chiết khấu thanh khoản | 0% | 5% | 10% | 20% |
|---|---|---|---|---|
| Tâm | 35.974 | 34.175 | 32.376 | 28.779 |

- Vị thế áp dụng: 2% NAV. Mỗi 1 tỷ cần ~11–22 phiên (ước lượng) để thoát xong, ở tỷ lệ tham gia 10–20%.

## 5. V5 — 5F

5F đã làm ngày 18/11/2026 (<12 tháng ⇒ tái dùng rev2 §7): **NONE** (EPC_TRACK_RECORD_SOE).
- Kiểm nhanh: GPM FY2025 là 7,0%, FY2024 là 1,74% [KT25 p12] ⇒ biên vẫn dao động mạnh, giữ NONE.

## 6. V6 — hai nền (CHỈ HIỂN THỊ, không đổi tâm)

| V_ngắn | V_dài | D | Cờ |
|---|---|---|---|
| 9.965 | 54.216 | **1,69** | > ln3 ⇒ **phân kỳ mạnh**. Luật 0,85×tâm KHÔNG tự kích hoạt, cần Mike/user phán đoán |

- Nguồn chênh: CFO phồng nhờ vốn lưu động một lần (tạm ứng +657,8, xả tồn kho 440,9).
- Bỏ hai khoản này ⇒ V_dài 20.189, D 0,71.
- Vùng đọc hai nền: [9.965; 54.216].

## 7. Pháp lý / kiểm toán — WARNING (không vào base)

**Kiểm toán 2025 NGOẠI TRỪ** [KT25 p07–09]:
- (1) Công ty con Cơ khí Lắp máy / Lilama 5 / Lilama 7:
  - phải thu quá hạn 92,26; tồn kho 246,69;
  - Lilama 5: lãi quá hạn 74,01 + vay BIDV quá hạn 182,96;
  - Cơ khí Lắp máy: vốn hoá lãi 31,56.
- (2) Công ty liên kết 330,77.
- Nhấn mạnh: quyết toán CPH chưa duyệt.
- Độ nhạy ngoại trừ / CPH / bảo lãnh: xem §1B.

## 8. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)

**Tăng tâm:**
- BCTC năm 2026 cho thấy chi bảo hành bằng tiền <10% ⇒ ~33.150.
- Hamon được ghi nhận ⇒ +1.288.
- Có công bố phần giá trị của LLM trong QT II cho DT bền ≥5.400 ⇒ ~35.700.
- Một năm nữa có GPM ≥7% ⇒ nâng trọng số tốt.

**Giảm tâm:**
- Kiểm toán 2026 vẫn ngoại trừ và có tổn thất thực ở công ty con ⇒ ≤28.194.
- Quyết toán CPH buộc nộp NSNN ≥300 tỷ ⇒ ≤28.990.
- Lộ bảo lãnh cho 69-1 ⇒ 26.766–30.974.
- DT 2026 ≤3.400 ⇒ ~30.400.
- Tăng vốn ở mệnh giá ⇒ ~23.900.
- Năm 2026 lỗ cốt lõi.

**Theo dõi:** BCTC Q4/26 (~cuối 01/2027); BCTC KT 2026; đấu giá Lilama 69-1; phương án tăng vốn; cổ tức cổ phiếu 31,7% (sau chia: tâm/1,317 = **24.583**, vùng [2.756; 42.391]).

## 9. Không kiểm chứng được

| Hạng mục | Ảnh hưởng ước lượng lên tâm |
|---|---|
| Tỷ lệ chi bằng tiền của số dư bảo hành 2024–25 (BCTC năm không có roll-forward) | 25% ⇄ 100% = 32.351 ⇄ 28.328 |
| Tính bền của hoàn nhập 1,68% DT (mới có 2 năm) | 0% ⇒ 28.760 |
| Bảo lãnh ngoài bảng | 0 … −5.610 |
| Số tiền quyết toán CPH | 0 … −5.644 (khung ước lượng) |
| Phần giá trị/backlog của LLM ở QT II và Ô Môn I | Xem độ nhạy DT |
| Kết quả đấu giá HNA 07/2025 | Thuyết minh cho thấy còn giữ |

## Nguồn
- BCTC HN Q3/26 (txt: TM23 dòng 2895–2915; TM24 Hamon 2950–2980; TM25 phân phối LN ~3135–3150; TM31 3375–3395; TM33 3450–3460).
- BCTC KT HN 2025: p07–09, p12, p23, p28, p31, p38, p42, p44, p46, p48, p49, p54.
- BQ `ticker_financial` (`model/bq_fin_LLM.csv`: np/rev năm 2017–2025).
- QT II: https://vneconomy.vn/ky-hop-dong-epc-tri-gia-25202-ty-dong-cho-nhiet-dien-lng-quang-trach-ii.htm
- Lilama 69-1: https://baodauthau.vn/lilama-sap-dau-gia-411-von-tai-lilama-69-1-thach-thuc-vuc-day-doanh-nghiep-lo-lon-post210406.html ; https://baodauthau.vn/ngay-0162026-dau-gia-toan-bo-khoan-no-goc-lai-lai-phat-phi-cua-cong-ty-co-phan-lilama-69-1-tai-bidv-chi-nhanh-bac-ninh-post199575.html
- HNA: https://baodauthau.vn/lilama-thoai-von-loat-doanh-nghiep-don-luc-tai-co-cau-post178983.html
