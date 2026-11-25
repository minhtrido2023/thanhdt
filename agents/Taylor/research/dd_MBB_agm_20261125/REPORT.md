# MBB: đóng hạng mục trích quỹ khen thưởng phúc lợi (KTPL), 25/11/2026 (job Taylor_20261125_080251)

Thẩm định MÙ GIÁ. Giá 19.250 (06/11, kế thừa sổ) chỉ dùng để gắn nhãn cơ học ở cuối. Đơn vị triệu đồng, trừ khi ghi khác.
Calc: `calc/calc_agm.py`. Chạy 2 lần cho cùng output (`run1.txt` = `run2.txt`). Có 3 chân CONTROL tái lập số đã ghi sổ: tâm 21.069, vùng 14.729–27.577, tâm điều chỉnh đợt 2 là 20.587.
Nguồn gốc: BCTC tải từ static2.vietstock.vn (md5 ở `src/pdf_md5.txt`, ảnh trích trang ở `src/img/`). Mô hình RI r3 khôi phục từ git `14ad1c925^`, md5 `mbb_r3.py` là f5ad8f9e.

## 0. Nghị quyết ĐHĐCĐ 2026: KHÔNG lấy được văn bản gốc
- mbbank.com.vn trả 403 với tải tự động và không được vượt. Trang tài liệu của vietstock nạp bằng ajax, CafeF không có tài liệu. Vì vậy **chưa đọc được bản NQ/BB gốc**.
- Đọc được từ nguồn công ty: tin chính thức news.mbbank.com.vn về ĐHĐCĐ 18/04/2026. Nội dung gồm cổ tức tổng 25% (10% tiền mặt + 15% cổ phiếu), quyền mua 10:1 giá 10.000, phát hành riêng lẻ tối đa 200 triệu CP, vốn điều lệ tối đa 102.687 tỷ. **Bài này không nêu tỷ lệ trích quỹ.** Báo chí (diendandoanhnghiep, doanhnhan.baophapluat) và báo cáo SHS cũng không nêu.
- **Thay thế bằng nguồn mạnh hơn: BCTC kiểm toán và soát xét ghi lại việc thực hiện phân phối thật** (dòng "Trích quỹ khen thưởng và phúc lợi"). Đây là số đã chi, không phải số kế hoạch.

## 1. Số gốc
| Nguồn (trang in) | Dòng | Số |
|---|---|---|
| BCTC riêng KIỂM TOÁN 2025, TM 25.1 (tr.51) | Trích quỹ khen thưởng và phúc lợi **năm 2024** | (1.586.443) |
| nt | Trích quỹ khen thưởng và phúc lợi **năm 2025** | (1.775.629) |
| nt | LN thuần riêng 2024 / 2025 | 22.195.364 / 27.329.888 |
| BCTC hợp nhất KIỂM TOÁN 2025, TM 26.1 (tr.65–66) | Trích quỹ KTPL năm 2025, phần MB | (1.866.219) |
| nt | LN thuần thuộc MB 2024 / 2025 | 22.633.757 / 26.778.939 |
| BCTC hợp nhất Q3/2026, TM 22.1 (tr.36) | LNCPP sử dụng 9T/2026 | (28.462.814) |
| nt | Trích lập quỹ trong VCSH: dự trữ bổ sung VĐL / dự phòng TC / quỹ khác | 2.757.753 / 2.463.901 / 685.043 |
| nt | Vốn điều lệ | 80.549.999 → 100.687.499 (+20.137.500) |
| BCTC riêng Q3/2026, TM 22.1 (tr.33) | LNCPP sử dụng; quỹ dự phòng TC / dự trữ bổ sung VĐL / quỹ khác | (28.338.847); 2.459.690 / 2.732.989 / 685.048 |
| BCTC riêng Q3/2026, TM 21 (tr.32) | Quỹ khen thưởng, phúc lợi và Quỹ thưởng Người lãnh đạo quản trị điều hành | 1.906.685 → 3.335.476 |
| BCTC hợp nhất Q3/2026, LCTT | Cổ tức trả cho cổ đông 9T/2026 | (8.557.134) |

## 2. Dựng lại phân phối LN 2025 (thực hiện năm 2026)
- Vốn điều lệ tăng 20.137.500 = cổ phiếu thưởng 15% (12.082.500, từ LNCPP) + quyền mua 10:1 (8.055.000, **tiền cổ đông góp, không lấy từ LNCPP**). Số cổ phiếu 8.054.999.909 → 10.068.749.885 khớp, lệch lẻ 1 CP do làm tròn.
- Cổ tức tiền 10% × VĐL 80.549.999 = 8.055.000. Dòng LCTT 8.557.134 gồm thêm ≈502.134 cổ tức trả cổ đông không kiểm soát (≤ NCI sử dụng 555.369). **Đợt 2 trừ 8.557 là nhầm.**
- Quỹ trong VCSH lấy theo số **trích gộp** 5.906.697, không lấy biến động thuần 5.446 (phần 460.531 là chi quỹ khác). Riêng lẻ: dự trữ bổ sung VĐL = 10,0% LN riêng 2025; dự phòng tài chính = 10% phần còn lại. Cả hai khớp tới 1e-4.
- **Phần dư rời VCSH = trích quỹ KTPL + quỹ thưởng ban điều hành:**
  - Hợp nhất: 28.462.814 − 12.082.500 − 8.055.000 − 5.906.697 = **2.418.617 = 9,03% LN 2025 thuộc MB**.
  - Riêng lẻ: 2.323.620 = 8,50% LN riêng 2025.
  - Nhất quán với số dư quỹ tăng thuần 1.428.791 (đã chi một phần trong 9 tháng).
- Chuỗi tỷ lệ: riêng 8,00% (2025, dòng trực tiếp) → 8,50% (2026). Hợp nhất 8,25% (2025, dòng trực tiếp) → 9,03% (2026). **Ba năm liền ≈8–9%, là chính sách lặp lại chứ không phải sự kiện một lần.**

## 3. Kết luận định giá
**Hạng mục KTPL ĐÓNG: tỷ lệ thật k = 9,03% LN/năm (hợp nhất, phần MB), chứ không phải cận bảo thủ 4,45%. Bậc A (dòng BCTC trực tiếp, 3 kỳ).**
Mô hình RI giả định toàn bộ LN về cổ đông (clean-surplus), nên đây là sửa mô hình chứ không phải hạng mục xác suất. **KTPL vào TÂM BASE (rev6).**

| | rev5 (sổ) | **rev6** | Δ |
|---|---|---|---|
| Tâm (base, r 13,5%, sau CK 5 tỷ) | 21.069 | **18.595** | −11,74% |
| Vùng P10–P90 (n=45) | 14.729–27.577 | **13.151–24.140** | |
| Độ nhạy k = 8,25% (năm trước) | | 18.803 | −10,75% |
| Ngưỡng luật 4 (0,85 × tâm) | 17.909 | 15.806 | |
| Nhãn @19.250 (06/11) | TRONG | **TRONG** (giá > tâm +3,5%; 60% trọng số kết cục dưới giá) | không đổi |

**TÂM (base, r 13,5%, sau CK 5 tỷ): 18.595 đ/cp — vùng 13.151–24.140. Hạng mục KTPL đóng bằng BCTC gốc, k = 9,03%.**

## 4. Tâm kỳ vọng điều chỉnh (E17) trên base rev6
Bỏ #1 (đã vào base). Giữ #2 và #3 đợt 2, cùng p, chạy lại mô hình tổ hợp trên k = 9,03%:
| # | Hạng mục | m (% tâm rev6) | Bậc | p | p×m |
|---|---|---|---|---|---|
| 2 | Đường ROE 2027–29 +1,5/+1/+1pp | +2,58 | B (Bneg) | 0,35 [0,15; 0,55] | +0,90 |
| 3 | Phát hành riêng lẻ 200 tr CP tại BVPS…1,3×BVPS | −0,32 | B | 0,50 [0,25; 0,75] | −0,16 |

**Tâm kỳ vọng điều chỉnh: 18.731 đ/cp (dải 18.621–19.088; +0,73% so với tâm base rev6).** Dải gồm cả k = 8,25%.

## 5. Còn mở (không đổi tâm)
- Bản NQ/BB ĐHĐCĐ 2026 gốc (chỉ để trích nguyên văn; số thực hiện đã có ở BCTC). Không vượt chặn 403.
- CAR/Tier1 30/09 và nhu cầu vốn (skeptic r1). Phải thu MBV 30/09. Pháp lý sau 05/11 chỉ là WARNING. Mốc chất lượng tài sản BCTC Q4/26.
- skeptic_final giữ **REFUTED_OPEN**: đòn 8 KTPL đã đóng bằng số gốc, các đòn khác còn mở. Có thể chạy skeptic r2 nếu Mike muốn nâng nhãn.
