# PREREG_rev3 — PHỤ LỤC sau skeptic r1 (25/11/2026) — khoá TRƯỚC khi chạy calc_adj_rev3.py

Kế thừa `PREREG_rev3.md` (md5 trong `LOCK_rev3_md5.txt`). Base KHÔNG đổi (skeptic r1 tái lập tâm 27.477, D4 đúng). Chỉ sửa bảng E17 theo phản biện `skeptic/r1.json` (INCONCLUSIVE medium), mỗi dòng có lý do; mù giá.

| # | Đổi | Lý do (skeptic r1 dòng) |
|---|---|---|
| 1 | GIỮ (B ngược, p 0,35 [0,15;0,55], m = N0 về biên vận hành 9T/25, dải m [½; đủ]). Thêm độ nhạy C: biên vận hành ~10% (ước lượng, giữa EBITM 2023–24 6–13% skeptic nêu, chưa tách thu nhập TC) | r1:15 — đỉnh có thể nhiều năm; nhưng 6–13% là EBITM BQ chưa cùng định nghĩa với biên vận hành (LNTT−TC ròng)×0,8 ⇒ không đủ làm B |
| 2 | **B → C+** (cận bảo thủ): dấu chắc (tiền ứng không sinh lãi, số dư 9T không đổi) ⇒ m = −giá trị thời gian 1 năm @13,5% trên 227,8 tỷ = −27,1 tỷ; dải m [1 năm; 3 năm = −72,0 tỷ] (ước lượng); p theo thang B 1 quan sát 0,50 [0,25;0,75]. Bỏ hệ số 86% | r1:20 — tiền lệ LD Nhà Việt khác bản chất; ứng GPMB thường thành QSDĐ |
| 3 | m = +130,3 tỷ (VLĐ ròng ngoài tiền, = biến thể A2 r3) thay +240,6; dải m [+65,1; +130,3]; p giữ 0,35 ngược | r1:16 — cộng GTGT mà không bù trừ phải trả vận hành |
| 4 (MỚI) | **Mùa vụ Q4** (chiều lên): N0 = 9T×4/3 ⇒ thay bằng 9T×(3+s)/3/… tức hệ số (3+s)/4, s = DT Q4 / TB DT Q1–Q3 (BQ `ticker_financial`): 2023 1,104 · 2024 1,118 · 2025 1,252 ⇒ s TB 1,158. Bậc B; nhánh NGƯỢC p 0,35 [0,15;0,55] vì LN Q4/2023 52,9 < TB Q1–Q3 80,4 (quan sát ngược có số); DT 3 kỳ cùng hướng. m = N0 × ((3+s)/4 − 1), dải s [1,104; 1,252] | r1:19 |
| C mới | (a) Hợp đồng thuê hữu hạn: cam kết thuê không huỷ ngang 30/06 (h1_45: ≤1 năm 29,3 · 2–5 năm 108,8 · >5 năm 642,1 tỷ) ⇒ ≈ 27 năm còn lại (ước lượng, giả định đây là mặt bằng chính) ⇒ TV niên kim 27 năm thay vĩnh viễn (g tương đương = r − r/(1−1,135⁻²⁷)); (b) q trượt thầu Long Thành: dịch Δ ±10pp; (c) biên vận hành ~10% | r1:12–13 |
| Đóng | Truy thu tiền thuê đất: đã hạch toán Q4/2025; thuyết minh thuế q3_32: phải nộp tiền thuê đất đầu năm 27,4 → phát sinh 22,0 → đã nộp 38,6 → cuối quý 10,7 tỷ (nằm trong VLĐ) ⇒ không thêm khoản. Soát xét H1/2026 Deloitte (14/08/2026): kết luận chấp nhận, không đoạn nhấn mạnh (h1_09). Cam kết vốn TSCĐ 103,5 tỷ (h1_45) = V4a NPV 0, khấu hao trong N0 thay capex duy trì ⇒ không phải D3 | r1:14, r1:39 |
| Bác | OCR Q3 sai cột: §3.4 dùng q3_35 (thuyết minh 24/26), tổng DT Q3 = 224,47+108,75+219,10+227,33 = 779,65 = BQ ⇒ cơ chế biên miễn thuế không dựa trên cột lỗi | r1:9 |

Σ = #1 + #2 + #3 + #4; |Σ| > 5% ⇒ tổ hợp qua mô hình (luôn chạy tổ hợp). Dải = cực trị (p, m) từng hạng mục, chạy qua mô hình.
