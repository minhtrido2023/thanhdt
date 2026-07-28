---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.ticker / ticker_1m / ticker_prune
group: price-volume
scope: lịch sử (backtest/nghiên cứu) — TRAP nếu dùng cho dữ liệu TRONG NGÀY
writer: Ingest ETL
---

# tav2_bq.ticker / ticker_1m / ticker_prune

**Status: CANONICAL cho lịch sử**

## Là gì
OHLCV + chỉ báo, backtest/nghiên cứu.

## Ai ghi / cadence
Ingest ETL (đã xác nhận 2026-07-10: `ticker`/`ticker_prune` của HÔM NAY đã đầy đủ trước 18:45 ICT,
không cần đợi tới đêm).

## Bẫy
**TRAP nếu dùng cho dữ liệu TRONG NGÀY**: BQ cache local (`data/bq_cache`) chỉ sync 23:45 ICT — script
chạy trước giờ đó đọc cache sẽ luôn trễ 1 ngày (sự cố thật 2026-07-09, DollarBill BID/MBB lệch +5.7%).
BQ TABLE gốc (không qua cache) có thể fresh sớm hơn nhiều — đừng lẫn 2 khái niệm "BQ" và "BQ cache
local".
