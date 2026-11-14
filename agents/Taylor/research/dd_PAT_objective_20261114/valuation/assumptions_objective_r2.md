# PAT — Giả định ĐÍNH CHÍNH r2 (vòng đính chính duy nhất), MÙ GIÁ — khoá TRƯỚC khi chạy mô hình
Người lập: người định giá độc lập stateless thứ hai (không phải tác giả bản gốc), 14/11/2026. Không tra/đọc giá cổ phiếu, P/E, P/B, vốn hoá, khuyến nghị.
Gốc: `assumptions_objective.md` (md5 4a177526…, KHÔNG sửa). Mọi #n giữ nghĩa bảng §0 bản gốc; bằng chứng MỚI đánh số #R1… ở §0.
Đơn vị: tỷ đồng; 25.000.000 cp. Khung giữ nguyên: V_ngắn/V_dài, r = 13,5% neo lãi huy động 7,4%, thanh khoản mô tả riêng, vụ án = WARNING, dự án mới NPV = 0, moat không thưởng/không trừ.

## 0. Bằng chứng mới dùng trong r2
| # | Nội dung | Nguồn |
|---|---|---|
| #R1 | Doanh thu nước ngoài BCTC là số SAU thuế XK: 9T/26 thuế 51,61 / (487,51 + 51,61) = 9,6% ≈ 10%; FY25 88,63 / (1.738,33 + 88,63) = 4,85% ≈ 5% | F2 §1.2, §1.5 [TỰ TÍNH] |
| #R2 | VN là nước XUẤT RÒNG P4: công suất ~125 kt (5 DN), các DN không thuộc nhóm DGC XK 100%/chủ yếu; DLC tự có lò P4 ~40 kt/năm | F3 §3.1 (VietTimes 18/03/2026); F2 §1.6 (TCCT 16/03/2025) |
| #R3 | Mục đích chính sách thuế XK P4: đẩy chế biến sâu trong nước (P4 dùng nội bộ làm H3PO4/muối không chịu thuế XK) | sector_read §1 (Bobby); F3 §2 (elibook, thứ cấp) |
| #R4 | DLC sở hữu 51% PAT (hưởng 100% lợi ích tại DLC, 51% tại PAT); ĐHĐCĐ bất thường 12/05/2026 thông qua "tờ trình giao dịch với bên liên quan trong năm nay" — nội dung/nguyên tắc giá KHÔNG công bố; BCTC 3 bộ không nêu nguyên tắc giá | F2 §2.1, §2.4; tìm web 14/11/2026 (nhadautu.vn 18/05/2026) — không thấy văn bản gốc |
| #R5 | DGC Q2/2026: DT mảng P4 −6,3%, sản lượng tiêu thụ −19,5% ⇒ giá ngầm định ≈ +16,4% YoY | F3 §3.2 (24hmoney 15/08/2026) [TỰ TÍNH] |
| #R6 | PAT: DT TP 9T/26 / 9T/25 = 1.366,520/1.351,881 = 1,0108; năm 2025 DN nói "giá bán bình quân P4 +9,4%" khi P4 TQ TB 2025 ≈ 2024 (23,1k vs 23,2k) | F2 §1.1, §1.6; F4 §2 |
| #R7 | Lời DN qua báo: Q4/25 "giá thành SX P4 +26%"; Q1/26 "giá bán không biến động nhiều", "giá vốn SX +14% do NVL"; Q2/26 "giá bán tăng"; Q3/26 "sản lượng giảm, NVL tăng" | F1 §2, F2 §1.6 |
| #R8 | Tồn kho TP 30/06 → 30/09/2026: 53,794 → 70,448 (+16,65); NVL 21,049 → 49,738; tỷ lệ giá vốn TP/CPSX Q3/26 = 0,9575 | F2 §1.5; `prelock_inputs.py` |
| #R9 | Lãi tiền gửi 9T/26 = 25,10 tỷ; HTM 553,19 (30/06) / 558,07 (30/09) ⇒ lợi suất ≈ 25,10/(0,75×555,6) = **6,0%/năm** | F1 §2 (png_q326/p29); F4 §1.3 |
| #R10 | 70 tỷ tiền gửi BIDV cầm cố bảo lãnh nghĩa vụ trả tiền điện, có mặt liên tục 01/01/2025 → 01/01/2026 → 30/06 → 30/09/2026 | F2 §5.1–5.3 (TM4/TM6/TM7 cả 3 bộ BCTC) |
| #R11 | Bảo đảm chéo hai chiều trong nhóm: DLC + DGC bảo lãnh vay của PAT tới 400 tỷ mỗi bên; tiền gửi 1.610.000 USD của DLC thế chấp cho vay BIDV của PAT; 30/06/2026 tiền gửi 100 tỷ của DLC bảo đảm vay Vietinbank của PAT. Khoản cầm cố của PAT cho "công ty thành viên" đổi lượng mỗi quý (31/12/25: 3,664 tr USD; 30/06: 100.000 USD; 30/09: 40 tỷ + 100.000 USD); dư nợ Vietinbank của PAT 30/09 = 0; TM15 Q3 ghi 40 tỷ bảo đảm "các khoản vay của Công ty" | F2 §5.1–5.3 |
| #R12 | Hoá học lò P4: Ca3(PO4)2 + 3SiO2 + 5C → 3CaSiO3 + P2 + 5CO ⇒ C tối thiểu = 60/62 = 0,97 t C/t P4; tỷ lệ phối liệu điển hình cốc:cát:quặng = 16:30:100 (khối lượng); điện 12.000–15.000 kWh/t | 911metallurgist "Properties of phosphate rock"; essentialchemicalindustry.org (qua tóm tắt tìm kiếm, trang lỗi chứng chỉ); Springer s12633-019-00171-z (tóm tắt) |
| #R13 | Than cốc sunsirs TB quý (CNY/t): 2023Q1–2026Q3 TB 15 quý = **1.825,5**; TB 2025 = 1.491; H1/26 = 1.541; 9T/26 ≈ 1.704; Q3/26 2.040; T11/26 ≈ 2.108–2.156; đỉnh 2022 2.500–3.300 | `factpack/data/pat_commodity_quarterly.csv`; F4 §3 |
| #R14 | Lưu huỳnh (cùng cú sốc năng lượng/Hormuz 2026) đã rút −44% từ đỉnh T8 (5.197 vs 9.261) | sector_read §1 |
| #R15 | Bobby F5: P(giá điện bình quân EVN 14/11/2027 > 2.159,9) = 0,55; P(≥ +5%) = 0,25; P(< 2.159,9) = 0,10; NĐ 278/2026: không chỉnh nếu tăng < 2% | sector_read §6; F3 §4 |
| #R16 | Thuế XK 15% từ 01/01/2027: bản chép Phụ lục I NĐ 199/2025 xác nhận; NĐ 201/2026 không nhắc P4; có 1 dự thảo NĐ sửa thuế XK (chinhphu.vn 29/01/2026) danh mục chưa đọc được; tiền lệ 2026 đã giảm thuế XK khoáng sản (fluorit) | F3 §2 |
| #R17 | KH 2025: 1.800 tỷ / 18.000 t P4 ⇒ 100 tr đ/t (giá kế hoạch); DT TP FY25 thực 1.855 | F2 §1.6 |
| #R18 | USD/VND 25.725; USD/CNY 6,67 ⇒ 3.857 đ/CNY (13/11/2026) | macro_snapshot |

## 1. Bảng ĐIỂM → QUYẾT ĐỊNH → BẰNG CHỨNG
| Điểm | Bản gốc | Quyết định r2 | Bằng chứng / lý do (kể cả lý do không áp phần còn lại) |
|---|---|---|---|
| 1. Thuế XK 15% "chỉ chạm 35% DT" | Cơ sở: phần bán DLC (65%) không chịu bước 10→15% | **ÁP — thay bằng NÚT T (3 nhánh, §3)**; kỳ vọng tỷ trọng DT chịu bước ≈ 0,75 (×P(15% hiệu lực) 0,90) | Chuẩn TRUNG TÍNH cho giao dịch bên liên quan là **giá giao dịch độc lập**. Ở nước xuất ròng P4 (#R2) có thuế XK, giá độc lập trong nước = **giá XK trừ thuế** (netback): DLC có lò riêng + nhiều DN khác chỉ chờ bán XK ⇒ không có lý do kinh tế để DLC trả cao hơn netback; chính sách thuế XK hoạt động đúng bằng cơ chế này (#R3). Giả định của bản gốc (DLC hấp thụ thuế cho PAT) là chuyển giá trị từ cổ đông kiểm soát sang cổ đông thiểu số — một khoản CỘNG không có bằng chứng, ngược chiều động cơ của bên kiểm soát (#R4) ⇒ gỡ khỏi vị trí "cơ sở", giữ làm nhánh có xác suất. Không áp chiều ngược (DLC trả DƯỚI netback) vào cơ sở: không có bằng chứng ⇒ WARNING + độ nhạy. |
| 1b. Quan sát giá DLC trả PAT Q4/25 → Q1–Q3/26 | — | **KHÔNG XÁC ĐỊNH ĐƯỢC** | Không có sản lượng/đơn giá theo kênh; không có tờ trình GD bên liên quan (#R4); không có giá XK hải quan (đã tìm). Chỉ có tín hiệu YẾU: giá thực hiện quy đổi trước thuế của PAT 9T/26 ≈ +6,7% YoY (#R6, giả định lượng phẳng) trong khi DGC +16% (#R5) ⇒ KHÔNG thấy dấu hiệu DLC trả giá gộp miễn thuế (nếu trả, giá thực hiện PAT phải tăng NHANH hơn thị trường); tương thích với netback, không phân biệt được với "dưới netback". |
| 2. Cây kịch bản | 0,25/0,50/0,25; bất lợi đòi 2 điều kiện đồng thời; thiếu nhánh "quặng chưa giải, giá giữ" | **ÁP — dựng lại cây 4 nút độc lập (O, P, T, TX), 54 lá** (§3) | Lỗi bản gốc: (i) xác suất đồng thời bị nâng ngược chiều tương quan âm mà chính bản gốc nêu; (ii) trạng thái "quặng chưa giải + giá giữ" bị gán giá trị cơ sở; (iii) thuận lợi 0,25 không nối với số Bobby nào. r2: mỗi nút có xác suất neo số Bobby/BCTC; tương quan nêu rõ. |
| 3a. 70 tỷ cầm cố bảo lãnh tiền điện | Cộng mệnh giá | **ÁP: giá trị = PV lãi sau thuế, giảm trừ −45,0** | Bằng chứng nó là tài sản hoạt động bị khoá vĩnh viễn khi còn sản xuất: cầm cố liên tục 7 quý cho nghĩa vụ điện (#R10) — giống vốn lưu động (mô hình giữ ΔVLĐ = 0). Tiền không chia được cho cổ đông; chỉ hưởng lãi 6,0% (#R9) × (1 − 20%) = 4,82%/năm, chiết khấu r 13,5% ⇒ 70 × 4,82%/13,5% = 25,0 ⇒ −45,0. Không trừ toàn bộ 70 (vẫn là tài sản của PAT, sinh lãi thật). |
| 3b. 40 tỷ + 100.000 USD (≈42,6) cầm cố cho vay "Công ty và các công ty thành viên" | Độ nhạy | **KHÔNG giảm trừ; WARNING + độ nhạy** | Bằng chứng bị phong toả TẠM: lượng đổi mỗi quý (#R11) ⇒ hạn mức quay vòng, không phải tiêu dùng; TM15 cùng BCTC ghi khoản 40 tỷ bảo đảm vay "của Công ty"; bảo đảm chéo 2 chiều (DLC/DGC bảo lãnh 800 tỷ và cầm cố tiền gửi DLC cho vay của PAT) ⇒ không có bằng chứng dòng giá trị ròng ra khỏi PAT; không có dấu hiệu vỡ nợ bên được bảo đảm. Áp luật đối xứng: thiếu bằng chứng tổn thất ⇒ không trừ. |
| 3c. 199 BIDV + 130 ACB cầm cố vay của PAT | Bù trừ với vay 67,2 | **Giữ** | Vay đã trừ khỏi tiền ròng; cầm cố cho hạn mức của chính PAT không tiêu dùng tiền. |
| 3d. Quỹ KT-PL trích từ LNST 9T/26 chưa ghi | Không trừ | **ÁP −12,9** (= 6% × 215,713) | #3: chính sách 6% LNST các năm; LN 9T/26 đang nằm trong tiền, sẽ trích sau quyết toán năm. |
| 4. Than cốc dài hạn | Giao ngay 2.108, gọi "trung chu kỳ" (TB 20 quý gồm 2021Q4–2022) | **ÁP: 2028+ = TB 2023Q1–2026Q3 = 1.825**; 2027 giữ giao ngay 2.108 | Lập luận kinh tế, không "nửa đường": (i) cửa sổ 20 quý chứa siêu chu kỳ năng lượng 2021–22 mà bản gốc tự loại ở chỗ khác (P4 dùng chế độ 2023+) ⇒ nhất quán phải loại; (ii) bước tăng 2026 (1.412 → 2.040) trùng cú sốc năng lượng Hormuz từ 28/02/2026 — cú sốc cùng nguồn ở lưu huỳnh ĐÃ rút −44% (#R14); (iii) phía doanh thu cơ sở dùng giá thực hiện TB 9T/26, KHÔNG dùng giá P4 giao ngay p90 ⇒ phía chi phí không được dùng giao ngay dài hạn; (iv) [NỀN] ngành cốc TQ dư công suất, thép TQ đi xuống ⇒ không có cơ sở cho "nền mới cao hơn" 2023+. Không chọn TB 9T/26 (1.704) cho dài hạn vì 9 tháng ngắn hơn một chu kỳ; không giữ 2.108 cho 2027 trở đi vì giá còn đi lên tới T11 (không có bằng chứng đảo chiều trong 12T). Độ nhạy 1.704 / 2.108. |
| 4b. Định mức cốc [NỀN 1,5 t/t] | 1,5 t/t | **ÁP: 1,37 t/t** (hai cách độc lập hội tụ) | #R12: (a) hoá học 0,97 t C/t P4 ÷ ~85% C cố định ÷ hệ số dư ~1,2 = 1,37; (b) phối liệu 16 cốc/100 quặng × 8,5 t quặng/t P4 (quặng ~30% P2O5, thu hồi 90%: 2,29 t P2O5/t P4 ÷ 0,27) = 1,36. Định mức PAT riêng: KHÔNG TÌM ĐƯỢC (đã thử: web VN "định mức than cốc phốt pho vàng ĐTM Lào Cai", web EN). Độ nhạy 1,25 / 1,5. Định mức điện 12.000–15.000 kWh/t (#R12) khớp lập luận DV ≈ điện. |
| 4c. Tỷ trọng cốc/DT | 7,7% DT ở ~1.500 CNY (tính tay, cộng chênh lệch sai cơ sở) | **ÁP công thức**: tỷ trọng = 1,37 × P_CNY/1,13 × 3.857 đ/CNY (#R18) / 100 tr đ/t (#R17) = **4,68e-5 × P_CNY** (≈7,0% ở 1.500) | Sửa lỗi: bản gốc cộng "%Δgiá × tỷ trọng" thay vì "ΔP × hệ số" (nhỏ). Doanh thu/t 100 tr đ là số kế hoạch 2025 duy nhất có công bố; sai số ±10% ⇒ ±0,1–0,3pp NVL. |
| 5. Phép đo giá/tấn qua DV mua ngoài | Dùng làm bằng chứng "giá đi ngang" | **KHÔNG dùng làm số đo giá; KHÔNG chọn phía; bất định vào nút O (O1 có điều kiện 0,5) + nút P + độ nhạy ±7%** | Mâu thuẫn có thật: H1/26 cho −6,6% trái #R7 (Q2 giá tăng); NVL/t H1/26 1,903 < FY25 1,959. Cơ chế giải thích được cả hai: quặng nghèo hơn ⇒ nhiều xỉ ⇒ **kWh/t tăng** ⇒ DV/t tăng ⇒ phép đo hạ thấp cả giá/t lẫn NVL/t [NỀN, chưa định lượng]. Lời DN (#R7, hai kỳ, hai nguồn báo) là bằng chứng trực tiếp chi phí/t tăng ⇒ giữ quy kết GĐ1 = chi phí quặng ở mức H1/26 (tỷ lệ NVL/DT đo TRỰC TIẾP, không qua proxy). Phương pháp thứ hai: sản lượng 2024–2026 KHÔNG TÌM ĐƯỢC (BCTN 2025 không mở được; 2022: 23.488 t, 2023: 18.027 t chỉ có báo); giá XK hải quan KHÔNG TÌM ĐƯỢC; DGC Q2 +16,4% (#R5) chỉ là chuẩn ngành. ⇒ giá/t PAT 2026 **không xác định được** trong ±7%. |
| 6. Sản lượng 2027 | DT 9T quy năm (1.822) + chi phí chế độ Q3 | **KHÔNG ÁP (giữ 1.822)** | Q3/26 lượng BÁN thấp vì tồn kho TP +16,65 tỷ (#R8): sản xuất Q3 theo giá bán = 439,029/0,9575 = 458,5 ⇒ ×4 = 1.834 ≈ 1.822. Tỷ lệ chi phí đã quy theo đơn vị bán (hệ số bán/sản xuất). Đề xuất 1.756 của skeptic dùng lượng bán, không phải nhịp sản xuất ⇒ không áp. |
| 7a. Trộn kỳ DV (Q3) với NVL (H1) | DV 24,13% Q3; khác 6,2% Q3 | **ÁP: DV/DT và khác/DT lấy 9T/26** (25,08% / 5,82%) — cùng khung giá với doanh thu cơ sở 9T/26 | Skeptic bi quan chiều ngược: trộn kỳ làm GPM dài hạn cao ~0,9pp. 9T/26 là cùng kỳ với DT cơ sở. |
| 7b. Giá điện chỉ cộng −2%, bỏ dự báo tăng | ×0,98 | **ÁP kỳ vọng F5**: từ 2027 hệ số điện = 0,98 × (1 + E[Δ]) với E[Δ] = 0,30×3,5% + 0,25×6,0% − 0,10×2,0% = **+2,35%** ⇒ **×1,0030** so mức Q1–Q3/26 | Đối xứng: −2% có văn bản (#15); khả năng tăng có xác suất Bobby khoá trước (#R15) + cơ chế NĐ 278 (chỉ chỉnh khi ≥2%). Nhánh "tăng" 0,55 tách 0,30 (2–5%, điểm đại diện 3,5% = giữa khoảng do văn bản quy định sàn 2% và mốc 5% của Bobby) và 0,25 (≥5%, đại diện 6%). |
| 7c. GĐ2 cả năm 2027 | Cả năm | **ÁP: H1/2027 GĐ2 mọi nhánh; H2/2027 theo nhánh O** | Bobby F7 mốc 31/05/2027 (P quyết định quặng tồn 0,5) là điểm sớm nhất có bằng chứng cho việc giải; không có bằng chứng giải trước đó (quặng Mỏ Cóc 1 chỉ tới hết T11/2026 #11). |
| 7d. Xác suất thuế 15% | Chắc chắn | **ÁP nút TX: 0,90 / giữ 10%: 0,10** | Bobby F6 0,70 lập khi CHƯA đọc phụ lục; F3 đã đọc bản chép (#R16) ⇒ rủi ro còn lại chỉ là sửa đổi trước 01/01/2027: có dự thảo chưa đọc được + tiền lệ 2026 giảm thuế khoáng sản ⇒ 0,10 (không 0: có dự thảo mở; không cao hơn: 7 tuần trước hiệu lực, không nguồn nào nêu P4). |

## 2. Build-up r2 (thay §2.2 bản gốc; phần không nêu = giữ nguyên bản gốc)
- **DT TP cơ sở = 1.822,0** (9T/26 × 4/3; giá & lượng 9T/26). Hàng hoá bỏ qua.
- Tỷ lệ chi phí /DT (đơn vị bán, khung giá 9T/26, TRƯỚC hệ số thuế): **DV = 25,08% × 1,0030 = 25,16%** (2027+); **khác = 5,82%** (cố định, chia cho hệ số lượng).
- **NVL/DT (trước hệ số thuế)**, hệ số cốc k = 4,68e-5/CNY:
  - GĐ2 @2027 (cốc 2.108): 55,20% + k×68 = **55,52%**
  - GĐ1 @2027 (cốc 2.108): 48,64% + k×567 = **51,29%**
  - O1 dài hạn (chi phí quặng 2025, cốc 1.825): 46,60% + k×334 = **48,16%**
  - O2 dài hạn (GĐ1, cốc 1.825): 48,64% + k×284 = **49,97%**
  - O3 dài hạn (GĐ2 vĩnh viễn, cốc 1.825): 55,20% − k×215 = **54,19%**
  - 2027 = ½ GĐ2@2027 + ½ (GĐ1@2027 nếu O1/O2; GĐ2@2027 nếu O3).
- **Hệ số thuế XK** (từ 2027): f = 1 − s_eff × (1 − 0,85/0,90) nếu 15%; f = 1 nếu giữ 10%. Doanh thu × f × p (p = hệ số giá nút P); mọi tỷ lệ chi phí ÷ (f × p) (chi phí/tấn không đổi). DT 9T/26 đã gồm thuế 10% trên MỌI kênh dưới nhánh T_a (netback) — nhất quán với #R1/#R6.
- **CPBH+QLDN** = 3,85% × s_exp × DT + 6,3 + 5 + 17 (giữ bản gốc); s_exp = 0,35 (T_a, T_b), 0,135 (T_c).
- EBIT = DT × GPM − SG&A. FCFE = EBIT × (1 − thuế) × 0,94 (capex = KH 45, ΔVLĐ = 0). Thuế 5% (2027–2030) / 10% (2031–32) / 20% (2033+). Q4/2026 FCFE = 53,844 × 0,95 × 0,94 = 48,1 (giữ). 2027 t = 0,63; 2028+ t = 1,63…; terminal Gordon g 2% tại 6,63.
- **Tiền ròng r2 = 415,407 − 45,0 (70 tỷ khoá, §1-3a) − 12,94 (KT-PL 9T/26) = 357,47.**
- r = 13,5%, g = 2,0% (giữ, lý do bản gốc §4).
- V_ngắn giữ công thức bản gốc (289,9 TTM) — chỉ để đối chiếu D.

## 3. CÂY KỊCH BẢN r2 (4 nút, giả định ĐỘC LẬP; 3×3×3×2 = 54 lá)
**Nút O — chi phí quặng dài hạn (từ 2028).** Hai nguyên nhân của GĐ2 (#10, #11): A = mỏ riêng nhóm DGC (KT25/19B) hoạt động hợp pháp trở lại trước 2028; B = cung quặng nhà nước (VAPC) bình thường hoá trước 2028.
- P(A) = **0,50**: không có bằng chứng nghiêng (ủng hộ: "tạm dừng phục vụ điều tra" là tạm thời theo bản chất, DGC đang làm thủ tục; chống: giấy phép KT25 hết cuối 2026 (#13, 1 nguồn báo), vụ án gồm tội khai thác tài nguyên) ⇒ trung tính.
- P(B) = **0,55**: từ Bobby F7 P(≥80% công suất trước 31/05/2027, 6,5 tháng) = 0,30 ⇒ hazard hằng λ = −ln(0,70)/6,5 = 0,0549/tháng ⇒ tới 01/2028 (14 tháng): 1 − e^(−0,768) = **0,54**; cộng các nguồn mới có bằng chứng (Tam Đỉnh 250 kt đã chạy, Cam Đường Q4/26, KT19 thi công lại 18/09/2026 — F3 §1.1, §1.4) không cộng thêm vì đã nằm trong đánh giá F7 của Bobby ⇒ 0,55 (làm tròn).
- Tương quan A–B: **ρ = 0** (A là tố tụng hình sự; B là GPMB/đất đai/quy hoạch — cơ quan và thủ tục khác nhau; cùng tỉnh nhưng không có bằng chứng liên kết).
- Ánh xạ: cả hai (0,275) ⇒ hết GĐ2; không cái nào (0,225) ⇒ GĐ2 vĩnh viễn; đúng một (0,50) ⇒ chi phí nằm giữa hai chế độ quan sát được, KHÔNG có bằng chứng về đóng góp tương đối ⇒ **chia xác suất đều cho hai đầu mút quan sát được** (không bịa một mức chi phí trung gian).
- Trong "hết GĐ2": về chi phí 2025 (O1) hay dừng ở GĐ1 (O2)? Ủng hộ O1: tỉnh giao tham mưu hỗ trợ giá quặng cho PAT (#12); chống: cáo trạng "khai thác trái phép hàng trăm nghìn tấn" (nguồn quặng rẻ 2025 không lặp lại hợp pháp), chất lượng quặng giảm hằng năm (F3 §1.3) ⇒ trung tính **0,5**.
- ⇒ **P(O1) = 0,1375; P(O2) = 0,3875; P(O3) = 0,475.**

**Nút P — giá thực hiện (từ 2027, nhân doanh thu; chi phí/t giữ).** Truyền dẫn giá TQ → PAT KHÔNG xác lập được (F4 §5: 2024–26 r = −0,57; 2025 PAT +9,4% khi TQ đi ngang; 2026 PAT ≈ +6,7% khi TQ +20%). Biên độ nhánh = **±6,3%** = đảo ngược/lặp lại đúng mức PAT đã thay đổi 2025 → 9T/26 (1/1,067 − 1; #R6 với giả định lượng phẳng) — cặp quan sát thật, không ngoại suy. Xác suất neo Bobby F2 (12T): xuống **0,32** (= P(P4 < 23.000), tức TQ về mức 2025 khi PAT ở mức giá 2025); lên **0,10** (= P(P4 > 32.000)); giữa **0,58**.

**Nút T — giá DLC trả PAT sau 01/01/2027 (tỷ lệ DT chịu bước 10→15%, s_eff).**
- T_a **netback** (giá DLC theo giá XK sau thuế; bước thuế chạm ~100% DT): s_eff = 1,0, **P = 0,65**.
- T_b **giữ cơ cấu giá hiện tại không cập nhật bước thuế** (chỉ phần XK 35% chịu): s_eff = 0,35, **P = 0,25**.
- T_c **DLC bù thuế bằng giá + dồn thêm lượng sang DLC** (XK về tỷ trọng Q3 13,5%): s_eff = 0,135, s_exp = 0,135, **P = 0,10**.
- Cơ sở xác suất: T_a là nhánh DUY NHẤT nhất quán với chuẩn giao dịch độc lập + cấu trúc thị trường xuất ròng (#R2, #R3) + động cơ bên kiểm soát (#R4) + tín hiệu yếu #R6/#R5; T_b/T_c đòi DLC chuyển giá trị cho cổ đông thiểu số — có thể (vd hợp đồng khung năm đã duyệt, quan hệ cung quặng), không có bằng chứng ủng hộ hay bác ⇒ tổng 0,35, T_b > T_c vì T_b chỉ cần "không đàm phán lại" còn T_c cần hành động chủ động có lợi cho PAT. Hợp đồng bên liên quan duyệt theo năm ("trong năm nay", #R4) ⇒ 2027 phải trình lại ⇒ cơ hội đàm phán lại theo netback cao.
- **Điểm kém chắc nhất của toàn bộ r2.** Không xác định được (đã thử): tờ trình GD bên liên quan 12/05 & 14/08/2026, nguyên tắc giá trong BCTC, giá XK hải quan, sản lượng theo kênh.

**Nút TX — thuế 15% hiệu lực 01/01/2027:** 0,90 / giữ 10%: 0,10 (§1-7d).

**Tương quan:** O–P ρ = 0 (VN ~10–15% cung thế giới [NỀN], là price-taker; thiếu quặng VN không đủ đẩy giá TQ — bản gốc tự ghi "thiếu quặng toàn ngành ít làm giá giảm" rồi lại cộng dồn xác suất); O–T ρ = 0; P–T ρ = 0; TX độc lập.

**Tâm = Σ p_lá × V_lá. Cơ sở (một đường) = mọi nút ở giá trị KỲ VỌNG của đầu vào** (NVL dài hạn, NVL 2027, hệ số giá, hệ số thuế). **Vùng = phân vị có trọng số P25–P75 của 54 lá**; báo thêm P10–P90.

## 4. Độ nhạy (khoá danh sách)
r ∈ {12,5; 13,0; 13,5; 14,0; 14,5} × g ∈ {0; 1; 2; 3}% · EBIT dài hạn ×0,8/0,9/1,1/1,2 · s_eff ∈ {0,135; 0,35; 0,75; 1,0} · thuế giữ 10% · giá ±5%/±10% · cốc dài hạn 1.704 / 2.108; định mức 1,25 / 1,5 · NVL dài hạn ±2,75pp · từng nhánh O cố định · P(A) 0,3/0,7 · điện giữ ×0,98 (bỏ F5) · DLC dưới netback −5% trên 65% DT · một lần −50 · mất cầm cố −42,6 · 70 tỷ theo mệnh giá (+45,0).

## 5. Danh sách đính chính
ÁP: (1) nút T thay "35% cố định"; (2) cây 4 nút; (3a) 70 tỷ khoá −45,0; (3d) KT-PL 9T/26 −12,9; (4) cốc dài hạn 1.825; (4b) định mức 1,37; (4c) công thức tỷ trọng cốc; (7a) DV/khác 9T/26; (7b) điện kỳ vọng F5; (7c) GĐ2 chỉ H1/2027; (7d) TX 0,90.
KHÔNG ÁP: (3b) trừ 42,6 cầm cố nhóm (WARNING); (5) chọn phía giá/t (đưa vào nút/độ nhạy); (6) sản lượng 2027 theo nhịp bán Q3; chiết khấu chuyển giá dưới netback (WARNING/độ nhạy); áp giá P4 TQ giao ngay; mở rộng; moat; giải phóng VLĐ; phạt vụ án (WARNING).
