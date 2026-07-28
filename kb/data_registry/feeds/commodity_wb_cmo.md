---
kind: local-file
status: CANONICAL
source: data/<commodity>_monthly.csv (6 file WB CMO)
group: feeds
cadence: THÁNG
writer: auto_update_commodity_wb.sh, cron ngày 5 + 10 hàng tháng 08:00 ICT (atomic + .bak)
---

# data/<commodity>_monthly.csv (6 file WB CMO)

**Status: CANONICAL**

## Là gì
Giá hàng hóa tháng (World Bank CMO).

## Ai ghi / cadence
`auto_update_commodity_wb.sh`, cron ngày 5 + 10 hàng tháng 08:00 ICT (atomic + .bak).

## Bẫy
Cadence THÁNG, 2 attempt vì WB publish trễ — đừng báo stale giữa tháng.
