---
kind: script-output
status: DERIVED
source: sql_queries/*.csv
group: config-meta
writer: bash script sinh từ gen_sql
---

# sql_queries/*.csv

**Status: DERIVED (cache kết quả)**

## Là gì
Kết quả query lần chạy cuối.

## Ai ghi / cadence
Bash script sinh từ gen_sql.

## Bẫy
Là cache — không có timestamp guarantee, đừng dùng làm dữ liệu "hiện tại".
