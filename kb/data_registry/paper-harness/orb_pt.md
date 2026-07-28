---
kind: local-file
status: CANONICAL
source: data/orb_pt_log.csv + data/orb_pt_status.json
group: paper-harness
note: nguồn dữ liệu = Vnstock/VCI API 1-phút fetch sống, KHÔNG phải BQ
writer: orb_pt.py, papertrade_daily.sh step [17]
---

# data/orb_pt_log.csv + data/orb_pt_status.json

**Status: CANONICAL (paper sleeve)**

## Là gì
ORB intraday VN30F1M paper (sleeve 1B riêng).

## Ai ghi / cadence
`orb_pt.py`, `papertrade_daily.sh` step [17] — **nguồn dữ liệu = Vnstock/VCI API 1-phút fetch sống mỗi
lần chạy, KHÔNG phải BQ**.

## Bẫy
Flaky: phụ thuộc API ngoài, từng chết 4/8 phiên không ai hay (audit Winston 07-11 → nay có FAIL-alert
cuối chain); mtime 07-08 lúc rà = đã miss phiên. Phiên chưa đóng đủ bar thì tự skip (by design).
