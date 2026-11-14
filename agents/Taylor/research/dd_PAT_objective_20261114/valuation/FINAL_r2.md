# PAT — Định giá đính chính r2 (mù giá thị trường), 14/11/2026

> Người định giá độc lập thứ hai, stateless, không phải tác giả bản gốc. Khoá giả định: `assumptions_objective_r2.md` md5 `f2eb154f…` lúc 2026-11-14T17:06:03Z (`lock_r2.txt`, có 2 đính chính làm tròn). Mã: `calc_r2/model.py` (md5 da3e9d8e…), kết quả đầy đủ ở `calc_r2/model_out_r2.json`. Bản gốc (`assumptions_objective.md`, `calc/`) giữ nguyên, không sửa.

**Kết luận:** giá trị nội tại TRƯỚC chiết khấu thanh khoản: **tâm ≈ 64.700 đ/cp**. Vùng P25–P75 là **49.600–79.200** (P10–P90: 36.200–100.200). Giá trị cơ sở, tức mọi nút ở đầu vào kỳ vọng, là **64.700**. Trong đó tiền ròng chiếm 14.300 đ/cp. Tâm bản gốc là 83.800, tức r2 thấp hơn 19.100.

## 1. Cây kịch bản (4 nút độc lập, 54 lá; tâm = Σ p × V)
| Nút | Nhánh (xác suất) | Giá trị bình quân có điều kiện (đ/cp) | Neo bằng chứng |
|---|---|---|---|
| **O**: chi phí quặng từ 2028 | O1 về mức 2025 (0,1375) · O2 giữ GĐ1 H1/26 (0,3875) · O3 GĐ2 Q3/26 vĩnh viễn (0,475) | 82.100 / 73.600 / 52.500 | A = mỏ riêng nhóm DGC trở lại, P = 0,5. Mức trung tính vì có bằng chứng cả hai chiều và không chiều nào trội. B = cung VAPC bình thường hoá trước 2028, P = 0,55: hazard ngoại suy từ Bobby F7 (0,30 trong 6,5 tháng). ρ(A,B) = 0. Ca "đúng một nguyên nhân được giải" chia đều xác suất cho hai đầu mút đã quan sát, không bịa mức trung gian |
| **P**: giá thực hiện từ 2027 | −6,3% (0,32) · giữ (0,58) · +6,3% (0,10) | 40.000 / 71.700 / 103.500 | Biên độ = đúng mức thay đổi của PAT giai đoạn 2025 → 9T/26, quy đổi trước thuế. Xác suất lấy theo Bobby F2: P(P4 < 23.000) và P(P4 > 32.000) |
| **T**: giá DLC trả sau 01/01/2027 | netback, thuế chạm ~100% DT (0,65) · giữ cơ cấu, chạm 35% (0,25) · DLC bù + dồn lượng, chạm 13,5% (0,10) | 57.900 / 74.700 / 84.500 | Chuẩn giao dịch độc lập ở nước xuất ròng P4 có thuế XK là netback (#R2, #R3). Bên kiểm soát có động cơ ngược chiều (#R4). Hợp đồng bên liên quan được duyệt theo năm |
| **TX**: thuế 15% hiệu lực | có (0,90) · giữ 10% (0,10) | 62.600 / 84.100 | Đã đọc bản chép Phụ lục NĐ 199. Có một dự thảo chưa đọc được và có tiền lệ giảm thuế khoáng sản năm 2026 |

Các lá chính (P = 1, thuế 15%), đơn vị đ/cp; EBIT dài hạn và biên gộp TP ghi trong ngoặc:

| | Ta | Tb | Tc |
|---|---|---|---|
| O1 | 79.200 (227 tỷ; 16,2%) | 98.100 | 108.700 |
| O2 | 70.700 (195 tỷ; 14,3%) | 89.600 | 100.200 |
| O3 | 49.600 (118 tỷ; 9,8%) | 68.500 | 79.100 |

Đường cơ sở: EBIT 2027 là 123 tỷ, EBIT dài hạn 172 tỷ (giá 2028), biên gộp TP dài hạn 12,9%, terminal 34% giá trị.

## 2. Độ nhạy chính (đ/cp, trên đường cơ sở 64.700)
**r × g** (r neo lãi huy động 7,4%; mỗi ±50bp × β 1 tương ứng ±0,5pp r):

| r \ g | 0% | 1% | 2% | 3% |
|---|---|---|---|---|
| 12,5% | 61.600 | 65.000 | 69.000 | 73.900 |
| 13,0% | 60.000 | 63.100 | 66.800 | 71.200 |
| 13,5% | 58.500 | 61.400 | **64.700** | 68.700 |
| 14,0% | 57.100 | 59.700 | 62.800 | 66.500 |
| 14,5% | 55.700 | 58.200 | 61.100 | 64.400 |

| Biến | Giá trị (đ/cp) |
|---|---|
| LNST bền vững (EBIT dài hạn ×0,8 / 0,9 / 1,1 / 1,2) | 55.800 / 60.300 / 69.200 / 73.600 |
| Tỷ trọng DT chịu bước thuế 15% (s_eff 0,135 / 0,35 / 0,75 / 1,0) | 79.800 / 73.600 / 62.200 / 55.000 |
| Thuế XK giữ 10% | 83.700 |
| Giá thực hiện ×0,90 / 0,95 / 1,05 / 1,10 | 15.000 / 39.900 / 89.600 / 114.400 (**đòn bẩy rất lớn, ±5% giá ⇒ ±38% giá trị**) |
| Cốc dài hạn 1.704 / 1.825 / 2.108 CNY | 67.400 / 64.700 / 58.500 |
| Định mức cốc 1,25 / 1,5 t/t | 64.900 / 64.600 |
| NVL/DT dài hạn ±2,75pp | 77.700 / 51.800 |
| Nút O cố định O1 / O2 / O3 | 82.100 / 73.600 / 52.500 |
| P(A) 0,3 / 0,7 | 62.100 / 67.300 |
| Điện giữ ×0,98 (bỏ dự báo F5) | 67.800 |
| DLC trả dưới netback −5% trên 65% DT (WARNING) | 48.600 |
| Lỗ một lần −50 tỷ / mất cầm cố nhóm −42,6 tỷ | 62.700 / 63.000 |
| Tính 70 tỷ khoá theo mệnh giá | 66.500 |

**V_ngắn 90.500 so với V_dài 64.700, D = 0,34**, dưới ngưỡng ln2 nên không cờ phân kỳ. Lý do lệch: V_ngắn đo trên lợi nhuận lịch sử (TTM BQ 289,9), chưa có bước thuế 15% và chế độ quặng Q3/26.

## 3. Khoản vào cơ sở có bằng chứng / khoản đã GỠ
| Khoản | Trong cơ sở? | Bằng chứng (#, xem `assumptions_objective_r2.md` §0) |
|---|---|---|
| Bước thuế XK 10→15% áp theo nút T (kỳ vọng s ≈ 0,75 × 0,90) | Có (−) | #8, #R1–#R4, #R16 |
| 70 tỷ cầm cố bảo lãnh tiền điện: chỉ tính PV lãi (−45,1 tỷ) | Có (−) | #R9, #R10 |
| Quỹ KT-PL 6% trên LNST 9T/26 (−12,9 tỷ) | Có (−) | #3 |
| Chế độ quặng theo nút O; H1/2027 GĐ2 | Có (±) | #10–#13, #22 (F7), #R7 |
| Than cốc: 2027 giao ngay 2.108; từ 2028 TB 2023+ 1.825; định mức 1,37 t/t | Có (− 2027 / + dài hạn so bản gốc) | #R12, #R13, #R14 |
| DV/khác theo 9T/26, cùng khung giá với doanh thu cơ sở | Có (−) | `prelock_inputs.py` |
| Điện: −2% từ 01/11/2026 và kỳ vọng F5 +2,35% từ 2027 (thực ×1,003) | Có (≈0) | #15, #R15 |
| Giá thực hiện theo nút P | Có (−1,4% kỳ vọng) | #R6, #22 (F2) |
| Tiền ròng 357,4 tỷ | Có (+) | #2 |
| SG&A thấp theo kênh DLC; thuế TNDN ưu đãi theo văn bản; capex = KH | Có | giữ bản gốc |
| **GỠ:** DLC hấp thụ thuế cho PAT như mặc định cơ sở | Chỉ còn là nhánh T_b/T_c (0,35) | không có bằng chứng; ngược động cơ bên kiểm soát |
| **GỠ:** "cốc 2.108 = trung chu kỳ" | — | cửa sổ chứa siêu chu kỳ 2021–22 |
| **GỠ:** giá/tấn từ DV mua ngoài làm bằng chứng | — | mâu thuẫn ±7pp với lời DN |
| **GỠ (WARNING/độ nhạy):** 42,6 tỷ cầm cố cho công ty thành viên; DLC trả dưới netback; phạt/truy thu vụ án; hoàn nguyên đất; hỗ trợ giá quặng (chỉ có trong O1); mở rộng; moat; giải phóng VLĐ; giá P4 TQ giao ngay | Không | thiếu bằng chứng tổn thất/lợi ích; có bảo đảm chéo hai chiều (#R11) |
| **KHÔNG ÁP:** sản lượng 2027 theo nhịp bán Q3 (1.756) | Giữ 1.822 | nhịp sản xuất Q3 ≈ 1.834 vì tồn kho TP +16,65 tỷ (#R8) |

## 4. So với bản gốc (83.800 → 64.700): vì sao khác
Gỡ từng đính chính trên đường cơ sở r2 (`calc_r2/attrib.py`, không cộng tuyến tính tuyệt đối):

| Đính chính | Tác động lên giá trị r2 (đ/cp) |
|---|---|
| Thuế: netback thay cho "35% cố định" | **−9.900** |
| Nút O với P(O3) = 0,475, thay cho cơ sở O2 cộng cây 0,25/0,5/0,25 | **−8.900** |
| Nút P theo F2, thay cho giá giữ nguyên | **−7.000** |
| Điện theo kỳ vọng F5 | −3.100 |
| DV/khác theo 9T/26 (bỏ trộn kỳ) | −3.000 |
| Tiền ròng (70 tỷ khoá + KT-PL) | −2.300 |
| H2/2027 theo nhánh O | +700 |
| TX: 0,10 khả năng giữ 10% | +2.200 |
| Cốc dài hạn 1.825 + định mức 1,37 | **+7.000** |

Ba khoản lớn nhất (thuế, quặng, giá) đều đi theo cùng một nguyên tắc: bản gốc đặt nhánh có lợi cho PAT vào cơ sở mà không có bằng chứng (DLC hấp thụ thuế; giá giữ ở mức 2026), hoặc gán xác suất mâu thuẫn với chính lập luận của nó (P(bất lợi)). Theo hướng ngược lại, bản gốc bi quan về cốc vì dùng cửa sổ có siêu chu kỳ và định mức nền 1,5 t/t. r2 đã sửa cả hai chiều.

## 5. WARNING pháp lý (không vào cơ sở)
- Vụ án (#18): ngày 17/03/2026 khởi tố các tội kế toán, khai thác tài nguyên, ô nhiễm môi trường. Bị can gồm nguyên Chủ tịch, thành viên HĐQT, Giám đốc, KTT của PAT. Ngày 23/07/2026 khởi tố thêm Chủ tịch đương nhiệm khi đó. Kiểm toán 2025 và soát xét BN26 đều có ý kiến ngoại trừ. BGĐ chưa ước được ảnh hưởng tài chính. Minh hoạ tác động: một khoản lỗ một lần −50 tỷ tương đương −2.000 đ/cp.
- Chưa có bằng chứng nào về phạt, truy thu, đình chỉ đích danh PAT. Rủi ro "di cư" sang PAT tồn tại vì PAT ở KCN Tằng Loỏng, nơi cơ quan điều tra mô tả hành vi đổ thải.
- Giao dịch bên liên quan chiếm 85,5% DT Q3/26 mà nguyên tắc giá không công bố. Nếu DLC trả dưới netback 5%, giá trị còn 48.600.
- 40 tỷ + 100.000 USD tiền gửi đang cầm cố cho khoản vay của "các công ty thành viên", dư nợ bên được bảo đảm không công bố. Nếu mất toàn bộ: −1.700 đ/cp.

## 6. Điều gì làm đổi ý (mốc + tài liệu cần đối chiếu gốc)
| Mốc | Nâng | Hạ | Tài liệu gốc cần đối chiếu |
|---|---|---|---|
| Ngay khi có: tờ trình GD bên liên quan ĐHĐCĐ 12/05 và 14/08/2026 | Có điều khoản giá DLC cố định hoặc không phụ thuộc thuế XK ⇒ T_b/T_c, tối đa +10.000…+20.000 | Giá = giá XK trừ thuế, chi phí ⇒ T_a chắc chắn (55.000 nếu thuế 15%) | Tài liệu ĐHĐCĐ trên HNX/website PAT; NQ 02/2026/NQ-ĐHCĐ |
| 15/01/2027: tờ khai XK 01/2027, văn bản thuế | Thuế 15% bị hoãn hoặc giảm (83.700) | — | Phụ lục I NĐ 199/2025 bản gốc trên công báo; dự thảo NĐ 29/01/2026 |
| Cuối 01/2027: BCTC Q4/2026 | NVL/DT ≤ 50% ⇒ nghiêng O2/O1 | NVL/DT ≥ 55% thêm 1 quý ⇒ nghiêng O3 | BCTC Q4/26: TM chi phí theo yếu tố, TM30 |
| Cuối 04/2027: BCTC Q1/2027 (quý đầu tiên chịu thuế 15%) | DT TP/quý không giảm so Q4/26 dù XK giảm ⇒ T_b/T_c | Giá thực hiện ngầm định giảm ~5,6% đồng loạt cả hai kênh ⇒ T_a | TM doanh thu theo địa lý, TM30 bán cho DLC, thuế XNK phát sinh |
| 31/05/2027 (Bobby F7) | Có quyết định dùng 3,53 tr t quặng tồn; 3 nhà máy VAPC ≥ 80% công suất ⇒ B đúng | Không có cả hai ⇒ P(O3) tăng | Báo Lào Cai, Bộ Công Thương, quyết định UBND tỉnh |
| 01/2027 trở đi: giấy phép KT25 / kết luận điều tra | Gia hạn hoặc mỏ chạy lại ⇒ A đúng | Không gia hạn ⇒ A sai | CBTT DGC; quyết định của Bộ NN&MT |
| 14/05 và 12/11/2027 (Bobby F1/F2) | P4 TQ > 32.000 | P4 TQ < 23.000 và giá thực hiện PAT đi theo | sunsirs; DT/sản lượng nếu PAT công bố |
| BCTN 2025/2026 | Sản lượng (tấn) ⇒ đo được giá/t và NVL/t, đóng mâu thuẫn ±7pp | — | BCTN PAT (HNX 22/04/2026) |

Định mức cốc, quặng và điện riêng của PAT chưa tìm được. Nguồn nên tìm là ĐTM dự án P4 của PAT tại Tằng Loỏng.

## 7. Thanh khoản (mô tả riêng, không trừ vào tâm)
Giữ nguyên bản gốc §9: khối lượng trung vị khoảng 9.300 cp/phiên. Với mức tham gia 10% khối lượng phiên, thoát 50.000 cp mất khoảng 54 phiên. Chiết khấu minh hoạ chỉ tính phần thời gian là 1,5%. Không áp vào tâm.

## 8. Điểm kém chắc nhất (xếp hạng)
1. **Nút T, tức giá DLC trả sau 01/01/2027.** Đây là nút lớn nhất và chưa có văn bản. Xác suất 0,65/0,25/0,10 dựa trên lập luận kinh tế và quản trị, không dựa trên điều khoản hợp đồng.
2. **Nút P, tức truyền dẫn giá TQ sang PAT.** Truyền dẫn chưa xác lập được. Biên độ ±6,3% dựa trên một cặp quan sát 2025/2026, với giả định sản lượng phẳng. Đòn bẩy rất lớn: ±5% giá tương đương ±38% giá trị.
3. **Nút O.** Hai đầu vào đều mang tính phán đoán: P(A) = 0,5 trung tính, và quy tắc chia đều xác suất cho ca "đúng một nguyên nhân được giải".
4. **Giá/tấn và NVL/tấn 2026 không xác định được trong ±7pp.** Chưa có sản lượng.
