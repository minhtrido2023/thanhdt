# DD — DBC (CTCP Tập đoàn Dabaco Việt Nam, HOSE) · REV 4 · 23/11/2026 · job `Taylor_20261123_100916`

> **Khoá giả định:** `rev4/assumptions_DBC_rev4.json`, **assumptions_md5 = `57b36d63e05ad2e2c209f2ce34fda8c9`**. Lint `bin/dd_assumptions_lint.py`: 0 vi phạm. File khoá không chứa giá thị trường.
> **Mô hình:** `rev4/calc_rev4.py` (md5 `ee3e09b5…`), đầu ra `rev4/calc_rev4_output.txt` (md5 `063dddd3…`); mốc trượt cửa sổ `rev4/calc_rev4_milestones.py` → `calc_rev4_milestones_output.txt`. Mọi số dưới đây lấy từ các file đầu ra này, trừ chỗ ghi nguồn khác.
> **Bản trước:** rev1 `REPORT.md` (tâm 19.491, r1 INCONCLUSIVE) · rev2 `REPORT_rev2.md` (17.317, r2 INCONCLUSIVE) · rev3 `REPORT_rev3.md` (14.696, r3 REFUTED — tâm quá THẤP vì BĐS dở dang nằm trong vốn hoạt động).
> **Mù giá:** giả định khoá trước; giá DNSE đọc sau khoá (§6d). Hạn chế: người dựng đã thấy giá ở rev1–rev3 (§10).

## 0. Kết luận

- **Tâm = 17.673 đ/cp; vùng giá trị [10.262; 24.835]; kịch bản cơ sở sau chiết khấu 17.798.**
  - Kỳ vọng trọng số 25/50/25, sau chiết khấu thanh khoản 2%. Trước chiết khấu: 18.034.
- **So với rev3 (14.696): +20,3%.** So rev2: +2,1%; so rev1: −9,3%.
  - Thay đổi duy nhất lên tâm: **tách BĐS dở dang (1.186,4 tỷ tại 30/6/2026, BCTC soát xét) khỏi vốn hoạt động**, ghi theo sổ sách (NPV = 0, V4a), giống XDCB. Mẫu số ROE lịch sử cũng trừ BĐS dở dang theo số dư kiểm toán từng năm; tử số loại toàn bộ lãi BĐS (bỏ cả mức chạy 2,64 tỷ/quý của rev3 để không đếm hai lần với giá trị sổ sách).
- **Giá 16.400 (DNSE G1, đóng cửa 23/11/2026) = 0,93× tâm ⇒ quanh giá trị hợp lý, hơi dưới tâm; CHƯA rẻ theo cổng 0,85×tâm = 15.022.**
- **Độ bất định vẫn lớn, hai chiều:** cửa sổ W12/W20 cho 26.819 / 9.753; XDCB+BĐS do vốn chủ tài trợ 50% cho 13.767 (−22,1%); hết toàn bộ miễn giảm thuế có thời hạn −6,0%.
- **Kiểm toán:** EY, BCTC 2025 chấp nhận toàn phần; soát xét H1/26 sạch.
- **Pháp lý: chỉ WARNING.** Phải thu người lao động 237,1 tỷ (~178 tỷ là tạm ứng GPMB cho dự án CHĂN NUÔI theo TM 7.1 H1/26, không phải BĐS); mất trắng −539 đ/cp. Không vào base.
- **Sizing (V8):** chuẩn 2–4% NAV/mã. Ở giá hiện tại chưa đạt cổng 0,85×tâm ⇒ **chưa đề xuất mua**; nếu giá ≤ 15.022, tối đa 2% NAV/tranche (thanh khoản §6c).

## Đính chính so với rev trước

### A/B. Hạng mục skeptic r1, r2 — giữ nguyên xử lý của rev2/rev3
Xem `REPORT_rev3.md` bảng A1–A8, B1–B7 (KTPL k = 11,06%; BCTC KT 2022–25; XDCB lịch sử; 3 cửa sổ khai trước; lỗ thuế 647 tỷ chỉ ở kịch bản tốt; loại lãi BĐS lịch sử; độ nhạy tài trợ XDCB; NCI không đáng kể). Riêng B5 (thuế) và mức chạy BĐS của B1 được sửa ở bảng C.

### C. Hạng mục skeptic r3 → xử lý trong rev4

| # | Hạng mục r3 | Bằng chứng độc lập (nguồn gốc) | Xử lý | Ảnh hưởng lên tâm |
|---|---|---|---|---|
| C1 | BĐS dở dang ~1.186 tỷ nằm trong vốn hoạt động (tâm quá thấp) | Chi phí SXKD dở dang hoạt động BĐS, tỷ đồng: 31/12/2021 966,73 · 2022 1.297,36 (KT22 TM8) · 2023 1.080,38 (KT23 TM8) · 2024 846,44 · 2025 1.114,54 (KT25 TM9) · 30/6/2026 1.186,38 (H1/26 TM8, EY soát xét). Q3/26 không tách (TM7 Q3: dở dang tổng 1.347,87) ⇒ lấy số 30/6 (ước lượng). Ảnh `png/r4_kt22_tm8_inventory.png`, `r4_kt23_…`, `r4_kt25_tm9_…`, `r4_h1_tm8_…` | **(a) Vào base.** BĐS dở dang = dự án, sổ sách NPV = 0; trừ khỏi vốn hoạt động hiện tại (E_op 7.417,8 → 6.231,4) và khỏi mẫu số ROE lịch sử (quý giữa nội suy, ước lượng); tử số loại toàn bộ lãi BĐS | **+20,3%** (14.696 → 17.673). Nằm trong dải skeptic ước (+5,4% … +28,9%) |
| C1b | Trừ LN gộp BĐS mà chưa trừ chi phí BH/QLDN riêng của BĐS | Không công bố chi phí bán hàng/QL theo mảng | (c) Ghi nhận; nghiêng làm tâm hơi thấp, độ lớn nhỏ (lãi BĐS 2024–26 chỉ 4,6–24,7 tỷ/năm) | không định lượng |
| C1c | Tạm ứng GPMB 237,1 tỷ có thuộc dự án BĐS không? | H1/26 TM 7.1: ~178 tỷ là tạm ứng cho người lao động để GPMB các **dự án chăn nuôi** của Tập đoàn | Không gộp vào BĐS; giữ WARNING | 0 |
| C2 | Thời hạn ưu đãi thuế TNDN (r3 ước ~−13%) | KT25 TM31: 15% cho TACN/trồng trọt/chế biến nông nghiệp, 20% hoạt động khác; một số công ty con NN công nghệ cao 10% + miễn 4 năm, giảm 50% 9 năm; một số công ty con địa bàn khó khăn 17% + miễn 2 năm, giảm 50% 4 năm. Thuế được **miễn, giảm**: 78,23 tỷ (2025) = 4,82% LNTT; 38,53 tỷ (2024) = 4,51%. Lỗ năm trước chuyển sang: 45,12 tỷ (2025). Thuế hiệu dụng 7,19% (2025), 9,97% (2024). Ảnh `png/r4_kt25_tm31_cit.png` | **(b) Độ nhạy, không vào base.** Phần có thời hạn chỉ là dòng miễn/giảm (4,8% LNTT), KHÔNG phải toàn bộ khoảng cách tới 20% như r3 ước — thuế suất 15% cho TACN/nông nghiệp là thuế suất áp dụng, không có thời hạn trong thuyết minh. Thời điểm hết hạn từng công ty con không công bố; trại mới (XDCB Quảng Ninh, Lào Cai, Thanh Hoá, Quảng Trị) có thể nhận ưu đãi mới ⇒ không có cơ sở độc lập để giảm base | Hết 100% miễn giảm: 16.610 (**−6,0%**); hết 50%: 17.142 (−3,0%); hết miễn giảm + hết lỗ chuyển sang: 15.997 (−9,5%). Ước −13% của r3 bị thay bằng số đo này |
| C3 | Trích lập tài sản sinh học 94–188 tỷ bị bỏ khỏi rev3 | Không có cơ sở độc lập: dự phòng = 0 tại Q3/26; giá thành không công bố; 94–188 tỷ là giả định 5–10% của rev1 | **(b) Đưa lại thành độ nhạy một lần**, không vào base (cửa sổ ROE đã chứa lỗ 2022–23) | −214 … −427 đ/cp (**−1,2% … −2,4%**) |
| C4 | Chi tuân thủ môi trường không kiểm chứng | KT25 TM35: Công ty và một số công ty con **có nghĩa vụ tái chế bao bì** (NĐ 08/2022, NĐ 05/2025, TT 07/2025/TT-BTNMT) từ 01/01/2024; tại ngày lập báo cáo "đang trong quá trình tính toán và xác định" — số tiền chưa có. Không thấy quyết định xử phạt môi trường trong tài liệu đã đọc | **(c) Nghĩa vụ CÓ THẬT (D3: dòng tiền ra) nhưng KHÔNG định lượng được từ nguồn.** Không vào base (luật: khoản trừ base phải có số + nguồn). Độ nhạy: phí EPR định kỳ 10–30 tỷ/năm (ước lượng); chi một lần cho trại hiện hữu 50–150 tỷ (ước lượng, giữ từ rev2) | EPR: −1,5% … −4,5%; một lần: −0,6% … −1,9% |
| C5 | Capex còn lại để hoàn thành XDCB không công bố | KT25 TM35 chỉ công bố cam kết thuê đất hoạt động 531,5 tỷ, không có cam kết vốn XDCB/BĐS | XDCB và BĐS là dự án tăng trưởng: NPV = 0, phần còn phải chi đối ứng bằng giá trị tương đương (V4a) ⇒ không trừ | 0 |
| C6 | Skeptic không đọc được PDF | PDF là bản scan; trang đã dùng được render thành PNG ở `png/r4_*.png` để kiểm trực tiếp | — | — |

## 1. Nguồn và đối chiếu

- LNST quý: BQ `NP_P0`, tổng năm khớp BCTC kiểm toán (2021, 2023–2025); 2022Q4 sửa theo KT22. Vốn chủ mẹ: BQ + 2 điểm kiểm toán. XDCB: mã 242 BCĐKT kiểm toán + Q3/26; quý giữa nội suy (ước lượng).
- **Mới ở rev4:** BĐS dở dang theo năm từ TM hàng tồn kho KT22/KT23/KT25 + H1/26 (bảng C1). Thuế TNDN: KT25 TM31/31.1. Cam kết/nghĩa vụ: KT25 TM35.
- LNST chuẩn hoá (loại toàn bộ BĐS) = 860,6 tỷ/năm; EPS 1.997 đ; sau KTPL 1.776 đ.

## 2. Chuẩn hoá ROE (luật khai trước, không đổi)

ROE_op quý = 4 × LNST quý (loại lãi BĐS) / (vốn chủ mẹ − XDCB − BĐS dở dang).

| Cửa sổ | ROE_op | Tâm nếu dùng riêng |
|---|---|---|
| W12 (Q4/23–Q3/26) | 19,98% | 26.819 (+51,8%) |
| W15 (Q1/23–Q3/26) | 12,98% | 16.447 (−6,9%) |
| W20 (Q4/21–Q3/26) | 8,47% | 9.753 (−44,8%) |
| **Tâm = trung bình đều** | **13,81%** | sau KTPL 12,28% |

- XDCB/BĐS bậc thang thay nội suy: 16.317 (−7,7%).

## 3. Quỹ khen thưởng phúc lợi
k = 11,06% (không đổi). Độ nhạy: k 0% → 20.220; 6,3% → 18.769; 13% → 17.227; 26,5% → 14.119.

## 4. XDCB, BĐS dở dang, thuế

- **XDCB 30/9/2026 1.302,6 tỷ** (trại heo 873,4): NPV = 0 sổ sách; kịch bản xấu haircut 40% phần trại heo (cơ sở: Bobby — làn sóng mở trại 2025–26).
- **BĐS dở dang 1.186,4 tỷ:** NPV = 0 sổ sách (base). Tốc độ bán chậm (doanh thu BĐS 2025 21,4 tỷ so với dở dang 1.114,5 tỷ) là dữ kiện quan sát được nhưng chưa có dấu hiệu suy giảm giá trị cụ thể (không trích lập) ⇒ chỉ độ nhạy: haircut 20% → 17.134 (−3,1%); 40% → 16.594 (−6,1%).
- Biến thể đối chiếu: cách rev3 (BĐS trong vốn hoạt động + mức chạy) 14.696; tách BĐS nhưng giữ mức chạy 18.079 (+2,3%, đếm hai lần nhẹ).
- **Tài trợ XDCB + BĐS:** base 100% vốn chủ (lãi vay thời gian xây dựng được vốn hoá). Vốn chủ tài trợ 50%: 13.767 (−22,1%); 25%: 11.589 (−34,4%).
- **Thuế:** base giữ thuế lịch sử trong cửa sổ; độ nhạy hết miễn giảm ở bảng C2.

## 5. Dòng tiền, V6 (chỉ hiển thị)

- CFO TB 1.133,3 tỷ/năm; capex gồm thuê TC 1.178,7 tỷ/năm ⇒ FCFE ≈ −45,5 tỷ/năm ⇒ V_dài không xác định; không có cờ D.
- **V_ngắn = 8.991 đ/cp** (tái đầu tư 0,570; ROE toàn vốn sau KTPL 8,78%). FCFE âm do capex tăng trưởng (trại heo) và BĐS dở dang tăng; không phải tín hiệu đắt. Tâm không trộn với V_ngắn.

## 6. Định giá

### 6a. Khung, V1
- Thu nhập thặng dư: V = E_op × (ROE_op × (1 − k) − g)/(r − g) + XDCB + BĐS dở dang − haircut (xấu) + lá chắn thuế 129,4 tỷ (tốt). E_op = 8.720,4 − 1.302,6 − 1.186,4 = 6.231,4 tỷ; 431,05 triệu cp; g = 5%; biên kịch bản ±3,25 điểm % ROE toàn vốn.
- **r = 13,5%** (V1): neo 7,4% lãi huy động 12T hiệu dụng; `deposit_rate_vn.effective_deposit_rate('2026-11-23')` = 7,4% (cctg_12m 02/11) ⇒ Δ = 0, β = 1.

| Lãi huy động | Tâm β = 1 | Tâm β = 0,5 |
|---|---|---|
| −100bp | 19.292 (+9,2%) | 18.432 (+4,3%) |
| −50bp | 18.432 (+4,3%) | 18.041 (+2,1%) |
| +50bp | 16.999 (−3,8%) | 17.326 (−2,0%) |
| +100bp | 16.395 (−7,2%) | 16.999 (−3,8%) |

- Dải Ke D4: 12,3% → 19.669; 13,4% → 17.818. g 4% → 17.887; 6% → 17.403. Terminal RONIC = Ke (moat NARROW, D4).

### 6b. Kịch bản

| Kịch bản | Xác suất | Giá trị trước chiết khấu thanh khoản |
|---|---|---|
| Xấu (ROE −3,25đ% toàn vốn; haircut 40% XDCB trại heo) | 25% | 10.471 |
| Cơ sở (ROE_op 13,81%) | 50% | 18.162 |
| Tốt (ROE +3,25đ%; + lá chắn thuế 129,4 tỷ) | 25% | 25.341 |
| **Kỳ vọng sau chiết khấu 2%** | | **17.673**, vùng [10.262; 24.835] |

Trọng số 35/50/15 → 16.216 (−8,2%); 15/50/35 → 19.131 (+8,2%).

### 6c. V3 — thanh khoản
Chiết khấu 2% (ước lượng, ADV đo sau khoá ở rev1 18/11; vị thế ≤ 20 tỷ thoát ≤ 10 phiên ở mức tham gia 10%). Trước chiết khấu 18.034; 0% → 18.034; 5% → 17.132. Nhãn dùng giá trị sau chiết khấu. Phiên 23/11: giá trị khớp G1 31,3 tỷ (DNSE `grossTradeAmount`).

### 6d. So giá (sau khoá)
- **Giá DNSE `latest_trade` G1: 16.400 đ (khớp 14:45, 23/11/2026).** Giá/tâm 0,93; giá/cơ sở 0,92; P/B hàm ý tại tâm 0,87; P/E chuẩn hoá hàm ý 8,9.
- Giá/tâm qua các phán đoán chính: cửa sổ 0,61–1,68; tài trợ XDCB+BĐS 50–100% 0,93–1,19; hết miễn giảm thuế 0,93–0,99.
- **⇒ Nhãn: quanh giá trị hợp lý (dưới tâm ~7%), chưa đạt cổng 0,85×tâm = 15.022.** Đổi lớp so với rev3 ("quanh/trên, không rẻ", giá/tâm 1,10).

## 7. Pháp lý / quản trị — chỉ WARNING
- EY: kiểm toán 2025 chấp nhận toàn phần; soát xét H1/26 sạch. KT22 điều chỉnh giảm LNST Q4/22 144,9 tỷ ⇒ theo dõi chất lượng số quý chưa kiểm toán.
- Phải thu người lao động 237,1 tỷ (TM 4a Q3/26; ~178 tỷ GPMB dự án chăn nuôi theo TM 7.1 H1/26): WARNING; mất trắng −539 đ/cp.
- Nghĩa vụ tái chế bao bì (KT25 TM35) chưa xác định số tiền — xem C4. Bên liên quan Transeco 20 tỷ.
- Không kiểm chứng được: giấy phép môi trường từng trại; thời hạn ưu đãi thuế từng công ty con; toàn văn ESOP 2026 (độ nhạy pha loãng 1–3%: 17.595 / 17.444).

## 8. 5F (V5)
Tái dùng rev1 §8 (18/11/2026, < 12 tháng): **moat_tier = NARROW (mỏng)**, COST/INTEGRATION; rủi ro số 1: chu kỳ giá heo + ASF. Kiểm nhanh rev4: ROE_op lõi 8,5% (W20) – 20,0% (W12), không qua tiêu chí lợi nhuận siêu ngạch bền ⇒ không thưởng tham số moat. BĐS không phải nguồn lãi định kỳ; quỹ đất ghi sổ sách.

## 9. Mốc khoá trước — cả hai chiều

**Trượt cửa sổ (cơ học):** khi có Q4/26, Q1/23 (lỗ −320,7 tỷ) và Q4/21 rơi khỏi cửa sổ ⇒ tâm tăng dù quý mới lỗ: LNST Q4/26 −50 tỷ → 20.159 (+14,1%); +35 → 20.700 (+17,1%); +120 → 21.226 (+20,1%) (ước lượng: vốn chủ Q4 = Q3 + LNST, XDCB/BĐS giữ Q3). ⚠️ Đổi nhận định dựa vào bảng dưới, KHÔNG dựa vào mức tăng cơ học; rev sau báo kèm tâm "neo khung" giữ các quý đầu cửa sổ của rev4.

| Mốc | Thời điểm | Chiều tăng | Chiều giảm |
|---|---|---|---|
| BCTC Q4/26 | ≤ 30/01/2027 | LNST ≥ 120 tỷ, không trích lập TSSH ⇒ trọng số tốt 35% | LNST < −50 tỷ hoặc trích lập > 100 tỷ ⇒ trọng số xấu 35% |
| BĐS dở dang (TM tồn kho) | mỗi BCTC | Doanh thu BĐS bàn giao có biên ≥ 20% ⇒ xác nhận sổ sách | Trích lập BĐS hoặc dở dang tăng tiếp > 1.400 tỷ mà doanh thu BĐS < 50 tỷ/năm ⇒ kịch bản haircut 20% |
| Thuế TNDN (TM thuế KT26) | ~03/2027 | Miễn giảm ≥ 4% LNTT | Miễn giảm < 2% LNTT ⇒ đưa −3% … −6% vào base |
| Nghĩa vụ tái chế bao bì | KT26 | Số được xác định ≤ 10 tỷ/năm | > 30 tỷ/năm ⇒ vào base (D3) |
| Trích KTPL từ LN 2026 | ~04/2027 | ≤ 6% LNST | ≥ 15% LNST |
| Giá heo T1/27 (Bobby F1/F2) | 05/02/2027 | ≥ 65k/kg | < 50k/kg |
| BCTC Q1/27 | ≤ 30/04/2027 | LNST ≥ 300 tỷ và biên gộp ≥ 8,5% | LNST < 150 tỷ |
| Lãi huy động 12T | liên tục | −50bp ⇒ +4,3% | +50bp ⇒ −3,8% |
| Phải thu người lao động | BCTC Q4/26 | ≤ 150 tỷ ⇒ gỡ WARNING | > 300 tỷ hoặc trích lập |

## 10. Điểm yếu của chính báo cáo
1. Tâm phụ thuộc mạnh vào cửa sổ (0,61–1,68 giá/tâm) và giả định tài trợ XDCB+BĐS (tới −34%). Đọc vùng, không đọc tâm như con số chắc.
2. BĐS dở dang Q3/26 lấy bằng số 30/6 (Q3 không tách); quý giữa nội suy. BĐS ghi sổ sách NPV = 0 dù bán chậm — nếu dự án ứ đọng nhiều năm, giá trị thời gian làm giảm (độ nhạy −3% … −6%).
3. Thời hạn miễn giảm thuế từng công ty con không công bố; nghĩa vụ tái chế bao bì chưa có số — cả hai là rủi ro GIẢM chưa vào base (−1,5% … −9,5% tuỳ mục).
4. Người dựng đã thấy giá ở rev1–rev3; rev4 đẩy tâm LÊN (thuận chiều mua) ⇒ lý do duy nhất là sửa không nhất quán mô hình do skeptic r3 chỉ ra, có số dư kiểm toán từng năm; không đổi tham số nào khác.

## 11. Nguồn
- BCTC hợp nhất kiểm toán `src/kt22_hopnhat_vi.pdf` (TM8 trang 30), `src/kt23_hopnhat_vi.pdf` (TM8 trang 30), `src/kt24_hopnhat_vi.pdf`, `src/kt25_hopnhat_vi.pdf` (TM9 trang 31, TM31 trang 46, TM35 trang 54; EY). Soát xét H1/26 `src/h1_d.pdf` (TM8 trang 37, TM7.1 trang 36). Q3/26 `src/q3_hopnhat.pdf` (TM7 trang 12–13).
- Ảnh kiểm chứng rev4: `png/r4_kt22_tm8_inventory.png`, `png/r4_kt23_tm8_inventory.png`, `png/r4_kt25_tm9_inventory.png`, `png/r4_h1_tm8_inventory.png`, `png/r4_kt25_tm31_cit.png`, `png/r4_kt25_tm35_commit.png`.
- BQ `tav2_bq.ticker_financial` (LNST, vốn chủ). Lãi suất `deposit_rate_vn`. Giá DNSE (sau khoá). Ngành: Bobby sector read 18/11. 5F: `REPORT.md` §8.

## 12. Sổ giá
- KHÔNG ghi `kb/dd_price_zones.json`. Đề xuất: `LEDGER_PROPOSAL_DBC.json` (rev 3 của dd_date 2026-11-18).
- Tâm 17.673; vùng [10.262; 24.835]; center_alt (cơ sở sau chiết khấu) 17.798; giá tham chiếu 16.400 (23/11/2026); assumptions_md5 `57b36d63e05ad2e2c209f2ce34fda8c9`.
