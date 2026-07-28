---
kind: bigquery-table
status: CANONICAL
source: lithe-record-440915-m9.tav2_mike.universe_pit
group: price-volume
production_since: 2026-07-22
writer: Winston — mike/bin/build_universe_pit.py --date $TODAY, pipeline-1b của bq_freshness_check.sh, 19:00 ICT T2-T6
---

# `lithe-record-440915-m9.tav2_mike.universe_pit`

**Status: CANONICAL — PRODUCTION** (2026-07-22)

## Là gì
Universe point-in-time append-only: bảng do đội Mike sở hữu, 1 dòng/ticker/phiên, `in_universe`
flag; tính CHỈ từ cột thô `tav2_bq.ticker` (KHÔNG đọc `ticker_prune`). Dataset `tav2_mike` RIÊNG
(tránh `WRITE_TRUNCATE` từ bq_admin).

## Ai ghi / cadence
**Winston**: `mike/bin/build_universe_pit.py --date $TODAY`, pipeline-1b của `bq_freshness_check.sh`,
19:00 ICT T2-T6, sau ticker FRESH BLOCK.

## Bẫy
**Consumers**: `golive_recommend_v23.py` (panel D1), `custom_basket.py` (custom30V) —
assert_universe_covers() sẽ crash nếu thiếu phiên hôm nay. Build idempotent: B8_DUPLICATE nếu đã có →
exit 1 (nhưng pipeline-1b wrapper check BQ count để phân biệt với fail thật). Script đọc BQ LIVE,
KHÔNG qua `BQ_LOCAL_CACHE`.
