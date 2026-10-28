---
kind: local-file
status: CANONICAL
source: data/bdi_daily_real.csv
group: feeds
writer: fetch_bdi_daily.py, papertrade_daily.sh step [21]
---

# data/bdi_daily_real.csv

**Status: CANONICAL**

## Là gì
Baltic Dry Index daily.

## Ai ghi / cadence
`fetch_bdi_daily.py`, `papertrade_daily.sh` step [21] (mtime 07-10 ✓).

## Bẫy
—

## File bổ sung (26/10/2026)
`data/bdi_daily_te_fill.csv` (+ `_NOTES.md`): 10 ngày TE daily (`tav2_bq.commodity_prices`) mà csv này thiếu 05-05→10-23; 2 ngày lệch (07-06, 08-31) ghi ở NOTES, chưa chọn bên. **KHÔNG phải nguồn production, chưa có consumer.**
