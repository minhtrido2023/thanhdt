# Backtest tốt, live kém từ 07/2026: BAL/LAG — BẢN SỬA sau phản biện quant-skeptic (INCONCLUSIVE) — job `Taylor_20261110_091634`

> PAPER-ONLY. Không sửa code live, `trading_rules.json`, main; KHÔNG ghi đè `data/lagged_pos_ov.pkl`, `data/earnings_px.pkl`, `data/pt_v22_dt5g_*.csv`.
> Bản trước giữ nguyên ở `REPORT_v1_20261110_1530.md` (md5 87155a1f…). Prereg: `PREREG.md` (không đổi).
> Vintage: papertrade đến **2026-11-09** (91 phiên từ 01/07, gốc = đóng cửa 30/06); BQ đến 2026-11-09. Số "đến 11-06" (90 phiên) chỉ để so sánh cùng cửa sổ với bản cũ.
> Đóng băng trước khi làm gì (md5, `frozen/MD5.txt`): logs `edfe1853…`, transactions `10f74dc8…`, earnings_px.pkl `af4b8c1b…`, lagged_pos_ov.pkl `afb2484e…`. Cuối phiên md5 canonical vẫn trùng.

## 0. Phản biện của skeptic: ĐÚNG. Tự xác minh
| Điều skeptic nói | Tôi đo lại | Kết quả |
|---|---|---|
| 2 file pkl thiếu phiên gần-rỗng 26/06–29/07 | số mã/phiên trong cả 2 pkl (bình thường ~760–840, BQ ~900–990) | **ĐÚNG, và còn 2 phiên nữa:** 06-26 (8 mã), 06-30 (4), 07-15→07-17 (11/15/12), 07-20 (3), 07-21 (43), 07-22 (1), 07-27→07-29 (4/6/4) **+ 09-08 (7), 09-14 (11)** = **13 phiên** (skeptic nêu 11). 2014–2025: **0** phiên ngày thường như vậy (2 dòng thứ Bảy/CN 2025-05-04/11 có 1 mã, không phải phiên giao dịch). Cùng nguyên nhân: file giá sinh/append lúc BQ chưa đủ dòng. |
| `ffill(limit=5)` làm lệnh LAG khớp giá cũ | 44 lệnh cổ phiếu LAG trên 13 phiên đó, **22,77 tỷ** (cả mua+bán) | **ĐÚNG.** So giá khớp với `Open` thật BQ (thô) cùng phiên: **27/42 lệnh lệch >2%, 5 lệnh >5%** (phiên thường: 1/49 lệnh). Ví dụ PNJ 21/07 mua **43.900**, ngày đó BQ Open 40.900, High 41.500, Low 38.150 (ngoài biên). PVT 21/07 +15,3%, CSV 28/07 +12,6%. |
| Giá raw, chưa cộng cổ tức | NCT ex 27/07 (8.000đ/cp), SAB ex 28/07 (3.000đ/cp) (`corporate_action`, `event_code=DIV`) | **ĐÚNG.** pkl `Close` = giá tại lúc fetch (≈ `Price` thô); BQ hôm nay đã hồi tố `Close` (NCT 22/07: pkl 93.000 vs BQ 84.980). Cổ tức tiền mặt trong các vị thế LAG: **+0,136 tỷ = +0,53% NAV sổ**. Không có sự kiện ISS (chia tách/thưởng) nào rơi trong thời gian nắm giữ vị thế LAG. |
| BAL sạch | 7 lệnh cổ phiếu BAL (4,89 tỷ) trên các phiên gap; chạy lại engine với pkl vá | **ĐÚNG.** Giao dịch BAL **giống hệt từng dòng** giữa control/A/B (60 dòng), và giá khớp = BQ Open **0,00%** lệch ở cả 21 lệnh cổ phiếu (gap lẫn thường). BAL không đọc 2 pkl này. |

## 1. Cách sửa (mọi file ở thư mục này, tên không canonical)
- `pull_bq_prices.py` → `data/lag_px_bq_fixed_2026H2.csv` (BQ sống, `Close` hiệu chỉnh + `Price` thô + `Open` + Volume_3M_P50, 105.398 dòng, 06-01→11-09, ≥ 800 mã MỖI phiên). Tra `kb/data_registry/price-volume/` trước: `ticker_close_vs_price_dividend_adj.md` (Close hồi tố / Price thô), `ticker_price_stale_on_exdate.md` (Price kẹt CUM đúng ngày GDKHQ ⇒ 193 dòng nghi bị chuyển sang dùng Close).
- `build_fixed_pkls.py` → `engine/*_fixedA.pkl` và `*_fixedB.pkl`:
  - **A (cơ sở GIÁ THÔ, sửa tối thiểu — cùng cơ sở với pkl):** giữ nguyên mọi ô đang có, chỉ THÊM 13 phiên gap từ BQ: `Close=Price`, `Open = Open×Price/Close`. Chưa có cổ tức tiền.
  - **B (cơ sở HIỆU CHỈNH, total-return):** từ 06-25 dùng `Close/Open` BQ hiệu chỉnh nhân hệ số ghép `f = pkl_Close(06-24)/BQ_Close(06-24)` mỗi mã. ⚠️ B còn khác A ở **đường đi** (HTT được A mua/bán, B không mua) nên B−A không chỉ là cổ tức.
  - **A+cổ tức (số chính của báo cáo):** A cộng `Σ shares × value_per_share` cho vị thế nắm qua ex-date (`lag_cash_dividends.py`; 2 sự kiện NCT, SAB).
- `make_engine_copy.py` → `engine/pt_{ctrl,fixA,fixB}.py`: BẢN SAO `pt_v22_dt5g.py`, chỉ đổi đường dẫn pkl + tên file output. **Control (pkl gốc) khớp md5 từng byte với bản đóng băng** (logs `edfe1853…`, transactions `10f74dc8…`) ⇒ engine tái lập được.
- Interpreter `$DNA_PYEXE`, threads=1. Mỗi lần chạy ~96 giây.

## 2. Kết luận (SỐ CŨ → SỐ SAU SỬA)
Số "đến 11-09" nếu không ghi khác. `ctrl` = pkl gốc chạy lại (số cũ cùng cửa sổ).

| | SỐ CŨ (v1, đến 11-06) | ctrl đến 11-09 | **A (giá thô, đủ phiên)** | **A + cổ tức tiền (số chính)** | B (hiệu chỉnh) |
|---|---:|---:|---:|---:|---:|
| LAG lợi suất | −13,71% | −14,06% | −12,90% | **−12,36%** | −11,54% |
| (cùng cửa sổ 11-06) | −13,71% | −13,75% | −12,58% | −12,05% | −11,22% |
| VNINDEX | −7,24% | −7,83% | −7,83% | −7,83% | −7,83% |
| MaxDD LAG | −15,6% | −15,7% | −14,5% | −14,5% | −13,2% |
| Chọn mã vs VNI (%NAV) | **−7,24** | −7,28 | −5,95 | **−5,42** | −4,69 |
| Beta trên vốn đầu tư | −4,08 | −4,46 | −4,61 | −4,61 | −4,52 |
| Xe park vs VNI | −1,48 | −1,40 | −1,44 | −1,44 | −1,39 |
| Phí | −0,91 | −0,92 | −0,90 | −0,90 | −0,94 |
| BAL lợi suất | −5,75% | −6,23% | −6,23% | −6,23% | −6,23% |

(ctrl đến 11-06 = −13,75% vs v1 −13,71%: chênh 0,04pp do v1 chạy từ log trước khi cron 15:30 hôm nay cập nhật BQ vintage; không phải lỗi mới.)

1. **BAL: không đổi (kết luận cũ đứng).** −6,23% (đến 11-09), chọn mã +2,04pp so với VNI. Residual theo VNI ở percentile 32% (R3park0) / 29% (park70), bootstrap 6,8% / 7,7%. Bình thường theo ngưỡng prereg. *Chưa kiểm:* BAL có được ghi nhận đúng cổ tức tiền/cổ tức cổ phiếu (VPI 10% ex 07/09 nằm trong thời gian nắm giữ BAL) hay không — BAL dùng giá BQ hiệu chỉnh nên có thể đúng, tôi chưa mở nhánh code đó.
2. **LAG: lỗi gap có thật và làm số xấu đi ~1,7pp, nhưng KHÔNG xoá được độ lệch.** Sau sửa vẫn −12,4% so với VNI −7,8%. Lỗi tập trung ở tháng 7: chọn mã vs VNI **−4,98 → −2,64pp**. Tháng 9 lại **xấu hơn** (−1,57 → −2,58pp, do đường đi lệnh đổi). Cả quý: chọn mã **−7,28 → −5,42pp**. Số cũ "−7,2pp chọn mã" **đã phóng đại ~1,9pp** (gồm cả cổ tức +0,53pp).
3. **Phân bố backtest (Part B, lặp lại):** xem bảng §4. LAG vẫn nằm đuôi trái; đã giảm độ nghiêng.
4. **Chưa đủ bằng chứng để nói LAG "gãy" — kết luận cũ GIỮ NGUYÊN, nhưng chỉ còn đứng vững với 1 trong 2 ledger.** Power 1 cửa sổ 21–26%, BF "edge mất" 1,7–2,4 (yếu, cùng cỡ số cũ 1,9–2,6).
5. **Nhận diện thời điểm chạy (Part C): không đổi, 0/32.** Part C chạy trên ledger pin PIT 2014→2026-05, không đọc 2 pkl lỗi. Xem §5.
6. **DT5G: không đổi.** Sửa câu Part D ở §6.

### "LAG lệch đuôi trái" — còn hay không?
- **Ledger R3park0 (theo yêu cầu dispatch): CÒN.** Percentile residual 2,9% (= 1/34, mức nhỏ nhất đo được), bootstrap 0,4–0,5%, có điều kiện VNI −3…−12%: 0,0%. Theo prereg (<5% cả cửa sổ không chồng lấn VÀ residual) ⇒ "lệch có ý nghĩa".
- **Ledger park70 (cấu hình sát papertrade hơn): YẾU XUỐNG "đuôi, chưa kết luận".** Residual 8,8% (đến 11-09) hoặc 5,9% (cùng cửa sổ 11-06, cũ 2,9%); bootstrap 1,2%; có điều kiện 0,4%. Cảnh báo: đoạn 2,9→8,8 một phần do độ dài cửa sổ 90→91 phiên (ctrl cũng 8,8% ở 91 phiên), một phần do sửa lỗi — xem cột ctrl vs fixA+cashdiv ở §4.
- Hai ledger không đồng nhất ⇒ nên nói **"LAG kém nhiều so với kỳ vọng, đuôi trái, nhưng độ sâu phụ thuộc cấu hình park"**, không nói "lệch có ý nghĩa" không điều kiện như v1.

## 3. A. Từng sổ (papertrade `pt_v22_dt5g`, V2.3: 50/50 + park 70%; KHÔNG phải NAV tài khoản V2.4 live)
Self-check đồng nhất thức dNAV = PnL cổ phiếu + PnL ETF − phí: dư **cộng dồn −0,004% NAV** (LAG), −0,001% (BAL); lệch theo ngày tối đa **5,2 triệu VND**, KHÔNG phải 0 VND/ngày (lệch thời điểm ghi phí ETF — như v1). Lỗi gap không đổi mức dư này (5,209M → 5,208M).
Phân rã và vol năm: vol LAG tăng từ 14,5% → 16,8% sau sửa (đường giá thật có biến động mà ffill làm phẳng) — bản cũ đánh giá thấp vol.

**Theo tháng LAG (%NAV; `engine/monthly_attr_{ctrl,fixA}_to1109.txt`)**

| Tháng | ret ctrl → fixA | VNI | beta (fixA) | chọn mã vs VNI ctrl → fixA | park vs VNI | expo CP |
|---|---|---:|---:|---|---:|---:|
| 07 | −11,57 → **−9,46** | −6,68 | −5,31 | −4,98 → **−2,64** | −1,10 | 26% |
| 08 | +4,43 → +4,47 | +5,55 | +5,58 | −1,15 → −1,11 | 0,00 | 100% |
| 09 | −3,70 → **−4,68** | −3,47 | −1,83 | −1,57 → **−2,58** | +0,11 | 29% |
| 10 | −2,41 → −2,44 | −1,53 | −1,53 | +0,17 → +0,16 | −0,92 | 14% |
| 11 (đến 09) | −0,98 → −0,98 | −1,57 | −1,10 | 0,00 | +0,12 | 0% |

BAL theo tháng: không đổi (xem `engine/monthly_attr_fixA_to1109.txt`).

**Theo loại lệnh LAG (realized+MTM, vị thế còn sống sau 01/07; `engine/by_playtype_*_to1109.txt`)**

| | ctrl | fixA | fixB |
|---|---|---|---|
| CAPIT (6 mã) | −0,44 tỷ, thắng 2/6 | −0,26 tỷ, thắng 2/6 | −0,14 tỷ |
| LAG_HI | −0,11 tỷ, thắng **27%** (n=15) | −0,01 tỷ, thắng **58%** (n=12) | +0,06 tỷ, 47% (n=15) |
| LAG_LO | +0,02 tỷ, thắng 42% (n=12) | +0,05 tỷ, thắng **71%** (n=14) | +0,19 tỷ, 75% |

Số mã trong từng nhóm đổi vì đường đi lệnh đổi (số lệnh mua LAG 01/07→09/11: **63 → 58**; riêng 21→28/07: **49 → 42**). Cú giảm sàn PNJ **vẫn còn** (−0,51 tỷ, −54%): đây là sụt giá thật (BQ `Close = Price` đã đối chiếu ở v1), không phải lỗi dữ liệu. Tuyên bố "tỉ lệ thắng LAG_HI 4/13" của v1 là **sản phẩm của lỗi giá**: sau sửa không còn nhóm nào thắng dưới 47%.

## 4. B. Live có thật sự kém hơn backtest? (`part_b_v2.py`, `part_b_v2.json`, `part_b_v2_bayes.txt`)
Ledger: R3park0 `537e349b`, park70 `65e7bb04`. Control: CAGR tính lại = METRIC, chênh **0,0** cả hai; md5 khớp. Control LẶP LẠI số cũ: ctrl đến 11-06 cho z_intact −1,68 / BF 2,57 (v1: −1,68 / 2,56).

| LAG, N=34 cửa sổ không chồng lấn | R3park0 ctrl | R3park0 **A+cổ tức** | R3park0 B | park70 ctrl | park70 **A+cổ tức** | park70 B |
|---|---:|---:|---:|---:|---:|---:|
| Live (91 phiên) | −14,06% | **−12,36%** | −11,54% | −14,06% | **−12,36%** | −11,54% |
| Dự báo theo VNI −7,83% | +5,47% | +5,47% | +5,47% | +2,05% | +2,05% | +2,05% |
| Percentile phần dư | 0,0% | **2,9%** | 2,9% | 8,8% | **8,8%** | 8,8% |
| Percentile block bootstrap | 0,2% | **0,5%** | 0,7% | 0,7% | **1,2%** | 1,6% |
| Có điều kiện VNI∈[−12%,−3%] | 0,0% | 0,0% | 0,0% | 0,0% | 0,4% | 1,5% |
| z (edge còn) / z (alpha=0) | −1,74 / −1,04 | −1,59 / −0,89 | −1,52 / −0,82 | −1,43 / −0,89 | −1,28 / −0,74 | −1,21 / −0,66 |
| Bayes factor "edge mất" vs "còn" | 2,64 | **2,37** | 2,26 | 1,89 | **1,74** | 1,67 |
| Power (1 cửa sổ bắt "edge=0") | 26% | 26% | 26% | 21% | 21% | 21% |

Cùng cửa sổ 90 phiên với v1 (đến 11-06): R3park0 percentile phần dư 2,9% → 2,9%, bootstrap 0,3% → 0,6%; park70 phần dư 2,9% → **5,9%**, bootstrap 0,8% → 1,4%, BF 1,86 → 1,69.
BAL (cả hai ledger, đến 11-09): percentile phần dư 32%/29%, bootstrap 6,8%/7,7%, BF 1,12/1,15, power 24%/19%.

**Trả lời thẳng (đã sửa):** BAL = bình thường. LAG = **kém hơn kỳ vọng, nằm đuôi trái, nhưng nhẹ hơn v1 và phụ thuộc ledger**; N live vẫn = 1 cửa sổ, power ≤26%, BF <3 ⇒ chưa kết luận gãy. Phần "cần thêm ~2–3 cửa sổ 90 phiên" vẫn là *ước lượng chưa đo*. Thước nhanh hơn (excess per-event của LAG) vẫn là bước tiếp đề xuất, chưa làm.

## 5. C. Nhận diện thời điểm chạy từng sổ — không đổi (nhưng ứng viên V8 yếu đi)
- Part C dùng ledger pin PIT (2014→2026-05, N=148 tháng) + BQ; **không đọc 2 pkl lỗi** ⇒ số `part_c_results.json` không bị ảnh hưởng. PASS **0/32**, q_BH nhỏ nhất **0,64**.
- Câu hỏi "data/xsec.csv tái lập được không": `pull_bq_data.py` + `regen_check.txt`. `dt5g.csv`, `vnindex.csv` và cột `n_ma`/`breadth` của xsec **tái lập chính xác (max|diff| = 0)**. Các cột `n_r21`, `disp21`, `iqr21`, `disp1`, `ew_r1` **KHÔNG tái lập chính xác** (truy vấn gốc không được lưu; median |diff| disp21 = 0,015, p95 = 0,24, ew_r1 lệch trên 31% số ngày). Độ nhạy: chạy lại Part C với xsec tái sinh (`part_c_regenxsec.py`) cho **PASS 0, q_BH nhỏ nhất vẫn 0,64**; |IC| V7 đổi tối đa ~0,1 (V7 vẫn q≥0,96). Kết luận Part C không phụ thuộc phần không tái lập.
- **Ứng viên V8 ("LAG sau đợt dồn nhiều lệnh thì tháng sau kém VNI"): không còn đứng như một bằng chứng.** (a) Phần backtest: IC −0,20, p 0,025, **q_BH 0,64** — vẫn là nhiễu có thể, chưa bao giờ qua chuẩn. (b) Phần "khớp live tháng 7–8/2026" của v1 **yếu đi**: đợt dồn 21–28/07 là 42 lệnh mua (v1 cũ nói "31 lệnh", tôi không tái hiện được định nghĩa đó; số đo hiện tại là 49 → 42 sau sửa). Tháng 8 kém VNI −1,1pp vẫn còn, nhưng tháng 7 (nơi v1 gán −4,9pp) chỉ còn −2,6pp và tháng 9 lại xấu hơn (−2,6pp) — hình mẫu live không còn một chiều rõ. **V8 hạ xuống "ghi chú, không theo dõi chủ động" cho đến khi có kiểm per-event.**
- Power vẫn giới hạn: |IC| ≲ 0,25 không thấy được.

## 6. D. Tín hiệu thị trường 07→11/2026 — sửa 1 câu
Câu cũ: *"Chỉ có 2024-08 (−8,7%) là DT5G về CRISIS ở mức giảm nông…"* **SAI.** Theo `part_d_episodes.csv`, **cả 2023-10 (−17,4%, state tại trigger = 1 = CRISIS) lẫn 2024-08 (−8,7%, state = 1)** là đợt nông mà DT5G về CRISIS (cùng 2018-05 −27,1%, 2022-04 −40,3%). Hai đợt nông 2014-12 (−19,1%) và 2015-11 (−17,9%) DT5G giữ NEUTRAL. Giả thuyết "do trụ Mỹ (VIX)" cho 2024-08 vẫn **chưa kiểm**. Bảng so 12 đợt giảm và kết luận "HẸP chứ không SÂU" giữ nguyên (không đọc pkl lỗi).

## 7. N độc lập từng phép thử
A: 1 cửa sổ (mô tả); sau sửa số lệnh LAG bị ảnh hưởng 44 (trên 13 phiên) · B: 34 cửa sổ không chồng lấn / sổ; có điều kiện ≈5; hai ledger không độc lập nhau · C: 148 tháng, số đợt chế độ 12–71, 32 phép thử · D: 12 đợt (8 có DT5G), mô tả.

## 8. Còn chưa chắc / chưa làm
- LAG "gãy" hay "xui": vẫn cần thêm cửa sổ hoặc kiểm per-event (N = lệnh LAG).
- A vs B: số chính chọn **A+cổ tức** vì sạch (không dính path divergence) và chỉ dùng dữ liệu đã đối chiếu `corporate_action`. B là cận lạc quan; chênh A+D→B (+0,8pp) là đường đi lệnh + điều chỉnh khác, chưa tách.
- Cổ tức BAL chưa kiểm (§2 mục 1). Cổ tức tiền chỉ lấy `corporate_action.DIV` (bảng ghi 1 lần nạp, status TRAP trong registry — đã lọc `not_executed`); ISS không rơi vào vị thế LAG.
- `ffill(limit=5)` còn tồn tại ở cấp từng mã (mã không có dòng 1–5 phiên). Tôi chỉ vá cấp phiên; không đo mức ảnh hưởng cấp mã.
- Papertrade vẫn là V2.3 park70; phân rã trên NAV tài khoản V2.4 cần ledger per-book của bot (chưa có).
- **Gốc rễ lỗi pkl là việc ngoài phạm vi (không sửa code live).** Khuyến nghị cho owner pipeline `refresh_lagged_caches.py`/`papertrade_daily.sh`: thêm kiểm "số mã/phiên < 50% trung vị ⇒ fail" trước khi ghi pkl. Đã `append_event` để Mike chuyển.

## Artifacts
`frozen/` (+`MD5.txt`) · `pull_bq_prices.py` (+`data/lag_px_bq_fixed_2026H2.csv`) · `build_fixed_pkls.py` · `make_engine_copy.py` · `engine/` (`pt_{ctrl,fixA,fixB}.py`, `*_logs/transactions/open_positions.csv`, `*_fixed{A,B}.pkl`, `partA_*`, `monthly_attr_*`, `by_playtype_*`, `lag_holdings_*`, `lag_div_*`) · `part_a_v2.py` · `part_a_extras.py` (sinh by_playtype / lag_holdings) · `part_a_monthly_attr.py` · `lag_cash_dividends.py` · `check_gap_fills.py` (+`gap_fill_check.txt`) · `part_b_v2.py` (+`part_b_v2.json`, `part_b_v2_bayes.txt` — sinh luôn dòng Bayes) · `pull_bq_data.py` (+`data/regen_*.csv`, `regen_check.txt`) · `part_c_regenxsec.py` (+`engine/part_c_regenxsec_*`) · các file v1 (`part_a.py`, `part_b.py`, `part_c.py`, `part_d.py`) giữ nguyên. Interpreter `$DNA_PYEXE`, threads=1.
