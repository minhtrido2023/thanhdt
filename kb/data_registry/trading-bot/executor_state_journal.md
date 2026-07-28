---
kind: local-file
status: CANONICAL
source: data/execution_logs/exec_<label>_<date>_state.json / _journal.csv
group: trading-bot
role: state + journal executor per account/ngày
writer: trading_bot/executor.py, liên tục trong phiên
---

# data/execution_logs/exec_<label>_<date>_state.json / _journal.csv

**Status: CANONICAL (bot state)**

## Là gì
State + journal executor per account/ngày (idempotency guard `_ghost_tickers`, atomic write).

## Ai ghi / cadence
`trading_bot/executor.py`, liên tục trong phiên.

## Bẫy
Ghost-pause cần unpause THỦ CÔNG (by design); selfcheck driving Executor phải dùng TAG account riêng +
dọn fixture cũ (guidelines §7).
