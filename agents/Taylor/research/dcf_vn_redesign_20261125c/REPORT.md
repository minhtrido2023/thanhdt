# Định giá đa proxy cho thị trường Việt Nam — vòng 3 (V3: sửa theo quant-skeptic; job Taylor_20261125_001435, tiếp nối Taylor_20261124_170355)

Taylor · 2026-11-25 · CHỈ NGHIÊN CỨU + ĐỀ XUẤT. Bản V2 giữ nguyên ở `REPORT_V2.md`. Không sửa `dcf_valuation.py`, không wire. **Chưa qua quant-skeptic — không
được coi là CONFIRMED.** Tiêu chí khoá trước ở `PRELOCK.md` (commit `f303028e8`, trước khi chạy mô hình mới).
Quy ước: tiền nhàn rỗi **pin0% (đầu sàn)**, phí 0,1%/chiều, khớp T+1, mã ngừng giao dịch mất 50% trên giá cuối (cận 0%
và 100% báo kèm). IS = as-of 2014-01→2019-12, OOS = 2020-01→2023-10.

## 0. Kết luận trước (V3)

**Thay đổi so với V2 — nói thẳng:** (a) công "không mở mới khi đắt" của mô hình **không tách được khỏi cảnh báo E/P** cùng tỉ lệ cờ;
(b) sau khi embargo nhãn 36 tháng khi fit trọng số, **luật chọn §5 khoá trước chọn `ENS2`, không còn `ENS1w`**; (c) công của cổng
rating bị V2 thổi phồng. Ba kết luận chính của V2 (mục tiêu 2 đạt theo tiêu chí khoá, mục tiêu 1 không đạt, lens chưa phải alpha)
**giữ nguyên chiều**, nhưng bằng chứng cho mục tiêu 2 yếu hơn V2 mô tả.

1. **Mục tiêu 1 (phát hiện rẻ rồi giá chạm tâm) KHÔNG ĐẠT — không đổi.** U-hit của ENS1w 62,8% / 68,8% (V2: 66,4 / 68,3), của ENS2
   64,4% / 68,2%; null giá-trung-vị-5-năm 70,2% / 78,4% (hơn mô hình 7,4 / 9,6 điểm với ENS1w).
2. **Mục tiêu 2 (cảnh báo đắt) ĐẠT theo tiêu chí khoá trước — nhưng một phép null E/P cũng đạt cùng tiêu chí.**
   - ENS1w: đúng-tương đối 71,6% / 71,8% (nền 61,4 / 58,7), báo sai 15,2 / 17,9% (nền 21,9 / 21,6). ENS2: 70,3 / 68,9%, báo sai 15,4 / 18,4%.
   - **Null B-1 "cảnh báo theo E/P, cùng số cờ mỗi tháng, cùng luật 6 tháng liền + 36 tháng bấm lại":** đúng 67,3% / 67,2%, báo sai
     16,9 / 19,4% — **đạt cả bốn điều kiện của mục tiêu 2** (≥ 60%, hơn nền ≥ 5 điểm: +5,9 / +8,5, báo sai ≤ nền, hơn N0).
   - Hiệu ENS1w − E/P: đúng +4,3 điểm [−0,1; +12,0] ở IS, +4,6 [+0,9; +11,6] ở OOS; báo sai −1,7 [−7,1; +1,3] / −1,4 [−5,4; +1,1].
     Với bản được luật chọn: ENS2 − E/P cùng cờ: +0,6 [−8,2; +12,6] / −0,1 [−8,2; +7,8]. D0 − E/P: +3,6 [−3,5; +12,2] / +0,9 [−4,6; +8,6]
     (CI bootstrap theo năm sự kiện, không hiệu chỉnh đa so sánh).
   - **Bằng chứng không phân biệt ENS1w/ENS2 với E/P cho công "đạt ⇒ không mở mới"** (chỉ ENS1w ở OOS có CI không chứa 0, và V2 chọn
     ENS1w bằng trọng số fit IS). Phần thông tin thêm duy nhất đã chứng minh được của mô hình là **IC phần dư** (§1, §3).
   - Cảnh báo vẫn có độ trễ dài, không phải tín hiệu bán (trung vị 13 tháng IS / 6 tháng OOS tới đỉnh; ca VNM, §4).
3. **Bộ mô hình do luật §5 chọn = `ENS2`** (trung vị 5 mô hình, không fit; điểm IS 3,09 điểm so với 2,75 của ENS1w; hoà trong 1 điểm với
   ENS1w, META, D0J nên áp thứ tự ưu tiên không-fit). V2 chọn ENS1w vì trọng số IC IS chưa embargo; chênh giữa hai là 0,3 điểm — **lựa chọn
   mong manh**, báo cả hai. IC 36 tháng: ENS2 0,146 [0,05; 0,24] / 0,190 [0,14; 0,23]; ENS1w 0,152 [0,09; 0,22] / 0,223 [0,17; 0,27];
   IC phần dư (sau E/P, B/P, quy mô): ENS2 0,068 / 0,081, ENS1w 0,070 / 0,118.
4. **Đa proxy không thắng rõ mô hình đơn:** RIM-VN một mình (D0) IC 0,138 / 0,208 và danh mục 14,99%/năm — vẫn tốt nhất trong các S1.
5. **Tạo giá trị: lens, chưa phải alpha — đổi lý do.** S1 ENS1w 12,87%/năm (IS 5,81 / OOS 19,05), ENS2 14,10% (6,59 / 20,71), D0 14,99%
   so với universe 6,12%. E/P công bằng cùng số mã: 12,30% (OOS 20,33) cho ENS1w, 11,96% (OOS 18,63) cho ENS2 ⇒ ENS1w **thua** E/P ở OOS
   (−1,28 điểm), ENS2 **hơn** E/P ở OOS (+2,08), nhưng mốc E/P công bằng tự nó lệch 1,7 điểm OOS chỉ vì số mã đổi 37 → 40: nhiễu cỡ đó.
   DSR phần vượt trội so với universe: ENS1w 0,20, ENS2 0,47, D0 0,56 (< 0,95; N = 57, độ nhạy N = 80 vẫn < 0,95).
6. **Tránh đắt (S7): bỏ mã đang bị cảnh báo khỏi universe cộng 2,2–3,1 điểm/năm (ENS1w 8,83%, ENS2 8,31%, D0 9,17% so với 6,12%) — nhưng
   E/P cùng tỉ lệ cờ cho 8,55% (ENS2 so E/P cùng cờ: 8,31 so 8,38).** ENS1w − E/P = +0,28 điểm/năm (IS +0,16, OOS +0,39), không CI,
   nhỏ so với nhiễu. Tách theo loại cờ (§3.3): loại riêng mã chỉ-mô hình-cờ cho 5,90% (≈ universe), loại riêng mã chỉ-E/P-cờ 6,01% —
   không loại nào một mình mang lại mức tăng.
7. **Kiến nghị rõ (theo yêu cầu):** cho công mềm "cảnh báo đắt ⇒ không mở mới", **KHÔNG nên thay E/P bằng ENS1w/ENS2 dựa trên bằng
   chứng này** — E/P đạt cùng tiêu chí, đơn giản, không fit tham số. Nếu muốn dùng mô hình: hiển thị **cùng** E/P, coi cờ đồng thuận
   (cả hai cùng báo) là mức cảnh báo cao hơn; không coi mô hình là nguồn thông tin riêng cho tới khi có kiểm định ngoài mẫu mới (ngoài 2023-10).
8. **Đính chính vòng 1 (giữ từ V2):** FCFE chỉ là lỗi gốc ở OOS; sống sót là thật (EW 8,25% chỉ-BQ so 6,12% có mã vắng BQ — V2 ghi 5,96/8,09,
   nay đổi vì NB-2); mô hình không nhận ra nhóm "sổ sách đẹp rồi sụp".

**Delta V2 → V3 theo hạng mục** (số V2 = `out_A/` tái lập đúng V2; nguồn so sánh `out/delta_out_A_out_C.csv`, `delta_out_C_out_D_out.csv`, `delta_out_C_out_E_out.csv`):

| Hạng mục | Đổi gì | Số trước → sau |
|---|---|---|
| NB-2 giá T+1 từ giá đầy đủ, bỏ fallback giá cuối toàn cục | `e_bt2.period_ret` | Universe EW 5,96 → **6,12**% (IS 1,24 không đổi, OOS 10,03 → 10,33); S1 ENS1w 13,51 → 13,25; S1 D0 14,99 → 14,99; S3f 13,14 → 13,16; S7 ENS1w 8,30 → 8,46; S7 D0 9,00 → 9,17; EW chỉ-BQ 8,09 → 8,25 |
| NB-1 N của nhánh VND tại ngày công bố | `b_panel.py` | Cú nhảy vốn hoá > 15% (dòng VND, trong universe 2014+): 9,44 → **7,51**%; toàn bộ dòng VND 5,07 → 4,22%; 167 / 4.490 dòng VND đổi N > 5%. Kết quả: D0 không đổi ở 3 chữ số; S1 ENS1w 13,25 → 13,26; S3f 13,16 → 13,27 (nhánh tách `out_E`) |
| NB-3 embargo 36 tháng khi fit trọng số | `c_models2.py` | Trọng số: D0B 0,117 → 0,101; DDM 0,048 → 0; EPV 0,122 → 0,097; MULT 0,134 → 0,048; HEDf 0,065 → 0. ENS1w IC IS 0,150 → 0,152, OOS 0,204 → **0,223**; S1 ENS1w 13,26 → 12,87 (IS 5,18 → 5,81; OOS 20,41 → 19,05). **Luật §5: ENS1w → ENS2** |
| NB-6 trung vị PIT thay trung vị toàn mẫu | `c_models2.py` | HEDf tâm HPG 12/2018: 8.145 → 8.151; IC đổi ≤ 0,001 |

## 1. Dữ liệu, khung PIT và kiểm kê nguồn (mục tiêu 3)

Panel tháng 2008-01→2026-11: 188.947 dòng, 1.556 mã. Mẫu đánh giá (in-universe, as-of 2014-01→2023-10): 38.846 dòng mã
BQ + 2.741 dòng mã vắng BQ. N độc lập: theo mã 781 cụm; theo thời gian 6 năm as-of (IS) và 4 năm (OOS), tức chỉ 2 và
≈1,3 khối 36 tháng không chồng lấn — **sức mạnh theo thời gian yếu**, mọi CI ghi "khối năm" là bootstrap B = 2000 theo
năm as-of.

| Nguồn | Dùng? | Ghi chú |
|---|---|---|
| `ticker` (cache 23/11 + BQ trước 2013) | Có | Nguồn DUY NHẤT cho Close và Price (một vintage) |
| `ticker_financial` | Có | Tổng tài sản, nợ, LN và doanh thu 8 quý, biên, CFO, capex, tiền, nợ vay, DY, FSCORE, IntCov |
| `universe_pit` | Có | Cổng PIT; tự dựng lại cổng cho mã vắng BQ, khớp bảng thật 99,7% (512.576 phiên-mã) |
| `fa_ratings_8l` | Có | Rating PIT cho cổng ≤ 3; route chỉ có bản hiện tại (không PIT trước 2026) |
| `risk_rating`, DT5G live, `deposit_rate_vn` | Có | Proxy đơn biến / phân rã theo trạng thái / mô tả |
| VNDirect finfo (ngoài BQ) | Có | Giá + BCTC quý của 669 mã vắng BQ (409 đã huỷ niêm yết); giá từ 2013-01 |
| `OShares`, `PB`, `PE`, `EVEB`, `EBITDA_P0` vendor | Không | `OShares` bị restate; `EBITDA_P0` lẫn số quý và số 12 tháng (VNM 2015Q4 2,56 nghìn tỷ, 2019Q3 14,0 nghìn tỷ) ⇒ dùng EBIT = biên EBIT × doanh thu 12 tháng |
| `oshares_live` (số CP PIT) | Không | Gọi BQ lỗi trong sandbox và tự khai từ chối 12–33% ⇒ thay bằng vốn chủ tổng (§2 lỗi 2) |
| `moat_tags` | Không | 39 mã, một phiên bản 06/2026, không PIT |
| Room ngoại / sở hữu nước ngoài | Không | Chỉ có API VNDirect từ 2018-08, chưa wire, không phủ IS |
| Tín dụng, tỷ giá, CPI, GDP, hàng hoá (SunSirs/WB), BDI, `VNINDEX_PE`, breadth, CCTG, refi | Chỉ mô tả | Chuỗi thị trường; N theo thời gian ≤ 10 điểm chồng lấn |
| `ticker_prune`, `profit_*` | Không | TRAP / cấm |

**IC 36 tháng đơn biến** (số V2; V3 đổi ≤ 0,002 mỗi ô — số chính xác ở `out/proxy_ic.csv`; [CI khối năm]; dấu đã đảo để "cao = tốt"):

| Proxy | IS | OOS |
|---|---|---|
| E/P (LN 12 tháng / vốn hoá) | +0,128 [0,05; 0,20] | +0,255 [0,23; 0,28] |
| Biên ròng trung vị 5 năm | +0,123 [0,06; 0,19] | +0,233 [0,14; 0,32] |
| ROE trung vị 5 năm | +0,114 [−0,00; 0,23] | +0,232 [0,15; 0,31] |
| Biên gộp | +0,105 [0,06; 0,14] | +0,178 [0,15; 0,20] |
| Cổ tức tiền / giá | +0,085 [0,03; 0,14] | +0,230 [0,16; 0,29] |
| Tiền ròng / vốn hoá | +0,078 [0,03; 0,12] | +0,176 [0,12; 0,22] |
| CFO / giá | +0,073 [0,06; 0,09] | +0,170 [0,14; 0,19] |
| EBIT / EV | +0,066 [0,01; 0,13] | +0,149 [0,11; 0,19] |
| Vốn hoá (log) | +0,144 [0,00; 0,28] | +0,234 [0,13; 0,33] |
| Rẻ so lịch sử bội số của chính mã (REL) | +0,131 [0,05; 0,20] | +0,192 [0,14; 0,24] |
| B/P | −0,010 [−0,17; 0,15] | −0,048 [−0,14; 0,11] |
| S/P | +0,008 [−0,09; 0,10] | +0,020 [−0,02; 0,07] |
| Tăng trưởng doanh thu / LN 12 tháng | +0,016 / −0,028 | +0,025 / −0,026 |
| FSCORE | +0,017 [−0,03; 0,06] | +0,015 [−0,01; 0,03] |
| Rating 8L | +0,034 [−0,06; 0,14] | +0,216 [0,12; 0,30] |
| Nợ vay/EBIT thấp, IntCov cao, vòng quay tiền ngắn | −0,009 / −0,104 / +0,037 | +0,131 / +0,164 / +0,239 |
| Rẻ so trung vị giá 5 năm của chính mã (null N0) | +0,010 [−0,10; 0,12] | +0,060 [−0,01; 0,10] |

Đọc: (i) thị trường VN trả tiền cho **lợi nhuận hiện tại + chất lượng bền**, không trả cho sổ sách (B/P) hay doanh thu
(S/P); (ii) các proxy đòn bẩy và vòng quay tiền đổi dấu giữa hai era ⇒ không ổn định, không đưa vào tâm; (iii) vốn hoá
lớn thắng ở cả hai era — phần vượt trội của mọi mô hình phải đọc sau khi loại quy mô (đã làm ở IC phần dư).

Chuỗi thị trường (10 mốc cuối năm, mô tả): cuối 2021 tổ hợp cho tâm/giá trung vị 0,49 và 69,9% universe ở vùng cảnh báo;
lợi suất EW 36 tháng sau đó −24,4%. Cuối 2018, 2019, 2022 có 38–44% universe ở vùng rẻ; 36 tháng sau +207%, +51%, +54%.
Tương quan 0,52 trên 10 điểm chồng lấn — không đủ để kết luận, chỉ nhất quán về chiều.

## 2. Sửa 9 lỗi skeptic vòng 1 và delta (số V2 — giữ nguyên làm lịch sử; số V3 xem §2b)

| # | Lỗi | Cách sửa | Delta đo được |
|---|---|---|---|
| 1 | Hai vintage giá | Close chỉ từ `ticker`; bỏ Close của `ticker_financial` | Hai nguồn lệch > 2% ở 24,6% dòng, 378 mã (skeptic: 26%, 380) |
| 2 | BVPS đổi cơ sở cổ phiếu lệch ngày giá | Làm việc bằng tổng: vốn chủ = TS − nợ; vốn hoá = Price × N, N chọn giữa {OShares, vốn chủ/BVPS} theo tính liên tục với bước nhảy hệ số điều chỉnh giá | 2.696 dòng (4,6%) có B/P đổi > 15%. HPG quý 1/2019: B/P 0,462 → 0,600 |
| 1+2 | Tác động gộp lên D0 | Cùng 37.200 dòng, cùng nhãn | corr log(tâm/giá) cũ–mới 0,972; 3,5% đổi dấu; IC36 IS 0,151 → 0,149, OOS 0,251 → 0,237 |
| 3 | Sống sót | Kéo giá + BCTC mã vắng BQ từ VNDirect, dựng cổng thanh khoản theo ruleset v1 | 640 mã có giá, 92 từng qua cổng, 75 mã vào mẫu, đủ 9 mã skeptic nêu. Universe EW 8,09% → 5,96%/năm. IC36 D0 0,149 / 0,231 → 0,137 / 0,208. Đổi mức mất 0% ↔ 100% chỉ làm IC lệch ≤ 0,005 |
| 4 | Quy nguyên nhân FCFE chưa cô lập | Chạy engine với tổng giá trị (`oshares=1`) rồi chia vốn hoá mới; ablation chỉ đổi dòng tiền gốc | Cùng 7.972 / 7.910 dòng: FCFE 0,097 / 0,028; lợi nhuận thặng dư cùng r, g, 5 năm 0,087 / 0,200; D0 0,171 / 0,243. Phần riêng FCFE − RI: IC +0,034 [−0,06; 0,12] IS, −0,119 [−0,18; −0,04] OOS |
| 5 | CI cụm theo mã quá hẹp | CI khối năm B = 2000; IC theo từng năm so với E/P | E/P hơn tổ hợp ở 2021, 2022, 2023 (2023: 0,255 so với 0,159 của ENS1, 0,102 của D0); tổ hợp hơn ở 2015, 2016, 2019, 2020 |
| 6 | Tính "không chạy được" là trượt | NA riêng | A_pit 1/2 (3 ca NA); D0 3/5. HPG đạt ở D0 **chỉ nhờ vốn chủ tăng** (39,0 → 46,0 nghìn tỷ, +18%; tâm +16,8%) |
| 7 | Thiếu null cho tiêu chí cắt giá | Null N0 = trung vị 60 tháng giá của chính mã | Null cắt 71% / 69% (skeptic: 71,6% / 69,8%). Không mô hình mù giá nào vượt null ở phép đo chạm tâm (§3) |
| 8 | Sức chứa | Sổ 50 tỷ, trần vị thế 20% × GTGD × 5 phiên, sàn GTGD | S1 tổ hợp: không sàn 12,13%; sàn 1 tỷ 13,51%; sàn 5 tỷ 12,67% (IS 0,43%, OOS 23,91%); bỏ trần 14,08% |
| 9 | Đối chứng E/P không công bằng | Cùng cổng rating, cùng số mã, có vùng đệm top 2N | Turnover 35,7% so với 35,9%/tháng. Tổ hợp 13,51% so với E/P 13,14% (IS 5,68 / 4,46; OOS 20,43 / 20,87). D0 14,99% so với E/P cùng số mã 12,69% (IS 6,47 / 3,42; OOS 22,54 / 20,99) |

Hệ quả của lỗi 4: engine FCFE có phương sai log(tâm/giá) 1,52 (IS), gấp đôi bản lợi nhuận thặng dư (0,75) và gấp ba D0
(0,54), tương quan giữa FCFE và bản RI chỉ 0,11. Ở IS, phần hơn của D0 (0,087 → 0,171) đến từ **ROE xuyên chu kỳ nhân vốn
chủ hiện tại + fade 10 năm**, không phải từ việc bỏ FCFE. Độ phủ engine vẫn chỉ 39–41% universe.

## 2b. Sửa theo quant-skeptic vòng 2 (V3) và delta

Mỗi mục: số `trước` = tái lập V2 (`out_A/`), `sau` = `out/`. Chạy tách: `out_C` = chỉ NB-2; `out_E` = NB-1 + NB-2 + NB-6, tắt embargo (`EMBARGO=0`); `out` = tất cả.

| Mục | Việc làm | Kết quả |
|---|---|---|
| B-1 | Null "cảnh báo E/P cùng số cờ mỗi tháng" (`h_null_ep.py` + khối trong `c_models2.py`): mỗi tháng, trong universe, gán cờ cho đúng k mã có E/P cao nhất (k = số cờ của mô hình trong tháng đó), rồi chạy **cùng** luật 6 tháng liền + 36 tháng bấm lại; cùng nền vô điều kiện. Thêm 3 tổ hợp: cả hai cờ (WBOTH), chỉ mô hình (WONLY), chỉ E/P (EONLY). Cũng làm bản khớp cờ ENS2 (hậu tố `_E2`). Script tự tạo, không dùng `/tmp` của skeptic | §3.3: E/P đạt cùng tiêu chí mục tiêu 2; §5: S7 E/P cùng cờ 8,55% so ENS1w 8,83%. Không tái lập được đúng số của skeptic (69,3 / 69,5 đúng; 17,1 / 17,4 sai) vì định nghĩa chọn cờ khác (k theo tháng tại đây); 67,3 / 67,2 và 16,9 / 19,4 |
| B-2 | Viết lại công cổng rating | §5 và §6 mục 2 |
| NB-2 | `e_bt2.period_ret` lấy giá T+1 từ **toàn bộ dữ liệu giá** (`out/px_t1.parquet`: giá phiên đầu mỗi tháng của mọi mã); thiếu tháng ⇒ lấy phiên đầu tháng kế tiếp còn giao dịch; chỉ khi mã **không còn phiên nào** từ tháng đó mới áp mức mất 50% trên giá cuối **của chính mã đó**. Bỏ `last_close` toàn cục | Universe EW 5,96 → 6,12%; S1 ENS1w 13,51 → 13,25; S1 D0 14,99 → 14,99; S3f 13,14 → 13,16; S7 ENS1w 8,30 → 8,46; S7 D0 9,00 → 9,17. Selfcheck 8 tính lại giá T+1 của 400 dòng ngẫu nhiên + ≤ 300 dòng lợi suất ≤ −45% từ `px_t1` thô, lệch tối đa 2,2e-16, 40 dòng thuộc nhánh ngừng giao dịch |
| NB-1 | Nhánh VND: N = vốn góp cuối quý × hệ số sự kiện (bonus/chia tách/quyền) xảy ra giữa cuối quý và ngày công bố, suy từ bước nhảy log(Price/Close) giữa hai ngày — cùng nguyên lý `pick_n` của nhánh BQ. **Không** dùng bảng GDKHQ (chưa kiểm). `VND_N_OLD=1` quay về cách V2 | Cú nhảy vốn hoá > 15% (sau điều chỉnh hệ số giá): dòng VND 5,07 → **4,22%**, riêng in-universe 2014+ 9,44 → **7,51%** (skeptic đo 8,9%); thước đo thay thế chỉ trên dòng VND: 4,70 → 3,96% (4.192 dòng); 167 / 4.490 dòng VND đổi N > 5%. Nhánh BQ (đo lại, in-universe 2014+): OS 3,0%, OS* 3,4%, E/BVPS **10,3%** (n = 497) — skeptic 2,8 / 9,7. Tác động lên kết quả: D0 không đổi ở 3 chữ số; S1 ENS1w 13,25 → 13,26 |
| NB-1b | Đối chiếu nhánh E/BVPS với `oshares_live.oshares_at(live=False)` (BQ nay chạy được; V2 ghi lỗi). Mẫu 80 dòng E/BVPS in-universe 2014+ + 30 dòng OS làm đối chứng (`calc/l_oshares_xcheck.py`, `out/oshares_xcheck.json`) | OS đối chứng: lệch 0,0% (29/29 có số, 1 bị từ chối). **E/BVPS: 78/80 có số live; lệch > 5% ở 98,7%, > 15% ở 61,5%, trung vị |log N/N_live| = 0,189.** Nhưng chính `oshares_live` chỉ chứng nhận được 5/80 ca (AIS_EXACT); 45 ANCHOR_UNVERIFIED, 18 ANCHOR_ONLY, 10 FIN_FALLBACK ⇒ **không thể gọi bên nào là đúng**. Nhánh này chỉ 497 / 19.723 dòng (2,5%). **Chưa chạy** độ nhạy thay N bằng số live (mẫu quá nhỏ, 80 dòng) |
| NB-3 | Embargo: mọi bước FIT trên IS (trọng số ENS1w, chọn theo ngành META, hedonic) loại as-of sau 2016-12 (nhãn 36T của 2016-12 xong 2019-12) ⇒ không chồng lên OOS 2020-01+ | Trọng số ENS1w (D0B / DDM / EPV / MULT / HEDf): 0,117 / 0,048 / 0,122 / 0,134 / 0,065 → **0,101 / 0 / 0,097 / 0,048 / 0** (IC IS embargo của DDM −0,019, HEDf −0,100 ⇒ trọng số 0). ENS1w IC IS 0,150 → 0,152; **OOS 0,204 → 0,223**; cảnh báo đúng 70,5 / 69,9 → 71,6 / 71,8%; U-hit 66,3 / 68,0 → 62,8 / 68,8%; S1 ENS1w 13,26 → 12,87 (IS 5,18 → 5,81; OOS 20,41 → 19,05). META: BANK chọn ENS2 (IC −0,186); CYCLICAL chọn DDM (0,286 thay 0,197 ở ENS2). **Luật §5 đổi chọn ENS1w → ENS2** (§3). OOS **tăng** khi bỏ nhãn chồng lấn, không giảm ⇒ không thấy dấu hiệu lợi thế OOS của V2 đến từ chồng nhãn |
| NB-4 | Khai báo: **OOS chỉ là lần nhìn thứ hai.** D0, r = 12,25% và ngưỡng chọn (0,8 / 0,67 / 6 tháng) được chốt sau khi vòng 1 đã thấy 2014-2023; PRELOCK V2 khoá chọn **mô hình** và **tiêu chí**, không khoá r, g, ngưỡng. N biến thể đếm lại: 51 mô hình + 6 chiến lược + 8 cờ null/tổ hợp (EPN, WBOTH, WONLY, EONLY × 2) + S3f_ENS2, S1_ENS2, 8 S7 ⇒ N hiệu dụng cho DSR giữ 57, báo độ nhạy N = 80 (mọi DSR vượt trội < 0,95) | §7 |
| NB-5 | U-static có nền khớp ngưỡng: nền cố định "tăng ≥ 25% tại một thời điểm" 69,5 / 68,1% so nền khớp mức tăng cần thiết trung bình 59,9 / 56,5% (ENS1w, n = 266 / 240; `out/null_ep.json` khối `ustatic_matched_baseline`). | U-static ENS1w 61,7 / 65,8% hơn nền khớp **+1,7 (IS) / +9,3 (OOS)** điểm, so với nền cố định −7,8 / −2,2. Tiêu chí khoá trước (≥ 5 điểm) trượt ở IS ngay cả với nền công bằng ⇒ **kết luận mục tiêu 1 không đổi** |
| NB-6 | Trung vị PIT (lát cắt tháng) thay trung vị toàn mẫu cho `roe_sd5` và `ltv` trong hedonic; xoá biến `gapfill` không dùng; PRELOCK ghi "~23:35" nhưng commit `f303028e8` ghi **23:12:19 +0700** — lấy theo commit | HEDf tâm HPG 12/2018 8.145 → 8.151; IC đổi ≤ 0,001. Bản V3 không chỉnh PRELOCK (giữ tiêu chí khoá) |
| NB-6b | Tái lập panel: CSV VNDirect thô (1.342 file, 62 MB) **không commit**; thay bằng `MD5SUMS_delisted.txt` (md5 từng file) + script `a0_fetch_delisted.py` | `MD5SUMS_delisted.txt` |

## 3. Họ mô hình và kết quả theo mục tiêu 1–2

18 biến thể mới (định nghĩa đầy đủ ở `PRELOCK.md` §1), cùng mẫu, cùng khung PIT:

| Nhóm | Ký hiệu | Mô tả ngắn |
|---|---|---|
| Mù giá tuyệt đối | A_pit · A_RI | Engine FCFE production · ablation đổi sang lợi nhuận thặng dư |
| | D0 · D0J · D0B | RIM-VN vòng 1 · + cờ "ROE đang nhảy" · + ngân hàng độ bền 0,7 |
| | DDM · EPV | Cổ tức chiết khấu hai giai đoạn · doanh thu × biên ròng trung vị 5 năm, vốn hoá theo Gordon |
| Tương đối thị trường (dùng giá của mã KHÁC) | MULT | Trung vị 60 tháng trước của P/E chuẩn hoá, P/B, P/S, EV/EBIT theo ngành × cơ sở của mã |
| | HEDf · HEDr · HEDL | Hồi quy log(P/B) theo ROE, tăng trưởng, payout, nợ, quy mô vốn chủ, ngành; đóng băng 2019-12 · cuốn chiếu · thêm thanh khoản |
| Có dùng giá quá khứ của chính mã (Lớp 2) | REL · G1 · L2 | Bội số lịch sử của mã × cơ sở hiện tại · D0 × premium riêng · Lớp 1 × premium riêng |
| Tổ hợp | ENS1 · ENS1w · ENS2 · META | Trung vị 3 mô hình mù giá · trọng số theo IC IS trên 5 mô hình · trung vị 5 mô hình · chọn theo ngành |

Bảng chính V3 (BQ + mã vắng BQ; IS / OOS; nguồn `out/tables.md` ← `out/metrics2.csv`). U-hit = sau tín hiệu rẻ, giá đi lên chạm tâm
trượt trong 36 tháng. U-static = giá chạm mức tâm lúc phát tín hiệu. "Đúng" = sau cảnh báo đắt, mã kém universe trong 36 tháng. Các hàng
ENS1w/ENS2/META dùng trọng số/chọn có embargo (NB-3).

| Mô hình | Độ phủ IS/OOS | IC36 [CI khối năm] IS / OOS | IC phần dư | U-hit | U-static | Đúng | Sai | N cảnh báo |
|---|---|---|---|---|---|---|---|---|
| A_pit | 39 / 41 | 0.096 [0.00; 0.19] / 0.030 [-0.03; 0.11] | 0.063 / 0.008 | 38.7 / 44.2 | 32.7 / 39.8 | 59.2 / 61.4 | 21.1 / 19.9 | n=152/176 |
| A_RI | 39 / 40 | 0.082 [0.01; 0.14] / 0.204 [0.16; 0.24] | 0.014 / 0.086 | 42.3 / 56.2 | 49.5 / 59.9 | 64.6 / 68.6 | 18.6 / 17.0 | n=161/194 |
| D0 | 95 / 97 | 0.138 [0.06; 0.22] / 0.208 [0.15; 0.25] | 0.046 / 0.110 | 60.3 / 70.5 | 61.9 / 68.3 | 71.0 / 68.1 | 15.5 / 18.8 | n=420/475 |
| D0B | 95 / 96 | 0.117 [0.04; 0.20] / 0.207 [0.15; 0.25] | 0.025 / 0.097 | 61.9 / 67.8 | 57.1 / 62.8 | 71.6 / 68.1 | 15.7 / 18.8 | n=408/458 |
| DDM | 28 / 29 | 0.048 [-0.03; 0.12] / 0.080 [0.04; 0.11] | -0.015 / 0.048 | 53.8 / 54.7 | 52.7 / 62.8 | 69.4 / 48.9 | 17.7 / 23.3 | n=62/90 |
| EPV | 62 / 64 | 0.122 [0.08; 0.17] / 0.167 [0.12; 0.21] | 0.046 / 0.122 | 58.8 / 73.1 | 59.4 / 67.2 | 68.4 / 67.5 | 16.2 / 19.9 | n=247/311 |
| MULT | 85 / 99 | 0.134 [0.03; 0.24] / 0.118 [0.04; 0.20] | 0.101 / 0.041 | 62.9 / 65.6 | 59.5 / 58.2 | 68.4 / 70.8 | 14.6 / 14.2 | n=294/373 |
| HEDf | 82 / 96 | 0.065 [-0.11; 0.24] / 0.145 [0.08; 0.22] | -0.006 / 0.034 | 57.0 / 66.7 | 55.5 / 58.4 | 69.4 / 70.2 | 17.7 / 16.4 | n=232/367 |
| ENS1 | 95 / 96 | 0.135 [0.07; 0.21] / 0.239 [0.19; 0.28] | 0.044 / 0.124 | 60.6 / 67.4 | 59.8 / 64.2 | 71.7 / 70.4 | 16.2 / 17.6 | n=438/506 |
| ENS1w | 99 / 99 | 0.152 [0.09; 0.22] / 0.223 [0.17; 0.27] | 0.070 / 0.118 | 62.8 / 68.8 | 61.7 / 65.8 | 71.6 / 71.8 | 15.2 / 17.9 | n=433/507 |
| ENS2 | 99 / 99 | 0.146 [0.05; 0.24] / 0.190 [0.14; 0.23] | 0.068 / 0.081 | 64.4 / 68.2 | 62.1 / 61.8 | 70.3 / 68.9 | 15.4 / 18.4 | n=384/426 |
| META | 99 / 99 | 0.135 [0.05; 0.23] / 0.187 [0.14; 0.23] | 0.050 / 0.077 | 64.0 / 66.4 | 61.3 / 59.7 | 70.0 / 68.9 | 14.8 / 18.8 | n=393/426 |
| REL | 81 / 91 | 0.130 [0.05; 0.20] / 0.190 [0.14; 0.24] | 0.081 / 0.105 | 73.5 / 81.9 | 63.3 / 69.3 | 69.5 / 67.7 | 19.9 / 19.3 | n=226/332 |
| L2_ENS1w | 80 / 92 | 0.127 [0.07; 0.18] / 0.178 [0.14; 0.21] | 0.078 / 0.064 | 71.0 / 75.3 | 61.3 / 60.4 | 66.7 / 67.9 | 20.1 / 18.6 | n=279/350 |
| N0 | 82 / 93 | 0.010 [-0.10; 0.12] / 0.060 [-0.01; 0.10] | 0.025 / 0.076 | 70.2 / 78.4 | 59.0 / 70.3 | 63.8 / 61.4 | 20.3 / 22.2 | n=345/447 |

Nền vô điều kiện: U-static (+25%) 69,5 / 68,1% · đúng 61,4 / 58,7% · sai 21,9 / 21,6%. Null N0 (giá so trung vị giá 5 năm): U-hit 70,2 / 78,4%.

CI cụm theo mã (B = 500) của ENS1w: [0,10; 0,20] / [0,15; 0,26] — hẹp hơn CI khối năm ở IS, đúng như skeptic cảnh báo.

**Đối chiếu tiêu chí khoá trước (V3):**
- **Mục tiêu 1 — KHÔNG ĐẠT** (cả ENS1w và ENS2). U-hit ≥ 60% có (ENS1w 62,8 / 68,8%; ENS2 64,4 / 68,2%) nhưng thấp hơn null N0 70,2 / 78,4% thay
  vì hơn 5 điểm; U-static (61,7 / 65,8%) thấp hơn nền cố định 69,5 / 68,1%. Với nền khớp ngưỡng (NB-5) U-static hơn +1,7 / +9,3 điểm: trượt
  IS (< 5), đạt OOS. Bản có dùng giá quá khứ tốt nhất (REL) hơn null 3,4 / 3,5 điểm.
- Điều phân biệt mô hình với null là **chuyện xảy ra sau khi chạm** (giữ từ V2: lợi suất vượt trội 36T sau tín hiệu rẻ của ENS1w −0,26 / −0,16 log,
  của null −0,49 / −0,31) — số V2 chưa tính lại sau NB-2/NB-3, đọc như định tính.
- **Mục tiêu 2 — ĐẠT** cho ENS1w, ENS2, D0, ENS1, MULT, HEDf (cả bốn điều kiện, cả hai era) — **và cho null E/P** (§3.3).
- **Độ tin cậy theo độ phân tán giữa các phương pháp — không đạt phép thử khoá trước.** Tercile phân tán thấp: IC 0,126 so 0,073 (IS), 0,193 so 0,116
  (OOS) — tốt hơn; U-hit OOS thấp hơn (64,1% so 68,9%); U-static OOS 62,0 so 56,8%. (`out/confidence2.csv`.)
- **Chống overfit:** META không hơn ENS2 ở OOS (0,187 so 0,190). Hedonic cuốn chiếu kém bản đóng băng; thêm thanh khoản vào hedonic làm IC phần
  dư âm. Cờ "ROE đang nhảy" không cải thiện universe-level (D0J 0,120 so D0 0,138 IS).
- **Luật chọn (§5 PRELOCK, sau embargo):** điểm IS = (U-hit − U-hit null) + (cảnh báo đúng − nền), tính bằng điểm %: **ENS2 3,09 · ENS1w 2,75 ·
  META 2,33 · D0J 2,15 · D0B 1,85 · ENS1 0,65 · MULT −0,33 · D0 −0,42** (`out/tables.md`). Bốn mô hình đầu hoà trong 1 điểm ⇒ ưu tiên
  không-fit (ENS1 > ENS2 > D0B > khác); ENS1 ngoài dải hoà ⇒ **chọn ENS2**. V2 chọn ENS1w (trọng số chưa embargo). **ENS1w giữ làm bản đối chiếu
  vì V2 đã công bố; kết luận ở §0 áp dụng cho cả hai.**

### 3.3 Cảnh báo đắt: mô hình vs null E/P cùng tỉ lệ cờ (B-1)

Cùng luật 6 tháng liền + 36 tháng bấm lại; cờ E/P = k mã có E/P cao nhất mỗi tháng, k = số cờ của mô hình trong tháng đó (trong universe). `EPN` khớp
cờ ENS1w; `*_E2` khớp cờ ENS2. WBOTH = cả hai cùng cờ cùng tháng; WONLY = chỉ mô hình; EONLY = chỉ E/P. "Đúng-tuyệt-đối" = mã giảm giá 36T. Nền vô điều
kiện: đúng-tương-đối 61,4 / 58,7%, báo sai 21,9 / 21,6%. Nguồn `out/null_ep.csv`, `out/null_ep.json`, `out/log_n.txt`; số cờ khớp bản trong `metrics2.csv`.

| Cờ | Era | N | Đúng-tương đối | Đúng-tuyệt đối | Báo sai | Vượt trội TB (log) |
|---|---|---|---|---|---|---|
| ENS1w | IS | 433 | 71.6 | 58.7 | 15.2 | -0.496 |
| D0 | IS | 420 | 71.0 | 57.6 | 15.5 | -0.468 |
| ENS2 | IS | 384 | 70.3 | 60.4 | 15.4 | -0.514 |
| EPN | IS | 419 | 67.3 | 56.1 | 16.9 | -0.460 |
| WBOTH | IS | 293 | 68.3 | 58.0 | 15.4 | -0.526 |
| WONLY | IS | 190 | 67.4 | 52.6 | 17.9 | -0.382 |
| EONLY | IS | 142 | 65.5 | 54.2 | 22.5 | -0.337 |
| EPN_E2 | IS | 350 | 69.7 | 60.3 | 16.0 | -0.491 |
| WBOTH_E2 | IS | 228 | 69.3 | 60.5 | 16.2 | -0.537 |
| WONLY_E2 | IS | 175 | 69.1 | 55.4 | 16.0 | -0.398 |
| EONLY_E2 | IS | 136 | 69.1 | 56.6 | 18.4 | -0.406 |
| ENS1w | OOS | 507 | 71.8 | 68.2 | 17.9 | -0.430 |
| D0 | OOS | 475 | 68.1 | 66.0 | 18.8 | -0.420 |
| ENS2 | OOS | 426 | 68.9 | 69.6 | 18.4 | -0.421 |
| EPN | OOS | 507 | 67.2 | 64.4 | 19.4 | -0.377 |
| WBOTH | OOS | 395 | 73.1 | 73.1 | 17.3 | -0.481 |
| WONLY | OOS | 139 | 66.2 | 55.4 | 19.4 | -0.282 |
| EONLY | OOS | 143 | 55.9 | 49.0 | 20.3 | -0.256 |
| EPN_E2 | OOS | 447 | 69.1 | 69.1 | 17.9 | -0.415 |
| WBOTH_E2 | OOS | 315 | 71.0 | 75.2 | 17.2 | -0.477 |
| WONLY_E2 | OOS | 116 | 62.9 | 57.8 | 12.9 | -0.277 |
| EONLY_E2 | OOS | 147 | 65.3 | 58.5 | 17.7 | -0.353 |

Hiệu [điểm; CI 95% bootstrap theo năm sự kiện] — `out/null_ep.json` khối `diff_*`:

| So sánh | Era | Đúng-tương đối | Báo sai |
|---|---|---|---|
| ENS1w − EPN | IS | +4,3 [−0,1; +12,0] | −1,7 [−7,1; +1,3] |
| | OOS | +4,6 [+0,9; +11,6] | −1,4 [−5,4; +1,1] |
| D0 − EPN | IS | +3,6 [−3,5; +12,2] | −1,5 [−5,4; +1,4] |
| | OOS | +0,9 [−4,6; +8,6] | −0,6 [−3,4; +1,6] |
| ENS2 − EPN_E2 | IS | +0,6 [−8,2; +12,6] | −0,6 [−6,6; +3,2] |
| | OOS | −0,1 [−8,2; +7,8] | +0,4 [−4,2; +4,4] |

Trùng cờ cùng tháng: ENS1w trùng cờ E/P ở 65,4% (IS) / 76,1% (OOS) sự kiện; ENS2 58,3% / 72,8%. **Đọc:** (i) phép null E/P đạt cả bốn điều kiện; (ii) phần mô hình
hơn E/P nhỏ (4–5 điểm), CI IS chứa 0, ENS2 (bản luật chọn) không hơn; (iii) cờ đồng thuận (WBOTH) cho tỉ lệ đúng cao nhất ở OOS (73,1%; E2: 71,0%) nhưng ở IS
chỉ 68,3% (E2: 69,3%) — không ổn định; cờ chỉ-mô hình (WONLY: 67,4 / 66,2%) và chỉ-E/P (EONLY: 65,5 / 55,9%) đều kém. Không hiệu chỉnh đa so sánh (6 so sánh × 2 chỉ số).

## 4. Năm ca kiểm (PIT; `out/cases2.csv`; NA = mô hình không chạy được)

| Ca | A_pit | D0 | D0B | EPV | MULT | ENS1w | REL | L2 | Null |
|---|---|---|---|---|---|---|---|---|---|
| VCS 2015: ≥ 50% tháng tâm > giá | ✗ 33% | ✗ 0% | ✗ 0% | **✓ 75%** | ✗ 0% | ✗ 0% | ✗ 42% | ✗ 0% | ✗ |
| DGC 2016: ≥ 50% tháng tâm > giá | NA | ✓ 100% | ✓ | ✓ | ✗ 8% | ✓ 100% | ✗ 0% | ✗ 0% | ✗ |
| VNM 2011: ≥ 50% tháng tâm > giá | NA | ✗ 0% | ✓ 50% | ✗ 8% | NA | ✗ 25% | ✓ 75% | ✓ 83% | ✗ |
| HPG: tâm tăng qua 2019 và có tháng tâm > giá | NA | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ |
| VNM 07/2015–12/2016: ≥ 50% tháng tâm < giá | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Điểm | 1/2 | 3/5 | 4/5 | 4/5 | 1/4 | 3/5 | 3/5 | 2/5 | 1/5 |

Điểm ca V3 không đổi so V2 (ENS1w 3/5; ENS2 cũng 3/5: VCS ✗, DGC ✓, VNM2011 ✗, HPG ✓, VNM15–16 ✓; `out/cases2.csv`). Tâm HPG sau embargo: ENS1w 9.727 → 11.029 (12/2018 → 12/2019), ENS2 8.846 → 9.752.

- **VCS 2015** chỉ EPV bắt được (rẻ ≥ 25% từ 2015-05, giá chạm tâm sau 5 tháng): EPV nhìn doanh thu × biên, không nhìn
  sổ sách. Cờ "ROE đang nhảy" khoá trước **bỏ lỡ** VCS vì điều kiện "vốn chủ không giảm": cuối 2014 vốn chủ VCS giảm từ
  1.121 xuống 762 tỷ do mua lại cổ phiếu, cờ chỉ bật từ 2015-12. ROE nhảy 12% → 44% một phần là do mẫu số co lại.
- **HPG 2019**: tâm D0 11.694 → 13.656 (12/2018 → 12/2019). Vốn chủ tăng 18%, tâm tăng 16,8% ⇒ đạt **chỉ nhờ tăng trưởng
  sổ sách**, đúng như skeptic nghi. Ở EPV tâm tăng 27% (9.600 → 12.196) nhờ doanh thu tăng với biên chuẩn hoá. Hai mô hình
  tương đối thị trường (MULT, HEDf) cho tâm giảm trong 2019 vì bội số ngành co lại.
- **VNM 2011**: mù giá chỉ D0B đạt, sát ngưỡng (50%). Lớp 2 đạt rõ (REL 75%, L2 83%).
- **VNM 2015–2016**: mọi mô hình báo đắt đúng (tâm/giá 0,42–0,47 cuối 2015). Nhưng giá còn tăng 110% (tính từ cảnh báo
  của D0, 2015-12) tới 196% (từ cảnh báo của ENS1w, 2015-06) trước khi đạt đỉnh 2017-12; 36 tháng sau cảnh báo giá vẫn
  cao hơn 49% / 143%. Sau đỉnh giảm 36% tới 12/2022. Trong phép đo của chính báo cáo này, ca VNM 2015 là một **ca báo sai
  trong cửa sổ 36 tháng** và chỉ đúng ở cửa sổ 7 năm.
- **Ngân hàng quốc doanh vẫn lệch một phía ở mọi mô hình Lớp 1**: VCB tâm/giá trung vị 0,44–0,59, "đắt" 90–100% số tháng
  trong khi giá tăng 8,1 lần; BID 0,62–0,84. Độ bền 0,7 (D0B) chỉ nhích VCB từ 0,47 lên 0,54. Chỉ REL đưa VCB về 0,92.
  CTG thì bội số ngành và hedonic xử lý được (0,95–1,17). Trong nhóm 27 ngân hàng, IC36 của ENS1w là 0,185 (D0 0,158).

Mẫu ngẫu nhiên 24 mã (seed 20261124) + 19 ca thất bại ép: `out/sample2.csv`. Đáng nói: ROS, TTF, HNG, ITA, POM được cảnh
báo đắt 64–100% số tháng (đúng). GTN bị cảnh báo 85–94% nhưng giá tăng 64% rồi bị thâu tóm (sai). FLC (tâm/giá trung vị
1,61), HAI (1,59), ART (3,31), AMD (1,04), KSA (1,04), QBS (0,96) **không bị cảnh báo** và mất 36–96% giá.

## 5. Tạo giá trị (mục tiêu 4) — luật khoá trước (`out/bt2_summary.csv`, `bt2_dsr.json`; V3)

2014-06→2026-10, sổ 50 tỷ, sàn GTGD ≥ 1 tỷ/phiên, trần vị thế, pin0%, đã trừ phí; giá khớp T+1 theo NB-2. S1 = giữ mã có giá ≤ 0,8 × tâm và
rating 8L ≤ 3, ra khi giá > tâm. Số V2 trong ngoặc khi khác.

| Chiến lược | CAGR | IS | OOS | Sharpe | MaxDD | Số mã | Turnover/tháng |
|---|---|---|---|---|---|---|---|
| S1 tổ hợp ENS1w (V2: 13,51) | 12,87% | 5,81% | 19,05% | 0,64 | −44,3% | 37 | 35,4% |
| **S1 tổ hợp ENS2 (bản luật §5 chọn)** | **14,10%** | 6,59% | 20,71% | 0,69 | −41,7% | 40 | 37,1% |
| S1 RIM-VN D0 (V2: 14,99) | 14,99% | 6,47% | 22,54% | 0,74 | −40,7% | 36 | 34,1% |
| S1 MULT · ENS1 | 12,82 · 12,35% | 5,14 · 6,00% | 19,59 · 17,88% | 0,62 · 0,63 | −43,0 · −45,6% | 40 · 39 | |
| S3f đối chứng E/P công bằng, cùng số mã với ENS1w (V2: 13,14) | 12,30% | 3,30% | 20,33% | 0,61 | −43,6% | 37 | 35,3% |
| S3f cùng số mã với ENS2 | 11,96% | 4,39% | 18,63% | 0,60 | −44,7% | 40 | 35,8% |
| S3f cùng số mã với D0 | 12,69% | 3,42% | 20,99% | 0,63 | −42,0% | 36 | 35,5% |
| S2 ENS1w, không cổng rating (V2: 10,05) | 10,34% | 0,96% | 18,75% | 0,51 | −48,7% | 58 | 35,8% |
| S1 engine FCFE (A_pit) | 8,88% | 4,57% | 12,59% | 0,50 | −44,1% | 34 | 36,5% |
| S1 theo Lớp 2 (L2) · REL · null N0 | 7,48 · 7,75 · 2,57% | 0,76 · 2,68 · −7,21% | 13,37 · 12,13 · 11,44% | 0,43 · 0,46 · 0,22 | | | |
| S5 sizing đồng thuận hai lớp (V2: 13,57) | 12,72% | 5,61% | 18,96% | 0,64 | −44,5% | 37 | 38,0% |
| **S7 universe bỏ mã đang bị cảnh báo** ENS1w · ENS2 · D0 | 8,83 · 8,31 · 9,17% | 3,03 · 2,62 · 2,93% | 13,87 · 13,26 · 14,62% | 0,47 · 0,44 · 0,48 | −49,8 · −51,8 · −49,3% | 172 · 195 · 172 | 33,6 · 32,3 · 32,2% |
| **S7 bỏ mã bị cờ E/P cùng số cờ (null B-1)**, khớp ENS1w · khớp ENS2 | 8,55 · 8,38% | 2,87 · 3,29% | 13,48 · 12,78% | 0,46 · 0,45 | −50,4 · −49,7% | 180 · 202 | 32,4 · 30,7% |
| S7 bỏ chỉ mã cả-hai-cờ (WBOTH) · chỉ-mô-hình (WONLY) · chỉ-E/P (EONLY) — khớp ENS1w | 8,14 · 5,90 · 6,01% | 2,44 · 0,87 · 1,27% | 13,10 · 10,25 · 10,10% | 0,44 · 0,36 · 0,36 | | 207 · 252 · 254 | |
| Cùng ba loại, khớp ENS2 (WBOTH_E2 · WONLY_E2 · EONLY_E2) | 7,56 · 6,29 · 6,10% | 2,21 · 1,20 · 1,35% | 12,20 · 10,68 · 10,20% | 0,42 · 0,37 · 0,37 | | 227 · 253 · 252 | |
| Universe EW (cùng sàn, có mã vắng BQ) (V2: 5,96) | 6,12% | 1,24% | 10,33% | 0,37 | −51,7% | 265 | 27,2% |
| Universe EW chỉ mã BQ (V2: 8,09) | 8,25% | 4,62% | 11,35% | 0,45 | −50,2% | 252 | |

- **Phán quyết theo prelock:** S1 ENS1w > universe ở IS và OOS (đạt); S1 ≥ E/P công bằng ở OOS: ENS1w **trượt** (19,05 so 20,33), ENS2 **đạt**
  (20,71 so 18,63, +2,08); DSR phần vượt trội so với universe: ENS1w 0,20 · ENS2 0,47 · D0 0,56; DSR tuyệt đối 0,84 · 0,88 · 0,91 (N = 57; N = 80:
  0,15 · 0,40 · 0,48 và 0,83 · 0,87 · 0,90) — **tất cả < 0,95 ⇒ trượt** ⇒ **lens, chưa phải alpha** (kết luận giữ, lý do đổi: DSR chứ không còn là E/P ở OOS
  cho bản ENS2). Chênh S1 − E/P-công-bằng nhạy theo số mã: S3f 37 mã OOS 20,33, 40 mã OOS 18,63 ⇒ nhiễu ≈ 1,7 điểm OOS. S1 ENS1w thắng universe 10/13 năm,
  ENS2 10/13, D0 11/13. Sharpe chủ động so với E/P công bằng: ENS1w 0,06 · ENS2 0,31 · D0 0,29.
- **D0 vẫn là danh mục tốt nhất** (+3,05 / +1,55 điểm so E/P công bằng ở IS / OOS). D0 không phải mô hình luật §5 chọn ⇒ **quan sát, không phải kết luận**.
- **Tránh đắt (S7):** +2,2 đến +3,1 điểm/năm so universe cho cả ba mô hình, dương ở IS và OOS. **Nhưng null E/P cùng cờ cho +2,4 (ENS1w) / +2,3 (ENS2):**
  ENS1w − E/P = +0,28 điểm/năm (IS +0,16, OOS +0,39); ENS2 − E/P = −0,07 (IS −0,67, OOS +0,48). Không có CI cho S7 (chưa bootstrap) — chênh ≤ 0,5 điểm/năm
  trên 12 năm không đủ để nói mô hình hơn E/P. Tách loại cờ không cộng tính (chỉ-mô-hình 5,90 và chỉ-E/P 6,01 đều ≈ universe 6,12, trong khi loại cả-hai
  8,14 và loại hợp 8,55–8,83): lợi ích nằm ở mã bị **cả hai** hoặc ít nhất một loại cờ cùng lúc — chưa đủ dữ liệu để quy cho mô hình.
- **Sức chứa:** sàn thanh khoản 0 / 1 tỷ / 5 tỷ: 11,66 / 12,87 / 11,79% (V2: 12,13 / 13,51 / 12,67); bỏ trần vị thế 13,51% (V2: 14,08) ⇒ trần lấy đi 0,6 điểm,
  không đổi kết luận "phần vượt trội không đến từ mã kém thanh khoản". Ở sàn 5 tỷ IS chỉ 0,59%/năm, OOS 21,99%.
- **Cổng rating 8L ≤ 3 — SỬA (B-2).** V2 viết "bỏ cổng mất 3,5 điểm" và sai về nguồn: mã vắng BQ không có rating nên S1 tự loại chúng, đó là lợi thế giả. Tách ba
  trạng thái cho ENS1w: **S1 (có cổng, mã vắng BQ bị loại tự động) 12,87%** · **S1 deadin (có cổng, mã vắng BQ lọt cổng) 10,56%** (IS 2,02, OOS 18,15) ·
  **S2 (không cổng) 10,34%** (IS 0,96, OOS 18,75). ⇒ Cổng rating đóng góp **0,22 điểm/năm** trên cùng điều kiện (10,56 − 10,34; IS +1,06, OOS −0,60); phần còn lại
  **2,31 điểm (12,87 − 10,56) là lợi thế sống sót** do loại tự động mã đã hủy niêm yết. V2: 1,08 và 2,38 (cùng cấu trúc). D0: S1 14,99 so deadin 12,42 (2,57 điểm
  lợi thế sống sót). **Không thể nói cổng rating tạo lợi nhuận;** việc giữ nó là chính sách rủi ro/chất lượng của fleet, không phải kết quả đo ở đây.
- **Cận dưới trung thực của S1:** lọt hết qua cổng rating: ENS1w 10,56% (IS 2,02, OOS 18,15; 10,0% tỉ trọng ở mã về sau rời sàn — số V2, chưa đo lại), D0 12,42%, E/P công bằng cùng điều kiện
  12,34% (S3f deadin) ⇒ **ở cận dưới ENS1w thua E/P 1,8 điểm, D0 hơn 0,1 điểm.**
- **Tâm cắt giá nhiều hơn không tạo giá trị:** Lớp 2 chọn mã cho 7,48%, null 2,57%. Lớp 2 chỉ để hiển thị.
- **Sizing theo đồng thuận hai lớp không thêm gì** (12,72 so 12,87).
- Theo DT5G lúc lập danh mục, S1 ENS1w vượt universe trung bình/tháng: CRISIS +0,86% (21 tháng), BEAR +0,47% (13), NEUTRAL +0,36% (90), BULL +0,69% (21), EX-BULL +0,77% (3).
- Quy đổi thực tế theo quy ước chung: trừ thêm ~1,5 điểm %/năm; chưa đo ở đầu trần pin1M.

## 6. Thiết kế đề xuất cho bản hiển thị `dcf` v3

Ba lớp, mỗi lớp một việc, không lớp nào chặn lệnh:

| Lớp | Nội dung | Dùng để | Bằng chứng |
|---|---|---|---|
| 1 — Giá trị nội tại (mù giá riêng của mã) | Điểm = ENS2 (trung vị 5 phương pháp; luật §5 sau embargo; ENS1w là phương án đối chiếu); **vùng** = [q25; q75] giữa 5 phương pháp; liệt kê từng phương pháp (RIM-VN, DDM, EPV, bội số ngành, hedonic) | Xếp hạng, hiển thị cảnh báo đắt | IC và mục tiêu 2 đạt cả hai era — **nhưng cảnh báo E/P cùng cờ đạt cùng tiêu chí** (§3.3); phần riêng của mô hình = IC phần dư 0,068 / 0,081 |
| 2 — Tâm hiển thị, nhãn bắt buộc "CÓ DÙNG GIÁ QUÁ KHỨ CỦA CHÍNH MÃ" | L2 = Lớp 1 × premium riêng 60 tháng (bản khoá trước); REL chạm tâm tốt hơn (73,6% / 81,9% so với 68,4% / 77,5%, số V2) | Vùng tham chiếu trong báo cáo DD; **cấm dùng chọn mã** | Dùng chọn mã cho 7,48% so với 12,87% của Lớp 1 |
| 3 — Cờ | Cảnh báo đắt đang hiệu lực + số tháng đã kéo dài + **cờ E/P song song (đồng thuận = mức cao)**; cờ "ROE đang nhảy"; cờ "ngân hàng quốc doanh / mã có premium cấu trúc" khi Lớp 1 và Lớp 2 lệch > 40% | Gợi việc cho DD | §3, §4 |

Tham số và lý do (không tham số nào fit theo giá của chính mã):

| Tham số | Giá trị | Lý do góc nhìn VN | Bằng chứng trong vòng này |
|---|---|---|---|
| Cơ sở lợi nhuận | ROE trung vị 5 năm × vốn chủ hiện tại (TS − nợ) | Chu kỳ ngành 3–5 năm; capex đi trước lợi nhuận | Ablation §2: phần hơn ở IS đến từ đây |
| r · g dài hạn | 12,25% · 5,5% | Huy động 12 tháng chuẩn hoá 6,75% + ERP nội địa 5,5 điểm | Giữ như `domestic_v2`; vòng 1 đo r động không đổi kết quả |
| Fade | 10 năm, giữ 0,4 phần ROE vượt r; ngân hàng 0,7 | Ngành cấp phép hồi quy chậm | 0,7 chỉ nhích VCB 0,47 → 0,54; không đổi IC |
| EPV | Doanh thu 12 tháng × biên ròng trung vị 5 năm | Biên hồi quy về trung bình; doanh thu ít nhiễu hơn LN quý | Duy nhất bắt VCS 2015; IC phần dư 0,045 / 0,121 |
| Bội số ngành | Trung vị 60 tháng trước, theo route | "Thị trường VN thực sự trả bao nhiêu" | IC phần dư IS cao nhất (0,101) nhưng OOS 0,041 |
| Hedonic | Đóng băng tại cuối IS | Cuốn chiếu chạy theo giá gần nhất | Đóng băng 0,145 so với cuốn chiếu 0,103 (OOS) |
| Ngưỡng | Rẻ: giá ≤ 0,8 × tâm · Cảnh báo: tâm ≤ 0,67 × giá đủ 6 tháng | Khoá trước, không dò | — |
| Thanh khoản, quy mô | Không đưa vào tâm | Thêm thanh khoản vào hedonic làm IC phần dư âm | Xử lý ở sizing |

Cách dùng để tạo giá trị, xếp theo độ chắc của bằng chứng:
1. **Cảnh báo đắt = "không mở mới / không tăng tỉ trọng", không phải lệnh bán.** Ghi kèm phân phối độ trễ: trung vị 6–13 tháng tới đỉnh, một phần tư tới
   một phần sáu không nguội trong 3 năm. **Bằng chứng V3 không cho thấy mô hình vượt E/P cho công này** (+2,2–3,1 điểm/năm của S7 gần như đều có ở E/P cùng cờ,
   8,55 so 8,83): nếu làm cổng mềm, E/P là mốc đơn giản đã đạt cùng tiêu chí; mô hình là thông tin bổ sung cần kiểm định ngoài mẫu mới.
2. **Vùng mua = giá ≤ 0,8 × tâm Lớp 1.** Cổng rating 8L ≤ 3 giữ như chính sách chất lượng hiện hành của fleet, **nhưng V3 không chứng minh nó tăng lợi nhuận**:
   trên cùng điều kiện nó thêm 0,22 điểm/năm (IS +1,06, OOS −0,60); phần "mất 3,5 điểm khi bỏ cổng" của V2 gồm ~2,3 điểm lợi thế sống sót giả (mã vắng BQ không có rating
   nên bị loại tự động) — xem §5.
3. **Không dùng thời điểm "tâm cắt giá" làm tín hiệu**, không dùng Lớp 2 để xếp hạng, không sizing theo đồng thuận hai lớp.
4. **Ca đổi cấu trúc là việc của DD:** khi cờ ROE nhảy bật, hiển thị cả EPV (nhìn doanh thu và biên) lẫn RIM (nhìn sổ sách)
   và để DD chọn có lý do bằng văn bản. Trung bình các ca có cờ kém thị trường.
5. **Ngân hàng quốc doanh và mã có premium cấu trúc:** Lớp 1 sẽ luôn báo đắt; phải đọc Lớp 2 và nêu premium là giả định.
6. **Mô hình không thay được soát chất lượng sổ sách.** Cần `forensic_flags` hoặc cổng tương đương trước khi tin vùng rẻ.

## 7. Giới hạn trung thực

- **Sống sót còn sót:** VNDirect chỉ có giá từ 2013-01 và thiếu ngày công bố BCTC (dùng cuối quý + 45/90 ngày). 548/640 mã
  vắng BQ không qua cổng thanh khoản nên không vào mẫu. Mã vắng BQ thiếu CFO, cổ tức, rating ⇒ engine FCFE và DDM không
  chạy trên chúng. Chuỗi giá điều chỉnh của VNDirect khác vintage với BQ (chỉ dùng trong nội bộ từng mã). Mức mất sau khi
  ngừng giao dịch là giả định (50%); đổi 0% ↔ 100% làm IC lệch ≤ 0,005 nhưng lợi suất tuyệt đối của universe đổi nhiều hơn.
- **Sức mạnh theo thời gian yếu:** OOS = 4 năm as-of, 15 lát cắt quý, ≈ 1,3 khối 36 tháng; trùng giai đoạn 2020–2021.
- **51 biến thể mô hình + 6 chiến lược + 8 cờ null/tổ hợp + 12 S7/S3f/S1 bổ sung (V3).** ENS1w có trọng số fit trên IS (nay có embargo); DSR < 0,95 ở mọi cấu hình, kể cả N = 80.
- **OOS chỉ là lần nhìn thứ hai (NB-4):** D0, r = 12,25%, g = 5,5% và ngưỡng 0,8 / 0,67 / 6 tháng được chốt sau khi vòng 1 đã thấy 2014-2023; PRELOCK khoá mô hình và tiêu chí, không khoá các tham số
  đó. OOS vì vậy không phải kiểm định ngoài mẫu thật sự; kiểm định ngoài mẫu thật cần dữ liệu sau 2023-10 (chưa đủ 36 tháng nhãn).
- **Lợi suất vượt trội đo so với trung bình số học của universe** nên âm với đa số mã (61% / 59%); mọi tỉ lệ "đúng" phải
  đọc cùng nền vô điều kiện đã ghi cạnh.
- **Route 8L không PIT trước 2026** (bội số ngành, hedonic, EPV, độ bền ngân hàng đều dùng route hiện tại).
- **Cách chọn số cổ phiếu ở lỗi 2 là suy luận** (liên tục với bước nhảy hệ số điều chỉnh giá). Đối chiếu V3 với `oshares_live` (mẫu 80 dòng E/BVPS): lệch > 5% ở 98,7% — nhưng
  `oshares_live` chỉ chứng nhận 5/80 ca, nên chưa kết luận bên nào đúng; nhánh E/BVPS có nhảy vốn hoá > 15% ở 10,3% dòng in-universe (vs ~3% nhánh OS). Chưa chạy độ nhạy thay N.
  Nhánh VND dùng hệ số sự kiện suy từ bước nhảy giá, chưa kiểm bảng GDKHQ.
- **`EBITDA_P0` không dùng được** ⇒ họ EV/EBITDA được thay bằng EV/EBIT; chưa có D&A để dựng lại EBITDA.
- Chưa đo ở quy ước pin1M (đầu trần); chưa mô hình hoá slippage và thuế; MaxDD ~−44% không phù hợp làm sổ độc lập.
- Chuỗi thị trường (lãi suất, tín dụng, tỷ giá, hàng hoá) chưa được kiểm định, chỉ mô tả.
- **Null E/P (B-1) chọn cờ theo k mã/tháng của mô hình** — số cờ nội sinh với mô hình; không thể tái lập đúng số của skeptic (69,3 / 69,5) vì định nghĩa khác; không hiệu chỉnh đa so sánh.
- **S7 không có CI** — mọi so sánh S7 giữa mô hình và E/P chỉ là điểm ước.
- **Panel VNDirect không tái lập từ repo:** CSV thô (62 MB) không commit; chỉ có md5 từng file (`MD5SUMS_delisted.txt`) và script kéo.

## 8. Lệch so với PRELOCK

1. Họ EV/EBITDA dùng EBIT thay EBITDA (phát hiện đơn vị lẫn lộn sau khi khoá).
2. Vốn chủ của ngân hàng lấy BVPS × OShares vì `StLiab`/`LtLiab` = 0 ở nhóm này (1.133 dòng).
3. Thêm sau khi thấy số, gắn nhãn **độ nhạy/giả thuyết**: (a) "cho mã vắng BQ lọt cổng rating" ở S1 và S3f; (b) universe EW
   chỉ-BQ để tách ảnh hưởng sống sót; (c) bảng ngân hàng VCB/BID/CTG và lợi suất của nhóm có cờ ROE nhảy.
4. CI cụm theo mã B = 500 chỉ cho 11 mô hình chính.
5. Lớp 2 khoá trước là L2; REL (cũng khai trước, biến thể 12) chạm tâm tốt hơn — nêu ở §6 như phương án, không tự đổi.
6. Rổ E/P đối chứng ban đầu phụ thuộc thứ tự `set` (không tất định giữa các lần chạy, lệch tới 0,4 điểm CAGR); đã sửa
   sắp theo hạng E/P và kiểm lại bằng hai giá trị `PYTHONHASHSEED`.
7. **V3:** luật §5 chọn ENS2 (không phải ENS1w) sau embargo — áp luật nguyên văn, không đổi PRELOCK. Thêm sau khi thấy số, nhãn **độ nhạy/giả thuyết**: null E/P và 3 tổ hợp cờ, S7 theo loại cờ, S3f_ENS2/S1_ENS2, đối chiếu oshares_live, nền U-static khớp ngưỡng, tách cổng rating (deadin so S2).
8. **V3:** PRELOCK ghi "~23:35" nhưng commit `f303028e8` lúc 23:12:19 +0700; lấy theo commit; PRELOCK.md không chỉnh.

## 9. Lộ trình và việc cần duyệt

| Bước | Nội dung | Ai duyệt |
|---|---|---|
| 0 | quant-skeptic soát V3 (Mike chạy đúng 1 vòng). Trọng tâm đề nghị: null B-1 (cách chọn k cờ/tháng); đối chiếu oshares_live (mẫu 80); chọn ENS2 so ENS1w sau embargo; lập luận "cổng rating chỉ 0,22 điểm" | Mike |
| 1 | Winston: nạp giá + BCTC mã huỷ niêm yết vào BQ (nguồn VNDirect), sửa `EBITDA_P0`, xử lý `oshares_live` cho nhánh E/BVPS (80 mẫu lệch; cần nguồn số CP đã chứng nhận) | Mike |
| 2 | Viết `dcf_multi_vn.py` **song song** engine cũ, chỉ hiển thị: Lớp 1 (điểm + vùng + từng phương pháp), Lớp 2 có nhãn, 3 cờ, **kèm cờ E/P song song**. DD hiển thị cả engine cũ và mới trong một quý | **user** |
| 3 | Chọn Lớp 2 hiển thị: L2 (khoá trước) hay REL (chạm tâm tốt hơn 4–5 điểm, số V2) | **user** |
| 4 | Cổng mềm "cảnh báo đắt ⇒ không mở mới" cho custom30V / sleeve discretionary: **kiến nghị KHÔNG thay E/P bằng ENS1w/ENS2** (E/P đạt cùng tiêu chí, S7 8,55% so 8,83%/8,31%); hoặc chỉ hiển thị. Quyết định thuộc user | **user**, sau bước 0 |
| 5 | Thay tiêu chí "tâm giao giá" bằng "lợi suất sau tín hiệu so với null" **và so với null E/P** trong mọi đánh giá định giá về sau | **user** |

Không đề xuất thay cơ sở FCFE trong `dcf_valuation.py`: bằng chứng ablation chỉ rõ ở OOS. Không wire, không merge, không email; chưa qua quant-skeptic V3 — không CONFIRMED.

## 10. Tái lập và tự kiểm

```
cd agents/Taylor/research/dcf_vn_redesign_20261125c ; PY=/home/trido/thanhdt/wc_venv/bin/python ; export PYTHONHASHSEED=0
# out/ không nằm trong git (parquet bị .gitignore): panel/phụ trợ đọc từ out/ của lần chạy; MD5SUMS ở thư mục này.
(cd calc; $PY a0_fetch_delisted.py)            # VNDirect -> out/delisted/ (669 mã); đối chiếu MD5SUMS_delisted.txt
# out/px_pre2013_d.csv: bq query ticker 2006-01-01..2013-01-31 (Close, Price, Volume)
bash run_stage.sh out b c d e f n              # b_panel, c_models2 (EMBARGO=1 PITMED=1 mặc định), d_metrics2, e_bt2, f_proxy_diag, h_null_ep
EMBARGO=0 bash run_stage.sh out_E c d e n      # nhánh tách NB-3 (cần symlink panel/px từ ../out)
$PY calc/a_engine_total.py ; $PY calc/j_delta.py out_A out_C out ; $PY calc/k_tables.py
$PY calc/l_oshares_xcheck.py                   # cần BQ (oshares_live)
$PY calc/g_selfcheck3.py                       # chạy dưới env -u TZ, TZ=Asia/Ho_Chi_Minh, TZ=America/New_York
```
Tự kiểm độc lập `g_selfcheck3.py`: **21/21 PASS**; sáu lần chạy — ba lần đầu (`out/selfcheck3_{noTZ,ICT,NY}.txt`, seed không ghi) và ba lần V3b với `env -u TZ` + `PYTHONHASHSEED=0`, `TZ=Asia/Ho_Chi_Minh` + `12345`, `TZ=America/New_York` + `777` (`out/selfcheck3b_*.txt`) — cho
đầu ra **giống từng byte** (md5 `2b1e725ee51f42d1c7a03eda49b16bd9` ở cả `out/selfcheck3_{noTZ,ICT,NY}.txt` và `out/selfcheck3b_{noTZ,ICT,NY}.txt`). NAV tính lại từ CSV danh mục lệch ≤ 0,0009 VND
(S1 ENS1w trên 222.461.082.343 VND; S1 ENS2 0,0006 / 254.412.126.912; S1 D0 0,0004; S3f 0,0006; S3f ENS2 0,0006; S7 D0 0,0007; S7 EPN_E2 0,0003); V/B của D0 tính lại bằng vòng lặp thuần lệch tối đa 3,6e-15 (200 dòng);
hedonic đóng băng tính lại từ dòng thô 2015-01→2019-12 lệch ≤ 4,6e-05; IC36 ENS1w (scipy) IS 0,151906 / OOS 0,222679 khớp; U-hit và tỉ lệ cảnh báo đúng (D0, ENS2, ENS1w, EPN_E2) tính lại bằng vòng lặp pandas khớp tuyệt đối;
giá T+1 của holdings tính lại từ `px_t1` thô lệch ≤ 2,2e-16. PIT: `known ≤ time` trên 188.947 dòng, tuổi BCTC tối đa 200 ngày.

**Giới hạn của tự kiểm:** không phủ S7 ENS1w/ENS2 (NAV), không phủ DSR, không phủ `oshares_xcheck`; panel VNDirect không tái lập từ repo (§7).
