---
kind: local-file
status: CANONICAL
source: data/macro_health.json
group: macro
role: gate — get_gated_state() chỉ trả DT5G_macro khi file này tươi
writer: macro_healthcheck.py, papertrade_daily.sh step [4], 15:30 ICT
---

# data/macro_health.json

**Status: CANONICAL (gate)**

## Là gì
Health-check các feed vĩ mô — `get_gated_state()` chỉ trả DT5G_macro khi file này tươi (<1440') và
`recommended_state_source=="DT5G_macro"`, nếu không fail-CLOSED về DT4-only.

## Ai ghi / cadence
`macro_healthcheck.py`, `papertrade_daily.sh` step [4], 15:30 ICT.

## Bẫy
File này stale = TOÀN BỘ consumer production tự rơi về DT4-only (đúng thiết kế fail-safe, nhưng dễ
nhầm là bug khi thấy state khác nhau giữa 2 máy).
