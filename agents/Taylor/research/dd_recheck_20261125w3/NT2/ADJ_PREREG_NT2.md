# NT2 — kiểm kê hạng mục E17 (KHOÁ TRƯỚC khi tính; theo PREREG_adj.md md5 ef5157cb3f762d58623ed550ebc214c7 + PREREG_adj_v2.md md5 835dfc1e07f9c67ac7f6c3028b529d13)
Nguồn: S = `skeptic/r1_raw.md` (REFUTED medium); BS = BCTC riêng 30/09/2026 trang 2–3 (`dd_redo_20261105/NT2/img/p06.png`, `p07.png`; PDF `src/Q3_2026_hopnhat_va_giaitrinh.pdf`); F = `calc_r3/fin_nt2_r3.csv` (BQ, cộng theo năm). MÙ GIÁ.
Tâm base 24.003 (sau CK 0,92%) / 24.226 (trước CK). Mọi hạng mục chạy QUA mô hình r3 (`val`: np_shift / fcf_shift; khoản t=0 cộng thẳng vào net cash), không cộng tuyến tính tay.

| # | Hạng mục | Hướng | Bậc | m (đầu vào mô hình) | Nhánh thang p |
|---|---|---|---|---|---|
| N1 | Biên LNST thời kỳ đã hết khấu hao máy chính (S killer). Quan sát: FY2025 1.130,3/7.958 = 14,2% (BS 420b đầu kỳ = 1.130,28 tỷ; DT F); 9T/26 906,4/7.803 = 11,6% (BS 420b). Base 800 = 11,2% × 7.137 | lên | B | np_shift = biên × 7.137 − 800: TB hai kỳ +121 [9T/26 +29; FY25 +214] | 2 kỳ cùng hướng, không quan sát ngược có số ⇒ mặc định 0,50 [0,25; 0,75] |
| N2 | FCF − LNST thời kỳ hết khấu hao (S: base FCF=LNST) — FY2025 −136, 9T/26 +252 (F) ⇒ năm hoá (−136+252)/1,75 = +66 | lên | B | fcf_shift +66 [−136; +252] | có quan sát ngược có số (FY2025 −136) ⇒ 0,35 [0,15; 0,55] |
| N3 | Nợ ngắn hạn ngoài net cash/NWC (S missing 2): thuế phải nộp 113,26 + phải trả NLĐ 26,37 + phải trả khác 0,86 + quỹ KTPL 37,90 = −178,39; tài sản ngoài: VAT được khấu trừ 77,45 + trả trước NB 2,81 + phải thu khác 0,23 + CP trả trước NH 6,02 = +86,51 ⇒ ròng −91,88 tỷ tại t=0 | xuống | A | −91,88 tỷ (số trực tiếp BS) | mặc định A 0,90 [0,75; 1,00] |
| N4 | Trích quỹ KTPL hằng năm từ LNST (S missing 1; flow ≠ tồn quỹ N3). Cận bảo thủ: quỹ KTPL tăng ròng 9,51 → 37,90 (+28,39) trong 9T/26 sau phân phối LN 2025 ⇒ trích ≥ 28,39/1.130,28 = 2,5% LNST | xuống | C+ | np_shift −20 (2,5% × 800) [−20; −40 (5% LNST, ước lượng)] | C+ ⇒ thang B, 1 quan sát ⇒ 0,50 [0,25; 0,75] |
| C1 | Giá công suất PPA bị điều chỉnh giảm khi hết khấu hao (cơ chế giá điện) | xuống | C | không có số hợp đồng | chỉ độ nhạy |
| C2 | Hàng tồn kho 346,40 (phụ tùng/nhiên liệu) — giá trị thu hồi | lên | C | không có cơ sở giá trị thu hồi | chỉ độ nhạy |
| C3 | Nghĩa vụ tháo dỡ/môi trường cuối đời nhà máy | xuống | C | chưa đọc thuyết minh | chỉ độ nhạy |
| C4 | Q3/26 chưa soát xét (tiền lệ H1 −94 tỷ) | xuống | C | không có số cho Q3 | chỉ độ nhạy |
| C5 | Rủi ro đối tác tiền gửi SHB | xuống | C | không có thuyết minh theo NH | chỉ độ nhạy |
| X1 | Ưu đãi thuế TNDN hết hạn trong thời hạn dự phóng (S missing 3) | — | A, ĐÓNG | thuế TNDN Q3 20,1% = đã hết ưu đãi (`dd_redo_20261105/NT2/REPORT.md:33`) ⇒ m = 0 | — |
| L1 | r 13,5% > dải Ke (E15 24.638, +2,64%) | lên | luật | không vào Σ | — |
| L2 | Giá trị sau thời hạn = 0 (moat NONE) | — | luật | không vào Σ; độ nhạy WIDE ở ADDENDUM_5F | — |
Chống đếm hai lần: N1 (mức LNST) và N2 (chênh FCF−LNST) là hai thành phần khác nhau của cùng dòng tiền; N2 đo trên dòng tiền đã gồm biến động phải thu, mô hình đã có giải phóng NWC 262,9 riêng ⇒ N2 có thể chồng một phần với NWC (ghi caveat, đã ở nhánh p ngược 0,35). N3 (tồn quỹ KTPL 37,90) ≠ N4 (trích hằng năm). Cổ tức: đã GDKHQ 29/10 (1.000 đ), không còn quyền chưa chốt.
