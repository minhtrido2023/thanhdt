# TV1 (EVNPECC1) — REPORT v9 (nội bộ): định giá nội tại dựng mù + so giá

Job `Taylor_20261102_144349` · 02/11/2026 · NỘI BỘ (chưa qua phản biện; không phải báo cáo NĐT).
Bộ file:
- `INTRINSIC.md`: giai đoạn 1, khoá md5 `0e194156785e2f37eac69436ec8327e2` lúc 21:54:32 ICT (`LOCK.txt`).
- `valuation_blind.py` → `valuation_blind_out.txt`.
- `PRICE_COMPARE.md` + `phase2/compare.py` → `phase2/compare_out.txt`.

Hồ sơ doanh nghiệp, chất lượng lợi nhuận, BCTC, pháp lý giữ nguyên ở `../dd_TV1_20261102/REPORT.md` §2–§7. Bản này thay
§0/§8 của hồ sơ đó cho mục đích định giá.

## 1. Kết luận

- **Giá trị nội tại (mù giá):**
  - tâm **27.800 đ/cp**; trung vị 25.100;
  - dải chính P20–P80 **22.100–35.100**; toàn lưới 16.200–50.000.
  - Cấu phần: thuỷ điện 16.400 + tư vấn 12.300 + tiền ròng −900. Không có xác suất vụ án trong tâm.
- **Giá 19.500** (DNSE 02/11/2026 14:34): thấp hơn tâm 30%, thấp hơn trung vị 22%, thấp hơn P20 12%.
  - P/E TTM 2,8×; P/B 0,91; lợi suất 7,7%.
  - SOTP bằng bội số peer (độc lập với DCF) 21.400–26.800.
- **Thị trường ngầm định một trong ba:**
  - giá PPA ~370 đ/kWh (dưới sàn kinh tế 440–540);
  - tư vấn chỉ đáng 107 tỷ (dưới kịch bản thấp 170);
  - Ke 17,4%.
  Khoảng cách ≈ đúng cú sốc "cấm thầu EVN 3 năm" (−8.600 đ/cp).
- **Thay đổi phương pháp so với các vòng trước:**
  1. Giá PPA suy từ kinh tế và quy định (IRR thực, sàn trên giá trị còn lại), không từ tin đồn.
  2. Tư vấn dựng từ đường ống × định mức × thị phần, không đặt LNST.
  3. Vụ án tách khỏi cơ sở.
  4. Mù giá có khoá md5. Mức nhiễm được khai ở INTRINSIC §0b.

## 2. Thuỷ điện Sông Bung 5 — điểm then chốt

- **IRR dự án thực:**
  - luỹ kế đến 2026: 2,8%;
  - toàn đời ở giá 949: **7,7–8,0%**, thấp hơn trần 12%. Muốn chạm 12% cần giá >3.000 đ/kWh.
  ⇒ Quy định không đòi hạ giá. Nếu hạ, nguồn duy nhất là bậc giá đã ghi trong hợp đồng (dự thảo 2018: 243,66 từ 2022 —
  thực tế chưa áp; điều kiện kích hoạt chưa xác định).
- **Sàn kinh tế** (O&M + sửa chữa + lợi nhuận 8–15% trên RAB 449 tỷ): **398–540 đ/kWh**.
  - Mức 340 thấp hơn hoà vốn kế toán (309 + lợi nhuận ≈ 0).
  - Nếu O&M tính theo định mức TT 12 thì 415.
- **Kịch bản [UL]:** 949 (0,15) / 600 (0,30) / 520 (0,35) / 440 (0,20) ⇒ kỳ vọng 592 đ/kWh.
  Q P50 195 GWh (độ nhạy 175–236,6).
- **DCF 2027–08/2059:** 286–790 tỷ theo kịch bản; kỳ vọng 437 tỷ. Mỗi năm hạ bậc trễ: +1.500–1.850 đ/cp.
- **Điện mặt trời nổi:** IRR 6,8% < Ke ⇒ không tính. Có giá trị dương nếu vốn đầu tư ≤ ~504 tỷ.

## 3. Tư vấn — dựng từ gốc

- **Doanh thu tư vấn:** 318,7 (2023) → 346,2 (2024) → 447,0 (2025); 9T/26 +29%.
- **Biên EBIT sau chi phí chung:** 5,4% → 10,0% → 11–17% (9T/26 lõi).
- **Hợp đồng ký mới 2025:** 835,1 tỷ (book-to-bill 1,87).
- **Định mức TT 38/2026:** thiết kế 2 bước ≈ 1,7–2,0% chi phí xây dựng. Kiểm bằng gói 500kV thật: 1,12–1,13% TMĐT
  ⇒ f = 1,6% TMĐT ⇒ bể phí khối EVN 2025 ~2.000 tỷ ⇒ thị phần TV1 ~22%.
- **Vai trò:** đơn vị thiết kế phía Bắc của EVN. Thiết kế gốc Tuyên Quang, nay làm Tuyên Quang MR (81,7 tỷ, duy nhất dự thầu).
  Nguồn việc nêu tại ĐHCĐ: Sơn La/Lai Châu MR, 500kV AC/HVDC, FS lại NT1, ĐGNK cùng PTSC.
- **Kịch bản:** thấp / giữa / cao = 170 / 328 / 569 tỷ (P 0,30 / 0,50 / 0,20) ⇒ 329 tỷ.
  Giả định: g 5% dài hạn, ΔVLĐ 40%, KTPL 20%, Ke 12,85%. Terminal 58–77% giá trị.

## 4. Bảng cân đối

Tiền ròng thô −38,7 tỷ (đã trừ cổ tức phải trả và lãi vay cá nhân) − KTPL 9T 24,9 + LNST Q4 sau KTPL 40 [UL] = **−23,7 tỷ**.
Nợ tranh chấp 127,63 tỷ đã khấu trừ đủ theo sổ. Số dư quỹ KTPL chưa chi chưa tách được (tối đa −1.130 đ/cp).

## 5. Vụ án — độ nhạy riêng

| Cú sốc | Δ đ/cp |
|---|---|
| Cấm thầu EVN 3 năm, doanh thu tư vấn −50% | −8.600 |
| Cấm 5 năm, −50% | −13.700 |
| Buộc nộp lợi bất chính 20 / 50 / 100 tỷ | −660 / −1.660 / −3.320 |

Bằng chứng xác nhận: cáo trạng nêu pháp nhân; quyết định cấm thầu theo NĐ 214/2025 Đ.133; trích lập ở BCTC kiểm toán FY2026.

## 6. Thị trường có thể chưa tính / đã tính quá tay

Xem INTRINSIC §E và PRICE_COMPARE §4.

**Có thể chưa tính:**
- sàn kinh tế của giá PPA;
- backlog 835 tỷ;
- đòn bẩy hoạt động;
- vị thế thiết kế gốc;
- thiết kế lại là nguồn việc.

**Có thể đã tính quá tay:**
- bậc giá có thật (chính công ty viết "sụt giảm");
- điện mặt trời nổi NPV âm;
- KTPL và payout thấp;
- ADMIN_GATED;
- chất lượng số liệu.

## 7. Mốc kiểm chứng hai chiều

Xem PRICE_COMPARE §5: BCTC Q4/2026 (~30/01/2027), BCTC kiểm toán FY2026 (~03/2027), CBTT/ĐHĐCĐ về phụ lục PPA (~04/2027),
giá ròng/kWh Q1–Q2/2027, tiến độ vụ án, capex EVN 2026/kế hoạch 2027, các gói Sơn La/Lai Châu MR và NT1.

## 8. Giới hạn (trung thực)

- **Xác suất kịch bản là [UL].** Đây là điểm yếu nhất. Phản biện nên thử P(949) = 0 và P(340) > 0.
- **Chưa đọc được văn bản PPA/phụ lục 05** đã ký. Lời lãnh đạo 500–600 qua KBSV chưa kiểm bản gốc.
- **Sản lượng 2018/2019/2020/2024 là suy ra.** IRR nhạy với chúng (7,7% ↔ 8,0%), nhưng kết luận "dưới 12%" vững.
- **Thuế suất thuỷ điện:** giả định 20% suốt đời. Ưu đãi thuế quá khứ (nếu có) làm IRR quá khứ cao hơn chút; không đổi kết luận.
- **Tư vấn:**
  - DT 2026E 520 giả định Q4/26 = Q4/25;
  - biên 11% (kịch bản giữa) phụ thuộc cách đọc khoản hoàn nhập Q3;
  - thị phần ngầm định chưa trừ khách ngoài EVN;
  - số EVN 2026–2030 có hai nguồn mâu thuẫn (830k so với ~5 tỷ USD/năm).
- **Mù giá không tuyệt đối:** working memory tự bơm và README 13/10 đã lộ các mức giá/vùng cũ (khai ở INTRINSIC §0b).
  Kết quả lệch xa các vùng cũ, nhưng điều đó không chứng minh hết neo.
