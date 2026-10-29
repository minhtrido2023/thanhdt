# DGC định giá — VÒNG 11 (29/10/2026, job Taylor_20261029_131656) — tái cân bằng: Nghi Sơn + xếp hạng động lực + kiểm nhận định "100 tỷ/quý"

## Kết luận (đọc trước)
1. **Tái lập r10 khớp:** A7 32.182 / B7 37.060 (`r11_calc.py` assert). Nhãn **P1 giữ nguyên**. Không chọn base case.
2. **Mâu thuẫn 151.000 t đã giải được bằng văn bản gốc.** NQ HĐQT 34/2026 (15/10) nói rõ: Dự án số 1 = 151.000 t/năm (xút 50k, HCl 15k, PAC 30k, hợp chất Cl 46k, H3PO3 10k). NQ chỉ cho phép đổi dòng H3PO3 thành rổ H3PO3/H3PO4/PCl3/PCl5 (tối đa 10.000 t quy H3PO3) và thêm 75.000 t HCl 31% phụ phẩm. Con số "150k xút / 150k PVC" là của cả tổ hợp 3 GĐ, không phải GĐ1. Tổ hợp: GĐ2 PVC ~6.000 tỷ, GĐ3 soda 400k t ~3.600 tỷ (VietnamFinance 17/07/2026). Chưa thấy quyết định đầu tư GĐ2-3.
3. **Nghi Sơn GĐ1 đã nằm trong A7: +2.163 đ/cp (6,6% giá 32.900).** Theo kịch bản: thuận 4.196 / cơ sở 2.204 / nghịch 740. A7 cũng đã trừ capex còn lại 991 tỷ (= 2.610 đ/cp).
4. **Dựng từ dưới lên, thuế 20%, NPAT 2030 (tải 70/85/90%):** thấp −182 tỷ, giữa 217, cao 479. Model r10 dùng 70 / 165 / 280. NPV dự án tính từ hôm nay, đã trừ capex còn lại: **−3.245 / +2.524 / +6.781 đ/cp**.
   Đối chiếu comp: doanh thu × biên ròng CSV 2021-25 (9,7–16,8%) cho 2030 = 104–180 tỷ ở kịch bản giữa. Số 165 của r10 nằm trong khoảng này. Kịch bản giữa từ dưới lên (217) cao hơn biên tốt nhất CSV.
5. **Phần D:** thay ns_np bằng số từ dưới lên ⇒ A7 32.690 / B7 37.569 (+508). Nếu thuế 0% [UL]: 33.474 / 38.351.
   Chênh lệch này nhỏ hơn độ bất định của giá bán [UL], nên **tôi KHÔNG đổi giả định chính**. r10 giữ làm dải chính, r11 là biến thể.
6. **Xếp hạng động lực (biên độ đ/cp):**

   | # | Động lực | Biên độ đ/cp | Độ chắc của bằng chứng |
   |---|---|---|---|
   | 1 | Dự phòng lặp vĩnh viễn | 6.065 | **yếu nhất** |
   | 2 | Tiền ròng × haircut pháp lý | 5.731 | |
   | 3 | Nguồn quặng | 4.878 | |
   | 4 | Biên gộp 2027-28 | 4.481 | |
   | 5 | Nghi Sơn (trong model) | 3.455 | |
   | 6 | Dự phòng 100 × 4 quý | 960 | |

7. **Nhận định "không thể có 100 tỷ/quý" — bằng chứng ủng hộ MỘT PHẦN.**
   - Ủng hộ: không tìm được tiền lệ nào ở VN có chi phí môi trường THƯỜNG XUYÊN ≥100 tỷ/quý. 400 tỷ/năm ≈ toàn bộ BH+QLDN 9T của DGC (397,4).
   - Không ủng hộ: khoản xử lý MỘT LẦN ≥100 tỷ có tiền lệ (Vedan ~220 tỷ; Formosa ~11.500 tỷ). DGC đang có cáo buộc đổ thải "hàng triệu tấn" ở Tằng Loỏng, và HĐQT nói sẽ lập phương án xử lý toàn bộ chất thải rắn tồn đọng.
   - Kết luận: "lặp vĩnh viễn như chi phí vận hành" là giả định **không có tiền lệ quan sát được**. Câu tuyệt đối "không thể có ở bất kỳ DN nào" thì **chưa chứng minh được**. Số liệu chi môi trường thường niên của các DN cùng ngành: **không tìm được**.
8. **Đề xuất trình bày:** dự phòng chuyển sang độ nhạy phụ (giữ đủ số). Trục chính = biên gộp, nguồn quặng, tiền/pháp lý, Nghi Sơn.

---

## A. Kinh tế dự án Nghi Sơn

### A1. Dự án thật sự gồm gì
**Nguồn gốc.** NQ 34/2026/NQ-HĐQT ngày 15/10/2026, đọc nguyên văn ảnh PDF `/tmp/dgcpdf/20261015-...pdf`, trang 2-3.

**GCN đầu tư 6236772834, thay đổi lần 01 ngày 06/12/2022: 151.000 t/năm.**

| Sản phẩm | Công suất (t/năm) | Ghi chú |
|---|---|---|
| NaOH (quy 100%) | 50.000 | |
| HCl 31% | 15.000 | |
| PAC | 30.000 | quy 32% Al2O3 |
| Hợp chất chứa Cl | 46.000 | gồm: Javen 30.000 (10.000 từ dây chuyền javen + 20.000 phụ phẩm từ bột tẩy), Ca(OCl)2 20.000, Clo lỏng 5.000, Chloramin B 1.000, CaCl2 10.000 |
| H3PO3 | 10.000 | |

**Điều chỉnh 1.** Dòng H3PO3 thành rổ H3PO3/H3PO4/PCl3/PCl5, tổng ≤10.000 t quy 100% H3PO3. Công suất lớn nhất từng sản phẩm: H3PO3 10.000, PCl3 17.500, PCl5 25.000. Kèm 75.000 t HCl 31% phụ phẩm. Lý do theo NQ: "nhu cầu thị trường rất lớn"; PCl3/PCl5 là sản phẩm trung gian của H3PO3; không đổi quy mô thiết bị.

**Điều chỉnh 3 (tiến độ).**
- Lắp đặt và chạy thử Q4/2026.
- Vận hành phân xưởng Xút và PAC Q4/2026.
- **Vận hành toàn bộ Q1/2027.**
- Lịch cũ (QĐ 3738/QĐ-UBND 17/09/2024): hoàn thành Q1/2026.

**Giải mâu thuẫn với KB 23/07.** Hai nguồn **khớp** nhau: 151.000 t là GĐ1/Dự án số 1. KB 23/07 sai ở chỗ liệt kê "150k NaOH + 150k PVC" là sản phẩm của tổ hợp; nguồn báo chí 17/07/2026 lại cho GĐ2 = PVC và GĐ3 = soda 400k t.

**Vốn — còn mâu thuẫn chưa đóng.**
- 2.400 tỷ cho GĐ1 (VietnamFinance 17/07/2026; model.py).
- 2.900 tỷ cho Dự án số 1 (Thời báo Tài chính VN 17/09/2025). Bài này nói Dự án số 1 có thêm "giai đoạn 2" riêng 75.500 t: K2SO4 20k, H2O2 15k, hóa chất tinh khiết 500 t, ắc quy 2 triệu kWh, vận hành từ Q4/2027.
- Đọc nhất quán nhất: 2.400 = phần 151.000 t; 2.900 = cả Dự án số 1 gồm phần 75.500 t. Đây là **[UL]**, chưa thấy văn bản gốc xác nhận.
- r11 dùng 2.400 cho GĐ1. XDCB Nghi Sơn 30/09 = 1.408,8 (note 11 BCTC Q3) ⇒ còn lại 991,2.

**Chưa giải được.**
- 75.000 t HCl 31% phụ phẩm lớn hơn số tôi tính theo tỷ lượng thủy phân PCl3 cho 10.000 t H3PO3 (~43.000 t HCl 31%). Có thể khác quy trình hoặc cách tính; không ảnh hưởng đáng kể vì HCl giá thấp.
- Chưa có bằng chứng đã chạy thử tới 29/10.

### A2. P&L GĐ1 dựng từ dưới lên (`out_r11_A2_nghison_pnl.csv`, `out_r11_A2_nghison_value.csv`)

**Công thức:** công suất NQ 34 × tải × giá − điện + muối (2.400 kWh/t NaOH [UL] × giá điện 2.300/2.100/2.000 đ/kWh [UL; giá bán lẻ BQ 2.204 đ/kWh, Lao Động/VietnamFinance]; muối 1,6 t/t [UL]) − vật tư khác cho dẫn xuất (45/35/25% doanh thu dẫn xuất [UL]) − P4 cho H3PO3 − chi phí cố định (200/150/130 tỷ [UL]) − KH 2.400/15 = 160 − thuế 20% (0% nếu được miễn ưu đãi KKT [UL, chưa xác minh]).

**Lãi vay = 0:** dự án tự tài trợ; chi phí cơ hội tiền gửi đã nằm trong model qua tiền giảm.

**Luật vận hành:** dây chuyền P chỉ chạy khi giá H3PO3 ≥ giá cơ hội P4. Tiêu hao 0,378 t P/t H3PO3 (tỷ lượng) × P4 TQ 104,6 tr/t (BQ SunSirs 28/10) = 39,5 tr/t. Tại giá 25/35 tr/t [UL], kịch bản thấp/giữa **không chạy dây chuyền P**; bán P4 thẳng có lợi hơn. Đây là phát hiện mới: giá trị của rổ H3PO3/PCl3 phụ thuộc giá bán thực, mà giá này **không tìm được nguồn**.

**Giá bán.**

| Sản phẩm | Thấp | Giữa | Cao | Nguồn |
|---|---|---|---|---|
| Xút quy 100% (tr/t) | 6,98 | 10,69 | 11,47 | BQ `commodity_prices.caustic_soda` (SunSirs, lỏng 32%, giả định nồng độ [UL]; FX 3.704 VND/CNY [UL]). Thấp = giá TQ nội địa 28/10 (đáy chu kỳ, −37% so đỉnh Q4/2024). Giữa = trung bình 3 năm × 1,15 (chênh nhập khẩu [UL]). Cao = quý cao nhất 3 năm. Đối chiếu: CFR ĐNA Q1/2026 380–400 $/t ≈ 10,0–10,5 tr/t (Tradeasia dẫn Intratec, nguồn thứ cấp). |
| PAC (tr/t) | 5,5 | 6,5 | 7,5 | FOB TQ 240–268 $/t, nguồn yếu |
| HCl, Javen, Ca(OCl)2, Clo lỏng, Chloramin B, CaCl2, H3PO3 | | | | **[UL] toàn bộ**, không tìm được giá có nguồn |

**Kết quả (thuế 20%).**

| | Thấp | Giữa | Cao |
|---|---|---|---|
| Tải 2027/28/29/30 | 40/55/65/70% | 65/70/80/85% (Vietcap 04/09/2026 giả định 65% 2027, 70% 2028 — tiền lệ duy nhất có nguồn) | 70/85/90/90% |
| Doanh thu 2030 | 593 | 1.073 | 1.699 |
| EBITDA 2030 | −22 | 431 | 758 |
| LNST 2027 / 2028 / 2030 | −258 / −220 / −182 | 107 / 135 / 217 | 321 / 439 / 479 |
| ROIC 2030 trên 2.400 | −6,1% | 9,0% | 19,9% |
| Hoàn vốn | >2041 | 2034 | 2031 |
| **NPV từ 29/10/26, đã trừ capex còn lại, 15 năm (đ/cp)** | **−3.245** | **+2.524** | **+6.781** |
| NPV có terminal (đ/cp) | −3.245 | 3.308 | 8.167 |
| % giá 32.900 | −9,9% | 7,7% | 20,6% |

**Cách đọc từng kịch bản.**
- **Thấp:** ở giá xút đáy chu kỳ TQ, chi phí điện + muối cho mỗi tấn NaOH (7,4 tr) **cao hơn giá xút** (6,98 tr). EBITDA âm. Từ 2031 giả định tạm dừng (giá trị vận hành 0). Kịch bản này **khắc nghiệt hơn bằng chứng comp**: CSV vẫn có biên gộp 24,6% ở H1/2026, cùng lúc giá TQ ở đáy. Như vậy giá VN không rơi theo đáy TQ, hoặc rổ sản phẩm của CSV khác. Coi đây là kịch bản stress, không phải comp.
- **Thuế 0%:** giữa 2030 = 271, cao 2030 = 598.
- **Neo cũ để đối chiếu:** BSC 2023 "2.000 tỷ DT / 200 tỷ LN khi đủ tải" (nguồn cũ, qua tóm tắt tìm kiếm). Vietcap 07/11/2025: ~6–8% LNST DGC. KB 23/07: 70/165/280. Doanh thu @100% tải của r11: 1.097 / 1.634 / 1.888 tỷ. Ảnh AI 16/10 ghi 2.363, chưa có nguồn.

**So với model.py.**
- r10 dùng ns_np 2027-28 (−30,50) / (30,110) / (100,200), steady 70 / 165 / 280.
- Từ dưới lên: năm đầu **thấp hơn** model ở thấp và giữa (model chưa phản ánh đủ gánh KH 160 + định phí lúc tải thấp). Steady giữa/cao **cao hơn** model.
- Đối chiếu comp (`out_r11_A2_comp_anchor.csv`) cho 2030 giữa = 104–180, bao trọn 165 của model.
- Kết luận: giả định model **không lệch có hệ thống**. Lệch đến từ cấu trúc chi phí [UL] của tôi, chưa đủ cơ sở để thay.

**Rủi ro chính, theo thứ tự tác động.**
1. Giá xút theo chu kỳ: giá TQ hiện ở đáy 3 năm.
2. Tải thực tế: không tìm được số ramp-up năm đầu của nhà máy hóa chất VN có nguồn.
3. Giá rổ dẫn xuất clo (Ca(OCl)2/Javen ≈ 1/3 doanh thu ở kịch bản giữa) đều [UL].
4. Dây chuyền P có thể không kinh tế ở giá P4 hiện tại.
5. Vượt vốn: 2.400 vs 2.900.
6. Cân bằng clo: 50k NaOH sinh ~44k t Cl2, phải tiêu thụ hết qua dẫn xuất, nếu không phải giảm tải xút.
7. Thuế ưu đãi chưa xác minh.

**GĐ2-3 = tùy chọn dài hạn, KHÔNG vào giá trị cơ sở.** PVC ~6.000 tỷ, soda 400k t ~3.600 tỷ (VietnamFinance 17/07/2026). Không có quyết định đầu tư, nguồn vốn hay tiến độ chính thức. Vốn cần (9.600 tỷ) ≈ 115% tiền ròng hiện tại (8.370). Nếu làm, cổ tức tiền mặt sẽ bị cạnh tranh nguồn tiền. Không định lượng.

### A3. Nghi Sơn đang nằm trong A7/B7 (`out_r11_A3_ns_in_model.csv`)
- Đặt LN Nghi Sơn = 0 nhưng vẫn trừ capex còn lại ⇒ A7 30.019 / B7 34.896. Như vậy **phần LN Nghi Sơn = +2.163 đ/cp** (thuận 4.196 / cơ sở 2.204 / nghịch 740).
- Capex còn lại 991 tỷ = 2.610 đ/cp đã bị trừ ở mọi cột.
- XDCB 1.408,8 đã chi nằm trong tiền ròng thấp hơn. Người đọc thấy Nghi Sơn **đã có trong định giá**, ở mức trung bình gia quyền ~6,6% giá.

## B. Xếp hạng động lực giá trị (`out_r11_B_tornado.csv`; đ/cp)

| Động lực | Thấp ↔ cao | Biên độ | Độ chắc bằng chứng |
|---|---|---|---|
| Dự phòng 100 tỷ/quý lặp **vĩnh viễn** | −6.065 ↔ 0 | 6.065 | **Yếu**: không có tiền lệ thường xuyên quan sát được (phần C) |
| (1) Tiền ròng 8.370 (22.040 đ/cp) × haircut pháp lý 29% ↔ 3% [UL] | −6.392 ↔ −661 | 5.731 | Số dư tiền **chắc** (BCTC 30/09). Haircut [UL] |
| (3) Khai trường 25/19B mở lại (B7) vs không (A7) | 32.182 ↔ 37.060 | 4.878 | Chưa có quyết định mở lại; khai trường 25 tạm dừng phục vụ điều tra |
| (2) Biên gộp 2027-28: nền r4 (16,5/17,5%) ↔ R2 (19,5/20,7%); 1pp ≈ 1.420 | 32.399 ↔ 36.880 | 4.481 | Biên 9T thực 20,7% (chắc). Hướng 2027-28 là [UL] (P4/DAP, lưu huỳnh, NH3) |
| (4) Nghi Sơn GĐ1: LN 0 ↔ r11 cao thuế 0% (trong model) | −2.163 ↔ +1.292 | 3.455 | Công suất chắc (NQ 34). Giá/biên phần lớn [UL]. NPV độc lập −3.245…+6.781 |
| (5) Pháp lý: phạt / khắc phục / đình chỉ | không định lượng | — | Đ.235 phạt pháp nhân 6–40 tỷ **không phải trần**; Đ.82/BLDS 602 không trần; đình chỉ là rủi ro lớn nhất chưa đo |
| Dự phòng: 200 một lần (đã trừ) ↔ thêm 100 × 4 quý | −960 ↔ 0 | 960 | note 19 (200 tới 30/09) |

**Cổ tức tiền mặt.**
- 8.000 đ/cp trả 25/09/2026 (5.000 còn lại 2025 + 3.000 tạm ứng 2026; doanhnhan.baophapluat 13/09, trong model.py). Cổ tức đã trả 9T 4.213 tỷ (LCTT, theo dispatch) − 3.038 (đợt 25/09) ≈ 1.175 tỷ cho đợt trước trong năm.
- Lợi suất trên giá 32.900: phần tạm ứng 2026 = 9,1%; cả đợt 25/09 = 24,3%. Đợt 25/09 gộp phần còn lại của 2025, **không phải mức thường niên**.
- Khả năng chi trả: 3.000 đ/cp/năm ≈ 1.139 tỷ, so với tiền ròng 8.370 và LNST hợp nhất 9T 1.369,4.
- **CBTT 03/09 chưa đọc nguyên văn trong phiên này.** Mức/đợt lấy theo báo chí đã dẫn. Không dự báo cổ tức ngoài sự kiện đã công bố.

**Xếp hạng (không gán xác suất).**
- Theo biên độ: dự phòng-vĩnh-viễn ≈ tiền/pháp lý > quặng ≈ biên > Nghi Sơn > dự phòng hữu hạn.
- Theo độ chắc bằng chứng: chỉ có số dư tiền và công suất Nghi Sơn là "chắc". Mọi động lực khác có ít nhất một tham số [UL].
- Dự phòng-vĩnh-viễn có biên độ lớn nhất nhưng **bằng chứng yếu nhất**. Đây là lý do nó không nên là trục chính.

## C. Kiểm nhận định "không thể có 100 tỷ/quý chi xử lý môi trường"

**Bằng chứng thu thập** (agent web; chi tiết nguồn ở mục Nguồn).

**(i) Chi phí môi trường thường niên.**
- DGC 2022-25: không tìm được. BCTN 2025 không có bản văn bản đọc được trong phiên này.
- DPM, DCM, CSV, BFC, LAS, DDV, DAP, Apatit VN, Supe Lâm Thao, Việt Trì, MSR/TKV: **không tìm được**.
- Núi Pháo: "hàng trăm tỷ" lũy kế tới 2016, không có số năm (baodautu 19/05/2017).

**(ii) Quy mô.** 400 tỷ/năm ≈ toàn bộ BH+QLDN 9T/2026 của DGC (397,4) ≈ 22% LNST hợp nhất 9T quy năm (1.369,4 × 4/3 = 1.826).

**(iii) Bản chất có thể của khoản dự phòng.**

| Khả năng | Bằng chứng ủng hộ | Bằng chứng phản bác / thiếu |
|---|---|---|
| (a) Xử lý chất thải rắn tồn đọng (thạch cao) / bãi thải Tằng Loỏng | ĐHĐCĐ 13/08: "chủ động trích lập dự phòng 100 tỷ để xử lý môi trường"; HĐQT sẽ lập phương án xử lý toàn bộ chất thải rắn tồn đọng (baophapluat/mekongasean 13–15/08); cáo buộc đổ thải "hàng triệu tấn" (vneconomy 17/03) | Không nguồn nào nối trực tiếp khoản 100 tỷ với bãi thải; phương án chưa công bố |
| (b) Cải tạo phục hồi môi trường mỏ / ký quỹ (NĐ 08/2022, TT 57/2024) | Bối cảnh: khai trường 25 tạm dừng, rủi ro gia hạn giấy phép (SHS qua vneconomy) | Không tìm được mức ký quỹ phương án mỏ apatit của DGC; ĐHĐCĐ không nhắc mỏ; công thức ký quỹ chưa đọc nguyên văn |
| (c) Khắc phục hậu quả vụ án | 331 tỷ gia đình ông Huyền nộp, lãnh đạo nói "chưa phải thiệt hại cuối cùng" (viettimes 13/08) | Đó là tiền cá nhân, ngoài BCTC; thuyết minh 36 H1: HĐQT chưa đủ cơ sở ước tính ⇒ **không nối khoản 200 với vụ án như sự thật** (ERRATA §1) |

**Tiền lệ ≥100 tỷ:** chỉ có dạng sự cố/một lần.
- Vedan ~220 tỷ bồi thường (2010-11, RFA).
- Formosa 500 triệu USD (2016).
- Không tìm được tiền lệ ≥100 tỷ/quý ở dạng chi phí thường xuyên.

**Kết luận trung thực.**
- Bằng chứng **ủng hộ** quan điểm "100 tỷ/quý lặp vĩnh viễn là không hợp lý" ở mức: không có tiền lệ quan sát được + lời DGC mô tả mục đích là xử lý tồn đọng. Đó là bằng chứng gián tiếp, và "không tìm được dữ liệu ngành" ≠ "dữ liệu ngành chứng minh thấp".
- Bằng chứng **không ủng hộ** phát biểu tuyệt đối "không thể có 100 tỷ xử lý môi trường ở bất kỳ DN nào": khoản một lần ≥100 tỷ có tiền lệ, và DGC đã tự trích 2 × 100 tỷ trong 2 quý liên tiếp.
- ERRATA §1 vẫn đúng: hữu hạn hay lặp **chưa phân định được** từ văn bản kế toán. Phần C thêm một luận cứ ngoài (thiếu tiền lệ ngành), nhưng luận cứ này không đủ để gọi là đã phân định.

**Đề xuất trình bày lại lưới.** Trục chính = biên gộp (r4↔R2) × nguồn quặng (A7↔B7), cộng một dòng Nghi Sơn. Dự phòng thành **bảng độ nhạy phụ**: một lần (đã trừ) / 1 / 4 / 8 quý / vĩnh viễn (6.065). Mỗi dòng ghi mức bằng chứng: "vĩnh viễn = không có tiền lệ quan sát được"; "hữu hạn = khớp mô tả ĐHĐCĐ, chưa có phương án". Không xóa số nào; ô thấp nhất r4 + vĩnh viễn ≈ 26,1–26,6 nghìn vẫn ở bảng phụ (ERRATA §2).

## D. Dải định giá (`out_r11_D_band.csv`)

| Trường hợp | A7 | B7 |
|---|---|---|
| r10 (giữ làm dải chính) | 32.182 | 37.060 |
| LN Nghi Sơn = 0 | 30.019 | 34.896 |
| r11 từ dưới lên, thuế 20% (biến thể) | 32.690 | 37.569 |
| r11 từ dưới lên, thuế 0% [UL] | 33.474 | 38.351 |

**Waterfall r10 → r11 (thuế 20%, theo kịch bản):** thuận 44.213 → 48.012, cơ sở 33.778 → 34.667, nghịch 21.501 → 19.182. Trung bình gia quyền +508.

Giả định chính **không đổi** (lý do ở A2). P1 giữ.

## Chưa kiểm được (không bịa)
- Giá VN và giá TQ cho HCl, Javen, Ca(OCl)2, clo lỏng, CaCl2, H3PO3, PCl3, PCl5.
- Giá điện 110kV, giá muối.
- Số tải năm đầu của nhà máy hóa chất VN nào.
- Ước tính riêng cho Nghi Sơn của HSC/SSI/MBS/DSC/VND.
- Vốn 2.400 vs 2.900 (văn bản gốc).
- Thuế ưu đãi KKT Nghi Sơn.
- CBTT 03/09 nguyên văn.
- BCTN 2025 trang môi trường.
- Chi phí môi trường thường niên của các DN cùng ngành.
- Mức ký quỹ cải tạo mỏ apatit của DGC.
- HCl phụ phẩm 75k so với tỷ lượng.

## Nguồn
- NQ 34/2026/NQ-HĐQT (PDF ducgiangchem.vn, đọc ảnh).
- BCTC Q3/2026 note 11/19.
- BQ `tav2_bq.commodity_prices` (caustic_soda, yellow_phosphorus; SunSirs; tới 28/10/2026) → `data/bq_caustic_soda_sunsirs_20261029.csv`.
- BQ `ticker_financial` CSV → `data/bq_csv_quarters_20261029.csv`.
- Báo chí: thoibaotaichinhvietnam.vn 17/09/2025; vietnamfinance.vn 17/07/2026; stockbiz.vn (Vietcap 04/09/2026); doanhnhan.baophapluat.vn và mekongasean.vn 13–15/08/2026; viettimes.vn 13/08/2026; vneconomy.vn 17/03/2026; baodautu.vn 19/05/2017; rfa.org (Vedan); vneconomy.vn (Formosa); chemtradeasia.com (xút CFR, PAC — thứ cấp); laodong.vn (giá điện BQ).

Tái lập: `cd` thư mục này && `/home/trido/thanhdt/wc_venv/bin/python r11_calc.py` → `run_stdout_r11.txt` + `out_r11_*.csv`.
