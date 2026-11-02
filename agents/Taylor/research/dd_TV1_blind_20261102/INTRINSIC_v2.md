# TV1 (EVNPECC1) — Giá trị nội tại v2 (NỘI BỘ)

Job `Taylor_20261102_152306` · 02/11/2026 · tái lập: `python3 -I valuation_blind_v2.py > valuation_blind_v2_out.txt`
(ghi kèm `valuation_blind_v2_out.json`; mọi số dưới đây lấy từ hai file này). `INTRINSIC.md` (md5 0e194156…) giữ nguyên, không sửa.

> **Hiệu chỉnh cơ học theo phản biện độc lập chạy mù (`SKEPTIC_BLIND_20261102.md`); không hiệu chuẩn theo giá.**
> Người dựng đã thấy giá thị trường ở giai đoạn 2 (`PRICE_COMPARE.md`: 19.500 đ). Vì vậy v2 CHỈ áp đúng danh sách B1, B2, B3,
> N1–N4 của phản biện; mọi giả định khác giữ nguyên như `valuation_blind.py` đã khoá. Không tham số nào được chọn theo giá.
> Kết quả (18.100) rơi gần giá 19.500 — ghi nhận đây là hệ quả của các hiệu chỉnh cơ học, không phải mục tiêu; người đọc
> nên biết rủi ro neo giá vẫn tồn tại ở cấp lựa chọn danh sách hiệu chỉnh (do phản biện, cũng mù giá, đặt ra).

## 0. Kết quả

| | đ/cp |
|---|---|
| **Tâm = kỳ vọng xác suất** (5 kịch bản giá PPA × 4 kịch bản tư vấn; Q 187,5 GWh; Ke 12,85%) | **18.100** |
| Trung vị có trọng số (P50) | 18.500 |
| **Dải chính P20–P80** | **11.400 – 24.200** |
| Toàn lưới 20 ô | 4.600 – 44.900 |
| Cấu phần | thuỷ điện 12.500 + tư vấn 8.000 + tiền ròng điều chỉnh −2.400 |

So với v1 khoá (27.800): thuỷ điện −3.900 (B1 + N3), tư vấn −4.300 (B3 + N2), tiền ròng −1.500 (B2).
Phản biện ước ≈21.500; v2 thấp hơn vì N2 (VLĐ 49%) và kịch bản biên 5% cộng hưởng (tư vấn biên 5% chỉ còn 23 tỷ khi ΔVLĐ 49%).

## 1. Danh sách hiệu chỉnh đã áp (đúng phản biện, không thêm)

| Mục | Trước (v1) | Sau (v2) | Δ tâm |
|---|---|---|---|
| B1 phân bố giá PPA ròng 2027+ | {949: 0,15 · 600: 0,30 · 520: 0,35 · 440: 0,20}; 340 chỉ ở độ nhạy | **{949: 0,05 · 600: 0,25 · 520: 0,30 · 440: 0,20 · 340: 0,20}**; kỳ vọng 592 → 509 đ/kWh | thuỷ điện 16.400 → 12.500 (gồm N3) |
| B1 nhãn 440 | "sàn kinh tế" | mức thoả thuận trung gian; Đ.14 TT 12 chỉ áp hợp đồng HẾT HẠN, không áp bậc giá Đ.16 đã ghi | — |
| B1 nhãn 340 | "không làm kịch bản" | 243,66 + O&M ≈95 = 338 — mức DUY NHẤT có văn bản phê duyệt (EVN NQ 286/NQ-HĐTV, Cục ĐTĐL 1374/ĐTĐL-GP, 2018); hoà vốn tiền mặt 146, biên tiền mặt ở 340 ≈36 tỷ/năm ⇒ vẫn vận hành | — |
| B2 quỹ KTPL đã trích (mã 323) | bỏ ("chưa tách được") | **−40,7 tỷ** (40.708.199.257, BCTC Q3/2026; kiểm trên `img/hn_p4.png`; đầu năm 26,75) | −1.500 |
| B3 kịch bản tư vấn biên quay về | không có | **biên 5%, tăng 3%/năm, P 0,20**; P biên5/thấp/giữa/cao = 0,2/0,3/0,4/0,1 | tư vấn 12.300 → 8.000 (gồm N2) |
| N2 ΔVLĐ/ΔDT | 40% | **49%** (đo 45–53%); độ nhạy 45/53 | xem §3 |
| N3 sản lượng P50 | 195 | **187,5** (185–190; BQ 2015–25 = 187) | xem §3 |
| N1 truy thu bậc giá 2022–26 | không nêu | ≈659 tỷ trước thuế (≈19.700 đ/cp sau thuế) — **WARNING, không vào tâm** | 0 |
| N4 mục E đủ vế | chọn lọc | bổ sung đủ (§4) | 0 |
| E5 "thiết kế lại là nguồn việc" | luận điểm | giả thuyết cần kiểm, không hạ số | 0 |

## 2. Lịch sử biên tư vấn — cách tách (B3)

Cách tách: EBIT hợp nhất năm = Σ quý (`Revenue_P0` × `EBITM_P0`) từ BQ `ticker_financial` (`v2data/bq_tv1_quarterly_2022_2025.csv`)
− kết quả bộ phận thuỷ điện (2025: kiểm toán 165,055 [FY25 tr.34]; 2022–24: mô hình Q × 949 − O&M − KH 38, cùng hàm hiệu chuẩn 2025).
DT tư vấn = DT thuần − DT thuỷ điện. Cận dưới = sau toàn bộ chi phí chung; cận trên = cộng lại 8 tỷ chi phí chung phân bổ thuỷ điện.

| Năm | DT tư vấn | EBIT tư vấn | Biên |
|---|---|---|---|
| 2022 | 358,4 | −68,6 | −19% … −17% |
| 2023 | 318,7 | −7,1 | −2% … 0% |
| 2024 | 346,2 | +13,5 | +4% … +6% (kiểm toán sau toàn bộ chi phí chung: 10,9 ⇒ 3%) |
| 2025 | 447,0 | +37,7 | +8% … +10% (kiểm toán 36,8) |
| 9T/2026 | 324,5 | — | 11% (A) … 17% (B), Q3 chưa soát xét |

Đối chiếu phản biện (−15% 2022, −5% 2023): cùng chiều; lệch 2022–23 do mô hình kết quả thuỷ điện các năm đó (không có
báo cáo bộ phận kiểm toán trong hồ sơ). Kết luận không đổi: biên có chu kỳ; 5% = mức 2024, không phải đáy.

## 3. Lưới và độ nhạy (đ/cp)

| Giá PPA ròng (P) \ Tư vấn (P) | Biên 5% (0,2) | Thấp (0,3) | Giữa (0,4) | Cao (0,1) |
|---|---|---|---|---|
| 949 (0,05) | 26.700 | 31.300 | 36.600 | 44.900 |
| 600 (0,25) | 14.200 | 18.900 | 24.200 | 32.400 |
| 520 (0,30) | 11.400 | 16.000 | 21.300 | 29.500 |
| 440 (0,20) | 8.500 | 13.100 | 18.500 | 26.700 |
| 340 (0,20) | 4.600 | 9.200 | 14.600 | 22.800 |

| Biến | Giá trị thử → tâm |
|---|---|
| Ke | 10%: 25.300 · 11%: 22.200 · 12%: 19.800 · 12,3%: 19.100 · 13,4%: 17.200 · 14%: 16.300 |
| Sản lượng P50 | 175: 16.900 · 185: 17.900 · 190: 18.400 · 215: 20.800 · 236,6: 22.900 |
| Giá PPA (tư vấn kỳ vọng) | 340: 11.800 · 440: 15.700 · 520: 18.600 · 600: 21.400 · 750: 26.800 · 949: 33.900 |
| Tư vấn (thuỷ điện kỳ vọng) | biên 5%: 10.900 · thấp: 15.600 · giữa: 20.900 · cao: 29.100 |
| Tỷ lệ KTPL/LNST | 10%: 20.900 · 15%: 19.500 · 25%: 16.700 |
| ΔVLĐ/ΔDT | 40%: 19.400 · 45%: 18.700 · 53%: 17.600 |
| Quỹ KTPL 40,7 | không trừ: 19.600 |
| g dài hạn tư vấn | 3%: 18.100 · 7%: 18.100 |

## 4. WARNING — tách khỏi tâm

| Cú sốc | Δ đ/cp |
|---|---|
| Cấm thầu EVN 3 năm, DT tư vấn −50% 2027–29 | −8.300 |
| Cấm 5 năm, −50% | −13.300 |
| Cấm 3 năm, −70% | −11.700 |
| Buộc nộp lợi bất chính 20 / 50 / 100 tỷ | −660 / −1.660 / −3.320 |
| **Truy thu bậc giá 2022–26** nếu bậc 2018 bị áp hồi tố đủ (≈659 tỷ trước thuế; sản lượng 2024, 2026 [UL]) | **−17.500** (PV) |

Vụ án: Chủ tịch HĐQT và phó phòng TCKT bị khởi tố 07/05/2026; TV1 có tên trong "13 công ty liên quan" (VnExpress 02/07;
The Investor ghi 13 người — hai nguồn không khớp); Đ.76 BLHS: pháp nhân không bị truy cứu 5 tội danh; kênh thực tế: cấm thầu
EVN 3–5 năm (NĐ 214/2025 Đ.133), buộc nộp lợi bất chính, truy thu bậc giá. Nền biên tư vấn 2024–26 trùng giai đoạn dự án
500kV mạch 3 đang điều tra ⇒ thêm lý do biên có thể không bền (đã có kịch bản biên 5%).

## 5. Mục E — đủ hai vế (N4)

**Có thể chưa phản ánh:**
1. Kết quả kinh doanh 9T/26 chưa thấy tác động vụ án: DT tư vấn +29%, hợp đồng ký mới 2025 835,1 tỷ (1,87× DT), trả trước +33%.
2. Mốc hạ bậc giá chưa có văn bản; mỗi năm trễ ≈+1.450–1.780 đ/cp. EVN không được đơn phương hạ (Luật Điện lực 61/2024 Đ.52.4).
3. Đòn bẩy chi phí chung: biên tư vấn 3% (2024) → 8–10% (2025) → 11% (9T/26).
4. Thiết kế gốc các nhà máy thuỷ điện mở rộng miền Bắc (Tuyên Quang MR 81,7 tỷ, dự thầu duy nhất) trong bối cảnh thiếu điện miền Bắc 2027.
5. *Giả thuyết cần kiểm (không vào số):* điều chỉnh quy hoạch sinh thêm việc FS/thiết kế cho đơn vị nắm hồ sơ.

**Có thể đã phản ánh, hoặc thị trường đúng:**
1. Văn bản duy nhất có phê duyệt là bậc 243,66 (≈340 ròng); BCTN 2025 tr.38 công ty tự viết giá "sụt giảm"; lãnh đạo nêu 500–600.
   Nếu bậc đã ký là thật, chủ đầu tư khó viện "lợi nhuận hợp lý" để bỏ (LEGAL_PPA) và trần IRR 12% không bảo vệ.
2. Ngành: "cạnh tranh gay gắt, quy mô một số lĩnh vực truyền thống thu hẹp" (công ty tự nêu); hợp đồng ký mới 2024 chỉ ≈280 tỷ;
   gói 5 Krông Buk–Tây Ninh 1 trao liên danh PECC3+2+4, không có TV1.
3. Biên tư vấn âm 2022–23; dự phòng phải thu 86–113 tỷ (22–28% phải thu gộp).
4. Không trả cổ tức tiền FY2016–22; payout FY2025 27%; KTPL 20% LNST chảy ra người lao động (số dư quỹ 40,7 tỷ).
5. Truy thu bậc giá 2022–26 (≈659 tỷ trước thuế) — xác suất thấp, quy mô lớn.
6. Điện mặt trời nổi NPV âm ở vốn công bố (IRR ≈6,8%).

## 6. Việc cần (không đổi)
Đọc văn bản hợp đồng sửa đổi 2018 + CBTT/ĐHĐCĐ (phụ lục 05 đã ký chưa, điều kiện kích hoạt bậc giá); hỏi IR bằng văn bản;
đối chiếu bản gốc KBSV 17/04/2026 (500–600).
