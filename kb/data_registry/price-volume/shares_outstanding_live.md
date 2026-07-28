---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.shares_outstanding_live
group: price-volume
role: override ticker_financial.OShares (quý, trễ ~3 tháng)
writer: update_shares_live.py --ticker/--ack-cash, do Winston chạy tay sau khi phân loại
---

# tav2_bq.shares_outstanding_live

**Status: CANONICAL (override)**

## Là gì
Số cổ phiếu lưu hành đã điều chỉnh corp-action, override `ticker_financial.OShares` (quý, có thể trễ
~3 tháng).

## Ai ghi / cadence
`update_shares_live.py --ticker`/`--ack-cash`, do Winston chạy tay sau khi phân loại.

## Bẫy
Chỉ có hiệu lực nếu consumer JOIN đúng cú pháp (xem template cuối `update_shares_live.py`) — không
JOIN thì vẫn dùng OShares quý cũ.
