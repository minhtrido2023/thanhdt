---
kind: local-file
status: CANONICAL
source: data/earnings_px.pkl, data/lagged_pos_ov.pkl, data/earnings_surprise_data.pkl, data/earnings_events_classified.csv
group: lag-book
note: 4 cache LAG-leg mà pt_v22/pt_v4/mọi V12 sim phụ thuộc
writer: refresh_lagged_caches.py, papertrade_daily.sh step [2], 15:30 ICT (cả 4 file, qua BQ_LOCAL_CACHE = cache đêm trước) + refresh_earnings_surprise_pkl.py, bq_freshness_check.sh pipeline-1d, 19:00 ICT (CHỈ earnings_surprise_data.pkl, BQ sống)
---

# data/earnings_px.pkl, data/lagged_pos_ov.pkl, data/earnings_surprise_data.pkl, data/earnings_events_classified.csv

**Status: CANONICAL (LAG caches)**

## Là gì
4 cache LAG-leg (giá daily, Open+Volume, NP quý, events phân loại) mà pt_v22/pt_v4/mọi V12 sim phụ
thuộc.

## Ai ghi / cadence
`refresh_lagged_caches.py`, `papertrade_daily.sh` step [2], 15:30 ICT (mtime 07-10 ✓).

**Từ 2026-10-13 `earnings_surprise_data.pkl` có writer THỨ HAI**: `refresh_earnings_surprise_pkl.py`,
bước `[pipeline-1d]` của `bq_freshness_check.sh` (19:00 ICT, ngay trước `golive_recommend_v23`) — cùng
SQL với bước [3] ở trên nhưng đọc **BQ SỐNG**, ghi nguyên tử (tmp + `os.replace`), WARN-only (hỏng thì
giữ bản 15:30). 3 file còn lại vẫn chỉ có writer 15:30.

## Bẫy
(1) Pickle ghi bằng pandas 3 — PHẢI đọc bằng `$DNA_PYEXE`, system python3/pandas 2.3 raise
`NotImplementedError` (guidelines §8); (2) `pt_dates.detect_end_date()` cap END_DATE theo max time của
`lagged_pos_ov.pkl` → file này stale = MỌI paper sim lặng lẽ đóng băng ngày cuối (đây chính là lý do
sinh ra refresh step). (3) **Bản 15:30 KHÔNG phải BQ sống**: `papertrade_daily.sh` source `wc_env.sh` ⇒
`BQ_LOCAL_CACHE` bật ⇒ `refresh_lagged_caches.py` đọc cache DuckDB sync 23:45 ĐÊM TRƯỚC (đo 2026-10-13:
pkl 15:30 = 58.233 dòng, max Release_Date 08-21 = y hệt `data/bq_cache/ticker_financial.parquet`; BQ sống
đã có KBC 2026Q3). BCTC ingest ngày D chỉ vào pkl 15:30 ngày D+1 — đó là lý do có writer 19:00. Ai đọc
`earnings_surprise_data.pkl` giữa 15:30 và 19:00 vẫn thấy dữ liệu T-1. (4) Writer 15:30 ghi thẳng
(`open(path,'wb')`, KHÔNG nguyên tử) — bị kill giữa chừng có thể để lại pkl hỏng; writer 19:00 thì không.
