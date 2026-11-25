# SZL — kiểm kê hạng mục E17 (KHOÁ TRƯỚC khi tính; theo PREREG_adj.md md5 ef5157cb3f762d58623ed550ebc214c7 + PREREG_adj_v2.md md5 835dfc1e07f9c67ac7f6c3028b529d13)
Nguồn: S = `dd_redo_20261105/SZL/skeptic/r4_raw.md` (INCONCLUSIVE medium, vòng cuối); P = ảnh trang BCTC Q3/2026 `dd_redo_20261105/SZL/rev4/png/q3_pNN.png` (đọc phiên này); M = `rev5/calc/model_rev5.py`. MÙ GIÁ.
Tâm base = 26.183 (rev5, cỡ 5 tỷ sau CK 4,12%). Mọi hạng mục chạy QUA mô hình rev5 (`calc/calc_adj.py`: `add_extra` cho khoản t=0, dịch trục `NCS` cho nc).

| # | Hạng mục | Hướng | Bậc | m (đầu vào mô hình) | Nhánh thang p |
|---|---|---|---|---|---|
| S1 | Tồn kho BĐS khu dân cư Tam An: CP SXKD dở dang 76,21 (san lấp, xây dựng KDC Tam An) + thành phẩm BĐS 40,37 = 116,58 tỷ, không đổi so đầu năm (P q3_p22 TM7). Công cụ + hàng hoá 1,45 = vốn lưu động vận hành, KHÔNG tính. Không có trong `val()` (S missing_items 1). Luật "dự án mới = sổ sách" | lên | A | +116,58 tại t=0 | A hạ p 0,75 [0,50; 0,90] — lý do QUY ĐỔI: không bán được trong 9T (số dư không đổi; DT nhà đất ≈1,3 tỷ/quý theo S) |
| S2 | Trả trước người bán tăng 58,39 trong 9T (14,22 → 72,61): Phúc Hiếu 34,34, Kỹ thuật SEEN 16,80, Xây dựng Tu Sa 10,24 — nhà thầu, cùng kỳ XDCB nhà xưởng cho thuê 3,83 → 39,25 và Long Phước 295,86 → 344,66 (P q3_p19 TM4, q3_p22 TM8). Suy là ứng trước capex ⇒ tài sản theo giá vốn (NPV 0), chưa nằm trong XDCB 407 | lên | B | +58,39 [58,39 (phần tăng); 72,61 (toàn bộ)] tại t=0 | 1 quan sát (bản chất suy từ tên nhà thầu, thuyết minh không ghi) ⇒ mặc định 0,50 [0,25; 0,75] |
| S3 | Cổ tức dự thu từ bên liên quan 23,264 tỷ (P q3_p20 TM5 c). Không có trong `val()`; DT tài chính đã bị loại khỏi N0 ⇒ không đếm hai lần; đã ghi nhận tại 30/09 ⇒ GDKHQ ≤ 30/09 < 06/11 nên không trùng giá trị cổ phần niêm yết theo giá 06/11 | lên | A | +23,264 tại t=0 | mặc định A 0,90 [0,75; 1,00] |
| S4 | Trục nc (phần LN phi tiền mặt do phân bổ DT chưa thực hiện) trung bình 10% thấp hơn sàn phân bổ đều: DTCTH 762,16 (P q3_p28 TM19: NH 42,90 + DH 719,25) ÷ 27 năm (đến 2053) = 28,23 tỷ/năm × 0,8 = 22,58 ≈ 17% N0 (S missing_items 2) | xuống | C+ (cận bảo thủ = phân bổ đều 27 năm) | dịch trục nc +7pp [+7pp; +13pp (ước lượng: thời hạn còn lại BQ 20 năm ⇒ 38,1 × 0,8 ≈ 23% N0)] | CÓ quan sát ngược có số: DTCTH tăng ròng +81,23 trong 9T/26 (680,92 → 762,16) và CF_OA/LNST ≈ 1,8× (2025, 9T/26 — S) ⇒ nhánh ngược 0,35 [0,15; 0,55] |
| C1 | Tiền thuê thu trước MỚI định kỳ (CF_OA ≈ 1,8× LNST) chưa được ghi có | lên | C | phụ thuộc quỹ đất còn lại (KCN Long Thành gần lấp đầy) — không có số theo năm | chỉ độ nhạy |
| C2 | Capex duy trì vs KH (CF đầu tư 202 (2025) / 309 (9T/26) ≫ KH ~90) | hai chiều | C | đã là trục rộng nhất ±6.482 của rev5; không tách duy trì/mở rộng | chỉ độ nhạy |
| C3 | Ý kiến kiểm toán FY2025 | xuống | C | không có văn bản | chỉ độ nhạy |
| C4 | Long Phước vượt tổng mức 920 (báo chí) | xuống | C | độ nhạy rev5 −2.041 | chỉ độ nhạy |
| C5 | Công ty liên kết Bình Thuận 80 + An Bình 24,5 theo giá gốc, chưa kiểm suy giảm | xuống | C | không có số | chỉ độ nhạy |
| C6 | Số dư/bảo lãnh với SNZ (bên liên quan) | xuống | C | chưa đọc | chỉ độ nhạy |
| C7 | Người mua trả trước cho dự án Tam An (nếu có, giảm phần S1) | xuống | C | chưa đọc | chỉ độ nhạy |
| W | Truy thu/phạt thuế ~14 tỷ; vụ SNZ | xuống | pháp lý | WARNING, không vào tâm | — |
| L1 | r 13,5% > dải Ke (E15 27.233, +4,01%) | lên | luật | không vào Σ | — |
| L2 | RONIC = Ke; holdco 0% (CK holding v5 hiển thị 0…+20%) | — | luật | không vào Σ | — |
Chống đếm hai lần: S1/S2/S3 là tài sản t=0 khác dòng BCTC (tồn kho / trả trước / phải thu khác), không trùng XDCB 407 hay net debt; S4 (phân bổ số dư DTCTH hiện có) ≠ C1 (khoản thu trước MỚI trong tương lai). Cổ tức của SZL: tiền 25% đã ghi phải trả 70,36 tại 30/09 (đã trừ trong net debt), thưởng 70% đã vào mẫu số ⇒ một dòng tâm.
