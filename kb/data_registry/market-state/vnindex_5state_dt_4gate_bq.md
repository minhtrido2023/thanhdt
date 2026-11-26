---
kind: bigquery-table
status: DEAD
source: tav2_archive.vnindex_5state_dt_4gate
group: market-state
frozen_since: 2026-06-02
alive_alternative: CSV local data/vnindex_5state_dt_4gate.csv
---

# tav2_archive.vnindex_5state_dt_4gate (trước 2026-11-26: tav2_bq)

**Status: DEAD (frozen 2026-06-02)**

## Là gì
Snapshot DT4 một lần lúc go-live DT5G.

## Ai ghi / cadence
Không ai ghi nữa (verify lastModified 06-02, 6291 rows).

## Bẫy
Xem `vnindex_5state_dt_4gate.csv` (bản local còn sống) — muốn DT4 hiện tại: đọc CSV local.
`dt5g_live` KHÔNG có cột `state_dt4` (schema kiểm 2026-11-26: time, state, state_raw, asof_date).
~20 script research cũ vẫn reference bảng này.
Dời sang `tav2_archive` 2026-11-26; cùng lúc gỡ khỏi `sync_bq_cache.py` và `preflight_bq_cache.py`
(commit ngoài `edba18f1e`). `data/bq_cache/manifest.json` còn giữ mục + parquet cũ (dữ liệu đóng
băng) nên truy vấn qua `BQ_LOCAL_CACHE` vẫn trả số tới 2026-06-02; cache dựng mới từ đầu sẽ không có.
