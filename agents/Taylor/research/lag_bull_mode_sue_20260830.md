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

## KẾT QUẢ

⚠️ Chạy trên `BQ_LOCAL_CACHE=data/bq_cache` (cache rolling, `wc_env.sh` mặc định) chứ KHÔNG phải
snapshot đóng cứng `bq_cache_asof20260729_postrestate` dùng để pin R3 — nên mức tuyệt đối control
**29.13%** lệch so với pin registry 28.86% (data-drift bình thường, đã ghi nhận nhiều lần trong
registry). Không ảnh hưởng kết luận vì cả 3 chân chạy **cùng lúc, cùng cache snapshot** → so sánh
A/B nội bộ vẫn hợp lệ (đúng 1 biến khác nhau).

| Config | CAGR | Sharpe | MaxDD | Calmar | Final NAV | self-check |
|---|---|---|---|---|---|---|
| **Control** (production, NP_R>=15 mọi state) | **29.13%** | 1.91 | −17.8% | **1.64** | 1.209,28B | 0 VND (BAL+LAG) |
| Treatment 0.8x (NP_R>=12 nếu BULL/EXBULL+breadth-HIGH) | 28.96% | 1.90 | −17.8% | 1.63 | 1.188,78B | 0 VND |
| Treatment 0.7x (NP_R>=10.5 nếu BULL/EXBULL+breadth-HIGH) | 28.96% | 1.90 | −17.8% | 1.63 | 1.188,78B | 0 VND |

**Cả 2 mức nới đều THUA control: −0.17pp CAGR, −0.01 Sharpe, −0.01 Calmar, −20.5B NAV cuối kỳ.**
T07 và T08 cho **kết quả giống hệt nhau** dù T07 nới thêm 3 sự kiện nữa (16 vs 13 theo log harness)
— book LAG cash-constrained (oversubscribed ~6x, ghi nhận trước đây) nên vài ứng viên biên thêm
không đổi thực tế được funding gì.

### Toàn bộ delta nằm ở ĐÚNG 1 năm (2021) — N hiệu lực = 2, không phải 8
Per-year breakdown: 2014-2020 và 2022-2026 **giống hệt** giữa control/treatment; chỉ **2021** khác
(control +109.40% vs treatment +104.98%, cả 2 mức nới). Đếm episode BULL(4,5)+breadth-HIGH liên
tục 2014+ (PIT, không nhìn trước): **N=8 episode**, nhưng CHỈ 2 episode thực sự sinh ra deal LAG
mới nhờ nới ngưỡng — **2020-10-06→2021-02-18** (3-4 deal mới) và **2021-10-27→2021-12-02** (9-11
deal mới); 6 episode còn lại (kể cả 2 episode 2025) sinh **0 deal mới**. IS(<2020) chỉ có 1 episode
(2018-01, 2 phiên, không sinh deal nào) → **không có bằng chứng IS nào cho cơ chế này** — không thể
walk-forward theo đúng nghĩa vì hiệu ứng gần như hoàn toàn OOS và tập trung vào đúng 1 năm.

### Chất lượng deal mới KHÔNG tệ — cơ chế thua là CROWDING-OUT, không phải noise
Deal chỉ lọt qua nhờ nới (proxy `post_ret`, cùng metric dùng tính `pa_HL3` production):
- thr=12: 12 deal mới, mean post_ret **+8.69%**, median +4.78%, win-rate **75.0%**
- thr=10.5: 15 deal mới, mean post_ret **+9.22%**, median +4.72%, win-rate **80.0%**
- So baseline (event NP_R>=15 đã lọt gate, cùng regime BULL+breadth-HIGH): mean **+9.80%**,
  win-rate 68.8% (263 sự kiện, 2020+2021) — deal mới xấp xỉ CÙNG mức chất lượng, không phải noise.

→ Deal mới KHÔNG rác. Cơ chế thua thật: batch 2021-Q3 (BWE/FOX/PET/NCT/CPC/FCM/NAG, entry
2021-10-27→2021-11-08) trộn lẫn cả tên yếu (FOX −5.0%, NCT −2.5%, PET 0%, BWE +0.45%) và tên mạnh
(NAG +17.5%, FCM +13.5%) rơi ĐÚNG vào cửa sổ book đã cash-constrained của **năm compounding tốt
nhất hệ thống (2021 +109%)** — thêm ứng viên cạnh tranh vào đúng lúc vốn khan hiếm nhất trong năm
nền tảng nhất của toàn bộ track record khiến hỗn hợp funding-thật bị pha loãng, dù danh sách ứng
viên xét riêng lẻ không tệ. Thiệt hại tập trung đúng năm compounding lớn nhất → tốn nhiều hơn tưởng
(sequence-of-returns: mất capacity ở năm tốt nhất đắt hơn mất ở năm thường).

## VERDICT: NO-GO
Sai dấu ở CẢ 2 mức ngưỡng (không phải noise 1 mức) VÀ N hiệu lực chỉ = 2 episode độc lập (cả 2 đều
OOS, không có đối chứng IS) — hai lý do NO-GO ĐỘC LẬP nhau, không cần chờ DSR/PBO hay quant-skeptic
(chỉ bắt buộc khi verdict là GO). Không đề xuất wire. Bài học tái dùng: LAG book cash-constrained
là ràng buộc THẬT — bất kỳ hướng "nới cửa nạp thêm deal" nào (kể cả deal chất lượng tốt) đều có
rủi ro loãng vốn đúng lúc cần vốn nhất, không chỉ là câu hỏi "deal mới có tốt không".

## File / lệnh tái lập
- Harness: `mike/agents/Taylor/exp_lag_bullmode_20260830/pt_v23_lagbullsue.py` (copy nghiên cứu,
  KHÔNG đụng `pt_v23_audit_2014.py` production; `git status` sạch trên file canonical).
- Diagnostic (danh sách deal mới + N-episode, không chạy full NAV): `.../gate_diagnostic.py`.
- CSV output: `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_univpit_lagbullsue{12|10p5}.csv`
  (tag tự động qua `_qs_tag`, không đụng CSV canonical R3).
- Lệnh (xem §Kế hoạch chạy ở trên), `LAG_BULL_SUE=""` / `"12"` / `"10.5"`.

## Sự cố phụ đã tự phát hiện + sửa (coding_guidelines §8)
Bản đầu `pt_v23_lagbullsue.py` chỉ nối thêm `_qs_tag` bên trong khối `LAG_BULL_SUE` — nhưng
`AUDIT_PATH` đã được TÍNH XONG ở dòng ~677, TRƯỚC khối này (nằm trong section [4], chạy sau).
Hậu quả: cả 3 chân (control/T08/T07) chạy song song đều RACE ghi cùng 1 file bare-path
`data/v23_golive_audit_2014_now_..._advprice_univpit.csv` — đúng dạng lỗi §8 cảnh báo. Số liệu
CAGR/Sharpe/MaxDD/Calmar/self-check báo cáo ở trên KHÔNG bị ảnh hưởng (tính từ DataFrame trong bộ
nhớ, in ra console TRƯỚC bước ghi CSV, không đọc lại từ file) — nhưng CSV trên đĩa đã bị ghi đè lẫn
nhau. Đã: (1) xoá file lẫn lộn đó (không map với entry canonical nào trong registry — kiểm tra
grep không thấy filename này được cite ở đâu, an toàn để xoá), (2) sửa code: đổi thẳng `AUDIT_PATH`
(mutate trực tiếp) thay vì nối `_qs_tag` — có ghi log dạng comment giải thích lý do trong code.
Muốn tái lập số CSV-level phải chạy lại bằng bản đã sửa (3 lệnh ở §Kế hoạch chạy, giờ ra 3 file
tách biệt: `..._advprice_univpit.csv` (control) / `..._lagbullsue12.csv` / `..._lagbullsue10p5.csv`).
