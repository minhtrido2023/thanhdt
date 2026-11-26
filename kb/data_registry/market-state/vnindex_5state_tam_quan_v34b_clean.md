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

## Bất biến kế thừa (2026-07-30)
Step [11] là `CREATE OR REPLACE ... AS SELECT time, state, state_raw FROM vnindex_5state`, và
`vnindex_5state` publish BẤT BIẾN ⇒ bảng này kế thừa tính bất biến (lịch sử đã chốt không còn bị
viết lại). Bảng chỉ có 3 cột, KHÔNG có `asof_date`.

## Mô tả bảng trên BQ (2026-11-26)
Vì bảng được tạo lại mỗi đêm, description nằm trong `OPTIONS(...)` của chính câu lệnh step [11]
(`daily_refresh_v34b_linux.sh`); sửa bằng `bq update` sẽ mất ở lượt chạy sau.
