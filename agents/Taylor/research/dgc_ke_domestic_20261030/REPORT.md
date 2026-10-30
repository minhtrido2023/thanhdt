# DGC — định giá lại theo Ke nội địa (30/10/2026, job Taylor_20261030_094438)

Khung (user chốt 30/10; `erp_domestic_v2_20261030/REPORT.md`): rf chuẩn hoá 6,75%, β 1,1, ERP nội địa 5,22–6,15%
⇒ **Ke khoảng 12,5–13,5%** (dải rộng 10,5–14,0%). 15,8% Damodaran = "góc nhìn nước ngoài, USD". Ke 14,9% của r12 chỉ còn là đối chứng.
Mô hình: `dgc_valuation_20261029_r12/model.py` không sửa; đặt `rf = Ke − 0,075` (vì `ke() = rf + 1,0×7,5%`).
Ke đi vào 3 chỗ: DCF lõi (Gordon, g 3%), P/B hợp lý (ROE−g)/(Ke−g), chiết khấu 2 năm giá trị Nghi Sơn; P/E lịch sử/nhóm so sánh không phụ thuộc Ke.
`dcf_valuation.py` (DCF_RATE_FRAME=domestic_v2) là mô hình fleet khác, không dùng cho DGC ở đây.

## Kết quả (đ/cp; trọng số kịch bản w 0,2/0,5/0,3 như r12)

| Ke | A7 | B7 | A7 thuận/cơ sở/nghịch | Ô thấp nhất lưới A7 (nền thấp + lặp vĩnh viễn, qua mô hình) | Nền biên cao, không trích thêm (A7 / B7) |
|---|---|---|---|---|---|
| 10,5 (dải rộng) | 36.263 | 42.498 | 50.282 / 38.012 / 24.003 | 28.823 | 41.996 / — |
| **12,5** | **33.951** | **39.414** | 46.846 / 35.613 / 22.584 | 27.293 | 39.095 / 44.557 |
| **13,0 (mốc giữa)** | **33.514** | **38.832** | 46.197 / 35.159 / 22.316 | 27.003 | 38.548 / 43.865 |
| **13,5** | **33.118** | **38.305** | 45.608 / 34.749 / 22.074 | 26.739 | 38.053 / 43.238 |
| 14,0 (dải rộng) | 32.757 | 37.825 | 45.070 / 34.375 / 21.853 | 26.499 | 37.601 / — |
| 14,9 (đối chứng r12) | 32.182 | 37.060 | 44.213 / 33.778 / 21.501 | 26.117 | 36.880 / 41.757 |
| 15,8 (nước ngoài) | 31.685 | 36.400 | 43.471 / 33.262 / 21.198 | 25.785 | 36.259 / — |

- Khoảng 12,5–13,5: **A7 33.118–33.951, B7 38.305–39.414**; dịch +0,9…+1,8 nghìn so với Ke 14,9. Giá 32.900 (28/10) thấp hơn A7 0,7–3,1%.
- Δ theo Ke nhỏ hơn mọi động lực chính (khai trường ≈ 5,2–5,5k; Nghi Sơn −3,9…+5,8k; dự phòng lặp −6,4…−6,7k).

## Mốc giữa 13,0 (khoảng 12,5–13,5) — các số phân rã dùng trong báo cáo 2.2

| Mục | 13,0 | 12,5 … 13,5 | r12 (14,9) |
|---|---|---|---|
| Haircut pháp lý 29% / 3% (Δ vs A7) | −3.240 / +2.303 | gần như không đổi | −3.241 / +2.302 |
| Biên: nền thấp không trích thêm / nền cao (Δ) | +217 / +5.034 | +217 / +5.144…+4.935 | +217 / +4.698 |
| Biên ±2pp quanh A7 | 30.467 – 36.559 | 30.834–37.064 … 30.134–36.100 | 29.345 – 35.017 |
| Mỗi 1pp biên | ≈ 1.523 | ≈ 1.558 … 1.492 | ≈ 1.420 |
| Khai trường B7 − A7 | +5.318 | +5.463 … +5.187 | +4.878 |
| Nghi Sơn P&L thấp / cao (Δ) | −3.942 / +5.753 | −4.006/+5.875 … −3.883/+5.639 | −3.742 / +5.364 |
| Nghi Sơn LN = 0 (A7 / B7) | 31.158 / 36.476 (Δ −2.356) | Δ −2.419 … −2.300 | 30.019 / 34.896 |
| Nghi Sơn từ dưới lên thuế 20% (A7 / B7) | 34.078 / 39.396 | | 32.690 / 37.569 |
| Nghi Sơn ròng trong A7: thuận / cơ sở / nghịch / TB | +1.933 / −208 / −1.788 / **−254** (gộp 2.356) | TB −191 … −310 | −447 |
| Nghi Sơn ròng cơ sở khi đưa NPAT 217 | +745 | +829 … +669 | +483 |
| NPV độc lập thấp / giữa / cao | −3.279 / 3.019 / 7.677 | −3.288…−3.270 / 3.163…2.881 / 7.938…7.428 | −3.245 / 2.524 / 6.781 |
| Cầu nối P/E↔DCF (giữa): −228 → 522 → 825 → 3.019 → 2.719 (VLĐ) → 3.412 (thuế ưu đãi) | | | −306 → 420 → 518 → 2.524 → 2.215 → 2.848 |
| Dự phòng 4 quý (nền thấp): Δ | −971 (32.760 vs 33.731) | | −960 |
| Dự phòng lặp vĩnh viễn qua mô hình: Δ | −6.511 | −6.658 … −6.379 | −6.065 |
| Lặp vĩnh viễn thô 100/quý: trước thuế / sau lá chắn 20% | 8.440 / 6.752 | | 7.406 / 5.925 |
| 1 quý / 8 quý (thô) | 254 / 1.830 | | 263 / 1.796 |

Lưới dự phòng đầy đủ ở từng Ke: `r10_at_ke*/out_r10_final_grid.csv`; tornado: `rerun/ke_*/out_r12_B_tornado.csv`.

## Tỉ trọng terminal, g ≤ GDP, RONIC ≥ Ke (DCF lõi, kịch bản cơ sở A7)

- **Tỉ trọng terminal**: 59% giá trị hoạt động của DCF ở Ke 13,0 (61% ở 12,5; 58% ở 13,5; 54% ở 14,9); 34% tổng giá trị DCF/cp (vì tiền ròng cộng riêng). DCF chỉ là 1/3 trong mỗi kịch bản (cùng SOTP và bội số) ⇒ terminal ≈ 11% giá trị kịch bản cơ sở (ước lượng: 0,34 × 1/3).
- **g = 3%** danh nghĩa VND, thấp hơn nhiều so với tăng trưởng GDP danh nghĩa dài hạn (ước lượng 8–10%: thực ~6% + lạm phát mục tiêu ~4%) ⇒ g ≤ GDP đạt, phía thận trọng.
- **RONIC = 12%** trong mô hình, THẤP hơn Ke 12,5–13,5% ⇒ tăng trưởng terminal hơi phá giá trị. Biến thể RONIC = Ke (tăng trưởng trung tính): A7 +74 (12,5) / +135 (13,0) / +185 (13,5) đ/cp — không đổi kết luận. Nhóm giữ RONIC 12% (thận trọng), không nâng g đồng thời với hạ Ke.

## Tái lập & đối chứng
- `ke_sens.py` (assert A7/B7 = 32.182/37.060 ở 14,9; dcf_parts = dcf_core), `grid_ke.py` (assert A7/B7/R1/R2N0 ở 14,9), `margin_ke.py` (assert 29.345/35.017),
  `rerun_r12.py`: r10+r11+r12_calc chạy lại trong bản sao; ở 14,9 **18/18 file out_r10_/r11_/r12_*.csv trùng byte** với r12.
- Sửa duy nhất trong bản sao: rf; bỏ assert neo số 14,9; hằng −6065 trong tornado r12 thay bằng Δ đọc từ out_r10_perpetual.csv của chính lần chạy (ở 14,9 cho đúng −6065).
- Tornado r12 gốc đọc lưới r10 cố định ⇒ rerun chạy lại r10 trước (đã sửa trong `rerun_r12.py`).
