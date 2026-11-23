# DD — LLM (Lilama, UPCoM) · REV 3 · 2026-11-23 · job `Taylor_20261123_001048`

> Chỉ là nghiên cứu, không phải khuyến nghị mua. Không đặt lệnh. Pháp lý chỉ ghi WARNING.
> Bản này **thay khung định giá** của rev2 (`REPORT.md`, 18/11, tâm 24.599). Rev2 bị fundamental-skeptic DD_GENERAL r1 (22/11) phán **REFUTED** (`skeptic/r1_raw.md`).
> Phần mô tả doanh nghiệp, chất lượng lợi nhuận, 5F, pháp lý ở rev2 §3–§7, §11 vẫn giữ nguyên, trừ các điểm sửa ở §1 dưới đây.
>
> **Ký hiệu nguồn:**
> - **[HN]** BCTC hợp nhất Q3/26, `src/bao_cao_tai_chinh_hop_nhat_q3.2026_vie-da_nen.{pdf,txt}`.
> - **[KT25 pX]** BCTC hợp nhất kiểm toán 2025 (AASC, báo cáo 310325.015/BCTC.KT2 ngày 31/03/2026), `src_r2/llm_25cn_bctc_hn_da_kt_signed.pdf`, md5 `9be1160b5c2ffca6683ff765ce00ade7`. Rev3 mới render đủ 57 trang ảnh ở `png/kt25full/`; pX là số trang PDF.
> - **[BQ]** `tav2_bq.ticker_financial`.
> - **[Web]** URL ở mục Nguồn.
>
> **Khoá giả định MÙ GIÁ** (không truy vấn giá LLM trước khi khoá):
> - `model/assumptions_LLM_20261123_rev3.json`, md5 **`1324555180a92b84938ace205922aa11`**. `bin/dd_assumptions_lint.py`: 0 vi phạm.
> - Đầu vào số: `model/model_rev3_inputs.json`, md5 `7116b6edee702a70b80f10b23ad21630`.
> - Mô hình: `model/calc_rev3.py`, md5 `f64e26defa3599c3255addc076da7ed8`. Output: `model/calc_rev3_output.txt`.
> - Pha sau khoá: `model/postlock_rev3.py` → `postlock_rev3_output.txt`.
> - Số do tôi tự đặt đều gắn nhãn **(ước lượng)**.

## 0. Kết luận rev3

**Tâm giá trị 28.834 đ/cp** (sau chiết khấu thanh khoản 10%; trước chiết khấu 32.038). **Vùng [3.630; 47.339]**. Mốc 0,85×tâm = 24.509.
- Tâm rev2 là 24.599, tức tăng **+17,2%**.
- Tâm được tính một phương pháp SOTP cho cả ba kịch bản, trọng số 25/50/25:

| Kịch bản | Trước chiết khấu thanh khoản | Sau chiết khấu thanh khoản |
|---|---|---|
| Xấu | 4.033 | 3.630 |
| Cơ sở | 35.760 | 32.184 |
| Tốt | 52.599 | 47.339 |

- Giá tham chiếu 33.300 đ (18/11/2026, lấy từ rev2, KHÔNG truy vấn lại) = **1,155× tâm**: giá nằm TRÊN tâm 15,5%, trong vùng. Nhãn: **hơi đắt so với giá trị nội tại sau chiết khấu thanh khoản**.
  - Rev2 ghi 1,35× là quá nặng vì đã tính toàn bộ dự phòng bảo hành như nợ tiền mặt.
  - Muốn tâm bằng giá thì cần biên gộp cơ sở bền **8,2%**, so với trung vị 9 năm 4,5%.
- **Sizing V8:** không đề xuất mở vị thế ở giá hiện tại (giá > tâm). Nếu giá ≤ 24.509 (0,85×tâm) ⇒ tối đa **2% NAV** (đáy dải 2–4%), vì có kiểm toán ngoại trừ 3 năm liền, free float ~2% và thanh khoản thấp.
- **WARNING** (không đưa vào base):
  - Kiểm toán ngoại trừ 2023–2025 và soát xét 6T/26 cũng ngoại trừ.
  - Quyết toán cổ phần hoá chưa được duyệt.
  - HNX duy trì diện cảnh báo.
  - Công ty con có ~330 tỷ vay quá hạn.

## 1. Đính chính so với rev2 — từng hạng mục skeptic r1

| # | Hạng mục skeptic (chiều) | Bằng chứng mới | Xử lý rev3 | Ảnh hưởng lên tâm |
|---|---|---|---|---|
| 1 | Dự phòng bảo hành 747,1 bị coi là nợ tiền mặt 100% + NOPAT trừ thêm 45/năm ⇒ trừ hai lần (↑) | Xem §2 | **(a) vào base:** phần chi bằng tiền = **25% (ước lượng thận trọng)**, cùng tỷ lệ cho số dư và dòng hằng năm. Mức đo được chỉ 0,9%, tức base đệm gấp ~27 lần. Kịch bản xấu vẫn 100%, tốt 10%. Phần không phải tiền được cộng lại sau thuế 20% | Kịch bản cơ sở trước chiết khấu: 30.577 → 37.840 (+7.263) nếu chỉ sửa trục này. Tâm: lưới 100% ⇒ 23.090 so với 25% ⇒ 28.547 (+5.457) |
| 2 | Hamon 160,4 tính 100% là nợ, chưa lượng hoá (↑) | [HN TM24] [KT25 p42 TM22]: đây là tiền đã thu từ bảo lãnh thực hiện HĐ của Hamon (USD 6.175.500, Sông Hậu 1). Chưa ghi nhận thu nhập vì Hamon phá sản và nghĩa vụ/chi phí chưa xác định. Ngoài ra còn phải trả thương mại Hamon Italia 163,4 [KT25 p38] và phải thu Hamon 9,8 [KT25 p31] | **(b) kịch bản:** base giữ là nợ, khớp hạch toán, vì không có cơ sở độc lập về xác suất. Kịch bản tốt ghi nhận thu nhập 160,4×0,8 = 128,3. Độ nhạy cho base ghi nhận ⇒ tâm 29.920 | Tâm +362 đ/cp qua kịch bản tốt; nếu base ghi nhận thì +1.086 |
| 3 | Doanh thu base 4.500 không có backlog (↓) | Không tìm thấy phần giá trị của LLM trong QT II (HĐ 25.202 tỷ ký với liên danh PowerChina–Lilama, [Web vneconomy]). Không tìm thấy giá trị Ô Môn I; không có công bố backlog. Lilama 69-1 dự kiến thiếu việc năm 2027 [Web baodauthau 20/10] | **(a) vào base: DT 4.150 = TTM thực tế 4.145,5** (Q4/25 1.719,8 [BQ] + 9T/26 2.425,7 [HN]). Đây là điều chỉnh giảm có cơ sở (số báo cáo). Độ nhạy: 3.378 (kế hoạch 2026 của mẹ) ⇒ 27.877; 5.433 (FY2025 [KT25 p12]) ⇒ 30.424 | −434 đ/cp sau chiết khấu (so với 4.500) |
| 4 | Bảo lãnh ngoài bảng của mẹ cho công ty liên kết, chưa đọc (↓) | **Đã đọc đủ thuyết minh [KT25 p22–57]:** không có thuyết minh bảo lãnh/nợ tiềm tàng. TM26 (p46) chỉ có thuê đất + ngoại tệ. TM39 (p54): "Không có sự kiện trọng yếu…". Lilama 69-1: VCSH −102,61, nợ quá hạn 496,97; ngân hàng đã khởi kiện **69-1** và BIDV đấu giá khoản nợ 69-1 (01/06/2026) [Web] — nếu mẹ bảo lãnh thì chủ nợ có thể đòi mẹ thay vì bán nợ (suy luận, không phải bằng chứng) | **(c) không kiểm chứng được tuyệt đối** (VAS không buộc liệt kê, bảo lãnh có thể nằm trong hạn mức tín dụng 9.870 tỷ). Chỉ để độ nhạy: nếu mẹ gánh 25/50/100% nợ quá hạn 69-1 ⇒ tâm 27.431 / 26.029 / 23.224 | 0 ở base; −1.403…−5.610 ở độ nhạy |
| 5 | Tăng vốn 1.500/2.500 tỷ, giá chưa rõ | Không tìm thấy phương án/giá (NQ ĐHĐCĐ 2026 chỉ có tiêu đề trên stockbiz) | **V4a:** NPV=0 nếu phát hành bằng giá trị. Độ nhạy: phát hành 45 triệu cp mệnh giá 10.000 ⇒ 21.678 đ/cp | Base 0 |
| 6 | Quỹ khen thưởng phúc lợi trích từ lãi 2026 chưa trừ (↓, skeptic ước <2%) | [KT25 p44 TM25a]: phân phối LN 2024 gồm KTPL 11,352 + BĐH 0,546 trên LNST mẹ 92,695 = **12,8%**. [KT25 p49 TM36]: "chưa có dự tính trích Quỹ KTPL" trên LN 2025 | **(a) vào base:** trừ 12,8% × LN mẹ 9T/26 chưa trích 695,0 = **89,0** khỏi vị thế tài chính. NOPAT tương lai × (1 − 12,8%) | −753 đ/cp (tắt trục này ⇒ 29.587) |
| 7 | Số cp HNA còn giữ chưa kiểm (968 đ/cp) | [KT25 p28 TM4c]: giá gốc 85,696, tỷ lệ **3,71% tại cả 31/12/2025 và 01/01/2025**, tức sau phiên đấu giá 07/2025 vẫn còn giữ. Q3/26 giá gốc không đổi [HN]. Kết quả đấu giá không tìm thấy trên web | **(a) giữ trong base 77,2** (lãi ẩn sau thuế theo giá HNA — mã khác — của rev2). Độ nhạy HNA=0 ⇒ 27.963 | 0 (đã kiểm) |
| 8 | Giá LLM nằm trong file khoá rev2 (`price_today`) | — | File khoá rev3 **không chứa giá**. Giá chỉ xuất hiện ở pha sau khoá (`postlock_rev3.py`) | — |

**Cầu nối tâm cơ sở (trước chiết khấu thanh khoản):** 30.577 (rev2) → 37.840 (bảo hành 25% tiền, gồm cả dòng hằng năm) → 36.876 (DT 4.150) → **35.760** (quỹ KTPL).

## 2. Dự phòng bảo hành — bằng chứng (hạng mục nặng nhất)

**Roll-forward 9T/26** [HN TM23, TM31, TM33]:
- Đầu kỳ: 386,340 (ngắn hạn) + 593,770 (dài hạn) = **980,110**.
- Trích mới: +148,883 (chi phí bán hàng).
- Hoàn nhập: −376,018 (ghi giảm chi phí bán hàng theo TT 99/2025) và −2,337 (thu nhập khác).
- Cuối kỳ: 9,394 + 737,705 = **747,099**.
- ⇒ **Chi bằng tiền ≈ 3,54 tỷ**, tức 0,9% phần đã giải quyết (3,54 + 378,36).

**Lịch sử** [KT25]:
- Số dư 609,93 (31/12/24) → 980,11 (31/12/25) [p42 TM23].
- Hoàn nhập vào thu nhập khác: 174,27 (2025), 19,61 (2024) [p48 TM32].
- BCTC năm không trình bày roll-forward (phần sử dụng) ⇒ năm 2024–25 **không kiểm chứng được** tỷ lệ chi bằng tiền.
- Chính sách [KT25 p23 TM2.21]: trích **tối đa 5% giá trị công trình**; phần thừa khi hết hạn bảo hành được hoàn nhập ⇒ cơ chế này mang tính trích dư có hệ thống.

**Vì sao base vẫn để 25% chứ không 0,9%:**
- Chỉ có một cửa sổ đo được (9 tháng).
- Khiếu nại bảo hành ở EPC thường gộp cục.
- Ở Sông Hậu 1, nhà thầu phụ thiết bị Hamon đã phá sản ⇒ nghĩa vụ bảo hành thiết bị FGD/ESP có thể dồn lên LLM.
- Mức 25% là **ước lượng**. Lưới độ nhạy (áp cho cả ba kịch bản): 0,9% ⇒ 30.301 · 10% ⇒ 29.638 · 25% ⇒ 28.547 · 50% ⇒ 26.728 · 75% ⇒ 24.909 · 100% ⇒ 23.090.
- (Base rev3 dùng 100/25/10 theo xấu/cơ sở/tốt ⇒ 28.834.)

## 3. Khung định giá rev3 (không đổi phương pháp so với rev2)

**Công thức:** SOTP = NOPAT/r + (vị thế tài chính ròng sau nợ vận hành + phần bảo hành không phải tiền × 0,8 − quỹ KTPL chưa trích) × f + đầu tư tài chính dài hạn theo sổ 553,7 + lãi ẩn HNA 77,2 + Hamon (chỉ kịch bản tốt) − tổn thất phải thu cũ 200 (chỉ kịch bản xấu, ước lượng).

**Đầu vào chung:**
- Vị thế tài chính ròng sau nợ vận hành = **1.466,16**: tiền + tiền gửi 3.576,4 − vay 620,7 = 2.955,75; NWC vận hành −1.489,59 [HN, skeptic r1 đã khớp].
- Hệ số tiền mắc kẹt f: xấu 0,077 / cơ sở 1 / tốt 1.
- r = 13,5%, g = 0, moat NONE ⇒ không thưởng tăng trưởng.
- Số cổ phiếu 79,726104 triệu (mã 411).

| Kịch bản (trọng số) | DT | Biên gộp | QLDN | Bảo hành chi bằng tiền | NOPAT (sau quỹ KTPL) | Giá trị trước / sau chiết khấu thanh khoản |
|---|---|---|---|---|---|---|
| Xấu (25%) | — | — | — | 100% | −30 (như 2018–19) | 4.033 / 3.630 |
| Cơ sở (50%) | 4.150 (TTM) | 4,5% (trung vị TTM 2017Q3–2024Q4 [BQ]) | 100 | 25% (ước lượng) | 53,3 | 35.760 / 32.184 |
| Tốt (25%) | 6.000 (2024: 6.101) | 7% (năm 2025) | 120 | 10% + Hamon 128,3 | 205,1 | 52.599 / 47.339 |

**Trọng số 25/50/25** là mặc định, không có cơ sở định lượng. Lưới:
- 40/45/15 ⇒ 23.035
- 50/40/10 ⇒ 19.422
- 10/50/40 ⇒ 35.390
- 100% cơ sở ⇒ 32.184

**Vì sao biên 31% của 9T/26 không vào base:** biên này đến từ quyết toán một lần, đúng như công ty tự giải trình (rev2 §3). Độ nhạy biên gộp cơ sở:

| Biên gộp cơ sở | 3% | 4% | 5% | 6% | 7% |
|---|---|---|---|---|---|
| Tâm | 27.018 | 28.229 | 29.439 | 30.650 | 31.860 |

## 4. V1 — chi phí vốn gắn lãi huy động

**r = 13,5%:**
- Lãi huy động 12T hiệu dụng = max(Big-4 12M 6,8% [deposit_rate_vn_events 16/11], CCTG 12M 7,40% [02/11]) = **7,40%**, đúng bằng điểm neo 03/11 ⇒ Δ = 0.
- β = 1 (độ nhạy β 0,5).

**Độ nhạy tâm theo lãi huy động:**

| Δ lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| β = 1 | 29.305 (+1,6%) | 29.060 (+0,8%) | 28.624 (−0,7%) | 28.428 (−1,4%) |
| β = 0,5 | 29.060 | 28.945 | 28.727 | 28.624 |

- Độ nhạy thấp vì phần lớn giá trị là tiền/tài sản theo sổ, không phải dòng NOPAT.
- **D4 — hai đầu dải Ke nội địa:** Ke 12,3% ⇒ 29.408; 13,4% ⇒ 28.878.

## 5. V3 — thanh khoản (pha sau khoá)

- Dữ liệu tham chiếu từ rev2 (18/11): ADV trung vị 90 phiên ~15.200 cp ≈ 0,45 tỷ/phiên; Bộ Xây dựng nắm ~97,9% ⇒ free float ~2%.
- Không có dữ liệu Amihud hay số liệu thực thi độc lập ⇒ **chỉ độ nhạy**. Tâm báo ở mức 10% (giữ quy ước rev2).

| Chiết khấu thanh khoản | 0% | 5% | 10% | 20% |
|---|---|---|---|---|
| Tâm | 32.038 | 30.436 | 28.834 | 25.630 |

- Vị thế áp dụng: 2% NAV. Ở ADV 0,45 tỷ, với tỷ lệ tham gia 10–20%, mỗi 1 tỷ cần ~11–22 phiên (ước lượng) mới thoát xong.

## 6. V5 — 5F

5F đã làm đầy đủ ngày 18/11/2026 (<12 tháng ⇒ tái dùng, rev2 §7): **moat_tier NONE**, moat_type EPC_TRACK_RECORD_SOE. Rủi ro số 1: biên quyết toán 2025–26 bị coi là bền.

Kiểm nhanh 23/11:
- FY2025 kiểm toán [KT25 p12]: DT 5.432,6 (2024: 6.101,3), LN gộp 380,3 ⇒ GPM **7,0%**; năm 2024 chỉ 1,7%. Biên vẫn dao động mạnh, chưa thấy dấu hiệu biên mới bền ⇒ giữ NONE.

## 7. V6 — hai nền (CHỈ HIỂN THỊ, không đổi tâm)

| V_ngắn | V_dài | D | Cờ |
|---|---|---|---|
| 9.965 | 54.216 | **1,69** | > ln3 ⇒ **phân kỳ mạnh**. Luật 0,85×tâm KHÔNG tự kích hoạt, cần Mike/user phán đoán |

- Nguồn chênh: CFO 9T/26 phồng nhờ vốn lưu động một lần (tạm ứng QT II/Ô Môn +657,8, xả tồn kho 440,9).
- Bỏ hai khoản này ⇒ V_dài 20.189, D 0,71 (> ln2).
- Vùng đọc hai nền: [9.965; 54.216].
- C4 / D2 xem `calc_output.txt` rev2 (không đổi; "chưa qua tiêu chí khoá trước, chỉ theo dõi").

## 8. Pháp lý / kiểm toán — WARNING (không vào base)

**Ý kiến kiểm toán 2025:** NGOẠI TRỪ [KT25 p07–09].
- (1) Công ty con Cơ khí Lắp máy / Lilama 5 / Lilama 7:
  - phải thu quá hạn 92,26; tồn kho 246,69;
  - Lilama 5: lãi quá hạn 74,01 + vay BIDV quá hạn 182,96;
  - Cơ khí Lắp máy: vốn hoá lãi 31,56 (chi phí tài chính 2025 bị ghi thấp 10,24).
- (2) Công ty liên kết 45-3, 69-3, BĐS: mã 252 = 330,77, chưa đánh giá được.
- Nhấn mạnh: quyết toán cổ phần hoá chưa duyệt.

**Độ nhạy ngoại trừ** (rev2 §8b, khung cũ): xoá toàn bộ khoản mục công ty con bị ngoại trừ, thêm liên kết về 0 ⇒ giảm mạnh. Không bake vào base. Các khoản này đã trừ 100% nợ công ty con trong số hợp nhất.

## 9. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)

**Tăng tâm:**
- BCTC năm 2026 có roll-forward bảo hành cho thấy chi bằng tiền <10% ⇒ chuyển base về 10% (lưới §2: 28.547 → 29.638, +1.091).
- Hamon được ghi nhận thu nhập ⇒ +1.086.
- Công bố phần giá trị của LLM ở QT II cho thấy DT bền ≥5.400 ⇒ ~30.400.

**Giảm tâm:**
- Phát sinh chi bảo hành lớn (tỷ lệ tiền >50%) ⇒ ≤26.728.
- Lộ bảo lãnh của mẹ cho 69-1 / công ty con ⇒ 23.224–27.431.
- DT 2026 thực tế ≤3.400 ⇒ ~27.900.
- Tăng vốn ở mệnh giá ⇒ ~21.700.
- Ý kiến kiểm toán 2026 chuyển sang từ chối hoặc trái ngược.

**Theo dõi:** BCTC Q4/26 (~cuối 01/2027); kết quả đấu giá Lilama 69-1; NQ phương án tăng vốn; cổ tức cổ phiếu 31,7% (sau chia: tâm/1,317 = **21.894**, vùng [2.756; 35.944]).

## 10. Không kiểm chứng được (ghi thẳng)

| Hạng mục | Ảnh hưởng ước lượng lên tâm |
|---|---|
| Tỷ lệ chi bằng tiền của bảo hành 2024–25 (BCTC năm không có roll-forward) | 25% ⇄ 100% = 28.547 ⇄ 23.090 |
| Bảo lãnh ngoài bảng (không có thuyết minh) | 0 … −5.610 |
| Phần giá trị/backlog của LLM ở QT II và Ô Môn I | Xem độ nhạy DT §1 #3 |
| Kết quả đấu giá HNA 07/2025 | Thuyết minh cho thấy còn giữ; −871 nếu đã bán ở giá gốc |
| Phương án/giá tăng vốn | Xem §1 #5 |

## Nguồn
- BCTC HN Q3/26 (txt dòng 2895–2915 TM23; 2950–2980 TM24 Hamon; 3375–3395 TM31; 3450–3460 TM33).
- BCTC KT HN 2025: p07–09 ý kiến kiểm toán; p12 KQKD; p23 chính sách 2.21; p28 TM4c HNA; p31 TM8; p38 TM17; p42 TM22–23; p44 TM25a; p46 TM26; p48 TM31–32; p49 TM36; p54 TM39.
- QT II: https://vneconomy.vn/ky-hop-dong-epc-tri-gia-25202-ty-dong-cho-nhiet-dien-lng-quang-trach-ii.htm
- Lilama 69-1: https://baodauthau.vn/lilama-sap-dau-gia-411-von-tai-lilama-69-1-thach-thuc-vuc-day-doanh-nghiep-lo-lon-post210406.html ; https://baodauthau.vn/ngay-0162026-dau-gia-toan-bo-khoan-no-goc-lai-lai-phat-phi-cua-cong-ty-co-phan-lilama-69-1-tai-bidv-chi-nhanh-bac-ninh-post199575.html
- HNA: https://baodauthau.vn/lilama-thoai-von-loat-doanh-nghiep-don-luc-tai-co-cau-post178983.html
