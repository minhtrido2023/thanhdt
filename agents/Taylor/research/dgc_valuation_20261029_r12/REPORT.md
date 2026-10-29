# DGC định giá — VÒNG 12 (29/10/2026, job Taylor_20261029_134234) — áp ERRATA r11 (phản biện vòng 5)

## Kết luận (12 dòng)
1. Tái lập r10/r11 khớp 7/7 file `out_r11_*.csv` (cmp từng byte); A7 32.182 / B7 37.060 giữ làm dải chính. Nhãn **P1 giữ**. Không chọn base case.
2. Trọng số kịch bản dùng mọi nơi: **w = thuận 0,2 / cơ sở 0,5 / nghịch 0,3** — do nhóm tự đặt, chủ quan (model.py CFG_A).
3. **Nghi Sơn RÒNG trong A7 = −447 đ/cp** (gộp +2.163 trừ capex còn lại 2.610; theo kịch bản +1.586 / −406 / −1.870). "+2.163 (6,6% giá)" chỉ là số GỘP.
4. Chênh với NPV độc lập giữa (+2.524) là do **phương pháp**: model = NPAT ổn định × P/E 7 / 1,149² (−306); DCF = FCF 15 năm (NPAT + KH 160 − duy tu 36). Bước lớn nhất +2.006 là cộng lại KH−duy tu (`out_r12_A3_pe_vs_dcf.csv`).
5. Đưa NPAT từ dưới lên 107/135/217 vào kịch bản cơ sở của model ⇒ Nghi Sơn ròng cơ sở **+483** (khớp người phản biện).
6. DCF độc lập giữa: thêm VLĐ 15% doanh thu [UL] **2.215** (không thu hồi 2.160, tức −364); thuế ưu đãi theo legal-vn (0% 2027–30, 5% 2031–39, 10% 2040–41; **chưa xác minh điều kiện**) 3.157, kèm VLĐ 2.848. Chỉ là ĐỘ NHẠY theo giá [UL].
7. Điện sản xuất 110kV (QĐ 1279/QĐ-BCT 09/05/2025): bình thường 1.811 / thấp điểm 1.146 / cao điểm 3.266 đ/kWh; phụ tải phẳng ~1.905 [UL khung giờ]. Kịch bản thấp EBITDA 2030 **đổi dấu −22 → +11** (+19 ở 1.811); NPV thấp vẫn âm (−3.037).
8. Ca(OCl)2 [UL]: r11 giữa 15 tr/t = 23,8% doanh thu 2030; giá chào B2B quốc tế 65–70% là 900–1.200 USD/t (23,7–31,6 tr/t, chỉ snippet). Không tìm được giá "clorua vôi" ⇒ sản phẩm thật **chưa xác minh**; độ nhạy NPV giữa 1.183 (5 tr/t) … 4.741 (31,6 tr/t).
9. **Phần C — câu "không DN nào ở VN chi ≥100 tỷ/quý cho môi trường" bị bác về dữ kiện:** TKV chi BVMT 1.160 tỷ năm 2021, "hơn 1.000 tỷ/năm" (nhandan.vn 21/08/2022).
10. Nhưng **quy mô TƯƠNG ĐỐI ủng hộ trực giác**: TKV 1.160/138.813 = 0,84% doanh thu (1,02% trên DT thuần); DGC 400/9.346 = 4,28% (≈ 4–5× TKV), = 75% BH+QLDN quy năm (530), = 22% LNST quy năm. Hai định nghĩa "chi BVMT" không cùng phạm vi.
11. Hữu hạn hay lặp vĩnh viễn: **vẫn chưa phân định**, bằng chứng hai chiều. Phép kiểm vật lý không làm được (không tìm được đơn giá xử lý thạch cao; chỉ có quy đổi 200 tỷ / ~3 triệu t tồn = ~67.000 đ/t).
12. Cổ tức đã trả 9T **4.213 tỷ** (LCTT); đợt 8.000 đ/cp ngày 25/09 = 3.038 tỷ. Tiền ròng 8.370 = 1,99× mức đã chi 9T. Không dự báo cổ tức mới.

---

## A. Nghi Sơn trên một cơ sở ròng (`out_r12_A1_ns_net_in_A7.csv`)

| Kịch bản | w | NPAT ổn định (model) | P/E | Gộp đ/cp | Capex còn lại | **Ròng** |
|---|---|---|---|---|---|---|
| Thuận | 0,2 | 280 | 8 | 4.196 | −2.610 | **+1.586** |
| Cơ sở | 0,5 | 165 | 7 | 2.204 | −2.610 | **−406** |
| Nghịch | 0,3 | 70 | 6 | 740 | −2.610 | **−1.870** |
| TB gia quyền (w 0,2/0,5/0,3) | | | | 2.163 | −2.610 | **−447** |

- "Gộp" đo bằng cách đặt LN Nghi Sơn = 0 trong mọi dòng của model (gồm ns_np 2027–28), giữ trừ capex còn lại.
- Capex còn lại 991,2 = 2.400 − XDCB 1.408,8 (note 11 BCTC Q3/2026).
- Cách đọc: model đang định giá phần còn lại của dự án **thấp hơn** số tiền còn phải chi.

### A3. Cầu nối P/E-trên-NPAT ↔ DCF FCF (kịch bản giữa, đ/cp, đã trừ capex còn lại)

| Bước | đ/cp | Δ |
|---|---|---|
| 1 model.py:328: 165 × P/E 7 / 1,149² − capex | −306 | |
| 2 NPAT 165 → 217 (từ dưới lên 2030, thuế 20%) | 420 | +726 |
| 3 DCF 15 năm trên NPAT (không cộng KH) | 518 | +98 |
| 4 DCF FCF = NPAT + KH 160 − duy tu 36 (= r11) | 2.524 | **+2.006** |
| 5 + VLĐ 15% doanh thu [UL], thu hồi cuối 2041 | 2.215 | −309 |
| 6 VLĐ không thu hồi | 2.160 | −55 |
| 7 bước 5 + thuế lịch ưu đãi (chưa xác minh) | 2.848 | +688 |

- P/E 7 trên NPAT ≈ suất 14,3%, gần ke 14,9%, nhưng bỏ qua phần KH vượt duy tu (124 tỷ/năm) và chiết khấu thêm 2 năm.
- Phương pháp nào đúng hơn phụ thuộc duy tu thực (1,5% capex là [UL]; 72 tỷ/năm ⇒ 1.941). Không đổi model; ghi cả hai.

### A2. Độ nhạy DCF độc lập (`out_r12_A2_dcf_variants.csv`, đ/cp)

| | Thấp | Giữa | Cao |
|---|---|---|---|
| r11 thuế 20% | −3.245 | 2.524 | 6.781 |
| + VLĐ 15% | −3.409 | 2.215 | 6.279 |
| thuế ưu đãi (chưa xác minh) | −3.245 | 3.157 | 8.330 |
| thuế ưu đãi + VLĐ 15% | −3.409 | 2.848 | 7.829 |
| điện 110kV phụ tải phẳng ~1.905 | −3.037 | 2.766 | 6.906 |
| EBITDA 2030 (r11 → điện 1.905) | −22 → 11 | 431 → 451 | 758 → 768 |

### Ghi chú nguồn
- **Vốn:** 2.400 tỷ cho "giai đoạn 1, 30 ha, 151.000 t" (VietnamFinance 17/07/2026; gốc nhadautu.vn 13/06/2020, 136.000 t). 2.900 tỷ: "tổng mức đầu tư của dự án được nâng từ 2.400 tỷ đồng lên 2.900 tỷ đồng", Dự án số 1 mở rộng thêm giai đoạn 2 (75.500 t, từ Q4/2027) (Thời báo Tài chính VN 17/09/2025). **Chưa ngã ngũ**; NQ 34 không ghi vốn. Model dùng 2.400; nếu 2.900 cho cùng phạm vi thì capex còn lại thêm 500 tỷ ≈ −1.317 đ/cp.
- **Bố cục tổ hợp (KB 23/07):** "chưa xác minh" (hai bài báo mâu thuẫn, không có văn bản gốc). Thay cho chữ "KB 23/07 sai" ở r11.
- **Ca(OCl)2 vs clorua vôi:** NQ 34 ghi "Ca(OCl)2 20.000 t". Clorua vôi (30–35% clo hoạt tính) và Ca(OCl)2 65–70% là hai cấp sản phẩm (bằng chứng gián tiếp, snippet). DGC sản xuất cấp nào: chưa xác minh.

## B. Động lực giá trị, Δ so với A7 = 32.182 (`out_r12_B_tornado.csv`; KHÔNG xếp hạng)

| Động lực | Đầu thấp (định nghĩa) | Δ thấp | Đầu cao (định nghĩa) | Δ cao |
|---|---|---|---|---|
| Biên gộp 2027-28 | nền r4 16,5/17,5%, Q4 ex-dự phòng | +217 | nền R2 19,5/20,7%, giá vốn phẳng | +4.698 |
| Nguồn quặng | A7: không mở lại khai trường | 0 | B7: mở lại | +4.878 |
| Tiền ròng × haircut pháp lý | 29% ở cả 3 kịch bản | −3.241 | 3% ở cả 3 kịch bản | +2.302 |
| Nghi Sơn GĐ1 | P&L "thấp" từ dưới lên cho cả 3 kịch bản | −3.742 | P&L "cao" cho cả 3 kịch bản | +5.364 |
| Dự phòng hữu hạn (nền r4) | +100 tỷ/quý × 4 quý | −743 | không trích thêm | +217 |
| Dự phòng lặp vĩnh viễn — độ nhạy phụ | nền r4 + lặp vĩnh viễn (ô thấp nhất 26.117; 26,1–26,6k) | −6.065 | A7 | 0 |
| (đối xứng) lặp vĩnh viễn nền R2 | R1 = 30.598 | −1.584 | R2 36.880 | +4.698 |
| Pháp lý: phạt/khắc phục/đình chỉ | không định lượng | | | |

- Đầu mút Nghi Sơn áp CÙNG một P&L cho cả 3 kịch bản (khác r11 dòng (4) là trung bình gia quyền ở thuế 0%).
- Đầu thấp "LN=0" của r11 (−2.163) không phải đáy, vì kịch bản thấp lỗ.

## C. "100 tỷ/quý chi môi trường" — quy mô tương đối (`out_r12_C_relative_scale.csv`)

**Tiền lệ tuyệt đối có tồn tại** (câu tuyệt đối của user bị bác về dữ kiện):
- TKV: "Hằng năm, TKV dành ra hơn 1.000 tỷ đồng đầu tư cho công tác bảo vệ môi trường", "riêng năm 2021 chi 1.160 tỷ đồng (vùng Quảng Ninh là 1.076 tỷ đồng)" (nhandan.vn 21/08/2022, đọc bài gốc).
- moit.gov.vn: "Tổng chi phí trực tiếp cho công tác bảo vệ môi trường của Tập đoàn hiện nay trên 1.000 tỷ đồng/năm" (ngày trang 29/01/2017, chưa chắc là ngày gốc).
- Bài cand.vn mà người phản biện dẫn: nhóm **không mở được**; số 1.200–1.400 tỷ, phí BVMT ~1.000 tỷ, thuế BVMT ~1.500 tỷ: **không tìm được nguồn** ⇒ không dùng.
- Vedan ~220 tỷ, Formosa 500 triệu USD: tiền lệ xử lý MỘT LẦN, không phải chi thường xuyên.

**Quy mô tương đối:**

| | Tỷ lệ |
|---|---|
| TKV 2021: 1.160 / tổng doanh thu toàn Tập đoàn 138.813 (qua tìm kiếm, 2 báo) | 0,84% |
| TKV 2021: 1.160 / doanh thu thuần hợp nhất 113.173 (viettimes, qua tìm kiếm) | 1,02% |
| DGC: 400 / doanh thu 9T quy năm 9.346 | 4,28% |
| DGC: 400 / giá vốn quy năm 7.411 | 5,40% |
| DGC: 400 / BH+QLDN quy năm 530 | 75% |
| DGC: 400 / LNST hợp nhất quy năm 1.826 | 22% |

- Cường độ DGC ≈ 4,2–5,1× TKV (TKV là ngành than, mỏ lộ thiên, khác ngành; "chi BVMT" của TKV có thể gồm đầu tư).
- Trực giác user về quy mô tương đối **có bằng chứng ủng hộ** (cao bất thường so với tiền lệ lớn nhất tìm được); không chứng minh được "không thể".

**Đối xứng (ERRATA r10 §1):** nghiêng hữu hạn = nhãn "restoration" + ĐHĐCĐ 13/08 mô tả "trích lập dự phòng 100 tỷ để xử lý môi trường"; nghiêng lặp = note 19 "arising from production and business activities" + sổ đã có 200 tỷ (gấp đôi mức ĐHĐCĐ mô tả) sau 2 quý liên tiếp. **Chưa phân định.**

**Ký quỹ cải tạo mỏ:** không tìm được số của Apatit Việt Nam (số 11,1 / 2,1 tỷ trên mạng là của công ty khác). Ký quỹ là tài sản, không phải chi phí. Nhóm **không mở được** nguồn "~3 tỷ cho 2007–09" mà người phản biện dẫn ⇒ không trích.

**Phép kiểm vật lý:** không làm được. Có khối lượng (baolaocai.vn 12/12/2021: thạch cao Đức Giang Lào Cai >600.000 t/năm, tồn ~3 triệu t), không tìm được đơn giá xử lý (đ/t). Quy đổi đơn thuần: 200 tỷ / 3 triệu t ≈ 67.000 đ/t; 400 tỷ/năm / 600.000 t ≈ 667.000 đ/t — không có mốc so sánh.

**Đã bỏ khỏi r11:** câu "không có tiền lệ ≥100 tỷ/quý"; câu "HĐQT lập phương án xử lý toàn bộ chất thải rắn tồn đọng" (chưa xác minh). "Hàng triệu tấn" = cáo buộc của Cơ quan CSĐT Bộ Công an (vneconomy 17/03/2026), chưa phải kết luận của tòa.

## D. Cổ tức (`out_r12_D_dividend.csv`)
- Cổ tức đã trả 9T: 4.213,0 tỷ (LCTT; MIKE_EXTRACT_BCTC_Q3_2026.md:43). Đợt 25/09: 8.000 đ/cp = 3.038 tỷ; phần trước đó 1.175.
- Tiền ròng 30/09: 8.370 (22.040 đ/cp) = 1,99× mức đã chi 9T; LNST hợp nhất 9T 1.369,4. Không dự báo cổ tức mới.

## Dải (giữ r10 + biến thể)
| Trường hợp | A7 | B7 |
|---|---|---|
| r10 (dải chính) | 32.182 | 37.060 |
| LN Nghi Sơn = 0 | 30.019 | 34.896 |
| r11 từ dưới lên thuế 20% | 32.690 | 37.569 |
| Ô thấp nhất: nền r4 + lặp vĩnh viễn | 26,1–26,6k | |
| Ô cao nhất: R2 không trích thêm | 36.880 | 41.757 |

## Chưa làm được (không bịa)
Đơn giá xử lý thạch cao; giá clorua vôi; ký quỹ cải tạo mỏ Apatit; văn bản gốc vốn 2.400/2.900; khung giờ điện văn bản gốc; QĐ giá điện mới hơn 1279 (chưa kiểm); bài cand.vn TKV.

Tái lập: `/home/trido/thanhdt/wc_venv/bin/python r12_calc.py` → `run_stdout_r12.txt` + `out_r12_*.csv` (assert A7/B7, −447, NPV r11).
