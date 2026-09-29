---
kind: local-file
status: DERIVED
source: data/bq_cache/*.parquet (11 bảng)
group: bq-cache
note: mirror local threads=1 (~100ms vs 5-15s BQ)
writer: sync_bq_cache.py qua sync_bq_cache_daily.sh, cron 23:45 ICT
tables: ticker, ticker_prune, ticker_financial, ticker_1m, vnindex_5state_dt5g_live, vnindex_5state, vnindex_5state_tam_quan_v34b_clean, vnindex_5state_dt_4gate, fa_ratings, fa_ratings_8l, custom30v_8l
---

# `data/bq_cache/*.parquet` (11 bảng: `ticker`, `ticker_prune`, `ticker_financial`, `ticker_1m`, `vnindex_5state_dt5g_live`, `vnindex_5state`, `vnindex_5state_tam_quan_v34b_clean`, `vnindex_5state_dt_4gate`, `fa_ratings`, `fa_ratings_8l`, `custom30v_8l`)

**Status: DERIVED (mirror)**

## Là gì
Cache local threads=1 (~100ms vs 5-15s BQ) cho backtest/sim.

## Ai ghi / cadence
`sync_bq_cache.py` qua `sync_bq_cache_daily.sh`, cron 23:45 ICT.

## Bẫy
3 bẫy: (1) trễ 1 ngày cho mọi script chạy trước 23:45 (sự cố 2026-07-09); (2) **cache mirror CẢ bảng
trap y nguyên tên** — `bq_cache/vnindex_5state.parquet` = v3.4b BASE chứ không phải DT5G, đọc cache
không cứu khỏi đọc nhầm bảng; (3) cache mirror cả bảng FROZEN (`vnindex_5state_dt_4gate` chết 06-02) —
mtime parquet là hôm qua nhưng DATA bên trong đứng yên từ nguồn (`fa_ratings` từng thuộc nhóm này, hết
frozen từ 2026-07-12 khi refresh weekly sống lại). Riêng `fa_ratings`/`fa_ratings_8l`: nguồn refresh
kiểu DELETE+INSERT/re-rank → sync chuyển sang `full_only` (full re-download mỗi đêm kể cả `--delta`,
job Winston_20260713_103213) — delta-append cũ không vớt được row bị rewrite, gây count-mismatch giả
mỗi thứ Bảy. Từng có bug sync `ticker` chết âm thầm ~06-26 (chunk parquet cũ) — đã fix; (4)
**`ticker`/`ticker_prune` là THƯ MỤC chunked theo năm** (`data/bq_cache/ticker_prune/<year>.parquet`,
đọc bằng glob `ticker_prune/*.parquet`) từ 2026-06-26 — file monolith cũ `ticker_prune.parquet` KHÔNG
được sync nữa, đóng băng 06-26, user phát hiện stale 07-13; đã archive sang
`data/archive/ticker_prune_monolith_frozen_20260626.parquet` + sửa hết 28 file .py từng đọc nhầm (27
script research/screen + `trading_bot/executor.py:507`) sang chunked (job Winston_20260713_143546).
Đường dẫn đúng DUY NHẤT giờ là thư mục chunked.

Bẫy (5) — **`ticker.MA200` NULL cho phần lớn mã giai đoạn 2015-2017** (phát hiện 2026-09-27, job
`Taylor_20260927_022338`). Kiểm kê thật trên cache: số mã có `MA200 IS NULL` mỗi phiên, median theo
năm — 2015: **10**, **2016: 137**, 2017: **23**, 2018: 22, 2019: 11, 2021: 15, các năm còn lại ≤8. Ca cực trị
**2016-07-13: 199/296 mã** trong `universe_pit` có `MA200` NULL.
**Hệ quả cụ thể:** mọi phép `%mã Close>MA200` (breadth, quy ước trục-2 conditional của
`kb/canonical.md`) tính từ cache mà đếm cả dòng NULL vào MẪU SỐ sẽ ra breadth **0,243 thay vì
0,730** cùng phiên đó — `corr` với chuỗi gốc 0,934, **max|Δ| 0,487**, và nhãn tercile lệch hẳn sang
LOW suốt 2015-2017. Thêm `MA200 IS NOT NULL AND MA200 > 0` vào mẫu số → **corr 0,999954,
mean|Δ| 0,000585** so với `research/strategy_regime_matrix_20260822/b2_breadth.csv` (chuỗi dựng từ
BQ live, 3.402 phiên chồng lấn).
**Vì sao dễ lọt:** `Close > NULL` trả NULL/False im lặng — tử số đúng, chỉ mẫu số sai, nên chuỗi
kết quả vẫn nằm trong [0,1] và vẫn biến thiên "trông hợp lý". Không có lỗi, không có cảnh báo.
Thứ duy nhất bắt được là **so chuỗi tự dựng với một chuỗi gốc đã pin** (self-check kiểu §28: chuẩn
hoá GIÁ TRỊ rồi so, không suy từ sự vắng mặt của lỗi).
**Chưa xác minh:** NULL này là khuyết của cache hay có thật ở `tav2_bq.ticker` — cần Winston đối
chiếu BQ live trước khi kết luận. Dù nguồn nào thì luật dùng vẫn vậy: **lọc mẫu số.**

**Xác minh 2026-09-27 (data-ops) — kết luận: CÓ THẬT Ở NGUỒN `tav2_bq.ticker`, KHÔNG phải khuyết của cache.**
Đếm cùng một phép trên 2 nguồn: mẫu số = `tav2_mike.universe_pit` `in_universe=TRUE` cùng ngày
(ruleset_version=1 duy nhất 2014-2019), LEFT JOIN `ticker` theo `(time, ticker)`; median theo phiên
của số mã có dòng nhưng `MA200 IS NULL`; cột `norow` = mã universe không có dòng `ticker` hôm đó.

| Nhóm | BQ live: med NULL / max / med univ | Cache parquet: med NULL / max / med univ | norow (cả 2) |
|---|---|---|---|
| 2014 | 2 / 6 / 229 | 2 / 6 / 229 | 0 |
| 2015 | 10 / 135 / 249 | 10 / 137 / 249 | 0 |
| 2016 | **135** / 195 / 288 | **137** / 199 / 288 | 0 |
| 2017 | 26 / 67 / 304 | 23 / 55 / 304,5 | 0 |
| 2018 | 22 / 30 / 300 | 22 / 30 / 300,5 | 0 |
| 2019 | 11 / 19 / 277 | 11 / 19 / 277 | 0 |
| **2016-07-13** | **195 / 296** | **199 / 296** | 0 |

Hai nguồn khớp trong phạm vi ≤4 mã/phiên. Phần dư 2016-07-13 đo theo tên: cache NULL thêm đúng 4 mã
{DHG, DMC, PHR, PVS} mà BQ live hiện ĐÃ có `MA200`; chiều ngược lại (BQ NULL, cache có) = rỗng ⇒ cache
2016.parquet hơi cũ hơn BQ cho 4 mã đó, không phải cache tự sinh NULL. Median BQ dùng
`APPROX_QUANTILES` (2016: 135 vs cache 137 exact) — sai số cùng bậc với phần dư trên. Dry-run 44 MB.
Luật dùng giữ nguyên: **lọc `MA200 IS NOT NULL` khỏi mẫu số, ở CẢ BQ live lẫn cache.**

Lệnh đã dùng (`source wc_env.sh` trước):
```sql
-- bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv "$(cat ma200_null_bq.sql)"
WITH u AS (
  SELECT time, ticker FROM `lithe-record-440915-m9.tav2_mike.universe_pit`
  WHERE in_universe = TRUE AND time BETWEEN '2014-01-01' AND '2019-12-31' GROUP BY time, ticker),
d AS (
  SELECT u.time, COUNT(DISTINCT u.ticker) AS n_univ,
    COUNT(DISTINCT IF(t.ticker IS NULL, u.ticker, NULL)) AS n_norow,
    COUNT(DISTINCT IF(t.ticker IS NOT NULL AND t.MA200 IS NULL, u.ticker, NULL)) AS n_null_ma200
  FROM u LEFT JOIN `lithe-record-440915-m9.tav2_bq.ticker` t
    ON t.time = u.time AND t.ticker = u.ticker AND t.time BETWEEN '2014-01-01' AND '2019-12-31'
  GROUP BY u.time)
SELECT CAST(EXTRACT(YEAR FROM time) AS STRING) AS grp, COUNT(*) AS n_days,
  APPROX_QUANTILES(n_null_ma200, 100)[OFFSET(50)] AS med_null_ma200,
  APPROX_QUANTILES(n_norow, 100)[OFFSET(50)] AS med_norow,
  APPROX_QUANTILES(n_univ, 100)[OFFSET(50)] AS med_univ, MAX(n_null_ma200) AS max_null_ma200
FROM d GROUP BY grp
UNION ALL SELECT '2016-07-13', 1, n_null_ma200, n_norow, n_univ, n_null_ma200 FROM d WHERE time = '2016-07-13'
ORDER BY grp
```
Cache: cùng bộ lọc trên `data/bq_cache/universe_pit_q/{2014..2019}.parquet` (`in_universe`) ⋈
`data/bq_cache/ticker/{2014..2019}.parquet`, pandas median exact.
