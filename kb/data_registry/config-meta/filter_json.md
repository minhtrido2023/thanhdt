---
kind: config
status: CANONICAL
source: filter.json
group: config-meta
role: source of truth mọi buy/sell filter
writer: con người khi đổi chiến lược; gen_sql.py convert → sql_queries/*.sql
---

# filter.json

**Status: CANONICAL (source of truth)**

## Là gì
Định nghĩa mọi buy/sell filter (`_Strategy`/`~Signal`/`$Strategy`/`Init`/MARKET_DICT_FILTER).

## Ai ghi / cadence
Con người khi đổi chiến lược; `gen_sql.py` convert → `sql_queries/*.sql`.

## Bẫy
Sửa filter.json mà quên chạy lại gen_sql = SQL cũ vẫn được dùng.
