---
kind: script-output
status: DERIVED
source: golive_v23_recommendations_<date>.csv
group: market-state
writer: golive_recommend_v23.py (đọc dt5g_live)
---

# golive_v23_recommendations_<date>.csv

**Status: DERIVED**

## Là gì
Khuyến nghị BAL/LAG hàng ngày.

## Ai ghi / cadence
`golive_recommend_v23.py`, đọc `dt5g_live` (đã fix 2026-07-11, trước đó đọc nhầm base).

## Bẫy
Kiểm tra `state_source` field = `DT5G_macro`, không phải suy đoán.
