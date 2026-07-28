---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.vnindex_5state_dt5g_live
group: market-state
aka: DT5G production
writer: macro_state_live.py → daily_refresh_v34b_linux.sh, cron 18:30 ICT
---

# tav2_bq.vnindex_5state_dt5g_live

**Status: CANONICAL**

## Là gì
Trạng thái thị trường PRODUCTION (DT-gate + macro gate, 49 transitions).

## Ai ghi / cadence
`macro_state_live.py` → `daily_refresh_v34b_linux.sh` cron 18:30 ICT (dời từ 23:15, 2026-07-10).

## Bẫy
Không có, đây là nguồn ĐÚNG duy nhất cho production.
