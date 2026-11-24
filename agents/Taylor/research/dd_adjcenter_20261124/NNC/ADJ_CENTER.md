# NNC — Tâm kỳ vọng điều chỉnh (24/11/2026, job Taylor_20261124_110054, nhóm g3)

Phương pháp: `../PREREG_adj.md` (md5 `ef5157cb…`) + `../PREREG_adj_v2.md` (md5 `835dfc1e…`, ghi đè điểm xung đột). Mù giá: không đọc giá thị trường.
Tâm gốc = sổ NNC **rev6, 61.273 đ/cp** (`skeptic_final` REFUTED_OPEN — trạng thái phản biện, không phải quan điểm).
Calc: `rerun_combo.py` (chạy lại mô hình r3 với tổ hợp, CONTROL trùng byte r3 `857c7adb…`; 2 lần chạy cùng md5 `8971f24b…`) → `calc_adj.py` (run1 = run2 md5 `8f4321f3…`) → `adj.json` (md5 `6beb796c…`).

## Kết luận
**Tâm kỳ vọng điều chỉnh: 58.914 đ/cp (−3,85% so với 61.273). Dải (p, m) cực trị: 52.959–61.630.**
Không có cổ tức tiền đã công bố mà chưa GDKHQ trong nguồn (cổ tức phải trả 5,89 tỷ đã trừ ở tiền ròng) ⇒ một dòng duy nhất.

Hai hạng mục skeptic để mở (trích quỹ KTPL, capex > khấu hao) đều có dữ liệu trong tay đủ để định cận và dấu. Truy thu Núi Nhỏ thì đóng hẳn: đã phủ đủ.

## 1. Hạng mục vào tâm
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | Trích quỹ KTPL hằng năm từ LNST 2026–2043 chưa trừ | ↓ | −3,59 [−3,59; −6,40] | **C+** | 0,50 [0,25; 0,75] | −1,79 | r1_raw:11; FPTS (tồn quỹ 2023A 4 / 2024A 7); BCTC Q3/26 16,78; BQ NP_P0 |
| 2 | Capex duy trì > khấu hao | ↓ | −3,85 [0; −9,75] | B | 0,65 [0,40; 0,90] | −2,50 | r1_raw:12; FPTS:1323-1330, 2203; dd_NNC_20261026/REPORT.md:86-88 |
| 3 | LNST Q4/26 ước 60 tỷ < nhịp quý | ↑ | +0,70 [0; +2,13] | B | 0,35 [0,15; 0,55] | +0,24 | BQ NP_P0 quý; r1_raw:37 |
| 4 | Chân MVC dùng engine chưa vá trần chu kỳ | ↑ | +0,43 [0; +0,43] (ước lượng) | B | 0,50 [0,25; 0,75] | +0,22 | r1_raw:18; dd_redo_20261105/MVC/REPORT_r3.md:22 |
| 5 | Truy thu Núi Nhỏ ~42 tỷ vs dự phòng 22,37 | — | **0 (đã phủ đủ)** | A | — | 0 | REPORT_r2.md:60; REPORT_v2_20261031.md:93,202 |
| | **Σ tuyến tính** | | | | | **−3,84** | |
| | **Tổ hợp (chạy lại mô hình) + #4 tuyến tính** | | | | | **−3,85** | |

**Cơ sở từng hạng mục:**
- **#1 (C+, cận bảo thủ).** Quỹ KTPL chỉ hình thành từ trích LNST, và chi quỹ không âm, nên số trích trong kỳ ≥ mức tăng tồn quỹ. Năm 2024: (7 − 4) / LNST 2023 36,61 = **8,2%**. Từ 2025 đến 9T26: (16,78 − 7) / (LNST 2024 62,62 + 2025 147,84) = **4,6%**. Tâm lấy 4,6% (cận bảo thủ), dải m kéo tới 8,2%. Có 2 kỳ nên p lấy mặc định bậc B. m không dùng độ dốc của skeptic mà đo trực tiếp bằng mô hình: thuế hiệu dụng của riêng NNC = 1 − 0,8×(1 − KT), cộng trừ KT × LN 2026 (9T 160,08 + Q4), khoản lãi này đang nằm trong tiền ròng và sẽ được trích năm 2027. Kết quả 4,6% cho −3,59%, khớp với skeptic (5% ⇒ −3,6%).
- **#2 (B, 3 kỳ cùng hướng có số).** Capex: 23 (2022), 19 (2023), 23 (2024), 54 (2025) tỷ. Khấu hao: 7 (2023), 10 (2024), và Q3/26 là 5,56 tỷ/quý, tức 22,2 tỷ/năm. Capex vượt khấu hao cùng năm: 2023 +12, 2024 +13, 2025 ≥ +32. Khoảng hở tương lai (ước lượng): capex TB 2022–25 là 29,75 so với khấu hao hiện tại 22,2 ⇒ **7,5 tỷ/năm**. Khoảng [0; 19]: cận dưới 0 vì mỏ hữu hạn có thể giảm capex về cuối đời; cận trên 19 = TB 3 khoảng hở cùng năm.
- **#3 (B, nhánh ngược).** Tỷ lệ Q4/Q3 năm 2024 là 1,28, năm 2025 là 1,27, nhưng năm 2023 là 0,92 (quan sát ngược, có số). m: Q4 = Q3 69,29 ⇒ +9,29 tỷ; cận trên Q3 × 1,275 ⇒ +28,3 tỷ.
- **#4.** Bản vá D1 ở MVC redo r3 làm MVC tăng +556 đ/cp. Quy về NNC: × 10,3 triệu cp × 1/(1 − 0,103 × 0,4407) / 21,92 triệu cp × hệ số CK. Cận dưới 0 vì có thể NNC r3 đã vá một phần (patch `np_bottom` dùng chung).
- **#5.** 42 tỷ = dự phòng 15,58 + 5,95 (đã nằm trong 22,37 và đã trừ ở tiền ròng) + 20,43 đã nộp năm 2026 (tiền đã ra). Khoảng hở ≤ 1,5% mà skeptic nêu được đóng bằng 0.

**Vì sao chạy lại mô hình:** |Σ| = 3,84%, sát ngưỡng 5% (v2 §5), và ba hạng mục cùng đi qua dòng tiền mỏ. Mô hình tổ hợp chạy với đầu vào kỳ vọng (KT = 0,5 × 4,6%, G = 0,65 × 7,5, ΔQ4 = 0,35 × 9,29) ra 58.788. Cộng #4 tuyến tính được 58.914. Lệch so với cộng tuyến tính chỉ 0,01pp.
**Dải:** chạy mô hình ở tổ hợp cực trị (p, m). Thấp: KT = 0,75 × 8,2%, G = 0,9 × 19, Q4 = 0 ⇒ 52.959. Cao: KT = 0,25 × 4,6%, G = 0, ΔQ4 = 0,55 × 28,3, cộng #4 ở 0,75 ⇒ 61.630.

## 2. Chỉ độ nhạy — KHÔNG vào tâm
| Hạng mục | Hướng | Độ nhạy | Vì sao không vào tâm |
|---|---|---|---|
| [LUẬT] r 13,5% so với dải Ke 12,3–13,4% (E15) | ↑ | Ke 12,3% ⇒ 63.725 (+4,00%); 13,4% ⇒ +0,32% | Tham số luật V1 (v2 §4) |
| Đối thủ hết giấy phép từ 2034 | ↑ | +4.367 (+7,13%) | C: không có cơ sở độc lập |
| ADMIN perm05 | ↑ | +4.962 (+8,10%) | C |
| Trả trước dài hạn CNBP là tiền thuê | ↑ | +2.126 (+3,47%) | C: chưa xác minh hợp đồng |
| Trọng số STRUCTURAL 0,20 → 0,30 | ↑ | ≈ +4,8% | C: [UL] cả hai chiều |
| Truy thu lan sang mỏ lõi Mũi Tàu (E12) | ↓ | ngoài 0,84 đã trừ: chưa có độ lớn | C |
| Chi phục hồi môi trường / đóng mỏ 2043 ngoài 4,50 | ↓ | không trọng yếu (hệ số ≈ 0,12) | C |
| Pháp lý: MVC 44,07% + uỷ quyền 51% / D195; NHC chiếm 61% phải thu | ↓ | WARNING | Pháp lý không vào tâm |

## 3. Không đếm hai lần
- Hạng mục KTPL: tồn quỹ 16,78 (stock) đã trừ ở tiền ròng từ r3. #1 chỉ là dòng trích hằng năm (flow).
- Capex mở rộng Tam Lập (CIP 83,5 tỷ, sổ sách / NPV 0; đền bù 79,48 tỷ năm 2026) KHÔNG nằm trong #2. #2 chỉ là capex duy trì máy móc của mỏ hiện hữu.
- r, dải Ke, E15 và ±50bp là một dòng luật, không vào Σ.

## 4. BẢNG ĐIỀU KIỆN ĐỔI SỐ
Δ tính trên tâm 61.273. Các dòng độc lập cộng xấp xỉ được với nhau.

| Sự kiện / dữ kiện | Khi nào | Đổi gì | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|
| Đọc thuyết minh VCSH BCTC kiểm toán 2025 (đã công bố): số trích KTPL thực từ LN 2024 (ví dụ 8,2%) | **làm được ngay** | #1 C+→A, p 0,9 | −2.428 | −3,96 |
| NQ ĐHĐCĐ 2027 phân phối LN 2026: tỷ lệ trích KTPL 5% | ước lượng 04/2027* | #1 → A | −1.051 | −1,72 |
| NQ ĐHĐCĐ 2027: tỷ lệ trích KTPL 10% | ước lượng 04/2027* | #1 → A (ngoại suy tuyến tính) | −3.202 | −5,23 |
| LCTT năm 2026: capex − KH ≥ 7,5 tỷ (kỳ thứ 4 cùng hướng) | ước lượng cuối 01/2027* | #2 p 0,65→0,90 | −589 | −0,96 |
| LCTT năm 2026: capex ≤ KH (quan sát ngược có số) | ước lượng cuối 01/2027* | #2 p 0,65→0,35 | +707 | +1,15 |
| BCTC Q4/2026: LNST Q4 ≥ 69 tỷ | ước lượng cuối 01/2027* | #3 → A | +235 | +0,38 |
| BCTC Q4/2026: LNST Q4 ≤ 60 tỷ | ước lượng cuối 01/2027* | #3 = 0 | −150 | −0,24 |
| Vá trần chu kỳ engine MVC r6, chạy lại chân MVC trong NNC | nội bộ, khi làm | #4 → A (nếu đã vá sẵn: −0,22%) | +105 | +0,17 |
| Lãi huy động 12T hiệu dụng ±50bp (luật V1, β = 1) | liên tục | r ±50bp | −944 / +988 | −1,54 / +1,61 |
| Văn bản truy thu mới chạm Mũi Tàu / D195 MVC | khi có | Có số tiền ⇒ trừ ở tiền ròng theo số (A); chưa có số ⇒ WARNING | theo số | — |

\* Lịch công bố là ước lượng theo nhịp thông thường, chưa xác minh với lịch CBTT của NNC.

**Điều kiện đổi số lớn nhất:** tỷ lệ trích KTPL thực. Đọc được ngay trong BCTC kiểm toán 2025 (biến động VCSH). Nếu tỷ lệ là 8,2% thì tâm còn ≈ 56.500 (ước lượng tuyến tính). Nếu là 10% (qua NQ 2027) thì ≈ 55.700.

## 5. Ghi chú
- Chạy lại mô hình qua hook `N3._nnc_ex6`. Thuế hiệu dụng chỉ đổi trong lời gọi NNC, MVC không bị chạm. Thu nhập tài chính (lãi tiền gửi) chưa chịu KTPL trong hook; phần sót này nhỏ, chưa đo.
- Nguồn calc gốc bị TRIM, khôi phục ở `/tmp/ddrestore_B` (LOCK md5 assert trong `rerun_combo.py`). Không ghi đè repo.
