# DT5G r_score → state reconciliation pack (2026-06-02, BigQuery-sourced)

**Mục tiêu:** dev tái lập ĐỘC LẬP toàn bộ chuỗi `BQ raw → eligible basket → daily aggregates →
7 factors → r_score → state`, đối chiếu từng ngày. **TẤT CẢ dữ liệu lấy từ BigQuery — KHÔNG dùng
file local.** Mọi bảng/CSV trong pack này đều sinh từ BQ vintage **2026-06-02**.

## 0. Single source of truth = BigQuery (vintage 2026-06-02)
| Bảng | Nội dung | MAX(time) |
|---|---|---|
| `tav2_bq.ticker` (ticker='VNINDEX') | giá/PE chỉ số (spine) | 2026-06-02 |
| `tav2_bq.ticker` (universe) | giá/khối lượng từng mã | 2026-06-02 |
| `tav2_bq.vnindex_5state_dt_4gate` | base DT-4gate state (đã deploy) | 2026-06-02 |
| `tav2_bq.vnindex_5state_tam_quan_v34b_clean` | v3.4b state | 2026-06-02 |
| `tav2_bq.vnindex_5state` | LIVE canonical | 2026-06-02 |
Backup trước deploy: `vnindex_5state_archive_tinh_te_20260602_213635`.

## 1. RAW pull từ BQ (chạy y hệt để có cùng input)
**Universe (mỗi mã, mỗi ngày):**
```sql
SELECT t.time, t.ticker, t.Close, t.Price, t.Volume, t.MA50, t.D_CMF
FROM tav2_bq.ticker AS t
WHERE t.time >= '2013-01-01'
  AND t.ticker NOT IN ('VNINDEX','VN30')
  AND t.ticker NOT LIKE 'VN30F%' AND t.ticker NOT LIKE 'E1VFVN30%' AND t.ticker NOT LIKE 'FUE%'
  AND t.Close IS NOT NULL AND t.Close > 0
```
**VNINDEX (spine, PE):**
```sql
SELECT t.time, t.Close, t.VNINDEX_PE, t.MA200, t.D_CMF, t.D_RSI, ...
FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' ORDER BY t.time
```
**Breadth-decoupling guard (giống live engine `macro_state_live.py`):**
```sql
SELECT t.time, AVG(IF(t.Close>t.MA200,1.0,0.0)) AS Breadth_MA200, COUNT(*) AS Breadth_Total_MA200
FROM tav2_bq.ticker AS t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.MA200 IS NOT NULL AND t.time BETWEEN DATE '2014-01-01' AND DATE '<end>'
GROUP BY t.time
```
*(Đổi 2026-06-02 từ file Downloads → BQ `ticker_prune` để khớp live engine.)*

## 2. Eligibility (rổ EW mỗi ngày) — PRODUCTION
- `tv = Close * Volume` (production; `Price*Volume` chỉ dùng khi bật env TV_PRICE=1)
- `tv_avg60 = rolling(60, min_periods=30).mean()` của `tv`, mỗi mã
- `session_n` = số phiên lịch sử tới ngày đó
- **eligible = (session_n >= 252) AND (tv_avg60 >= 500e6)**

## 3. Daily aggregates → EW close (file `vnindex_5state_ew_daily_aggregates.csv`)
- `ret_ew = mean(log_ret)` trên rổ eligible; `breadth = mean(above_ma50)`; `cmf_med = median(D_CMF)`
- `above_ma50 = 1 if Close>MA50 else 0`; `log_ret = ln(Close/Close_prev)`
- `close_ew = 100 * exp(cumsum(ret_ew))`; `close_ew_scaled` = neo về VNINDEX tại 2014-01-03

## 4. Factors → r_score → state (file `vnindex_5state_ew_full.csv` — đã có sẵn r_score)
- 7 factor tính TRÊN `close_ew_scaled`: P3M=close/close[-60]−1, P1M=close/close[-20]−1,
  MA200dev=close/MA200−1, RSI Wilder-14, MACD-hist(12,26,9), CMF(=cmf_med), Breadth
- **Expanding percentile rank** (min 252 phiên) từng factor → composite có TRỌNG SỐ:
  **P3M 0.30 · P1M 0.10 · MA200 0.15 · RSI 0.15 · MACD 0.10 · CMF 0.08 · Breadth 0.12** = `r_score`
- `r_score_ema = EMA(alpha=0.40)` của r_score → phân ngưỡng (CRISIS/BEAR/NEUTRAL/BULL/EX-BULL)
- **PE override:** nếu `VNINDEX_PE > expanding-P90(VNINDEX_PE)` và state==EX-BULL(5) → hạ về BULL(4)
- **Smoothing:** mode(window=15) → min_stay_filter(7) → cột `state` (state_raw = trước smoothing)
- Code chuẩn: `vnindex_5state_ew_v1.py` Step 5–9.

## 5. Base v3.4b + DT5G overlay
`ew state` → concentration filter → US/v3.1 → bull-aware/v3.4b (`state` ở BQ `_v34b_clean`) →
`_dt_4gate` asym-commit 10/25/25 (BQ `vnindex_5state_dt_4gate`) → macro fusion (US T-1 + SBV refi+5d
+ breadth gate) → **DT5G**. Reference: `dt5g_transitions.csv` + `dt5g_daily_reference.csv`.

## 6. File trong pack (đối chiếu)
| File | Nội dung | Rows |
|---|---|---|
| `vnindex_5state_ew_eligible_universe.csv` | rổ EW từng (ngày, mã): Close/Price/Volume/tv_avg60/MA50/above_ma50/log_ret/D_CMF | 936,238 |
| `vnindex_5state_ew_daily_aggregates.csv` | ret_ew, breadth, cmf_med, close_ew, n_universe theo ngày | 3,093 |
| `vnindex_5state_ew_full.csv` | 7 factor + r_score + r_score_ema + state_raw + state | 6,291 |
| `dt5g_daily_reference.csv` | state DT5G + weight + NAV + inputs từng ngày | 6,291 |
| `dt5g_transitions.csv` | 111 transition (date, from→to, driver) | 111 |

## 7. ⚠️ CẠM BẪY căn thời gian (nguồn lệch còn lại)
1. **Ngày cuối có thể KHÔNG đủ universe:** trong BQ, dòng VNINDEX cập nhật TRƯỚC các mã thành phần.
   Vd 2026-06-02: `n_universe=1` (mã chưa load) → breadth/EW ngày đó vô nghĩa. State vẫn đúng nhờ
   smoothing, nhưng **dev pull ở thời điểm khác → n_universe ngày cuối khác → r_score ngày cuối lệch.**
   → Khuyến nghị: BỎ/không publish ngày có `n_universe < 100` (= breadth_min_universe).
2. **US căn ngày-lịch t−1** (merge_asof backward) → lag biến thiên 1–3 ngày quanh cuối tuần (đúng kinh tế).
3. **SBV refi** shift +5 phiên; ffill theo lịch ngày.
4. **Vintage:** mọi số trên = BQ 2026-06-02. Nếu BQ tiếp tục cập nhật/restate, phải pull lại CÙNG ngày
   ở cả hai phía mới đối chiếu được. ĐỪNG so reference vintage cũ với BQ pull mới.
