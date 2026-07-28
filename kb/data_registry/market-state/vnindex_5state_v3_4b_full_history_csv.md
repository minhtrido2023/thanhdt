---
kind: local-file
status: CANONICAL
source: data/vnindex_5state_tam_quan_v3_4b_full_history.csv
group: market-state
aka: CSV local base — input build_dt_4gate.py + ~30 script research
writer: daily_refresh_v34b_linux.sh step [7] + cp root→data/ 18:30 ICT
---

# data/vnindex_5state_tam_quan_v3_4b_full_history.csv

**Status: CANONICAL (local base)**

## Là gì
Bản CSV local của v3.4b base — input cho `build_dt_4gate.py` + ~30 script research.

## Ai ghi / cadence
`daily_refresh_v34b_linux.sh` step [7] + cp root→`data/` 18:30 ICT (mirror fix 2026-07-10, audit
Winston_20260710_173031).

## Bẫy
Trước 07-10 bản `data/` đóng băng 06-30 trong khi bản root tươi — nếu thấy 2 bản lệch nhau, bản root
là bản build, `data/` phải được cp theo.
