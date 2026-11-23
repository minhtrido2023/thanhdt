# DD — LLM (Lilama, UPCoM) · REV 5 · 2026-11-23 · job `Taylor_20261123_120256`

> Chỉ nghiên cứu, không phải khuyến nghị mua. Không đặt lệnh. Pháp lý chỉ ghi WARNING.
>
> **Lịch sử bản:**
> - rev2 (`REPORT.md`, 18/11, tâm 24.599) → skeptic DD_GENERAL r1 **REFUTED**.
> - rev3 (`REPORT_rev3.md`, tâm 28.834) → r2 **REFUTED**.
> - rev4 (`REPORT_rev4.md`, tâm 32.376) → r3 **REFUTED** medium (`skeptic/r3_raw.md`).
> - **Rev5 = rev4 + xử lý toàn bộ hạng mục của r3 (§1C).** Vòng phản biện cuối của ca (user duyệt 23/11 19:00).
> - Mô tả doanh nghiệp, chất lượng lợi nhuận, 5F, pháp lý ở rev2 §3–§7, §11 giữ nguyên trừ điểm sửa dưới đây. Bảng §1A/§1B của rev4 vẫn hiệu lực.
>
> **Ký hiệu nguồn:**
> - **[HN]** BCTC hợp nhất Q3/26, `src/bao_cao_tai_chinh_hop_nhat_q3.2026_vie-da_nen.{pdf,txt}` (txt = OCR, dòng trích dẫn ở mục Nguồn).
> - **[KT25 pX]** BCTC hợp nhất kiểm toán 2025 (AASC), `src_r2/llm_25cn_bctc_hn_da_kt_signed.pdf`, md5 `9be1160b5c2ffca6683ff765ce00ade7`; ảnh trang `png/kt25full/pXX.png`.
> - **[BQ]** `tav2_bq.ticker_financial` (`model/bq_fin_LLM.csv`: cột `div1y`, `rev`, `np` theo quý).
>
> **Khoá giả định MÙ GIÁ** (không truy vấn giá LLM; giá tham chiếu chỉ dùng ở pha sau khoá):
> - `model/assumptions_LLM_20261123_rev5.json`, md5 **`bbfd4da597c17c46e751d2c98504ffd6`**. `bin/dd_assumptions_lint.py`: 0 vi phạm.
> - Đầu vào: `model/model_rev5_inputs.json`, md5 `3e5d558f19a889d8ee1d5a5cfdaae076`.
> - Mô hình: `model/calc_rev5.py`, md5 `3d57009047a175155d38b7b9563e71ae`. Output: `model/calc_rev5_output.txt`.
> - **Control leg:** `calc_rev5.py` chạy lại đúng công thức rev4 ⇒ **32.376** (khớp số pin rev4).
> - Pha sau khoá: `model/postlock_rev5.py` → `postlock_rev5_output.txt`.
> - Số tôi tự đặt đều gắn nhãn **(ước lượng)**.

## 0. Kết luận rev5

**Tâm giá trị 20.978 đ/cp** (sau chiết khấu thanh khoản 10%; trước chiết khấu 23.309). **Vùng [8.163; 38.007]**. Mốc 0,85×tâm = 17.831.
- So với rev4 32.376: **−35,2%**. Chiều GIẢM, lý do chính: trục tiền mắc kẹt nay được neo vào lịch sử phân phối tiền thật 2017–2026 (§1C-#1), áp cho cả ba kịch bản thay vì chỉ kịch bản xấu.
- Trọng số giữ **2/9 – 6/9 – 1/9** (tần suất năm lỗ / năm biên cao 2017–25). Kịch bản xấu nay CHỈ là "lỗ vận hành" — khớp với neo tần suất của nó.

| Kịch bản | Trọng số | Trước / sau chiết khấu thanh khoản |
|---|---|---|
| Xấu (lỗ vận hành) | 2/9 | 9.070 / 8.163 |
| Cơ sở | 6/9 | 24.901 / 22.411 |
| Tốt | 1/9 | 42.230 / 38.007 |

**Trục quyết định = hazard giải phóng tiền p** (0 sự kiện phân phối gốc trong 9 năm; p cơ sở = Laplace 1/11, là lựa chọn estimator — **ước lượng**):

| Ước lượng p | p/năm | f tiền | f đầu tư DH | Tâm |
|---|---|---|---|---|
| MLE (không bao giờ giải phóng) | 0 | 0,076 | 0,311 | 11.612 |
| Jeffreys | 0,05 | 0,326 | 0,497 | 17.902 |
| **Laplace (cơ sở)** | **0,091** | **0,448** | **0,588** | **20.978** |
| Giả định | 0,20 | 0,628 | 0,722 | 25.507 |
| Cận trên 95% (quy tắc 3/N) | 0,333 | 0,734 | 0,801 | 28.177 |
| Không mắc kẹt (f = 1, như base rev4) | — | 1 | 1 | 34.886 |

- Giá tham chiếu 33.300 đ (18/11/2026, lấy từ rev2, KHÔNG truy vấn lại) = **1,59× tâm**. Nhãn: **trên giá trị hợp lý (đắt)**.
  - Nhãn này **vững theo trục p**: mọi ước lượng p dựng từ dữ liệu (kể cả cận trên 95%, 28.177) đều cho tâm < giá. Chỉ khi bỏ hẳn giả thiết mắc kẹt (f = 1, trái với hồ sơ 9 năm) tâm mới vượt giá (34.886).
  - Muốn tâm = giá cần p ≈ 1,85/năm, tức thị trường đang ngầm định tiền được giải phóng trong ~6 tháng. Không có bằng chứng nào cho sự kiện đó.
- Doanh thu cơ sở 4.150 (TTM) hiển thị cạnh mức mùa vụ 2026E **3.490 ⇒ tâm 19.405** và nhịp tuyến tính 9T/26 3.234 ⇒ 18.796 (§1C-#5).
- **Sizing V8:** ở giá ≈ 1,59× tâm, **không mở vị thế**. Chỉ xem xét khi giá ≤ 17.831 (0,85×tâm), tối đa **2% NAV** (đáy dải 2–4%): kiểm toán ngoại trừ 3 năm liền, free float ~2%, thanh khoản ~0,45 tỷ/phiên.
- **WARNING** (không vào base): kiểm toán ngoại trừ 2023–2025 + soát xét 6T/26 ngoại trừ; quyết toán CPH chưa duyệt; HNX duy trì cảnh báo; công ty con ~330 tỷ vay quá hạn.

## 1. Đính chính so với rev trước

### 1C. Hạng mục skeptic r3 (đối với rev4)

| # | Hạng mục (chiều skeptic nêu) | Bằng chứng độc lập | Loại xử lý | Ảnh hưởng lên tâm |
|---|---|---|---|---|
| 1 | **Trục f tiền mắc kẹt không có neo; trọng số 2/9 là tần suất năm lỗ — sự kiện khác** (killer, ±10%) | **Cổ tức tiền 2017–25 (đ/cp):** 225 / 600 / 400 / 400 / 200 / 100 / 100 / 450 / 350 [BQ `div1y` dòng Q4]. **Đối chiếu kiểm toán:** LCTT mã 36 năm 2024 = 35,776 tỷ (448,7 đ/cp), năm 2025 = 27,850 tỷ (349,3 đ/cp) [KT25 p13] ⇒ khớp BQ 2/2 năm. **9T/26 chi 5,244 triệu đ** [HN LCTT mã 36]. **Phân phối LN 2025** (NQ 232/NQ-ĐHĐCĐ 26/06/2026): chỉ ĐTPT 242,306 + KTPL 30,895, **không có cổ tức tiền** dù LNST mẹ kỷ lục 492,04 [HN TM25]. Số cp không đổi 79.726.104 [HN TM25d]. Cổ tức trả theo tỷ lệ cho mọi cổ đông ⇒ cơ chế mắc kẹt KHÔNG phải loại trừ cổ đông thiểu số, mà là quy mô chi trả rất nhỏ so với khối tiền: bình quân ~314 đ/cp/năm so với vị thế tài chính ròng ~18.390 đ/cp. **0 lần phân phối gốc trong 9 năm.** **Lợi suất thực nhận trên tiền:** 2024 1,45%; 2025 1,18% [KT25 TM29 p47, cận trên]; 9T/26 1,28% [HN TM29] ⇒ trung vị 1,28% | (a) Tách trục f khỏi kịch bản xấu. Áp **chung** cho cả 3 kịch bản: f(p) = (y sau thuế + p)/(r + p) — tài sản phi hoạt động sinh lợi y cho tới khi được giải phóng theo mệnh giá với hazard p/năm. y tiền = 1,28%×0,8; p cơ sở = Laplace (0+1)/(9+2) = 0,091 (**ước lượng** — lựa chọn estimator trên N=9, 0 sự kiện; lưới ở §0) | Bỏ f riêng của kịch bản xấu: **+3.395** (32.376 → 35.771, đúng tính toán +10,5% của skeptic). f tiền 0,448 cả 3 kịch bản: **−10.977** |
| 1b | Hệ quả nhất quán của #1: đầu tư tài chính dài hạn 553,7 + lãi ẩn HNA 77,2 cũng là tài sản phi hoạt động không được phân phối | Cổ tức nhận: 2024 23,283; 2025 19,196 [KT25 TM29 p47]; 9T/26 17,441 (năm hoá 23,25) [HN TM29] ⇒ trung vị 4,2% trên sổ 553,7; cổ tức giữa doanh nghiệp không chịu thuế TNDN | (a) cùng công thức, f đầu tư = 0,588 | **−2.931** |
| 2 | Số dư bảo hành (75%×747,1×0,8) chồng với cộng lại hoàn nhập vĩnh viễn 1,68% DT (−1,3…−7,1%) | Nhịp hoàn nhập 9T/26 = 376,018 + 2,337 = 378,355 trong 0,75 năm ⇒ 504,5/năm [HN TM23/31/33] ⇒ số dư 747,1 chạy hết sau **1,48 năm** | (a) cộng lại dòng 1,68% DT chỉ bắt đầu sau 1,48 năm (hệ số PV 0,829), giữ tín dụng số dư | **−598** (bậc cầu trên khung f=1). Không hoãn ⇒ 21.576 |
| 3 | Tỷ lệ cộng lại 1,68% chỉ dựa N=2 năm (hai chiều) | 2024 0,32%; 2025 3,2%; tính cả 9T/26 ~4,1% (skeptic) | (b) giữ 1,68% (trung bình 2 năm kiểm toán), lưới: 0% ⇒ 18.078 · 1% ⇒ 19.804 · 3% ⇒ 23.256 · 4,1% ⇒ 25.155 | 0 ở base |
| 4 | Chưa trừ phần LN cổ đông không kiểm soát (~−1%) | 9T/26: LNST 718,515 = mẹ 694,979 + CĐKKS 23,536 [HN KQKD] ⇒ **3,28%** (9T/25 CĐKKS âm −5,56 ⇒ tỷ lệ đổi dấu theo năm) | (a) NOPAT × (1 − 3,28%) | **−287**. NCI = 0 ⇒ 21.245 |
| 5 | DT TTM 4.150 dựa vào Q4/25 chiếm 41% TTM (~−7%) | Tỷ trọng Q4 trong DT năm 2018–25 [BQ]: 21,2 / 33,1 / 29,3 / 19,0 / 39,3 / 47,9 / 16,5 / 31,7% ⇒ trung vị **30,5%**; Q4/25 = 31,7% DT 2025 ≈ trung vị ⇒ **không bất thường về mùa vụ**. 41% TTM là do 9T/26 yếu, không phải Q4/25 phình. Mức mùa vụ 2026E = 2.425,7/(1−0,305) = **3.490**. DT 2019–25 trung vị 5.432,5 | (b) giữ base TTM 4.150 (nằm giữa 2026E 3.490 và trung vị 7 năm 5.433); **hiển thị 2026E cạnh base ở §0** | 0 ở base. 3.490 ⇒ 19.405 · 3.234 ⇒ 18.796 · 5.433 ⇒ 24.034 |
| 6 | Đổi nhận định qua các bản (attack 6) | Rev2→rev3→rev4 tăng; rev5 GIẢM 35,2%, toàn bộ do bằng chứng cổ tức/lãi thực nhận mới đọc ở vòng này (§1C-#1, #1b) | — | Cầu đầy đủ §2 |

**Không kiểm chứng được (c):** khả năng Nhà nước thoái vốn / chào mua công khai để giải phóng tiền (không có tài liệu nào trong `src/`, `src_r2/` hay BCTC). Ảnh hưởng: đã nằm trong lưới p (§0). p 0,091 → 0,2 ⇒ tâm +4.529 (20.978 → 25.507).

## 2. Khung định giá rev5

**Công thức** (cho mỗi kịch bản k):
- Giá trị = NOPAT lõi/r + NOPAT cộng lại/r × (1+r)^−1,48 + **f_tiền** × (vị thế tài chính ròng 1.466,16 + số dư bảo hành không phải tiền ×0,8 − quỹ KTPL chưa trích 43,6 − tổn thất phải thu 200 (chỉ xấu, ước lượng) + Hamon 128,3 (chỉ tốt)) + **f_đầu tư** × (ĐTTC dài hạn theo sổ 553,7 + HNA 77,2).
- NOPAT lõi = 0,8 × (DT × GPM − QLDN) × (1 − 6,28%) × (1 − 3,28%); xấu = −30.
- NOPAT cộng lại = 0,8 × 1,68% × DT × (1 − 6,28%) × (1 − 3,28%); xấu = 0.
- Mọi khoản trừ độ nhạy (ngoại trừ, CPH, bảo lãnh) đi ra từ khối tiền ⇒ cũng nhân f_tiền.
- r = 13,5%, g = 0, moat NONE. Số cp 79,726104 triệu.

| Kịch bản | DT | GPM | QLDN | Cộng lại | Bảo hành chi tiền | f tiền / f đầu tư |
|---|---|---|---|---|---|---|
| Xấu 2/9 | — | — | — | 0 | 100% | 0,448 / 0,588 |
| Cơ sở 6/9 | 4.150 | 4,5% | 100 | 1,68% (hoãn 1,48 năm) | 25% | 0,448 / 0,588 |
| Tốt 1/9 | 6.000 | 7% | 120 | 1,68% (hoãn 1,48 năm) | 10% (+ Hamon) | 0,448 / 0,588 |

**Cầu rev4 → rev5 (tâm sau chiết khấu thanh khoản):**

| Bước | Tâm |
|---|---|
| rev4 (control, tái lập) | 32.376 |
| Bỏ f riêng của kịch bản xấu (f = 1 cả 3) | 35.771 |
| + NCI 3,28% | 35.484 |
| + hoãn cộng lại bảo hành 1,48 năm | 34.886 |
| + f tiền (p Laplace) | 23.909 |
| + f đầu tư dài hạn = **rev5** | **20.978** |

**Độ nhạy khác:**
- GPM cơ sở 3% / 4% / 5% / 6% / 7% ⇒ 18.461 / 20.139 / 21.817 / 23.494 / 25.172.
- Lợi suất tiền 1,18% / 1,45% ⇒ 20.907 / 21.097.
- Số dư bảo hành chi tiền 0,9% / 50% / 100% ⇒ 22.159 / 20.676 / 19.165.
- Trọng số 25/50/25 ⇒ 22.748; 40/45/15 ⇒ 19.051.
- **LN giữ lại cũng bị kẹt như tiền tồn** (không vào base, (b)): payout 38% ⇒ 18.092; payout 0% (như LN 2025) ⇒ 16.323. Base giữ NOPAT/r vì vốn giữ lại được dùng cho vốn lưu động EPC (công ty đang có kế hoạch TĂNG vốn 1.500–2.500 tỷ — dấu hiệu hấp thụ vốn, không phải thừa).
- HNA = 0 ⇒ 20.465.

## 3. V1 — r gắn lãi huy động

r = 13,5%: lãi huy động 12T hiệu dụng = max(Big-4 12M 6,8% [16/11], CCTG 12M 7,40% [02/11]) = 7,40% = điểm neo 03/11 ⇒ Δ = 0; β = 1. (r cũng đi vào f(p).)

| Δ lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| β = 1 | 22.256 (+6,1%) | 21.597 (+3,0%) | 20.394 (−2,8%) | 19.844 (−5,4%) |
| β = 0,5 | 21.597 | 21.283 | 20.682 | 20.394 |

Hai đầu dải Ke nội địa: 12,3% ⇒ 22.532; 13,4% ⇒ 21.099.

## 4. V3 — thanh khoản (pha sau khoá)

ADV trung vị 90 phiên ~0,45 tỷ/phiên (rev2, 18/11); Bộ Xây dựng 97,88% [HN TM25b] ⇒ free float ~2%. Không có Amihud/thực thi độc lập ⇒ chỉ độ nhạy; tâm báo ở 10%.

| Chiết khấu thanh khoản | 0% | 5% | 10% | 20% |
|---|---|---|---|---|
| Tâm | 23.309 | 22.143 | 20.978 | 18.647 |

Vị thế tối đa 2% NAV; mỗi 1 tỷ cần ~11–22 phiên để thoát ở tỷ lệ tham gia 10–20% (ước lượng).

## 5. V5 — 5F

5F làm 18/11/2026 (<12 tháng ⇒ tái dùng rev2 §7): **NONE** (EPC_TRACK_RECORD_SOE). GPM FY2025 7,0% vs FY2024 1,74% [KT25 p12] ⇒ biên vẫn dao động mạnh, giữ NONE.

## 6. V6 — hai nền (CHỈ HIỂN THỊ, công thức giữ nguyên rev4)

V_ngắn 9.965 · V_dài 54.216 · **D = 1,69** > ln3 ⇒ phân kỳ mạnh; luật 0,85×tâm KHÔNG tự kích hoạt. Bỏ vốn lưu động một lần (tạm ứng +657,8, xả tồn kho 440,9) ⇒ V_dài 20.189, D 0,71. Ghi chú: V_dài 20.189 (sau làm sạch) gần tâm rev5 20.978.

## 7. Pháp lý / kiểm toán — WARNING (không vào base)

Kiểm toán 2025 NGOẠI TRỪ [KT25 p07–09]: (1) công ty con Cơ khí Lắp máy / Lilama 5 / Lilama 7 — phải thu quá hạn 92,26, tồn kho 246,69, Lilama 5 lãi quá hạn 74,01 + vay BIDV quá hạn 182,96, CKLM vốn hoá lãi 31,56; (2) công ty liên kết 330,77. Nhấn mạnh: quyết toán CPH chưa duyệt.

| Độ nhạy (khoản trừ nhân f tiền 0,448; ở mệnh giá trong ngoặc) | Tâm |
|---|---|
| Xoá hạng mục ngoại trừ ở công ty con 370,51 | 19.105 (16.795) |
| + xoá liên kết 330,77 (f tiền / f đầu tư) | 17.433 / 16.908 |
| Quyết toán CPH −100 / −300 / −500 (ước lượng khung, không có cơ sở) | 20.472 / 19.461 / 18.450 (CPH 300 ở mệnh giá: 17.591) |
| Bảo lãnh 69-1 nếu có 25 / 50 / 100% × 496,97 | 20.350 / 19.722 / 18.466 (100% ở mệnh giá: 15.368) |

## 8. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)

**Tăng tâm:**
- Có quyết định chi cổ tức tiền lớn / thoái vốn Nhà nước / chào mua công khai ⇒ p tăng; p = 0,2 ⇒ 25.507; f = 1 ⇒ 34.886.
- LN 2026 (695 tỷ mẹ 9T) được chia bằng tiền ≥50% ⇒ đánh giá lại p.
- Hamon được ghi nhận ở mọi kịch bản ⇒ 21.554 (+576; 128,3 × f tiền).
- Công bố phần giá trị của LLM trong QT II đỡ DT bền ≥5.400 ⇒ ~24.000.

**Giảm tâm:**
- ĐHĐCĐ 2027 lại không chia cổ tức tiền ⇒ chuỗi 0 kéo dài, p tiến về Jeffreys/MLE ⇒ 17.902 / 11.612.
- Kiểm toán 2026 vẫn ngoại trừ có tổn thất thực ⇒ ≤19.105.
- Lộ bảo lãnh 69-1 ⇒ 18.466–20.350.
- DT 2026 ≤3.490 ⇒ ≤19.405. Năm 2026 lỗ cốt lõi.
- Tăng vốn 45 triệu cp ở mệnh giá ⇒ 16.656 (V4a: vốn mới cho dự án = NPV0, tính theo tiền thu về).

**Theo dõi:** BCTC Q4/26 (~cuối 01/2027); ĐHĐCĐ 2027 (phân phối LN 2026); BCTC KT 2026; đấu giá Lilama 69-1; phương án tăng vốn; cổ tức cổ phiếu 31,7% (sau chia: tâm/1,317 = **15.928**, vùng [6.198; 28.859]).

## 9. Không kiểm chứng được

| Hạng mục | Ảnh hưởng ước lượng lên tâm |
|---|---|
| Hazard giải phóng tiền p (0 sự kiện/9 năm; estimator) | 11.612 … 28.177 (MLE … cận trên 95%) |
| Tỷ lệ chi tiền của số dư bảo hành 2024–25 | 22.159 … 19.165 |
| Tính bền của cộng lại 1,68% DT | 0% ⇒ 18.078; 4,1% ⇒ 25.155 |
| Bảo lãnh ngoài bảng (69-1) | 0 … −2.512 (nhân f) |
| Số tiền quyết toán CPH | 0 … −2.528 (khung ước lượng, nhân f) |
| Phần giá trị/backlog của LLM ở QT II, Ô Môn I | Xem độ nhạy DT |
| Cổ tức `div1y` 2017–2023 | Chỉ BQ (chưa đối chiếu BCTC từng năm); 2024–25 đã khớp kiểm toán. Dù 2017–23 sai, kết luận "0 phân phối gốc" đứng vững vì tổng chi 2017–25 (~225 tỷ) ≪ khối tiền |

## Nguồn
- BCTC HN Q3/26 (txt OCR): LCTT mã 33–36 dòng 690–712 (cổ tức đã trả 5.244.000 / 112.710.141); KQKD LNST/CĐKKS dòng 518–520; TM23 2895–2915; TM25 phân phối LN 3117–3150, cổ tức phải trả 3178–3205; TM29 doanh thu tài chính 3310–3325.
- BCTC KT HN 2025: p07–09, p12, p13 (LCTT mã 36: 27.849.729.900 / 35.775.942.300), p14 (tiền cuối năm 2.699,17 / 2.976,47 / 2.738,04), p47 (TM29: lãi tiền gửi 33.452.287.939 / 41.438.199.363; cổ tức nhận 19.195.550.394 / 23.283.352.000), p23, p28, p38, p42, p46, p48.
- BQ `ticker_financial` (`model/bq_fin_LLM.csv`): `div1y`, `rev`, `np` theo quý 2017Q2–2026Q3.
- Nguồn web của rev4 giữ nguyên (QT II, Lilama 69-1, HNA).
