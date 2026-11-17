# PAT — Định giá r4 (vòng đính chính sau 2 skeptic mù giá), mù giá thị trường, 17/11/2026

## KẾT LUẬN ĐẦU
- **Tâm r4 = 66.300 đ/cp** (cây 3.024 lá: 66.318; đường cơ sở với đầu vào kỳ vọng: 66.301; đường độc lập: 66.320).
- **Khoảng:** P25–P75 = **47.100 – 81.700** · P10–P90 = **37.400 – 98.600** · trung vị 67.600.
- **Bắc cầu r3 → r4** (r3 = 66.864; khung r4 chạy với tham số r3 ra 66.864,5, lệch 0,00000%). Các bước cộng dồn, đơn vị đ/cp:

| Bước | Giá trị | Đóng góp | Gỡ riêng khỏi r4 |
|---|---|---|---|
| r3 | 66.864 | | |
| (1) Cước/DT XK 3,85% (FY25) → **4,686%** (9T/26, ảnh p29 + p31). Sửa lỗi hiệu chỉnh lệch kỳ gốc | 65.489 | **−1.375** | −1.373 |
| (2) Nút P theo **một** quy tắc độ co giãn ε = 0,250 cho cả 3 nhánh ⇒ {0,9384; 0,9961; 1,0670} | 64.781 | **−709** | −709 |
| (3) Tồn kho dư 44,44 tỷ, giải phóng khi cung quặng bình thường hoá (cùng khung nút O) | 66.318 | **+1.538** | +1.538 |
| **Tổng r3 → r4** | | **−546 (−0,8%)** | |

- **Phán quyết các mục tranh chấp lớn** (bảng đầy đủ ở `assumptions_objective_r4.md` §1):
  - Cước: ĐỒNG Ý, đã sửa.
  - Nhánh giữa nút P: ĐỒNG Ý về nguyên tắc, MỘT PHẦN về mức. Mức đúng là 0,996, không phải 0,990.
  - Nút O: MỘT PHẦN. Độ nhạy q_B của r3 cài sai, đã sửa. Giữ hazard hằng cho B (không có cơ chế mất vĩnh viễn).
  - Nút T: BÁC. P(A) = 0,5: BÁC. Nút D: BÁC. Cốc dài hạn: BÁC.
  - Sản lượng sau Q1/2027: MỘT PHẦN, chỉ đưa vào độ nhạy hai chiều.
  - Khối O3 vĩnh viễn (lạc quan): BÁC, chỉ ghi khoảng.
  - Tồn kho dư: MỘT PHẦN, đã sửa.
  - Điện tính trên 100% DV: BÁC.
- **Điểm kém chắc nhất (theo thứ tự):**
  1. **Giá DLC trả PAT.** Nút T cho dải 58.900 (T_a) → 88.100 (T_c). Nếu DLC trả thấp hơn netback 5% thì còn 50.300. Nguyên tắc giá vẫn không tìm được.
  2. **Mức giá thực hiện.** ±5% giá ⇒ ±24.700/cp, vì biên EBIT dài hạn chỉ ≈ 10,4%.
  3. **Khung nút quặng.** Chọn khung khác dịch tâm trong dải 61.100 – 71.100 (§2).
  4. **Cốc dài hạn.** Nếu cốc giữ 2.100–2.108 thay vì hồi về 1.825 ⇒ −6.000 đến −6.200.
- **Độ tin cậy: thấp–trung bình.** Tâm vững với các sửa lỗi có bằng chứng (dịch < 1%), nhưng khoảng rộng. Tâm bi quan 57.500 chỉ đạt được khi xếp chồng ba phán đoán không có bằng chứng độc lập, cộng sản lượng một chiều (xếp chồng trong mô hình r4 ra 57.200). Tâm lạc quan 69.200 cũng cần các phán đoán tương tự (xếp chồng lạc quan ra 71.700).

## 1. Từng mục skeptic: tự kiểm và kết quả
- **Cước (C3/E3 bi quan) — ĐỒNG Ý.**
  - Tôi tự xem ảnh `png_q326/p29` (TM25: vận chuyển 9T/26 = 22.843.840.946 đ) và `p31` (TM29: DT nước ngoài 487.507.728.152 đ) ⇒ 4,686%.
  - Số 3,85% (FY25) đúng về số học, nhưng lệch kỳ: mọi tỷ lệ chi phí khác của mô hình hiệu chỉnh theo 9T/26. Vì thế khung r3 tái tạo 9T/26 quy năm cao hơn số thực (r3: 283 so với thực 274).
  - Sau khi sửa: 278,3 tại E[s_exp]; 276,2 tại s_exp 9T so với thực 274,1. Phần còn lệch 2,1 là DT hàng hoá và làm tròn.
  - Độ nhạy: 3,85% ⇒ 67.700; gộp 21 tháng 4,03% ⇒ 67.400. Q3/26 riêng là 7,85%, nghĩa là có phần cố định, nên 4,686% không phải cận trên.
- **Nút P (C2/E2 bi quan) — ĐỒNG Ý về nguyên tắc, MỘT PHẦN về mức.**
  - Lỗi: r3 dùng hai quy tắc ánh xạ cho cùng một biến (đuôi theo co giãn ≈ 0,25, nhánh giữa theo "độ dính" = 1,0).
  - Quy tắc r4 (`pnode_r4.py`): p = 1 + ε·(E[S|nhánh]/27.740 − 1), với một ε chung, hiệu chỉnh để hai đuôi khớp biên độ ±6,3% của r3.
  - Phân phối S khớp đủ 5 điểm của F2, gồm cả P(<28.466) = 0,66 mà lognormal 2 tham số của skeptic bỏ qua. Lognormal đó còn cho xác suất nhánh 0,31/0,62/0,07, lệch khỏi F2.
  - Kết quả: ε = 0,250; nhánh giữa 0,9961 (skeptic: 0,990).
  - Độ nhạy: lognormal của skeptic ⇒ 64.100; cùng quy tắc với mốc 31.500 ⇒ 65.400; r3 (giữa = 1,0) ⇒ 67.000.
- **Nút O (C1/E1 bi quan) — MỘT PHẦN.**
  - (a) ĐÚNG: độ nhạy "q_B 0,25 ⇒ 64.000" của r3 giữ λ cũ nên không còn khớp F7. Bản sửa (λ' 0,0786, khớp F7) ⇒ 63.700 trên nền r4.
  - (b) BÁC: lập luận "F7 ≠ biến cố PAT cần". Mức O2 được đo ở H1/2026, khi mỏ DGC đã dừng, VAPC còn chạy và DGC mua của VAPC. Vì vậy "B giải ⇒ O2" là quay lại đúng chế độ đã quan sát. Câu "VAPC khó đáp ứng đủ đến 2030" được nói 19/03/2026, ngay trong chế độ đó, nên đã nằm sẵn trong O2.
  - (c) BÁC: đưa q_B vào base (lý do ở §2).
  - (d) ĐỒNG Ý: nhãn VALUATION_r3 dòng 17 sai. +4.871 chỉ là bước (3b); (3a)+(3b) = +4.317.
- **Nút T (C4 bi quan) — BÁC.**
  - Proxy DT/DV phẳng trong khi benchmark +22% khớp cả "DLC trả dưới thị trường" lẫn "giá cost-plus/hợp đồng dài hạn". Kịch bản sau lại ủng hộ T_b/T_c.
  - DGC Q2/26 cũng chỉ hưởng khoảng nửa mức tăng benchmark (A3 §3.2 dòng 113) ⇒ độ trễ giá không riêng kênh DLC.
  - Giữ 0,65/0,25/0,10. Độ nhạy: 0,80/0,15/0,05 ⇒ 63.100; 0,55/0,35/0,10 ⇒ 68.100.
- **P(A) = 0,5 (C4 bi quan) — BÁC.**
  - Không có sự kiện nào sau r2 làm đổi xác suất.
  - A gồm cả KT19B (khai thác từ 2023, không có tin hết hạn giấy phép).
  - Độ nhạy: 0,30 ⇒ 63.500; 0,35 ⇒ 64.200; 0,70 ⇒ 69.200.
- **Sản lượng sau Q1/2027 (C5 bi quan) — MỘT PHẦN.**
  - Rủi ro là thật: Ai Cập chỉ tới hết Q1/27, UBND ghi nhận PAT thiếu NVL, proxy DV Q3/26 = 0,927 × nền.
  - Nhưng nền 9T/26 đã chứa sẵn quý thiếu đó; H1/26 (B còn chạy) = 1,037 × nền. Cắt một chiều là không nhất quán.
  - Độ nhạy theo trạng thái cung: một chiều (0,927/1,0) ⇒ 65.800; hai chiều (0,927/1,037) ⇒ 68.700; r3 −15%/−30% H2/27 ⇒ 65.700/65.100. Base giữ 1,0, vì proxy DV là giả định.
- **Nút D (E7 bi quan) — BÁC.** Số ">80% tự cấp" là của CTCK. Ô (A tắt, B bật) quan sát ở H1/26 nghiêng ngược chiều. Độ nhạy D(A) 0,7 ⇒ 64.600.
- **Cốc 2028+ (E8 bi quan) — BÁC (giữ 1.825 = TB 2023Q1–Q3/2026).**
  - Cửa sổ 2020+ ⇒ 2.100 ⇒ 60.300. Giữ 2.108 mãi ⇒ 60.100.
  - EBIT tuyến tính riêng theo p và theo cốc, nên tương quan cốc–P không đổi tâm, chỉ đổi phân vị.
- **Khối O3 vĩnh viễn (E1 lạc quan) — BÁC đưa vào base.**
  - Ô (A tắt, B bật) trong r3 đã là 50/50 O2/O3. Đề xuất của skeptic dời lên 75/25 dựa trên kênh thứ ba mà bằng chứng chỉ ở mức báo chí chưa kiểm chứng.
  - Độ nhạy: 75/25 ⇒ 68.700; ô → O2 hẳn ⇒ 71.100.
- **Tồn kho dư (E2 lạc quan) — MỘT PHẦN, đã sửa.**
  - Số liệu: 120,19 so với TB 3 mốc trước 75,75 ⇒ 44,44 (F2 §1.5). Skeptic bi quan cũng thừa nhận chiều này.
  - Giải phóng tại max(7,5 tháng; min(τ_B; τ_A)), cùng xô của cây ⇒ E[PV] = 38,4 tỷ.
  - Skeptic lạc quan dùng 0,55 "rồi không bao giờ", mâu thuẫn với π_B = 1. Các khoản phải thu/phải trả DLC dao động 0–313 do bù trừ theo kỳ, không có mức chuẩn ⇒ không chuẩn hoá.
- **Điện 100% DV (E3 lạc quan) — BÁC.** Kiểm từ dưới lên cho φ ≈ 0,76–1,06. φ 0,91 ⇒ +98; φ 0,6 ⇒ +434.
- **Phương pháp (E4, E5 lạc quan) — ĐỒNG Ý.**
  - Đối chiếu chu kỳ viết lại theo **biên EBIT/DT sau thuế XK, cùng quy ước E[s]**: r4 2028 = 9,4%, dài hạn 10,4%. Bảng của skeptic lạc quan cùng quy ước: 2023 8,3%, 2024 7,1%, 2025 10,8% (năm tốt nhất).
  - ⇒ r4 dài hạn nằm giữa 2023–24 và năm tốt nhất, không vượt năm tốt nhất.
  - Giả định "giá thực hiện/đơn vị 2025 ≈ 9T/26" (DT/DV 3,83 so với 3,70) nay ghi tường minh.

## 2. Khung nút quặng: chọn một khung, chênh bao nhiêu nếu chọn khung khác
- **Khung chọn: "nguồn × cơ chế"** (hỗn hợp chữa khỏi theo từng nguồn).
  - Mỗi nguồn có π = P(từng khôi phục) và một phân bố thời điểm có điều kiện.
  - π < 1 chỉ khi bằng chứng nêu được một cơ chế mất quyền. A có cơ chế đó (giấy phép KT25 hết hạn trong lúc có bị can theo điều 227 tại chính khai trường) ⇒ π_A = 0,5. B không có cơ chế nào được nêu: nguyên nhân hành chính, đã chạy lại một phần trong 3,5 tháng, có cấp phép Mỏ Cóc 1 ⇒ π_B = 1.
  - Thời điểm: A theo cửa sổ pháp lý H2/2027; B là phân bố mũ hiệu chỉnh đúng một điểm F7.
  - Ánh xạ chi phí theo ô trạng thái nguồn: ô đã quan sát sạch dùng mức đo được; ô quan sát bị nhiễu hoặc chưa quan sát dùng 50/50 bất khả tri (D).
  - Khung này giải mâu thuẫn r2 và áp **cùng một luật** cho cả A, B và ô chi phí. Base nút O không đổi so với r3.
- **Vì sao không chọn khối vĩnh viễn q_B:** với một điểm F7, mọi cặp (q, λ') thoả (1 − q)(1 − e^(−6,5λ')) = 0,30 đều khớp. Dữ liệu không xác định được q, nên chọn q > 0 là đặt một con số không có bằng chứng về cơ chế.
- **Chênh nếu chọn khung khác** (trên nền r4, không trung bình hoá vào tâm):

| Khung | Tâm | Chênh |
|---|---|---|
| Cure q_B 0,25, λ' khớp F7 | 63.700 | −2.700 |
| Cure q_B 0,40, λ' khớp F7 | 61.900 | −4.400 |
| Kiểu r2: cắt 2028 rồi vĩnh viễn | 61.100 | −5.200 |
| Ô (A tắt, B bật) 75/25 (lạc quan) | 68.700 | +2.400 |
| Ô (A tắt, B bật) → O2 hẳn | 71.100 | +4.800 |

## 3. Phân phối theo nút (cây r4)
| Nút | Nhánh: xác suất → giá trị có điều kiện (đ/cp) |
|---|---|
| T | T_a 0,65 → 58.900 · T_b 0,25 → 76.900 · T_c 0,10 → 88.100 |
| P | 0,9384: 0,32 → 43.100 · 0,9961: 0,58 → 72.000 · 1,067: 0,10 → 107.600 |
| TX | 15%: 0,97 → 65.700 · 10%: 0,03 → 87.100 |
| A | giải: 0,5 → 73.500 · không: 0,5 → 59.200 |
| D | A: 0,5 → 62.000 · B: 0,5 → 70.700 |
| Thời điểm B | trước giữa 2027 0,337 → 67.700 · H2/27 0,186 → 67.300 · 2028 0,230 → 66.300 · 2029–30 0,181 → 64.500 · 2031+ 0,066 → 61.700 |

Cơ sở: EBIT 2027 = 101,7 · EBIT 2028 = 162,3 · EBIT 2045 (giá 2028) = 178,6 · tiền ròng 357,4 · E[PV tồn kho] 38,4 · PV dòng 2027–2045 = 1.104,1 · PV terminal 157,6 (9,5%).

Cầu EBIT 2027 (`ebit_2026_2027_r4.py`):

| Bước | EBIT | Thay đổi |
|---|---|---|
| 9T/26 quy năm, khung r4 | 278,3 | |
| Thuế 10→15% | | −72,5 |
| Cốc 9T → 2.108 | | −34,7 |
| Quặng | | −39,3 |
| Điện | | −3,7 |
| Giá E[p] | | −26,3 |
| **E[EBIT 2027]** | **101,7** | |

## 4. Độ nhạy (đường cơ sở 66.301 trừ khi ghi "cây"; đầy đủ ở `calc_r4/bridge_sens_r4_out.json`)
| Trục | Giá trị (đ/cp) |
|---|---|
| r 12,5 / 13 / 13,5 / 14 / 14,5% (g 2%) | 70.800 / 68.400 / 66.300 / 64.300 / 62.500 |
| g 0 / 1 / 2 / 3% | 59.800 / 62.800 / 66.300 / 70.400 |
| EBIT dài hạn ×0,8 / 0,9 / 1,1 / 1,2 | 57.300 / 61.800 / 70.800 / 75.300 |
| giá ×0,90 / 0,95 / 1,05 / 1,10 | 17.000 / 41.600 / 91.000 / 115.600 |
| s_eff 0,135 / 0,35 / 0,75 / 0,785 / 1,0; DLC dưới netback −5% | 82.700 / 76.600 / 65.200 / 64.200 / 58.000; 50.300 |
| thuế giữ 10% chắc / TX 0,90 (cây) | 86.600 / 67.800 |
| cước 3,85% / 4,03% (cây) | 67.700 / 67.400 |
| P: r3 / mốc 31.500 / lognormal skeptic / biên độ ±10% (cây) | 67.000 / 65.400 / 64.100 / 61.800 |
| O: xem §2; D(A) 0,7; P(A) 0,30/0,35/0,70; A muộn 01/2029 (cây) | 64.600; 63.500/64.200/69.200; 65.400 |
| O cố định: chưa giải mãi / O2 từ H2/27 / O1 từ 2028 | 49.700 / 70.900 / 79.400 |
| T 0,80/0,15/0,05 · 0,55/0,35/0,10 (cây) | 63.100 · 68.100 |
| điện 0,98 / bỏ F5 / φ 0,91 / φ 0,6 | 67.000 / 69.400 / 66.400 / 66.800 |
| cốc dài hạn 2.100 / 2.108 (cây) | 60.300 / 60.100 |
| sản lượng theo cung một chiều / hai chiều (cây); H2/27 −15% / −30% | 65.800 / 68.700; 65.700 / 65.100 |
| bỏ tồn kho (= r3 về điểm này) | 64.800 |
| một lần −50 / mất cầm cố −42,6 / 70 tỷ theo mệnh giá | 64.300 / 64.600 / 68.100 |
| **Xếp chồng bi quan** (q_B 0,25 khớp F7 + P(A) 0,35 + T 0,80/0,15/0,05 + sản lượng một chiều) | **57.200** |
| **Xếp chồng lạc quan** (ô 75/25 + φ 0,6 + sản lượng hai chiều) | **71.700** |

## 5. Mốc xác minh
1. **BCTC Q4/2026** (cuối 01/2027):
   - Cước/DT nước ngoài ≈ 4,7% ⇒ xác nhận sửa (1).
   - Tồn kho 31/12/26 về ~75 ⇒ xác nhận (3) sớm. Tăng thêm ⇒ dự trữ an toàn kéo dài, (3) muộn hơn.
   - GPM, tỷ trọng bán DLC.
2. **Thuế XK P4 hiệu lực 01/01/2027** (TX). **Tỷ lệ thuế XNK/DT nước ngoài Q1/2027** ≈ 15% ⇒ khớp không hưởng ưu đãi.
3. **Quặng:**
   - Quyết định về giấy phép KT25 / cho chạy lại KT19B (~31/12/2026 – đầu 2027) ⇒ nút A.
   - **F7 ngày 31/05/2027** ⇒ chấm hazard B và phân biệt khung π_B = 1 với khung có khối vĩnh viễn.
   - Hợp đồng quặng sau Q1/2027 ⇒ rủi ro sản lượng.
   - Khối lượng Tam Đỉnh / Cam Đường bán cho DLC/PAT ⇒ cơ sở duy nhất để dời ô (A tắt, B bật).
4. **Nguyên tắc giá DLC ↔ PAT** (tờ trình GD bên liên quan ĐHĐCĐ 2027) ⇒ nút T. Đây là biến lớn nhất.
5. Giá điện sau 31/03/2027 (F5). P4 SunSirs so với F2 (12/11/2027).

## 6. Phương pháp và kiểm tra
- Giả định khoá trước khi chạy: `assumptions_objective_r4.md` md5 `2521604da439d323074162f5102909ed`, khoá 2026-11-17T12:48:31Z (`lock_r4.txt`). Các số đầu vào của nút P, cước và tồn kho được tính sẵn (thuần đầu vào, không chạy mô hình định giá) trước khi khoá.
- `calc_r4/` = bản sao `calc_r3/` (không sửa các tệp r3) + `model_r4.py`, `pnode_r4.py`, `bridge_sens_r4.py`, `selfcheck_r4.py`, `ebit_2026_2027_r4.py`, và các tệp kết quả `model_out_r4.json`, `bridge_sens_r4_out.json`.
- **Kiểm hồi quy:** khung r4 chạy với tham số r3 ⇒ 66.864,45 = r3 (lệch 0,00000%).
- **Self-check** `selfcheck_r4.py`: đường độc lập, không import mô hình (dạng đóng E[NVL], EBIT tuyến tính, tồn kho tích phân liên tục theo τ_B) ⇒ 66.320,2 so với cây 66.318,4. **Lệch +0,0027% (ĐẠT, ngưỡng < 0,5%).** Chạy dưới TZ America/New_York và không đặt TZ cho kết quả giống hệt. Tổng xác suất lá = 1,0000000000.
- **Lệch so với giả định khoá:** không có lệch về giả định. Một điểm cài đặt nhỏ: bảng lưới r × g giữ E[PV tồn kho] chiết khấu ở 13,5% cho mọi r. Sai số < 0,5 tỷ (< 20 đ/cp), bỏ qua.

## WARNING (không bake vào base)
- Vụ án hình sự lãnh đạo nhóm DGC/PAT (khởi tố 03/2026, mở rộng 07/2026). Kiểm toán ngoại trừ.
- Bảo đảm chéo trong nhóm: 40 tỷ + 100.000 USD cầm cố cho "Công ty và các công ty thành viên".
- Rủi ro thiếu quặng ảnh hưởng KHỐI LƯỢNG sau Q1/2027 (độ nhạy §4).
- Thanh khoản cổ phiếu không đánh giá ở đây.
