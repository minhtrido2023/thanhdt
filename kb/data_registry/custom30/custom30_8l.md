---
kind: bigquery-table
status: TRAP
source: tav2_bq.custom30_8l
group: custom30
note: legacy blend, vẫn tươi hàng ngày — "tươi" ≠ "đúng rổ"
writer: custom30_history.py default env, step [6] daily 15:30
---

# tav2_bq.custom30_8l

**Status: TRAP (legacy blend, vẫn tươi hàng ngày)**

## Là gì
Rổ blend liquidity-led — spec live TRƯỚC 2026-06-30, nay chỉ giữ cho audit ([6] default env của cùng
script).

## Ai ghi / cadence
`custom30_history.py` default env, step [6] daily 15:30 (lastModified 07-10 — bảng SỐNG).

## Bẫy
**Đã gây bug mislabel thật**: `golive_recommend_v23.py` đọc nhầm bảng này tới 2026-07-11 trong khi
advisory ghi "custom30V" (fix cùng ngày). Bẫy kép: bảng tươi hàng ngày nên nhìn freshness không phát
hiện được — "tươi" ≠ "đúng rổ". Code mới phải dùng `custom30.TABLE_V`, không hardcode tên.
