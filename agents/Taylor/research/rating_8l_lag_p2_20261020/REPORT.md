# Độ trễ rating 8L — Phần 2: TRỄ TÍN HIỆU (event-study giá quanh eff_date)

Job `Taylor_20261020_034545` · 2026-10-20 · read-only. Không đổi luật/gate production, không chạy lại R3/V2.4.

## 0. PREREG (viết 2026-10-20 ~10:55 ICT, TRƯỚC khi tính bất kỳ CAR nào)

**Câu hỏi.** Khi rating 8L đổi hạng, giá (vượt benchmark) đã đi bao nhiêu trước eff_date và còn bao nhiêu sau eff_date (thực thi T+1)?

**Nguồn** (đã tra `kb/data_registry/`):
- Rating: `tav2_bq.fa_ratings_8l` (CANONICAL, `time` = eff_date = Release_Date, NULL→`time`). Rating 8L tính từ BCTC (không dùng giá) ⇒ không có liên kết cơ học giá→rating.
- Giá: `tav2_bq.ticker.Close` (đã điều chỉnh cổ tức + chia tách, hồi tố theo vintage hôm nay; registry `ticker_close_vs_price_dividend_adj.md`). Chỉ dùng tỉ số `Close_t/Close_{t-1}` giữa hai NGÀY ⇒ đúng ngữ cảnh "Close/Close" của registry; KHÔNG cộng thêm cổ tức (tránh double-count). Kiểm tra bằng 1 mã có chia tách/cổ tức CP lớn trước khi dùng.
- Benchmark B1: VN-Index có cổ tức `data/benchmark/vnindex_tr_daily.csv` cột `tr_gross` (CANONICAL; vì `Close` là total-return, so với chỉ số giá sẽ lệch ~1,6-1,9 điểm %/năm). B2: trung vị lợi suất ngày (`Close`) của các mã `in_universe` trong `tav2_mike.universe_pit` cùng phiên.
- Universe: `universe_pit.in_universe` tại phiên 0 (KHÔNG `ticker_prune`).
- Lịch phiên: các ngày có dòng trong `vnindex_tr_daily.csv`.

**Sự kiện.** Dòng rating (ticker, eff_date) có rating ≠ dòng liền trước của cùng ticker. Chỉ giữ dòng khớp một (ticker, quý) trong `ticker_financial` theo eff_date = RD (NULL→`time`); dòng không khớp (vd override forensic) bị loại và đếm. eff_date ∈ [2014-07-01, 2026-07-31] (cần đủ +60 phiên; sự kiện thiếu cửa sổ bị loại và đếm).
- G1: trước ≥4 → sau ≤3 (vào vùng mua). G2: trước ≤3 → sau ≥4 (rớt khỏi vùng). G3: đổi cùng phía cổng (mô tả, tách G3-lên/G3-xuống).
- Phân đoạn: ngân hàng (route BANK ở dòng sự kiện) / phi ngân hàng; IS = eff 2014-2019, OOS = 2020+.

**Loại khỏi mẫu chính** (bản "không loại" chạy song song để đo độ nhạy):
(a) 7 ca nhìn trộm chắc chắn (`out_phase3_definite_peek_cases.csv` của P1; luật: RD < cuối quý HOẶC RD ≤ RD quý trước) — áp luật này cho MỌI mã, không chỉ universe;
(b) RD trong 0-7 ngày sau cuối quý (gồm 125 ca Q1 2025/2026 đầu tháng 4);
(c) RD NULL.

**Phiên 0** = phiên đầu tiên có ngày ≥ eff_date. Lợi suất bất thường ngày AR_t = r_stock − r_bench. Mã không giao dịch trong phiên ⇒ Close ffill (lợi suất 0). Loại sự kiện có <80% phiên có giao dịch thật trong cửa sổ [−60,+60] hoặc có |r_stock| > 40%/phiên (lỗi dữ liệu) — đếm số bị loại.

**Đo** (CAR = tổng AR, phiên giao dịch):
- PRE = CAR[−60,−1]; DAY0 = AR_0; TOTAL = CAR[−60,+60].
- (i) tỉ lệ trước phiên 0 = PRE / TOTAL (tính trên CAR trung bình nhóm; chỉ diễn giải khi CI của TOTAL không chứa 0).
- (ii) POST T+1: vào lệnh tại close phiên +1 ⇒ CAR[+2,+20], CAR[+2,+40], CAR[+2,+60].
- (iii) nửa-đời drift: phiên k nhỏ nhất mà CAR[+2,k] trung bình ≥ 50% CAR[+2,+60] (chỉ khi CI của CAR[+2,+60] không chứa 0).
- Đối chiếu trễ vận hành P1 (median 3,4 ngày lịch, p90 9,4): CAR[+4,+60] (vào close +3) và CAR[+9,+60] (vào close +8).

**Không phải look-ahead**: eff_date là ngày thông tin BCTC (và rating) có hiệu lực; mọi lợi suất "sau" chỉ là KẾT QUẢ được đo, không được dùng để chọn sự kiện hay làm filter. Không dùng cột `profit_*`/`PC*`/`O*`. Loại (a)-(c) chính là để eff_date không sớm hơn ngày thông tin thật.

**Thống kê.** N = số sự kiện (ticker, quý). Tương quan chéo cùng quý ⇒ CI 95% bằng block bootstrap theo QUÝ LỊCH của eff_date (2.000 lần, seed 20261020) và p-value từ t cluster-robust theo quý (df = số quý − 1). N hiệu dụng = N × SE²_iid / SE²_cluster. Nhóm có N hiệu dụng < 30 ⇒ "không đủ để kết luận".
**Số phép thử**: họ CHÍNH F1 = {G1, G2} × {PRE, POST+20, POST+40, POST+60} × {B1, B2} = **16 phép**, BH-FDR q=0,05. Mọi thứ khác (G3, ngân hàng/phi NH, IS/OOS, độ trễ vận hành, bản không loại) = họ THĂM DÒ F2, BH-FDR riêng, chỉ mô tả.

**Giả thuyết** (không định hướng dấu trước): H0 mỗi phép = CAR trung bình bằng 0. Verdict theo nhóm:
"giá đã đi trước" nếu PRE có ý nghĩa (F1, BH) và POST+60 không; "còn drift" nếu POST+60 có ý nghĩa cùng dấu với kỳ vọng của hạng (G1 dương / G2 âm) ở cả B1 và B2; "không đủ N" nếu N hiệu dụng < 30; ngoài ra "không có tín hiệu rõ".

## 1. Lệch khỏi PREREG (khai báo trung thực — đều thêm SAU khi thấy số)

1. **B2 (trung vị universe) hỏng**: cho CAR +9…+13% ở MỌI nhóm, kể cả G2 (rớt hạng) và placebo G0 (G0 B2 PRE+POST ≈ +0,1%/phiên). Nguyên nhân: tổng các TRUNG VỊ lợi suất ngày thấp hơn hệ thống so với trung bình lợi suất từng mã (phân phối lệch phải) ⇒ drift giả. Kết quả F1 trên B2 vẫn in đúng như PREREG nhưng **KHÔNG được diễn giải**.
2. **Thêm B3** = trung bình EW lợi suất các mã `in_universe` cùng phiên (thay B2 làm benchmark universe).
3. **Thêm placebo G0** = dòng rating quý KHÔNG đổi hạng (N=11.175) và chênh lệch "nhóm − G0" (bootstrap theo quý chung). Lý do: phần drift chung của mọi mã vừa công bố BCTC phải bị trừ ra.
4. **Thêm cửa sổ trễ vận hành chân trời ngắn** `[4,20]`, `[9,20]`, `[4,40]`, `[9,40]` vì drift đạt đỉnh ở +20…+40 rồi phai.
5. Bug tự bắt khi soát: lần chạy 2 hàm chênh lệch lấy nhầm cột cuối cho cửa sổ bắt đầu ở −60 (PRE/TOTAL) — đã sửa trước khi đọc kết luận; số dưới đây là bản sửa.
Mọi mục 2-4 thuộc họ THĂM DÒ F2 (BH-FDR trên 1.784 phép ở bảng chính, 384 phép ở bảng chênh lệch).

## 2. Mẫu

`out_event_study_stdout.txt`: 52.414 dòng rating có dòng trước; 8 dòng không khớp (ticker, quý) bị loại (override forensic…);
eff 2014-07-01→2026-07-31: 52.111. Loại cửa sổ: không có giá (mã chưa từng trong universe) 25.075 · thiếu ±60 phiên 364 ·
không `in_universe` tại phiên 0: 11.568 · <80% phiên có giao dịch 5 · |r|>40% 18 ⇒ còn 15.081 sự kiện.
Mẫu CHÍNH (sau loại a-c) — sự kiện đổi hạng: **G1 = 1.012, G2 = 1.019, G3-lên 839, G3-xuống 838**; G0 = 11.175.
Bản không loại: G1 1.022, G2 1.032 (loại a-c chỉ bỏ 10/13 sự kiện qua cổng ⇒ kết quả gần như y hệt, §3.4).
48 cụm quý. Ngân hàng: **G1 = 19, G2 = 15** sự kiện ⇒ **không đủ để kết luận**.

Kiểm giá điều chỉnh (`check_adj.py`, `out_check_adj.txt`): VHM 2026-08-07 r(Price) −52,3% vs r(Close) −5,3%; MWG 4 lần chia/thưởng; TCB 2018; F88 2026 — đều được điều chỉnh trong `Close`.

## 3. Kết quả (CAR %, CI 95% bootstrap theo quý; q = BH)

### 3.1 Họ F1 (PREREG, 16 phép) — `out_p2_car_tests.csv` (family=F1)

| Nhóm | Bench | PRE[−60,−1] | POST T+1 [2,20] | [2,40] | [2,60] |
|---|---|---|---|---|---|
| G1 ≥4→≤3 | B1 VNI-TR | +1,72 [−1,19; +5,07] q=0,39 | **+1,97 [+0,34; +3,61] q=0,037** | **+2,83 [+0,69; +5,16] q=0,029** | +0,40 [−2,17; +3,14] q=0,77 |
| G2 ≤3→≥4 | B1 VNI-TR | −1,86 [−4,51; +1,20] q=0,32 | +0,44 [−1,16; +2,19] q=0,68 | +0,84 [−1,70; +3,48] q=0,63 | −0,80 [−3,94; +2,78] q=0,68 |
| G1/G2 | B2 | (q<0,001 toàn bộ — vô hiệu, §1.1) | | | |

N hiệu dụng (POST60, B1): G1 308, G2 157.

### 3.2 Thăm dò: benchmark B3 (EW universe) và chênh lệch so với placebo G0 — `out_p2_car_tests.csv`, `out_p2_diff_vs_g0.csv`

| | PRE[−60,−1] | DAY0 | [2,20] | [2,40] | [2,60] | trễ 3: [4,20] | trễ 8: [9,20] | trễ 8: [9,40] |
|---|---|---|---|---|---|---|---|---|
| G1 vs B3 | +2,31 [+0,57; +3,98] | +0,15 | **+1,11 [+0,51; +1,73] q=0,004** | +1,36 [+0,44; +2,29] q=0,023 | +1,15 [−0,48; +2,61] | +1,01 [+0,45; +1,63] q=0,008 | +0,81 [+0,29; +1,37] q=0,016 | +1,07 [+0,15; +1,94] q=0,082 |
| G1 − G0 | +1,66 [−0,14; +3,35] | +0,10 | **+1,34 [+0,71; +2,03] q=0,022** | +1,64 [+0,64; +2,69] q=0,033 | +1,42 [−0,21; +3,07] | +1,17 [+0,56; +1,84] q=0,022 | +0,92 [+0,38; +1,51] q=0,022 | +1,22 [+0,21; +2,22] q=0,12 |
| G2 vs B3 | −1,01 [−2,80; +0,88] | −0,07 | −0,74 [−1,32; −0,17] q=0,043 | −0,69 [−1,54; +0,22] | −0,59 [−1,86; +0,73] | −0,58 q=0,096 | −0,39 q=0,24 | −0,34 |
| G2 − G0 | −1,65 [−3,48; +0,16] | −0,13 | −0,51 [−1,10; +0,13] q=0,35 | −0,41 | −0,32 | −0,43 q=0,39 | −0,29 | −0,19 |
| G0 vs B3 | +0,64 [+0,39; +0,92] | +0,06 | −0,23 [−0,36; −0,11] | −0,28 | −0,28 | | | |

Ổn định IS/OOS (G1 vs B3, [2,20]): IS +1,11 [+0,27; +2,01] (N=383) · OOS +1,10 [+0,34; +1,95] (N=629). G1 − G0 [2,20]: IS +1,17, OOS +1,43.
G2 − G0 [2,20]: IS −0,89 [−1,62; −0,22], OOS −0,30 [−1,16; +0,60] ⇒ không ổn định.

### 3.3 Đường CAR, tỉ lệ trước phiên 0, nửa-đời — `out_car_path_summary.txt`, `out_p2_frac_halflife.csv`

CAR cộng dồn vs B3 (%), mẫu chính:

| offset | −40 | −20 | −10 | −1 | 0 | +1 | +5 | +10 | +20 | +30 | +40 | +60 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 | 0,84 | 1,74 | 1,84 | 2,31 | 2,46 | 2,76 | 2,83 | 3,32 | 3,86 | 4,00 | 4,12 | 3,90 |
| G2 | 0,04 | 0,32 | −0,17 | −1,01 | −1,08 | −1,20 | −1,52 | −1,77 | −1,95 | −1,71 | −1,90 | −1,80 |
| G0 | 0,26 | 0,58 | 0,72 | 0,64 | 0,70 | 0,69 | 0,53 | 0,58 | 0,46 | 0,45 | 0,41 | 0,41 |

- **(i) Tỉ lệ trước phiên 0** (B3): G1 **59%** [20%; 102%] (TOTAL CI không chứa 0). G2: TOTAL CI chứa 0 ⇒ không diễn giải theo PREREG (điểm ước lượng 56%). B1: TOTAL CI chứa 0 cho cả G1, G2.
- **(ii) POST T+1**: G1 còn ≈ +1,1…+1,4% vượt B3 tới +20…+40 phiên; tới +60 không còn có ý nghĩa (CI chứa 0, B1 tụt về +0,4%).
- **(iii) Nửa-đời**: theo PREREG chỉ tính khi CI của CAR[2,60] không chứa 0 ⇒ **không xác định** cho G1/G2 (B1 và B3). Mô tả: phần tăng sau eff_date của G1 dồn ở +2…+30 (đỉnh +30…+40).
- **"Rating chậm hơn giá bao nhiêu phiên"**: G1 tích luỹ phần lớn PRE trong −60…−20 (+1,7 điểm) rồi thêm +0,6 tới −1; G2 rơi tập trung −20…−1 (−1,3 điểm). Tức giá đi trước eff_date khoảng 1-3 tháng giao dịch — đúng bản chất: rating dùng BCTC quý đã kết thúc, giá phản ánh kinh doanh trong quý trước khi BCTC ra.

### 3.4 Độ nhạy loại ca (a)-(c)
Bản không loại (G1 N=1.022, G2 N=1.032) khác bản chính ≤0,1 điểm % ở mọi cửa sổ (vd G1 vs B3 [2,20] +1,08 vs +1,11; G1−G0 [2,20] +1,32 vs +1,34). Lý do: trong mẫu đủ cửa sổ + in_universe chỉ có 10 G1 (8 RD≤quý+7, 2 nhìn trộm chắc chắn) + 13 G2 (12 RD≤quý+7, 1 RD NULL) thuộc nhóm loại, eff 2022-10→2026-05 (`out_p2_events.csv`, cột x_*). ⇒ Kết luận Phần 2 KHÔNG phụ thuộc vào lỗi RD của Phần 3.

## 4. Đối chiếu Phần 1 (trễ vận hành median 3,4 ngày lịch, p90 9,4 ≈ 3 và ~7-8 phiên)

Với G1: vào lệnh close +3 vẫn còn +1,01% (vs B3, [4,20]) / +1,17% (vs G0); vào close +8 còn +0,81% / +0,92% (q≤0,022). So với vào close +1 (+1,11% / +1,34%) ⇒ trễ vận hành median "ăn" ≈ 0,1-0,2 điểm, p90 ≈ 0,3-0,4 điểm trên tổng ~1,1-1,3. **Drift sau +3…+8 phiên còn (ngắn hạn tới +20…+40), chưa hết.** Với G2: không có drift đáng tin để mất.

## 5. Verdict theo nhóm

| Nhóm | N (độc lập ~ sự kiện; 48 cụm quý) | Verdict PREREG (F1, B1) | Đọc thăm dò (B3, G0) |
|---|---|---|---|
| **G1** ≥4→≤3 | 1.012 (N_eff B1 ~220-310) | **"còn drift" ngắn hạn**: POST+20/+40 có ý nghĩa (q 0,037/0,029) nhưng POST+60 KHÔNG ⇒ theo đúng luật PREREG (cần POST+60) là **"không có tín hiệu rõ" ở +60**; PRE không có ý nghĩa ở B1 | Giá đi trước ~59% tổng dịch chuyển; còn ≈ +1,1…+1,6% drift tới +20…+40 phiên (vs B3 và vs G0, IS≈OOS), phai về không có ý nghĩa ở +60 |
| **G2** ≤3→≥4 | 1.019 (N_eff B1 ~160-250) | **"không có tín hiệu rõ"** (không phép nào có ý nghĩa) | Giảm chủ yếu TRƯỚC eff (−20…−1); sau eff −0,5…−0,7 (vs B3 q=0,043 ở [2,20]; vs G0 không ý nghĩa; OOS không ý nghĩa) ⇒ **"giá đã đi trước" (mô tả, yếu)** |
| G3 (cùng phía) | 839 / 838 | (mô tả) | G3-lên: PRE +2,0 vs G0, sau eff không ổn định; G3-xuống: không có gì |
| Ngân hàng | G1 19, G2 15 | **không đủ N** | – |

**Lưu ý diễn giải** (quan trọng): sự kiện đổi hạng trùng với ngày công bố BCTC ⇒ drift của G1 rất có thể là **PEAD/earnings drift** (thứ book LAG đã khai thác), không phải giá trị riêng của rating. Placebo G0 trừ được drift chung của "mọi mã vừa công bố", nhưng không trừ được việc G1 có bất ngờ lợi nhuận dương nhiều hơn. Đây là ước lượng mô tả, CHƯA phải edge.

**Điều kiện cần để kiểm chứng tiếp (nếu muốn)**: (1) kiểm soát SUE/bất ngờ lợi nhuận (G1 − G0 trong cùng nhóm SUE) để tách rating khỏi PEAD; (2) backtest có chi phí (TC 0,1%/chiều, ~1,1% gộp trên 20-40 phiên còn mỏng sau phí + slippage), walk-forward IS/OOS, DSR/PBO; (3) quant-skeptic CONFIRMED trước bất kỳ đề xuất nào. **KHÔNG đề xuất đổi luật/gate production.**

## Tái lập

```bash
cd mike/agents/Taylor/research/rating_8l_lag_p2_20261020
$DNA_PYEXE pull_data.py           # BQ -> raw/*.parquet (fa_ratings_8l, ticker_financial, universe_pit, ticker Close/Price); --force để kéo lại
$DNA_PYEXE check_adj.py           # kiểm Close đã điều chỉnh corp-action -> out_check_adj.txt
OMP_NUM_THREADS=1 $DNA_PYEXE event_study.py > out_event_study_stdout.txt   # mọi bảng §2-§5
```
Đầu ra: `out_p2_events.csv` (sự kiện + cờ loại), `out_p2_car_tests.csv` (mọi phép, family F1/F2, q_bh),
`out_p2_diff_vs_g0.csv`, `out_p2_frac_halflife.csv`, `out_p2_car_paths.csv`, `out_car_path_summary.txt`.
Dữ liệu kéo 2026-10-20 ~11:00 ICT; `vnindex_tr_daily.csv` vintage tới 2026-10-19. Republish `fa_ratings_8l` ⇒ số có thể lệch nhẹ.
