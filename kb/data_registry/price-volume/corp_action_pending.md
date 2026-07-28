---
kind: local-file
status: VANHANH
source: data/corp_action_pending.json + data/corp_action_backlog.json
group: price-volume
writer: update_shares_live.py --scan, cron 18:40 ICT hàng ngày
---

# data/corp_action_pending.json + data/corp_action_backlog.json

**Status: Vận hành**

## Là gì
Theo dõi corp-action đã alert/chưa resolve.

## Ai ghi / cadence
`update_shares_live.py --scan`, cron 18:40 ICT hàng ngày.

## Bẫy
Đã từng có backlog 21 ngày không ai xử lý trước khi thêm heartbeat + escalate (2026-07-10).
