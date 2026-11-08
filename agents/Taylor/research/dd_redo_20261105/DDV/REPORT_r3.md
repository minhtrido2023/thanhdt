# DDV — DD làm lại VÒNG 3 (08/11/2026, job `Taylor_20261108_153738`) — áp/kiểm đính chính `../TOP5B_CORRECTIONS_20261108.md` mục DDV

> NGHIÊN CỨU nội bộ, không phải khuyến nghị. Chưa qua phản biện cuối. Số: `calc_r3/model_r3.py` → `calc_r3/model_r3_out.json` (chạy 2 lần, `cmp` trùng byte) → `calc_r3/make_summary_r3.py` → `SUMMARY.json` (r2: `SUMMARY_r2.json`, `REPORT_r2.md`). Giả định khoá ở `calc_r3/assumptions_r3.json`; md5 đã chốt TRƯỚC khi chạy/so giá (`calc_r3/LOCK_md5.txt` phần 1). Nguồn BCTC: BCTC riêng Q3/2026 (bản EN, `../../dd_DDV_20261026/src/en_p1.txt`).

## 0. Kết luận (headline ở cỡ CK tham chiếu 5 tỷ)
| Ba con số (đ/cp) | Trước CK | Sau CK 5 tỷ (1,47%) |
|---|---|---|
| **Tâm** (kỳ vọng trọng số lưới kết cục) | 16.149 | **15.911** |
| **P50 kết cục** | — | **15.919** |
| Giá trị tại tham số trung tâm (cơ sở, m=1, Δr=0, Q4 như Q3, trừ lãi gửi 35,4) | 16.700 | 16.454 |
| **P10 / P90 kết cục** | — | **13.315 / 18.573** |

- n = **405 kết cục**; min 11.308, max 22.143 (sau CK). **37,9% trọng số nằm dưới giá**.
- Giá **đóng cửa 06/11/2026: 15.200** (BQ) ⇒ thấp hơn tâm 4,5%, cao hơn P10 14,2% ⇒ **TRONG vùng** (nửa dưới, giữa P25 14.471 và P50). r2: TRONG vùng ⇒ **nhãn không đổi**.
- **Cỡ sleeve thật (dòng riêng):** 40 triệu, CK 0,13% ⇒ tâm 16.128, P10/P90 13.496 / 18.826, TRONG vùng. 10/20 triệu: CK 0,07% / 0,09%.
- Tâm < giá trị tại tham số trung tâm 0,5k vì nhánh xấu đường 2027 (w 0,45) nặng hơn nhánh tốt (0,15). Liven đã ra khỏi lưới. **Đính chính:** KHÔNG phải "mọi trục đối xứng" — trục kịch bản 2027 lệch (0,45/0,40/0,15 với −185/+107/+373) và trục trừ lãi gửi 70,9/35,4/0 có trung điểm 35,4 nằm nửa trên khoảng thực; theo skeptic ~49% trọng số đuôi trên P90 đến từ nhánh "tốt" (w 0,15) và ~70% từ nhánh "không trừ lãi" ⇒ P90 phụ thuộc đáng kể hai nhánh trọng số nhỏ/đầu lạc quan này.
- ⚠️ **CAVEAT (không đổi bảng trên):** DT chuẩn hoá 5.652 (FY2025) là NĂM ĐỈNH lịch sử (trước đó tối đa 3.392; DAP ở đỉnh nhiều năm); TB 2021–25 = 3.710 thấp hơn 34%, ngoài ±20% của trục 0,8–1,2. Dùng TB 2021–25 thì tâm ~12.452 và nhãn sang TRÊN (§2). LN giữa chu kỳ 229 nằm giữa hai cách tính cùng cửa sổ (112 cho 2015–25; 284 cho 2021–25). Headline giữ 5.652 nhưng nhãn TRONG phụ thuộc lựa chọn này.
- **So r2: tâm 13.109 → 15.911 (+2.802, +21,4%)**; P10 10.115 → 13.315; P90 16.270 → 18.573. Điểm của skeptic 14.388 (13.840–14.740): khớp phần skeptic đã tính (bước 1–6 của tôi = 14.754 ≈ cận trên skeptic); phần cao hơn đến từ #6 (DT có cơ sở, +271) và #5 (khoản trừ lãi gửi, +886 — skeptic ước +0,5–1,0k nhưng chưa đưa vào điểm).

## 1. Kiểm từng đính chính (cầu r2 → r3, mỗi bước đổi một thứ)
Control: chạy lại `calc/model_r2.py` ra **13.109 / 10.115 / 12.823 / 16.270, 76,9% dưới giá** = trùng r2; hàm r3 cấu hình r2 tái lập từng kết cục (sai khác tối đa 0,0 đ/cp).

| Bước | Tâm | Δ | P10 / P90 | Kết luận kiểm |
|---|---|---|---|---|
| 0 r2 (giá + CK 04/11) | 13.109 | — | 10.115 / 16.270 | trùng |
| 1 Giá + CK 06/11 (giá 15.200 không đổi; CK 1,447% → 1,473%) | 13.106 | −3 | 10.113 / 16.265 | — |
| 2 **#1 VLĐ**: tiền ròng = sổ BCTC 1.108 | 14.717 | +1.611 | 11.724 / 17.876 | **ĐÚNG.** Tái lập số skeptic: VLĐ ròng đủ chân (PT KH + trả trước NB + HTK − PT NB − KH trả trước) 30/09 = 219,4+130,1+836,6−569,4−34,9 = **581,8** > 01/01 kiểm toán 23,8+82,8+693,9−321,2−15,4 = **463,9** ⇒ tiền 30/09 không bị nợ NCC thổi phồng trên cơ sở ròng; r2 chỉ lấy chân PT NB/PT KH so mốc 30/06 (đỉnh HTK 905,8) = một chiều. Tôi chọn **bỏ chuẩn hoá** (sổ sách, luật 03/11), KHÔNG chọn mốc 01/01 một chân (−355, skeptic dùng cho điểm 14.388) vì nó vẫn giữ lỗi một chân. |
| 3 **#2** bỏ hệ số giữa chu kỳ 0,8/1,0/1,1 theo kịch bản | 15.320 | +603 | 13.025 / 17.631 | **ĐÚNG.** Biên chu kỳ 4,05% đã gộp 2016 lỗ −470,3 tỷ (BQ); trục 0,8…1,2 đều vẫn giữ. Trùng số skeptic (+603). |
| 4 **#3** RONIC = Ke (mọi ô, cả f27 và terminal) | 14.589 | −731 | 12.458 / 16.755 | **ĐÚNG** (moat NONE, quy ước 08/11, tiền lệ HPG). Skeptic −675 tính trước bước 3; sau bước 3 terminal lớn hơn nên −731. |
| 5 **#4** Liven 217 tỷ theo sổ (xác suất mất → độ nhạy) | 14.736 | +147 | 12.590 / 16.777 | **ĐÚNG.** BCTC Q3 không có văn bản nợ quá hạn. Trùng số skeptic. |
| 6 **#7** trục Q4 đối xứng ±50 quanh Q3 thật (−54,4/−4,4/+45,6) | 14.754 | +18 | 12.612 / 16.800 | **ĐÚNG** (skeptic +19). VCSH dùng BCTC 2.208,2 thay 2.214 (chỉ ảnh hưởng kiểm chéo ROE). |
| 7 **#6** DT chuẩn hoá 5.500 [UL] → **5.652 = FY2025** (BQ, 4 quý) | 15.025 | +271 | 12.852 / 17.133 | **ĐÚNG** (5.500 không có dòng cơ sở). Chọn năm đủ gần nhất làm cơ sở dữ liệu; hai chiều ở §2 (TB 2021–25 3.709,7 / LTM 6.406,2). **Caveat (skeptic vòng 3):** 5.652 là năm ĐỈNH lịch sử (trước đó tối đa 3.392), TB 2021–25 thấp hơn 34% — ngoài ±20% của trục 0,8…1,2 nên trục đó KHÔNG phủ rủi ro này; lập luận "đã phủ/đếm đôi" trước đây bị bỏ. DT không đưa vào lưới chỉ vì quy ước giữ lưới r3; rủi ro hiển thị ở độ nhạy §2 (TB 2021–25 → tâm 12.452, nhãn TRÊN). |
| 8 **#5** khoản trừ lãi gửi: 55,6 cố định → trục **70,9 / 35,4 / 0** (0,25/0,5/0,25) | **15.911** | +886 | 13.315 / 18.573 | **KIỂM MỘT PHẦN — hướng đúng, số chính xác CHƯA KIỂM.** Khoản trừ phải bằng thu nhập TC ròng LỊCH SỬ nằm trong biên 2015–25, không phải lãi hiện tại. Cận trên = lãi gửi hiện tại trên tiền thật 30/09 (22,15 tỷ/quý ×4 ×0,8 = 70,9; r2 dùng 55,6 vì scale theo tiền đã chuẩn hoá). Cận dưới 0 là **đầu LẠC QUAN** (không phải bảo thủ): proxy lãi tiền gửi dương từ 2018 nên trừ 0 là mức trừ thấp nhất. Dữ kiện: 2015–20 DDV nợ vay NH 260–1.050 tỷ (BQ `StDebt_P0`); 2023/2024 DT tài chính thuần +43/+50 tỷ trước thuế (VND 02/06/2025) < lãi hiện tại 88,6. Tự kiểm của skeptic: proxy NP/0,8−EBIT 2023/24 = +49/+42 tỷ (khớp VND +43/+50), TB 2015–25 −9…+26 tỷ/năm trước thuế; trung điểm 35,4 của r3 nằm nửa TRÊN khoảng đó. Thiếu thu nhập TC kiểm toán 2015–22 (BQ không có cột) ⇒ để làm trục đối xứng quanh trung điểm, không phải số chốt. +886 nằm trong ước skeptic +0,5–1,0k. |

**#8 (kỳ hạn/giá):** ĐÚNG, giá 06/11 = 15.200 (BQ `tav2_bq.ticker`, `calc_r3/px_ddv_r3_20261106.csv`). WARNING giữ: chưa tra trực tiếp UBCKNN/HNX.

## 2. Headline và các biến thể song song (sau CK 5 tỷ; mỗi dòng đổi MỘT giả định so với headline)
| Biến thể | Tâm | P10 / P50 / P90 | % dưới giá | Nhãn | Δ tâm |
|---|---|---|---|---|---|
| **HEADLINE r3** | **15.911** | 13.315 / 15.919 / 18.573 | 37,9% | **TRONG** | 0 |
| Tiền ròng như r2 (chuẩn hoá một chân mốc 30/06, 869,1) | 14.300 | 11.704 / 14.308 / 16.962 | 67,6% | TRONG | −1.611 |
| Tiền ròng mốc 01/01 một chân (1.055,4) — bản skeptic | 15.556 | 12.960 / 15.564 / 18.219 | 43,3% | TRONG | −355 |
| Tiền ròng VLĐ đủ chân về 01/01 (1.225,9) | 16.706 | 14.110 / 16.714 / 19.368 | 23,9% | TRONG | +795 |
| Trừ lãi gửi hiện tại 70,9 (cận trên) | 14.353 | 12.257 / 14.286 / 16.306 | 69,8% | TRONG | −1.558 |
| Trừ 55,6 như r2 | 15.025 | 12.852 / 15.052 / 17.133 | 55,2% | TRONG | −886 |
| Không trừ lãi gửi (cận dưới) | 17.469 | 15.007 / 17.398 / 19.979 | 11,8% | TRONG | +1.558 |
| **DT chuẩn hoá = TB 2021–25 3.709,7** | **12.452** | 10.194 / 12.336 / 14.768 | 93,2% | **TRÊN** | −3.459 |
| DT chuẩn hoá = LTM 6.406,2 | 17.254 | 14.526 / 17.138 / 20.087 | 18,1% | TRONG | +1.343 |
| DT 5.500 như r2 | 15.640 | 13.083 / 15.618 / 18.266 | 42,6% | TRONG | −271 |
| Trọng số đường 2027 đối xứng 1/3 | 16.336 | 13.627 / 16.289 / 19.017 | 30,2% | TRONG | +425 |
| Khôi phục hệ số giữa chu kỳ Bobby 0,8/1,0/1,1 | 15.273 | 12.012 / 15.064 / 18.783 | 51,6% | TRONG | −638 |
| RONIC 20% (thưởng moat ngầm) | 16.749 | 13.948 / 16.686 / 19.607 | 25,8% | TRONG | +838 |
| Liven mất 100%, xác suất 0,10 [UL] | 15.765 | 13.163 / 15.669 / 18.487 | 40,7% | TRONG | −146 |
| **Kiểm chéo điều 10: tiền không theo mệnh giá, vốn hoá lãi gửi 70,9 tỷ/năm ở r** | **11.555** | 8.533 / 11.437 / 14.653 | 93,5% | **TRÊN** | −4.356 |
| Gộp mọi lựa chọn bi quan của r2 | 13.106 | 10.113 / 12.820 / 16.265 | 76,9% | TRONG | −2.805 |

Đọc: nhãn TRONG vững trước từng đính chính riêng lẻ; **chỉ đổi sang TRÊN ở hai trục**: (a) DT chuẩn hoá về TB 5 năm 2021–25 (năm giá DAP thấp hơn, chưa có NH3 tự doanh); (b) coi tiền ròng bị "nhốt" (cổ đông lớn Vinachem 64%, chỉ hưởng lãi gửi < r). Không bản nào cho DƯỚI vùng. Lưu ý (a) không phải ngoại lệ nhỏ: 5.652 là năm đỉnh, TB 2021–25 thấp hơn 34%, và dùng TB 2021–25 cho tâm ~12.452 / nhãn TRÊN.

## 3. Giá ngụ ý
Giá 15.200 = tâm sau CK nếu LN giữa chu kỳ trước trừ lãi = **212,8 tỷ** thay 229,0 (×0,929 ⇒ tương đương DT chuẩn hoá ~5.252 ở biên 4,05%), **hoặc r = 14,58%** (lãi huy động 12T ~8,48%). Tức thị trường đang định giá DDV gần mô hình; chênh nằm trong trục 0,8…1,2.

## 4. Giả định khoá (đủ ở `SUMMARY.json` → `assumptions`)
r 13,50% (lãi huy động 12T hiệu dụng 06/11 = 7,40% = neo) · tiền ròng 1.108 theo sổ · đường 2027 −185/+107/+373 w 0,45/0,40/0,15 (giữ: E[LN 2027] 15,5 tỷ cùng bậc LN lõi Q3 thật năm hoá −17,5; bản 1/3 ở §2) · biên chu kỳ 4,052% (BQ 2015–25) · DT 5.652 (FY2025) · trừ lãi gửi 70,9/35,4/0 · RONIC = Ke · g 3% [UL] · Q4 ±50 [UL] · trục r ±50bp [UL] · Liven theo sổ · CK căn bậc hai Y=1 [UL].

## 5. Thanh khoản (điều 6)
| | ADV 250 phiên (05/11/25–06/11/26) | ADV 60 phiên (12/08–06/11) |
|---|---|---|
| GTGD trung vị | 12,50 tỷ | 6,42 tỷ |
| CK 5 tỷ (tham chiếu nhãn) | **1,47%** — Q/ADV 40%, **NGOÀI vùng hiệu chỉnh**; 2,7 phiên @15% | 2,02% (Q/ADV 78%, ngoài vùng; 5,2 phiên) |
| CK sleeve 10 / 20 / 40 triệu | 0,07% / 0,09% / 0,13% | 0,09% / 0,13% / 0,18% |
Nhãn ở cỡ 5 tỷ và 40 triệu như nhau (TRONG). CK 5 tỷ là ước lượng thô (ngoài vùng hiệu chỉnh).

## 6. Kiểm chéo Gordon/ROE (điều 10)
LN giữa chu kỳ gồm lãi gửi lịch sử 229,0 tỷ; sau trừ trung điểm 193,6 tỷ. ROE gồm lãi trên VCSH BCTC 2.208,2 = **10,4%** (< r); ROE lõi trên VCSH trừ tiền ròng = **17,6%**. Hai cách định giá tiền: theo mệnh giá (headline, quy ước mọi mã) 15.911 vs vốn hoá lãi gửi 11.555 (§2). Khoảng cách 4,4k là giá trị "tiền có được phân phối hay không" — không có dữ liệu chính sách cổ tức/dùng tiền mới ⇒ giữ quy ước, ghi WARNING.

## 7. Độ nhạy r (sau CK)
−100bp 16.684 · −50bp 16.282 · 0 15.911 · +50bp 15.567 · +100bp 15.247.

## 8. Pháp lý / quản trị — WARNING (mang từ r2, không tra mới trong job này)
Vinachem 64% (giá chuyển giao apatit, thoái vốn chưa thực hiện) · Liven 217 tỷ một khách · phải trả Tường Nguyên 326,3 tỷ · bãi thạch cao Đình Vũ · 20/04/2026 hai lãnh đạo từ nhiệm · tồn kho NVL 617,3 tỷ chưa trích lập · UPCOM, free float 36% · **mới:** tiền ròng 1.108 tỷ có rủi ro bị giữ lại (kiểm chéo §6). Chưa tra trực tiếp UBCKNN/HNX (WebSearch 05/11 không thấy xử phạt/khởi tố).

## 9. Mốc đổi nhận định
- **Xấu đi**: BCTC Q4/26 (~20/01/2027) Liven chưa thu/trích lập (−146 kỳ vọng, −1,5k nếu mất); biên gộp Q4 âm + trích lập tồn kho; QSP Qatar ≥800 tháng 12; tiền ròng <600 tỷ; thu nhập TC kiểm toán 2015–22 cho thấy biên lịch sử đã chứa ≥ lãi hiện tại (tâm → 14.353); giá > P90 18.573 ⇒ TRÊN.
- **Tốt lên**: QSP Qatar ≤600 USD/t hai tháng liền và DAP WB ≥700; biên gộp quý ≥8%; công bố chi trả cổ tức tiền mặt lớn (đóng rủi ro tiền bị nhốt); giá < P10 13.315 ⇒ DƯỚI vùng.
- **HARD ABANDON**: Liven không thu/trích lập; tiền ròng <600 tỷ hoặc dùng tiền cho bên liên quan; Vinachem ép rút giá trị/huỷ cổ tức; đình chỉ/huỷ niêm yết; đình chỉ nhà máy do bãi thạch cao.
- **Sleeve fear-buy §2.5: KHÔNG đủ điều kiện** (DD 26/10 NON; 28/10 "NON nghiêng xấu đi").

## 10. Lưu ý skeptic chưa kiểm được
- #5: thu nhập TC kiểm toán 2015–22 — **chưa kiểm**; độ nhạy 70,9 → −1.558, 0 → +1.558 (§2).
- #8: tra trực tiếp UBCKNN/HNX — **chưa kiểm**.

## 11. LOCK + tái lập
`calc_r3/LOCK_md5.txt`: phần 1 (chốt trước khi chạy) = assumptions_r3.json, model_r3.py, calc/model.py, calc/model_r2.py, calc/bq_hist_out.csv, px_ddv_r3.sql + px_ddv_r3_20261106.csv, bq_cash_hist.sql + bq_cash_hist_out.csv, common.py, common_r2.py, bq_px_liq_20261104.csv (control), _shared/wpct.py, deposit_rate_vn.py, cctg_rate_vn.py, data/deposit_rate_vn_events.csv, data/cctg_rate_vn_events.csv, en_p1.txt, vnd.txt, DD 26/10 + 28/10 REPORT, TOP5B_CORRECTIONS, STANDARD_r2. Phần 1b: model_r3.py sửa sau lần chạy 1 CHỈ để thêm biến thể kiểm chéo "tiền vốn hoá" (assumptions không đổi ⇒ headline không đổi). Phần 2: đầu ra + SUMMARY.
`cd calc_r3 && $DNA_PYEXE -I model_r3.py && $DNA_PYEXE -I make_summary_r3.py` — chạy 2 lần **trùng byte** (`cmp`).
