# TV1 (EVNPECC1) — DD làm lại theo khung skill 03/11 · giá 04/11/2026 · job `Taylor_20261105_014130`

> Chỉ nghiên cứu, trung dung. Vụ án/truy thu = WARNING, không vào tâm. Số: `calc/model_tv1_out.txt|json` (`$DNA_PYEXE -I calc/model_tv1.py`). Lõi = định giá nội tại mù giá INTRINSIC_v2 02/11 (`dd_TV1_blind_20261102/valuation_blind_v2.py`), chép nguyên văn sang `calc/tv1_v2_core.py` và **tái lập byte** (`tv1_v2_core_out.txt` md5 `785bcd8c…` = bản gốc). BCTC HN Q3/2026 + FY2025 kiểm toán đã có ở `dd_TV1_20261102/src/` (không tải lại). Sector read: `sector_read_power_consulting_20261028.md` (Bobby, blind).

## 0. Kết luận (số chuẩn hoá liên mã)

| | Trước CK thanh khoản | Sau CK (4,02% @5 tỷ) |
|---|---|---|
| **Tâm** (kỳ vọng xác suất PPA × tư vấn) | 17.033 | **16.348** |
| P10 / P50 / P90 (lưới n=60) | 8.716 / 16.363 / 25.600 | **8.366 / 15.706 / 24.571** |

- Giá **19.600** (đóng cửa 04/11/2026): **+19,9% so tâm**, −20,2% so P90 ⇒ **TRONG vùng**, cao hơn tâm.
- Cấu phần (trước CK): thuỷ điện SB5 12.063 + tư vấn 7.382 + tiền ròng điều chỉnh −2.412.
- Vùng rất rộng vì giá điện SB5 sau 2027 chưa có văn bản: ở tư vấn "giữa", giá 949 → 34.629; 340 → 13.505.
- So rev5 02/11 (tâm 18.100): **−9,7%**, do r 13,5% (thay Ke 12,85%) và CK thanh khoản.

## 1. Kiểm chứng giả thuyết
"P/E TTM ~3x là rẻ" — **nửa đúng**: LNST hiện tại gồm giá điện SB5 ròng ~949 đ/kWh (2025) sẽ bị hạ bậc; chính công ty viết "khi giá điện TĐ Sông Bung 5 sụt giảm" (BCTN 2025 tr.38). Theo giá trị nội tại kỳ vọng (kỳ vọng giá PPA 509 đ/kWh), giá cao hơn tâm ~20%.

## 2. Chất lượng lợi nhuận
- Hai mảng: thuỷ điện SB5 57 MW (FY2025 DT bộ phận 261,6, KQ 165,1) và tư vấn điện (biên EBIT chu kỳ: −19% 2022, −2% 2023, +4–6% 2024, +8–10% 2025, 11–17% 9T/26) [FY25 tr.32–36; `tv1_v2_core_out.txt` §B].
- LNST 9T/26 124,6 > KH năm 104,2; Q3 chưa soát xét. Hoàn nhập phải thu trong QLDN làm biên 9T dao động 11–17%.
- Quỹ KTPL ~20% LNST (30,1/150,2 FY2025) ⇒ chỉ ~80% LN về cổ đông.

## 3. Bảng cân đối — net cash thật (30/09/2026)
Tiền + HTM 198,6 − vay 129,9 − cổ tức phải trả 43,2 − lãi vay cá nhân phải trả 64,3 = −38,7; − quỹ KTPL 40,7 − KTPL sẽ trích từ 9T 24,9 + LNST Q4 sau KTPL 40,0 (ước lượng) ⇒ **−64,4 tỷ = −2.412 đ/cp**. Dở dang tư vấn 148,8 gộp, dự phòng 53,6 (36%).

## 4. Ghi nhận doanh thu
Tư vấn ghi nhận theo nghiệm thu giai đoạn; vốn lưu động hút 49% ΔDT (đo 45–53%); backlog ~835 tỷ (báo cáo cũ). Thuỷ điện ghi theo sản lượng × giá PPA.

## 5. Cổ đông, thanh khoản
- EVN 54,34%; Lê Minh Hà 9,84% (đồng thời bên cho vay). Free float ≈ 35,8% (ước lượng = 100 − 54,34 − 9,84).
- Thanh khoản (BQ 120 phiên tới 04/11): ADV trung vị **0,63 tỷ**; σ ngày 1,30%; spread CS 0,67%. 5 tỷ = **80 / 40 phiên** ở 10% / 20% ADV ⇒ CK 4,02% theo phương pháp đăng ký trước; 1 tỷ: 16/8 phiên, 1,98%. ⚠️ Với 80 phiên thoát, chi phí thực có thể cao hơn mô hình căn bậc hai — quy mô hợp lý ≤ ~1 tỷ.

## 6. Pháp lý / quản trị — ⚠️ WARNING (ngoài tâm; tính ở r 13,5%)
| Cú sốc | Δ đ/cp |
|---|---|
| Cấm thầu EVN 3 năm, DT tư vấn −50% | −8.194 |
| Cấm 5 năm, −50% / 3 năm −70% | −12.983 / −11.471 |
| Buộc nộp 20 / 50 / 100 tỷ | −660 / −1.650 / −3.301 |
| Truy thu bậc giá SB5 2022–26 nếu áp hồi tố đủ | −17.397 |

## 7. Định giá
- **SOTP nội tại:** PV FCFE thuỷ điện 2027–08/2059 (sau KTPL) + DCF tư vấn (2027–32 + terminal g 5%) + tiền ròng điều chỉnh; r = **13,5%** cho cả hai (lãi huy động 12T hiệu dụng 7,40% = CCTG 12M 02/11; điểm neo 03/11 = 7,40%).
- **Kịch bản giá PPA SB5 2027+** (xác suất [UL], từ INTRINSIC_v2): 949 (0,05) / 600 (0,25) / 520 (0,30) / 440 (0,20) / 340 (0,20) ⇒ kỳ vọng 509 đ/kWh. Sàn kinh tế 398–540; hoà vốn tiền mặt 146, kế toán 322.
- **Kịch bản tư vấn:** biên 5% (0,20) / 8% (0,30) / 11% (0,40) / 14% (0,10).
- **Dự án mới:** điện mặt trời nổi 46 MWp (~800 tỷ) chưa đầu tư (vướng thủ tục) ⇒ **NPV=0**, không cộng/không trừ (bản cũ ghi "NPV âm" nhưng cũng không trừ vào giá trị ⇒ không đổi số).
- **Lưới:** 5 PPA × 4 tư vấn × sản lượng {175; 187,5; 200} ⇒ n=60, trọng số = xác suất × đều.

Ô lưới (Q 187,5, trước CK, đ/cp):
| PPA \ tư vấn | biên 5% | 8% | 11% | 14% |
|---|---|---|---|---|
| 949 | 25.572 | 29.840 | 34.629 | 41.993 |
| 600 | 13.644 | 17.912 | 22.701 | 30.065 |
| 520 | 10.910 | 15.178 | 19.967 | 27.331 |
| 440 | 8.176 | 12.444 | 17.233 | 24.597 |
| 340 | 4.448 | 8.716 | 13.505 | 20.869 |

## 8. Độ nhạy r (tâm SAU CK)
| Lãi huy động | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| β=1,0 | 18.006 (+10,1%) | 17.136 (+4,8%) | 16.348 | 15.630 (−4,4%) | 14.971 (−8,4%) |
| β=0,5 | 17.136 (+4,8%) | 16.733 (+2,4%) | 16.348 | 15.981 (−2,2%) | 15.630 (−4,4%) |

## 9. Mốc khoá trước & điều kiện đổi nhận định (hai chiều)
| Mốc | LÊN nếu | XUỐNG nếu |
|---|---|---|
| Văn bản/phụ lục PPA SB5 (ĐHĐCĐ ~04/2027 hoặc CBTT) | giá ròng ≥ 600 hoặc mốc hạ bậc lùi ≥ 2 năm (mỗi năm trễ ≈ +1.450–1.780 đ/cp ở Ke cũ 12,85%, `tv1_v2_core_out.txt`) | ≤ 440 hoặc gần 340; văn bản truy thu 2022–26 |
| BCTC Q4/2026 (~30/01/2027) và kiểm toán FY2026 (~03/2027) | Tư vấn biên ≥ 11% giữ; chấp nhận toàn phần | Ngoại trừ; trích lập cho vụ án |
| Vụ án | Kết thúc không cấm thầu/buộc nộp | Quyết định cấm thầu EVN (−8.200 trở lên) |
| Lãi huy động 12T | −50bp ⇒ +4,8% | +50bp ⇒ −4,4% |
Nhãn DƯỚI vùng khi giá < 8.366; TRÊN vùng khi > 24.571. Giá ngang tâm khi giá PPA kỳ vọng ≈ 600 với tư vấn giữa (ô 600|11% = 22.701 trước CK) — tức thị trường đang định giá gần kịch bản giá điện 520–600.

## 10. Phụ lục — ĐỔI so với DD cũ và vì sao
| Mục | Cũ (rev5 blind 02/11) | Redo 05/11 | Lý do |
|---|---|---|---|
| Chiết khấu | Ke 12,85% (dải 12,3–13,4%, khung 30/10) | r 13,5% neo lãi huy động 7,40% | luật 03/11 |
| Thanh khoản | không | 4,02% @5 tỷ (1 tỷ: 1,98%) | luật 03/11 |
| Vùng | P20–P80 lưới 20 ô | P10–P90 lưới 60 ô (+ sản lượng) | chuẩn hoá liên mã |
| Mô hình, xác suất, BCTC | — | giữ nguyên (tái lập byte) | đã mù giá + qua phản biện mù |
- Lệch < 10% (−9,7%): r −1.083 đ/cp (tâm cũ tái lập 18.116 → 17.033 trước CK), CK thanh khoản −685.
- Các bản cũ khác 02/11 (rev1–rev4: 19.200/17.800/15.200/18.000) dùng P/E peer hoặc giá điện cũ, đã bị thay.
