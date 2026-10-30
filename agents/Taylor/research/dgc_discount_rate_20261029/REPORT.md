# Chi phí vốn dài hạn cho DCF DGC — rf nào là hợp lý?
Job `Taylor_20261029_133456` · 29/10/2026 · chỉ nghiên cứu (không wire, không sửa r7, không đặt lệnh).
PREREG `19d692087` (khai trước) · self-check 0 đồng · tất định 2 TZ — `SELFCHECK.md`.

## Kết luận trước

1. **Số đang dùng là 14,9%, không phải 14,5%.** Ke = rf 7,4% + β 1,0 × ERP 7,5% [UL]. Con số này giống nhau từ r2 đến r11 và
   trong báo cáo nhà đầu tư DGC (dòng 238: "Chi phí vốn chủ 14,9%"). Không tầng nào có 14,5%. Gần nhất là r1 với **14,3%**
   (rf 6,8% = Big-4 12M). rf 7,4% lấy từ `effective_deposit_rate` = max(Big-4 12M 6,8%, CCTG 12M 7,4%), nguồn `cctg_12m(2026-10-12)`.
2. **User đúng về nguyên tắc cho rf, nhưng Ke theo luật PREREG không giảm mà TĂNG.** Lãi huy động 12M là kỳ hạn 1 năm, đang ở đỉnh chu kỳ,
   nên không phải rf cho dòng tiền vô hạn. Theo luật đã khai trước, rf trung tâm = **6,75%** (lạm phát mục tiêu 4,25% + lãi thực 2,5%),
   **thấp hơn 0,65pp** so với 7,4% hiện hành. **Nhưng** ERP 7,5% của r7 đo trên lãi huy động nên không được ghép với rf mới (PREREG §3);
   ERP bond-based theo Damodaran là 8,13% ⇒ Ke = 6,75 + 1,11 × 8,13 = **15,77%, tăng +0,87pp so với 14,9%**. Chỉ khi cho ERP về mốc thị trường
   ngầm định 5,7% thì Ke mới giảm (13,1%). Nói "sửa rf hạ Ke 0,65pp" là sai khung: hạ rf không đủ để hạ Ke nếu ERP đổi theo.
   Ở VN, TPCP 10Y (4,47%) đang **thấp hơn** lãi huy động 12M; dấu hiệu bị kìm (Kho bạc neo giá; phiên 30/09 chỉ trúng thầu 33%) nhưng
   bằng chứng mỏng: **chỉ 1 điểm lợi suất (4,47%) + 1 phiên trúng thầu 33%**, và có thể là hiện tượng **cấu trúc từ 2020** (chuỗi tham khảo 2020-26
   đều dưới 4,5%, nhưng phần lớn điểm chưa kiểm chứng nên chỉ là gợi ý) chứ không phải kìm nén nhất thời.
3. **Mức Ke do ERP quyết định, không phải rf.** ERP 7,5% của r7 là [UL] và được đo so với lãi huy động. Hai mốc độc lập:
   Damodaran (01/2026) cho VN **8,13%** (ERP trưởng thành 4,23% + rủi ro quốc gia 3,90%), còn thị trường ngầm định
   (E/P VNINDEX + lạm phát − rf) cho khoảng **5,7%**. Hai mốc cách nhau 2,4pp, rộng gấp ~4 lần chênh lệch do rf.
4. **Vùng Ke hợp lý: 12,2% – 16,7%.**
   - Điểm theo luật PREREG = **15,8%** (6,75 + 1,11 × 8,13). Điểm này **nằm trên** phần lớn dải đối chiếu thị trường (11,5–12,7%) ⇒ báo cáo, KHÔNG đổi luật.
   - Điểm theo ERP thị trường ngầm định = **13,1%**.
   - **14,9% hiện hành nằm trong vùng, gần giữa.** Không có cơ sở nói nó "quá cao" khi đo bằng khung dài hạn nhất quán.
5. **Tác động lên DGC nhỏ hơn trực giác.** Ở tầng A, đổi Ke trong cả vùng 12,2–16,7% làm EV blend chạy **31.898 → 28.869**
   (gốc 29.817), còn DCF cơ sở chạy 37.726 → 30.756 (gốc 32.925). Có ba lý do:
   - DCF chỉ chiếm 1/3 blend (blend = trung bình SOTP, DCF, multiple_avg; Ke còn vào multiple_avg qua P/B hợp lý, xem mục 4: kênh này chiếm ~24% độ nhạy blend).
   - Tiền ròng là 15.234 đ/cp, tức 46% DCF cơ sở và không nhạy với Ke.
   - Terminal chỉ chiếm 29% DCF ở 14,9%.
6. **Cảnh báo lạc quan.** Hạ Ke xuống 11% và nâng g lên 5% cùng lúc sẽ đẩy DCF cơ sở lên **41.853 (+27%)**. Đây là hai núm cùng chiều.
   Với RONIC 12% [UL] của r7, tăng g khi Ke > 12% còn làm **giảm** giá trị, nên nâng g không cứu được Ke thấp.

## 1. Nguyên tắc (cơ sở lý thuyết)

- **Damodaran** (Investment Valuation; "Country Risk" update 2026): rf phải khớp **tiền tệ** của dòng tiền. Với VND, rf = lợi suất
  TPCP VND dài hạn **trừ default spread** của quốc gia. Rủi ro quốc gia không nằm trong rf mà được cộng qua CRP trong ERP.
  ERP = ERP thị trường trưởng thành + CRP.
- **McKinsey Valuation** (Koller et al.): dùng lợi suất TPCP **10 năm** cùng tiền tệ (khớp kỳ hạn với dòng tiền dài). Khi lãi suất bị
  méo bởi chính sách (ví dụ QE), McKinsey khuyên **bình thường hoá** = lãi thực dài hạn (~2%) + lạm phát kỳ vọng.
- **Tiêu chí đã khai ở PREREG §1:**
  - K1: khớp VND.
  - K2: kỳ hạn ≥10Y.
  - K3: không phản ánh chu kỳ chính sách.
  - K4: quan sát được.
  - K5: không nhìn trước.
  - K6: g ≤ rf dài hạn ≤ GDP danh nghĩa.
- Lãi huy động 12M/CCTG trượt **K2** (kỳ hạn 1 năm) và **K3** (đang ở đỉnh chu kỳ).
- TPCP 10Y VN đạt K1, K2, K4 nhưng trượt **K3** theo hướng ngược lại: thấp giả tạo do kìm nén tài chính. Bằng chứng:
  - 4,47% < lãi huy động 12M 6,8%.
  - Trúng thầu chỉ 33%.
  - Damodaran-literal rf = 4,47 − 2,56 = **1,9%**, tức lãi thực **âm** so với lạm phát mục tiêu ~4%. Một rf như vậy không có nghĩa kinh tế cho đầu tư 30 năm.

## 2. Ứng viên rf (khai trước; số trong `out_rf_candidates.csv`)

| Ứng viên | rf | Nguồn / nhãn | Đạt tiêu chí? |
|---|---|---|---|
| (a) TPCP 10Y hiện tại | **4,47%** | ADB AsianBondsOnline, đóng cửa 28/10/2026 [SRC] | Trượt K3 (bị kìm) |
| (b) TPCP 10Y trung vị 2016-25 | 3,70% (TB 3,95) | **CHƯA KIỂM CHỨNG (trí nhớ mô hình)** — trong 16 điểm năm: 1 có nguồn (2019 = 4,35%, VietnamPlus), 5 neo 1 phiên, 1 ước lượng có mốc 12/2019, **9 là trí nhớ mô hình không nguồn** (2011-17, 2022, 2024; `kind=chua_kiem_chung`). Ứng viên (b) KHÔNG dùng làm căn cứ kết luận; chỉ giữ để cho thấy luật rf không phụ thuộc nó | Trượt K3, K4 yếu |
| (b) TPCP 10Y trung vị 2011-25 | 4,80% | chưa kiểm chứng (trí nhớ mô hình) | như trên |
| (c) Lạm phát mục tiêu + lãi thực: thấp / **giữa** / cao | 6,00 / **6,75** / 7,50% | CPI mục tiêu QH ~4,5% (4,0 cận dưới [UL]); lãi thực 2–3% [UL, McKinsey ~2% + đến 1pp EM] | **Đạt K1–K6** |
| (c') Damodaran-literal (TPCP − default spread 2,56) | 1,91% | Damodaran ctryprem 05/01/2026 | Trượt K3 (thực âm) |
| (d) Big-4 12M TB 10 năm / 15 năm | 6,01 / 6,61% | `deposit_rate_vn.py` — mốc neo hồi tố (caveat b) | Kỳ hạn 1Y nhưng đã làm mượt chu kỳ |
| (e) GDP danh nghĩa CAGR 2021-25 | 11,25% | FiinPro snapshot, cùng vintage | Mốc TRẦN cho g, không phải rf |
| (f) Hiện hành (đối chứng) | 7,40% | max(Big-4 12M, CCTG 12M) | Trượt K2, K3 |
| **(g) Chênh lệch lạm phát — KIỂM CHÉO, không phải luật** | **6,71 / 6,97 / 7,23%** (π_VN 4,0 / 4,25 / 4,5) | (1+UST10Y)(1+π_VN)/(1+π_US)−1; UST10Y **5,05%** (FRED DGS10, 28/10/2026) [SRC], π_US = **2,38%** (FRED T10YIE 28/10/2026) [SRC], π_VN [UL]. `out_rf_infl_diff.csv` | Đạt K1, K2, K4; gồm phần bù kỳ hạn Mỹ, không gồm rủi ro VN |

**Luật rf (PREREG §3):** |b10 3,70 − c 6,75| = 3,05pp > 1pp ⇒ rf trung tâm = **(c) 6,75%**. Luật không phụ thuộc chất lượng (b): kể cả khi (b) sai ±2pp, chênh lệch vẫn > 1pp.

**Kiểm chéo tính đôi rủi ro quốc gia (theo skeptic).** Lãi thực 2,5% của (c) đã "+đến 1pp thị trường mới nổi" [UL], trong khi ERP Damodaran đã cộng CRP 3,90 ⇒ điểm trung tâm 15,77% có thể cao ~0,5pp. Hàng (g) là phép kiểm chéo phần chồng lấn,
**không đổi luật PREREG** (rf trung tâm vẫn 6,75%): rf theo chênh lệch lạm phát = 6,97% ở π_VN 4,25%, tức **cao hơn** (c) 0,22pp (−0,04…+0,48pp theo π_VN 4,0…4,5);
lãi thực Mỹ ngầm định 5,05 − 2,38 = 2,67% ≈ 2,5%. Vậy kiểm chéo **không xác nhận** mức tính đôi 0,5pp ở phía rf: UST chưa chứa rủi ro VN nên CRP nằm ở ERP là hợp lý.
Cảnh báo giữ nguyên ở dạng định tính: "+1pp EM" trong (c) là [UL] và nếu bỏ nó rf về ~5,75% thì Ke trung tâm thấp hơn ~1pp; kiểm chéo (g) cho thấy không cần bỏ. Điểm 15,77% vì thế nên đọc là **15,8% ± ~0,5pp do cách xử lý rủi ro quốc gia**, không phải điểm chính xác.

Ghi chú: (d) TB 10 năm của chính quy ước cũ = 6,0%, gần với (c). Điều này cho thấy 7,4% hiện tại là **đỉnh chu kỳ của rf**, cao hơn mức bình thường hoá khoảng 0,65–1,4pp (đây là về rf, không phải về Ke).

## 3. ERP và β

| Thành phần | Giá trị | Nguồn |
|---|---|---|
| ERP r7 | 7,5% | [UL], không có dẫn chiếu; đo **so với lãi huy động** |
| ERP fleet `dcf_valuation.py` | 6,5% | Thực nghiệm: TR VNINDEX 2013-26 − Big-4 deposit TB ~6,8% (premium **trên lãi huy động**) |
| ERP Damodaran VN 01/2026 | **8,13%** = 4,23 trưởng thành + 3,90 CRP (Ba2, DS 2,56 × σ cổ phiếu/trái phiếu) | [SRC] pages.stern.nyu.edu/~adamodar ctryprem.html |
| ERP thị trường ngầm định | **5,70%** = (E/P 8,20% + lạm phát 4,0–4,5%) − 6,75 | E/P từ VNINDEX_PE 12,19 ngày 28/10 [BQ]; giả định tăng trưởng thực = 0 |
| β DGC (tuần, 5Y, vs VNINDEX) | thô 1,204 → Blume **1,136** (ρ 0,47, n 259) — số **dùng trong mô hình**, gốc không có script | [BQ] |
| β trung vị peer hoá chất | thô 1,125 → Blume **1,083** (N = 19, universe_pit ∩ ICB 13xx) — số **dùng trong mô hình** | [BQ] |
| β dùng | **1,11** (khoảng 1,08–1,14) | luật PREREG |
| **β tái lập bằng script** `beta_weekly.py` (Close điều chỉnh, điểm tuần = phiên giao dịch cuối tuần ISO/Thứ Sáu, lợi suất đơn giản, 259 tuần đến 28/10/2026) | DGC thô **1,195** → Blume **1,130** (ρ 0,480); peer thô **1,143** → Blume **1,095** (N = 18, trung vị) | [BQ] `out_beta.csv` |

- **Không ghép rf trái phiếu với ERP đo trên lãi huy động.** Ghép như vậy sẽ hạ Ke giả tạo. Ví dụ: (b) 3,7 + 7,5 = 11,2% là sai khung.
- **β: không tái lập đúng 1,204/1,125.** Script mới (`beta_weekly.py`) cho 1,195 / 1,143; skeptic đo thô 1,164. Độ nhạy quy ước DGC: log-return 1,217, chỉ Thứ Sáu thật (n = 251) 1,190, cửa sổ lùi 1 tuần 1,212–1,215 ⇒ β thô nằm 1,16–1,22 tuỳ quy ước tuần. Hai số peer lệch (N = 18 vs 19; tập con khác) nên số gốc 1,125 không dựng lại được. Với số mới, β_c = (1,130 + 1,095)/2 = 1,1125 so với 1,1095: Ke trung tâm 15,79% thay vì 15,77% (+0,02pp, tính tay, **không chạy lại** `model_ke.py` để giữ nguyên các số đã tái lập). Không đổi kết luận.
- β DGC 5Y có phần do cú sốc pháp lý 2025-26, mang tính đặc thù chứ không hệ thống. Peer 1,08 là mốc kiểm. Khoảng hẹp nên ảnh hưởng nhỏ (±0,2pp Ke).
- **Chi phí nợ.** DGC chỉ có vay ngắn hạn 1.391 tỷ và không có nợ dài hạn; lãi vay DN VN ~6,5–8% (ước lượng, chưa đo cho DGC). Ke > Kd + 4pp ở mọi ứng viên trừ (c'), nên mốc kiểm này không ràng buộc.

**Đối chiếu độc lập** (`out_market_xcheck.csv`, KHÔNG dùng để chọn):

| Đối chiếu | Ke ngụ ý |
|---|---|
| TR VNINDEX 2011-26 (giá 10,01% [BQ] + cổ tức 1,5–2% [UL]) | 11,5–12,0% |
| TR VNINDEX 2016-26 | 11,5–12,0% |
| … bỏ đổi P/E 2016-26 (P/E 16,6 → 12,2, −3,0%/năm) | 14,9–15,4% |
| … bỏ đổi P/E 2011-26 (P/E 9,5 → 12,2, +1,65%/năm) | 9,7–10,2% |
| E/P VNINDEX + lạm phát | 12,2–12,7% |
| Ke thị trường (β = 1) theo luật trung tâm | 14,9% |

Lợi suất thực hiện rất nhạy với P/E đầu và cuối kỳ: hai cửa sổ cho 10% và 15%. Vì vậy đối chiếu chỉ cho một **dải** chứ không cho một điểm.
Ke trung tâm 15,8% (β 1,11) nằm trên dải 11,5–12,7% ⇒ báo cáo, theo PREREG không sửa luật.

## 4. Tác động lên DGC (tầng A r7, `out_ke_candidates.csv`, `out_ke_grid.csv`)

| Ứng viên Ke | Ke | DCF nghịch / cơ sở / thuận | EV blend A |
|---|---|---|---|
| (f) hiện hành r7 | 14,90% | **21.407 / 32.925 / 41.779** | **29.817** |
| fleet dcf_valuation (7,4 + 6,5) | 13,90% | 22.296 / 34.407 / 43.883 | 30.462 |
| **Trung tâm PREREG** (6,75 + 1,11 × 8,13) | **15,77%** | 20.746 / 31.823 / 40.213 | **29.336** |
| rf_c + β × ERP ngầm định | 13,08% | 23.155 / 35.840 / 45.917 | 31.083 |
| (a) TPCP hiện tại + β × 8,13 | 13,49% | 22.709 / 35.096 / 44.861 | 30.761 |
| (b) TPCP trung vị + β × 8,13 | 12,72% | 23.577 / 36.544 / 46.917 | 31.387 |
| (d) Big-4 TB 10 năm + 7,5 | 13,51% | 22.688 / 35.061 / 44.811 | 30.745 |
| (c') Damodaran-literal | 10,93% | 26.240 / 40.987 / 53.225 | 33.303 |
| **Vùng thấp** (6,0 + 1,08 × 5,7) | 12,17% | 24.285 / 37.726 / 48.595 | **31.898** |
| **Vùng cao** (7,5 + 1,14 × 8,13) | 16,74% | 20.106 / 30.756 / 38.699 | **28.869** |

**Kênh Ke → P/B hợp lý (bổ sung).** Ke vào blend qua ba đường: SOTP, DCF và `multiple_avg`; trong `multiple_avg` có `v_pb` với P/B hợp lý = (ROE − g)/(Ke − g) (r7 `model.py` dòng ~400), trọng số 1/9 trong blend.
Phép kiểm ở Ke 13,08% so với 14,9% (đ/cp, kịch bản cơ sở, `out_ke_candidates.csv`): ΔDCF 35.840 − 32.925 = 2.915 → /3 = **972**; Δv_pb 35.737 − 32.890 = 2.847 → /9 = **316**; ΔSOTP 32.844 − 32.769 = 75 → /3 = **25**; tổng **1.313** = Δblend cơ sở 32.529 − 31.216 = 1.313 (khớp 0 đồng).
Kênh P/B chiếm 316/1.313 = **24%** độ nhạy blend. (EV có trọng số kịch bản dịch 1.266, không phải 1.313.) Kết luận "tác động nhỏ" giữ nguyên.

**Độ nhạy.** Mỗi −1pp Ke quanh 14–15% làm DCF cơ sở tăng khoảng +1.460 đ/cp, còn EV blend A chỉ tăng khoảng +634 đ/cp (lưới 14%→15%: DCF 34.247−32.790; EV 30.392−29.758).
A7 (r7 chính) ở lưới: Ke 12% → EV 34.434; 14,9% → 32.182; 16% → 31.583.

**Phân rã DCF cơ sở** (`out_dcf_decomp.csv`, đ/cp):

| Ke | PV 2027-31 | Terminal | Tiền (sau haircut, −NS capex) | Tổng | TV % | Phần do dòng tiền Nghi Sơn |
|---|---|---|---|---|---|---|
| 11,0% | 8.836 | 16.706 | 15.234 | 40.776 | 41% | 3.735 |
| 13,0% | 8.464 | 12.293 | 15.234 | 35.992 | 34% | 2.962 |
| 14,9% | 8.136 | 9.555 | 15.234 | 32.925 | 29% | 2.470 |
| 15,8% | 7.993 | 8.595 | 15.234 | 31.823 | 27% | 2.293 |

- **Gần như toàn bộ độ nhạy Ke nằm ở terminal.** Từ 14,9% xuống 11%: terminal +7.151, PV 2027-31 chỉ +700, tiền 0.
- **Nghi Sơn** nhạy theo tỷ lệ vì phần lớn là steady-state trong terminal (2.470 → 3.735).
- Trong SOTP, Nghi Sơn chiết khấu 2 năm theo Ke nhưng vẫn dùng PE cố định, nên SOTP gần như không đổi: 32.769 → 32.934.

**g × Ke** (DCF cơ sở, `out_g_x_ke.csv`):

| g \ Ke | 10% | 11% | 12% | 13% | 14% | 15% | 16% |
|---|---|---|---|---|---|---|---|
| 2% | 43.344 | 40.373 | 37.994 | 36.044 | 34.417 | 33.038 | 31.855 |
| **3% (r7)** | 44.185 | 40.776 | 38.120 | 35.992 | 34.247 | 32.790 | 31.555 |
| 4% | 45.263 | 41.256 | 38.245 | 35.899 | 34.017 | 32.474 | 31.185 |
| 5% | 46.720 | 41.853 | 38.370 | 35.751 | 33.709 | 32.070 | 30.726 |

r7 tái đầu tư g/RONIC với RONIC = 12% [UL]. Khi Ke > 12%, tăng trưởng **phá** giá trị (hàng g = 5% thấp hơn g = 2%).
Vì vậy, nếu hạ Ke xuống dưới RONIC thì g mới bắt đầu cộng giá trị. Đó là cơ chế cộng dồn lạc quan cần chặn.
g = 3% ≪ GDP danh nghĩa 11,25% (K6 đạt rộng).

## 5. Khuyến nghị

**(i) Cách chọn rf/Ke cho DCF dài hạn DGC.**
- **rf** = lạm phát mục tiêu + lãi thực dài hạn = **6,75%** (6,0–7,5%). Không dùng max(huy động 12M, CCTG) hay TPCP 10Y thô.
  - Huy động 12M/CCTG sai kỳ hạn và chạy theo chu kỳ.
  - TPCP 10Y thô bị kìm nén.
- **ERP** phải ghi rõ đo so với rf nào.
- **β** ≈ 1,1.
- Theo luật khai trước, điểm là **15,8%**. Không chọn theo FV mong muốn: điểm này cho FV **thấp hơn** hiện tại, ngược với kỳ vọng của câu hỏi.

**(ii) Báo Ke theo vùng 12,2–16,7%, không theo một điểm.** Ba mốc đọc:
- 13,1% (ERP thị trường ngầm định);
- 14,9% (hiện hành, gần giữa vùng);
- 15,8% (Damodaran ERP).

Với DGC tầng A, ba mốc này cho EV **31.083 / 29.817 / 29.336** và DCF cơ sở **35.840 / 32.925 / 31.823**. Khoảng EV ~1.750 đ/cp,
nhỏ hơn các bất định khác của DGC (biên ±2pp, dự phòng R1/R2 6.065, nghĩa vụ vụ án). **Không cần đổi nhãn DGC vì Ke.**

**(iii) Phạm vi áp dụng trong fleet.** Chỉ liệt kê, KHÔNG sửa; tác động lên FV các mã khác **chưa đo**.
- **Chỉ áp cho DCF going-concern vô hạn** (terminal Gordon). Không áp cho dòng tiền có thời hạn:
  - DRI r3/r4: khung thực r = 12% danh nghĩa ⇒ 8,74% thực, π 3%, cây cao su có vòng đời.
  - PVP: hợp đồng FSO chiết khấu 10% [UL].
  - TV1: thuỷ điện thuê đất đến 2059.
  - Các trường hợp này cần lãi suất khớp kỳ hạn hoặc khớp rủi ro hợp đồng.
- SCL/PVT/TV1 định giá chủ yếu theo PE nên không dùng Ke trực tiếp.
- 5 consumer của `consumer_deposit_rate()`:
  - `rating_8l` NEUTRAL tilt và `custom30_yield_labels` so **lợi suất cổ phiếu với tiền gửi hôm nay**. Đây là chi phí cơ hội NGẮN HẠN thật của nhà đầu tư, nên lãi huy động hiện hành là **đúng** cho hai consumer này. Không nên đổi.
  - `dcf_valuation.py` / `dcf_refresh_gate` / `due_diligence` là chiết khấu DCF ⇒ thuộc phạm vi khuyến nghị.
  - ⚠️ Phát hiện phụ (chỉ báo): `dcf_valuation.py` ngày 28/10 cho r = **13,9%** và g_T = **7,4%**. Mode `cap_rf` đặt g_T = min(CPI + GDP thực, rf = lãi huy động), nên chênh r − g chỉ 6,5pp. Nếu đổi rf ở đó thì g_T cũng đổi theo. Cần nghiên cứu riêng trước khi đụng.

**(iv) Cảnh báo thiên lệch, cả hai chiều.**
- Hạ Ke đẩy FV lên chủ yếu qua terminal (TV từ 29% lên 41% DCF ở 11%). Mọi đề xuất hạ Ke phải đi kèm kiểm tra:
  - g ≤ GDP danh nghĩa dài hạn;
  - RONIC ≥ Ke thì mới cho g cộng giá trị;
  - không đồng thời nâng g.
- Không tính đôi rủi ro quốc gia: CRP đã nằm trong ERP, nên lãi thực của rf không được cộng thêm phần bù EM (xem kiểm chéo (g) ở mục 2).
- Chiều ngược lại: giữ 7,4% chỉ vì quán tính cũng sai cơ sở (rf đỉnh chu kỳ). Còn 15,8% dựa trên CRP đo bằng USD. Đối chiếu thị trường VN ngụ ý ERP thấp hơn, nên đầu cao của vùng có thể đang khắt khe quá.
- Không có ứng viên nào ở đây phục vụ quyết định mua/bán DGC. Kết luận "Ke không phải biến quyết định cho DGC" đứng vững ở cả hai đầu vùng.

## Nguồn & giới hạn
- [ADB AsianBondsOnline VN](https://asianbondsonline.adb.org/economy/?economy=VN) 10Y 4,467% ngày 28/10/2026.
- [Damodaran ctryprem 01/2026](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html).
- [VietnamPlus 26/09/2019](https://en.vietnamplus.vn/interest-rates-of-gbonds-plunge-in-10-years/161091.vnp).
- VBMA 11/2021; HNX 10/2023 & 02/2026; ACBS 06/2026.
- TradingEconomics 12/2025 (trang chính trả 403, chỉ đọc được qua snippet tìm kiếm).
- `kb/projects/vn_realestate_monthly_checks/2026-10-multiproxy.md` (TPCP 10Y 4,45–4,47%, trúng thầu 33%).
- **Chuỗi TPCP 10Y theo năm: 9/16 điểm là trí nhớ mô hình, CHƯA KIỂM CHỨNG** (`kind=chua_kiem_chung`). Không có chuỗi chính thức trong data_registry, và FiinPro đã hết hạn.
- [FRED DGS10](https://fred.stlouisfed.org/series/DGS10) 5,05% và [FRED T10YIE](https://fred.stlouisfed.org/series/T10YIE) 2,38% ngày 28/10/2026 (tải CSV 30/10/2026).
- Lạm phát mục tiêu và lãi thực là [UL] theo khoảng.
- Cổ tức VNINDEX 1,5–2% là [UL].
