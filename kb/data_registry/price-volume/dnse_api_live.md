---
kind: external-api
status: CANONICAL
source: DNSE API live (dnse_api.py secdef/latest_trade/positions/balances)
group: price-volume
scope: dữ liệu TRONG NGÀY (real-time)
---

# DNSE API live (`dnse_api.py` secdef/latest_trade/positions/balances)

**Status: CANONICAL cho dữ liệu TRONG NGÀY**

## Là gì
Giá/khối lượng/vị thế thật, real-time.

## Ai ghi / cadence
Broker, không có độ trễ.

## Bẫy
Đây là nguồn BẮT BUỘC cho mọi tính toán cùng ngày (xem `coding_guidelines.md` §6 bright-line rule,
user directive 2026-07-09).
