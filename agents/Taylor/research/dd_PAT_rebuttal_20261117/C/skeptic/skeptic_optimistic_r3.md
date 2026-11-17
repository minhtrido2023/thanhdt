# PAT r3 — Phản biện LẠC QUAN (stateless, mù giá thị trường), 17/11/2026

Vai trò: cố chứng minh tâm r3 (66.864 đ/cp) **quá THẤP**. Không tra/nhắc giá cổ phiếu, P/E, P/B, vốn hoá, mục tiêu giá.
Đã đọc: `RULES.md`; `C/VALUATION_r3.md`; `C/assumptions_objective_r3.md`; `C/calc_r3/*` (chạy lại `ebit_2026_2027.py` trên bản sao tạm, khớp 108,9); `A/A1`, `A/A2`, `A/A3` (theo mục); factpack F1, F2, F4 và `factpack/data/*.csv`; `blind_val_20261114/inputs/facts_extracted.md`, `sector_read_phot_pho_20261114.md`. Ảnh BCTC tự xem: `png_q326/p06.png` (BCĐKT nợ+VCSH), `p07.png` (KQKD), `p24.png` (TM11–14 thuế), `p31.png` (TM28 chi phí theo yếu tố, TM29 địa lý). Không đọc tệp bị cấm.

---

## VERDICT

**r3: CONFIRMED (KHÔNG bị chứng minh là quá thấp).**

- **Khoảng tâm sau hiệu chỉnh lạc quan có bằng chứng: 67.000 – 71.500 đ/cp, điểm ≈ 69.200** (+2.300, +3,4%). Mức này nằm trong biên "không thay đổi nào vượt ±5.000" mà r3 tự nêu.
- Ba chỉnh lạc quan có bằng chứng, đều mức TRUNG BÌNH hoặc THẤP:
  - E1, khối O3 vĩnh viễn: +1.200 (khoảng 0…+2.400).
  - E2, tồn kho dư: +800 (0…+1.740).
  - E3, điện tính trên 100% chi phí DV mua ngoài: +300 (0…+500).
- Không có nút nào bi quan mà thiếu bằng chứng ở mức làm đổi kết luận.
  - Thuế XK 15% (xác suất 0,97) có văn bản.
  - Than cốc 2027 = 2.108 thấp hơn mức thực Q4/26 là 2.156.
  - Cầu EBIT 2027 đúng số học.
  - Đối chiếu chu kỳ 2023–25 theo cùng quy ước cho thấy EBIT dài hạn của r3 ngang **năm tốt nhất** (2025), không thấp hơn.
- Một số chỗ r3 đang **lạc quan sẵn**, đi ngược luận điểm của nhà đầu tư:
  - Ánh xạ nhánh giữa P: nếu ánh xạ tuyến tính thì còn 60.200.
  - Proxy DT/DV mua ngoài cho thấy giá DLC trả PAT Q3/26 ≈ Q3/25, trong khi P4 TQ tăng 22%.
  - Rủi ro chuyển giá phía quặng (88,5% NVL mua từ DLC) không có trong mô hình.
- Độ tin cậy của phán quyết: trung bình. Hai ẩn số lớn nhất (giá DLC trả PAT, giá thực hiện/tấn) không quan sát được, cả hai chiều.

---

## Đòn 1 — Kiểm dữ kiện/số trong r3 so với BCTC gốc và factpack

| # | Số trong r3 | Giá trị r3 | Nguồn đối chiếu | Giá trị gốc | Kết quả |
|---|---|---|---|---|---|
| 1 | DT thuần Q3/26 | 440,032 | ảnh `png_q326/p07` (KQKD mã 10) | 440.032.422.804 | KHỚP |
| 2 | DT thuần 9T/26 (→ H1 = 939,271) | 1.379,304 | `p07` | 1.379.303.850.164 | KHỚP (H1 = 939,272, làm tròn) |
| 3 | DT thành phẩm 9T/26 (REV gốc) | 1.366,520 | facts_extracted §TM (DT TP 1.366,52) | 1.366,52 | KHỚP (chưa tự xem ảnh TM DT) |
| 4 | EBIT Q3/26 | 53,844 | `p07`: LN gộp 63,604 − BH 5,049 − QLDN 4,711 | 53,844 | KHỚP |
| 5 | EBIT H1/26 | 151,717 | 9T: 250,598 − 32,289 − 12,750 = 205,559 − 53,844 | 151,715 | KHỚP (lệch 0,002, làm tròn) |
| 6 | LNST 9T/26 (cơ sở KT-PL 6%) | 215,713 | `p07` mã 60; `p06` LNCPP 420b | 215.712.839.971 | KHỚP |
| 7 | GPM Q1/Q2/Q3 | 13,6% / 25,0% / 14,5% | `pat_identified_periods.csv` (GP H1 186,994; Q3 63,604) | Q1 57,59/421,92 = 13,65%; Q2 129,40/517,36 = 25,0%; Q3 14,45% | KHỚP |
| 8 | Vay NH | 67,218 | `p06` mã 321 | 67.217.555.923 | KHỚP |
| 9 | Quỹ KT-PL (trừ khỏi tiền) | 76,690 | `p06` mã 323 | 76.689.866.077 | KHỚP |
| 10 | Tiền | 1,246 | facts_extracted (BS 1,246; TM3 1,286) | 1,246 / 1,286 | KHỚP BS. Lệch nội bộ BCTC 0,04 tỷ, không trọng yếu |
| 11 | HTM | 558,069 (gồm lãi dự thu 6,50) | facts_extracted §TM HTM | 558,07 | KHỚP |
| 12 | Nợ dài hạn | 0 | `p06`: Nợ phải trả 233,74 = Nợ ngắn hạn 233,74 | 0 | KHỚP |
| 13 | Tiền ròng 357,35 | 415,407 − 45,11 − 12,94 | tự tính lại | 357,353 | KHỚP |
| 14 | Thuế XNK 9T/DT nước ngoài | 51,610/487,508 = 10,59% | `p24` TM13 (51.610.325.083); `p31` TM29 (487.507.728.152) | 10,59% | KHỚP. Dòng "xuất, nhập khẩu" có thể lẫn thuế NK nhỏ (thuế GTGT NK 0,162) |
| 15 | FY25 thuế XNK/DT nước ngoài | 88,627/1.738,334 = 5,10% | F2 §1.5 (KT TM13); facts_extracted KT 2025 | 5,10% | KHỚP (chưa tự xem ảnh KT) |
| 16 | NVL 9T/26 (cơ sở mức NVL/DT) | 709,270 | `p31` TM28 | 709.269.920.510 | KHỚP. Quy về GVHB (×1.116/1.141) ⇒ NVL/DT ≈ 50,8% so với nvl9 50,7% của mô hình |
| 17 | DV mua ngoài 9T/26 | 373,218 (DV/DT 25,08%) | `p31` TM28 | 373.218.345.470 | KHỚP; 25,08% hợp lý sau khi tách phần DV vào BH (vận chuyển 22,84) |
| 18 | Bán DLC 9T 63,7%, Q3 85,5% | | F2 §2.2 (Q3 TM30) | 878,140/1.379,304; 376,286/440,032 | KHỚP |
| 19 | Tồn kho NVL 21,0 → 49,7; TP +16,65 | | F2 §1.5 | 21,049 → 49,738; 53,794 → 70,448 | KHỚP |
| 20 | Cầm cố 70 tỷ BIDV (điện); 40 tỷ + 100k USD Vietinbank | | facts_extracted HTM; A3 §1.4 | đúng | KHỚP |
| 21 | Than cốc H1/Q3/2025 | 1.541 / 2.040 / 1.491 | `pat_commodity_quarterly.csv` | Q1 1.411,8, Q2 1.660,7 (TB đơn 1.536); Q3 2.040,2; 2025 TB 1.491,4 | KHỚP (H1 1.541 theo trọng số ngày, lệch 5 CNY, không trọng yếu) |
| 22 | KH LNST 2026 = 280 ⇒ Q4 ≈ 64,3 | | F1 (Báo Pháp Luật 24/10/2026) | 280 − 215,713 = 64,29 | KHỚP |
| 23 | Thuế TNDN 5% (2027–30) / 10% (2031–32) / 20% (2033+) | | F2 §1.5 (Q3 TM27: ưu đãi 10% 2018–2032, giảm 50% 2022–2030) | đúng | KHỚP |
| 24 | E[f] = 0,95953; ELEC = 1,008148; λ = 0,054874; P_B(13,5) = 0,523 | | tự tính lại bằng tay | 0,95953 / 1,00815 / 0,054873 / 0,5233 | KHỚP |
| 25 | Cầu EBIT 283,3 → 108,9 | | chạy lại `ebit_2026_2027.py` (bản sao tạm) | 283,3 −72,8 −34,7 −39,3 −3,7 −23,9 = 108,9 | KHỚP |

**Kết luận đòn 1:** không tìm thấy lỗi số nào làm giảm giá trị.
- Lệch duy nhất có ý nghĩa nằm ở chiều ngược lại: điểm xuất phát của cầu (khung mô hình 9T quy năm = 283,3) cao hơn số thực 9T quy năm là 274,1 (205,559 × 4/3), tức cầu bắt đầu **lạc quan hơn** thực tế 9 tỷ.
- Cả 2027 lẫn dài hạn đều tính từ mức chi phí, không phải từ điểm xuất phát này, nên không đổi giá trị.

---

## Đòn 2 — Logic cây kịch bản, xác suất, nhánh thiếu, đếm trùng

**2.1 Xác suất bất lợi.**
- TX 0,97: có văn bản NĐ 199/2025 (A2 §a1), các dự thảo không có P4 (A2 §a2). Không vượt mức bằng chứng cho phép.
- T_a 0,65: chưa có nguyên tắc giá (#N12). Tuy vậy hai bằng chứng độc lập đều nghiêng về phía bất lợi cho PAT, nên 0,65 không phải bi quan thiếu cơ sở:
  - Động cơ cổ đông kiểm soát: DLC giữ 51% PAT, và DGC sở hữu 100% DLC (F2 §2.1).
  - Proxy DT/DV mua ngoài Q3/26 YoY +0,2% trong khi P4 TQ +22,2% (A3 §3.2(iv)): giá DLC trả gần như không theo thị trường.
- A-không-bao-giờ 0,5 và P(A) 0,5: trung tính, giữ.
- B: hazard theo Bobby F7, không có khối vĩnh viễn, nên đã là cách xử lý thuận lợi.
- P: 0,32 nhánh thấp so với 0,10 nhánh cao, nhưng nhánh giữa ánh xạ = 1,0 dù trung vị F2 thấp hơn 9T khoảng 10%. Tổng thể nút P **không** bi quan, r3 tự ghi (độ nhạy 0,977 ⇒ 60.200).

**2.2 Đếm trùng thuế XK / giá DLC / quặng.** Không tìm thấy đếm trùng trong tâm:
- Thuế chỉ vào qua `f` trên doanh thu (`model_r3.py` hàm `value`: `ff = f*(1-0.65*transfer)`, `transfer = 0` ở tâm).
- Giá P4 chỉ vào qua `p`.
- Quặng chỉ vào qua NVL_y nhân với DT cơ sở. Chi phí tuyệt đối không bị nhân `f` hay `p`, nên không có chuyện thuế bị trừ hai lần.
- Than cốc vào qua K; mức GĐ1/GĐ2 đã quy về cốc chuẩn trước khi cộng, nên không trùng với bước quặng.
- "DLC dưới netback −5%" chỉ là độ nhạy, không nằm trong tâm.
- Lưu ý (không phải đếm trùng): mức cơ sở 9T/26 đã chứa giá DLC có vẻ thấp so với thị trường, rồi T_a áp thêm trọn bước thuế. Hai điều này nhất quán nếu DLC định giá theo netback trừ một khoản cố định, nên không phải lỗi.

**2.3 Nhánh thiếu** (theo mức quan trọng với chiều lạc quan):
- (i) **Kênh cung quặng thứ ba ngoài A (mỏ DGC) và B (3 nhà máy tuyển VAPC)**: Tam Đỉnh–Làng Phúng 250 kt/năm "cũng đi vào sản xuất" (Báo Lào Cai 20/10/2026), nhà máy tuyển quặng nghèo Cam Đường 200 kt/năm chạy thử Q4/26 (A1 §B dòng 51), chỉ đạo UBND Lào Cai "trợ giá, giảm giá thành quặng apatit" cho PAT (A1 §C5 dòng 84; F3). Trong cây r3, khi D=A và A không bao giờ giải thì chi phí kẹt ở O3 (mức khủng hoảng Q3/26) **tới 2045 và cả terminal**, bất kể B hay kênh thứ ba ⇒ xem E1.
- (ii) Không có nhánh tăng tương ứng với độ nhạy "DLC dưới netback −5%": độ nhạy giá chuyển nhượng chỉ có chiều xấu. Tuy vậy bằng chứng hiện có (DT/DV) nghiêng chiều xấu, nên **không** đưa vào tâm.
- (iii) Nhánh giảm thuế XK P4 trở lại sau 2027: không có bằng chứng; chủ trương là đẩy chế biến sâu (sector_read dòng 49, 111). Không thêm.

---

## Đòn 3 — Nút nào bi quan thiếu bằng chứng?

**3.1 Thuế XK 15% từ 01/01/2027, xác suất 0,97 — ĐỨNG.**
- NĐ 199/2025 (A2 §a1) và Báo Chính phủ 09/07/2025 + EY đều khớp 15% từ 2027.
- Dự thảo 03/02/2026 chỉ có 3 mặt hàng, không P4; dự thảo 25/08/2026 không thấy 2804 (A2 §a2).
- Khẳng định "Hàn/Đài không bị thuế" là SAI theo văn bản (A2 §b): chỉ Nhật (CPTPP 0% từ 2025) và EU (0% từ 2027).
- Bản thân PAT đóng đủ mức MFN (`p24`: 51,61 trên DT nước ngoài 487,51 = 10,59%). Dù có khách EU (Italmatch, phải thu 21,03 tại 31/12/25 — F2/facts_extracted), PAT vẫn không hưởng EVFTA 5% năm 2026. Vì vậy không có bằng chứng PAT sẽ dùng kênh 0% năm 2027.

**3.2 Cầu EBIT 2027 ≈ 109 so với 2026E ≈ 259 — số học đúng, từng bước có bằng chứng.**
- Thuế −72,8 = (1 − E[f]) × DT × E[p] ≈ 4,05% × 1.822.
- Than cốc −34,7: 9T ≈ 1.700 → 2.108; giá TB thực Q4/26 (tới 13/11) **2.156** (`pat_commodity_quarterly.csv`) ⇒ giả định 2027 **thấp hơn** giá giao ngay, không bi quan.
- Quặng −39,3: H1/27 vẫn ở GĐ2. Không có quyết định mở lại mỏ nào tới 17/11 (A1 §B); Ai Cập chỉ đảm bảo tới hết Q1/27 (A1 §C2).
- Điện −3,7.
- Giá −23,9: E[p] = 0,986. P4 TQ Q4/26 = 28.191, cao hơn TB 9T 27.741 khoảng 1,6%, nên đây là phần duy nhất có thể nói hơi bi quan cho 2027. Nhưng nhánh giữa P đang ánh xạ lạc quan cho dài hạn, nên **không** sửa.
- 259 so với 109: 24 tỷ chênh giữa 283 và 259 là do điểm xuất phát (đòn 1) và Q4 = Q3. 150 tỷ còn lại đã được bóc tách ở trên.

**3.3 Đối chiếu chu kỳ 2023+ cùng quy ước.**
- Đặt EBIT thực 2023–25 (`pat_identified_periods.csv`) về nền thuế 15%, với giả định thuế XK trước 2026 = 5% như FY25 (5,10%); 2023–24 chưa kiểm văn bản.
- Cách đặt: EBIT − s × (1 − 0,85/0,95) × DT.

| Năm | EBIT thực | DT | EBIT ở thuế 15%, s = E[s] 0,751 | Biên trên DT sau thuế | Ở s = 1 |
|---|---|---|---|---|---|
| 2023 | 265,8 | 1.710,6 | 130,6 | 8,3% | 85,7 |
| 2024 | 248,8 | 1.721,4 | 112,8 | 7,1% | 67,6 |
| 2025 | 343,5 | 1.923,4 | 191,5 | 10,8% | 141,1 |
| **r3 2027 (E)** | 108,9 | | | **6,3%** | |
| **r3 dài hạn (E, giá 2028)** | 185,8 | | | **10,8%** | |

- ⇒ Biên EBIT dài hạn của r3 **bằng năm tốt nhất 2025**: năm đó có quặng tự khai thác và than cốc 1.491. Biên này cao hơn 2023 và 2024. Biên 2027 ≈ ngang 2024.
- Đối chiếu chu kỳ **không** ủng hộ luận điểm "r3 quá bi quan".
- Tuy nhiên, phép "kiểm GPM15" của r3 (VALUATION §2) trộn quy ước: lịch sử quy theo s = 1, mô hình ở E[s]. Xem E4: lỗi phương pháp, không đổi giá trị.

**3.4 Giá chuyển nhượng DLC theo netback (T_a 0,65) — KHÔNG đủ bằng chứng để giảm.**
- Lập luận ủng hộ lạc quan:
  - DLC thiếu P4/quặng cho dây chuyền axit (A1 dòng 84). Phần P4 dùng nội bộ làm H3PO4 không chịu thuế XK P4 (sector_read dòng 49; A2 dòng 173: DGC tiêu thụ nội bộ một phần).
  - Tỷ trọng bán DLC tăng từ 8,5% (FY25) lên 85,5% (Q3/26) (F2 §2.2), khớp với giả thuyết DLC mua P4 của PAT cho hạ nguồn.
- Lập luận bác:
  - Việt Nam là nước xuất ròng P4 (A2 §c1), nên giá P4 nội địa biên vẫn bằng netback xuất khẩu.
  - Động cơ cổ đông kiểm soát (DLC 51%, DGC 100% DLC).
  - Proxy DT/DV (A3 §3.2(iv)) cho thấy DLC trả ≈ giá 2025.
- Độ nhạy (KHÔNG đưa vào tâm): chuyển 0,10 từ T_a sang T_b ⇒ 68.672 (+1.808).

**3.5 Than cốc −35 — ĐỨNG.** Q4/26 thực 2.156 > 2.108. Than cốc dài hạn 1.825 thấp hơn TB 2020–2026 (≈ 2.090, tự tính từ `pat_commodity_quarterly.csv`), tức thuận lợi. Tỷ lệ P4/than cốc dài hạn ≈ 15 so với 13,9 (2024–25) và 12,2 (2023), cũng thuận lợi.

**3.6 Giá điện — gần đúng.** Có một điểm thấp, xem E3: hệ số F5 cộng mức cắt nhân lên 100% DV mua ngoài, trong khi r3 tự ghi đó là CẬN TRÊN (A3 §1.4).

---

## Đòn 4 — Tâm lạc quan hiệu chỉnh: chỉ thay đổi CỤ THỂ có bằng chứng

Phương pháp: chạy lại `model_r3.run()` trên bản sao tạm của `calc_r3/` (không sửa tệp gốc). Biến thể đặt vào hàm `leaf_nvl`/hằng số như mã dưới. Các phần tiền mặt tính trực tiếp theo 1 tỷ = 40 đ/cp.

| # | Thay đổi | Bằng chứng | Kết quả cây (đ/cp) | Δ | Đưa vào tâm |
|---|---|---|---|---|---|
| E1 | Nhánh D=A ∧ A không bao giờ: khi B đã giải, chi phí về **trung điểm (O2+O3)/2** (2027: (R27+U27)/2) thay vì kẹt O3 vĩnh viễn. Hệ quả: E[NVL] dài hạn 50,57% → 50,04% | Kênh cung thứ ba ngoài A/B: Tam Đỉnh 250 kt "đi vào sản xuất" (A1 §B dòng 51), DGC đã mua của Tam Đỉnh (A1 dòng 32); Cam Đường 200 kt; UBND "trợ giá" (A1 dòng 84). r3 tự lập luận B không có khối vĩnh viễn vì nguyên nhân là hành chính. Áp nhất quán cho chi phí: 20 năm không có điều chỉnh chuỗi cung nào là giả định cực đoan | 69.237 | +2.373 | **½ = +1.200** (bằng chứng trung bình–yếu: chưa xác minh vận hành/khách hàng của Tam Đỉnh; trợ giá chưa có văn bản/thời hạn) |
| E2 | ΔVLĐ = 0 bỏ qua **tồn kho dư** tại 30/09: NVL 49,74 so với TB 3 mốc 21,6 (+28,1); TP 70,45 so với TB 55,1 (+15,4) ⇒ 43,5 tỷ | F2 §1.5 (4 mốc tồn kho, không dự phòng giảm giá). Giải phóng khi cung quặng bình thường hoá; P(đã giải tới 01/2028) ≈ 0,512 (assumptions §3); PV ×0,82 | tiền: 43,5 × 0,55 × 0,82 ≈ 19,6 tỷ | +780 (trần +1.740 nếu giải ngay) | **+800** |
| E3 | Hệ số điện 1,00815 (F5 tăng ròng) chỉ áp cho phần điện của DV, không phải 100% DV | A3 §1.4: "điện = 100% DV là CẬN TRÊN"; kiểm từ dưới lên 383–533 tỷ so với DV 502 (điện "có thể là phần lớn"). Giả định tỷ trọng điện 0,5–0,7 (chưa kiểm) | ≈ 1,1–1,9 tỷ/năm EBIT | +280…+470 | **+300** |
| — | **Tổng tâm lạc quan có bằng chứng** | | | **≈ +2.300** | **≈ 69.200** (khoảng 67.000–71.500) |

**Đã kiểm và BÁC (không đưa vào tâm):**
- **O1 (mức NVL/DT 2025 = 46,6%) chưa quy đổi theo mặt bằng giá 9T/26.**
  - Nếu giá thực hiện/tấn 2026 cao hơn 2025 theo P4 TQ (+20,3%) × netback thuế (0,947) thì ρ = 1,139 ⇒ O1 42,5% thay vì 48,2% ⇒ 73.063 (+6.199); ρ = 1,07 ⇒ +3.323.
  - Nhưng proxy DT/DV mua ngoài cho 9T/26 = 3,70, còn 9T/25 = 3,94 và FY25 = 3,83 (tự tính từ `p31` + F2 §1.4; A3 §3.2(iv)). Giá thực hiện/đơn vị sản xuất KHÔNG tăng, nên ρ ≈ 1 và tác động ≈ 0.
  - Ghi như lỗi phương pháp E5, không đổi tâm.
- **Sản lượng phục hồi khi hết thiếu quặng:** DV 9T/26 +3,4% YoY (F2 §1.4), tức sản xuất 9T ≈ 9T/25 (≈ công suất). Cơ sở 1.822 không bị nén. Bác.
- **PAT tự dùng kênh EVFTA 0% từ 2027:** năm 2026 không dùng được 5% EVFTA (tỷ lệ 10,59%), nên không có bằng chứng. Bác (≤ +550 nếu có).
- **Giảm T_a:** xem 3.4. Bác (chỉ là độ nhạy +1.808).
- **Tiền gửi 70 tỷ tính theo mệnh giá (+1.800):** đây là tài sản bảo đảm còn dùng chừng nào còn mua điện; cách r3 tính (PV của lãi) là hợp lý. Bác.

Mã biến thể (chạy trên bản sao tạm `calc_r3`, đã xoá sau khi chạy):

```python
import model_r3 as M
def center(): M._cache.clear(); return M.run()['center']
# V1 (bác): M.O1 = 0.4660/rho + M.K*(1825-1491)  -> rho 1.035/1.07/1.139: 68.582 / 70.188 / 73.063
# E1: trong leaf_nvl, thêm nhánh: elif D=='A' and (not a_yes) and B_ok: s += 0.5*(res+unres)   -> 69.237
# T 0.55/0.35/0.10 (độ nhạy): M.PT={'Ta':(1.0,0.35,0.55),'Tb':(0.35,0.35,0.35),'Tc':(0.135,0.135,0.10)} -> 68.672
```

---

## Danh sách lỗi theo mức nghiêm trọng (góc nhìn lạc quan)

1. **TRUNG BÌNH — E1: khối O3 vĩnh viễn 25% trọng số dài hạn** (`model_r3.py` `leaf_nvl`: D=='A' ∧ not a_yes ⇒ unres mãi).
   - Chi phí khủng hoảng Q3/26 được coi là kéo dài tới terminal dù có kênh cung thứ ba và B giải. Điều này không nhất quán với chính lập luận "không khối vĩnh viễn" mà r3 dùng cho B.
   - Tác động +0…+2.400; điểm +1.200.
2. **THẤP — E2: ΔVLĐ = 0 bỏ qua tồn kho dư 43,5 tỷ** (NVL ×2,3 so với mức thường). Tác động +0…+1.740; điểm +800.
3. **THẤP — E3: hệ số điện trên 100% DV** (r3 tự thừa nhận là cận trên). Tác động +280…+470.
4. **THẤP/PHƯƠNG PHÁP (không đổi giá trị) — E4: "Đối chiếu chu kỳ GPM15" trong VALUATION §2 trộn quy ước.**
   - Lịch sử quy theo s = 1, mô hình ở E[s] = 0,751. So cùng quy ước thì GPM dài hạn thấp hơn lịch sử 1,5–3,2pp: trông bi quan, nhưng GPM bị méo vì kênh DLC (giá xuất xưởng, chi phí bán hàng thấp — CPBH Q3 5,05 so với 20,55).
   - Thước đo đúng là biên EBIT: dài hạn 10,8% = 2025 (đòn 3.3). Nên viết lại phép kiểm theo EBIT.
5. **THẤP/PHƯƠNG PHÁP — E5: mức O1 (tỷ lệ NVL/DT của năm 2025) áp lên DT cơ sở 9T/26 mà không quy đổi mặt bằng giá.** Chiều tác động mơ hồ: P4 TQ ⇒ +, proxy DT/DV ⇒ ≈ 0. Nên ghi rõ giả định "giá thực hiện/tấn 2025 ≈ 9T/26".
6. **Ngược chiều (r3 đang lạc quan, nhà đầu tư không dùng được để nâng giá trị):**
   - Ánh xạ nhánh giữa P (tuyến tính ⇒ 60.200).
   - Điểm xuất phát cầu 283 > 274 thực.
   - Than cốc 2027 2.108 < 2.156 giao ngay.
   - Chuyển giá phía quặng (88,5% NVL mua từ DLC, F2 §2.2) không có nút.
   - Proxy DT/DV cho thấy giá DLC trả Q3/26 ≈ Q3/25 dù P4 TQ +22%.

---

## ĐÃ BỎ
- Không gặp và không tra số giá cổ phiếu/P/E/vốn hoá/mục tiêu giá nào. Không có mục bỏ.

## KHÔNG TÌM ĐƯỢC (đã thử)
- **Tỷ trọng điện trong DV mua ngoài:** BCTC không tách (đã xem `p31` TM28; A3 §1.4).
- **Sản lượng (tấn) và giá thực hiện/tấn 2025, 9T/26:** F1 chỉ có 2022–2024 (F1 bảng kế hoạch; mục "KHÔNG TÌM ĐƯỢC").
- **Bằng chứng Tam Đỉnh bán cho PAT/DLC sau 10/2026 và văn bản trợ giá quặng của UBND Lào Cai:** A1 chỉ có báo chí, văn bản gốc không tìm được (A1 §C5, §KHÔNG TÌM ĐƯỢC). Không tự tra web thêm (vai trò stateless, chỉ đọc đầu vào).
- **Thuế XK P4 năm 2023–2024 (giả định 5% khi quy chu kỳ):** chỉ có FY25 5,10% (F2 §1.5).

## ĐIỂM MÂU THUẪN
- Tiền: BCĐKT 1,246 so với TM3 1,286 (lệch 0,04 tỷ; facts_extracted).
- Than cốc H1 1.541 (r3) so với TB đơn 2 quý 1.536 (csv): trọng số ngày, lệch 5 CNY.
- Proxy DT/DV H1/26 −9,3% YoY so với Q3/26 +0,2% YoY (A3 §3.2(iv)): ngược chiều nhau, đều chưa tính tồn kho thành phẩm thay đổi.
- Đối chiếu chu kỳ: GPM nói "r3 thấp hơn lịch sử", biên EBIT nói "r3 = năm tốt nhất". Cách hoà giải là thay đổi cơ cấu kênh bán (DLC, giá xuất xưởng) — đây là nhận định, độ tin cậy trung bình.
