---
kind: script-output
status: DERIVED
source: data/custom30_8l_publish.csv
group: custom30
writer: cùng custom30_history.py (env CUSTOM30_CSV)
---

# data/custom30_8l_publish.csv

**Status: DERIVED**

## Là gì
Bản publish local của rổ hiện tại (env `CUSTOM30_CSV`).

## Ai ghi / cadence
Cùng script/cadence trên.

## Bẫy
Tên file mặc định là `custom30_8l_publish.csv` kể cả khi build rổ V — nhìn tên file không suy ra được
rổ nào bên trong, phải xem env của lần chạy.
