---
kind: local-file
status: CANONICAL
source: data/execution_logs/exec_main_*
group: paper-harness
note: paper evidence — go-live sign-off input
writer: bot_execute.py --account main, cron 09:10/10:46/13:05 ICT
---

# data/execution_logs/exec_main_*

**Status: CANONICAL (paper evidence)**

## Là gì
State/journal PaperBroker của `main` — dữ liệu gốc cho `execution_quality_review.py` + điều kiện
go-live 3 patch.

## Ai ghi / cadence
`bot_execute.py --account main`, cron 09:10/10:46/13:05 ICT.

## Bẫy
Evidence tích theo PHIÊN THẬT — ngày bot main không chạy (early_check alert) = lỗ hổng evidence, kéo
dài lịch sign-off.
