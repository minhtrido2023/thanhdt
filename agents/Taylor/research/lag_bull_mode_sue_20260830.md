# LAG BULL-mode SUE relax — job Taylor_20260830_164112

## Bối cảnh
Hướng #4 từ `lag_bull_cash_routing_20260825.md`: LAG idle trung bình 28,3% combined NAV trong
BULL vì deal PEAD ít đi. Route-tiền-đi (BAL/parking) đã NO-GO (`lag_bull_cash_routing_20260825.md`
— thêm beta đúng đỉnh cycle, Calmar 1,63→1,41). Hướng MỚI: thay vì route tiền đi, **nới tiêu chí
LAG chính nó** khi ở BULL để bắt thêm deal — KHÔNG đụng 8L rating gate (hard lock 2026-07-27).

## Production hiện tại (đọc từ `pt_v23_audit_2014.py`, dòng ~1003-1053)
- **Entry gate LAG**: `NP_R>=15` (YoY earnings growth ≥15%, đây là trục "earnings-surprise" mà
  dispatch gọi là SUE) **AND** `prior_n_good>=4` (≥4 sự kiện tốt trước đó cùng ticker) **AND**
  `pa_HL3>=5` (decay-weighted (half-life 3 năm) trung bình post_ret các sự kiện tốt trước đó ≥5%).
- `surprise_B_MA = (NP_P0 − mean(NP_P1..P4)) / max(|mean|, 1e9)` clip [-5,5] — dùng để tier weight
  HI/LO (>0.5 → `LAG_HI` 10%, else `LAG_LO` 8%), **KHÔNG dùng làm entry filter**.
- `LAG_SUE_TILT` (3-tier theo tercile surprise) đã **BỊ LOẠI** trước đó (−0,66pp CAGR, cả 2 nửa
  IS/OOS đều tệ hơn — xem comment dòng 1381-1385 code). Không lặp lại hướng đó.

→ Trục "SUE" khả thi nhất để nới là **ngưỡng `NP_R>=15`** — đây chính là bộ lọc earnings-surprise
quyết định event nào được XÉT làm ứng viên LAG, khác hẳn 8L rating (rating là gate CHẤT LƯỢNG
công ty, NP_R là gate ĐỘ LỚN bất ngờ lợi nhuận quý này). `prior_n_good`/`pa_HL3` giữ NGUYÊN để cô
lập đúng 1 trục theo yêu cầu dispatch.

## Giả thuyết (pre-registered TRƯỚC khi chạm return)
Trong BULL/EXBULL với breadth cao (đồng thuận thị trường rộng), PEAD drift kéo dài hơn (tin tốt
được định giá vào chậm hơn do dòng tiền phân tán rộng khắp thị trường thay vì tập trung) →
`NP_R>=15` hiệu chỉnh cho NEUTRAL có thể bỏ sót deal thật (NP_R 10-15%) vẫn có drift đáng kể trong
điều kiện BULL+breadth cao.

## Trục 2 — breadth-tercile (đã chốt 2026-08-22, KHÔNG tự chế lại)
Nguồn: `mike/agents/Taylor/research/strategy_regime_matrix_20260822/b2_breadth.csv` — breadth =
`tav2_mike.universe_pit` %Close>MA200, PIT. Tercile = phân vị breadth HÔM NAY trong 252 phiên
TRƯỚC ĐÓ (rolling, không nhìn trước) — code mirror y hệt `strategy_regime_matrix_20260822_b2.py`.
Điều kiện regime: `state ∈ {4,5}` (BULL/EXBULL, DT5G) **AND** `btile == "HIGH"` tại **entry T+5**
(ngày quyết định vào lệnh, không phải Release_Date — đúng thời điểm thông tin sẵn có khi cân nhắc
entry).

## Ngưỡng NP_R nới — pre-register 2 mức
- **0,8x**: `NP_R >= 12` khi BULL/EXBULL + breadth HIGH (else vẫn 15)
- **0,7x**: `NP_R >= 10.5` khi BULL/EXBULL + breadth HIGH (else vẫn 15)
Chọn tỷ lệ cố định (không percentile tùy chỉnh theo data) để tránh nhìn-trộm distribution rồi mới
chọn ngưỡng đẹp. `prior_n_good>=4` và `pa_HL3>=5` GIỮ NGUYÊN cho cả 2 mức.

## Cơ chế implement
Bản sao nghiên cứu `mike/agents/Taylor/exp_lag_bullmode_20260830/pt_v23_lagbullsue.py` (copy
nguyên văn `pt_v23_audit_2014.py`, KHÔNG đụng file production). Thêm khối env-toggle
`LAG_BULL_SUE` (mặc định `""` = byte-identical production) ngay trước `e_hl3 = ev[_m].copy()`:
mask nới = `(NP_R>=thr_bull) & (prior_n_good>=4) & (pa_HL3>=5) & state∈{4,5} & breadth=HIGH` (cộng
2 gate non-op/forensic sẵn có), OR vào mask gốc. Event chỉ lọt qua nhờ nới được đánh dấu
`_bull_relaxed_new` để audit riêng chất lượng. Tier HI/LO vẫn theo `surprise_B_MA` nhị phân y hệt
sản xuất (không thêm tier mới, tránh lặp lại LAG_SUE_TILT đã bị loại).

## Kế hoạch chạy
Lệnh pin R3 nguyên văn (`data/results_registry.md` §"2026-08-03 RE-PIN"), CHỈ thêm `LAG_BULL_SUE`:
```bash
source /home/trido/thanhdt/WorkingClaude/wc_env.sh   # BQ_LOCAL_CACHE=data/bq_cache
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" \
BQ_CACHE_THREADS=1 AUDIT_END=2026-06-19 LAG_BULL_SUE=<""|12|10.5> \
$DNA_PYEXE mike/agents/Taylor/exp_lag_bullmode_20260830/pt_v23_lagbullsue.py v23a none postbull 0 edge
```
1. Control (`LAG_BULL_SUE=""`) — phải tái lập đúng pin 28,86%/1,90/−17,8%/1,62 TUYỆT ĐỐI (xác nhận
   bản sao trung thực trước khi tin số treatment).
2. Treatment 0,8x (`NP_R>=12`) và 0,7x (`NP_R>=10.5`).
3. Đếm N episode BULL+breadth-HIGH ĐỘC LẬP (contiguous block, không đếm theo số deal) trong IS
   (2014-19) và OOS (2020+) riêng — tránh lặp lỗi N=6 giả-độc-lập của job DC state-gated
   (`dc_state_gated_bull_only_20260830.md`, cùng ngày).
4. Chất lượng deal mới (`_bull_relaxed_new`): so sánh phân phối `post_ret` (proxy PEAD outcome đã
   có sẵn trong `earnings_events_classified.csv`, dùng để tính `pa_HL3`) của deal MỚI vs deal CŨ
   cùng cửa sổ BULL+breadth-HIGH.
5. DSR/PBO nếu GO trên cả IS/OOS. quant-skeptic bắt buộc nếu GO.
