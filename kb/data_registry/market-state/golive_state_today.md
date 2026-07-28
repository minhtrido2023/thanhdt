---
kind: script-output
status: DERIVED
source: deploy_golive_dt5g_v4/golive_state_today.json
group: market-state
derived_from: tav2_bq.vnindex_5state_dt5g_live
writer: publish_gated_state.py, chạy trong bq_freshness_check.sh, cron 19:00 ICT
---

# deploy_golive_dt5g_v4/golive_state_today.json

**Status: DERIVED (từ `dt5g_live`)**

## Là gì
File publish nhanh cho DollarBill đọc.

## Ai ghi / cadence
`publish_gated_state.py`, chạy trong `bq_freshness_check.sh` cron 19:00 ICT.

## Bẫy
Field `as_of` phải khớp NGÀY HÔM NAY — nếu lệch 1 ngày, xem sự cố cron-order 2026-07-10 (đã sửa).
