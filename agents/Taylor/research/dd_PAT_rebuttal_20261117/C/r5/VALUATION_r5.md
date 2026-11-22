# PAT — Định giá r5 (r4 → r5, user duyệt 22/11/2026), mù giá thị trường

## KẾT LUẬN ĐẦU
- **Tâm r5 TRƯỚC chiết khấu thanh khoản = 66.470 đ/cp** (cây trộn 9.072 lá; đường độc lập 66.475, lệch +0,0079%).
- **Tâm r5 SAU chiết khấu thanh khoản 10% = 59.823 đ/cp. Cổng mua 0,85 × tâm sau chiết khấu = 50.850 đ/cp.** (r4 cùng quy tắc: 59.686 / 50.733 — khớp ước lượng skeptic ~59.700 / ~50.700.)
- Khoảng sau chiết khấu: P25–P75 = 41.000 – 74.900 · P10–P90 = 33.800 – 87.500 · trung vị 59.500 (trước chiết khấu: 45.600–83.200; 37.600–97.300; 66.100).
- **⚠ Tâm r5 phụ thuộc MỘT lựa chọn đọc quan sát H1/26 (mục 3).** Đọc "sạch" (base r5, lý do ở §1.3) ⇒ 66.470. Đọc "nhiễu" (cách r4 dùng cho phía lạc quan) ⇒ **62.578** trước / **56.320** sau chiết khấu. Hai con số này là khoảng trung thực của tâm; con số 66.470 không phải "vững".
- Hành động không đổi: giá tham chiếu 70.200 (theo dispatch) cao hơn cả tâm trước chiết khấu lẫn cổng 50.850 ⇒ không có biên an toàn, không mua.

## 0. Bắc cầu r4 → r5 (đo trong phiên này, `calc_r5/bridge_sens_r5.py`; thứ tự cộng dồn: 2 → 3 → 1)
Kiểm hồi quy: khung r5 với tham số r4 (q=0, tồn kho 44,44, ô theo D) = 66.318,42 = r4.

| Bước | Tâm | Đóng góp | Gỡ riêng khỏi r5 |
|---|---|---|---|
| r4 | 66.318 | | |
| (mục 2) bỏ giải phóng tồn kho (về r2) | 64.781 | **−1.538** | thêm lại: −1.398 (r5 sẽ là 67.868) |
| (mục 3) ô (A tắt, B bật) → O2 — H1/26 đọc sạch | 69.581 | **+4.800** | gỡ (về D): r5 = 62.578 |
| (mục 1) trộn q_B {0; 0,25; 0,40}, mỗi cây refit λ' khớp F7 | **66.470** | **−3.111** | gỡ (q=0): r5 = 69.581 |
| **Tổng r4 → r5** | | **+152** | |

Tâm theo từng cây q_B (ô → O2): q=0 69.581 · q=0,25 66.057 · q=0,40 63.772. Cùng với ô theo D (r4): 64.781 / 62.285 / 60.669.
(Dispatch dự kiến trộn ≈ 64.000 "theo skeptic": đúng cho ô theo D — trung bình ba số trên = 62.578; đạt 66.470 chỉ vì mục 3 chọn đọc sạch.)

## 1. Từng mục
### 1.1 Mục 1 — q_B: áp ĐỦ
Bỏ luật nghĩa vụ chứng minh một chiều. Dựng được trộn (không phải dùng khoảng): tâm = trung bình đều ba cây. Trọng số đều là phán đoán (ba giá trị là lưới đại diện, không có bằng chứng xếp hạng) ⇒ báo kèm tâm từng cây ở trên. Giá trị q=0,40 và 0,25 giữ nguyên từ độ nhạy r4 (λ' 0,10664 / 0,07859).
### 1.2 Mục 2 — tồn kho: áp ĐỦ (đảo về r2)
Không có bằng chứng mới độc lập sau 14/11 (#R11 của r4) ⇒ không giữ. Biến thể độ nhạy (không vào tâm): giữ nguyên 44,44 ⇒ 67.868 (+1.398); giữ có haircut (nền 7 quý, dư 39,4 theo dispatch — **chưa tự đo** BQ; hệ số giữ 50% là quy ước độ nhạy của tôi, không có cơ sở bằng chứng) ⇒ 67.090 (+620). Thêm vào WARNING: tồn kho 31/12/2025 (67,7 tỷ) bị UHY ngoại trừ vì không xác minh được hiện hữu/giá trị (theo dispatch).
### 1.3 Mục 3 — một cách đọc H1/26: áp ĐỦ, nhưng chọn là phán đoán có hệ quả lớn
Chọn "sạch" cho CẢ hai phía. Lý do (dữ kiện trong file, không nhắm số): tồn kho 30/06/26 = 74,8 ≈ TB 3 mốc 75,75 (#R4) ⇒ không có kho quặng rẻ lớn để đốt trong H1; mua DLC H1 ≈ 190/quý ngang nhịp 2025 (#R7). Hệ quả: ô (A tắt, B bật) đã quan sát ⇒ O2; D chỉ áp ô (A bật, B tắt) chưa quan sát. +4.800 ở q=0. **Đây là bước đẩy tâm lên; nếu skeptic r5 bác cách đọc này, tâm về 62.578 (độ nhạy "mix, ô theo D").** Độ nhạy khác: ô → 75/25 = 64.524.
### 1.4 Mục 4 — phân tách "bằng chứng mới" vs "đọc lại thông tin có sẵn"
Thay câu "tâm vững, dịch <1%". Số theo skeptic r4/dispatch (so với rev4 = 64.700; **chưa tự đo lại**): thay đổi có bằng chứng mới −4.826 · đọc lại thông tin có từ 14/11 +6.409 (tổng +1.583 ≈ +1.600). Số đo trong phiên này (r4 → r5): cả ba thay đổi là đọc lại/phán đoán trên thông tin có từ 14/11 (không có sự kiện mới, #R11): −1.538 / +4.800 / −3.111 = **+152**. Hàm ý: tâm là hàm của cách đọc, không phải của bằng chứng; hai cách đọc hợp lý cách nhau 3.892 (cell O2 vs D) và ba giá trị q cách nhau 5.809 (69.581 vs 63.772). Độ tin cậy: **thấp**.
### 1.5 Mục 5 — chồng bi quan CÙNG cơ sở với skeptic
Cơ sở skeptic: q_B 0,25 + P(A) 0,35 + sản lượng một chiều (0,927/1,0), **không** đổi nút T.
| Mô hình | Chồng bi quan cùng cơ sở | + T 0,80/0,15/0,05 (phạm vi r4 cũ) |
|---|---|---|
| r4 | **60.354** (kiểm: trùng con số skeptic) | 57.154 (r4 báo 57.200) |
| r5 | 63.913 | 60.713 |
So 57.200 (r4) với 57.500 (skeptic) không cùng phạm vi, vì r4 có đổi nút T mà skeptic bi quan không có. Cùng cơ sở: 60.354 (r4) so 57.500 ⇒ cách 2.854, không phải 300. Trên r5 chồng bi quan là 63.913 (cách tâm −2.557).
### 1.6 Mục 6 — chiết khấu thanh khoản 10%
GTGD bình quân 1,01 tỷ, trung vị 0,60 tỷ/phiên, 64 phiên đến 17/11 (BQ; **số theo dispatch, chưa tự đo vòng này**). Tâm 66.470 → **59.823**. Cổng 0,85 × 59.823 = **50.850** (không phải 0,85 × 66.470 = 56.500). Phân vị sau chiết khấu: P10 33.847 · P25 41.038 · P50 59.483 · P75 74.906 · P90 87.530.
### 1.7 Mục 7 — ghi chú sổ giá
Viết ở `ledger_notes_r5.md`; không ghi `dd_price_zones.json`.

## 2. Độ nhạy (tâm cây trộn = 66.470 trừ khi ghi; đầy đủ `calc_r5/bridge_sens_r5_out.json`)
| Trục | Giá trị (đ/cp) |
|---|---|
| r 12,5 / 13 / 13,5 / 14 / 14,5% (g 2%) | 71.061 / 68.663 / 66.470 / 64.458 / 62.605 |
| g 0 / 1 / 2 / 3% (r 13,5%) | 59.817 / 62.880 / 66.470 / 70.736 |
| EBIT dài hạn ×0,8 / 0,9 / 1,1 / 1,2 | 57.120 / 61.795 / 71.145 / 75.820 |
| giá ×0,90 / 0,95 / 1,05 / 1,10 | 17.121 / 41.795 / 91.145 / 115.819 |
| DLC dưới netback −5% | 50.432 |
| T 0,80/0,15/0,05 · 0,55/0,35/0,10 | 63.212 · 68.270 |
| TX 0,90 | 67.971 |
| cước 3,85% / 4,03% | 67.843 / 67.547 |
| P giữa 1,0 (r3) | 67.179 |
| P(A) 0,30 / 0,35 / 0,70 · D(A) 0,7 · A muộn 25,5 tháng | 65.298 / 65.591 / 67.642 · 67.009 · 66.017 |
| cắt 2028 kiểu r2 (q=0) | 62.704 |
| cốc 2.100 / 2.108 | 60.422 / 60.246 |
| sản lượng một chiều / hai chiều · H2/27 −15% / −30% | 65.487 / 68.296 · 65.873 / 65.276 |
| điện 0,98 · φ 0,91 · φ 0,6 | 67.151 · 66.568 · 66.904 |
| một lần −50 · mất cầm cố −42,6 · 70 tỷ theo mệnh giá | 64.470 · 64.766 · 68.275 |
| ô (A tắt, B bật): 50/50 (= r4) · 75/25 | 62.578 · 64.524 |
| tồn kho: r4 nguyên · haircut | 67.868 · 67.090 |
(Các trục "EBIT dài hạn", "giá" chạy trên cây trộn; r4 chạy trên đường cơ sở nên số hơi khác.)

## 3. Điểm kém chắc nhất (theo thứ tự)
1. Cách đọc H1/26 (mục 3): ±3.900 lên tâm.
2. Giá DLC trả PAT (nút T): 58.900 → 88.200; dưới netback 5% còn 50.400. Nguyên tắc giá vẫn không tìm được.
3. q_B: 63.772 – 69.581 tuỳ q.
4. Cốc dài hạn: −6.000 đến −6.200 nếu giữ 2.100–2.108.
5. Mức giá thực hiện: ±5% giá ⇒ ±24.700.

## 4. Phương pháp và kiểm tra
- Khoá: `assumptions_objective_r5.md` md5 `872a9b82c9aaff679ea392beb4419123`, 2026-11-22T09:48:54Z (`lock_r5.txt`); calc chạy sau khoá. **Lệch so với giả định khoá: không có.**
- `calc_r5/` = bản sao `calc_r4/` + `model_r5.py` (`run_mix`, mặc định inv=0, cell='O2'), `bridge_sens_r5.py`, `selfcheck_r5.py`. Không sửa `r4/`.
- Kiểm hồi quy: khung r5 với tham số r4 ⇒ 66.318,42 = r4. Chồng bi quan trên mô hình r4 ⇒ 60.354 = số skeptic.
- Self-check (đường độc lập, không import mô hình, tích phân liên tục, trộn q_B): 66.475,3 vs cây 66.470,1, **lệch +0,0079% (ĐẠT < 0,5%)**; TZ không đặt / America/New_York cho kết quả giống hệt. Tổng xác suất lá = 1,0000000000.
- E[EBIT 2027] = 107,3 (self-check; r4 là 101,7 vì ô → O2). Bảng cầu EBIT 2027 của r4 không dựng lại ở r5.

## WARNING (không bake vào base)
- Vụ án hình sự lãnh đạo nhóm DGC/PAT (khởi tố 03/2026, mở rộng 07/2026); CT/GĐ/KTT PAT bị khởi tố vi phạm kế toán (theo dispatch). Kiểm toán ngoại trừ.
- **Tồn kho 31/12/2025 (67,7 tỷ) bị UHY ngoại trừ**: không xác minh được hiện hữu/giá trị — nền cho mọi so sánh tồn kho; khoản giải phóng tồn kho đã gỡ khỏi base.
- Bảo đảm chéo trong nhóm: 40 tỷ + 100.000 USD cầm cố cho "Công ty và các công ty thành viên".
- Công ty mẹ DLC (51%) rút giá trị qua giá chuyển giao: 2026 PAT +1% so P4 Trung Quốc +19,5% (theo dispatch).
- Rủi ro thiếu quặng ảnh hưởng KHỐI LƯỢNG sau Q1/2027.
- **Thanh khoản đã chiết khấu 10% ở đầu bài** (không còn "không đánh giá").
