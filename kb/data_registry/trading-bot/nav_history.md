---
kind: local-file
status: CANONICAL
source: data/execution_logs/nav_history_<account>.csv
group: trading-bot
role: chuỗi NAV ngày — nguồn duy nhất mọi báo cáo daily/weekly/monthly
writer: daily_nav_snapshot.py trong eod_trading_report.sh, 15:00 ICT
---

# data/execution_logs/nav_history_<account>.csv

**Status: CANONICAL (NAV series)**

## Là gì
Chuỗi NAV ngày — nguồn duy nhất mọi báo cáo daily/weekly/monthly.

## Ai ghi / cadence
`daily_nav_snapshot.py` trong `eod_trading_report.sh`, 15:00 ICT.

## Bẫy
MTM cùng ngày phải dùng giá DNSE, BQ chỉ cho ngày quá khứ (sự cố 07-06 đã vá); P&L cho vị thế legacy
(ZaloPay) chưa đúng — known gap.
