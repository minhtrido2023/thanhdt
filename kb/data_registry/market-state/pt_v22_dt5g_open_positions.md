---
kind: script-output
status: DERIVED
source: data/pt_v22_dt5g_open_positions.csv
group: market-state
role: money-path (sổ vị thế production)
writer: pt_v22_dt5g.py, cron papertrade_daily.sh 15:30 ICT
---

# data/pt_v22_dt5g_open_positions.csv

**Status: DERIVED**

## Là gì
Sổ vị thế production (`trading_bot/strategies.py` đọc để build plan sống SpaceX/ZaloPay).

## Ai ghi / cadence
`pt_v22_dt5g.py`, cron `papertrade_daily.sh` 15:30 ICT.

## Bẫy
Money-path THẬT — bug ở đây ảnh hưởng lệnh thật. Đã fix 2026-07-11 (commit 0537514/9149c0f), có
selfcheck riêng (`money_path_freshness_selfcheck.py` section F, 29/29 PASS).

> (Cross-ref: sổ vị thế production này cũng được nhắc ở cuối registry cũ — nay là 1 file duy nhất.)
