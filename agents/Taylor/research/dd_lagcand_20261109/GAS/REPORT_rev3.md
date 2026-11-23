# DD — GAS (Tổng Công ty Khí Việt Nam – PV GAS) · rev3 · 23/11/2026 · job `Taylor_20261123_050003` (tiếp nối `Taylor_20261123_003454`)

Bản này dựng lại DD sau khi skeptic DD_GENERAL r1 (22/11/2026, `skeptic/r1.json`) phán **INCONCLUSIVE**. Các bản trước giữ nguyên: r2 `REPORT.md` (09/11) và r1 `REPORT_r1.md`.
Phạm vi: chỉ nghiên cứu; không đặt lệnh, không ghi sổ giá.
Định giá **mù giá thị trường**. Giá 74.100đ (BQ 06/11/2026) đã biết từ r1/r2 và chỉ dùng để dán nhãn sau khi khoá. Mọi thay đổi ở r3 đều dựa trên BCTC, không dựa trên giá (khoá: `calc/LOCK_prerun_r3.txt`).

**Nguồn (đều nằm trong `src/`):**
- BCTC HN Q3/2026, CBTT 30/10/2026: `src/GAS_Q3_2026_HN_VN.pdf`, trang đã render ở `src/png/vn_p*.png`.
- BCTC HN soát xét 6T/2026 của Deloitte: `src/GAS_H1_2026_HN_soatxet.pdf`, bản OCR ở `src/ocr_h1/`.
- **MỚI ở r3 — BCTC HN năm 2025 đã kiểm toán** (Deloitte): `src/dl_20261123/GAS_Baocaotaichinh_2025_Kiemtoan_Hopnhat.pdf`, md5 `a00baa0354470f10e936cbd04714950d`. Tải từ static2.vietstock.vn vì pvgas.com.vn trả 403. Bản OCR ở `src/dl_20261123/ocr/k*.txt`.
- BQ `ticker_financial`: `calc/bq_fin_gas.csv`, `calc/np_hist_gas.csv`.

**Về artefact bị TRIM** (skeptic nêu): các tệp `src/` PDF, `calc/model_out_r2.txt`, LOCK và CSV đầu vào hiện **có mặt trong cây làm việc**, vì đã được khôi phục ngày 19/11. Đã kiểm md5 PDF Q3 = `b81a07c7…`, khớp `LOCK_prerun_r2.txt`. Tệp nào r3 dùng thì md5 nằm trong `calc/LOCK_prerun_r3.txt`.

## 1. Kết luận
- **Giá trị nội tại sau chiết khấu thanh khoản (cỡ 5 tỷ):** tâm **50.651đ** · P10 **43.779** · P50 50.333 · P90 **58.770**.
  - So với r2: tâm 50.146 / P10 43.327 / P90 57.840, tức tâm **+1,0%**.
  - Trước chiết khấu: tâm 50.985 (P10 44.067, P90 59.157).
  - Cỡ 40 triệu: tâm 50.955.
- **Vùng giá (sau CK 5 tỷ):** rẻ < 43.800 · hợp lý 43.800–58.800 · đắt > 58.800.
- **Nhãn: TRÊN vùng (đắt) — đây là nhãn TƯƠNG ĐỐI THEO KHUNG, không đổi so với r2.**
  - Giá 74.100 cao hơn tâm 46,3% và cao hơn P90 26,1%. 100% trọng số lưới nằm dưới giá.
  - Ở r = 8% tâm là 68.043, vẫn dưới giá.
  - r ngụ ý từ giá = 6,95%. Ở r = 13,5%, giá ngụ ý LN tăng trưởng danh nghĩa vĩnh viễn **+5,2%/năm**.
  - P/E TTM 12,1x đang sát đáy 10 năm (11,7x). Khoảng cách giữa giá và tâm đến từ khung định giá (r danh nghĩa 13,5%, RONIC = Ke, có suy giảm), **không phải** từ việc mô hình ép LN thấp.
- **Rủi ro lớn nhất (WARNING, không đưa vào tâm):** GAS không còn đủ điều kiện công ty đại chúng (free float 4,24%, hạn khắc phục 31/12/2026). Thay Chủ tịch HĐQT và TGĐ hồi 07/2026.
  - **MỚI ở r3:** các hợp đồng mua khí Lô 05.2/05.3/05-1b/c và hợp đồng bán khí NCS cho NT2 đều **hết hạn 12/2026** (BCTC KT 2025, TM35).
- **Sizing (V8, chuẩn 2–4% NAV/mã):** giá nằm ngoài vùng giá trị nên DD **không đề xuất mở vị thế giá trị**. Nếu LAG vẫn mua theo cơ học thì đó là vị thế ăn theo đà LN; DD không ủng hộ vượt mức sàn 2% NAV.

## 2. Đính chính so với rev trước — từng hạng mục skeptic r1 → xử lý
Bậc cầu tích luỹ (đ/cp, sau CK 5 tỷ; số lấy từ `calc/model_out_r3.txt`, khoá `steps_cumulative_from_r2`):

| Bước | Tâm | P10 | P90 | Loại |
|---|---|---|---|---|
| r2 (09/11) | 50.146 | 43.327 | 57.840 | — |
| + trích quỹ KT-PL hằng năm 1,91% LN; dời mốc chiết khấu từ 09/11 sang 23/11 | 49.692 | 43.168 | 57.521 | (a) base |
| + dự phòng 343 chuyển từ trục 0/50/100% sang trừ 100% (D3) | 49.012 | 42.489 | 56.842 | (a) base |
| + góp vốn BCC Lô B 1.395,7 tỷ theo giá sổ (V4a) | 49.587 | 43.064 | 57.417 | (a) base |
| + quỹ KH&CN −235,9 tỷ | 49.490 | 42.967 | 57.320 | (a) base |
| + RES trừ phần khấu hao giảm (−536,8 tỷ/năm sau thuế) | 48.743 | 42.285 | 56.368 | (a) base |
| + chiết khấu giữa kỳ (= **r3**) | **50.651** | **43.779** | **58.770** | (a) base |

Riêng phần trích quỹ KT-PL: bỏ đi thì +631 đ/cp. Phần dời mốc chiết khấu không tách riêng. Hai mục cộng lại ≈ −454 đ/cp so với r2.

| # | Hạng mục skeptic r1 | Bằng chứng độc lập | Xử lý |
|---|---|---|---|
| M1 | ~10,2 nghìn tỷ tài sản chưa phân loại vận hành/ngoài vận hành | Phân loại **đủ từng dòng** BCĐKT 30/09/2026 (`calc/notes_bctc_r3.md`); tổng khớp VCSH CĐ mẹ 73.208,6 (lệch 0,2 do làm tròn). Tài sản ngoài cầu tiền ròng gồm: vốn lưu động hoạt động ròng 13.287,3; TSCĐ/BĐSĐT/chi phí trả trước dài hạn 15.441,3; dự án tăng trưởng 7.312,1; đầu tư LDLK 402,7; thuế hoãn lại ròng −253,7 | **(a)** Mục mới vào base: **phải thu dài hạn 1.395,7 = góp vốn BCC đường ống Lô B–Ô Môn** (TM38 Q3 p35; BCTC KT 2025 ghi "phải thu góp vốn theo BCC (i)" 1.022,1 tỷ tại 31/12/25, BCC 26a/2010, GAS 51%). Đây là dự án tăng trưởng, tính NPV 0 theo giá sổ (V4a): **+574**. Đầu tư LDLK 402,7: LN của chúng đã nằm trong chuỗi LN nên KHÔNG cộng (cộng sẽ tính hai lần, +166 chỉ để tham khảo). Vốn lưu động: coi là hoạt động (conv = 1, nằm trong NOPAT). Hai chiều của nó chỉ đưa vào **(b) độ nhạy**: quay về mức 01/01 thì +656; mất 10% phải thu PVPower thì −390 |
| M2 | ~2,3 nghìn tỷ nợ nằm ngoài cầu | Mọi dòng nợ đã gắn nhãn (bảng nợ trong `notes_bctc_r3.md`) | **(a)** Quỹ KH&CN 344 (235,9) trừ như nợ: **−97**. Các khoản 314, 315, 316, 311 v.v. là vốn lưu động hoạt động (TNDN phải nộp 2.196,4 là thuế dồn tích của LN 9T đã nằm trong NOPAT). Thuế hoãn lại ròng −253,7: **(b)** độ nhạy −104 |
| M3 | Capex cam kết Lô B / kế hoạch capex chưa mô hình, NPV 0 chưa kiểm | BCTC KT 2025 TM35: cam kết vốn còn lại Lô B–Ô Môn **12.394,4**, mở rộng kho LNG Thị Vải 1→3 triệu tấn **8.827,6**, ERP 16,7; tổng **21.238,7 tỷ** | Cả hai là dự án TĂNG TRƯỞNG nên base NPV 0 (V4a): phần còn phải chi đối ứng bằng giá trị tương đương. Cước ống Lô B / IRR được duyệt KHÔNG có trong BCTC, nên **không có cơ sở độc lập để lệch khỏi 0** ⇒ **(b)** độ nhạy NPV ±5% tổng cam kết = ±437 đ/cp, −10% = −874. Đây không phải capex tuân thủ |
| M4 | Không trích ý kiến kiểm toán FY2025 | `src/dl_20261123/ocr/k08.txt`: **Deloitte VN, 28/02/2026, CHẤP NHẬN TOÀN PHẦN**. Đoạn "Vấn đề khác" chỉ nói số so sánh 2024 do hãng khác kiểm toán (chấp nhận toàn phần 20/02/2025) | **(a)** đã trích. `audited_fy_missing = false` |
| M5 | Thuyết minh dự phòng 343 (3.300) chưa đọc | Soát xét 6T/2026 TM25 (`src/ocr_h1/p50.txt`): đây là **chi phí thu dọn, khôi phục, hoàn trả mặt bằng công trình khí**, gồm Bể Cửu Long 1.994,8 · PM3-Cà Mau 598,0 · GPP/ống/trạm 329,3 · NCS2-GĐ2 + Sao Vàng Đại Nguyệt 221,7 · Phú Mỹ–HCM 65,5 · khác 63,8 (= 3.273,1 tại 30/06). Dự toán do BCT duyệt (QĐ 1295/QĐ-BCT 2019, 2437/QĐ-BCT 2020, 610/QĐ-BCT 2023, 3754/QĐ-BCT 2016); trích theo sản lượng (`p24.txt`) | **(a)** Đây là chi BẮT BUỘC và không tạo doanh thu, nên theo **D3 là dòng tiền ra 100% giá sổ trong base** (bỏ trục 0/50/100): **−680** so với trục giữa. Thời điểm chi không công bố, nên chiết khấu PV chỉ là **(b)** độ nhạy: chi sau 10 năm thì +976 |
| M6 | Dòng tiền bên liên quan PVN | TM38 Q3/26 p35-36: phải thu KH **PVPower 8.870,4** (01/01: 4.003,3); phải thu khác PVPower 2.980,5; PVN: phải trả NB 3.582,6, chi phí phải trả 3.131,3, phí thương hiệu 163,4 (TM18); tiền gửi PVComBank 1.783,6. Nợ xấu PVPower gốc 1.523,5, chỉ thu hồi được 30,5 (TM7) | Đã định lượng. Tập trung phải thu PVPower là **rủi ro thu tiền** ⇒ **(b)** −390 đ/cp cho mỗi 10% bị mất. Không đưa vào base vì đã có dự phòng 1.833,8 và không có tín hiệu nợ mới quá hạn ngoài khoản đã dự phòng |
| M7 | Phát hành khắc phục free float, pha loãng | Chưa có NQ ĐHĐCĐ/HĐQT trong nguồn đã đọc | **(c) Không kiểm chứng được.** Định lượng cơ chế: để đạt 10% free float cần ≈ 154,4 triệu cp mới (6,4%). Ảnh hưởng = (giá phát hành − V) × X/(N+X): phát hành ở giá bằng V thì 0. Nếu PVN thoái vốn thay vì phát hành thì không pha loãng. Chỉ là WARNING |
| M8 | Hạn hợp đồng khí / giấy phép mỏ | BCTC KT 2025 TM35: mua khí Lô 05.2/05.3 (0,2506 tỷ m³/năm) và Lô 05-1b/c (1,508 tỷ m³/năm) **đến 12/2026**; Lô 102/106 đến hết giai đoạn bình ổn; LNG Shell 20,7 triệu MMBTU/năm 2027–2031; bán khí NCS cho NT2 0,6 tỷ m³/năm đến 12/2026 | Hạn hợp đồng: đã nêu, WARNING. Giấy phép mỏ: **(c) không kiểm chứng được** từ BCTC. Ảnh hưởng đã nằm trong trục suy giảm 0/1,4/2,8% và độ nhạy "suy giảm +3pp" = −5.162 |
| T1 | Hai chiều: RES tính khấu hao giảm là LN bền (−1,5%) | TM32: khấu hao 9T 1.691,2 so với 2.194,4 ⇒ −670,9 tỷ/năm trước thuế, −536,8 sau thuế. Mô hình giả định capex duy trì = khấu hao, nên phần này không được coi là LN bền | **(a)** RES 2.291 → **1.754** rồi mới áp trục 0/50/100%: **−747** (riêng lẻ). Không trừ thì +794 |
| T2 | Hai chiều: chiết khấu cuối kỳ (+4%) | Quy ước: dòng tiền phát sinh đều trong năm | **(a)** Chuyển sang chiết khấu **giữa kỳ** (2027 = 0,60; 2028 và TV = 1,60 năm): **+1.908** (+3,9%). Quay lại cuối kỳ thì −1.908 |
| T3 | Hai chiều: bao tiêu cộng lại nhưng trích trước mua khí 4.050,5 không đối xứng | Trích trước mua khí (TM18) là chi phí phải trả của lượng khí đã nhận, tức vốn lưu động hoạt động. Còn tiền khí trả trước bao tiêu (TM15) là khoản trả trước cho lượng khí chưa nhận, đang được thu hồi (2.122,6 → 1.775,5) | Giữ như r2. Hai khoản có bản chất khác nhau nên không đối xứng: khoản thứ nhất đã nằm trong vốn lưu động ròng. Đã ghi rõ trong bảng phân loại |
| T4 | RES có thể chứa lãi tồn kho LPG | Không tách được từ BCTC | **(b)** Giữ trục 0/50/100% cho RES; lỗ tồn kho −82 |
| P1 | Artefact bị TRIM, liên kết chết | Tệp đã có mặt lại; md5 đã kiểm | Đã khôi phục. r3 có LOCK + md5 riêng |
| E5 (mở từ r2) | Cổ tức phải trả lệch 540,7 tỷ | TM23: chia cổ tức 6.032,4 (CĐ mẹ) + 74,6 (CĐKKS); LCTT 9T đã trả 287,4; phải trả 5.491,7 | **(c) Vẫn chưa giải thích được hết**, tâm không đổi (dùng số bảng cân đối). Nếu 540,7 là đã chi thì tiền đã giảm tương ứng, không trừ hai lần |
| Mới | Trích quỹ KT-PL hằng năm (lint L13) | TM23 p27: trích quỹ 214,4 tỷ từ LN 2025 (11.212,5) = **1,91%** | **(a)** Nhân (1 − 1,91%) vào LN hoạt động mỗi năm: **−631** |

**Cơ chế B2:** tâm dịch +1,0% so với rev mà skeptic đã đọc, không đổi lớp nhãn. Phản biện lại vẫn chạy theo yêu cầu dispatch.

## 3. Giá trị nội tại — `calc/model_r3.py` (khung r2), khoá `calc/assumptions_r3.json` + `calc/lock_v1_r3.json` (lint strict 0 vi phạm)
**Cấu trúc:** Giá trị = các thành phần dưới đây cộng lại.
- Tiền ròng theo sổ: 39.654,7 tỷ.
- Cộng XDCB 5.916,4 và góp vốn BCC Lô B 1.395,7 (cả hai V4a, NPV 0).
- Cộng bao tiêu trả trước 1.775,5.
- Trừ quỹ KT-PL 875,6, quỹ KH&CN 235,9, dự phòng thu dọn 3.300 (D3).
- Cộng LN hoạt động Q4/26 (0,231 năm).
- Cộng NOPAT 2027–2028 chiết khấu giữa kỳ, cộng giá trị cuối kỳ = NOPAT₂₀₂₉/(r + suy giảm). RONIC = Ke; conv = 1.

LN hoạt động = hồi quy LN năm theo Brent năm (2016–2025: a = 2.240, b = 119,8, R² 0,68), trừ lãi tiền gửi sau thuế, cộng U × RES (RES đã trừ phần khấu hao giảm, nay = 1.754), rồi nhân (1 − 1,91%).
LN hoạt động tại các mức Brent: 62 ⇒ 9.175 · 72 ⇒ 10.350 · 85 ⇒ 11.877 tỷ/năm.
Tiền ròng kèm các khoản cộng/trừ trên = **19.740 đ/cp**.

**V1 — r = 13,5%**, neo lãi huy động 12T hiệu dụng 7,40% (`deposit_rate_vn.effective_deposit_rate('2026-11-23')` = CCTG 12T ngày 02/11, Big-4 6,8%), β = 1. Lãi huy động không đổi so với điểm neo nên r giữ nguyên.
- Độ nhạy theo lãi huy động: −100bp ⇒ 52.766 · −50bp ⇒ 51.671 · +50bp ⇒ 49.699 · +100bp ⇒ 48.807.
- Hai đầu dải Ke nội địa (D4, chỉ báo kèm; `calc/ke_band_r3.txt`): **r 12,3% ⇒ tâm 53.227** (P10 45.560, P90 62.329); **r 13,4% ⇒ tâm 50.850**. Tâm vẫn dùng r 13,5%.

| Kịch bản (w) | Brent Q4/26 · 2027 · 2028 · dài hạn | Suy giảm/năm | Giá trị (đ/cp, trục giữa, trước CK) |
|---|---|---|---|
| XẤU (0,275) | 95 · 72 · 62 · 62 | 2,8% | 45.296 |
| CƠ SỞ (0,45) | 100 · 85 · 75 · 72 | 1,4% | 51.348 |
| TỐT (0,275) | 105 · 100 · 85 · 82 | 0% | 58.566 |

**Lưới 81 kết cục** (kịch bản × hệ số Brent ±25% × Brent dài hạn ±5 × phần dư 0/50/100%; ARO đã bỏ khỏi lưới):
- Phân vị sau CK 5 tỷ: P10 43.779 · P25 46.518 · P50 50.333 · P75 54.545 · P90 58.770 · min 40.228 · max 63.814.

**Độ nhạy ngoài lưới** (đ/cp, sau CK; KHÔNG vào base):

| Độ nhạy | đ/cp |
|---|---|
| Truy thu cước ống tạm tính 1.500 tỷ | −618 |
| Lỗ tồn kho LPG | −82 |
| Cam kết vốn NPV −5% / −10% / +5% | −437 / −874 / +437 |
| Vốn lưu động về mức 01/01 | +656 |
| Mất 10% phải thu PVPower | −390 |
| Thuế hoãn lại ròng | −104 |
| Dự phòng thu dọn chi sau 10 năm | +976 |
| Chiết khấu cuối kỳ | −1.908 |
| Không trừ phần khấu hao giảm | +794 |
| Không trích quỹ KT-PL | +631 |
| Không suy giảm | +2.795 |
| Suy giảm +3pp | −5.162 |

**V6 — hai nền giá trị, CHỈ HIỂN THỊ** (`calc/v6_r3.txt`; không trộn vào tâm/vùng/sổ):

| Nền | Giá trị | Cách tính |
|---|---|---|
| V_ngắn | 32.009 | LNST chuẩn hoá = trung vị TTM 2023Q4–2026Q3 là 11.508 tỷ; g = −1,4% < 0 nên tái đầu tư chặn ở 0 |
| V_dài | 31.156 | FCFE 9T × 4/3 = 11.201 tỷ |
| V theo C4 | 38.493 | Nhãn "chưa qua tiêu chí khoá trước (2/4 chân trời), chi theo dõi" |

- D = 0,027 < ln2: không có cờ phân kỳ.
- Cả hai nền KHÔNG gồm tiền ròng theo sổ (19.740 đ/cp trong mô hình DD), nên không so trực tiếp với tâm.

**Đối chiếu P/E:** EPS TTM 6.110đ. Tâm r3 tương ứng 8,3x (P10 7,2x · P90 9,6x). P/E lịch sử 2016Q1–2026Q3 (43 quý, BQ): 11,7–26,5x, trung vị 15,6x.

## 4. Vị thế & lợi thế cạnh tranh (V5 / 5F) — tái dùng r2 (09/11/2026, < 12 tháng) + kiểm nhanh
- moat_tier **NARROW** · REGULATORY/INFRA · rủi ro số 1: mỏ cũ cạn cộng dịch chuyển sang LNG chuyển ngang biên mỏng. Bằng chứng định lượng: ROIC_Min10Y 13,8% so với Ke 13,5%. Đồng hồ cắt hào: CÓ (xem r2 §4).
- Kiểm nhanh r3 (1): các hợp đồng mua khí mỏ cũ (Lô 05.2/05.3/05-1b/c) **hết hạn 12/2026**. Điều này củng cố "đồng hồ đếm ngược" nhưng chưa đủ để đổi tầng; điều khoản gia hạn chưa biết.
- Kiểm nhanh r3 (2): cam kết vốn 21,2 nghìn tỷ (Lô B, kho LNG 3 triệu tấn) là nỗ lực thay thế nguồn khí. Trong base, nó ở NPV 0.

## 5. Điều làm nhận định đổi theo CẢ HAI chiều
**Lên:**
- LN quý 2027 ≥ 3.500 tỷ khi Brent ≤ 80. Mỗi +1.000 tỷ LN bền/năm ≈ +2.800 đ/cp.
- Cước ống Lô B / IRR công bố ≥ r. Hợp đồng khí 2027+ gia hạn với biên tương đương. Phải thu PVPower thu về (+656 khi vốn lưu động về mức 01/01). Lãi huy động giảm 100bp ⇒ +2.115.

**Xuống:**
- Brent < 75 hai quý liên tiếp và LN Q4/26 < 2.500 tỷ. Không gia hạn hợp đồng mỏ cũ sau 12/2026.
- Nợ PVPower phát sinh quá hạn mới (−390 mỗi 10%). Truy thu cước ống (−618). Hủy niêm yết.

**HARD ABANDON (với vị thế đã mua):** có quyết định hủy niêm yết, hoặc LN 4 quý < 9.500 tỷ khi Brent ≥ 80.

## 6. Thanh khoản / sizing (V3, V8) — sau khoá
- ADV trung vị 250 phiên 113,2 tỷ; σ ngày 3,11%.
- CK = σ·√(Q/ADV): **5 tỷ ⇒ 0,65%**; 40 triệu ⇒ 0,06%. Nhãn tính theo giá trị SAU CK.
- Thoát 5 tỷ ở mức tham gia 10% ≈ 0,44 phiên. Free float thực ~4,24% ⇒ thanh khoản phụ thuộc trạng thái niêm yết.
- Sizing V8: chuẩn 2–4% NAV/mã. Nhãn TRÊN vùng ⇒ không đề xuất vị thế giá trị; tối đa 2% NAV nếu LAG mua theo cơ học.

## 7. WARNING pháp lý / quản trị (không vào tâm)
- Free float 4,24% < 10% (CBTT 31/12/2025, hạn 1 năm). Kế hoạch khắc phục: không kiểm chứng được.
- Miễn nhiệm Chủ tịch (23/07/2026) và TGĐ (21/07/2026); ĐHĐCĐ bất thường 14/09/2026. Lý do: chưa kiểm.
- Kiểm toán: FY2025 Deloitte chấp nhận toàn phần (28/02/2026); soát xét 6T/2026 Deloitte chấp nhận toàn phần (12/08/2026).

## 8. Giả định [UL] / còn mở
- Trọng số 0,275/0,45/0,275, suy giảm 2,8/1,4/0%, Brent dài hạn ±5, hệ số Brent ±25%, phần dư 0/50/100% — đều [UL] đối xứng (như r2).
- **Không kiểm chứng được:** IRR/cước Lô B; tiến độ chi cam kết vốn; giấy phép mỏ; kế hoạch free float; lý do miễn nhiệm; phần 540,7 tỷ cổ tức; thời điểm chi thu dọn.

## 9. File
- `calc/notes_bctc_r3.md` — phân loại đủ BCĐKT và các sự kiện mới.
- `calc/assumptions_r3.json` · `calc/lock_v1_r3.json` · `calc/LOCK_prerun_r3.txt`.
- `calc/model_r3.py` → `calc/model_out_r3.txt`: 2 lần chạy cùng md5 `bfd33b94a4c9768447491c0b976adae2`.
- `calc/ke_band_r3.py` → `ke_band_r3.txt` · `calc/v6_r3.txt`.
- Bản cũ giữ nguyên: r2 `REPORT.md`, `calc/model_r2.py`, `assumptions_r2.json`.
