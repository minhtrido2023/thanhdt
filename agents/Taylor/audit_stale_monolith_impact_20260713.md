# Audit tác động monolith `ticker_prune.parquet` stale (06-26 → 07-13) — job Taylor_20260713_143629

**Bối cảnh**: `sync_bq_cache.py` migrate ticker_prune sang chunked `ticker_prune/<year>.parquet` ~06-27;
monolith `data/bq_cache/ticker_prune.parquet` đóng băng 2026-06-26 23:46 (17 ngày). 28 file .py vẫn đọc
monolith (27 research/screen + `trading_bot/executor.py`). User tự phát hiện 07-13. Winston fix + commit
`1630916` lúc 21:44 ICT 07-13 (monolith archive vào `data/archive/ticker_prune_monolith_frozen_20260626.parquet`).

## Kết luận tổng (TL;DR)
1. **LIVE money-path: KHÔNG ảnh hưởng.** SpaceX/ZaloPay tắt cả 3 flag (gap_adaptive/extreme/chase_cap)
   → `_load_gap_ref_data()` return sớm, không bao giờ đọc monolith.
2. **Mọi backtest/production consumer qua `BQ_LOCAL_CACHE` (DuckDB): KHÔNG ảnh hưởng.**
   `bq_local_cache.py` map bảng `ticker_prune` → thư mục chunked (manifest `"ticker_prune/"`), luôn tươi.
   Baseline R3 pin, pt_v23/pt_v4/pt_v22, DC-book, sector_lens_monitor, dc_trigger_gap_backtest,
   probe beta-cap hôm nay: đều không đọc monolith (đã grep xác nhận).
3. **Chase-cap vol-scale trial (review 07-14): bị nhiễm input NHƯNG zero khác biệt hành vi thực tế**
   (đối chiếu từng lệnh, xem §A). Bằng chứng trial mỏng hơn danh nghĩa — khuyến nghị cân nhắc kéo dài ~1 tuần.
4. **EXTREME trial (review ~07-28): nhánh (ii) bị giảm nhạy** bởi rvol thổi phồng trong 07-07→07-13;
   nhánh (i) (floor-band, chỉ quote) không ảnh hưởng. Sau fix còn ~2 tuần tích bằng chứng sạch.
5. **~20 finding R&D 06-26→07-06 chạy qua 27 script: kết luận ĐỀU ĐỨNG VỮNG** (§C) — toàn backtest
   cửa sổ dài 2014+, freeze chỉ cắt 1–8 phiên cuối, biên kết luận đều nhiều pp. Không cần re-run.

## §A — Chase-cap vol-scale (paper `main`, review dự kiến 07-14) — ƯU TIÊN 1

**Cơ chế nhiễm**: `_buy_chase_pct` = clamp(2·rvol_20d, 1.5%, 4%) với rvol từ monolith → mọi phiên paper
dùng rvol vintage 06-26 (KHÔNG ghi journal — nhiễm âm thầm).

**Phạm vi phiên thực tế**: chỉ 5 phiên có log (07-07, 07-08, 07-09, 07-10, 07-13). KHÔNG tồn tại log
07-01→07-06 (trial danh nghĩa bắt đầu 07-01 — bằng chứng thực tế ít hơn kế hoạch). 07-08/07-09 bị
GHOST-pause toàn bộ (0 lệnh) → **chỉ 3 phiên có lệnh thật**.

**Định lượng sai lệch input (stale vs true, 6 mã ACB/FPT/HDB/HPG/MBB/VNM):**
- rvol_20d stale lệch **+3% → +59%** (tệ nhất ACB +55–59% vì vol thật của ACB đã giảm mạnh sau 06-26;
  MBB −8% hai phiên cuối; median ~+10–20%).
- prior_close stale lệch tới **−8.3%** (HDB 07-08); phổ biến ±1–3%.
- gap_z stale hoàn toàn sai bản chất (đo drift tích lũy 17 ngày thay vì gap qua đêm): HDB stale gap_z
  +5.2→+8.5 (thật ≈ −0.4..0); **VNM 07-07/07-08 stale gap_z = −2.03/−2.40 vượt ngưỡng override −2.0 GIẢ**
  (thật ≈ −0.22).

**Hành vi thực tế — đối chiếu TỪNG lệnh (18 buy PLACE × 3 phiên):**
- **Zero khác biệt.** Mọi giá đặt đều dưới cap bất kể vintage. 2 lệnh duy nhất đặt TRÊN cap static
  (MBB 25.700 vs lim_static 25.679; HDB 27.650 vs 27.608 — phiên 07-07, chứng minh widen-path có chạy
  thật) đều vẫn hợp lệ dưới cap tính bằng rvol ĐÚNG (lim_true MBB 25.710, HDB 27.688) → giá đặt
  identical dù dữ liệu tươi.
- **False-fire gap-override VNM không thành hiện thực**: 07-07 chạy phiên chiều (override chỉ tác động
  09:15–09:45); 07-08 ghost-pause 0 lệnh. 07-10/07-13 chạy 09:15 nhưng gap_z stale đều > −2.0.
- Không có event EXTREME/GAP_OVERRIDE/chase nào trong journal cả 5 phiên.

**Hàm ý cho review 07-14** (báo cáo rủi ro, KHÔNG tự quyết hoãn/hủy):
- Bằng chứng wiring + fail-safe vẫn dùng được (stress 15/15 độc lập với data; widen-path chứng minh
  hoạt động; hành vi realized identical với data đúng — đã verify từng lệnh, không suy đoán).
- NHƯNG điều kiện (a) "paper sạch, wiring đúng trên quote thật" chỉ đạt với input rvol sai vintage
  ở 100% số phiên, và chỉ 3 phiên có lệnh. Winston đã re-run stress PASS sau fix (commit 1630916).
- **Khuyến nghị**: nếu muốn giữ chuẩn bằng chứng như plan, kéo dài paper thêm ~1 tuần (3–5 phiên
  fresh-vintage) rồi mới review/flip LIVE. Nếu review vẫn tiến hành 07-14: kết quả đối chiếu từng-lệnh
  ở trên là căn cứ định lượng rằng contamination không đổi hành vi. Mike/user quyết.

## §B — EXTREME-regime gate (review ~07-28)
- Nhánh (i) cận-sàn: chỉ dùng quote (floor/last) → KHÔNG ảnh hưởng. Poll-1 floor guard (case PNJ) cũng quote-only.
- Nhánh (ii) r15 < −3·rvol: rvol stale thổi phồng (ACB +55–59%) → ngưỡng RỘNG hơn thật → sensor GIẢM NHẠY
  trong 07-07→07-13. "Zero false-trigger" giai đoạn này yếu hơn danh nghĩa cho nhánh (ii) (sensor bị che
  một phần — không phải bằng chứng sạch về độ đặc hiệu). Không có trigger nào fire (kỳ vọng benign đúng).
- Sau fix, từ 07-14 → ~07-28 còn ~2 tuần tích bằng chứng đúng vintage — đủ nếu tính điều kiện (a)
  "4 tuần benign" từ dữ liệu sạch một cách khoan dung, thiếu nếu đòi toàn bộ cửa sổ sạch. Đề xuất: ghi rõ
  trong review 07-28 rằng cửa sổ 07-07→07-13 chỉ tính cho nhánh (i).

## §C — Finding R&D 06-26→nay chạy qua 27 script (sweep bus đầy đủ, 47 event khớp)
Tất cả chạy trong khoảng 06-27→07-06, monolith khi đó thiếu 1–8 phiên cuối. Đánh giá từng nhóm:
| Finding (ngày chạy) | Thiếu dữ liệu | Ảnh hưởng |
|---|---|---|
| lag_dnpr_event_study (06-27) | ≤1 phiên | Không — event study 2012+ |
| gap_adaptive_proxy Layer-3 (06-29) | ~1 phiên | Không — study 2014+ |
| fair-value thread CLOSED + gq_score FAIL (06-30) | ~2 phiên | Không — kết luận NEGATIVE trên 2014+, thiếu 2 ngày không cứu nổi |
| Sector sweeps #10–15 (compounder/retail/bank/RE/logistics/fertchem/steel/energy/pharma/fnb/tech/securities/aviation, 06-30) | ~2 phiên | Không — lens-not-book trên cửa sổ dài, biên nhiều pp |
| textile #16 + livestock #17 (07-05→07-06) | ~6 phiên | Kết luận khung: KHÔNG. Caveat nhẹ: claim "MSH in entry window"/"DBC WATCH" dùng giá ≤06-26 — refresh khi tiện, không phải input production |
| construction #18 (HTN AVOID), SOE #19, holdco #20 (07-06) | ~7 phiên | Không — framework/exclusion dài hạn; HTN AVOID càng conservative |
| converge_union REFUTED (07-06) | ~7 phiên | Không — biên 12.07% vs 18.75% CAGR, 7 phiên không lật |
| neutral_glide (Part1 waterfall CONFIRMED / Part2 glide REFUTED, 07-06) | ~7 phiên | Không — DSR 0.775/Sharpe-flat trên 2014+, đã có caveat insurance-grade sẵn |
| securities off-by-one fix re-run (07-06) | ~7 phiên | Không — calibration UNCHANGED là kết luận chính |

**Không finding nào cần re-run.** Lý do cấu trúc: các script này là backtest/event-study lịch sử — monolith
freeze tương đương "chạy backtest với data cắt ở 06-26", điều mà chính các finding đó không hề claim ngược lại.
Khác hẳn executor.py — nơi cần dữ liệu "mới nhất" (rolling rvol/prior_close) mỗi phiên.

## §D — Đính chính tiền đề dispatch
Tiền đề "bất kỳ kết luận nào chạy qua 27 script từ 06-26 có thể đã dùng dữ liệu cũ mà không ai biết" đúng
về mặt kỹ thuật nhưng phạm vi hẹp hơn nhiều so với lo ngại: (a) tầng BQ_LOCAL_CACHE DuckDB — đường dữ liệu
của MỌI backtest pinned/production — map ticker_prune vào chunked dir tươi từ đầu, chưa bao giờ stale;
(b) 27 script đọc trực tiếp đều là script nghiên cứu lịch sử, nơi 1–8 phiên cuối không mang kết luận;
(c) consumer "cần-dữ-liệu-mới-nhất" duy nhất là executor.py — đã định lượng đầy đủ ở §A/§B.

## Số liệu gốc
Bảng stale-vs-true đầy đủ 6 mã × 5 phiên (prior_close/rvol/gap_z) + đối chiếu 18 lệnh: in trong log phiên
này; tái lập bằng cách so `data/archive/ticker_prune_monolith_frozen_20260626.parquet` (stale) với
`data/bq_cache/ticker_prune/2026.parquet` (true), cùng công thức `_load_gap_ref_data` (tail(22), pct_change,
std(20)) và plan/journal `data/trade_plans/plan_main_*.json` + `data/execution_logs/exec_main_*_journal.csv`.
