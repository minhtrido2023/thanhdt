# fundamental-skeptic vòng 1 — POW — VERDICT: REFUTED (mức tham số/văn bản; nhãn ĐẮT vẫn đứng), confidence medium, 18/11/2026

Phạm vi: REPORT.md vòng 1 + model/ (calc.py chạy lại ra đúng 8.806) + đối chiếu scan BCTC trong src/ (render pymupdf).
Kết luận một dòng: **số liệu BCTC khớp; nhãn "ĐẮT theo mô hình" đứng vững kể cả khi sửa hết thiên lệch** (cận lạc quan có cơ sở ≈ 9.958 ở r 13,5%,
≈ 11.900 nếu cộng thêm r 11% + E_NT3&4 15.000 — vẫn < 13.250). Nhưng **tâm 8.806 thấp có hệ thống ~13%** vì hai lỗi trái luật user
(g>0 khi ROE<r = "đầu tư mới làm giảm giá trị"; vốn cho dự án mới định giá 0,52× thay vì sổ sách). Tâm/vùng phải tính lại trước khi đóng gói.

## A. Kiểm số liệu — đã xác minh độc lập (render scan)
| Số | REPORT | Nguồn kiểm | Kết quả |
|---|---|---|---|
| Tiền / HTM / phải thu KH / DP khó đòi 30/9 | 10.609,4 / 19.548,3 / 23.964,3 / 355,6 | Q3 HN BCĐKT (tr.2 in) | khớp |
| Vay NH / DH | 19.438,3 / 18.087,1 | Q3 HN tr.3 | khớp |
| VCSH tổng / NCI ⇒ mẹ | 46.376,2 / 3.241,8 ⇒ 43.134,5 | Q3 HN tr.3 | khớp |
| Số cp | 3.067,85 tr | vốn góp 30.678,46 tỷ / 10.000 đ; đầu năm 27.868,2 + 2.810,2 chào bán | khớp |
| DT/LN gộp/LNTT/thuế/LNST mẹ 9T | 49.405,5/8.701,3/7.743,5/768,1+76,8/6.434,5 | Q3 HN KQKD tr.5 | khớp |
| Hồi tố H1 1.103 + 991 + 381 = 2.475,6 | | CBTT 03/08 (post.html) — "tại Công ty mẹ" | khớp |
| Q3 hoàn nhập ~280 | ước lượng | GT-Q3 tr.4: QLDN HN giảm ~290, LN +285 "do hoàn nhập DP phải thu O&M Cà Mau" | hợp lý, nhưng BCĐKT: DP khó đòi chỉ giảm 187,1 cả 9T ⇒ nêu khoảng 187–290 |
| Citi&ING / SMBC | 11.261,9 / 4.035,6 | TM21 (tr. pdf 31) | khớp (Citi&ING đầu năm 9.872 ⇒ còn giải ngân +1.390 trong 9T/26) |
| Giá 17/11, ADV 62 phiên | 13.250 / 63,3 tỷ | BQ `ticker` | khớp |
| calc.py | 8.806; vùng [5.551; 12.060] | chạy lại | khớp |

## B. Các điểm REFUTE (phải sửa)

**B1. g = 2% đi ngược chính lý do của nó và trái luật NPV=0 (load-bearing).** Công thức E×(ROE−g)/(r−g) = cổ tức E(ROE−g) tăng g ⇒ g>0
nghĩa là MỖI NĂM giữ lại g×E tái đầu tư ở ROE di sản 8% < r 13,5% ⇒ phá giá trị vĩnh viễn. Trong khi `g_basis` tự viết "đội máy già … tăng trưởng
mới đến từ dự án mới (NPV=0)". Máy già ⇒ g di sản ≤ 0, và trong khung thặng dư ÂM thì g thấp làm giá trị TĂNG chứ không giảm (calc_output: g 0% ⇒ 9.563,
−2% ⇒ 10.125). Chọn 2% vì tưởng là "thận trọng" là nhầm chiều; về bản chất là gán NPV âm cho tái đầu tư — đúng lỗi luật 20 cấm.
⇒ **Base g = 0** (tâm 9.563), g 2% chuyển thành độ nhạy "tái đầu tư vào mảng di sản ở ROE di sản".

**B2. Vốn đã/sẽ dành cho dự án mới bị định giá ở bội số di sản 0,52× thay vì sổ sách.** E_di sản 33.134 gồm cả XDCB dở dang 1.659,6 (30/9),
phần chưa dùng của 2.810 tỷ chào bán (NQ 19 đổi mục đích) và VCSH mẹ KH 2026 cho dự án 5.049 [NQ 90]. Luật 20: phần đã chi = tài sản theo giá vốn.
Tách 1.660 / 3.000 / 5.000 ra ghi theo sổ: tâm +256 / +463 / +771 đ (tính lại độc lập: 9.062 / 9.269 / 9.577 khi g giữ 2%).
⇒ Tách dòng `e_new_projects_book` trong assumptions (cơ sở: XDCB TM13 + tiền chào bán chưa dùng + giải ngân 9T dự án mới), ghi theo sổ.
Gộp B1+B2 (g 0, 3.000 theo sổ): **tâm ≈ 9.958**, giá = 1,33× tâm (không còn 1,50×).

**B3. Cơ sở ROE di sản 8% không tái lập được như viết và dùng sai mẫu số.** BQ `BVPS × OShares` = VCSH TỔNG gồm NCI (Q3/26: 15.116,9 × 3.067,85 tr =
46.376 = 43.134,5 + 3.241,8). Chuỗi 8,4/7,1/5,5/5,7/3,1/3,2/6,5% là LN mẹ / VCSH tổng ⇒ thấp hơn ROE mẹ ~0,5pp (mẹ, NCI ~2.900: 9,3/7,8/6,1/6,3/3,4/3,5/7,1%,
TB 6,2%). Điều chỉnh vốn XDCB NT3&4 (XDCB 31/12/24 = 19.759 [FY25 BCĐKT]) và cộng lại hồi tố thuộc các năm trước (LN bị dồn sang 2026) cho ~7–8%.
8% chấp nhận được, nhưng REPORT phải ghi phép tính (mẫu số mẹ, vốn XDCB từng năm, phần hồi tố phân bổ ngược), không chỉ ghi "(ước lượng) ≈ 7–8%".

**B4. Bỏ sót tài sản tiềm tàng đã có số (mất cân bằng hai chiều).** FY2025 TM36 [BCTN tr.184-185]: CLTG VA1 "phát sinh đến năm 2025, ước tính 1.596 tỷ",
ghi nhận khi được duyệt; 2026 mới ghi 1.103 (2019-21, EVN mới duyệt một phần 2021: 21,6%) ⇒ còn ~490 tỷ chưa ghi nhận + cùng cơ chế cho NT2/Đakđrinh
+ điều chỉnh TMĐT trong giá điện VA1 khi quyết toán (hai chiều). REPORT chỉ viết "dòng thu ADMIN, lumpy". ⇒ Nêu rõ trong §4/§5/§8 như kịch bản dương có
số của chính DN (~490 × 0,89 / 3.068 ≈ +140 đ/cp), không nhét vào base nếu muốn chặt, nhưng phải có.

**B5. Câu "thị trường coi năm đỉnh El Niño là năm chuẩn" mâu thuẫn với lịch sử chính POW.** El Niño 2023-24 trùng với ROE THẤP NHẤT của POW (3,1–3,2%);
2025 (La Niña theo Bobby) ROE mẹ 7,1%, điều chỉnh vốn XDCB ~10%. Lợi nhuận 2026 đến từ FMP 1.500 vs 1.143, cú sốc năng lượng (Hormuz), NT3&4 vào vận hành
và hồi tố — không chỉ thời tiết. ⇒ Hạ giọng §0 và §8a: "2026 có thể là đỉnh chu kỳ theo cơ chế Bobby, nhưng lịch sử POW không cho thấy El Niño ⇒ ROE cao;
phần cấu trúc (FMP, NĐ 100 Qc, thiếu nguồn 2027-30) chưa tách được" và đưa vào điều kiện đổi nhận định LÊN.

**B6. Lợi nhuận cốt lõi phân bổ sai một phần cho cổ đông thiểu số.** CBTT 03/08 nói ba khoản hồi tố "tại Công ty mẹ" (VA1, CM1&2 là chi nhánh mẹ) ⇒ 100% thuộc mẹ.
calc nhân (LNTT − một lần)×(1−t)×93,3% ⇒ đẩy 6,7% hồi tố sang NCI. Đúng: 6.434,5 − 2.755×(1−10,9%) ≈ **3.980** (một lần 280) … **4.062** (187,1).
REPORT ghi 4.145 ⇒ sửa thành khoảng **~3.980–4.060** (thuế hiệu dụng của khoản hồi tố chưa biết, ghi rõ). Chỉ hiển thị, không đổi tâm; P/E cốt lõi 7,4x → ~7,7x.

**B7. Moat NARROW không có bằng chứng định lượng nhiều chu kỳ.** Chính REPORT: ROE/ROIC < Ke MỌI năm (ROIC5Y 5,0%, ROIC_Min5Y 2,0%). Tiền lệ trong
`data/moat_tags.csv`: QTP NARROW dựa trên "ROIC floor 12–16%"; DRC NONE. Rào cản (giấy phép, vị trí hệ thống) có thật nhưng người mua độc quyền chiếm thặng dư
⇒ không có lợi nhuận siêu ngạch ⇒ bằng chứng nghiêng **NONE (kinh tế)**. Không đổi định giá (NARROW/NONE đều không thưởng/không trừ), nhưng dòng moat_tags đề
xuất phải đổi thành NONE hoặc ghi rõ "NARROW-cấu trúc, NONE-kinh tế: rào cản không chuyển thành ROIC>Ke". Dòng "độ nhạy moat WIDE = ROE 11,5%" thực chất là
kịch bản tốt, không phải giả định moat — ghi lại cho đúng.

**B8. Nhỏ.** (a) "Phải trả cổ tức PVN 728,2 (TM16)" — theo FY2025 TM, 728,2 là LNST từ CLTG VA1 2016-17 (trước CPH) phải nộp PVN, không phải cổ tức; sửa nhãn.
(b) "ROE ~12–13% năm hoá" (§8a): 5.527 / VCSH mẹ CUỐI kỳ; trên VCSH bình quân 9T = 14,3%; trên vốn di sản (NT3&4 ở r) ~12,6% — ghi rõ mẫu số.
(c) E_NT3&4 10.000: cơ sở "TMĐT 32.487 × 30%" yếu hơn bằng chứng sẵn có — FY25 BCĐKT: TSCĐ nguyên giá +24.300 (70.535→94.835), XDCB −18.850 ⇒
chi phí NT3&4 vốn hoá ~23–25 nghìn tỷ − nợ dự án Citi&ING+SMBC 15.298 ⇒ **~8.000–10.000**. Thay cơ sở; độ nhạy 15.000 khó có căn cứ (8.806 không bi quan theo trục này,
nếu có thì hơi lạc quan). (d) Implied ROE tại giá phải tính lại sau B1/B2 (~12,6%).

## C. Đứng vững (không cần sửa)
- **r 13,5%**: đúng luật 21 (lãi huy động hiệu dụng 7,4% = neo 7,4% ⇒ không điều chỉnh); r 11%/12% chỉ là độ nhạy, đúng cách.
- **Số cp 3.067,85 tr**: khớp vốn góp và TM23.
- **Tách 2.755 tỷ một lần**: 2.475,6 có nguồn CBTT; 280 có GT-Q3 đỡ (chỉ cần nêu khoảng 187–290). Không thấy khoản một lần ngược chiều lớn (lãi tỷ giá đánh giá lại 91,4 nhỏ).
- **NT3&4 NPV=0**: đúng luật; Qc 65% có nhưng ToP/giá LNG không có số ⇒ không lệch là đúng.
- **Pháp lý**: không vụ việc; nhấn mạnh kiểm toán (chưa quyết toán CPH) và giao dịch bên liên quan ghi WARNING đúng luật 27/09. Chưa tra UBCKNN trực tiếp — đã tự khai.
- **Comp**: 10 peer, trung vị, nói rõ POW không đắt theo bội số trailing — cân bằng tốt.
- **Thanh khoản**: ADV 63,3 tỷ xác minh; không đề xuất vị thế.
- Không có DD POW trước ⇒ không có đảo chiều nhận định.

## D. Độ nhạy sau sửa (tính lại độc lập, r 13,5%, TK thanh khoản 1%)
| Biến thể | Tâm |
|---|---|
| REPORT hiện tại | 8.806 |
| g 0 | 9.563 |
| g 0 + vốn dự án mới 3.000 theo sổ | **9.958** |
| như trên + E_NT3&4 7.000 | 9.563 |
| như trên nhưng r 11% (chỉ độ nhạy) | 11.267 |
| g 0 + mới 5.000 + r 11% + E_NT3&4 15.000 (cận lạc quan) | 11.884 |
Mọi biến thể < 13.250 ⇒ nhãn ĐẮT theo mô hình đứng; tỷ lệ giá/tâm ~1,33× thay vì 1,50×; mốc 0,85×tâm đổi ~7.485 → ~8.460.

## E. required_change (theo file/mục)
1. `model/assumptions_POW_20261118.json`: `g` 0,02 → 0,0 (base) + sửa `g_basis`; thêm `e_new_projects_book` (cơ sở XDCB TM13 1.659,6 + tiền chào bán chưa dùng + VCSH dự án mới đã giải ngân 9T) và `calc.py` tách khỏi E_di sản, ghi theo sổ; sửa `e_nt34_basis` dùng FY25 TSCĐ/XDCB − nợ dự án; đổi `scenario_basis.base` thành phép tính trên VCSH MẸ. Ghi md5 mới.
2. `model/calc.py` dòng core: core mẹ = LNST mẹ − một lần×(1−t) (không nhân tỷ lệ mẹ 93,3%); khoảng một lần Q3 187,1–280.
3. REPORT §0, §8a, §8b, §8e, §11: tâm/vùng/mốc 0,85×tâm/implied ROE theo số mới; hạ giọng câu "thị trường coi năm đỉnh là chuẩn" (B5).
4. REPORT §3 + §0: LNST mẹ cốt lõi 9T ≈ 3.980–4.060 (B6); Q3 cốt lõi tính lại.
5. REPORT §4/§5/§8: thêm tài sản tiềm tàng CLTG VA1 ~490 tỷ còn lại (TM36 FY2025) + điều chỉnh TMĐT VA1 khi quyết toán (hai chiều) (B4).
6. REPORT §7 + dòng moat_tags đề xuất: NONE (kinh tế) hoặc giải thích NARROW-cấu trúc/NONE-kinh tế; sửa nhãn "độ nhạy moat WIDE" (B7).
7. REPORT §5: sửa nhãn 728,2 (B8a); §8a ghi mẫu số ROE 2026 (B8b); §7 ghi chuỗi ROE trên VCSH mẹ (B3).
8. Phụ lục E: ghi minh bạch đã áp đính chính skeptic vòng 1.
