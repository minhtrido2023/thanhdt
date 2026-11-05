# DDV — DD làm lại mùa BCTC Q3/2026 (05/11/2026, job `Taylor_20261105_014127`)

> NGHIÊN CỨU nội bộ, không phải khuyến nghị. Chưa qua fundamental-skeptic. Số định giá: `calc/model_out.json`, `SUMMARY.json` (khoá md5
> `calc/LOCK_md5.txt` trước khi đọc giá/ADV). BCTC: BCTC Q3/2026 (bản EN, duyệt 08/10/2026, `../../dd_DDV_20261026/src/en_p1.txt`; số chép ở
> `dd_DDV_20261026/REPORT.md`) — src/ đã có Q3 ⇒ không tải lại. Lịch sử LN/DT: BQ `tav2_bq.ticker_financial` (`calc/bq_hist_out.csv`, cột theo QUÝ).
> Sector read: `sector_read_fertilizer_dap_20261028.md` (Bobby, blind).

## 0. Kết luận (số chuẩn hoá liên mã)
| | Trước CK thanh khoản | Sau CK thanh khoản (5 tỷ, 1,45%) |
|---|---|---|
| Tâm (kỳ vọng trọng số) | 13.489 | **13.294** |
| P10 / P50 / P90 | 10.410 / 13.134 / 16.615 | **10.259 / 12.944 / 16.374** |

- Giá đóng cửa **04/11/2026: 15.200** (BQ). So tâm **+14,3%**, so P10 +48,2%, so P90 **−7,2%** ⇒ **TRONG vùng**, nửa trên (gần P75 15.184).
- r = **13,5%** (neo 13,5% @ lãi huy động 12T hiệu dụng 7,4%, CCTG 12M 02/11/2026; 04/11 không đổi).
- Lệch so tâm cũ 14.500 (28/10): **−8,3%** (<10%).

## 1. Giả thuyết kiểm chứng
| Giả thuyết | Kết quả |
|---|---|
| "Lỗ nặng Q3" | **Nửa đúng.** LNST Q3 +9,59 tỷ; lõi lỗ: LN gộp 47,65 − BH 21,51 − QLDN 30,52 = **−4,4 tỷ**, được lãi tiền gửi 22,15 tỷ che. |
| Net cash bảo vệ giá | **Đúng một phần.** Net cash BCTC 1.108,0 tỷ (7.583 đ/cp) bị thổi bởi vốn lưu động Q3; chuẩn hoá còn **869,1 tỷ (5.948 đ/cp)**. |
| Đáy chu kỳ đã qua | **Chưa.** Biên gộp Q3 3,69% (Q3/25 21,88%); độ trễ tồn kho 51–62 ngày ⇒ Q4/26–Q1/27 vẫn gánh lưu huỳnh mua T8–T12 (ME FOB 820–890 USD/t, Bobby). |

## 2. Chất lượng lợi nhuận
- Q3/26: DT 1.290,3 (−7,6% yoy), LN gộp 47,7 (biên 3,69%); 9T: DT 4.916,5 (+18,4%), LN gộp 447,3 (biên 9,10% vs 17,61%). H1/26 biên 11,02%.
- Toàn bộ LNTT Q3 là tài chính ròng +16,2 (lãi tiền gửi 22,15); khác 0,14 ⇒ không có khoản một lần.
- Chu kỳ 2015–2025 (BQ): LN âm 2016 (−470,3), gần 0 các năm 2017/2019/2020; đỉnh 2025 633,5. **Biên LN ròng cả chu kỳ 4,05%** (gồm lãi tiền gửi lịch sử).

## 3. Bảng cân đối / net cash thật (30/09/2026)
- Tiền 114,4 + HTM 1.207,8 (6 tháng, 7,8%/năm) − vay NH 210,9 − thuê TC 3,3 = **1.108,0 tỷ**.
- Vốn lưu động Q3: phải trả người bán 120 → 569 (+449; Tường Nguyên 326,3, Cát Long 109,1, ADF Energy 45,2); phải thu KH 9,3 → 219,4 (+210,1; **Liven Nutrients PTE 217,0 tỷ = 9,8% VCSH**). CFO Q3 +236,6 chủ yếu nhờ phải trả.
- **Net cash dùng trong base = 1.108,0 − (449 − 210,1) = 869,1 tỷ**. Cơ sở dữ liệu: chính BCTC (DCF lõi giả định vốn lưu động bình thường, nên phần tài trợ VLĐ bất thường phải loại để không tính đôi). Độ nhạy: net cash BCTC ⇒ tâm trước CK **15.124**; trừ thêm Liven không thu ⇒ **12.004**.
- Tồn kho 836,6 (NVL 617,3, mua giá S cao, chưa trích lập giảm giá) — rủi ro trích lập Q4.

## 4. Ghi nhận DT, khách hàng, cổ đông, thanh khoản
- DT ghi khi giao hàng (DAP nội địa + xuất khẩu); khách xuất khẩu tập trung (Liven).
- **Vinachem 64,0%** (935,1/1.461,1 tỷ VĐL) ⇒ free float **36,0%**. Cổ tức 9T/26 đã trả 248,4 tỷ (1.700 đ/cp). Room ngoại: chưa kiểm.
- Thanh khoản (BQ 250 phiên): GTGD trung vị **13,0 tỷ/ngày**, σ ngày 2,34%. Vị thế 5 tỷ thoát **3,8/2,6/1,9 phiên** ở 10/15/20%; CK Y=1 **1,45%** (Y 0,5/1,5: 0,72%/2,17%); 10 tỷ 2,05% / 7,7 phiên @10%.

## 5. Pháp lý / quản trị — WARNING
- Vinachem 64%: giá chuyển giao apatit (Apatit Việt Nam, cùng tập đoàn); thoái vốn chưa thực hiện. 20/04/2026: 2 lãnh đạo từ nhiệm chờ phân công (luân chuyển SOE).
- Bãi thạch cao / môi trường Đình Vũ: nút thắt công suất (không định lượng). Chưa thấy khởi tố/ngoại trừ kiểm toán trong tài liệu đã đọc.

## 6. Định giá (`calc/model.py`)
Giá trị = net cash chuẩn hoá + PV(LN hoạt động sau thuế 2027 theo đường S/DAP) + PV(Gordon trên LN lõi giữa chu kỳ từ 2028).
- LN lõi giữa chu kỳ = biên 4,05% × DT chuẩn hoá 5.500 (**ước lượng**) − lãi tiền gửi sau thuế trên net cash chuẩn hoá (55,6) = **167,3 tỷ/năm**. g 3%, RONIC 20% (**ước lượng**). Tỉ trọng terminal (cơ sở) 55,6%.
- LN hoạt động 2027 theo đường S: xấu −185 / cơ sở +107 / tốt +373 tỷ (hiệu chuẩn biên 2 điểm, độ dốc 2,44 điểm%/100 USD S — DD 28/10 §3, **ước lượng**); trọng số 0,45/0,40/0,15 theo đọc mù Bobby (DD 28/10 §2, **ước lượng**). Hệ số LN giữa chu kỳ theo kịch bản 0,8/1,0/1,1 (**ước lượng**; xấu = Bobby loại B, chi phí S cao kéo dài).

| Kịch bản (w) | LN 2027 | Giá trị trước CK (đ/cp) |
|---|---|---|
| Xấu (0,45) | −185 | 11.315 |
| Cơ sở (0,40) | +107 | 14.662 |
| Tốt (0,15) | +373 | 16.884 |
- Không có dự án đầu tư mới/cam kết vốn lớn trong BCTC Q3 ⇒ luật NPV=0 không phát sinh.
- **Lưới P10–P90**: 3 kịch bản × hệ số LN giữa chu kỳ 5 điểm 0,8–1,2 (đều) = **n 15**, trọng số ô = w_kb/5.

## 7. Độ nhạy r (lãi huy động), sau CK thanh khoản
| Δ lãi huy động 12T | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| β=1,0 | 14.167 (+6,6%) | 13.709 (+3,1%) | 13.294 | 12.917 (−2,8%) | 12.574 (−5,4%) |
| β=0,5 | 13.709 | 13.496 | 13.294 | 13.102 | 12.917 |

## 8. Phụ lục — ĐỔI gì so với DD cũ (tâm 14.500, dải 12.300–17.300, 28/10)
Lệch −8,3% (dưới ngưỡng 10%). Đổi phương pháp: (1) DCF Gordon r 13,5% thay bội số 9,5x/7x áp lên **một năm** LN 2027; (2) LN dài hạn = biên cả chu kỳ 2015–2025 đo từ BQ thay cho LN 2027; (3) net cash base = chuẩn hoá vốn lưu động 5.948 (cũ 7.583, cũ chỉ dùng 5.950 làm stress) — tách bạch vì DCF đã giả định VLĐ bình thường; (4) thêm CK thanh khoản 1,45%. Hai chiều bù nhau: (3) −1.635 (đo bằng `nc_sens_pre`: 15.124 → 13.489), phần còn lại là phương pháp lõi.

## 9. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)
- **Xấu đi** (về TRÊN vùng / hạ tâm): BCTC Q4/26 (~20/01/2027) Liven 217 tỷ chưa thu hoặc trích lập (tâm −~1.500); biên gộp Q4 âm và QSP Qatar ≥800 tháng 12; trích lập tồn kho NVL; net cash < 600 tỷ.
- **Tốt lên**: QSP Qatar ≤600 USD/t hai tháng liền và DAP WB ≥700 (cổng Bobby #2) ⇒ chuyển trọng số về tốt; biên gộp quý ≥8% (BCTC Q2/27 ~20/07/2027); lãi huy động −50bp (+3,1%). Giá ≤ P10 10.259 ⇒ DƯỚI vùng.

## 10. Còn mở
Đường S 2027 và độ dốc biên (2 điểm hiệu chuẩn); chi phí NH3 (không có chuỗi BQ); biên chu kỳ gồm lãi tiền gửi lịch sử; cơ cấu hợp đồng S/NH3 (giá trễ?); room ngoại; BCTC Q4/26.

Tái lập: `cd calc && $DNA_PYEXE -I model.py && md5sum model_out.json > LOCK_md5.txt && $DNA_PYEXE -I ../../_common_014127/compare.py DDV`.
