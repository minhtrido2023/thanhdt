---
kind: local-file
status: CANONICAL
source: data/execution_logs/dnse_raw_<date>.jsonl
group: trading-bot
role: broker raw, authoritative — nguồn CHUẨN cost-basis
writer: trading_bot/brokers.py ghi mỗi call, trong phiên
---

# data/execution_logs/dnse_raw_<date>.jsonl

**Status: CANONICAL (broker raw, authoritative)**

## Là gì
Log thô mọi call DNSE — nguồn CHUẨN cho fill price (`averagePrice`/`fillQuantity`), balances, đối
soát.

## Ai ghi / cadence
`trading_bot/brokers.py` ghi mỗi call, trong phiên.

## Bẫy
File DÙNG CHUNG mọi account theo ngày — mỗi bản ghi phải lọc theo `account_no`/`label` (bug NAV lẫn
account 2026-07-06 đã vá). Đây là nguồn duy nhất được phép làm cost-basis cho report (guidelines §6).
