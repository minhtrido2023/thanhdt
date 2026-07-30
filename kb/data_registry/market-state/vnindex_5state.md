---
kind: bigquery-table
status: TRAP
source: tav2_bq.vnindex_5state
group: market-state
aka: v3.4b BASE thô — KHÔNG PHẢI DT5G
byte_identical_to: tav2_bq.vnindex_5state_tam_quan_v34b_clean
writer: daily_refresh_v34b_linux.sh step [10] → state_publish_immutable.py (cron 18:30)
write_contract: APPEND-ONLY + recompute đuôi 25 phiên (BẤT BIẾN, từ 2026-07-30)
columns: time, state, state_raw, asof_date
---

# tav2_bq.vnindex_5state

**Status: TRAP**

## Là gì
v3.4b BASE thô (không DT-gate, không macro-cap, ~153 transitions) — **KHÔNG PHẢI DT5G**.

## Ai ghi / cadence
`daily_refresh_v34b_linux.sh` step [10] → `state_publish_immutable.py` (cron 18:30). Trước
2026-07-30 là `bq load --replace` (đè toàn bộ mỗi đêm).

## HỢP ĐỒNG GHI — BẤT BIẾN (từ 2026-07-30, job `Taylor_20260730_013951`)
Giống hệt `dt5g_live` — xem [vnindex_5state_dt5g_live.md](vnindex_5state_dt5g_live.md) mục cùng
tên: append phiên mới + recompute đuôi 25 phiên giao dịch, phần đã chốt bất khả xâm phạm, cột
`asof_date` (backfill `2026-07-30` = baseline đóng băng). Bảng này là bảng bị viết lại **134
phiên** ngày 2026-07-29.
Vì bảng này là nguồn của `_v34b_clean` (step [11] `CREATE OR REPLACE ... SELECT *`), tính bất
biến LAN sang `_v34b_clean` ⇒ input base của DT5G cũng đã chốt.

## Bẫy
**Đã gây sự cố thật 2 lần**: (1) 2026-07 EW-leg reorg bug tạo BULL giả; (2) 2026-07-11 phát hiện
`SIGNAL_V11.sql` + 4 script production (`golive_recommend_v23.py`, `pt_v4_dt5g.py`,
`pt_v22_dt5g.py`, `pt_v23_audit_2014.py`) đọc nhầm bảng này — sổ `pt_v22` vào 6 mã theo BULL giả.
Byte-identical với `vnindex_5state_tam_quan_v34b_clean`.
