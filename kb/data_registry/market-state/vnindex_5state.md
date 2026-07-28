---
kind: bigquery-table
status: TRAP
source: tav2_bq.vnindex_5state
group: market-state
aka: v3.4b BASE thô — KHÔNG PHẢI DT5G
byte_identical_to: tav2_bq.vnindex_5state_tam_quan_v34b_clean
writer: daily_refresh_v34b_linux.sh (cùng cron 18:30, bước load bare)
---

# tav2_bq.vnindex_5state

**Status: TRAP**

## Là gì
v3.4b BASE thô (không DT-gate, không macro-cap, ~153 transitions) — **KHÔNG PHẢI DT5G**.

## Ai ghi / cadence
`daily_refresh_v34b_linux.sh` (cùng cron, bước load bare).

## Bẫy
**Đã gây sự cố thật 2 lần**: (1) 2026-07 EW-leg reorg bug tạo BULL giả; (2) 2026-07-11 phát hiện
`SIGNAL_V11.sql` + 4 script production (`golive_recommend_v23.py`, `pt_v4_dt5g.py`,
`pt_v22_dt5g.py`, `pt_v23_audit_2014.py`) đọc nhầm bảng này — sổ `pt_v22` vào 6 mã theo BULL giả.
Byte-identical với `vnindex_5state_tam_quan_v34b_clean`.
