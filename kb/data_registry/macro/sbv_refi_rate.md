---
kind: config
status: CANONICAL
source: SBV refi-rate (sbv_macro_overlay)
group: macro
role: input Pillar A (macro gate DT5G)
writer: check_sbv_weekly.sh, cron thứ Sáu 15:00 ICT
---

# SBV refi-rate (`sbv_macro_overlay`)

**Status: CANONICAL**

## Là gì
Input Pillar A (macro gate DT5G).

## Ai ghi / cadence
`check_sbv_weekly.sh`, cron thứ Sáu 15:00 ICT.

## Bẫy
`fetch_status: fetch_failed` từng xảy ra (2026-07-10), tự fallback "assumed unchanged" — kiểm tra
field này khi audit.
