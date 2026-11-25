# MBB rev6': thêm rò "Quỹ khác – sử dụng" vào k, tính lại mọi độ nhạy (25/11/2026, job Taylor_20261125_082754)

Thẩm định MÙ GIÁ. Giá 19.250 (06/11, kế thừa sổ) chỉ dùng để gắn nhãn cơ học ở cuối. Đơn vị triệu đồng, trừ khi ghi khác.
Bản này thay `REPORT.md` (rev6, đã khoá md5 da55412e trong proposal cũ; giữ nguyên làm lịch sử). Xử lý skeptic r2 (`skeptic/r2.json`, INCONCLUSIVE medium).
Calc: `calc/calc_agm_v2.py` → `calc/calc_agm_v2_out.json`. Chạy 2 lần cho cùng output: `run_v2_1.txt` = `run_v2_2.txt` (md5 5ed5af00).
CONTROL đạt: tâm rev5 21.069, vùng 14.729–27.577, tâm rev6 18.595, cùng 3 độ nhạy rev5 (RONIC>Ke 25.317, HARD ABANDON 18.969, ROE_T ±2pp 18.742/23.396).

## 1. "Quỹ khác – sử dụng": RỜI VCSH CỔ ĐÔNG (bằng chứng BCTC gốc)
| Nguồn (ảnh) | Dòng | Số |
|---|---|---|
| KT HN 2025 TM26.1, năm 2024 (`h25_p66b.png`) | Trích quỹ khác / **Sử dụng các quỹ trong năm** | 498.558 / **(348.289)**, và cột Tổng cộng cũng (348.289) |
| KT HN 2025 TM26.1, năm 2025 (`h25_p65.png`) | Trích quỹ khác / **Sử dụng các quỹ trong năm** | 556.625 / **(620.313)**, và cột Tổng cộng cũng (620.313) |
| HN Q3/26 TM22.1 (`hn_p44.png`) | Quỹ khác: dư đầu / trích / **sử dụng** / dư cuối | 904.382 / 685.043 / **(460.531)** / 1.128.894 |
| Riêng Q3/26 TM22.1 (`cm_p41_n22.png`) | Quỹ khác sử dụng | (460.531) |
| KT HN 2025 TM4.24.4, tr.35 (`h25_pol35.png`) | "Các quỹ khác thuộc nguồn vốn chủ sở hữu được phân bổ từ lợi nhuận sau thuế. Việc phân bổ … phải được ĐHĐCĐ phê duyệt." | |

- **Rời VCSH, không phải chuyển nội bộ:** dòng "Sử dụng" xuất hiện cùng giá trị ở cột **Tổng cộng** VCSH (2024, 2025). Q3/26 cân tổng: HN 142.022.525 + 51.597.885 − 29.478.802 = 164.141.608; riêng 130.639.656 + 50.094.629 − 28.799.378 = 151.934.907. Không có dòng VCSH nào nhận đối ứng 460.531.
- **Không qua P&L, không có khoản bù:** khoản sử dụng ghi thẳng vào VCSH, nên LN mô hình không chịu chi phí này. Chính sách 4.24.4 không nêu mục đích và không có cơ chế hoàn nhập về LNCPP. Bản chất chi tiêu cụ thể (từ thiện, an sinh hay khác) **không được thuyết minh**. Về kế toán thì đây là tiền của cổ đông rời VCSH, cùng loại với KTPL.
- **Không đếm trùng với KTPL:** k_KTPL 9,03% đã TÍNH phần trích quỹ khác 685.043 như quỹ TRONG VCSH (calc_agm.py). Phần rò mới là khoản tiếp theo, khi quỹ đó được chi ra.
- **Tỷ lệ:** trích 2025 = 2,46% LN 2024, 2026 = 2,56% LN 2025. Sử dụng so với LN cùng năm: 1,54% (2024), 2,32% (2025), 1,94% (9T26).
  - **Điểm 2,56%** (trích năm gần nhất do ĐHĐCĐ quyết). Quỹ không phân phối về cổ đông, và dư quỹ ổn định 0,8–1,1 nghìn tỷ ⇒ dài hạn chi ≈ trích. Cùng quy ước "theo trích" như KTPL.
  - Thấp 1,54% (sử dụng 2024), cao 2,74% (sử dụng 2025 / LN 2024).
- **Kết luận: BẬC A (3 kỳ liền, dòng BCTC trực tiếp), vào TÂM BASE.** k tổng = 9,032% + 2,558% = **11,59%**.

| | KHÔNG gồm quỹ khác (rev6) | **CÓ quỹ khác (rev6', CHỌN)** |
|---|---|---|
| k | 9,03% | **11,59%** |
| Tâm (base, r 13,5%, sau CK 5 tỷ) | 18.595 | **17.925** (−3,60% so với rev6; −14,92% so với rev5 21.069) |
| Vùng P10–P90 (n=45) | 13.151–24.140 | **12.719–23.215** |

Lý do chọn: bằng chứng là dòng BCTC giảm tổng VCSH ở cả 3 kỳ, không có dòng nào chứng minh khoản này quay lại cổ đông. Skeptic ước 17.900–18.150, khớp.

**TÂM (base, r 13,5%, sau CK 5 tỷ): 17.925 đ/cp — vùng 12.719–23.215. k = 11,59% (KTPL 9,03% + quỹ khác 2,56%).**

## 2. Độ nhạy và trigger trên rev6' (thay toàn bộ số rev5)
| Độ nhạy | rev5/rev6 cũ (sai base) | **rev6'** |
|---|---|---|
| ROE_T −2pp / +2pp | 18.742 / 23.396 | **15.979 / 19.871** (±10,86%) |
| Bỏ chênh terminal (ROE_T = Ke) | 17.961 | **17.070** (−4,77%) |
| Ke 12,3% / 13,4% | 23.659 / 21.266 | **20.095 (+12,11%) / 18.090 (+0,92%)** |
| r ±50bp (lãi huy động 12T, β=1) | −942 / +1.019 | **+50bp 17.135 (−790, −4,41%); −50bp 18.778 (+853, +4,76%)** |
| r ±100bp | | 16.402 (−8,50%) / 19.703 (+9,92%) |
| RONIC > Ke (g_RI = g_T) | 25.317 | **19.913** (+11,09%) |
| HARD ABANDON (CƠ SỞ + gánh lỗ MBV 15.688, sau CK) | 18.969 | **16.163** (−9,83%) |
| Xây lại bao phủ 1.940 tỷ DP | 20.877 | **17.762** (−0,91%) |
| Phải thu MBV mất 30% p 0,20 | 20.983 | **17.852** (−0,41%) |
| Trọng số kịch bản 0,35/0,45/0,20 (mốc xấu Q4) | 20.419 | **17.394** (−2,96%) |
| k thấp 9,78% / k cao 12,56% | | **18.396 (+2,63%) / 17.674 (−1,40%)** |
| k chỉ KTPL theo xu hướng 9,82% (+ quỹ khác 2,56%) | | 17.721 (−1,13%) |
| Ngưỡng luật 4 (0,85 × tâm) | 15.806 | **15.236** |

## 3. Tâm kỳ vọng điều chỉnh (E17) trên rev6'
Giữ #2, #3 như đợt 2, cùng p. Chạy lại tổ hợp ở k = 11,59%:

| # | Hạng mục | m (% tâm rev6') | Bậc | p | p×m |
|---|---|---|---|---|---|
| 2 | Đường ROE 2027–29 +1,5/+1/+1pp | +2,53 | B (Bneg) | 0,35 [0,15; 0,55] | +0,89 |
| 3 | Phát hành riêng lẻ 200 tr CP tại BVPS 15.594…1,3×BVPS | −0,26 … +0,25 | B | 0,50 [0,25; 0,75] | −0,13 (tại BVPS) |

- Ở #3, giá 1,3×BVPS = 20.272 cao hơn tâm 17.925, nên cận trên có dấu dương. Tâm vẫn dùng BVPS (bảo thủ, như đợt 2).
- **Dải ĐỐI XỨNG theo k.** Lưới tổ hợp chạy k ∈ {9,78%; 12,56%}:
  - cận thấp: KTPL 8,25% (2025) + quỹ khác 1,54%;
  - cận cao: KTPL 9,82% (gương xu hướng 8,25→9,03, khớp riêng 8,0→8,5) + quỹ khác 2,74%.
  - Dải chỉ theo k (p giữ nguyên): 17.807–18.532.

**Tâm kỳ vọng điều chỉnh: 18.059 đ/cp (dải 17.709–18.678; +0,75% so với tâm base rev6').** Trigger "ROE Q4 ≥20%, p 0,35→0,65": +0,75%.

## 4. CAR/Tier1 30/09 và nhu cầu vốn: KHÔNG có nguồn gốc ⇒ ngoài Σ
- BCTC Q3/26 HN/riêng (scan) không có thuyết minh tỷ lệ an toàn vốn. MB không công bố CAR quý trên kênh đọc được (mbbank.com.vn 403).
- Thứ cấp, chỉ tham khảo: CAR HN cuối Q2/26 ≈10,7% (SSI qua elibook 18/09/2026). CAR riêng 30/06 10,28%, Tier1 9,02% (đã ghi ở đợt 2). Cuối 2025 11,02%. Phát hành quyền mua xong 03/10 (+8.055 tỷ VĐL). Có kế hoạch 6.000 tỷ trái phiếu cấp 2 (vnba).
- Định lượng trong mô hình: VCSH giữ lại tăng ≈ ROE × (1 − k − payout) = 18% × (1 − 0,116 − 0,30) ≈ 10,5%/năm (ước lượng). Con số này < tín dụng 18%/năm ⇒ sẽ cần vốn mới. Nhưng RI giả định RONIC = Ke ⇒ phát hành ở giá ≥ BVPS gần như **trung tính** với giá trị/cp (đo: riêng lẻ tại BVPS −0,26%). Chỉ phát hành dưới BVPS mới làm giảm.
  - Không có kế hoạch phát hành ngoài 200 tr CP, nên **không gán p×m**. Để trong sensitivity_only (C), chiều xuống.
- Pháp lý sau 05/11 (tìm 25/11): không thấy tin thanh tra/xử phạt mới tháng 11. Các tin thanh tra chi nhánh (Hưng Yên 11/03, Quảng Ngãi 04/03, Huế) và QĐ 67/QĐ-KPHQ của UBCK về trái phiếu (~650 tỷ còn lại theo MB, chưa rõ ngày) là cũ. **Chỉ WARNING**, không vào tâm.

## 5. Nhãn và trạng thái
- Nhãn @19.250 (06/11): giá cao hơn tâm 17.925 **+7,4%**; 64,1% trọng số kết cục dưới giá; vẫn trong vùng 12.719–23.215 ⇒ **TRONG**. Luật 4 (giá < 15.236): KHÔNG đạt.
- skeptic r2 INCONCLUSIVE ⇒ **giữ REFUTED_OPEN**:
  - đòn quỹ khác: ĐÓNG (vào base);
  - số rev5 cũ: đã tính lại hết (§2);
  - dải k: đối xứng (§3);
  - CAR: chưa có nguồn gốc (§4), còn mở.
- Còn mở: CAR 30/09 gốc; văn bản nghĩa vụ MBV; BCTC Q4/26 (mốc chất lượng tài sản); NQ ĐHĐCĐ 2026 gốc (403).
