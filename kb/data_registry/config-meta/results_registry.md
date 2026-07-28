---
kind: local-file
status: CANONICAL
source: data/results_registry.md
group: config-meta
role: pinned baselines (số tham chiếu chính thức mọi backtest)
writer: Taylor, sau mỗi lần pin/re-pin
---

# data/results_registry.md

**Status: CANONICAL (pinned baselines)**

## Là gì
Số tham chiếu chính thức mọi backtest (R3 mới nhất: 28.82%/1.90/−15.7%/1.83, re-pin dt5g 2026-07-11
commit 09724bc).

## Ai ghi / cadence
Taylor, sau mỗi lần pin/re-pin.

## Bẫy
Filename CSV canonical là artifact read-only — experiment PHẢI đổi tên output (guidelines §8, sự cố
overwrite 07-06); regenerate phải dùng đúng lệnh pin + `$DNA_PYEXE`.
