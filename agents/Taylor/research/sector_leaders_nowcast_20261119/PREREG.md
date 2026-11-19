# PREREG — Mã đầu ngành × nowcast ngành (job Taylor_20261119_090450, 2026-11-19, "việc 5")

Viết và commit TRƯỚC khi chạy bất kỳ phép tính kết quả nào. Sửa sau commit = vô hiệu; mọi lệch khỏi file này phải
ghi trong REPORT dưới mục "Lệch PREREG".

## 0. Giả thuyết nhân quả (và nói thẳng phần nào là lặp lại)
- **H-fund (KQKD):** đầu ngành có quy mô/hợp đồng dài hạn/hedging tốt hơn ⇒ (a) KQKD bám giá hàng hoá **sạch hơn**
  (IC cao hơn) HOẶC (b) **giữ biên khi pha xuống** (np_d đầu ngành − mã còn lại > 0 khi c_yoy < 0), (c) khi pha lên
  có thể ăn theo quy mô (hai phía).
- **H-px (giá):** đầu ngành thanh khoản cao ⇒ thị trường định giá tin ngành vào đầu ngành **trước** (trong quý), mã
  đi sau bắt kịp sau đó (spread đổi dấu ở +1M/+3M).
- **Phần LẶP LẠI phép thử đã NO-GO:** chân (ii) "đầu ngành vs universe_pit" có điều kiện theo dấu nowcast thực chất là
  momentum hàng hoá → giá cổ phiếu (H-a/H-b 26/10, 17 trial 0 qua cổng; cổ phiếu chạy cùng tháng IC 0,23, không có
  trễ khai thác). Kỳ vọng tiên nghiệm: ô "hiện tại" vs universe dương (đã biết, không giao dịch được), ô +1M/+3M ≈ 0.
  Vẫn đo vì dispatch yêu cầu, nhưng được gắn nhãn LẶP. Phần MỚI thật sự chỉ là **tương phản đầu ngành − mã còn lại
  cùng họ** (chân i) và H-fund.

## 1. Dữ liệu (đều đã tra `kb/data_registry/`)
- Hàng hoá: `commodity_cycle_te_20261026/te_daily.parquet` (TE daily, source tường minh); giá TB quý cần ≥40 phiên;
  `c_yoy` = log(TB quý Q / TB quý Q−4) × dấu họ — y hệt `b2_nowcast.py`. Tín hiệu biết tại `sig` = phiên đầu ≥ qend+2 ngày.
- Bản đồ: `commodity_cycle_te_20261026/commodity_map_te.csv` (đóng băng 26/10), **chỉ tier A**.
- Giá: `data/bq_cache/ticker` (vintage cache 2026-11-18): `Close` (điều chỉnh) cho lợi suất; `Trading_Value`
  (= Price thô × Volume thô; kiểm HPG 17/06/2022: Price×Volume/Trading_Value = 1,0 qua ngày chia cổ tức CP, Volume
  không nhảy) cho GTGD ⇒ **không có hệ số corp-action nào** trong định nghĩa đầu ngành; lợi suất chỉ dùng `Close`, không
  nhân thêm hệ số nào.
- Universe: `data/bq_cache/universe_pit` (`in_universe`), CANONICAL. Không `ticker_prune`, không `profit_*`.
- KQKD: `data/bq_cache/ticker_financial.parquet`, bản công bố ĐẦU TIÊN theo `Release_Date` (như `common.fin()`).

## 2. Định nghĩa đầu ngành (khai một giá trị duy nhất)
- **K = 2.** Tiêu chí: **trung vị `Trading_Value` 60 phiên** kết thúc ở phiên liền trước `d0(Q)` = phiên đầu tiên của
  quý Q. Chỉ xếp hạng các mã của họ có `in_universe` tại `d0(Q)` và có ≥40/60 phiên dữ liệu.
- Danh sách đổi theo quý; không dùng danh sách hôm nay áp ngược. Không dùng nhãn ngành ICB hôm nay — họ lấy từ bản đồ
  đóng băng.
- **Họ đủ điều kiện ở quý Q:** ≥ 3 mã hợp lệ tại `d0(Q)` (2 đầu ngành + ≥1 mã còn lại). Theo bản đồ tier A chỉ 4 họ
  có thể đạt: `rubber_tsr20` (5 mã), `crude` (5), `sugar` (3), `steel_cn` (6). `urea`, `dap` (2 mã), `dry_bulk`,
  `container` (1 mã) **bị loại về cấu trúc** — không có "mã còn lại".
- HSG/NKG (BANNED giao dịch) giữ để đo như bản đồ; capacity báo riêng có/không có mã banned.

## 3. Biến đích, đơn vị, horizon
Đơn vị độc lập = **họ × quý** (N thực báo trong REPORT). Chân đầu ngành (L) và còn lại (R) = trung vị (KQKD) / trung
bình đều (lợi suất) các mã trong chân.
- **(A) KQKD:** `np_d` = (NP_P0 − NP_P4)/Revenue_P4, clip ±0,5, chỉ quý có `Release_Date > sig` (luật b2).
- **(B) Lợi suất** (Close điều chỉnh, mã thiếu giá ở mốc thì bỏ khỏi chân):
  - H0 "hiện tại" = `d0(Q)` → `sig` (đồng thời với cửa sổ tính tín hiệu — KHÔNG giao dịch được, chỉ mô tả tốc độ định giá);
  - H1 "+1M" = `sig` → `sig` + 21 phiên; H3 "+3M" = `sig` → `sig` + 63 phiên (giao dịch được).
  - So với (i) R cùng họ, (ii) universe_pit bình quân đều (thành viên tại t−1, `common.bench`).
  - Thống kê = trung bình theo đơn vị của **sign(c_yoy) × (ret_L − ret_C)** (pp).

## 4. Trial khai trước (9 — dưới trần 12)
| # | Trial | Thống kê | Phía |
|---|---|---|---|
| T1 | A: KQKD sạch hơn | ΔIC = IC_pooled(c_yoy→np_d_L) − IC_pooled(c_yoy→np_d_R) (rank trong họ, như b2) | 2 phía |
| T2 | A: giữ biên pha xuống | TB(np_d_L − np_d_R) trên đơn vị c_yoy < 0 | 2 phía |
| T3 | A: quy mô pha lên | TB(np_d_L − np_d_R) trên đơn vị c_yoy > 0 | 2 phía |
| T4 | B: H0 vs R | TB sign·(L − R) | 2 phía |
| T5 | B: H1 vs R | như trên | 2 phía |
| T6 | B: H3 vs R | như trên | 2 phía |
| T7 | B: H0 vs universe (LẶP) | TB sign·(L − U) | 2 phía |
| T8 | B: H1 vs universe (LẶP) | như trên | 2 phía |
| T9 | B: H3 vs universe (LẶP) | như trên | 2 phía |

Tổng trial tích luỹ dòng hàng hoá/ngành: 17 (26/10) + 12 (A4, đã duyệt, chưa chạy) + **9** = **38**. BH-FDR trong
REPORT tính trên 9 trial của việc này; REPORT báo thêm ngưỡng Bonferroni ×38 để tham chiếu.

## 5. Suy diễn
- CI90: moving-block bootstrap theo **khối 4 quý liên tiếp** (lấy lại khối quý, giữ mọi họ trong quý), 5.000 lần, seed 20261119.
- p: **dịch vòng chung** — dịch chuỗi c_yoy (theo thứ tự quý) cùng một độ dời k cho mọi họ, k ∈ [4, n−4] (loại dịch
  ngắn < 4 quý vì tự tương quan YoY), 2.000 lần; p hai phía = (#|stat_perm| ≥ |stat| + 1)/(B+1). Không hoán vị trong năm.
- IS = quý < 2023Q1, OOS ≥ 2023Q1 (mọi họ chỉ có TE từ 2016-10 ⇒ c_yoy từ 2017Q4 ⇒ tách 2023, giống b2).
- Leave-one-year-out (theo năm của qend): báo min/max thống kê cho mọi trial.
- Chi phí quy đổi: spread L−R hoặc L−U cầm 1 kỳ = 2 chân × 2 chiều × 0,1% = **0,4pp/kỳ**; ngưỡng |TB| > 0,4pp.
- Placebo (KHÔNG phải trial): rổ ngẫu nhiên K=2 mã universe_pit ngoài họ, cùng tercile GTGD60 với đầu ngành tại d0(Q),
  200 lần ⇒ phân vị của T7–T9 trong phân bố placebo (tách "đầu ngành" khỏi "thanh khoản cao").
- Đối chứng tái lập (bắt buộc trước khi đọc T1–T9): tính lại np_d từng mã-quý theo luật b2 (universe tại sig) và so
  với `commodity_cycle_te_20261026/b2_panel.csv` trên các quý ≤ 2026Q2: tỷ lệ khớp |Δ| < 1e-6 ≥ 98%; IC gộp tier A
  c_yoy→np_d của bản tính lại trong khoảng 0,450 ± 0,02. Trượt ⇒ dừng, báo, không đọc kết quả.
- Power: báo MDE (≈ 2,5 × SE bootstrap) cho từng trial.

## 6. GO / NO-GO (khai trước)
- **DISPLAY lens (T1–T3):** đạt khi CI90 không chứa 0 **và** cùng dấu IS/OOS **và** BH q < 0,10 (trên 9). Đạt ⇒ đề
  xuất một dòng hiển thị "đầu ngành/mã còn lại" trong khối nowcast; không gate, không tilt.
- **PREREG-5 tilt/sleeve (chỉ T5, T6, T8, T9 — giao dịch được):** đạt khi đủ TẤT CẢ: CI90 không chứa 0; cùng dấu
  IS/OOS; BH q < 0,10; |TB| > 0,4pp (chi phí); LOYO không năm nào đảo dấu thống kê gộp; capacity (mục 7) đạt ở sổ
  1,5 tỷ. Việc này KHÔNG dựng NAV ⇒ DSR chưa áp; nếu có ô đạt, bước sau là PREREG-5 riêng dựng NAV, cặp pin0%…pin1M,
  DSR ≥ 0,95, quant-skeptic.
- T4, T7 không giao dịch được ⇒ chỉ diễn giải (cơ chế định giá), không bao giờ là GO giao dịch.
- Không ô nào đạt ⇒ NO-GO; không thử biến thể (K, tiêu chí, horizon khác).

## 7. Capacity
Vị thế giả định 10% NAV/mã, chia thực thi 5 phiên ở 20% GTGD ⇒ đạt nếu trung vị GTGD60 ≥ vị thế (1,5 tỷ ⇒ ≥ 0,15 tỷ/phiên;
50 tỷ ⇒ ≥ 5 tỷ/phiên). Báo % đầu ngành-quý đạt từng mức + danh sách đầu ngành quý gần nhất kèm GTGD.
