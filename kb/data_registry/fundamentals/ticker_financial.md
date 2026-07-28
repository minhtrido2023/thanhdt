---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.ticker_financial
group: fundamentals
writer: Ingest theo lịch công bố BCTC (MAX_FIN_LAG=90 trong bq_freshness_check.sh)
---

# tav2_bq.ticker_financial

**Status: CANONICAL**

## Là gì
Báo cáo tài chính quý.

## Ai ghi / cadence
Ingest theo lịch công bố BCTC (~60-85 ngày lệch cho phép, `MAX_FIN_LAG=90` trong
`bq_freshness_check.sh`).

## Bẫy
OShares ở đây bị trễ quanh ex-date corp-action — xem [`../price-volume/shares_outstanding_live.md`](../price-volume/shares_outstanding_live.md).
