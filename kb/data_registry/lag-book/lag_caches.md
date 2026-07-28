---
kind: local-file
status: CANONICAL
source: data/earnings_px.pkl, data/lagged_pos_ov.pkl, data/earnings_surprise_data.pkl, data/earnings_events_classified.csv
group: lag-book
note: 4 cache LAG-leg mà pt_v22/pt_v4/mọi V12 sim phụ thuộc
writer: refresh_lagged_caches.py, papertrade_daily.sh step [2], 15:30 ICT
---

# data/earnings_px.pkl, data/lagged_pos_ov.pkl, data/earnings_surprise_data.pkl, data/earnings_events_classified.csv

**Status: CANONICAL (LAG caches)**

## Là gì
4 cache LAG-leg (giá daily, Open+Volume, NP quý, events phân loại) mà pt_v22/pt_v4/mọi V12 sim phụ
thuộc.

## Ai ghi / cadence
`refresh_lagged_caches.py`, `papertrade_daily.sh` step [2], 15:30 ICT (mtime 07-10 ✓).

## Bẫy
(1) Pickle ghi bằng pandas 3 — PHẢI đọc bằng `$DNA_PYEXE`, system python3/pandas 2.3 raise
`NotImplementedError` (guidelines §8); (2) `pt_dates.detect_end_date()` cap END_DATE theo max time của
`lagged_pos_ov.pkl` → file này stale = MỌI paper sim lặng lẽ đóng băng ngày cuối (đây chính là lý do
sinh ra refresh step).
