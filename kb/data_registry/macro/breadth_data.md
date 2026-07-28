---
kind: local-file
status: DEAD
source: data/breadth_data.csv
group: macro
frozen_since: 2026-05-26
---

# data/breadth_data.csv

**Status: DEAD (research, frozen 2026-05-26)**

## Là gì
Snapshot breadth cho nghiên cứu cũ.

## Ai ghi / cadence
Không ai ghi.

## Bẫy
Breadth-decoupling guard PRODUCTION **không** đọc file này — `macro_state_live.py` query thẳng
`ticker_prune` (causal T-1). Đừng "fix freshness" file này cho production.
