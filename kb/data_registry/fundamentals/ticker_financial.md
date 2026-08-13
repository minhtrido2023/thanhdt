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
`OShares` ở đây **vừa trễ quanh ex-date, vừa bị RESTATE về sau** (2.667 dòng/576 mã mang số của
một AIS có hiệu lực SAU đó, tới 2.693 ngày) ⇒ đọc thẳng là look-ahead. Cột này có file riêng,
status **TRAP**: [`ticker_financial_oshares.md`](ticker_financial_oshares.md). Xem thêm
[`../price-volume/shares_outstanding_live.md`](../price-volume/shares_outstanding_live.md).
