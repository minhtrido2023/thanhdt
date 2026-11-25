# Định giá đa proxy cho thị trường Việt Nam — vòng 2 (job Taylor_20261124_160038)

Taylor · 2026-11-25 · CHỈ NGHIÊN CỨU + ĐỀ XUẤT. Không sửa `dcf_valuation.py`, không wire. **Chưa qua quant-skeptic — không
được coi là CONFIRMED.** Tiêu chí khoá trước ở `PRELOCK.md` (commit `f303028e8`, trước khi chạy mô hình mới).
Quy ước: tiền nhàn rỗi **pin0% (đầu sàn)**, phí 0,1%/chiều, khớp T+1, mã ngừng giao dịch mất 50% trên giá cuối (cận 0%
và 100% báo kèm). IS = as-of 2014-01→2019-12, OOS = 2020-01→2023-10.

## 0. Kết luận trước

1. **Mục tiêu 2 (cảnh báo đắt) ĐẠT theo tiêu chí khoá trước; mục tiêu 1 (phát hiện rẻ rồi giá chạm tâm) KHÔNG ĐẠT.**
   - Cảnh báo đắt (tâm ≤ 0,67 × giá đủ 6 tháng liền) của bộ mô hình được chọn đúng 70,4% (IS) / 69,9% (OOS), so với nền
     vô điều kiện 61,4% / 58,7% và null "giá so với trung vị giá 5 năm của chính mã" 63,8% / 61,4%. Tỉ lệ báo sai (mã vẫn
     vượt thị trường > 35% sau 36 tháng) 15,5% / 17,1%, thấp hơn nền 21,9% / 21,6%.
   - Phát hiện rẻ: sau tín hiệu "giá ≤ 0,8 × tâm", 66,4% / 68,3% trường hợp giá đi lên chạm tâm trong 36 tháng. Nhưng
     null giá-trung-vị-5-năm làm được 70,2% / 78,4%. **Tiêu chí "tâm phải giao với giá" bị một phép null tầm thường đáp
     ứng tốt hơn mọi mô hình định giá** — nó đo tính hồi quy của giá, không đo chất lượng định giá.
2. **Cảnh báo đắt có độ trễ dài và không phải tín hiệu bán.** Trung vị 13 tháng (IS) / 6 tháng (OOS) từ lúc cảnh báo tới
   đỉnh giá; 26,4% / 16,6% trường hợp giá không giảm nổi 15% trong 36 tháng. Ca VNM: cảnh báo đầu tiên 2015-06, giá tăng
   thêm 196% rồi mới đạt đỉnh 2017-12 (30 tháng sau), sau đó giảm 36% tới cuối 2022.
3. **Bộ mô hình được chọn theo luật IS = tổ hợp đa proxy `ENS1w`** (trung bình có trọng số của RIM-VN, cổ tức chiết
   khấu, sức sinh lời EPV, bội số ngành, hồi quy hedonic). IC 36 tháng 0,149 [0,07; 0,23] (IS) / 0,204 [0,15; 0,25]
   (OOS), CI theo khối năm. Còn thông tin sau khi loại E/P, B/P và quy mô: 0,073 [0,03; 0,11] / 0,106 [0,06; 0,15].
4. **Đa proxy không thắng rõ mô hình đơn.** RIM-VN một mình (D0) cho IC tương đương (0,137 / 0,208) và danh mục tốt hơn
   tổ hợp (14,99% so với 13,51%/năm). Trong 39 proxy đo được, gần hết thông tin nằm ở hai nhóm: lợi suất (E/P, cổ tức,
   CFO/P) và chất lượng bền (ROE và biên ròng trung vị 5 năm). Tăng trưởng, B/P, S/P, FSCORE không dự báo được gì ở 36 tháng.
5. **Tạo giá trị: lens tốt, chưa phải alpha.** Rổ "vùng mua" theo tổ hợp (sổ 50 tỷ, sàn thanh khoản 1 tỷ/phiên, có trần
   vị thế) đạt 13,51%/năm so với universe 5,96%, thắng 9/13 năm. Nhưng không hơn rổ E/P đối chứng công bằng ở OOS
   (20,43% so với 20,87%) và DSR phần vượt trội 0,38 < 0,95. Giá trị rõ nhất là **tránh đắt**: bỏ các mã đang bị cảnh
   báo khỏi universe thêm 2,3 điểm %/năm (8,30% so với 5,96%), dương ở cả IS và OOS.
6. **Ba đính chính so với vòng 1** (sau khi sửa 9 lỗi skeptic, §2):
   - "Lỗi gốc của engine là cơ sở FCFE" chỉ đúng ở OOS. Ablation sạch: chỉ đổi dòng tiền FCFE → lợi nhuận thặng dư thì
     IC IS không đổi (0,097 → 0,087), IC OOS mới tăng (0,028 → 0,200).
   - Thiên lệch sống sót là thật và đo được: thêm 75 mã vắng BQ (gồm FLC, ROS, HVG, KSA…) làm universe EW giảm từ 8,09%
     xuống 5,96%/năm; IC của D0 giảm 0,012 (IS) / 0,023 (OOS).
   - Mô hình **không nhận ra nhóm doanh nghiệp "sổ sách đẹp rồi sụp"**: FLC, HAI, ART, AMD, KSA được xếp rẻ (tâm/giá
     trung vị 1,0–3,3) trước khi mất 36–95% giá.

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

**IC 36 tháng đơn biến** (`out/proxy_ic.csv`, [CI khối năm]; dấu đã đảo để "cao = tốt"):

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

## 2. Sửa 9 lỗi skeptic và delta

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

Bảng chính (BQ + mã vắng BQ; IS / OOS). U-hit = sau tín hiệu rẻ, giá đi lên chạm tâm trượt trong 36 tháng. U-static =
giá chạm mức tâm lúc phát tín hiệu. "Đúng" = sau cảnh báo đắt, mã kém universe trong 36 tháng. Nguồn `out/metrics2.csv`.

| Mô hình | Độ phủ | IC 36T [CI khối năm] | IC phần dư sau E/P, B/P, quy mô | U-hit | U-static | Cảnh báo đúng | Báo sai | 5 ca |
|---|---|---|---|---|---|---|---|---|
| A_pit (FCFE) | 39 / 41% | 0,096 [0,00; 0,19] / 0,030 [−0,03; 0,11] | 0,063 / 0,008 | 39 / 44% | 33 / 40% | 59 / 61% | 21 / 20% | 1/2 |
| A_RI | 39 / 40% | 0,082 [0,01; 0,14] / 0,204 [0,16; 0,24] | 0,014 / 0,086 | 42 / 56% | 50 / 60% | 65 / 69% | 19 / 17% | 1/2 |
| D0 (RIM-VN) | 95 / 97% | 0,137 [0,06; 0,22] / 0,208 [0,15; 0,25] | 0,046 / 0,110 | 60 / 71% | 62 / 68% | 71 / 68% | 15 / 19% | 3/5 |
| D0B | 95 / 96% | 0,116 [0,04; 0,20] / 0,207 [0,15; 0,25] | 0,025 / 0,097 | 62 / 68% | 57 / 63% | 72 / 68% | 16 / 19% | 4/5 |
| DDM | 28 / 29% | 0,048 [−0,03; 0,12] / 0,080 [0,04; 0,11] | −0,015 / 0,048 | 54 / 55% | 53 / 63% | 69 / 49% | 18 / 23% | 1/1 |
| EPV | 62 / 64% | 0,120 [0,07; 0,17] / 0,166 [0,12; 0,21] | 0,045 / 0,121 | 59 / 73% | 59 / 67% | 68 / 68% | 16 / 20% | 4/5 |
| MULT | 85 / 99% | 0,133 [0,03; 0,24] / 0,117 [0,04; 0,20] | 0,101 / 0,041 | 63 / 65% | 60 / 58% | 68 / 71% | 15 / 14% | 1/4 |
| HEDf | 82 / 96% | 0,065 [−0,12; 0,24] / 0,145 [0,08; 0,22] | −0,004 / 0,034 | 57 / 66% | 56 / 58% | 70 / 70% | 18 / 16% | 2/4 |
| ENS1 | 95 / 96% | 0,134 [0,07; 0,21] / 0,238 [0,19; 0,28] | 0,044 / 0,124 | 61 / 67% | 60 / 64% | 72 / 70% | 16 / 18% | 3/5 |
| **ENS1w (chọn)** | 99 / 99% | **0,149 [0,07; 0,23] / 0,204 [0,15; 0,25]** | **0,073 [0,03; 0,11] / 0,106 [0,06; 0,15]** | 66,4 / 68,3% | 63,7 / 62,4% | **70,4 / 69,9%** | **15,5 / 17,1%** | 3/5 |
| ENS2 | 99 / 99% | 0,145 [0,05; 0,23] / 0,190 [0,14; 0,23] | 0,068 / 0,081 | 65 / 67% | 62 / 61% | 70 / 69% | 15 / 19% | 3/5 |
| META | 99 / 99% | 0,140 [0,05; 0,23] / 0,194 [0,15; 0,24] | 0,066 / 0,085 | 66 / 67% | 62 / 60% | 70 / 69% | 15 / 18% | 3/5 |
| REL *(giá quá khứ)* | 81 / 91% | 0,131 [0,05; 0,20] / 0,192 [0,14; 0,24] | 0,082 / 0,107 | 73,6 / 81,9% | 63 / 69% | 69 / 68% | 20 / 19% | 3/5 |
| L2 trên ENS1w *(giá quá khứ)* | 80 / 92% | 0,113 [0,05; 0,18] / 0,179 [0,14; 0,21] | 0,069 / 0,065 | 68,4 / 77,5% | 61 / 62% | 64 / 70% | 22 / 17% | 2/5 |
| **Null N0** | 82 / 93% | 0,010 [−0,10; 0,12] / 0,060 [−0,01; 0,10] | 0,026 / 0,076 | **70,2 / 78,4%** | 59 / 70% | 63,8 / 61,4% | 20 / 22% | 1/5 |
| E/P | 98 / 99% | 0,128 [0,05; 0,20] / 0,255 [0,23; 0,28] | — | — | — | — | — | — |
| Nền vô điều kiện | | | | | 69,5 / 68,1% | 61,4 / 58,7% | 21,9 / 21,6% | |

CI cụm theo mã (B = 500) của ENS1w: [0,10; 0,20] / [0,15; 0,26] — hẹp hơn CI khối năm ở IS, đúng như skeptic cảnh báo.

**Đối chiếu tiêu chí khoá trước:**
- **Mục tiêu 1 — KHÔNG ĐẠT.** U-hit ≥ 60% thì có (66,4% / 68,3%), nhưng thấp hơn null 3,8 / 10,1 điểm thay vì hơn 5 điểm;
  U-static (63,7% / 62,4%) thấp hơn cả nền "một mã bất kỳ tăng ≥ 25% tại một thời điểm trong 36 tháng" (69,5% / 68,1%).
  Bản có dùng giá quá khứ tốt nhất (REL) cũng chỉ hơn null 3,4 / 3,5 điểm. Tỉ lệ cắt giá 36 tháng mỗi phía của ENS1w:
  phía đắt 67% / 53%, phía rẻ 72% / 78%; null 68% / 65% và 80% / 85%.
- Điều phân biệt mô hình với null là **chuyện xảy ra sau khi chạm**: lợi suất vượt trội 36 tháng sau tín hiệu rẻ của
  ENS1w là −0,26 / −0,16 (log), tỉ lệ thắng universe 41,5% / 45,0% (nền 38,6% / 41,3%); của null là −0,49 / −0,31 và
  29,8% / 36,9%. Tín hiệu rẻ của null là "mã vừa rơi mạnh", còn rơi tiếp.
- **Mục tiêu 2 — ĐẠT** cho ENS1w (và cho D0, ENS1, ENS2, MULT, HEDf): cả bốn điều kiện ở cả hai era. Độ trễ ở §0 mục 2.
- **Độ tin cậy theo độ phân tán giữa các phương pháp — không đạt phép thử khoá trước.** Tercile phân tán thấp có IC cao
  hơn (0,126 so với 0,074 IS; 0,190 so với 0,117 OOS) và U-static cao hơn (71% / 61% so với 57% / 56%), nhưng U-hit OOS
  thấp hơn (63,0% so với 68,5%). Vùng [q25; q75] giữa các phương pháp rộng trung vị 0,32 log (khoảng ±17%); giá nằm trong
  vùng 20,9% số tháng.
- **Chống overfit:** META (chọn mô hình theo ngành trên IS — bất động sản → DDM với IC IS 0,55, điện → MULT) không hơn ENS2
  ở OOS (0,194 so với 0,190). Hedonic cuốn chiếu kém bản đóng băng (0,103 so với 0,145); thêm thanh khoản vào hedonic làm
  IC phần dư âm (−0,060 / −0,041). Cờ "ROE đang nhảy" không cải thiện gì ở mức universe (D0J so với D0: 0,119 so với
  0,137 IS); 1.489 dòng có cờ có lợi suất vượt trội 36 tháng −0,31 so với −0,25 toàn mẫu — phần lớn cú nhảy ROE là đỉnh chu kỳ.
- **Luật chọn (§5 PRELOCK):** điểm IS = (U-hit − U-hit null) + (cảnh báo đúng − nền): ENS1w +0,053, META +0,041, ENS2
  +0,039, D0J +0,023, D0B +0,020, ENS1 +0,008, D0 −0,003. ENS1w hơn bản không fit gần nhất (ENS2) 1,4 điểm ⇒ chọn ENS1w.
  Trọng số IS: MULT 0,133 · EPV 0,120 · D0B 0,116 · HEDf 0,065 · DDM 0,048 (gần đều).

## 4. Năm ca kiểm (PIT; `out/cases2.csv`; NA = mô hình không chạy được)

| Ca | A_pit | D0 | D0B | EPV | MULT | ENS1w | REL | L2 | Null |
|---|---|---|---|---|---|---|---|---|---|
| VCS 2015: ≥ 50% tháng tâm > giá | ✗ 33% | ✗ 0% | ✗ 0% | **✓ 75%** | ✗ 0% | ✗ 0% | ✗ 42% | ✗ 0% | ✗ |
| DGC 2016: ≥ 50% tháng tâm > giá | NA | ✓ 100% | ✓ | ✓ | ✗ 8% | ✓ 100% | ✗ 0% | ✗ 0% | ✗ |
| VNM 2011: ≥ 50% tháng tâm > giá | NA | ✗ 0% | ✓ 50% | ✗ 8% | NA | ✗ 25% | ✓ 75% | ✓ 83% | ✗ |
| HPG: tâm tăng qua 2019 và có tháng tâm > giá | NA | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ |
| VNM 07/2015–12/2016: ≥ 50% tháng tâm < giá | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Điểm | 1/2 | 3/5 | 4/5 | 4/5 | 1/4 | 3/5 | 3/5 | 2/5 | 1/5 |

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

## 5. Tạo giá trị (mục tiêu 4) — luật khoá trước (`out/bt2_summary.csv`, `bt2_dsr.json`)

2014-06→2026-10, sổ 50 tỷ, sàn GTGD ≥ 1 tỷ/phiên, trần vị thế, pin0%, đã trừ phí. S1 = giữ mã có giá ≤ 0,8 × tâm và
rating 8L ≤ 3, ra khi giá > tâm.

| Chiến lược | CAGR | IS | OOS | Sharpe | MaxDD | Số mã | Turnover/tháng |
|---|---|---|---|---|---|---|---|
| S1 tổ hợp ENS1w | 13,51% | 5,68% | 20,43% | 0,66 | −44,0% | 38 | 35,9% |
| S1 RIM-VN D0 | **14,99%** | 6,47% | 22,54% | 0,74 | −40,7% | 36 | 34,1% |
| S1 ENS2 · MULT · ENS1 | 14,08 · 12,46 · 12,35% | 6,59 · 4,39 · 6,00% | 20,66 · 19,60 · 17,88% | 0,69 · 0,60 · 0,63 | | | |
| S3f đối chứng E/P công bằng (cùng số mã với S1 tổ hợp) | 13,14% | 4,46% | 20,87% | 0,65 | −42,1% | 38 | 35,7% |
| S3f cùng số mã với S1 D0 | 12,69% | 3,42% | 20,99% | 0,63 | −42,0% | 36 | 35,5% |
| S2 tổ hợp, không cổng rating | 10,05% | 0,36% | 18,77% | 0,49 | −49,2% | 63 | 37,3% |
| S1 engine FCFE (A_pit) | 8,88% | 4,57% | 12,59% | 0,50 | −44,1% | 34 | 36,5% |
| S1 theo Lớp 2 (L2) · REL · null N0 | 8,69 · 7,75 · 2,57% | 1,77 · 2,68 · −7,21% | 14,77 · 12,13 · 11,44% | | | | |
| S5 sizing theo đồng thuận hai lớp | 13,57% | 5,48% | 20,73% | 0,67 | −43,5% | 38 | 38,7% |
| **S7 universe bỏ mã đang bị cảnh báo đắt** (ENS1w · D0) | 8,30 · 9,00% | 2,67 · 2,91% | 13,19 · 14,30% | 0,44 · 0,47 | −51,2 · −49,5% | 186 · 172 | |
| Universe EW (cùng sàn, có mã vắng BQ) | 5,96% | 1,24% | 10,03% | 0,36 | −52,0% | 265 | 27,1% |
| Universe EW chỉ mã BQ (như vòng 1) | 8,09% | 4,62% | 11,04% | 0,44 | −50,6% | 252 | |

- **Phán quyết theo prelock:** S1 tổ hợp > universe ở cả IS và OOS (đạt); S1 ≥ E/P công bằng ở OOS (**trượt**, 20,43 so
  với 20,87); DSR phần vượt trội so với universe 0,38, DSR tuyệt đối 0,87, cả hai < 0,95 với N = 57 (**trượt**). ⇒ **lens,
  chưa phải alpha.** S1 tổ hợp thắng universe 9/13 năm; thua 2014, 2016, 2019, 2021.
- **D0 đơn lẻ làm danh mục tốt hơn tổ hợp** và hơn E/P công bằng ở cả hai era (+3,05 / +1,55 điểm), Sharpe chủ động so với
  E/P 0,29, thắng universe 11/13 năm; DSR phần vượt trội 0,56 — vẫn dưới ngưỡng. D0 không phải mô hình luật IS chọn, nên
  đây là **quan sát, không phải kết luận**.
- **Sức chứa:** kết quả gần như không đổi theo sàn thanh khoản (12,1% → 13,5% → 12,7%) và trần vị thế chỉ lấy đi 0,6
  điểm ⇒ phần vượt trội không đến từ mã kém thanh khoản. Nhưng ở sàn 5 tỷ, IS chỉ 0,43%/năm (universe cùng sàn −4,51%):
  với nhóm thanh khoản cao, lợi thế tuyệt đối chỉ xuất hiện từ 2020.
- **Sống sót trong danh mục:** mã vắng BQ không có rating 8L nên S1 tự loại chúng — một lợi thế giả. Độ nhạy cho lọt hết
  qua cổng rating: S1 tổ hợp 13,51% → 11,13% (IS 2,10%, OOS 19,19%), 10,0% tỉ trọng nằm ở mã về sau rời sàn; S1 D0 14,99%
  → 12,61%; E/P công bằng cùng điều kiện 12,39%. **Cận dưới trung thực của S1 tổ hợp là ~11,1%/năm, và ở cận đó nó thua E/P.**
- **Tâm cắt giá nhiều hơn không tạo giá trị:** dùng Lớp 2 để chọn mã cho 8,69%, null 2,57%. Lớp 2 chỉ để hiển thị.
- **Sizing theo đồng thuận hai lớp không thêm gì** (13,57% so với 13,51%).
- Theo DT5G lúc lập danh mục, S1 tổ hợp vượt universe trung bình/tháng: CRISIS +0,82% (21 tháng), BEAR +0,36% (13),
  NEUTRAL +0,39% (90), BULL +1,12% (21), EX-BULL +0,72% (3).
- Quy đổi thực tế theo quy ước chung: trừ thêm ~1,5 điểm %/năm; chưa đo ở đầu trần pin1M.

## 6. Thiết kế đề xuất cho bản hiển thị `dcf` v3

Ba lớp, mỗi lớp một việc, không lớp nào chặn lệnh:

| Lớp | Nội dung | Dùng để | Bằng chứng |
|---|---|---|---|
| 1 — Giá trị nội tại (mù giá riêng của mã) | Điểm = ENS1w; **vùng** = [q25; q75] giữa 5 phương pháp; liệt kê từng phương pháp (RIM-VN, DDM, EPV, bội số ngành, hedonic) | Xếp hạng, cảnh báo đắt, cổng "không mở mới khi đắt" | IC và mục tiêu 2 đạt cả hai era |
| 2 — Tâm hiển thị, nhãn bắt buộc "CÓ DÙNG GIÁ QUÁ KHỨ CỦA CHÍNH MÃ" | L2 = Lớp 1 × premium riêng 60 tháng (bản khoá trước); REL chạm tâm tốt hơn (73,6% / 81,9% so với 68,4% / 77,5%) | Vùng tham chiếu trong báo cáo DD; **cấm dùng chọn mã** | Dùng chọn mã cho 8,69% so với 13,51% của Lớp 1 |
| 3 — Cờ | Cảnh báo đắt đang hiệu lực + số tháng đã kéo dài; cờ "ROE đang nhảy"; cờ "ngân hàng quốc doanh / mã có premium cấu trúc" khi Lớp 1 và Lớp 2 lệch > 40% | Gợi việc cho DD | §3, §4 |

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
1. **Cảnh báo đắt = "không mở mới / không tăng tỉ trọng", không phải lệnh bán.** Ghi kèm phân phối độ trễ: trung vị 6–13
   tháng tới đỉnh, một phần tư tới một phần sáu không nguội trong 3 năm.
2. **Vùng mua = giá ≤ 0,8 × tâm Lớp 1 VÀ rating 8L ≤ 3.** Cổng rating là bắt buộc: bỏ cổng mất 3,5 điểm %/năm và IS về 0.
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
- **51 biến thể mô hình + 6 chiến lược.** ENS1w có trọng số fit trên IS; số IS của nó lạc quan nhẹ, OOS mới là phép thử.
  DSR < 0,95 ở mọi cấu hình.
- **Lợi suất vượt trội đo so với trung bình số học của universe** nên âm với đa số mã (61% / 59%); mọi tỉ lệ "đúng" phải
  đọc cùng nền vô điều kiện đã ghi cạnh.
- **Route 8L không PIT trước 2026** (bội số ngành, hedonic, EPV, độ bền ngân hàng đều dùng route hiện tại).
- **Cách chọn số cổ phiếu ở lỗi 2 là suy luận** (liên tục với bước nhảy hệ số điều chỉnh giá), chưa đối chiếu với
  `oshares_live` vì BQ lỗi trong sandbox. 4.675 dòng giữ OShares dù lệch với vốn chủ/BVPS.
- **`EBITDA_P0` không dùng được** ⇒ họ EV/EBITDA được thay bằng EV/EBIT; chưa có D&A để dựng lại EBITDA.
- Chưa đo ở quy ước pin1M (đầu trần); chưa mô hình hoá slippage và thuế; MaxDD ~−44% không phù hợp làm sổ độc lập.
- Chuỗi thị trường (lãi suất, tín dụng, tỷ giá, hàng hoá) chưa được kiểm định, chỉ mô tả.

## 8. Lệch so với PRELOCK

1. Họ EV/EBITDA dùng EBIT thay EBITDA (phát hiện đơn vị lẫn lộn sau khi khoá).
2. Vốn chủ của ngân hàng lấy BVPS × OShares vì `StLiab`/`LtLiab` = 0 ở nhóm này (1.133 dòng).
3. Thêm sau khi thấy số, gắn nhãn **độ nhạy/giả thuyết**: (a) "cho mã vắng BQ lọt cổng rating" ở S1 và S3f; (b) universe EW
   chỉ-BQ để tách ảnh hưởng sống sót; (c) bảng ngân hàng VCB/BID/CTG và lợi suất của nhóm có cờ ROE nhảy.
4. CI cụm theo mã B = 500 chỉ cho 11 mô hình chính.
5. Lớp 2 khoá trước là L2; REL (cũng khai trước, biến thể 12) chạm tâm tốt hơn — nêu ở §6 như phương án, không tự đổi.
6. Rổ E/P đối chứng ban đầu phụ thuộc thứ tự `set` (không tất định giữa các lần chạy, lệch tới 0,4 điểm CAGR); đã sửa
   sắp theo hạng E/P và kiểm lại bằng hai giá trị `PYTHONHASHSEED`.

## 9. Lộ trình và việc cần duyệt

| Bước | Nội dung | Ai duyệt |
|---|---|---|
| 0 | quant-skeptic soát báo cáo này. Trọng tâm đề nghị: cách chọn N ở lỗi 2; cổng thanh khoản và mức mất của mã vắng BQ; trọng số ENS1w fit IS; định nghĩa nền | Mike |
| 1 | Winston: nạp giá + BCTC mã huỷ niêm yết vào BQ (nguồn VNDirect đã kiểm truy cập được), sửa `EBITDA_P0`, kiểm `oshares_live` trong sandbox | Mike |
| 2 | Viết `dcf_multi_vn.py` **song song** engine cũ, chỉ hiển thị: Lớp 1 (điểm + vùng + từng phương pháp), Lớp 2 có nhãn, 3 cờ. DD hiển thị cả engine cũ và mới trong một quý | **user** |
| 3 | Chọn Lớp 2 hiển thị: L2 (khoá trước) hay REL (chạm tâm tốt hơn 4–5 điểm) | **user** |
| 4 | Quyết định có đưa "cảnh báo đắt ⇒ không mở mới" thành cổng mềm cho custom30V / sleeve discretionary hay chỉ hiển thị | **user**, sau bước 0 |
| 5 | Thay tiêu chí "tâm giao giá" bằng "lợi suất sau tín hiệu so với null" trong mọi đánh giá định giá về sau | **user** |

Không đề xuất thay cơ sở FCFE trong `dcf_valuation.py` ở vòng này: bằng chứng ablation chỉ rõ ở OOS.

## 10. Tái lập và tự kiểm

```
cd agents/Taylor/research/dcf_vn_redesign_20261124b/calc ; PY=/home/trido/thanhdt/wc_venv/bin/python
$PY a0_fetch_delisted.py     # VNDirect -> out/delisted/ (669 mã; không commit CSV thô)
# out/px_pre2013_d.csv: bq query ticker 2006-01-01..2013-01-31 (Close, Price, Volume)
$PY b_panel.py ; $PY a_engine_total.py ; $PY c_models2.py ; $PY d_metrics2.py ; $PY e_bt2.py ; $PY f_proxy_diag.py
$PY g_selfcheck2.py          # cũng chạy dưới `env -u TZ` và `TZ=America/New_York`
```
Self-check độc lập (`out/selfcheck2.log`): 13/13 PASS, kết quả giống nhau ở ba cấu hình múi giờ. NAV tính lại từ CSV danh
mục lệch 0,0014 VND trên 238.657.809.111 VND (S1 tổ hợp) và 0,0004 VND (S1 D0); V/B của D0 tính lại bằng vòng lặp thuần
lệch tối đa 3,6e-15 trên 200 dòng; hệ số hedonic đóng băng tính lại từ dòng thô 2015-01→2019-12 lệch tối đa 4,8e-05; IC36,
U-hit và tỉ lệ cảnh báo đúng tính lại bằng đường code khác (scipy, vòng lặp pandas) khớp tới 1e-9. PIT: `known ≤ time`
trên 188.947 dòng.
