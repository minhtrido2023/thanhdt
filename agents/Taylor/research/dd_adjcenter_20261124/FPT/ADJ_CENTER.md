# FPT — Tâm kỳ vọng điều chỉnh (v2, 24/11/2026, job Taylor_20261124_110049)

Phương pháp: `../PREREG_adj.md` (md5 `ef5157cb…`) + phụ lục `../PREREG_adj_v2.md` (md5 `835dfc1e…`). Cả hai đều được khoá trước khi tính, và `calc_adj.py` assert cả hai md5. Script chạy 2 lần, run1 = run2 (md5 `3ed2f70f…`). Output: `adj.json`.
Bản này **thay bản pilot** (`0d52b34ec`: 56.204, dải 55.092–57.345).
Mù giá: không đọc giá thị trường. Tâm gốc = sổ rev4 (dd_date 2026-11-01), **57.312 đ/cp**. `skeptic_final` = REFUTED_OPEN, giữ nguyên nghĩa là trạng thái phản biện.

## Kết luận
**Tâm kỳ vọng điều chỉnh: 55.668 đ/cp (Σ p×m = −2,87%). Dải theo cực trị (p, m): 52.604–57.605.**
**Sau GDKHQ cổ tức 1.000 đ (chốt quyền 30/11, chưa GDKHQ): 54.668, dải 51.604–56.605.**

### Thay đổi so với pilot (theo v2)
| Điểm v2 | Áp vào FPT | Δ tâm |
|---|---|---|
| §1 bậc C+ | Trích KTPL hằng năm chuyển từ C sang C+, tính ở cận bảo thủ | −1,43% |
| §3 quan sát ngược phải có số | g: bỏ "5F Nhật giảm tốc" (định tính), nhánh p Bneg 0,35 → B1 0,50 | +0,50% |
| §2 dải theo (p, m) | ESOP có khoảng m [−0,47; −3,0]; trích KTPL có khoảng m [−2,87; −5,73] | dải rộng hơn |
| §5 | \|Σ\| = 2,87% ≤ 5% ⇒ cộng tuyến tính, không cần chạy tổ hợp | — |

## 1. Hạng mục vào tâm
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m |
|---|---|---|---|---|---|---|
| 1 | Tồn quỹ KTPL 1.477 tỷ chưa trừ khỏi NC (notes:323; S:14) | ↓ | −1,37 | A | 0,90 [0,75; 1] | −1,23 |
| 2 | XDCB "Khác" 371 tỷ chưa cộng (notes:344; S:24) | ↑ | +0,34 | A | 0,90 [0,75; 1] | +0,31 |
| 3 | **Trích KTPL hằng năm** (C+, cận bảo thủ) | ↓ | −2,87 [−5,73; −2,87] | C+ | 0,50 [0,25; 0,75] | −1,43 |
| 4 | Pha loãng ESOP (108 tỷ mệnh giá 9T26) | ↓ | −2,50 [−3,0; −0,47] ước lượng | B | 0,50 [0,25; 0,75] | −1,25 |
| 5 | conv CƠ SỞ 0,75 → 0,60 | ↓ | −1,85 (probe) | B | 0,50 [0,25; 0,75] | −0,93 |
| 6 | g CƠ SỞ 9% → 12% (LFL 9T26 +13,7%) | ↑ | +3,32 (probe) | B | 0,50 [0,25; 0,75] | +1,66 |
| | **Σ** | | | | | **−2,87** |

Cơ sở hạng mục #3 (C+):
- **Dấu chắc chắn.** Quỹ KTPL giảm từ 2.160 tỷ (31/12/25) xuống 1.477 tỷ (30/9/26), tức −683 tỷ. Trong 9T26 không có dòng trích (notes:323). Năm hoá, tốc độ chi là 911 tỷ/năm, bằng 9,71% LNST mẹ 2025 (9.376 tỷ = 9T25 6.866,6 + Q4/25 2.509,5).
- **Cận bảo thủ.** Lấy ½ tốc độ đó, tức 4,86% LNST. Nửa còn lại quy cho việc FTEL ra khỏi hợp nhất, vì phần này chưa tách được. Hệ số 0,59% tâm cho mỗi 1pp LNST lấy từ S:9 (phần DCF ≈ 59% tâm).
- **Hệ số p.** Chỉ có 1 quan sát (9T26), nên p theo thang B1.

Cơ sở chọn p:
- #4, #6: 1 kỳ quan sát. Với #6, LNST LFL và LNTT CN cùng kỳ 9T26 nên chỉ tính là một.
- #5: 2 kỳ cùng hướng (FY25 0,60; 9T26 −0,12). Chưa đủ 3 kỳ nên giữ mặc định.

Khoảng m của ESOP (ước lượng):
- Đầu thấp: pha loãng một lần 0,57% × (1 − 10.000/57.312).
- Đầu cao: pha loãng vĩnh viễn 0,57%/năm, tương đương cộng ≈ +0,57pp vào r trên phần DCF, sau khi trừ tiền thu theo mệnh giá.

## 2. Chỉ độ nhạy (C / tham số luật) — KHÔNG vào tâm
| Hạng mục | Hướng | Độ nhạy | Vì sao không vào tâm |
|---|---|---|---|
| Cam kết capex DC/AI/giáo dục vượt lịch sử conv | ↓ | −0,93% (−530 đ) mỗi 1.000 tỷ NPV âm | C thuần: dấu không chắc (capex tăng trưởng có NPV≈0), không có cận. Phần lịch sử đã nằm ở #5 |
| OTHER_ASSOC_BOOK 1.500 tỷ [UL] | ↕ | −2,27…+4,54% | C: thuyết minh không tách giá trị (notes:277) |
| Lãi LK Q4/25 600 tỷ [UL] | ↕ | 740 tỷ ⇒ −1,21% | C |
| [LUẬT] r 13,5% vs dải Ke (E15) | ↑ | Ke 12,3% ⇒ 61.176 (+6,74%) | Tham số luật V1, không vào Σ (v2 §4) |
| [LUẬT] chặn RONIC 5 năm (bản G) | ↓ | 50.652 (−11,62%) | Tham số luật V5, không vào Σ |
| Cổ tức 1.000 đ | ↓ | −1.000 đ, cơ học | Tách riêng, hai dòng kết luận |

Không đếm hai lần:
- Tồn quỹ KTPL (#1) là stock; trích hằng năm (#3) là flow. Hai hạng mục khác nhau.
- Phần capex đã thể hiện trong lịch sử nằm ở #5. Phần vượt lịch sử để ở C.
- r/E15 là một dòng luật.

## 3. BẢNG ĐIỀU KIỆN ĐỔI SỐ
Δ tính trên tâm 57.312. Các dòng độc lập cộng xấp xỉ tuyến tính.

| Sự kiện / dữ kiện | Khi nào (ước lượng lịch) | Đổi gì | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|
| GDKHQ cổ tức tiền 1.000 đ | cuối 11/2026 | cơ học | −1.000 | −1,74 |
| **BCTC năm 2026 có dòng trích KTPL / NQ ĐHĐCĐ 2027: tỷ lệ thật** | 01–04/2027 | #3 C+→A, p 0,9. Ví dụ 5% LNST. Mỗi 1pp lệch 5% ⇒ ∓0,53%. Tỷ lệ ≤ 2,7% ⇒ đổi chiều lên | −700 | −1,22 |
| Thuyết minh cam kết vốn DC/AI/giáo dục | cuối 01/2027 | C→A, tính theo mỗi 1.000 tỷ NPV âm (growth NPV≈0 ⇒ 0) | −530/1.000 tỷ | −0,93 |
| NQ ĐHĐCĐ 2027 có ESOP cùng cỡ | 03–04/2027 | #4 p → 0,9 | −573 | −1,00 |
| NQ ĐHĐCĐ 2027 KHÔNG có ESOP | 03–04/2027 | #4 p → 0 | +716 | +1,25 |
| BCTC kiểm toán 2026: lãi LK Q4/25 (ví dụ 740 tỷ) | 03/2027 | C→A | −696 | −1,21 |
| Q4/2026 (kỳ mới) LFL LNST ≥12% + KH 2027 ≥12% | 01–04/2027 | #6 có 3 quan sát ⇒ p 0,65 | +285 | +0,50 |
| Q4/2026 LFL LNST <9% | cuối 01/2027 | #6 có quan sát ngược bằng số ⇒ p 0,35 | −285 | −0,50 |
| Q4/2026 conv ≤0,60 | cuối 01/2027 | #5 p 0,65 | −159 | −0,28 |
| Q4/2026 conv ≥0,75 | cuối 01/2027 | #5 p 0,35 | +159 | +0,28 |
| Lãi huy động 12T ±50bp (luật V1) | liên tục | r | −1.406 / +1.519 | −2,45 / +2,65 |
| Số dư quỹ KTPL mỗi BCTC quý | mỗi quý | tính lại #1 | theo số | — |
| Pháp lý FTEL | khi có | chỉ WARNING | 0 | 0 |

**Điều kiện đổi số quan trọng nhất:** tỷ lệ trích KTPL thật trong BCTC năm 2026 / NQ ĐHĐCĐ 2027. Đây là hạng mục C+ lớn nhất, dải m rộng gấp đôi.
