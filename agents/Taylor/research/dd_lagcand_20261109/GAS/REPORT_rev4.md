# DD — GAS (Tổng Công ty Khí Việt Nam – PV GAS) · rev4 · 23/11/2026 · job `Taylor_20261123_050003` (tiếp nối `Taylor_20261123_003454`)

Bản này dựng lại DD sau skeptic DD_GENERAL r1 (22/11, `skeptic/r1.json`, INCONCLUSIVE trên r2) và r2 (23/11, `skeptic/r2.json`, INCONCLUSIVE trên `REPORT_rev3.md`). rev4 = rev3 + các sửa ở §2A. Các bản trước giữ nguyên: `REPORT_rev3.md`, r2 `REPORT.md` (09/11), r1 `REPORT_r1.md`.
Phạm vi: chỉ nghiên cứu; không đặt lệnh, không ghi sổ giá.
Định giá **mù giá thị trường**. Giá 74.100đ (BQ 06/11/2026) đã biết từ r1/r2 và chỉ dùng để dán nhãn sau khi khoá. Mọi thay đổi ở r3 đều dựa trên BCTC, không dựa trên giá (khoá: `calc/LOCK_prerun_r3.txt` → `calc/LOCK_prerun_r4.txt`).

**Nguồn (đều nằm trong `src/`):**
- BCTC HN Q3/2026, CBTT 30/10/2026: `src/GAS_Q3_2026_HN_VN.pdf`, trang đã render ở `src/png/vn_p*.png`.
- BCTC HN soát xét 6T/2026 của Deloitte: `src/GAS_H1_2026_HN_soatxet.pdf`, bản OCR ở `src/ocr_h1/`.
- **MỚI ở r3 — BCTC HN năm 2025 đã kiểm toán** (Deloitte): `src/dl_20261123/GAS_Baocaotaichinh_2025_Kiemtoan_Hopnhat.pdf`, md5 `a00baa0354470f10e936cbd04714950d`. Tải từ static2.vietstock.vn vì pvgas.com.vn trả 403. Bản OCR ở `src/dl_20261123/ocr/k*.txt`.
- BQ `ticker_financial`: `calc/bq_fin_gas.csv`, `calc/np_hist_gas.csv`.

**Về artefact bị TRIM** (skeptic nêu): các tệp `src/` PDF, `calc/model_out_r2.txt`, LOCK và CSV đầu vào hiện **có mặt trong cây làm việc**, vì đã được khôi phục ngày 19/11. Đã kiểm md5 PDF Q3 = `b81a07c7…`, khớp `LOCK_prerun_r2.txt`. Tệp nào r3 dùng thì md5 nằm trong `calc/LOCK_prerun_r3.txt`.

## 1. Kết luận
- **Giá trị nội tại sau chiết khấu thanh khoản (cỡ 5 tỷ):** tâm **51.652đ** · P10 **44.760** · P50 51.332 · P90 **59.986**.
  - So với rev3: tâm 50.651 (+2,0%). So với r2 (09/11): tâm 50.146 (+3,0%).
  - Trước chiết khấu: tâm 51.992 (P10 45.055, P90 60.381). Cỡ 40 triệu: tâm 51.962.
- **Vùng giá (sau CK 5 tỷ):** rẻ < 44.800 · hợp lý 44.800–60.000 · đắt > 60.000.
- **Nhãn: TRÊN vùng (đắt) — nhãn TƯƠNG ĐỐI THEO KHUNG, không đổi so với r2/rev3.**
  - Giá 74.100 (BQ 06/11) cao hơn tâm 43,5% và cao hơn P90 23,5%. 100% trọng số lưới nằm dưới giá.
  - Ở r = 8% tâm là 69.599, vẫn dưới giá. r ngụ ý từ giá = 7,22%. Ở r = 13,5%, giá ngụ ý LN tăng trưởng danh nghĩa vĩnh viễn **+4,9%/năm**.
  - P/E TTM 12,1x sát đáy 10 năm (11,7x). Khoảng cách đến từ khung (r danh nghĩa 13,5%, RONIC = Ke, có suy giảm), **không phải** do mô hình ép LN.
- **Rủi ro lớn nhất (WARNING / độ nhạy, không vào tâm):**
  - Hợp đồng mua khí mỏ cũ Lô 05.2/05.3 + 05-1b/c (≈1,76 tỷ m³/năm, ≈22% sản lượng khí khô theo ước lượng) và hợp đồng bán khí NCS cho NT2 đều **hết hạn 12/2026**. Điều khoản xấu hơn 25% biên ⇒ **−1.995 đ/cp**; không gia hạn (mất toàn bộ biên phần này) ⇒ **−7.980 đ/cp**, vẫn không đổi nhãn.
  - Free float 4,24% (hạn 31/12/2026). Thay Chủ tịch/TGĐ 07/2026.
- **Sizing (V8, chuẩn 2–4% NAV/mã):** giá ngoài vùng giá trị nên DD **không đề xuất vị thế giá trị**. Nếu LAG mua theo cơ học, tối đa mức sàn 2% NAV.

## 2A. Đính chính rev3 → rev4 (skeptic r2, `skeptic/r2.json`)
| # | Hạng mục skeptic r2 | Bằng chứng | Xử lý · tác động (đ/cp, sau CK) |
|---|---|---|---|
| S1 | Tỷ lệ trích quỹ KT-PL 1,91% bị đánh giá thấp | NQ ĐHĐCĐ 47/NQ-KVN 22/06/2026 (soát xét 6T/26 p52, `src/ocr_h1/p52.txt`): quỹ KT-PL + thưởng BQL điều hành từ LN 2025 = **379,6 tỷ** (tạm trích 187,75 + bổ sung 191,83). Cộng phần CĐ mẹ của quỹ ở công ty con (PVGas D 8,25; PV Coating 6,19) = 394,0 / LN CĐ mẹ 2025 11.212,5 = **3,51%** | **(a)** base 3,51%: **−554** so với 1,91% |
| S4 | Chưa soát khoản một lần Q4/25 và Q2/26 | **Phát hiện LỖI ở r2/rev3.** BCTC KT 2025 TM32 (`src/dl_20261123/ocr/k58.txt`): cả năm 2025 hoàn nhập dự phòng phải thu ròng chỉ **436,6 tỷ**, trong khi 9T/25 hoàn nhập 1.631,0 (TM31) ⇒ **Q4/25 trích lập lại 1.194,4 tỷ** (thêm CP QLDN Q4/25 = 1.324,0 − (−439,0) = 1.763,0 tỷ). r2/rev3 đã trừ 1.631 × 0,8 khỏi điểm hồi quy 2025 (đúng ra chỉ 436,6 × 0,8), và cửa sổ TTM giữ nguyên khoản trích Q4/25. Q2/26 (KQKD 6T/26, `src/ocr_h1/p10.png`): LN khác 0,8 tỷ; DT tài chính 740,7 (6T/25 758,7); CP QLDN 379,1 đã gồm hoàn nhập −497,1 (đã xử lý) ⇒ không có khoản một lần nào khác | **(a)** (i) Điểm hồi quy 2025: điều chỉnh −349,2 (= −436,6 × 0,8) thay cho −1.304,8 ⇒ a = 2.339, b = 119,7, R² 0,673. (ii) RES cộng lại khoản trích Q4/25 × 0,8 = +955,5 (đối xứng với việc trừ hoàn nhập 9T/26) ⇒ RES trước khấu hao 3.152, sau trừ khấu hao giảm 2.615. Cộng (i)+(ii) ≈ **+1.555** (tính bằng hiệu: tổng thay đổi +1.001 trừ phần KT-PL −554). Phần cao của Q2/26 do Brent và có thể lãi tồn kho LPG vẫn nằm trong trục RES 0/50/100% |
| S2 | Hết hạn hợp đồng khí 12/2026 chưa có độ nhạy | BCTC KT 2025 TM35. Tổng sản lượng khí khô ~8 tỷ m³/năm là **ước lượng** (sector read 09/11, số thứ cấp) ⇒ tỷ phần 22,0%. LN gộp khí khô + LNG năm = 12.473,2 × 4/3 = 16.631 tỷ | **(b)** chỉ độ nhạy, không gắn xác suất (không có cơ sở độc lập về gia hạn): biên −25% ⇒ −1.995 · mất 100% ⇒ −7.980 · biên +25% ⇒ +1.995. Không vào base. Lưu ý: GAS sở hữu đường ống NCS/Cửu Long là đầu ra gần như duy nhất của các mỏ này nên khả năng "không gia hạn hoàn toàn" là thấp — đây là nhận định, không phải số đo |
| S3 | Thời điểm ARO có thể bị kéo sớm | Base đã trừ 100% giá sổ KHÔNG chiết khấu, tức giả định chi ngay ⇒ kéo sớm không thể làm base xấu hơn. Phần chưa trích (tổng dự toán BCT trừ số đã trích, nếu mỏ dừng sớm) không công bố | **(c) không kiểm chứng được** phần dự toán chưa trích. Độ nhạy một chiều (+976 nếu chi sau 10 năm) là đúng bản chất |
| S5 | β = 1 không có cơ sở | β là hệ số truyền dẫn lãi huy động → r theo luật V1 (mặc định của luật, [UL]). Lãi huy động hiện = lãi neo (7,40%) ⇒ Δ = 0 ⇒ **β không ảnh hưởng tâm hiện tại** (β 0,5 hay 1,0 cho cùng r 13,5%) | Giữ [UL]. Đã báo dải Ke 12,3–13,4% |

## 2B. Đính chính r2 → rev3 (skeptic r1) — giữ nguyên từ rev3 (số trong bảng này là số rev3)
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

## 3. Giá trị nội tại — `calc/model_r4.py` (khung r2/rev3), khoá `calc/assumptions_r4.json` + `calc/lock_v1_r4.json` (lint strict 0 vi phạm), `calc/LOCK_prerun_r4.txt`
**Cấu trúc (như rev3):** Giá trị = tiền ròng theo sổ 39.654,7 + XDCB 5.916,4 + góp vốn BCC Lô B 1.395,7 (V4a, NPV 0) + bao tiêu trả trước 1.775,5 − quỹ KT-PL 875,6 − quỹ KH&CN 235,9 − dự phòng thu dọn 3.300 (D3) + LN hoạt động Q4/26 (0,231 năm) + NOPAT 2027–2028 chiết khấu giữa kỳ + giá trị cuối kỳ NOPAT₂₀₂₉/(r + suy giảm). RONIC = Ke; conv = 1. Các khoản sau tiền ròng cộng lại = **19.740 đ/cp**.

LN hoạt động = hồi quy LN năm theo Brent (2016–2025; **rev4: a = 2.339, b = 119,7, R² 0,673**) − lãi tiền gửi sau thuế + U × RES (**rev4: 2.615**), rồi × (1 − **3,51%**).
LN hoạt động tại Brent 62 ⇒ 9.533 · 72 ⇒ 10.688 · 85 ⇒ 12.190 tỷ/năm.

**V1 — r = 13,5%**, neo lãi huy động 12T hiệu dụng 7,40% (`deposit_rate_vn.effective_deposit_rate('2026-11-23')` = CCTG 12T 02/11; Big-4 6,8%), β = 1 [UL]; lãi hiện bằng lãi neo nên r không đổi.
- Độ nhạy lãi huy động: −100bp ⇒ 53.834 · −50bp ⇒ 52.705 · +50bp ⇒ 50.669 · +100bp ⇒ 49.749.
- Hai đầu dải Ke nội địa (D4, chỉ báo kèm; `calc/ke_band_r4.txt`): **r 12,3% ⇒ tâm 54.310** (P10 46.613, P90 63.680) · **r 13,4% ⇒ 51.857**. Tâm dùng r 13,5%.

| Kịch bản (w) | Brent Q4/26 · 2027 · 2028 · dài hạn | Suy giảm/năm | Giá trị (đ/cp, trục giữa, trước CK) |
|---|---|---|---|
| XẤU (0,275) | 95 · 72 · 62 · 62 | 2,8% | 46.274 |
| CƠ SỞ (0,45) | 100 · 85 · 75 · 72 | 1,4% | 52.354 |
| TỐT (0,275) | 105 · 100 · 85 · 82 | 0% | 59.606 |

**Lưới 81 kết cục** (kịch bản × hệ số Brent ±25% × Brent dài hạn ±5 × phần dư 0/50/100%), sau CK 5 tỷ: P10 44.760 · P25 47.062 · P50 51.332 · P75 55.757 · P90 59.986 · min 40.125 · max 66.114.

**Độ nhạy ngoài lưới** (đ/cp, sau CK; KHÔNG vào base; `calc/model_out_r4.txt`):

| Độ nhạy | đ/cp |
|---|---|
| Hợp đồng khí 12/2026: biên −25% / mất 100% / +25% | −1.995 / −7.980 / +1.995 |
| Truy thu cước ống tạm tính 1.500 tỷ | −618 |
| Lỗ tồn kho LPG | −82 |
| Cam kết vốn NPV −5% / −10% / +5% | −437 / −874 / +437 |
| Vốn lưu động về mức 01/01 | +656 |
| Mất 10% phải thu PVPower | −390 |
| Thuế hoãn lại ròng | −104 |
| Dự phòng thu dọn chi sau 10 năm | +976 |
| Chiết khấu cuối kỳ | −1.968 |
| Không trừ phần khấu hao giảm | +781 |
| Không trích quỹ KT-PL (3,51%) | +1.215 |
| Không suy giảm | +2.895 |
| Suy giảm +3pp | −5.328 |

**V6 — hai nền giá trị, CHỈ HIỂN THỊ** (`calc/v6_r3.txt`; dữ liệu không đổi ở rev4; không trộn vào tâm/vùng/sổ):

| Nền | Giá trị | Cách tính |
|---|---|---|
| V_ngắn | 32.009 | LNST chuẩn hoá = trung vị TTM 2023Q4–2026Q3 = 11.508 tỷ; g = −1,4% < 0 nên tái đầu tư chặn ở 0 |
| V_dài | 31.156 | FCFE 9T × 4/3 = 11.201 tỷ |
| V theo C4 | 38.493 | "chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi" |

D = 0,027 < ln2: không cờ. Hai nền KHÔNG gồm tiền ròng theo sổ (19.740 đ/cp).

**Đối chiếu P/E:** EPS TTM 6.110đ ⇒ tâm rev4 = 8,5x (P10 7,3x · P90 9,8x). P/E lịch sử 2016Q1–2026Q3 (43 quý, BQ): 11,7–26,5x, trung vị 15,6x.

## 4. Vị thế & lợi thế cạnh tranh (V5 / 5F) — tái dùng r2 (09/11/2026, < 12 tháng) + kiểm nhanh
- moat_tier **NARROW** · REGULATORY/INFRA · rủi ro số 1: mỏ cũ cạn cộng dịch chuyển sang LNG chuyển ngang biên mỏng. Bằng chứng định lượng: ROIC_Min10Y 13,8% so với Ke 13,5%. Đồng hồ cắt hào: CÓ (xem r2 §4).
- Kiểm nhanh r3 (1): các hợp đồng mua khí mỏ cũ (Lô 05.2/05.3/05-1b/c) **hết hạn 12/2026**. Điều này củng cố "đồng hồ đếm ngược" nhưng chưa đủ để đổi tầng; điều khoản gia hạn chưa biết.
- Kiểm nhanh r3 (2): cam kết vốn 21,2 nghìn tỷ (Lô B, kho LNG 3 triệu tấn) là nỗ lực thay thế nguồn khí. Trong base, nó ở NPV 0.

## 5. Điều làm nhận định đổi theo CẢ HAI chiều
**Lên:**
- LN quý 2027 ≥ 3.500 tỷ khi Brent ≤ 80. Mỗi +1.000 tỷ LN bền/năm ≈ +2.800 đ/cp.
- Cước ống Lô B / IRR công bố ≥ r. Hợp đồng khí 2027+ gia hạn với biên tương đương. Phải thu PVPower thu về (+656 khi vốn lưu động về mức 01/01). Lãi huy động giảm 100bp ⇒ +2.182.

**Xuống:**
- Brent < 75 hai quý liên tiếp và LN Q4/26 < 2.500 tỷ. Không gia hạn / gia hạn xấu hơn hợp đồng mỏ cũ sau 12/2026 (−1.995 đến −7.980).
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
- **Không kiểm chứng được:** điều khoản gia hạn hợp đồng khí mỏ cũ sau 12/2026; tổng sản lượng khí khô (dùng ước lượng 8 tỷ m³); IRR/cước Lô B; tiến độ chi cam kết vốn; giấy phép mỏ; kế hoạch free float; lý do miễn nhiệm; phần 540,7 tỷ cổ tức; thời điểm chi thu dọn.

## 9. File
- `calc/notes_bctc_r3.md` — phân loại đủ BCĐKT (dùng chung rev3/rev4).
- rev4: `calc/assumptions_r4.json` · `calc/lock_v1_r4.json` · `calc/LOCK_prerun_r4.txt` · `calc/model_r4.py` → `calc/model_out_r4.txt` (2 lần chạy cùng md5 `9096021ad65ac12d2c091efaead09bef`) · `calc/ke_band_r4.py` → `ke_band_r4.txt` · `calc/v6_r3.txt`.
- rev3 giữ nguyên: `REPORT_rev3.md`, `calc/*_r3*`. r2: `REPORT.md`, `calc/model_r2.py`, `assumptions_r2.json`.
