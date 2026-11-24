# VGS — Tâm kỳ vọng điều chỉnh (24/11/2026, job Taylor_20261124_110049)

Phương pháp: `../PREREG_adj.md` (`ef5157cb…`) + `../PREREG_adj_v2.md` (`835dfc1e…`). `calc_adj.py` assert md5 của cả hai file và của `assumptions_r2.json` (bản sao nguyên văn, md5 `c1301436…`). Chạy 2 lần cho run1 = run2 (md5 `6120d3cf…`). Output: `adj.json`.
Mù giá. Tâm gốc là sổ rev3 (dd_date 2026-11-10): **26.526 đ/cp** sau CK ≤1 tỷ. Mô hình r2 trước CK cho 26.778. Script tái hiện `model_r2.value()` và assert CONTROL = 26.778. `skeptic_final` = REFUTED_OPEN.

## Kết luận
**Tâm kỳ vọng điều chỉnh: 25.148 đ/cp (Σ = −5,20%). Dải theo cực trị (p, m): 22.325–26.996.**
- **Cách gộp:** Σ tuyến tính = −5,21%, vượt 5%. Theo v2 §5, tâm được tính lại bằng chạy mô hình SOTP r2 trên **tổ hợp 2⁷ = 128** trạng thái bật/tắt hạng mục, trọng số Π p. Cổ tức tiền 2025 (1.000 đ) đã chi, nguồn không có quyền nào chưa chốt ⇒ chỉ một dòng kết luận.
- **Chênh với cộng tuyến tính:** 0,01pp. Mô hình gần tuyến tính theo LN lõi, nên tương tác nhỏ.
- **Hạng mục mới:** BCTC Q3/2026 HN tr.2, mã 323, ghi **Quỹ khen thưởng phúc lợi 36,1 tỷ**. Đây là nợ phải trả mà nợ ròng của mô hình chưa trừ. Cả r2 lẫn recheck đều không có dòng này. Nguồn: PDF khôi phục từ git `30ca17444^`, md5 `e30e74ce` khớp bản skeptic đã đối chiếu.

## 1. Hạng mục vào tâm (m chạy qua mô hình r2)
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m (tuyến tính) |
|---|---|---|---|---|---|---|
| 1 | Tồn quỹ KTPL 36,1 tỷ chưa trừ khỏi nợ ròng (mã 323) | ↓ | −2,19 | A | 0,90 [0,75; 1] | −1,97 |
| 2 | Ứng trước Vinaconex 38,02 tỷ thiếu trong vốn ròng Legend City (skeptic r2:19) | ↑ | +2,10 | A | 0,90 [0,75; 1] | +1,89 |
| 3 | Capex duy trì > khấu hao | ↓ | −11,79 [−14,74; −5,90] | B | 0,50 [0,25; 0,75] | −5,90 |
| 4 | Trích KTPL hằng năm từ LN lõi (C+, cận bảo thủ) | ↓ | −0,34 [−4,13; −0,34] | C+ | 0,50 [0,25; 0,75] | −0,17 |
| 5 | SG&A base 1,5% → TTM 1,625% | ↓ | −3,42 | B | 0,35 [0,15; 0,55] | −1,20 |
| 6 | GPM base 3,6% → 4,0% | ↑ | +5,54 [+4,85; +5,54] | B | 0,35 [0,15; 0,55] | +1,94 |
| 7 | DT base 7.700 → TTM 7.849,6 tỷ | ↑ | +0,57 | B | 0,35 [0,15; 0,55] | +0,20 |
| | **Σ tuyến tính / tổ hợp** | | | | | **−5,21 / −5,20** |

Cơ sở từng hạng mục:
- **#2 (A).** Đây là chi phí dự án đã trả. Theo luật NPV = 0, Legend City tính theo giá gốc, nên khoản này cộng vào vốn ròng và chịu cùng hệ số kịch bản LGC 1,0/0,7.
- **#3 (B1).** Một kỳ quan sát (9T26):
  - Capex tiền là 124,6 tỷ. Trừ phần XDCB Legend City tăng 90,9 tỷ, còn 33,7 tỷ capex ngoài LGC. Khấu hao cùng kỳ chỉ 9,1 tỷ (skeptic r2 đối chiếu LCTT gốc tr.5).
  - Năm hoá, khoảng chênh là 32,8 tỷ/năm. m điểm giả định toàn bộ khoảng chênh là capex duy trì, sau lá chắn thuế 20% còn 26,2 tỷ/năm.
  - Khoảng m: đầu thấp lấy ½ khoảng chênh; đầu cao lấy toàn bộ khoảng chênh, không tính lá chắn thuế.
- **#4 (C+).** Dấu chắc chắn: luật cho phép trích KTPL và quỹ đang được chi. 9T26 không có dòng trích: LNST chưa phân phối tăng 137,76 = LNST 199,28 − cổ tức 61,52. Quỹ giảm 0,56 tỷ.
  - Cận bảo thủ = tốc độ chi năm hoá, 0,74 tỷ/năm.
  - Cận trên = 9,18 tỷ đã phân phối từ LN 2025 (217,02 − 420b 207,84 = 4,2% LNST). Có thể gồm quỹ khác.
- **#5.** Một kỳ (TTM; CPBH 9T +59%). Có quan sát ngược bằng số: FY25 là 1,28%. Vì vậy dùng nhánh ngược.
- **#6.** Hai kỳ cùng hướng: biên sản phẩm tự sản xuất 5,29% ở cả 9T25 và 9T26, tỷ trọng hàng thương mại giảm (1.304 → 853 tỷ). Có quan sát ngược bằng số: GPM các năm 2018/19/22/23/24 lần lượt 2,6/3,3/2,3/2,5/3,0%, đều < 3,6%. Vì vậy dùng nhánh ngược.
- **#7.** Một kỳ (TTM). Có quan sát ngược bằng số: FY25 là 7.318,6 < 7.700. Vì vậy dùng nhánh ngược.

## 2. Chỉ độ nhạy — KHÔNG vào tâm
| Hạng mục | Hướng | Độ nhạy | Vì sao không vào tâm |
|---|---|---|---|
| Legend City NPV = 0 vs trần lợi nhuận NOXH | ↕ | −2…−6% (skeptic, ước lượng) | C: dấu không chắc vì miễn tiền SDĐ bù ngược lại; kịch bản xấu 0,7 đã nằm trong lưới |
| Cam kết vốn còn lại Legend City (tờ trình 05/2026) | ↓ | chưa định lượng | C |
| Capex tuân thủ môi trường | ↓ | chưa định lượng | C |
| Hoàn nhập dự phòng 21,1 tỷ (mã 322: 31,37 → 10,02) làm phồng GPM TTM ở kịch bản tốt | ↓ | ≈ −520 đ (−1,9%) | C: bản chất dòng P&L chưa xác định |
| Cách đọc (b) lãi liên kết 2025 = 70,2 | ↑ | +535 đ (+2,0%) | C: liên kết không công bố BCTC |
| Liên kết base = 0,75 × sổ | ↓ | 24.911 trước CK (−7,0%) | C |
| [LUẬT] CK holding +20% trên liên kết + LGC | ↓ | 24.288 trước CK (−9,3%) | Tham số house |
| [LUẬT] CK thanh khoản theo ADV60 | ↓ | −0,64% | Quy ước thanh khoản |
| [LUẬT] r 13,5% vs dải Ke (E15) | ↑ | Ke 12,3% ⇒ 28.294 (+6,66%) | Tham số luật V1 |

Không đếm hai lần:
- Tồn quỹ KTPL (#1, stock) và trích hằng năm (#4, flow) là hai hạng mục riêng.
- Ba hạng mục #3, #5, #6 cùng đi vào LN lõi, nên được tính trong tổ hợp chứ không cộng tay.

## 3. BẢNG ĐIỀU KIỆN ĐỔI SỐ
Δ tính trên tâm 26.526.

| Sự kiện / dữ kiện | Khi nào (ước lượng lịch) | Đổi gì | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|
| **BCTC năm 2026: thuyết minh TSCĐ/XDCB cho thấy capex duy trì ≈ khấu hao (phần chênh là mở rộng)** | 01–03/2027 | p#3 0,50 → 0 | **+1.564** | +5,90 |
| BCTC năm 2026 / LCTT FY24–FY25: capex ngoài LGC ≫ khấu hao cả 3 kỳ, không có dự án mở rộng | 01–03/2027 | 3 kỳ ⇒ p#3 0,65 | −469 | −1,77 |
| NQ ĐHĐCĐ 2027: tỷ lệ trích KTPL (ví dụ 4,2% LNST ≈ 9,2 tỷ) | 04/2027 | #4 C+ → A ở cận trên | −941 | −3,55 |
| Q4/2026: GPM quý ≥4% và SG&A ≤1,5% | cuối 01/2027 | p#6 → 0,50; p#5 → 0,20 | +356 | +1,34 |
| Q4/2026: GPM quý <3% hoặc SG&A >1,8% | cuối 01/2027 | p#6 → 0,15; p#5 → 0,55 | −475 | −1,79 |
| Tờ trình 05/2026 / trần lợi nhuận NOXH Legend City | khi có | C → A: tính lại NPV LGC ở r 13,5% | −2…−6% (ước lượng) | — |
| BCTC kiểm toán 2026 + giải trình cổ tức liên kết 2025 (mốc M5) | 31/03/2027 | cách đọc (b) đúng ⇒ C → A | +531 | +2,00 |
| Lãi huy động 12T ±50bp (luật V1) | liên tục | r | −647 / +697 | −2,44 / +2,63 |
| User chốt CK holding +20% cho liên kết/LGC | khi user quyết | đổi luật ⇒ chạy lại | −2.467 | −9,30 |

**Điều kiện đổi số quan trọng nhất:** tách capex duy trì và capex mở rộng của lõi ống (thuyết minh TSCĐ trong BCTC năm 2026, hoặc đọc lại LCTT FY24/FY25 đã bị TRIM). Hạng mục này mang ≈ 6% tâm, gần bằng toàn bộ Σ.
