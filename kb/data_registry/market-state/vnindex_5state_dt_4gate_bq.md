---
kind: bigquery-table
status: DEAD
source: tav2_bq.vnindex_5state_dt_4gate
group: market-state
frozen_since: 2026-06-02
alive_alternative: CSV local data/vnindex_5state_dt_4gate.csv
---

# tav2_bq.vnindex_5state_dt_4gate

**Status: DEAD (frozen 2026-06-02)**

## Là gì
Snapshot DT4 một lần lúc go-live DT5G.

## Ai ghi / cadence
Không ai ghi nữa (verify lastModified 06-02, 6291 rows).

## Bẫy
Xem `vnindex_5state_dt_4gate.csv` (bản local còn sống) — muốn DT4 hiện tại: đọc CSV local.
`dt5g_live` KHÔNG có cột `state_dt4` (schema kiểm 2026-11-26: time, state, state_raw, asof_date).
~20 script research cũ vẫn reference bảng này.
CHƯA dời sang `tav2_archive`: `sync_bq_cache.py` còn cấu hình đọc bảng này, phải gỡ trước.
