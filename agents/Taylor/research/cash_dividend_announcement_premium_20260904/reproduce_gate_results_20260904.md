# Regime-conditioned cash-dividend pre-ex gate — tái lập độc lập + verdict chính thức

**Job**: `Taylor_20260904_111503` · **Ngày**: 2026-09-04 · Prereg: `prereg_regime_gate_20260904.md`
Script: `reproduce_gate.py` (độc lập với script exploratory của Mike, không copy code/số).

## Verdict: **NO-GO** (không wire làm lens cash-dividend-specific ở dạng hiện tại)

2/5 tiêu chí FAIL đã prereg đều fire:
1. **LOYO loại 2022 mất ý nghĩa ở mức cluster-robust**: N=292, median vẫn dương (+1,04%) nhưng
   cluster-robust (median-của-median-theo-ticker) tụt xuống +0,25% với **p=0,227** — mất ý nghĩa
   thống kê hoàn toàn. Toàn bộ sức mạnh thống kê của gate phụ thuộc nặng vào 1 năm (2022).
2. **Không tách được CASH khỏi STOCK_DIV (negative control) ở CẢ CRISIS lẫn BEAR**, two-sided MWU:
   CRISIS p=0,109, BEAR p=0,553 — cả hai ≥0,05. Đây là điểm yếu đã ghi nhận trước khi chạy (prereg
   §3), không phải phát hiện mới, nhưng theo đúng luật đã khoá: bất kỳ tiêu chí FAIL nào đúng ⇒
   FAIL, không được "cứu" bằng lý do đã biết trước.

3/5 tiêu chí PASS (không đủ để đảo verdict một mình): ticker/sector concentration trong ngưỡng,
AR window robustness không đảo dấu.

**Ý nghĩa thực tế**: mapping regime bị sửa đúng không thay đổi kết luận tổng thể của proxy sprint
trước (`Taylor_20260904_094347`, NO-GO) — hiệu ứng "cổ tức tiền mặt trước ex-date, mạnh hơn ở
CRISIS/BEAR" vẫn KHÔNG đủ vững để tin là cash-dividend-specific khi soi bằng đúng 2 stress-test đã
tự cam kết trước (leave-one-year-out + negative control cùng regime). Có thể là drift chung quanh
corporate action (không đặc thù cổ tức tiền mặt) + đóng góp bất thường của riêng năm 2022.

## Mapping regime (xác nhận trực tiếp, không suy diễn)
`macro_state_live.py:42` (`NEUTRAL, CRISIS, BEAR = 3, 1, 2`) + BQ:
```
SELECT state, COUNT(*) FROM tav2_bq.vnindex_5state_dt5g_live GROUP BY state
1: 489, 2: 241, 3: 1947, 4: 422, 5: 60
```
→ **1=CRISIS, 2=BEAR, 3=NEUTRAL, 4=BULL, 5=EXBULL**, không có state 0. Bản Mike gốc lệch 1 bậc
(dùng 0-indexed sai) — đã xác nhận và sửa trong `regime_conditioned_gate_mike_20260904.md`.

## Pipeline tái lập
- `raw_events.csv` (12.964 CASH+STOCK_DIV events, có sẵn từ sprint proxy) → lọc N/A boundary
  price/index (−544) + zero/neg price (−8) → N=12.411.
- `prior_3y`: đếm số CASH event CÙNG ticker với `ex_date` trong `(event.ex_date−1095d,
  event.ex_date)`, tính trên toàn bộ lịch sử CASH (không áp filter giá/yield khi đếm).
- Deposit rate PIT: `deposit_rate_vn.merge_deposit(df, time_col='t14')` (as-of backward, 26 mốc
  đóng băng + phần mở rộng append-only).
- `excess` = `div_vnd/c14*100 − deposit_rate_pit` (điểm %).
- Regime PIT: as-of backward merge với `dt5g_state_history.csv` (kéo trực tiếp từ
  `tav2_bq.vnindex_5state_dt5g_live`, 2014-01-02→2026-09-04, 3.159 phiên) tại `t14`.
- Eligible pool: `c14>=10000 & raw_yield<=0.50 & regime not null` → N=5.374 (2014-01-22..2026-06-01).
- Subset `excess>0 & prior_3y>=3` → N=1.552.

## Per-regime table (excess>0 & prior_3y>=3) — số tái lập độc lập
AR = (Close[ex−1]/Close[ex−14]−1) − (Close[ex−15]/Close[ex−28]−1) − (VNINDEX[ex−1]/VNINDEX[ex−14]−1).

| Regime | N | ticker | median AR | hit | Wilcoxon p (vs 0) | STOCK cùng regime N | STOCK median | MWU 2 phía p |
|---|---:|---:|---|---|---|---:|---|---|
| CRISIS | 329 | 208 | +1,51% | 56% | 0,0053 | 161 | +0,06% | 0,109 |
| BEAR | 105 | 91 | +2,33% | 64% | 0,0008 | 55 | +2,02% | 0,553 |
| NEUTRAL | 809 | 324 | +0,39% | 52% | 0,142 (ns) | 376 | −0,50% | 0,067 |
| BULL | 274 | 179 | **−1,80%** | 43% | 0,0109 (ÂM) | 121 | +0,80% | 0,096 |
| EXBULL | 35 | 34 | +0,89% | 54% | 0,852 (ns) | 10 | −2,57% | 0,521 |

**H2 xác nhận**: BULL median AR âm có ý nghĩa (p=0,0109) — value-drag trong mania, đúng hướng giả
thuyết. **H3 (dose-response)**: giữ trong gate (xem dưới). **H1**: gate CRISIS+BEAR dương có ý
nghĩa ở event-level VÀ cluster-robust FULL-sample, nhưng KHÔNG bền dưới LOYO (xem verdict).

Lưu ý N lệch nhẹ (~1-3%, 5-10 sự kiện/regime) so với bản Mike (CRISIS 332→329, BEAR 107→105,
NEUTRAL 819→809, BULL 280→274, EXBULL 32→35) — do khác biệt nhỏ trong cách đếm `prior_3y`/biên lọc
làm tròn. Không đổi hướng hay độ lớn kết luận nào. **Số trong bảng này là chuẩn** (script độc lập,
tự viết lại từ đầu, không copy).

## Gate: regime∈{CRISIS,BEAR} & excess>0 & prior_3y>=3 & c14>=10000
- N=434, 243 ticker, median **+1,88%**, hit 58,1%, Wilcoxon p=5,5e-05
- Cluster-robust (median-của-median-theo-ticker): +1,98%, N_ticker=243, p=0,0006
- Tail: p5=−17,4%, p95=+23,1%
- Bản chặt (excess>4pp): N=152, 111 ticker, median +2,50%, hit 61%, cluster-robust +2,79%
- Dose-response: 0-4pp N=282 +1,09% → 4-8pp N=96 +2,50% → >8pp N=56 +2,66% — đơn điệu, giữ nguyên.
- Split-half: 2014-2019 N=136 median +0,22% p=0,66 (ns) | 2020+ N=298 median +2,32% p=7,0e-06

## LOYO (bỏ 2022) — điểm FAIL #1
- Event-level: N=292, median **+1,04%**, Wilcoxon p=0,056 (borderline, không <0,05)
- **Cluster-robust: median +0,25%, N_ticker=193, p=0,227 — MẤT Ý NGHĨA THỐNG KÊ**
- Kết luận: gate PHỤ THUỘC NẶNG vào năm 2022 ở mức đã kiểm soát cho việc 1 ticker đóng góp nhiều
  sự kiện (cluster). Đây chính là fail criterion đã tự cam kết trước khi nhìn outcome.

## AR window robustness (điểm PASS)
Cùng gate 434 sự kiện, chỉ đổi biên cửa sổ pre-ex (giữ nguyên baseline [-28,-15] và regime/excess đo
tại ex-14 như prereg):

| Cửa sổ pre-ex | N | median AR | Wilcoxon p |
|---|---:|---|---|
| [-10,-1] | 433 | +1,13% | 0,0057 |
| [-14,-1] (gốc) | 434 | +1,88% | 5,5e-05 |
| [-20,-1] | 433 | +2,26% | 1,5e-08 |

Không đảo dấu ở cả 3 cửa sổ, giữ ý nghĩa thống kê ở cả 3 — FAIL criterion #5 KHÔNG fire.

## Ticker & sector concentration — điểm PASS
- Ticker: top 1 (DHA) = 7/434 = 1,6% N. **0/243 ticker vượt 3% N** (ngưỡng ~13 events).
- Sector (ICB level-1, ANY_VALUE 2025+ snapshot per ticker): Industrials (2xxx) = 142/434 = 32,7% N
  — cao nhất, dưới ngưỡng FAIL 40%. Loại sector này: N=292 còn lại, median +1,13%, Wilcoxon
  p=0,022 — **hiệu ứng SỐNG SÓT khi loại sector lớn nhất**, không phải artifact 1-ngành.

## Kết luận & khuyến nghị
- **NO-GO cho việc wire "gate cash-dividend-specific theo regime"** dưới dạng đã prereg — 2 tiêu
  chí FAIL tự cam kết đều fire, đặc biệt LOYO cluster-robust (p=0,227) là bằng chứng mạnh rằng
  effect không bền ngoài 2022.
- Concentration (ticker/sector) và AR-window đều PASS — nếu sau này muốn thử lại, đây KHÔNG phải
  chỗ cần sửa; chỗ cần giải quyết là (a) cash-vs-stock distinguishability và (b) độ bền theo năm.
- Không cần dispatch quant-skeptic thêm — verdict NO-GO tự thân dựa trên đúng tiêu chí FAIL đã
  prereg (giống tinh thần sprint trước `proxy_methodology_results.md`), không phải một claim GO
  cần kiểm chứng đối kháng.
- File `regime_conditioned_gate_mike_20260904.md` đã được đính chính mapping + thay bảng số theo
  kết quả tái lập này.
