# MVC — DD redo VÒNG 3 (09/11/2026, job Taylor_20261108_180136)

**Kết luận.** Số lấy từ `calc_r3/mvc_redo_r3_out.txt`. Phân vị tính ở MỨC KẾT CỤC bằng `_shared/wpct.py`: 157.464 kết cục = 6.561 ô × 3 mức thuê × 8.

- Tâm **16.241 đ/cp sau CK 5 tỷ** (17.759 trước CK).
- **P10 9.940 · P50 15.359 · P90 23.471**; kết cục thấp nhất 7.690.
- Giá đóng cửa 06/11/2026 (BQ) **13.500**: thấp hơn tâm 16,9%, cao hơn P10 35,8% ⇒ **TRONG vùng** ở mọi cỡ lệnh.
- **30,5% trọng số kết cục nằm dưới giá.** Bản r2 tính ở giá mới là 47,3%.
- So với r2: tâm **+6,3%** (15.276 → 16.241). Nhãn không đổi.
- **Luật 4 (giá ≤ 0,85 × tâm): ĐẠT ở mọi cỡ.** r2 không đạt ở 5 tỷ. Ở 5 tỷ biên mỏng: ngưỡng 13.805, giá thấp hơn ngưỡng 2,3%. Kết quả này **phụ thuộc trục biên Tân Lập**: với trục một chiều {25/30/~NNC} của r2, ngưỡng là 13.399 ⇒ TRƯỢT 0,7%.
- **KHÔNG đủ điều kiện sleeve fear-buy §2.5**: không có sự kiện sợ hãi; ĐK2 (nợ ròng tiến tới 1,4–1,5 nghìn tỷ) chưa đóng.

**Tái lập và khoá:**
- Engine được import, không sửa file nào: chuỗi MVC r9 → `model_r8` → `nnc_model_r6/r5/r4/r3` → MVC `model_r6/r5/valuation_base`.
- Vá ở runtime có cổng tắt. Khi tắt D1 và dùng ICD của r2, calc tái lập đúng tham số trung tâm r2 **17.053,02** (có assert). Có thêm assert khớp `model_r8.branch` cho cả hai trục trần.
- Hai lần chạy cho output trùng byte (`run1.md5` = `run2.md5`).
- `calc_r3/LOCK_r3_md5.txt` ghi lúc **01:08:26 ICT**, TRƯỚC lần chạy đầy đủ đầu tiên, bằng lệnh `md5sum` riêng. Trước đó chỉ chạy `--check`, chế độ này không đọc giá. LOCK gồm 24 file upstream/dữ liệu, cộng script và `assumptions_r3.json`.

## 1. Kiểm từng đính chính của skeptic bằng calc
| # | Đính chính | Kết quả kiểm | Áp? |
|---|---|---|---|
| 1 | Trần chu kỳ bị đếm hai lần: P_CYC tính bằng tiền 2026 lại nhân với g2031; trần biên 25/30% cũng vậy | **ĐÚNG.** Đo được biên Tân Lập ở trần ~NNC: trước D1 (g2031, năm 2030) là **25,7%**, sau D1 là **34,0%**; NNC 34,3%. Khớp skeptic. Dùng chung patch NNC r3: `np_bottom` với cap = P_CYC×1,03^t/g, gắn vào `N4._np6`. Patch phủ luôn trần biên 30/38/25%, vì `tanlap8` đặt `S.P_CYC = cap_tl` rồi gọi cùng hàm giá. **+556 sau CK, khớp skeptic** | **BASE** |
| 2 | Trục trần thiếu mức SL 1,05 (`model_r8.py:76` âm thầm quy về 1,40) | **ĐÚNG.** Viết hàm `branch` riêng, dùng `cap_for(float(cap_basis))`. **+158, khớp** | **BASE** |
| 3 | Thuê Núi Nhỏ phải vào lưới {2043/2030/không} như NNC r3 | **ĐÚNG.** Mức 2030 nội suy theo tỷ trọng PV thuê sau 2030, cùng công thức với NNC r3. **−161, khớp**. Bước này tái lập **15.821 = điểm của skeptic**. Kiểm nhất quán: V_NNC ngầm trong MVC trước CK **63.369**, NNC r3 trước CK **63.591** (−0,3%) ⇒ nhất quán | **BASE** |
| 4 | Trục biên Tân Lập {25/30/~NNC} chỉ mở chiều giảm | **ĐÚNG**: vi phạm STANDARD_r2 #2. Có hai cách sửa: bỏ trục (16.222 ở CK 06/11; skeptic 16.281 tính ở CK khác) hoặc làm đối xứng {30/~NNC/38} (**16.299, khớp skeptic**). **Chọn bản đối xứng làm headline.** Lý do: biên đá riêng của Tân Lập CHƯA KIỂM ở cả hai chiều, vì không có báo cáo bộ phận. GPM hợp nhất 16,1% < peer chỉ là dữ liệu một phần, do lẫn gạch/xăng. Bỏ trục sẽ giả vờ biết chắc biên. Hai bản còn lại báo song song (§3) | **BASE (đối xứng)** |
| 5 | ICD Hoa Lư 44,80 cộng chồng lên NETFIN hợp nhất ⇒ đếm đôi −429 | **Đúng về hướng, SAI về độ lớn.** Đối chiếu BCĐKT hợp nhất với BCĐKT riêng ngày 30/09/26. Phần chênh khớp tổng TS (166,523) và VCSH (165,612). Tài sản thuần ICD = **41,651 tỷ**, gồm: tiền 2,923; GTGT 2,695; TSCĐ hữu hình 20,830; chi phí trả trước dài hạn 16,073; trả trước ngắn hạn 0,041; trừ nợ 0,911. Chỉ khoản **tiền 2,923** đã nằm trong NETFIN. TSCĐ và chi phí trả trước không nằm trong NETFIN, cũng không nằm trong DCF Tân Lập. CIP ICD giảm 37,69 → 0 trong 2026 là **chuyển loại** sang TSCĐ (+19,9) và chi phí trả trước dài hạn (+16,1), không phải xoá sổ (V.11 HN: đầu năm 37.688.978.021, cuối quý "-"). Base dùng tài sản thuần trừ tiền **38,728 tỷ** ⇒ **−58 sau CK** (không phải −429) | **BASE (bản sửa)** |
| 6 | Luật 4 theo cỡ; tranche ≤1 tỷ vượt trần sleeve | **ĐÚNG.** Đã ghi theo cỡ (§4). Tranche sửa thành ≤ min(4% NAV ≈ 38 tr; 20% ADV60 = **37,8 tr/phiên**). CK 5 tỷ = **8,55%**: ngoại suy, vì Q/ADV250 = 11,5× | sửa |
| 7 | Provenance + LOCK_r2 sai đường dẫn | Đọc lại txt BCTC HN Q3/26: tiền 117.395.029.976; HTM ngắn hạn 274.415.908.083; HTM dài hạn 20.000.000.000 (mã 265); vay ngắn hạn 461.848.321.896; **cổ tức phải trả 60.000.000.000 (V.19)**; quỹ KTPL 6.523.765.195 ⇒ **KHỚP cả 6 số**. Lưu ý: số đọc từ pdftotext, chưa soát bằng mắt trên PDF gốc. Đã ghi chú vào `calc/LOCK_r2_md5.txt` 2 đường dẫn đúng; md5 vẫn khớp (433e60cc…, 6edda90c…) | sửa |

## 2. Bridge r2 → r3 (sau CK 5 tỷ)
15.276 (pin r2, CK 04/11) → 15.268 (CK 06/11) → **15.824** (D1) → **15.982** (thêm trần 1,05) → **15.821** (thêm trục thuê) → **16.299** (biên Tân Lập đối xứng) → **16.241** (ICD tính theo tài sản thuần trừ tiền).

## 3. Headline và các bản song song (sau CK 5 tỷ; % = tỷ trọng kết cục dưới giá)
| Bản | Tâm | P10 | P50 | P90 | Dưới giá | Luật 4 (5 tỷ) |
|---|---|---|---|---|---|---|
| **Headline r3** | **16.241** | **9.940** | **15.359** | **23.471** | **30,5%** | ĐẠT (13.805) |
| Biên Tân Lập một chiều r2 {25/30/~NNC} | 15.763 | 9.910 | 14.530 | 23.398 | 37,8% | TRƯỢT (13.399) |
| Bỏ trục biên Tân Lập (~NNC) | 16.222 | 9.940 | 15.350 | 23.436 | 33,3% | ĐẠT (13.789) |
| Thuê chỉ tới 2043 | 16.402 | 10.197 | 15.518 | 23.623 | 29,1% | ĐẠT |
| Trần chỉ {nhánh, 1,40} như r2 | 16.084 | 9.940 | 15.111 | 23.444 | 32,3% | ĐẠT |
| ICD theo vốn góp 44,80 như r2 | 16.299 | 9.999 | 15.417 | 23.529 | 30,1% | ĐẠT |
| Độ nhạy chặt-3c (bỏ STRUCTURAL và ADMIN-perm05; user 08/11: KHÔNG headline) | 14.415 | 9.940 | 14.588 | 18.425 | 33,7% | TRƯỢT (12.253) |

**Ba con số "tâm":**
- Kỳ vọng lưới: 17.759 trước CK, 16.241 sau CK.
- Giá trị tại tham số trung tâm (không trễ GP): 17.704 trước CK; có trễ GP: 17.133.
- P50 kết cục sau CK: 15.359.

**Theo nhánh** (sau CK): STRUCTURAL 21.490 · ADMIN 15.431 · CYCLICAL 14.284. P90 do nhánh STRUCTURAL quyết định (trọng số 0,20, nhận định Bobby); trung vị nhánh này là 21.959. Đổi trọng số STRUCTURAL:
- 0,10 ⇒ tâm 15.585, P90 21.495;
- 0,30 ⇒ tâm 16.897, P90 25.309.

P10 gần như bất biến, quanh 9,9k.

## 4. Thanh khoản và luật 4 theo cỡ lệnh
Dữ liệu BQ cửa sổ 05/11/2025 → 06/11/2026: ADV250 0,435 tỷ · ADV60 0,189 tỷ · σ ngày 2,52%.

| Cỡ | CK (ADV250) | CK (ADV60) | Tâm sau CK | P10 / P90 | Nhãn | Luật 4 (0,85 × tâm) |
|---|---|---|---|---|---|---|
| 5 tỷ (Q/ADV 11,5×, NGOẠI SUY) | 8,55% | 12,97% | 16.241 | 9.940 / 23.471 | TRONG | ĐẠT (13.805) |
| 1 tỷ | 3,82% | 5,80% | 17.080 | 10.454 / 24.683 | TRONG | ĐẠT (14.518) |
| 40 tr (sleeve thật) | 0,76% | 1,16% | 17.623 | 10.786 / 25.468 | TRONG | ĐẠT (14.980) |
| 10 tr | 0,38% | 0,58% | 17.691 | 10.828 / 25.566 | TRONG | ĐẠT (15.038) |

**Tranche (sửa so với r2):** mỗi lệnh ≤ min(4% NAV SpaceX ≈ 38 tr; 20% ADV60 = 37,8 tr/phiên).

## 5. Giá đang ngụ ý gì (giá 13.500)
- **Ngay cả 100% nhánh CYCLICAL cũng cho 14.284 > giá.** Ở r2 con số này là 12.855 < giá. Vì vậy giá không còn giải thích được chỉ bằng kịch bản chu kỳ.
- Không có tỷ trọng STRUCTURAL ≥ 0 nào kéo tâm về bằng giá (nghiệm tính ra là −0,22).
- Nếu định giá NNC theo giá thị trường 47.200 (−1.496 sau CK), cần thêm chiết khấu holding/quản trị chung **~8,4%** mới ra giá. Chiết khấu này là [UL], base 0%.
- Gordon (r 13,5%, g 3%, BVPS 15.460): giá ngụ ý **ROE bền 13,0%**; tâm ngụ ý 15,1%. ROE trailing Q4 2017–25 trung bình 7,4% (đo: ROE_MVC trong model_r6.py); Q3/26 TTM 20,7%.

## 6. Độ nhạy đơn tại tham số trung tâm (trước CK, so với 17.704)
Theo cấu phần:
- Biên Tân Lập: 25% −1.204 / 30% −564 / 38% +576.
- Trần: SL 1,05 +604 / SL 1,40 −831.
- ADMIN: perm05 +1.241 / full −227.
- Bỏ thuê Núi Nhỏ −329.
- ICD theo vốn góp (r2) +64.

Rủi ro ngoài base:
- Trễ GP (Bobby F6) −571.
- Mỏ mới tính hai phía −2.078.
- Chiết khấu holding: 6% −388 / 15% −967.
- V_NNC theo giá thị trường −1.636.
- Chỉ nhánh CYCLICAL −1.801.

Lãi huy động ±100bp: −2,4% / +2,6%. r = 13,5% + 1,0 × (7,40% − 7,40%) = **13,5%** (cctg_12m 02/11, hiệu dụng tại 06/11).

## 7. Giả định [UL] và giả định tự đặt
Đầy đủ, kèm basis, ở `calc_r3/assumptions_r3.json` và `SUMMARY.json.assumptions`.
- Trọng số trạng thái 0,20/0,45/0,35 (Bobby).
- W0 25/50/20/5; PW0 50/50.
- Các trục chia đều: ca, REL, SL, hạn GP, ADMIN, biên Tân Lập, trần, thuê.
- Free float 30,2%.
- CK = σ√(Q/ADV250), Y = 1.
- Base KHÔNG có trễ GP, không có chiết khấu holding, không lấy V_NNC theo giá thị trường.

## 8. Mốc đổi nhận định, WARNING
**Mốc đổi nhận định:**
- **Lên:** có báo cáo bộ phận cho biên đá Tân Lập ≥ 38%; hoặc GP 2 mỏ mới được cấp đúng hạn 2028; hoặc NNC nâng tâm.
- **Xuống:** biên đá riêng ≤ 25%; nợ ròng năm 2027 vượt ngưỡng đã đăng ký ở r8 (+150 tỷ trên lộ trình); hoặc giá đã ở dưới P10 9.940.
- **HARD ABANDON:** xác nhận MVC phải thoái NNC hoặc NNC phải thoái MVC với giá bất lợi; khởi tố hay xử phạt trọng yếu; mất GP Tân Lập trước 2035.

**WARNING** (mang từ r2, chưa đóng):
- Sở hữu chéo 44,07% ↔ 10,3%; trùng Chủ tịch HĐQT.
- Uỷ quyền mua NNC lên 51% (giao dịch với bên liên quan, giá chưa công bố). **Rủi ro buộc thoái theo Luật DN Điều 195** khi MVC lên 51% (cần legal-vn).
- Cụm công nghiệp tới 500 tỷ; nợ ròng tiến tới 1,4–1,5 nghìn tỷ trước khi có doanh thu từ mỏ.
- Dư nợ BIDV 452 > hạn mức 350.
- Thanh khoản rất thấp.
- **Pháp lý sau 05/11/2026 chưa quét lại** (chỉ WARNING).

---
*Không đặt lệnh · không sửa `kb/dd_price_zones.json` · không email/PDF. Mike chạy phản biện cuối rồi mới ghi sổ.*
