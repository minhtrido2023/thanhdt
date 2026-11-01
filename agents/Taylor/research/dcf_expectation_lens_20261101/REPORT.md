# Lăng kính kỳ vọng thị trường ("DCF nhẹ") — job Taylor_20261101_165940, 02/11/2026
R&D, KHÔNG wire, không sửa `dcf_valuation.py`, không đổi sản phẩm đang chạy. PREREG `1ec5daf27` (00:03 ICT, trước mọi số).
Mọi số dưới đây đo trong phiên; nguồn ở `out/run_*.txt` + `out/*.csv`. Universe = `universe_pit` phi tài chính, cuối tháng
2014-01 → 2026-10 (154 tháng); IS 2014-2019 / OOS 2020+; PE/PCF/EVEB = cột BQ cơ sở `Price` thô (CANONICAL).
Selfcheck: g1/gQ2 tính tay 200 dòng từ `ticker_financial` thô lệch 0; PE tự thân 40 (mã, tháng) tính lại từ cache ngày lệch 0;
tái lập %RẺ S0 = **53,1%** của bài trước (khớp); chạy lại dưới `env -u TZ` và `TZ=America/New_York` cùng kết quả (không đọc đồng hồ).

## Mở đầu — 4 câu trả lời

**(1) Thị trường có ngoại suy tăng trưởng 1-2 năm vào BỘI SỐ không? Nhìn chung KHÔNG — ngược lại.**
- Độ co giãn giá theo lợi nhuận TTM (cắt ngang, giá 12T vs Δlog LN 12T): **β = 0,18 (IS) / 0,12 (OOS)**, t 10,7 / 10,6. Bội số giữ
  nguyên thì β = 1; ngoại suy thì β > 1. Qua 24T: 0,31 / 0,20 cho năm gần nhất + 0,24 / 0,19 cho năm trước đó. Tức giá phản ứng
  với lợi nhuận **chủ yếu trong ~1 năm, phần năm thứ 2 nhỏ hơn** (đúng nhịp "1-2 năm" của user về THỜI GIAN), nhưng phản ứng
  chưa tới 1/3 mức tăng lợi nhuận ⇒ **P/E CO LẠI khi lợi nhuận tăng**, không nở ra.
- Ngũ phân vị tăng trưởng TTM cao nhất có P/E bằng **0,59× (IS) / 0,47× (OOS)** ngũ phân vị thấp nhất; và năm sau tăng trưởng
  của nhóm này THẤP hơn (chênh −0,08 / −0,31 đơn vị tăng trưởng đối xứng). Thị trường trả ít hơn cho tăng trưởng vừa qua, và
  dữ liệu nói như vậy là đúng hướng (tăng trưởng đảo chiều — khớp kết luận A bài trước).
- Mã đang trong chuỗi ≥ 5 quý tăng trưởng TTM ≥ 20%: giá 12T QUA tăng trung vị **+18,4% (OOS) / +28,4% (IS)** (nhóm không chuỗi
  +4,6% / +0,3%) — "giá chạy tốt" là ĐÚNG — nhưng do lợi nhuận tăng; P/E tự thân trung vị chỉ **18,8 (OOS) / 37,3 (IS)** so với
  75 / 69 ở nhóm không chuỗi. 12T SAU: trung vị −0,9% / −1,5% (nhóm không chuỗi +4,9% / 0,0%).
- **Ngoại lệ có hướng nhưng không có ý nghĩa thống kê**: nhóm thanh khoản cao nhất + ROE5Y ≥ 15% (14% số dòng) có P/E tự thân
  TĂNG theo chuỗi (+1,25 / +1,03 điểm phân vị mỗi quý chuỗi, t 1,3 / 1,2) trong khi phần còn lại GIẢM (−0,86 / −2,12, t −1,5 / −5,2).
  Đây là đúng hình ảnh của VCS 2015-18 (P/E 4,7 → 15,7), MWG 2015-17 (9,9 → 19,5), VNM 2015-18 (17 → 29), FPT 2020-25 (10 → 28,7).
  Câu chuyện của user có thật **ở nhóm chất lượng/vốn hoá lớn**, nhưng chưa đủ mạnh để gọi là quy luật (t ≈ 1,2).

**(2) Có nên xây "DCF nhẹ / lăng kính kỳ vọng" không? KHÔNG, ở cả 3 dạng được hỏi.**

| Dạng | Tiêu chí khai trước | Số đo | Kết luận |
|---|---|---|---|
| Cơ sở xếp hạng | ΔIC12 OOS vs S0 ≥ +0,01, CI loại 0, phần dư sau Q6 ≥ +0,01 | ΔIC12 OOS: L1 −0,004…−0,005, L2 −0,014, L3 −0,023…−0,025 (CI OOS chứa 0 hoặc âm); phần dư IC12 sau trực giao ≤ 0,009 | **Không qua** |
| Display "giá đang tính tăng trưởng X%" | R²_rel OOS ≥ 0,05 (giải thích giá tốt hơn S0) | R²_rel OOS: L1 −0,03, L2 −0,15…−0,17, L3 −0,34…−0,38 (KÉM hơn S0); "g ngầm định" = biến đổi đơn điệu của FCFE yield (Spearman −1,000) | **Không qua** — không thêm thông tin; chỉ đổi đơn vị |
| Cơ sở dự đoán de-rate | (Q3) | sau 477 sự kiện chậm lại: giá vượt đối chứng 12T **+6,3% [+2,6; +9,8]**, không sập; khi P/E tự thân > 67: P/E co −24% log [−42; −9] nhưng giá vượt đối chứng +6% [−1; +13] | **Không** — de-rate bội số có, thua lỗ tương đối không |

DCF nhẹ còn **dự báo lợi nhuận tệ hơn**: sai số trung vị |log| 1 năm 0,379-0,383 vs **0,304** (S0) vs 0,309 (g = 0); 2 năm
0,64-0,66 vs **0,413**. Phần IC tăng thêm của nó (ΔIC3 IS +0,015…+0,062) là **động lượng lợi nhuận ngắn hạn** — mất ở 12T và
OOS, và sau khi trừ SUE/NP_R (biến của LAG) + yield + momentum chỉ còn IC3 0,025-0,028 (cận dưới CI −0,001…+0,005) / IC12 0,005-0,009.
⇒ Giữ kết luận bài trước: **S0 (s 0, g_T 4,5%) cho giá trị nội tại**. Không đề xuất code, không knob.

**(3) Những gì KHÔNG chứng minh được** — xem §7. Chủ yếu: (a) ngoại suy ở nhóm chất lượng lớn (t ≈ 1,2); (b) β thấp có thể
một phần do nhiễu đo lường E (thành phần tạm thời) chứ không hẳn là thị trường "khôn" — không tách được; (c) vì sao FPT 2025-26
co P/E 28,7 → 9,7 khi tăng trưởng chỉ chậm từ 22% về 15% (dòng vốn ngoại, ngành CNTT toàn cầu?) — dữ liệu này không tách được.

**(4) Tự tấn công** cho quant-skeptic — §8. Phát hiện phụ đáng kiểm riêng (KHÔNG thuộc lăng kính này): `accS` = tăng trưởng 2 quý
gần nhất YoY − tăng trưởng TTM (gia tốc ngắn) giữ IC sau trực giao SUE/NP_R/yield/mom: **IC3 0,057 [0,036; 0,079]**, IC12 0,047
[0,023; 0,072], OOS 0,047 / 0,044. LAG đã có xếp lại theo `d_NPR` (gia tốc) trong cùng tầng surprise (`pt_v23_audit_2014.py`
~dòng 1092) ⇒ có thể phần lớn đã nằm trong LAG; cần PREREG riêng so với `d_NPR` trước khi nói gì thêm. Hậu nghiệm, N lớn.

## 1. Q1 — cửa sổ ngoại suy (`q1_extrap.py`, `q1b_elasticity.py`; `out/run_q1.txt`, `out/run_q1b.txt`)

**(a) Đơn biến log(P/E) (PE ∈ (0,200), trung vị ~230 mã/tháng)** — hệ số trên hạng (−0,5..0,5) = chênh top−bottom:

| Cửa sổ | R² IS / OOS | Hệ số IS (t) | Hệ số OOS (t) |
|---|---|---|---|
| gQ2 (2 quý YoY) | 0,026 / 0,030 | −0,29 (−4,0) | −0,42 (−6,4) |
| g1 (TTM 1 năm) | 0,079 / 0,104 | −0,69 (−12,3) | −0,85 (−11,1) |
| g2 (2 năm/năm) | 0,016 / 0,030 | −0,26 (−4,3) | −0,43 (−8,8) |
| g3 | 0,019 / 0,007 | −0,22 (−2,5) | −0,12 (−2,1) |
| g5 | 0,128 / 0,154 | −0,83 (−7,4) | −1,09 (−17,0) |
| acc (Δg1 so 4 quý trước) | 0,025 / 0,021 | −0,30 (−4,5) | −0,28 (−3,7) |
| accS (gQ2 − g1) | 0,008 / 0,007 | +0,14 (+2,9) | +0,11 (+3,4) |

Mọi cửa sổ có hệ số ÂM — một phần là cơ học (E ở mẫu số: E vừa tăng thì P/E tự giảm nếu giá chưa theo), nên PREREG Q1a không
đo được "ngoại suy" trực tiếp ⇒ bổ sung **hậu nghiệm** độ co giãn (b). Mô hình chung + ROE + quy mô (R² 0,36 / 0,50): g1 −0,43 / −0,39,
g5 −0,26 / −0,29, g2/g3 ≈ 0, **gQ2 +0,18 / +0,10 (t 3,1 / 2,1)** — trong cùng mức TTM, 2 quý gần nhất mạnh thì được trả P/E cao hơn,
và đúng hướng: gQ2 dự báo được tăng trưởng năm sau (hệ số f1 +0,39 / +0,44, t 11 / 6,8) còn g1, g5 dự báo NGƯỢC (−0,41 / −0,74;
−0,24 / −0,54). Tiêu chí "đúng 1-2 năm" (R² OOS cao nhất ∈ {gQ2, g1, g2}): R² cao nhất là g5 (do cơ học nền thấp) ⇒ tiêu chí
khai trước **không đạt**; nhưng về dấu thì không cửa sổ nào cho thấy ngoại suy.

**(b) Độ co giãn (hậu nghiệm, winsor 1%, trung vị ~200-290 mã/tháng):**

| Hồi quy | IS | OOS |
|---|---|---|
| log giá 12T qua ~ Δlog LN 1 năm | 0,180 (t 10,7) | 0,119 (t 10,6) |
| + Δlog LN năm trước nữa | 0,198 + **0,028** (t 2,1) | 0,126 + **0,025** (t 2,1) |
| log giá 24T ~ 2 năm LN | 0,307 + 0,241 | 0,199 + 0,187 |
| log giá 12T TỚI ~ Δlog LN năm tới (biết trước, chỉ để đo) | 0,158 | 0,102 |
| … + Δlog LN năm qua | +0,021 (t 2,2) | +0,017 (t 1,4) |

Giá phản ánh lợi nhuận **đồng thời và không đủ** (0,1-0,2 mỗi năm), không đi trước nhiều, có trôi sau nhỏ (PEAD, LAG đã khai thác).

**(c) Theo chuỗi** (số quý liên tiếp TTM ≥ 20%, `out/q1b_streak_table.csv`, OOS):

| Chuỗi | n | P/E tự thân trung vị | giá 12T qua | giá 12T tới | tăng trưởng năm tới f1 |
|---|---|---|---|---|---|
| 0 | 13.442 | 75,0 | +4,6% | +4,9% | +0,068 |
| 2 | 1.900 | 45,2 | +22,9% | −0,7% | −0,017 |
| 4 | 1.243 | 31,7 | +16,2% | −3,6% | −0,099 |
| 5 | 2.186 | 18,8 | +18,4% | −0,9% | −0,209 |

## 2. Q2 — DCF nhẹ (`q2_light.py`, `out/run_q2.txt`)
Base FCFE engine (147-~330 mã/tháng có FCFE 3Y > 0), r 12,25%, g_T 4,5%, g gần kẹp [−30%, +50%].

| Biến thể | R²_rel giải thích giá IS / OOS | MAE NP 1 năm / 2 năm (OOS) | IC3 (IS / OOS) | IC12 (IS / OOS) [CI] | ΔIC12 OOS vs S0 [CI OOS] | DSR IC12 |
|---|---|---|---|---|---|---|
| **S0** (g = g_T) | 0 / 0 | **0,327 / 0,428** | 0,020 (0,004 / 0,034) | 0,060 (0,047 / 0,075) [0,013; 0,114] | — | 0,748 |
| CUR (s 0,5 N 5) | +0,023 / −0,013 | 0,335 / 0,470 | 0,024 | 0,064 (0,050 / 0,078) | +0,004 [−0,013; +0,017] | 0,819 |
| L1_g1 | +0,021 / −0,028 | 0,411 / 0,546 | 0,026 | 0,062 (0,055 / 0,070) | −0,005 [−0,016; +0,006] | 0,722 |
| L1_gQ2 | +0,008 / −0,035 | 0,405 / 0,543 | 0,035 | 0,065 (0,060 / 0,070) | −0,004 [−0,011; +0,003] | 0,701 |
| L2_g1 | −0,045 / −0,149 | 0,411 / 0,726 | 0,029 | 0,060 (0,058 / 0,061) | −0,014 [−0,034; +0,005] | 0,680 |
| L2_gQ2 | −0,082 / −0,169 | 0,405 / 0,718 | 0,047 (0,052 / 0,042) | 0,063 (0,066 / 0,061) | −0,014 [−0,028; +0,004] | 0,690 |
| L3_g1 / L3_gQ2 | −0,18 / −0,34 · −0,25 / −0,38 | 0,411 / 0,726 | 0,030 / 0,052 | 0,055 / 0,058 | −0,023 / −0,025 | 0,64 |
| EP (1/PE, cơ sở E) | — | — | 0,038 (−0,009 / 0,080) | 0,066 (0,022 / 0,111) | +0,037 [−0,052; +0,122] | 0,671 |
| L2E_g1 (cơ sở E) | so EP: −0,97 / −0,97 | — | 0,040 | 0,050 | −0,015 | 0,657 |
| PEGY (g/PE) | — | — | 0,010 (0,051 / −0,027) | −0,006 (0,028 / −0,041) | −0,115 [−0,198; −0,020] | 0,078 |

- (ii) Chuẩn "không đổi" g = 0: MAE 1 năm 0,309, 2 năm 0,427 — S0 ngang/tốt hơn chút; mọi biến thể ngoại suy kém hơn và bias
  âm (dự quá cao). Tỷ lệ NP ≤ 0 sau 1 / 2 năm: 4,3% / 6,5% (bị loại khỏi MAE).
- (iii) Ngũ phân vị MoS → lợi suất 12T vượt TB (OOS): S0 Q1 −5,6% … Q5 +5,3%; L2_g1 Q5 chỉ +3,5% và Q4 +7,2% (không đơn điệu);
  CUR Q5 +7,4%. PEGY (mua tăng trưởng/PE) OOS âm có ý nghĩa: đúng điều Q1 nói — trả tiền cho tăng trưởng vừa qua là thua.
- DSR (IC12 tháng 12, T = 11 năm, N = 30, SR0 0,414): **mọi biến thể < 0,95**; không biến thể nào đạt chuẩn chọn.

## 3. Q3 — de-rating (`q3_derate.py`, `q3b_subgroups.py`; `out/run_q3.txt`, `out/run_q3b.txt`, `out/q3_cases.png`)
Chuỗi = 4 dòng quý trước đều TTM YoY ≥ 20%. **E1** = dòng kế có TTM YoY < 10% (477 sự kiện / 315 mã / 13 năm; 2022-23 = 137);
**E2** = TTM YoY giảm ≥ 20 điểm trong chuỗi (1.198 / 381). Lợi suất từ phiên SAU ngày dữ liệu, trừ trung vị đối chứng cùng tháng +
ICB cấp 1 + tercile thanh khoản, không có sự kiện ±6 tháng. CI bootstrap khối năm.

| E1 | n | TB | trung vị | CI 95% | IS / OOS |
|---|---|---|---|---|---|
| vượt đối chứng −63..0 phiên | 469 | −2,1% | −3,4% | [−4,4; +0,8] | −1,4 / −2,4% |
| vượt đối chứng 0..126 | 449 | +3,2% | −0,4% | [+0,1; +6,4] | +3,8 / +2,8% |
| vượt đối chứng 0..252 | 433 | **+6,3%** | +1,0% | [+2,6; +9,8] | +8,3 / +4,9% |
| Δlog P/E 12T | 326 | +0,095 | +0,043 | [−0,19; +0,32] | −0,10 / +0,23 |

E2 cùng hình: vượt 12T +5,7% [+1,8; +10,5], P/E 12T +0,18. Theo P/E tự thân lúc sự kiện (E2): **rẻ < 33**: trước sự kiện đã
thua −3,3% [−5,3; −1,0], 12T sau +7,6%, P/E nở +0,47 (E giảm, giá đứng); **đắt > 67**: P/E co **−0,24 [−0,42; −0,09]**, giá
vượt +6,3% [−1,4; +13,3]. Tức "de-rate" ở đây là bội số co lại vì giá KHÔNG theo lợi nhuận lên (hoặc lợi nhuận tiếp tục tăng),
không phải giá sập so với đồng loại sau khi BCTC chậm lại công bố.

**Dấu hiệu sớm** (2.016 dòng chuỗi, tỷ lệ cơ sở E1 kế tiếp 24,2%):

| Dấu hiệu ở dòng trước | % bật | P(E1 \| bật / tắt) | AUC (IS / OOS) | lợi suất 12T bật / tắt (thô) |
|---|---|---|---|---|
| ROE TTM < đỉnh 4 quý | 50% | 0,385 / 0,097 | **0,70** (0,67 / 0,72) | 6,6% / 12,6% |
| accS < 0 (2 quý gần chậm hơn TTM) | 71% | 0,314 / 0,071 | 0,64 (0,62 / 0,65) | 7,5% / 14,5% |
| Biên LN TTM < đỉnh 4 quý | 63% | 0,309 / 0,126 | 0,62 (0,58 / 0,66) | 8,1% / 12,1% |
| g1 giảm so quý trước | 64% | 0,281 / 0,172 | 0,57 | 6,8% / 14,5% |
| acc < 0 (so 4 quý trước) | 41% | 0,260 / 0,230 | 0,52 | 6,5% / 11,6% |
| P/E tự thân > 80 | 11% | 0,203 / 0,247 | **0,49** | 5,7% / 10,4% |

Dấu hiệu dự báo được SỰ KIỆN là cơ học (ROE/biên/2 quý gần là cùng chuỗi lợi nhuận). Về LỢI SUẤT vượt TB cắt ngang 12T trong
6.235 dòng tháng chuỗi ≥ 4: ROE dưới đỉnh −0,5% [−5,9; +5,3] vs không +3,9% [+1,2; +6,5]; accS < 0 +0,1% vs +5,5% — chênh 4-5 điểm
nhưng CI chồng nhau; P/E tự thân > 67 (+1,2%) vs không (+1,7%): **không khác**. P/E cao so với chính mình KHÔNG phải dấu hiệu sớm.

**Case** (`out/q3_cases_quarterly.csv`, hình `out/q3_cases.png`; giá điều chỉnh, P/E BQ):
- **VCS**: chuỗi 2015Q1-2018Q1 (TTM +47…+273%), P/E 4,7 → 15,7, giá ×16 (4.030 → 66.100). 2018Q2 TTM +11% (E1, công bố 01/08/2018):
  giá đã −23% từ 04/2018 (VNINDEX cũng −25% 04-07/2018), tiếp −25% tới 01/2019, P/E 15,7 → 8,7. Hình mẫu đúng câu chuyện user.
  Lần 2: 2022Q2-2023 TTM 0 → −51%, giá −59% từ 89.180 (10/2021, lúc TTM +31%).
- **DGC**: đỉnh giá 04/2022 (79.850, TTM +244%), P/E 20,5 (10/2021) → 4,1 (01/2023) **khi lợi nhuận VẪN tăng** tới 2022Q3 —
  thị trường co bội số TRƯỚC đỉnh chu kỳ hàng hoá. Từ E1 2023Q2 (TTM −17%) giá lại +60% (55.450 → 88.470) dù LN giảm tiếp; rồi
  2025-26 LN đi ngang/giảm, P/E 14 → 6,7, giá −62%.
- **MWG**: chuỗi 2015-2019, P/E 9,9 → 19,5 (2017) → 13-15; re-rate 2021-22 lên 21,9 với tăng trưởng chỉ 5-25%; đỉnh giá 05/2022
  (69.860, TTM +21%) khi 2 quý gần đã về +1% (2022Q2) ⇒ giá −49% tới 10/2023 cùng lúc LN TTM −86% (−96% ở 2023Q4). 2025-26 LN +88…+104%/năm mà P/E
  ~20-22 → 10,0 (giá chỉ +30%, 04/2025 → 10/2026).
- **FPT**: tăng trưởng đều 14-23% 2020-2025, P/E 10 → **28,7** (01/2025); 2025-26 tăng trưởng chỉ chậm 22% → 15% mà P/E → **9,7**,
  giá −55% (117.380 → 52.700). Bội số co mạnh nhất trong 5 case với mức chậm lại nhỏ nhất ⇒ không giải thích được bằng tăng
  trưởng riêng (nghi dòng vốn ngoại/ngành — chưa kiểm).
- **VNM** (đối chứng, không tăng trưởng): TTM +20-34% 2015-16 → P/E 17 → 29 (02/2018, khi tăng trưởng đã về +10%); rồi LN dao động
  −21…+28% suốt 2018-2026, P/E 29 → 11,6, giá ×0,64 (95.390 → 60.900).
Mẫu chung của case: bội số **nở trong chuỗi** (trừ DGC — hàng hoá), **đỉnh giá trùng hoặc ĐI TRƯỚC** quý chậm lại, và de-rate
lớn khi P/E đã nở. Trung bình toàn universe không có hình đó ⇒ case là nhóm chất lượng/vốn hoá lớn, đúng như §1 (t ≈ 1,2).

## 4. Q4 — 3×3 tăng trưởng × P/E tự thân (`q4_q6.py`, `out/q4_grid.csv`, `out/q4_fm.csv`)
37.416 dòng tháng / 606 mã. Nhóm tăng trưởng = tercile cắt ngang của `acc`; định giá = P/E tự thân 60T < 33 / 33-67 / > 67.

| Lợi suất vượt 12T (TB tháng) | rẻ | trung | đắt |
|---|---|---|---|
| gia tốc dương | +1,3% | −0,6% | +1,6% |
| ổn định | +0,4% | −1,9% | −1,2% |
| gia tốc âm | −1,7% | −2,2% | −2,7% [−7,0; +0,6] |

Không ô nào loại 0 ở 12T; ở 3T/6T "gia tốc âm × đắt" loại 0 ở CI 95% (−1,2% [−2,1; −0,3] / −1,75% [−3,5; −0,3]) và
"gia tốc âm × trung" ở 6T (−2,0% [−3,8; −0,2]) nhưng **không ô nào qua Bonferroni 27**. Fama-MacBeth 12T: tương tác pe_own × acc IS −0,009 (t −0,8) / OOS +0,030 (t 2,6) — **đổi dấu** ⇒ không đạt.
P/E tự thân +0,050 (t 2,1; IS 1,6 / OOS 1,3) — "rẻ so với chính nó" KHÔNG thắng khi đã có EP cắt ngang (+0,098, t 3,0; OOS t 3,4)
và SUE (+0,035, t 3,0). ⇒ Lưới là **mô tả** (giống breadth-tercile), không suy tín hiệu.

## 5. Q5 — Value Radar vs DCF S0 (`q5_radar.py`, `implied_and_selfcheck.py`; `out/run_q5.txt`)
Value Radar 30/10/2026: **14,4 RẺ** · P/E thị trường 10,68 (phân vị 3, cửa sổ 10 năm, trọng số vốn hoá cap 10%) · P/B p12.

| Thước đo (universe phi tài chính 279 mã) | Hôm nay | Phân vị lịch sử tháng 2014-01 → 2026-10 |
|---|---|---|
| P/E trung vị cắt ngang (mã thường, không trọng số) | 9,78 | **34** |
| P/E tự thân trung vị (mỗi mã so 60T của chính nó) | **18,3** (51% mã < p20, 67% < p33) | **1** (thấp nhất) |
| Trung vị P/FV DCF S0 (147 mã có FCFE > 0) | 0,905 | 26 |
| %RẺ S0 | **53,1%** | **71** (lịch sử trung vị 48,4%) |

**Vì sao lệch (đo, không chỉnh):**
1. **Cùng hướng, khác độ.** S0 được hiệu chuẩn để trung vị lịch sử P/FV ≈ 1 ⇒ %RẺ "bình thường" ~48%; 53,1% là phân vị 71 —
   DCF cũng nói "rẻ hơn thường lệ", chỉ không cực đoan như P/E tự thân.
2. **P/E thấp vì LỢI NHUẬN tăng, giá đứng** (76 mã có số 24T): Δlog LN TTM 24T trung vị **+0,351** (≈ +42%), Δlog giá **−0,020**
   ⇒ P/E −0,42 log. Đây chính là β thấp ở §1 — và lịch sử nói tăng trưởng vừa qua đảo chiều, nên P/E tự thân thấp sau một đợt
   tăng LN không tự động là "rẻ".
3. **Base DCF chậm hơn**: base FCFE-3Y chỉ +0,157 log trong 24T (bình quân 3 năm + tái đầu tư) ⇒ DCF thấy ít "rẻ" hơn P/E TTM.
   Tỷ lệ base/LN TTM trung vị 0,65 hôm nay (0,57-0,92 theo năm). S0 cố ý không ngoại suy cú tăng LN — đúng thiết kế.
4. **Khác mẫu**: DCF chỉ tính được 147/279 mã (FCFE 3Y > 0); trong 135 mã có cả hai: 104 rẻ theo P/E tự thân, trong đó 55 rẻ theo
   DCF / 49 đắt theo DCF.
5. **Khác trọng số**: Radar là P/E vốn hoá (mã lớn rẻ so 10 năm — p3); trung vị mã thường chỉ p34.
6. **Lag BCTC**: 30/10 mới 43,4% universe có 2026Q3; nhóm đã có Q3 P/E tự thân 14,0 vs 21,7 nhóm còn Q2 ⇒ khi Q3 nạp đủ, P/E tự
   thân có thể còn thấp nữa nếu LN Q3 tăng (giả định, chưa đo).
Tăng trưởng ngầm định 2 năm (giải ngược từ giá, base FCFE): trung vị hôm nay **−2,4%/năm** (phân vị 23 lịch sử; trung vị lịch sử
+5,2%) — nhưng đó chỉ là FCFE yield viết lại (Spearman với MoS S0 = −1,000), và trong lịch sử nó **không tương quan** với tăng
trưởng NP thực 2 năm sau (Spearman 0,003).

## 6. Q6 — trực giao với LAG / yield (`q4_q6.py`, `out/q6_orth.csv`)
Hồi quy hạng cắt ngang lên {EP, FCFE yield (S0), SUE kiểu LAG, NP_R, mom 12-1}, IC phần dư:

| Biến | IC3 thô → dư [CI] | IC12 thô → dư [CI] | dư OOS 3 / 12 |
|---|---|---|---|
| MoS CUR | 0,027 → −0,008 | 0,069 → −0,006 | −0,005 / +0,002 |
| MoS L1_gQ2 | 0,041 → 0,026 [0,003; 0,051] | 0,073 → 0,009 [−0,008; 0,027] | 0,016 / 0,004 |
| MoS L2_gQ2 | 0,051 → 0,028 [0,005; 0,055] | 0,069 → 0,007 [−0,016; 0,029] | 0,014 / 0,002 |
| MoS L2_g1 | 0,034 → −0,002 | 0,066 → 0,001 | −0,014 / −0,009 |
| P/E tự thân | −0,012 → 0,008 | −0,005 → 0,031 [−0,010; 0,076] | 0,006 / 0,028 |
| accS (hậu nghiệm) | 0,071 → **0,057 [0,036; 0,079]** | 0,047 → **0,047 [0,023; 0,072]** | 0,047 / 0,044 |

Control tự nó: SUE IC3 0,061 [0,031; 0,093], NP_R IC3 0,048; EP IC12 0,065; S0 IC12 0,069; mom 12-1 IC12 OOS **−0,104** (đảo chiều).
⇒ **Phần "tăng trưởng gần" của DCF nhẹ phần lớn là thứ LAG (SUE/NP_R) + yield đã có**; phần dư 12T ≈ 0. Nói thẳng: lăng kính này
không thêm gì cho xếp hạng.

## 7. Những gì KHÔNG chứng minh được
- Ngoại suy bội số ở nhóm chất lượng/vốn hoá lớn: hướng đúng như case, t ≈ 1,2 — chưa đủ; 5 case tự chọn (bias chọn mẫu).
- β thấp = thị trường đúng (biết LN đảo chiều) hay nhiễu đo lường E (phần tạm thời trong LN quý)? Hai cách đọc cho cùng số.
- Không tách được vai trò thị trường chung trong case (VCS 2018 trùng VNINDEX −25%; MWG/VCS 2022 trùng sập 2022; FPT 2025-26).
  Đối chứng cùng tháng xử lý trung bình, không xử lý từng case.
- De-rate KHÔNG dự đoán được bằng P/E tự thân cao (AUC 0,49); dấu hiệu ROE/biên/2 quý gần dự báo được SỰ KIỆN nhưng là cơ học,
  và chênh lợi suất của chúng có CI chồng nhau.
- Không đo trên P/FCFE tự thân cho Q4 (P/CF tự thân chỉ 176 mã hôm nay — dùng làm mô tả Q5).

## 8. Tự tấn công (cho quant-skeptic)
1. **Q1a cơ học**: log(P/E) lên tăng trưởng E bị nhiễu mẫu số; PREREG không lường trước ⇒ phép thử chính (b) là HẬU NGHIỆM. Đã
   khai, cộng N. Kết luận "không ngoại suy" dựa vào (b)+(c), không dựa vào dấu của (a).
2. **Tăng trưởng đối xứng** sg ∈ [−2,2] gộp mã hồi phục từ lỗ vào top; (b) chỉ dùng TTM dương 2 đầu ⇒ loại mã lỗ (survivorship
   nhẹ). Ở Q3 dùng tỷ số thường với TTM trước > 0.
3. **PE dính OShares TRAP** (EPS = NP_TTM/OShares, OShares restate) — lệch mức theo mã; P/E tự thân so cùng mã nên phần lớn triệt,
   nhưng bước nhảy OShares trong cửa sổ 60T làm méo phân vị. Chưa đo riêng (bài trước: 37% ticker-date OShares đổi > 10%).
4. **P/E tự thân cần ≥ 24 tháng** ⇒ loại mã mới niêm yết; 2014 dùng PE 2008-2012 kéo BQ trong phiên (`data/pe_2008_2012.csv.gz`).
5. **Lợi suất chồng kỳ** (3/6/12T theo tháng): CI bootstrap khối NĂM, t Newey-West lag h−1. N độc lập ≈ 13 năm (11 cho DSR IC12).
6. **Đối chứng sự kiện thô** (ICB cấp 1 + tercile thanh khoản, nới về chỉ tercile khi < 5 mã). Không khớp theo momentum ⇒ +6% vượt
   sau E1 có thể là đảo chiều ngắn hạn (mom 12-1 OOS âm) chứ không phải "thị trường phản ứng thiếu".
7. **Ngày sự kiện = ngày vendor ghi** (bài trước: 2014-19 mode 32 ngày = ngày chụp) ⇒ phần phản ứng trước sự kiện (−2,1%) có
   thể là phản ứng với BCTC thật đã công bố sớm hơn.
8. **N trials** ≈ 160: Q1 47 + Q1b 7 (hậu nghiệm) + Q2 30 + Q3 10 + Q3b 12 (hậu nghiệm) + Q4 28 + Q6 27. accS là kết quả hậu
   nghiệm nổi bật nhất — chính vì vậy phải kiểm riêng, không dùng từ đây.
9. **Universe_pit** (thanh khoản) — kết luận không áp cho đuôi kém thanh khoản.
10. **Quality_large** định nghĩa sau khi xem case (hậu nghiệm) — dễ bị "vẽ bia quanh mũi tên".

## 9. Đề xuất
- **Không xây DCF nhẹ, không knob, không code.** Giữ S0 cho giá trị nội tại (đề xuất bài trước, vẫn chờ user/skeptic).
- Muốn "đọc kỳ vọng thị trường" trong báo cáo DD/plan: đủ dùng 2 số có sẵn, ghi rõ display-only — P/E so lịch sử chính mã
  (P/E tự thân) và FCFE yield/“g ngầm định” (cùng một thông tin) — kèm câu: "tăng trưởng vừa qua ở VN đảo chiều trong < 1 năm;
  P/E thấp sau một đợt tăng LN không tự động là rẻ".
- Ứng viên R&D riêng (cần PREREG, so với `d_NPR` của LAG): `accS` (gia tốc 2 quý vs TTM).
- Với mã chất lượng lớn đang có P/E nở sau chuỗi dài (kiểu FPT 01/2025, VNM 2018): rủi ro de-rate là THẬT trong case nhưng chưa
  đo được thành quy luật — nếu muốn, thiết kế lại mẫu riêng nhóm này (≈ 14% dòng) với PREREG mới.

## Tái lập
`$DNA_PYEXE build.py` → `q1_extrap.py` → `q1b_elasticity.py` → `q2_light.py` → `q3_derate.py` → `q3b_subgroups.py` → `q4_q6.py` →
`q5_radar.py` → `implied_and_selfcheck.py` (selfcheck, rc 0). Đầu vào: `data/bq_cache/*` vintage 30/10/2026, data bài trước
(`../dcf_vn_calibration_20261101/data/`), `data/pe_2008_2012.csv.gz` (BQ 02/11, phiên cuối tháng 2008-2012).
