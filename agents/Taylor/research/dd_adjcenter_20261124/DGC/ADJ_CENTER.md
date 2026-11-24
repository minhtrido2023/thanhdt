# DGC — Tâm kỳ vọng điều chỉnh (24/11/2026, job Taylor_20261124_110054, nhóm g3)

Phương pháp: `../PREREG_adj.md` (md5 `ef5157cb…`) + `../PREREG_adj_v2.md` (md5 `835dfc1e…`). Mù giá: không đọc giá thị trường.
Tâm gốc = sổ DGC **rev3, 41.849 đ/cp** (`skeptic_final` REFUTED_OPEN — trạng thái phản biện).
Calc: `rerun_combo.py` chạy lại mô hình r3b (CONTROL 41.849, và tái lập đúng 7 biến thể của REPORT_r3b: 47.753 / 42.176 / 41.522 / 43.813 / 42.419 / 39.427 / 38.919). 2 lần chạy cùng md5 `149a7ba1…`. Tiếp theo là `calc_adj.py` (run1 = run2 md5 `ca753a7d…`), ra `adj.json` (md5 `3762e10b…`).
**Pháp lý (vụ án hình sự):** theo luật 27/09, phân tích bình thường trên BCTC, pháp lý chỉ là WARNING và KHÔNG vào tâm.

## Kết luận
**Tâm kỳ vọng điều chỉnh: 41.132 đ/cp (−1,71% so với 41.849). Dải (p, m) cực trị: 39.957–41.555.**
Cổ tức 8.000 đ/cp đã chi xong (cổ tức phải trả còn 0,06 tỷ). Không còn quyền tiền mặt nào chưa GDKHQ trong nguồn, nên chỉ có một dòng.

Hai đòn lớn nhất của skeptic không vào tâm:
- Biên vĩnh viễn của nhánh mở lại khai trường (+14,1%) là quyết định user (cách B, 08/11).
- Ngoại trừ tồn kho (−5,8%) là bậc C: dấu "xuống hoặc 0", cận bảo thủ = 0.

Tôi dựng một bảng điều kiện đổi số đủ cụ thể để hai điểm này được đóng bằng dữ kiện thay vì đoán. Hai việc làm được ngay là đọc BCTC soát xét bán niên 2026 và đọc thuyết minh 18 Q3.

## 1. Hạng mục vào tâm
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | Trích quỹ KTPL hằng năm từ LNST chưa trừ (mô hình chỉ trừ tồn quỹ 592,8) | ↓ | −3,73 [−3,73; −6,03] | **C+** | 0,50 [0,25; 0,75] | −1,86 | MIKE_EXTRACT Q3:35; BQ NP_P0 2025 |
| 2 | EBIT lõi Q4/26: base 9T/3 = 417,92 < nhịp Q3 481,21 (trước dự phòng) | ↑ | +0,31 [0; +0,31] | B | 0,50 [0,25; 0,75] | +0,16 | MIKE_EXTRACT Q3:8-17,40 |
| | **Σ tuyến tính** | | | | | **−1,71** | |
| | **Tổ hợp (chạy lại mô hình)** | | | | | **−1,71** | |

**Cơ sở từng hạng mục:**
- **#1 (C+, hạng mục skeptic bỏ sót — cùng lớp lỗi với FPT/NNC).** Quỹ KTPL tăng từ 405,7 (30/06) lên 592,8 (30/09), tức +187,1 tỷ trong Q3/26. Chi quỹ không âm nên số trích ≥ 187,1. Chia cho LNST mẹ 2025 là 3.024,9 (BQ, 4 quý) được **6,19%**: đây là cận bảo thủ và là con số vào tâm. Chỉ có 1 kỳ quan sát nên p lấy mặc định. Cận trên 10% là ước lượng, không có số riêng của DGC. Đo bằng mô hình: lõi × (1 − KT), vì mọi số hạng của lõi đều tỉ lệ với (1 − thuế). Trừ thêm KT × LNST mẹ 9T/26 là 1.267,10, khoản lãi đang nằm trong tiền ròng và sẽ được trích năm 2027. Tồn quỹ 592,8 (stock) đã trừ ở r3b; #1 chỉ là dòng trích hằng năm (flow), không đếm hai lần.
- **#2 (B).** EBIT lõi Q3/26 = LN gộp 506,35 − BH 76,18 − QLDN 48,96 + dự phòng 100 (ghi trong giá vốn Q3) = 481,21. Trung bình H1 là 386,3. Skeptic nghi Q4 bị đặt "quá cao" vì 9T còn gồm thời gian khai trường chạy. Số Q3 (sau khi khai trường dừng) đi ngược nghi ngờ đó, nên hạng mục có chiều LÊN. Dự phòng tách sang trục riêng của mô hình, không đếm hai lần.

**Dải:** chạy mô hình tại tổ hợp cực trị. Thấp: KT = 0,75 × 10%, Q4 = 0 ⇒ 39.957. Cao: KT = 0,25 × 6,19%, ΔQ4 = 0,75 × 63,29 ⇒ 41.555. |Σ| < 5%: cộng tuyến tính và tổ hợp lệch nhau 0,005pp.

## 2. Chỉ độ nhạy — KHÔNG vào tâm
| Hạng mục | Hướng | Độ nhạy (chạy mô hình) | Vì sao không vào tâm |
|---|---|---|---|
| [QUYẾT ĐỊNH USER 08/11, cách B] biên vĩnh viễn của nhánh mở lại khai trường 25 | ↑ | Có biên vĩnh viễn: 47.753 (+14,11%). w = 1 không biên: +0,78%. w = 0: −0,78% | User đã duyệt, không tự đảo. Mở lại khi có dữ kiện GP/trữ lượng |
| [LUẬT] r 13,5% so với dải Ke (E15) | ↑ | Ke 12,3%: 43.657 (+4,32%); 13,4%: +0,33% | Tham số luật V1 |
| [LUẬT D4] RONIC = Ke | ↑ | RONIC 20%: 43.813 (+4,69%) | Luật D4 |
| Ngoại trừ kiểm toán 2025: 950,9 tỷ tồn kho | ↓ | Mất toàn bộ: 39.437 (−5,76%); sau thuế: −5,00% | C: dấu "xuống hoặc 0", cận bảo thủ 0, chưa có tỷ lệ |
| Giải phóng VLĐ: tồn kho 2.085,9 về mức YE25 1.681,9 | ↑ | 42.873 (+2,45%) | C: không có cơ sở về thời điểm, và vướng cùng dòng tồn kho bị ngoại trừ |
| Trục dự phòng môi trường 100 tỷ/quý (1/3 mỗi nhánh [UL]) | ↕ | Một lần: +6,81%; bốn quý: +4,64%; vĩnh viễn: −11,46% | Trục [UL] của mô hình, đổi theo BCTC Q4 (§4) |
| Lá chắn thuế của dự phòng = 0 [UL] | ↑ | 20%: +1,36% | C |
| Nền biên r4 thay R2 | ↓ | −5,79% | Đã đối chiếu: GPM Q3 trước dự phòng 24,6% ủng hộ R2 |
| HTM 9.531 chưa đối chiếu PDF gốc | ↕ | Mỗi 1.000 tỷ lệch: ∓2.536 đ/cp (6,06%) | C |
| Capex môi trường bắt buộc sau vụ án | ↓ | Mỗi 1.000 tỷ NPV âm: −2.536 đ/cp | C: chưa có số |
| Nhà cung cấp quặng mua ngoài / bên liên quan | ↓ | chưa có số | C |
| **PHÁP LÝ: vụ án hình sự** | ↓ | Trục haircut tiền ròng 3/9/29%: 38.919 (−7,00%), chỉ hiển thị | **Luật 27/09: chỉ WARNING** |

## 3. Không đếm hai lần
- KTPL: tồn quỹ 592,8 (stock, đã trừ) tách khỏi dòng trích hằng năm (flow, #1).
- Q4: #2 là EBIT lõi trước dự phòng. Dự phòng 100 tỷ/quý nằm ở trục riêng của mô hình.
- Ngoại trừ tồn kho (C, xuống) và giải phóng VLĐ (C, lên) cùng nằm trên một dòng tồn kho. Cả hai chỉ là độ nhạy, không vào tâm, không bù trừ.
- r, dải Ke, E15 và ±50bp là một dòng luật.

## 4. BẢNG ĐIỀU KIỆN ĐỔI SỐ
Δ tính trên tâm 41.849. Các dòng độc lập cộng xấp xỉ được với nhau.

| Sự kiện / dữ kiện | Khi nào | Đổi gì | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|
| Thuyết minh 18 (quỹ KTPL) BCTC Q3/26 + NQ ĐHĐCĐ 2026: số trích thật = 10% | **làm được ngay** | #1 C+→A, p 0,9 | −1.490 | −3,56 |
| … số trích thật = 6,2% (đúng cận dưới) | **làm được ngay** | #1 C+→A | −624 | −1,49 |
| BCTC soát xét bán niên 2026 (đã công bố): ngoại trừ tồn kho còn hay đã gỡ | **làm được ngay** | Gỡ ⇒ 0. Còn VÀ được lượng hoá mất toàn bộ ⇒ C→A, p 0,9, sau thuế | 0 / −1.884 | 0 / −4,50 |
| Đối chiếu HTM 9.531 với PDF gốc | **làm được ngay** | Mỗi 1.000 tỷ lệch | ∓2.536 | ∓6,06 |
| BCTC Q4/2026: không trích dự phòng môi trường mới | ước lượng cuối 01/2027* | Trục dự phòng → nhánh một lần | +2.851 | +6,81 |
| BCTC Q4/2026: trích tiếp ≥ 100 tỷ | ước lượng cuối 01/2027* | Loại nhánh một lần; bốn quý / vĩnh viễn 50/50 | −1.426 | −3,41 |
| BCTC Q4/2026: EBIT lõi Q4 trước dự phòng ≥ 481 tỷ | ước lượng cuối 01/2027* | #2 → A | +52 | +0,13 |
| BCTC Q4/2026: EBIT lõi Q4 ≤ 418 tỷ | ước lượng cuối 01/2027* | #2 = 0 | −65 | −0,16 |
| Văn bản thời hạn GP + trữ lượng KT25/19B | khi có | Cận trên (biên vĩnh viễn). Biên hữu hạn theo thời hạn GP nằm giữa 0 và số này. Đổi cách B là quyết định user | ≤ +5.904 | ≤ +14,11 |
| Quyết định đóng vĩnh viễn khai trường 25 | khi có | w → 0 | −327 | −0,78 |
| NQ / công văn: capex môi trường bắt buộc | khi có | C→A, mỗi 1.000 tỷ NPV âm | −2.536 | −6,06 |
| Lãi huy động 12T hiệu dụng ±50bp (luật V1, β = 1) | liên tục | r ±50bp | −661 / +712 | −1,58 / +1,70 |
| Pháp lý: khởi tố pháp nhân / phạt, truy thu | khi có | WARNING. Có SỐ TIỀN phạt/truy thu ⇒ trừ tiền ròng theo số (A), không dùng haircut | theo số | — |

\* Lịch công bố là ước lượng theo nhịp thông thường, chưa xác minh với lịch CBTT của DGC.

**Điều kiện đổi số lớn nhất trong 2 tháng tới:** dự phòng môi trường Q4/26. Nếu bằng 0 thì tâm lên +2.851; nếu ≥ 100 tỷ thì xuống −1.426. **Làm được ngay:** số trích KTPL thật và tình trạng ngoại trừ ở bán niên. Kịch bản xấu của hai việc này cộng lại là ≈ −3.374 đ/cp (ước lượng tuyến tính).

## 5. Ghi chú
- Hook trong namespace `model_r3b` (thay `core` và `value_ps` lúc chạy, không sửa file khoá). Nguồn calc gốc bị TRIM, khôi phục ở `/tmp/ddrestore_B` với LOCK md5 assert.
- Cận trên tỷ lệ KTPL 10% là ước lượng. Cận dưới 6,19% là số đo.
