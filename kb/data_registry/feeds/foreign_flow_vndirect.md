---
kind: external-api
status: CANDIDATE-FEASIBLE
source: Khối ngoại (foreign flow) — VNDirect finfo
group: feeds
note: chưa wire, chưa có consumer — nguồn foreign-flow tốt nhất đã test
tested: 2026-07-23 (job Winston_20260723_080716)
---

# Khối ngoại (foreign flow) — VNDirect finfo

**Status: CANDIDATE-FEASIBLE ✅** (chưa wire, chưa có consumer)

## Là gì
API JSON công khai `https://api-finfo.vndirect.com.vn/v4/foreigns` — foreign net buy/sell theo NGÀY.
Query `?q=code:VNM~tradingDate:gte:2019-01-01&sort=tradingDate:asc&size=N` (header `Referer:
https://dstock.vndirect.com.vn/`). Fields: `buyVal/sellVal/netVal/buyVol/sellVol/netVol/totalRoom/
currentRoom`. **INDEX-level** (`code:VNINDEX`/`VN30`, type=INDEX) cho net toàn thị trường; **per-stock**
(type=STOCK); **PHÁI SINH** (`code:VN30Fyymm`, type=FU, floor=HNX — net vol foreign trên từng hợp
đồng, stitch front-month để có chuỗi liên tục).

## Ai ghi / cadence
KHÔNG cần auth.

## Bẫy
**Độ sâu chỉ từ 2018-08-30** (VNM per-stock 1971 rows, VNINDEX index 1966 rows) — KHÔNG có trước 2018
(BQ `ticker` tới 2000 nhưng foreign chỉ ~8 năm ở nguồn này). Test THẬT xác nhận 2026-07-23 (job
`Winston_20260723_080716`): window nghiên cứu 2026-05-18 peak có đủ (VNINDEX net −617bn ngày đó).
Endpoint dùng Elasticsearch — field ngày là `tradingDate` KHÔNG phải `date` (dùng `date` → HTTP 500
"all shards failed", KHÔNG phải lỗi auth). Là API bên thứ 3 không hợp đồng — có thể đổi/chặn bất kỳ
lúc nào, cần fail-safe nếu wire production.
