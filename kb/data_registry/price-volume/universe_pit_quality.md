---
kind: bigquery-table
status: CANONICAL
source: lithe-record-440915-m9.tav2_mike.universe_pit_quality
group: price-volume
production_since: 2026-07-22
writer: Winston — mike/bin/build_universe_pit_quality.py --date $TODAY, pipeline-1c của bq_freshness_check.sh, 19:00 ICT T2-T6
depends_on: universe_pit (đã có cho $TODAY)
---

# `lithe-record-440915-m9.tav2_mike.universe_pit_quality`

**Status: CANONICAL — PRODUCTION** (2026-07-22)

## Là gì
Subset chất lượng của `universe_pit` (qruleset_v1: trading value threshold + điều kiện quality bổ
sung); cùng append-only, 1 dòng/ticker/phiên.

## Ai ghi / cadence
**Winston**: `mike/bin/build_universe_pit_quality.py --date $TODAY`, pipeline-1c của
`bq_freshness_check.sh`, 19:00 ICT T2-T6, sau `universe_pit` build (pipeline-1b).

## Bẫy
**Consumers**: `golive_recommend_v23.py`, `custom_basket.py` (custom30V), tương lai: CAPIT breadth P4.
Build idempotent: SKIP_EXISTING → exit 0. Phụ thuộc universe_pit đã có cho $TODAY.
