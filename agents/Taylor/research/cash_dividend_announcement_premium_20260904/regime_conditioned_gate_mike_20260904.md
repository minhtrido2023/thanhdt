# Regime-conditioned dividend pre-ex gate — phân tích tương tác Mike 2026-09-04

> ⚠️ **ĐÍNH CHÍNH 2026-09-04 (Taylor, job `Taylor_20260904_111503`)**: mapping regime SAI ở bản đầu
> (dùng `{0:CRISIS,1:BEAR,2:NEUTRAL,3:BULL,4:EXBULL}`). Mapping ĐÚNG theo `macro_state_live.py:42`
> (`NEUTRAL, CRISIS, BEAR = 3, 1, 2`) + xác nhận trực tiếp bằng BQ
> `vnindex_5state_dt5g_live`: **1=CRISIS, 2=BEAR, 3=NEUTRAL, 4=BULL, 5=EXBULL** (không có state 0).
> Mọi nhãn regime bên dưới lệch một bậc so với bản gốc — "gate mở ở BEAR/NEUTRAL" ban đầu THỰC RA
> là **CRISIS/BEAR**. Bảng dưới đây đã được thay bằng số **tái lập độc lập** (script riêng của
> Taylor, không copy số Mike) — chi tiết đầy đủ + robustness bổ sung ở
> `reproduce_gate_results_20260904.md`. Prereg chính thức: `prereg_regime_gate_20260904.md`.

> Tiếp nối proxy sprint Taylor_20260904_094347 (NO-GO trên so sánh gộp CASH vs STOCK).
> User hypothesis: hiệu ứng cổ tức tiền mặt chỉ rõ trong bear/crisis/neutral, mất trong bull/mania.
> Dữ liệu: cash_events_analyzed.csv + DT5G production states (BQ `vnindex_5state_dt5g_live`)
> + deposit_rate_vn.py PIT (backward as-of tại t14).

## Kết quả chính — mẫu sạch giá>=10k, raw_yield<=50%, N=1.552 (excess>0 & prior_3y>=3)

AR = pre-ex[−14,−1] − baseline[−28,−15] − VNINDEX, regime + deposit-rate đo tại ex−14d (PIT).
Số liệu tái lập độc lập (Taylor); N lệch ~1-3% so với bản Mike (5-10 sự kiện/regime, do khác biệt
nhỏ trong biên lọc/đếm `prior_3y`) — không đổi kết luận, dùng số này làm chuẩn.

| Regime (excess>0 & prior_3y>=3) | N | ticker | median AR | hit | p (vs 0) | STOCK cùng regime | MWU 2 phía p |
|---|---|---|---|---|---|---|---|
| CRISIS | 329 | 208 | +1,51% | 56% | 0,0053 | +0,06% | 0,109 |
| BEAR | 105 | 91 | +2,33% | 64% | 0,0008 | +2,02% | 0,553 |
| NEUTRAL | 809 | 324 | +0,39% | 52% | 0,142 (ns) | −0,50% | 0,067 |
| BULL | 274 | 179 | **−1,80%** | 43% | 0,0109 (ÂM) | +0,80% | 0,096 |
| EXBULL | 35 | 34 | +0,89% | 54% | 0,852 (ns, quá mỏng) | −2,57% | 0,521 |

BULL đảo dấu: trong mania, cổ phiếu yield cao TỤT so với baseline trước ex-date (value drag) — xác
nhận H2. **Không regime nào tách CASH khỏi STOCK_DIV ở mức two-sided p<0,05** (gần nhất: NEUTRAL
p=0,067, BULL p=0,096) — cash-specificity vẫn là điểm yếu đã biết, KHÔNG cải thiện sau khi sửa
mapping.

## Gate: regime∈{CRISIS,BEAR} & excess>0 & prior_3y>=3 & giá>=10k
- N=434, 243 ticker, median **+1,88%**, hit 58,1%, wilcoxon p=5,5e-05
- Cluster-robust (median-of-ticker-medians): +1,98%, p=0,0006
- Tail: p5=−17,4%, p95=+23,1% — phân tán lớn, cần diversification
- Dose-response nội bộ: excess 0-4pp +1,09% → 4-8pp +2,50% → >8pp +2,66% (đơn điệu, giữ nguyên)
- Bản chặt (excess>4pp): N=152, median +2,50%, hit 61%, cluster +2,79%
- Split-half: 2014-2019 N=136 median +0,22% p=0,66 (ns) | 2020+ N=298 median +2,32% p=7,0e-06
- LOYO bỏ 2022: N=292, median +1,04% (còn dương, giảm ~45%)
- **AR window robustness** (cùng gate, đổi cửa sổ pre-ex): [-10,-1] N=433 median +1,13% p=0,0057
  | [-14,-1] (gốc) median +1,88% | [-20,-1] N=433 median +2,26% p=1,5e-08 — **KHÔNG đảo dấu ở cả 3
  cửa sổ**, giữ ý nghĩa thống kê ở cả 3.

## Ticker & sector concentration trong gate (kiểm tra mới)
- Ticker: top 1 (DHA) = 7/434 = 1,6% N; **0 ticker nào >3% N** — không có single-name driver.
- Sector (ICB level-1): Industrials (mã 2xxx) chiếm 32,7% N (142/434) — cao nhất nhưng dưới ngưỡng
  FAIL 40%. Loại bỏ sector này, phần còn lại (N=292) vẫn dương có ý nghĩa: median +1,13%, p=0,022.
  Không phải hiệu ứng 1-ngành.

## 4 caveat PHẢI mang theo (giữ nguyên tinh thần bản gốc, số liệu đã cập nhật)
1. **Cash-specificity KHÔNG chứng minh được ở mức two-sided p<0,05 tại BẤT KỲ regime nào** — kể cả
   CRISIS/BEAR (p=0,109/0,553). Phần "regime mở → drift trước corp-action" có thể là hiệu ứng
   CHUNG quanh corporate action nói chung; phần cash-specific rõ nhất chỉ nằm ở dose-response theo
   excess yield trong gate + chiều âm ở BULL.
2. **Era-concentration**: 2014-2019 ≈ 0 (p=0,66), phần lớn edge từ 2020+ (p=7e-06). LOYO bỏ 2022 →
   vẫn dương (+1,04%) nhưng giảm gần một nửa so với full gate (+1,88%).
3. Chuỗi deposit rate là CANONICAL-PROXY neo hồi tố (caveat b registry) — backtest mang hindsight nhẹ.
4. Sector Industrials chiếm gần 1/3 N trong gate — không đủ để FAIL (<40%) nhưng đáng theo dõi nếu
   universe live nghiêng mạnh hơn về ngành này.

## DGC 2026-09 qua gate?
excess +11,8pp ✓, prior đều ✓, giá 43k ✓ — nhưng DT5G hôm nay = **BULL** (state=4) → theo mapping
đúng, gate ĐÓNG (gate chỉ mở ở CRISIS/BEAR, và BULL có median AR ÂM theo H2). Kết luận DGC không đổi
so với bản gốc, chỉ đổi LÝ DO (trước ghi nhầm là "BULL từ state 3", nay đúng là state 4 = BULL).

## Trạng thái
Prereg chính thức đã khoá (`prereg_regime_gate_20260904.md`), số liệu tái lập độc lập xong
(`reproduce_gate_results_20260904.md`). Verdict cuối: xem file kết quả — chưa quant-skeptic, chưa
wire production.
