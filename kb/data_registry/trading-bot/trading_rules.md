---
kind: config
status: CANONICAL
source: data/trading_rules.json
group: trading-bot
role: rules — Mafee chặn lệnh, DollarBill lập plan
writer: Taylor đề xuất, user duyệt mới áp live (mtime 07-03 = v2.1)
---

# data/trading_rules.json

**Status: CANONICAL (rules)**

## Là gì
Hạn mức/rule giao dịch — Mafee đọc để CHẶN lệnh, DollarBill đọc để lập plan (neutral_parking 0.70,
risk_dial_override…).

## Ai ghi / cadence
Taylor đề xuất, **user duyệt** mới áp live (mtime 07-03 = v2.1).

## Bẫy
Sửa giữa phiên KHÔNG có hiệu lực tới lần load kế tiếp của bot (bot_execute đọc lúc start).
