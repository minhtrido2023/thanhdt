# DCM — Tâm kỳ vọng điều chỉnh (E17, 25/11/2026, job Taylor_20261125_032448)

Phương pháp: `dd_adjcenter_20261124/PREREG_adj.md` (md5 `ef5157cb…`) + `PREREG_adj_v2.md` (md5 `835dfc1e…`); `calc/calc_adj_dcm.py` assert cả hai + md5 `model_r9.py`/`assumptions_r9.json`, CONTROL 27.393 (lưới 2.430 kết cục, CK 0,585% đã khoá). Mô hình KHÔNG sửa — chỉ ghi đè hàm trong bộ nhớ. 2 lần chạy trùng md5 (`calc/run1.txt` = `run2.txt`, `f8589478…`). MÙ GIÁ. Tâm gốc 27.393 (proposal rev5 = sổ rev4). `skeptic_final` REFUTED_OPEN = trạng thái phản biện (r4 DD_GENERAL INCONCLUSIVE), không phải quan điểm đầu tư.

## Kết luận
**Tâm kỳ vọng điều chỉnh: 26.303 đ/cp (dải 24.470–27.236; −3,98% so với tâm base); căn cứ 2 hạng mục bậc B.**
|Σ tuyến tính| = 3,98% ≤ 5% ⇒ cộng tuyến tính (tổ hợp kiểm tra 26.309, −3,96%). Không có cổ tức tiền chưa GDKHQ trong dữ liệu rev9 ⇒ không có dòng cơ học.

## 1. Hạng mục vào tâm
| # | Hạng mục | Hướng | m điểm [thấp; cao] | Bậc | p [thấp; cao] | p×m |
|---|---|---|---|---|---|---|
| D1 | Quỹ KH&CN: phần trích bị chi bắt buộc cho KH&CN KHÔNG thành TSCĐ (chi phí, không tạo doanh thu đo được — D3) có giá trị 0 thay vì v (0,598 dòng / 0,779 số dư). Tỷ lệ f = (sử dụng − chuyển TSCĐ)/trích: 2024 61,9% · 2025 33,1% · gộp 2024–25 **38,7%** · 9T/26 ≤19,0% (47,5/249,63, chưa tách TSCĐ). Áp f cho cả dòng lẫn số dư | ↓ | −3,25 [−5,20 (f 2024); −1,60 (f 9T26)] | B | 0,50 [0,25; 0,75] — 2 kỳ cùng hướng (<3) | −1,63 |
| D2 | Hồi quy (LN trước khấu hao, trước trích) đoán cao hai năm kiểm toán gần nhất: phần dư r5_2021_25 +65,6 / −372,8, reg_ex22 −118,9 / −207,2 tỷ (2024/2025) ⇒ dịch tung độ gốc mỗi cửa sổ bằng phần dư TB 2 năm. Thấp: phần dư 2025; cao: phần dư 2024 | ↓ | −6,72 [−12,30; −1,13] | B | 0,35 [0,15; 0,55] — có quan sát NGƯỢC bằng số (r5 2024 +65,6; 9T/26 LNTT 2.562,9 > cả năm 2025) | −2,35 |
| | **Σ tuyến tính** | | | | | **−3,98** |

Nguồn: D1 — TM25 BCTC HN KT 2025 (`dd_DCM_20261104/png_r7/kt25_p37.png`; trích ở `REPORT_rev9.md` §1a T1, §9) + `skeptic/r4_raw.md:14-17`; D2 — `calc/model_r9.py` (fit_bd9, a_hist, DA_KT23), phần dư tái lập trùng REPORT_rev9 §1a T7 + `skeptic/r4_raw.md:18`.
Chống đếm hai lần: D1 chỉ đụng hệ số v (giá trị phần trích); D2 chỉ đụng tung độ gốc hồi quy (LN trước trích) — hai tham số khác nhau. Phần "mất toàn bộ quỹ nếu không được hoàn nhập" (rev7 reading) KHÔNG cộng thêm (đã bao một phần trong D1) — chỉ độ nhạy.

## 2. Chỉ độ nhạy — không vào tâm
| Hạng mục | Độ nhạy (sau CK) | Lý do |
|---|---|---|
| [LUẬT] r 13,5% vs dải Ke (E15) | 28.941 (+5,65%) | V1 — tham số luật |
| Khí 2035+ trục 0,5/0,25/0,25 | 22.574 (−17,59%) | C — trọng số trục là giả định; sau 24/4/2032 không còn khối lượng cam kết (A) nhưng chiều giá chưa có dữ liệu |
| Quỹ KH&CN mất 100% (cách đọc rev7: không hoàn nhập cho DN ngoài DNNN) | 25.009 (−8,70%) | C — văn bản chưa kiểm (T4) |
| Hạn thuê đất Cà Mau 2042 / 2047 | −1.873 / −994 đ/cp điểm (−6,8 / −3,6%) | C — năm hết hạn chưa kiểm (T5) |
| 332 tỷ phong toả MBV | −627 đ/cp điểm (−2,3%) | C |
| 4 cửa sổ hồi quy | 29.405 (+7,34%) | lựa chọn đặc tả, ngược chiều dữ kiện D2 |
| Thuế XK 0% P=0,55 | 28.423 (+3,76%) | C — xác suất chính sách không có dữ liệu |
| Quỹ thay capex M (T2) | ≤ +47 đ/cp | trần, không đối chiếu được từng dòng |

## 3. BẢNG ĐIỀU KIỆN ĐỔI SỐ
| Sự kiện | Khi nào | Đổi gì | Δ tâm adj |
|---|---|---|---|
| **BCTC KT 2026 (LNST 2026 vs đường hồi quy)** | ~03/2027 (Q4: ~01/2027) | phần dư 2026 ≥ 0 ⇒ D2 p 0,35→0,15 / âm lần 3 liên tiếp (≥3 kỳ cùng hướng) ⇒ p 0,65 + chạy lại mô hình (rev mới) | +1,3% / −2,0% |
| TM quỹ KH&CN KT 2026 (sử dụng, chuyển TSCĐ) | ~03/2027 | f 2026 ≤ 19% ⇒ D1 m −1,60% / f ≥ 62% ⇒ m −5,20% | +0,8% / −1,0% |
| Văn bản (Công báo/legal-vn) về hoàn nhập quỹ KH&CN cho DN ngoài DNNN | bất kỳ | không được hoàn nhập ⇒ C→A, chạy lại mô hình | tới −8,7% (ước lượng: cận rev7) |
| Hạn thuê đất nhà máy Cà Mau (HĐ thuê đất / GCN) | bất kỳ | C→A | −3,6…−6,8% nếu 2047…2042 |
| SĐBS 12 ký / văn bản giá khí sau 2034 | bất kỳ | trục khí 2035+ | tới −17,6% (giá Nam Du) / tới +4,0k đ/cp (rev9 §8) |
| Thuế XK phân bón 0% ban hành | bất kỳ | C→A | +3,8% |
| Lãi huy động 12T ±50bp | liên tục | r (V1) | −2,06% / +2,22% |

**Điều kiện đổi số quan trọng nhất:** LNST 2026 kiểm toán so với đường hồi quy (D2 — hạng mục lớn nhất, dải m rộng nhất); rủi ro đuôi lớn nhất vẫn là giá khí sau 2034 (C).
