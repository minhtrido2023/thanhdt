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

## Cách gọi đúng — xem hướng dẫn riêng
Chi tiết signing/HMAC, trading-token OTP, endpoint reference, và 10+ gotcha đã gây incident thật
(3 field "cash" khác nhau, settlement T+2 chiều-không-phải-sáng, board G1/G4/T*, `loanPackageId`
bắt buộc, v.v.) — xem
[`../trading-bot/dnse_openapi_v2_calling_guideline.md`](../trading-bot/dnse_openapi_v2_calling_guideline.md)
(nguồn đầy đủ: `agents/Mike/dnse_api_guideline_for_dashboard_bot.md`). Dùng khi build dashboard
quản lý danh mục DNSE.
