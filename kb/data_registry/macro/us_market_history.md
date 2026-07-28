---
kind: local-file
status: CANONICAL
source: us_market_history.csv (VIX/SPX)
group: macro
role: input Pillar B (macro gate DT5G)
writer: pull_us_market.py, chạy trong daily_refresh_v34b_linux.sh bước [2]
---

# `us_market_history.csv` (VIX/SPX)

**Status: CANONICAL**

## Là gì
Input Pillar B (macro gate DT5G).

## Ai ghi / cadence
`pull_us_market.py`, chạy trong `daily_refresh_v34b_linux.sh` bước [2].

## Bẫy
Lag theo thiết kế (aligned T-1), không phải bug.
