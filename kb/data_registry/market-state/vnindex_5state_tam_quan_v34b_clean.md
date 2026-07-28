---
kind: bigquery-table
status: DERIVED
source: tav2_bq.vnindex_5state_tam_quan_v34b_clean
group: market-state
aka: bản sync v3.4b base (== bare vnindex_5state)
writer: daily_refresh_v34b_linux.sh, cùng cron 18:30, bước "SYNCS _v34b_clean"
---

# tav2_bq.vnindex_5state_tam_quan_v34b_clean

**Status: DERIVED**

## Là gì
Bản sync của v3.4b base (== bare `vnindex_5state`).

## Ai ghi / cadence
Cùng cron 18:30, bước "SYNCS _v34b_clean".

## Bẫy
Là INPUT cho DT-gate tính `dt5g_live` — đọc để audit base, không phải để lấy state production.
