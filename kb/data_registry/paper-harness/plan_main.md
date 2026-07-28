---
kind: local-file
status: CANONICAL
source: data/trade_plans/plan_main_<date>.json
group: paper-harness
note: PAPER-ONLY (account main mode=paper)
writer: mike/bin/paper_main_probe_plan.py, cron 08:52 ICT
---

# data/trade_plans/plan_main_<date>.json

**Status: CANONICAL (paper probe)**

## Là gì
Probe plan cho paper `main` — evidence EXTREME gate + vol-scale chase-cap + fill-timing.

## Ai ghi / cadence
`mike/bin/paper_main_probe_plan.py`, cron 08:52 ICT.

## Bẫy
PAPER-ONLY — account `main` mode=paper; đừng lấy plan này làm mẫu cho plan live (sizing/window cố ý
khác).
