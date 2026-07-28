---
kind: script-output
status: DEAD
source: data/pt_v12_live_logs.csv
group: market-state
frozen_since: 2026-05-27
---

# data/pt_v12_live_logs.csv

**Status: DEAD**

## Là gì
Alt-state research variant.

## Ai ghi / cadence
KHÔNG chạy — output đóng băng từ 2026-05-27 (6+ tuần).

## Bẫy
Không phải production consumer (xác nhận: không trong crontab, không trong `papertrade_daily.sh`,
`papertrade_compare.py` ghi rõ "Removed"). Vẫn còn code SIGNAL_V11 thô — nếu hồi sinh PHẢI vá cùng
pattern trước khi chạy lại.
