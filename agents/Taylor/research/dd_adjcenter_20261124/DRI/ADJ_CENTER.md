# DRI — Tâm kỳ vọng điều chỉnh (24/11/2026, job Taylor_20261124_110052, nhóm g2)

Phương pháp: `../PREREG_adj.md` (md5 `ef5157cb…`) + phụ lục `../PREREG_adj_v2.md` (md5 `835dfc1e…`), cả hai assert trong `calc_adj.py`. Chạy 2 lần: run1 = run2 (md5 `07b69ed4…`). Output `adj.json`.
Mù giá: không đọc giá cổ phiếu (bỏ qua mọi dòng nhãn/giá trong output r3). Tâm gốc = sổ **rev4, 15.257 đ/cp** (sau CK 2,00% @5 tỷ; `skeptic_final` = REFUTED_OPEN, là trạng thái phản biện, không phải quan điểm).
Số m lấy từ output engine r3 đã khoá md5 (`dd_recheck_20261124/DRI/calc/mirror/.../dri_redo_r3_out.txt`). |Σ| < 5% ⇒ cộng tuyến tính, không cần chạy lại engine theo tổ hợp (v2 §5).

## Kết luận
**Tâm kỳ vọng điều chỉnh: 15.164 đ/cp (−0,61% so với 15.257). Dải (cực trị p × m): 14.979–15.315.**
Không còn quyền chưa chốt: cổ tức 2025 1.000 đ đã chi từ 20/10/2026 ⇒ một dòng.

Rủi ro lớn nhất mà skeptic nêu (đất tô nhượng Lào và nghĩa vụ rừng bảo tồn) **không vào tâm**. Lý do có cơ sở, không phải vì thiếu dữ kiện: theo luật 20, chu kỳ tái canh 2 đã tính NPV0. Vì vậy trả đất *sau* chu kỳ 1 làm tâm đổi ≈ 0. Tâm chỉ giảm khi có nghĩa vụ chi bắt buộc, hoặc phải trả đất *trước* hết đời cạo. Cả hai trường hợp đều có độ nhạy đ/cp ở §2 và một dòng ở bảng §4.

## 1. Hạng mục vào tâm (A/B/C+)
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | Haircut khoản cho Dakruco vay 40 tỷ (TSĐB là 6 triệu cp DRI ⇒ rủi ro cùng chiều) | ↓ | −2,64 [−1,76; −3,51] | B | 0,35 [0,15; 0,55] | −0,92 | r3_out ("haircut 50%" −268, "mất trắng" −536); r1_raw:13; SUMMARY_r2:84,136 |
| 2 | Tỷ lệ KTPL 10,6% (FY25) → 9,9% (mẫu 9T26) | ↑ | +0,63 [+0,43; +0,86] (ước lượng) | B | 0,50 [0,25; 0,75] | +0,31 | r1_raw:33; assumptions_r3 `wht_basis` |
| | **Σ** | | | | | **−0,61** | |

Lý do chọn p (v2 §3, 1 quan sát = 1 kỳ; quan sát ngược phải có số):
- **#1:** quan sát ủng hộ là khoản vay phải gia hạn (REPORT_recheck:77). Quan sát ngược có số: Dakruco đã trả đúng hạn 80 → 40 tỷ trong H1 (SUMMARY_r2:84) ⇒ nhánh ngược 0,35. m là khoảng của engine (haircut 50%…100%), tâm m lấy trung điểm.
- **#2:** 1 kỳ (9T26) ⇒ mặc định 0,50. Cách tính m: giá trị vận hành ∝ (1 − KTPL − TAU). Đổi KTPL 0,106 → 0,099 cho +0,86% trên phần vận hành; phần này ≈ 73% tâm (tâm trước CK trừ tiền ròng 236,7 tỷ và XDCB 72,7 tỷ; ước lượng). Cận dưới lấy ½.

## 2. Chỉ độ nhạy (C / tham số luật) — KHÔNG vào tâm
| Hạng mục | Hướng | Độ nhạy | Vì sao không vào tâm |
|---|---|---|---|
| Đất tô nhượng 01616 + trả/trồng bù rừng bảo tồn Đông Huê Sáo (D3) | ↓ | Trả đất sau chu kỳ 1: ≈ 0 (NPV0). Chi tuân thủ: −134 đ/cp mỗi 10 tỷ PV (−0,88%). Trả đất trước hết đời cạo: ≈ −8,9% mỗi 1.000 ha mất ngay (ước lượng cận trên) | C: chưa có diện tích chồng lấn hay chi phí trồng bù ⇒ cận bảo thủ = 0, không đủ điều kiện C+ |
| Trục q khối thanh lý [UL] | ↕ | q 0,7: +652 (+4,27%); q 1,0: −652; q 0,5: +1.522 | Chỉ có dữ liệu định tính "q < 1", đã nằm trong lưới |
| FCF/LN lõi 90% [UL] (skeptic: CFO TTM yếu) | ↕ | 80%: −936; 100%: +936 | 3 kỳ TTM không chồng nhau, CFO/LNST = 1,36 / 0,91 / 0,48 (BQ). Các kỳ đi ngược chiều nhau, trung bình 0,92 ≈ base. Q3/26 thấp do giữ hàng |
| wht 8,16% | ↕ | 7,04%: +159; 8,30%: −20 | Base nằm trong dải 2 quan sát ngược chiều |
| Giữ lại 15% tiền tại Lào | ↓ | −395 (−2,59%) | Biết dấu nhưng không có số quan sát ⇒ cận = 0 |
| wp PEAK giá cao su (E16 "ĐỈNH LỢI NHUẬN?") | ↕ | ∓76 mỗi 0,1 wp; wp 0/1: ±382 | Phân vị RSS3 thực phụ thuộc cửa sổ đo: 89% (2014–26) nhưng 56% (2006–26, đo lại từ snapshot cao su + CPI trong mirror) ⇒ không có hướng |
| Giá gỗ LAK ±10% | ↕ | ±164 | Biến tỷ giá, không có hướng |
| GPM về peer 25% | ↓ | −20,6% | Dữ liệu bác bỏ: GPM lịch sử của chính DRI 28–43%, trung bình ~37% (r1_raw:9) |
| Gia hạn tô nhượng sau 2054 | ↑ | ≈ 0 theo NPV0; ≤ +1,6% nếu chu kỳ 2 có NPV > 0 (ước lượng) | Văn bản chưa công khai |
| Ý kiến kiểm toán FY2025 | ↕ | — | Chưa ghi; có ngoại trừ ⇒ C → A |
| [LUẬT] r 13,5% vs dải Ke (E15) | ↑ | Ke 12,3%: 15.713 (+2,99%); Ke 13,4%: +0,24% | Tham số luật V1 (v2 §4) |
| [LUẬT] Tái canh NPV0 (RONIC = Ke) | ↕ | Nhánh KINH TẾ 0,1/0,2/0,3: −164/−329/−494; chiều lên chưa lượng hoá | Luật 20 / V5 |

## 3. Không đếm hai lần
- **Dakruco:** haircut tín dụng (#1) là một hạng mục kinh tế. Vụ án ở Dakruco và giao dịch bên liên quan là WARNING (luật 27/09), không trừ thêm.
- **wht và KTPL:** wht hiệu dụng = 10% × (1 − KTPL − TAU). Hạng mục #2 đã tính tác động qua công thức này. Trục wht 7,04/8,30% đứng riêng, không vào tâm.
- **E16 đỉnh lợi nhuận và CFO yếu:** đã phản ánh qua trục wp giá cao su và FCF/LN, đều là C. Không thêm hạng mục "LN đỉnh" riêng.
- **r / dải Ke / E15:** gộp thành một dòng luật.

## 4. BẢNG ĐIỀU KIỆN ĐỔI SỐ
Δ tính trên tâm 15.257. Lịch công bố là ước lượng theo nhịp thông thường, chưa xác minh với CBTT của DRI.

| Sự kiện / dữ kiện | Khi nào | Đổi gì | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|
| Dakruco trả nốt 40 tỷ (BCTC Q4/26 hoặc CBTT) | ước lượng cuối 01/2027 | p#1 → 0 | +141 | +0,92 |
| Dakruco gia hạn tiếp / quá hạn / DRI trích dự phòng | ước lượng cuối 01/2027 | p#1 0,35 → 0,90 (dự phòng có số ⇒ thay m) | −221 | −1,45 |
| Văn bản tô nhượng hoặc BCTN: diện tích rừng phải trả + chi trồng bù | BCTN 2026 (ước lượng 04/2027) hoặc legal-vn tra | C → A | −134 mỗi 10 tỷ PV; trả trước hết đời cạo ⇒ chạy lại engine với A0 − X ha | −0,88 mỗi 10 tỷ |
| BCTC kiểm toán 2026: KTPL cả năm ≤ 10% | ước lượng 03/2027 | p#2 → 0,9 | +38 | +0,25 |
| BCTC kiểm toán 2026: KTPL ≥ 10,6% | ước lượng 03/2027 | p#2 → 0 | −48 | −0,31 |
| Kết quả đấu giá 1.975 ha (giá trúng; ai trúng) | theo lịch NQ15 | Giá gỗ; bên liên quan trúng ⇒ WARNING | ±164 mỗi ±10% giá | ±1,07 |
| HĐQT 12/2026 mua Dakruwood từ Dakruco | 12/2026 | Trả cao hơn sổ/NPV0 | −134 mỗi 10 tỷ | −0,88 |
| BCTN 2026: năng suất khối thanh lý | ước lượng 04/2027 | q C → A | q 0,7: +652 / q 1,0: −652 | ±4,27 |
| Lãi huy động 12T hiệu dụng ±50bp (V1, β = 1) | liên tục | r | +50bp: −180 / −50bp: +186 | −1,18 / +1,22 |
| BCKT FY25/FY26 có ngoại trừ | khi đọc BCKT | Khoản ngoại trừ có số ⇒ A | theo số | — |
| Pháp lý Dakruco/DRG | khi có | Chỉ WARNING (luật 27/09) | 0 | 0 |

Kịch bản gộp (chỉ minh hoạ, tuyến tính, KHÔNG phải tâm):
- Chiều xấu: Dakruco quá hạn, nghĩa vụ rừng 20 tỷ PV, mua Dakruwood đắt 10 tỷ ⇒ ≈ 15.164 − 221 − 268 − 134 ≈ 14.541.
- Chiều tốt: Dakruco trả nốt, KTPL ≤ 10% ⇒ ≈ 15.164 + 141 + 38 ≈ 15.343.
