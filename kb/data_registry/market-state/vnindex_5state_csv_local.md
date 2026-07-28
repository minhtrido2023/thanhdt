---
kind: local-file
status: TRAP
source: data/vnindex_5state.csv
group: market-state
aka: twin local của trap tav2_bq.vnindex_5state — base + STALE
frozen_since: 2026-05-21
---

# data/vnindex_5state.csv

**Status: TRAP (local, frozen)**

## Là gì
Bản CSV local cùng tên bảng trap BQ, đóng băng 2026-05-21.

## Ai ghi / cadence
Không ai ghi (mtime 05-21).

## Bẫy
Twin local của trap `tav2_bq.vnindex_5state`: vừa là BASE (không phải DT5G) vừa STALE. ~29 script
research cũ đọc — kết quả sai kép nếu tưởng là state production hiện tại.
