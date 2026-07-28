---
kind: local-file
status: CANONICAL
source: data/trade_plans/plan_<account>_<YYYY-MM-DD>.json
group: trading-bot
role: plan T+1 bot thực thi — tên file là CONTRACT
writer: DollarBill (dispatch 19:00 ICT chain); user duyệt trước 08:45
---

# data/trade_plans/plan_<account>_<YYYY-MM-DD>.json

**Status: CANONICAL (plan)**

## Là gì
Plan T+1 bot thực thi — tên file là CONTRACT.

## Ai ghi / cadence
DollarBill (dispatch 19:00 ICT chain) ghi; user duyệt trước 08:45.

## Bẫy
**Sự cố thật 2026-07-06**: `load_plan()` CHỈ đọc đúng tên chính tắc — file suffix `_v2`/`_superseded`
vô hình với bot. Plan duyệt lại PHẢI đè lên tên chính thức, không để dạng suffix.
`filter_excluded_tickers()` áp SAU load — generator quên exclude không sao, nhưng đổi tên file sai là
chạy nhầm plan.
