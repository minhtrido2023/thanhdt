# PVT — DD làm lại mùa BCTC Q3/2026 (05/11/2026, job `Taylor_20261105_014127`)

> NGHIÊN CỨU nội bộ, không phải khuyến nghị. Chưa qua fundamental-skeptic. Số định giá: `calc/model_out.json`, `SUMMARY.json` (khoá md5
> `calc/LOCK_md5.txt` trước khi đọc giá/ADV). BCTC: BCTC hợp nhất Q3/2026 + CV 983 ngày 28/10/2026 (text đã trích:
> `../../dd_PVT_20261029/src/q3_pvt_hopnhat_text.txt`, chưa soát xét; số ráp bằng hằng đẳng thức ở DD 29/10) ⇒ không tải lại.
> Lịch sử: BQ `tav2_bq.ticker_financial` (`calc/bq_hist_out.csv`; `NP_P0` = LNST mẹ theo quý, 2026Q3 375,1 khớp 9T mẹ 1.272,3 − 6T 897,2).
> Sector read: `sector_read_oil_gas_shipping_20261029.md` (Bobby, blind).

## 0. Kết luận (số chuẩn hoá liên mã)
| | Trước CK thanh khoản | Sau CK thanh khoản (5 tỷ, 0,67%) |
|---|---|---|
| Tâm (kỳ vọng trọng số) | 17.871 | **17.751** |
| P10 / P50 / P90 | 13.089 / 17.644 / 23.120 | **13.001 / 17.525 / 22.965** |

- Giá đóng cửa **04/11/2026: 21.000** (BQ). So tâm **+18,3%**, so P10 +61,5%, so P90 **−8,6%** ⇒ **TRONG vùng**, phía trên (trên P75 20.651).
- r = **13,5%** (neo 7,4% CCTG 12M 02/11/2026; không đổi 04/11). Tâm ≈ **0,94× BVPS mẹ 19.066** (ROE giữa chu kỳ 13,2% ≈ r).
- Lệch so zone cũ (tâm ghi sổ "~20k", point): **−11,2%**. Nguyên nhân chính: sổ zone ghi mốc ~20k của dải FV 19,4–21,2k, còn kỳ vọng trọng số của chính DD 29/10 là **≈18.040** — tâm mới trước CK 17.871 chỉ lệch −0,9% so số đó (§8).

## 1. Giả thuyết kiểm chứng
| Giả thuyết | Kết quả |
|---|---|
| LN tăng thật | **Đúng.** LNST HN 9T 1.581,8 (+60,6%); CFO 9T 2.733,4 = 1,73× LNST; lãi bán tàu ≈0; LNTT lõi (trừ lãi gửi, liên kết, khác) **+65,5%**. |
| Đà còn tiếp | **Không chắc.** Q3 LNTT 613 vs Q2 834 (−26,5% QoQ); biên gộp vận tải Q3 20,7% vs 24,6% 6T. Bobby: cuối đỉnh. |
| PE thấp = rẻ | **Sai khung.** PE TTM ~7 trên LN đỉnh; PB 1,10 @21.000 > trung vị lịch sử 0,91. |

## 2. Chất lượng lợi nhuận
- Vận tải Q3 DT 3.515 (+40,4%), biên 20,7% (Q3/25 21,1%) ⇒ tăng nhờ khối lượng/đội tàu, không nhờ cước. FSO 9T LN gộp −27,5%.
- Lãi tiền gửi 9T 251,0 (12,7% LNTT); lỗ tỷ giá ròng −38,7; liên kết 18,1; khác ròng 93,5 (bồi thường 42,1). Hoàn nhập dự phòng phi tiền −85,4.
- ⚠️ **TT99/2025**: ngừng trích trước sửa chữa lớn từ 01/01/2026 ⇒ biên 2026 thiên lệch tăng so 2025, độ lớn chưa xác định từ text.
- CĐKKS 19,6% LNST HN; định giá dùng **LNST mẹ**.

## 3. Bảng cân đối / nợ ròng (30/09/2026)
- Tiền 2.060,2 + HTM 4.285,0 − vay NH 1.420,8 − vay DH 5.543,7 = **nợ ròng 619,3** (31/12/25: 2.693,6). VCSH mẹ **9.855,6** (BVPS 19.066), CĐKKS 3.007,4.
- Phải thu KH 1.913,2 (+26%), trong đó đơn vị PVN 1.144,7 (+130%). Phải trả PVN tiền mua tàu 232,7.
- FCF 9T 1.786 (CFO 2.733 − capex 947); capex/KH 0,52 ⇒ FCF hiện tại cao hơn mức bền nếu thay tàu (mô hình dùng FCFE = LN × (1 − g/ROE), tức capex duy tu ≈ KH).
- Cam kết vốn: chưa thấy dồn mua tàu trong 9T (XDCB 62,4; trả trước NB 184). Nếu mua Q4 ⇒ base NPV=0 (luật 03/11).

## 4. Ghi nhận DT, khách hàng, cổ đông, thanh khoản
- DT dịch vụ theo phần việc hoàn thành; cho thuê theo đường thẳng. Bên PVN 22,4% DT 9T (Q3 31,7%).
- **PVN 51%** ⇒ free float **49%**; 516,9 tr cp (sau cổ tức cp 10%). Room ngoại: chưa kiểm.
- Thanh khoản (BQ 250 phiên): GTGD trung vị **94,6 tỷ/ngày**, σ 2,92%. Vị thế 5 tỷ thoát **0,5/0,4/0,3 phiên**; CK Y=1 **0,67%** (Y 0,5/1,5: 0,34%/1,01%).

## 5. Pháp lý / quản trị — WARNING
- Thay TGĐ 2 lần trong 4 tháng (Trần Ngọc Nguyên miễn nhiệm 01/07; Nguyễn Thanh Bình từ 03/08/2026), lý do không công bố.
- Chủ tịch đăng ký bán 200.000 cp (0,043%) 03–04/2026 rồi không bán. Phải thu cũ liên quan Huỳnh Thị Huyền Như 73,1 tỷ đã dự phòng 100%.
- Không khởi tố/điều tra. Ý kiến kiểm toán 2025 / soát xét H1/2026: **chưa có trong tay**.

## 6. Định giá (`calc/model.py`, FCFE cổ đông mẹ)
Giá trị = PV(Q4/2026 ≈ LN mẹ Q3 375,1) + PV(FCFE 2027) + PV(Gordon từ 2028 trên LN giữa chu kỳ = ROE giữa chu kỳ × VCSH mẹ 9.855,6). FCFE = LN × (1 − g/ROE), g 3% (**ước lượng**).
- **ROE giữa chu kỳ = 13,15%** = trung vị `ROE_Trailing` Q4 2015–2025 (BQ; dải 10,8–15,8%) ⇒ LN mẹ giữa chu kỳ cơ sở **1.296 tỷ**.
- Nợ ròng (619,3) đã nằm trong LN sau lãi vay và VCSH ⇒ không trừ lần nữa.

| Kịch bản (w) | LN mẹ 2027 | Hệ số ROE giữa chu kỳ | đ/cp (trước CK) |
|---|---|---|---|
| Xấu (0,35): cước về 2023–25, KH tàu mới đè lên | 1.000 | 0,85 | 15.058 |
| Cơ sở (0,45): giữ khối lượng, biên vận tải ~20% | 1.250 | 1,00 | 18.618 |
| Tốt (0,20): Q3 năm hoá giữ được | 1.500 | 1,10 | 21.112 |
LN 2027 và trọng số theo DD 29/10 §7 + đọc mù Bobby (**ước lượng**); hệ số ROE theo kịch bản **ước lượng**.
- **Lưới P10–P90**: 3 kịch bản × hệ số ROE giữa chu kỳ 5 điểm 0,8–1,2 (đều) = **n 15**, trọng số ô = w_kb/5.

## 7. Độ nhạy r (lãi huy động), sau CK thanh khoản
| Δ lãi huy động 12T | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| β=1,0 | 19.576 (+10,3%) | 18.617 (+4,9%) | 17.751 | 16.963 (−4,4%) | 16.245 (−8,5%) |
| β=0,5 | 18.617 | 18.173 | 17.751 | 17.348 | 16.963 |
Nhạy r nhất trong 4 mã (giá trị gần như toàn bộ là dòng LN dài hạn, không có đệm tiền ròng). Lãi huy động −100bp đưa tâm 19.576, vẫn dưới giá 21.000.

## 8. Phụ lục — ĐỔI gì so với DD cũ (29/10: kỳ vọng ≈18.040; sổ zone ghi 19,4–21,2k, tâm ~20k)
- Phương pháp: DCF FCFE r 13,5% trên ROE giữa chu kỳ đo từ BQ thay PE 6,5/8,0/8,5 × LN 2027; cộng Q4/2026; CK thanh khoản 0,67%.
- So kỳ vọng trọng số cũ 18.040: **−0,9%** (trước CK). So mốc ~20k trong sổ zone: −11,2% — lệch là do mốc sổ zone (trung điểm dải FV) khác với kỳ vọng trọng số của chính báo cáo cũ, không do số BCTC mới.
- Không có dự án mới/cam kết vốn định lượng được; pháp lý chỉ WARNING như cũ.

## 9. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)
- **Xấu đi**: LNST mẹ Q4/2026 < 300 tỷ (BCTC năm ~T1–T3/2027); tác động TT99 > 150 tỷ; mua tàu lớn ở đỉnh trước 31/12/2026 với giá không có hợp đồng đầu ra; Bobby F2 (30/09/2027, BDTI ~2.800) ⇒ LN mẹ 9T/27 ≤ 900.
- **Tốt lên**: Bobby F1 (31/03/2027): BDTI ≤4.200 mà biên vận tải Q1/27 ≥20% ⇒ nâng cơ sở; công bố ≥60% ngày tàu là TC dài hạn tới 2028; lãi huy động −100bp (+10,3%). Giá ≤ P10 13.001 ⇒ DƯỚI vùng.

## 10. Còn mở
Ý kiến kiểm toán 2025 / soát xét H1; định lượng TT99; cơ cấu TC/spot + đáo hạn hợp đồng; nợ theo đồng tiền; LN 2027 theo kịch bản; room ngoại.

Tái lập: `cd calc && $DNA_PYEXE -I model.py && md5sum model_out.json > LOCK_md5.txt && $DNA_PYEXE -I ../../_common_014127/compare.py PVT`.
